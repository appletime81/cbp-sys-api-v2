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


@router.post("/InvoiceWKMaster/returnToValidated")
async def invoiceWKMasterBilledReturn(request: Request, db: Session = Depends(get_db)):
    """
    {
        "WKMasterID": int,
    }
    """

    crudBillMaster = CRUD(db, BillMasterDBModel)
    crudBillDetail = CRUD(db, BillDetailDBModel)
    crudInvoiceWKMaster = CRUD(db, InvoiceWKMasterDBModel)
    crudInvoiceMaster = CRUD(db, InvoiceMasterDBModel)
    crudInvoiceDetail = CRUD(db, InvoiceDetailDBModel)

    WKMasterID = (await request.json())["WKMasterID"]

    # =============================================
    # Get InvoiceDetail
    # =============================================
    InvoiceDetailDataList = crudInvoiceDetail.get_with_condition(
        {"WKMasterID": WKMasterID}
    )
    InvoiceWKMasterData = crudInvoiceWKMaster.get_with_condition(
        {"WKMasterID": WKMasterID}
    )[0]

    # =============================================
    # 檢查是否已開立帳單，或者帳單已進入銷帳狀態
    # =============================================

    # 抓取 InvoiceMasterID
    InvDetailIDList = list(set([x.InvDetailID for x in InvoiceDetailDataList]))
    BillDetailDataList = crudBillDetail.get_value_if_in_a_list(
        BillDetailDBModel.InvDetailID, InvDetailIDList
    )
    if BillDetailDataList:
        BillMasterIDList = list(set([x.BillMasterID for x in BillDetailDataList]))
        BillMasterDataList = crudBillMaster.get_value_if_in_a_list(
            BillMasterDBModel.BillMasterID, BillMasterIDList
        )
        BillMasterDataResult = {
            "INITIAL": [],
            "RATED": [],
            "SIGNED": [],
            "TO_WRITEOFF": [],
            "COMPLETE": [],
        }
        for BillMasterData in BillMasterDataList:
            if BillMasterData.Status == "INITIAL":
                BillMasterDataResult["INITIAL"].append(BillMasterData)
            elif BillMasterData.Status == "RATED":
                BillMasterDataResult["RATED"].append(BillMasterData)
            elif BillMasterData.Status == "SIGNED":
                BillMasterDataResult["SIGNED"].append(BillMasterData)
            elif BillMasterData.Status == "TO_WRITEOFF":
                BillMasterDataResult["TO_WRITEOFF"].append(BillMasterData)
            elif BillMasterData.Status == "COMPLETE":
                BillMasterDataResult["COMPLETE"].append(BillMasterData)
        return {"ifReturn": False, "BillMaster": BillMasterDataResult}

    # =============================================
    # 刪除 InvoiceMaster
    # =============================================
    # InvoiceMasterIDList = list(set([x.InvMasterID for x in InvoiceDetailDataList]))
    # InvoiceMasterDataList = crudInvoiceMaster.get_value_if_in_a_list(
    #     InvoiceMasterDBModel.InvMasterID, InvoiceMasterIDList
    # )
    # for InvoiceMasterData in InvoiceMasterDataList:
    #     crudInvoiceMaster.remove(InvoiceMasterData.InvMasterID)

    # =============================================
    # 刪除 InvoiceDetail
    # =============================================
    # for InvoiceDetailData in InvoiceDetailDataList:
    #     crudInvoiceDetail.remove(InvoiceDetailData.InvDetailID)

    # =============================================
    # 更改 InvoiceWKMaster 狀態
    # =============================================
    # newInvoiceWKMasterData = deepcopy(InvoiceWKMasterData)
    # newInvoiceWKMasterData.Status = "VALIDATED"
    # newInvoiceWKMasterData = crudInvoiceWKMaster.update(
    #     newInvoiceWKMasterData, orm_to_dict(newInvoiceWKMasterData)
    # )
    #
    # return {"message": "success", "InvoiceWKMaster": newInvoiceWKMasterData}
    return {"message": "success"}


@router.post("/invalidInvoice/afterBilled")
async def invalidInvoiceAfterBilled(request: Request, db: Session = Depends(get_db)):
    """
    input data:
    {
        "WKMasterID": int,
    }

    response data:
    1. 如果還有帳單存在:
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
    crudInvoiceWKDetail = CRUD(db, InvoiceWKDetailDBModel)
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
    if BillDetailDataList:
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

            subBillDetailDataList = list(
                filter(lambda x: x.BillMasterID == BillMasterID, BillDetailDataList)
            )

            if subBillDetailDataList[0].Status == "MERGED" or (
                not subBillDetailDataList[0].Status
            ):
                resultDictList["INITIAL"].append(BillMasterData)
            else:
                resultDictList[subBillDetailDataList[0].Status].append(BillMasterData)
        pprint(resultDictList)
        return {"ifReturn": False, "BillMaster": resultDictList}
    return None
