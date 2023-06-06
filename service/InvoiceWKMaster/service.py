from fastapi import APIRouter, Request, Depends

from crud import *
from get_db import get_db
from sqlalchemy.orm import Session
from utils.utils import *
from utils.log import *
from utils.orm_pydantic_convert import *

import os
from copy import deepcopy


router = APIRouter()


@router.post("/returnToValidated")
async def returnToValidatedInvoice(request: Request, db: Session = Depends(get_db)):
    """
    input data:
    {
        "WKMasterID": int,
    }
    """

    crudInvoiceWKMaster = CRUD(db, InvoiceWKMasterDBModel)
    crudInvoiceMaster = CRUD(db, InvoiceMasterDBModel)
    crudInvoiceDetail = CRUD(db, InvoiceDetailDBModel)

    crudBillMaster = CRUD(db, BillMasterDBModel)
    crudBillDetail = CRUD(db, BillDetailDBModel)

    # =============================================
    # 抓取 InvoiceDetail
    # =============================================
    InvoiceDetailDataList = crudInvoiceDetail.get_with_condition(
        {"WKMasterID": (await request.json())["WKMasterID"]}
    )

    # =============================================
    # 抓取 InvoiceMaster
    # =============================================
    InvoiceMasterDataList = crudInvoiceMaster.get_with_condition(
        {"WKMasterID": (await request.json())["WKMasterID"]}
    )

    # =============================================
    # 抓取 InvoiceWKMaster
    # =============================================
    InvoiceWKMasterData = crudInvoiceWKMaster.get_with_condition(
        {"WKMasterID": (await request.json())["WKMasterID"]}
    )[0]

    # =============================================
    # 抓取 BillDetail，
    # 檢查是否有其他 InvoiceDetail 還是被併為帳單
    # 若有 -> 不讓重新立帳
    # 無 -> 則反之
    # =============================================
    BillDetailDataList = crudBillDetail.get_value_if_in_a_list(
        BillDetailDBModel.InvDetailID,
        list(
            set(
                [
                    InvoiceDetailData.InvDetailID
                    for InvoiceDetailData in InvoiceDetailDataList
                ]
            )
        ),
    )
    BillMasterDataList = crudBillMaster.get_value_if_in_a_list(
        BillMasterDBModel.BillMasterID,
        list(
            set([BillDetailData.BillMasterID for BillDetailData in BillDetailDataList])
        ),
    )
    invalidBillDetailDataListStatus = list(set([x.Status for x in BillDetailDataList]))
    invalidBillDetailDataListStatus = (
        invalidBillDetailDataListStatus == ["INVALID"]
        if invalidBillDetailDataListStatus
        else False
    )
    if BillDetailDataList and (not invalidBillDetailDataListStatus):
        resultDictList = {
            "INITIAL": [],
            "RATED": [],
            "SIGNED": [],
            "TO_WRITEOFF": [],
            "COMPLETE": [],
        }
        for BillMasterData in BillMasterDataList:
            tempBillDetailDataList = list(
                filter(
                    lambda x: x.BillMasterID == BillMasterData.BillMasterID,
                    BillDetailDataList,
                )
            )
            if BillMasterData.Status == "INITIAL":
                resultDictList["INITIAL"].append(BillMasterData)
            else:
                resultDictList[tempBillDetailDataList[0].Status].append(BillMasterData)
            return {"ifReturn": False, "BillMaster": resultDictList}

    if (not BillDetailDataList) or invalidBillDetailDataListStatus:
        # =============================================
        # 刪除 InvoiceMaster
        # =============================================
        for InvoiceMasterData in InvoiceMasterDataList:
            crudInvoiceMaster.remove(InvoiceMasterData.InvMasterID)

        # =============================================
        # 刪除 InvoiceDetail
        # =============================================
        for InvoiceDetailData in InvoiceDetailDataList:
            crudInvoiceDetail.remove(InvoiceDetailData.InvDetailID)

        newInvoiceWKMasterData = deepcopy(InvoiceWKMasterData)
        newInvoiceWKMasterData.Status = "VALIDATED"
        newInvoiceWKMasterData = crudInvoiceWKMaster.update(
            InvoiceWKMasterData, orm_to_dict(newInvoiceWKMasterData)
        )

        return {
            "message": "success",
            "ifReturn": True,
            "InvoiceWKMaster": newInvoiceWKMasterData,
        }


@router.post("/invalidInvoice/afterBilled")
async def invalidInvoiceAfterBilled(request: Request, db: Session = Depends(get_db)):
    """
    input data:
    {
        "WKMasterID": int,
    }

    response data:
    如果還有帳單存在:
    {
        "ifReturn": False,
        "BillMaster": {
            "INITIAL": [],
            "RATED": [],
            "SIGNED": [],
            "TO_WRITEOFF": [],
            "COMPLETE": [],
        }
    }
    """
    crudInvoiceWKMaster = CRUD(db, InvoiceWKMasterDBModel)
    crudInvoiceMaster = CRUD(db, InvoiceMasterDBModel)
    crudInvoiceDetail = CRUD(db, InvoiceDetailDBModel)

    crudBillMaster = CRUD(db, BillMasterDBModel)
    crudBillDetail = CRUD(db, BillDetailDBModel)

    # =============================================
    # 抓取
    # 1. InvoiceWKMaster
    # 2. InvoiceMaster
    # 3. InvoiceDetail
    # =============================================
    InvoiceWKMasterData = crudInvoiceWKMaster.get_with_condition(
        {"WKMasterID": (await request.json())["WKMasterID"]}
    )[0]
    InvoiceMasterDataList = crudInvoiceMaster.get_with_condition(
        {"WKMasterID": InvoiceWKMasterData.WKMasterID}
    )
    InvoiceDetailDataList = crudInvoiceDetail.get_with_condition(
        {"WKMasterID": InvoiceWKMasterData.WKMasterID}
    )

    # =============================================
    # 根據InvoiceDetailDataList抓取BillDetail
    # =============================================
    InvDetailIDList = list(set([x.InvDetailID for x in InvoiceDetailDataList]))
    BillDetailDataList = crudBillDetail.get_value_if_in_a_list(
        BillDetailDBModel.InvDetailID, InvDetailIDList
    )
    invalidBillDetailDataListStatus = list(set([x.Status for x in BillDetailDataList]))
    invalidBillDetailDataListStatus = (
        invalidBillDetailDataListStatus == ["INVALID"]
        if invalidBillDetailDataListStatus
        else False
    )

    if BillDetailDataList and (not invalidBillDetailDataListStatus):
        resultDictList = {
            "INITIAL": [],
            "RATED": [],
            "SIGNED": [],
            "TO_WRITEOFF": [],
            "COMPLETE": [],
        }
        BillMasterIDList = list(set([x.BillMasterID for x in BillDetailDataList]))

        # =============================================
        # 抓取BillMaster
        # =============================================
        for BillMasterID in BillMasterIDList:
            BillMasterData = crudBillMaster.get_with_condition(
                {"BillMasterID": BillMasterID}
            )[0]

            tempBillDetailDataList = list(
                filter(lambda x: x.BillMasterID == BillMasterID, BillDetailDataList)
            )

            if tempBillDetailDataList[0].Status == "MERGED" or (
                not tempBillDetailDataList[0].Status
            ):
                resultDictList["INITIAL"].append(BillMasterData)
            else:
                resultDictList[tempBillDetailDataList[0].Status].append(BillMasterData)
        return {"ifReturn": False, "BillMaster": resultDictList}

    if (not BillDetailDataList) or invalidBillDetailDataListStatus:
        # =============================================
        # 作廢 InvoiceMaster
        # =============================================
        newInvoiceMasterDataList = []
        for InvoiceMasterData in InvoiceMasterDataList:
            newInvoiceMasterData = deepcopy(InvoiceMasterData)
            newInvoiceMasterData.Status = "INVALID"
            newInvoiceMasterData = crudInvoiceMaster.update(
                newInvoiceMasterData, orm_to_dict(newInvoiceMasterData)
            )
            newInvoiceMasterDataList.append(newInvoiceMasterData)

        # =============================================
        # 作廢 InvoiceDetail
        # =============================================
        newInvoiceDetailDataList = []
        for InvoiceDetailData in InvoiceDetailDataList:
            newInvoiceDetailData = deepcopy(InvoiceDetailData)
            newInvoiceDetailData.Status = "INVALID"
            newInvoiceDetailData = crudInvoiceDetail.update(
                newInvoiceDetailData, orm_to_dict(newInvoiceDetailData)
            )
            newInvoiceDetailDataList.append(newInvoiceDetailData)

        # =============================================
        # 作廢 InvoiceWKMaster
        # =============================================
        newInvoiceWKMasterData = deepcopy(InvoiceWKMasterData)
        newInvoiceWKMasterData.Status = "INVALID"
        newInvoiceWKMasterData = crudInvoiceWKMaster.update(
            newInvoiceWKMasterData, orm_to_dict(newInvoiceWKMasterData)
        )

        return {
            "message": "success",
            "ifReturn": True,
            "InvoiceWKMaster": newInvoiceWKMasterData,
            "InvoiceMaster": newInvoiceMasterDataList,
            "InvoiceDetail": newInvoiceDetailDataList,
        }
