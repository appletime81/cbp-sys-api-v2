import os
from fastapi import FastAPI, Depends, Request
from fastapi.middleware.cors import CORSMiddleware


# from starlette.responses import FileResponse
from fastapi.responses import FileResponse

import service.InvoiceWKMaster.app as InvoiceWKMasterApp
import service.InvoiceWKDetail.app as InvoiceWKDetailApp
import service.InvoiceMaster.app as InvoiceMasterApp
import service.InvoiceDetail.app as InvoiceDetailApp
import service.Liability.app as LiabilityApp
import service.Parties.app as PartiesApp
import service.SubmarineCables.app as SubmarineCablesApp
import service.Suppliers.app as SuppliersApp
import service.Letter.app as LetterApp

from crud import *
from get_db import get_db
from service.InvoiceDetail.app import router as InvoiceDetailRouter
from service.InvoiceMaster.app import router as InvoiceMasterRouter
from service.InvoiceWKDetail.app import router as InvoiceWKDetailRouter
from service.InvoiceWKMaster.app import router as InvoiceWKMasterRouter
from service.Liability.app import router as LiabilityRouter
from service.Parties.app import router as PartiesRouter
from service.SubmarineCables.app import router as SubmarineCablesRouter
from service.Suppliers.app import router as SuppliersRouter
from service.BillMilestone.app import router as BillMilestoneRouter
from service.CreditBalance.app import router as CreditBalanceRouter
from service.Letter.app import router as LetterRouter
from service.BillMaster.app import router as BillMasterRouter
from service.Corporates.app import router as CorporatesRouter
from service.Contracts.app import router as ContractsRouter
from service.SubmarineCables.app import router as SubmarineCablesRouter
from service.PartiesByContract.app import router as PartiesByContractRouter
from service.SuppliersByContract.app import router as SuppliersByContractRouter
from service.UploadFile.app import router as UploadFileRouter
from service.Users.app import router as UsersRouter
from service.Payment.app import router as PaymentRouter
from service.GlobalSearch.app import router as GlobalSearchRouter
from utils.utils import *
from utils.log import *
from utils.orm_pydantic_convert import *

# import logic service function
from service.BillMaster.service import router as BillMasterServiceRouter
from service.Users.service import router as UsersServiceRouter
from service.InvoiceWKMaster.service import router as InvoiceWKMasterServiceRouter
from service.Payment.service import router as PaymentServiceRouter

app = FastAPI()

ROOT_URL = "/api/v1"


app.include_router(InvoiceWKMasterRouter, prefix=ROOT_URL, tags=["InvoiceWKMaster"])
app.include_router(InvoiceWKDetailRouter, prefix=ROOT_URL, tags=["InvoiceWKDetail"])
app.include_router(InvoiceMasterRouter, prefix=ROOT_URL, tags=["InvoiceMaster"])
app.include_router(InvoiceDetailRouter, prefix=ROOT_URL, tags=["InvoiceDetail"])
app.include_router(LiabilityRouter, prefix=ROOT_URL, tags=["Liability"])
app.include_router(PartiesRouter, prefix=ROOT_URL, tags=["Parties"])
app.include_router(SubmarineCablesRouter, prefix=ROOT_URL, tags=["SubmarineCables"])
app.include_router(SuppliersRouter, prefix=ROOT_URL, tags=["Suppliers"])
app.include_router(BillMilestoneRouter, prefix=ROOT_URL, tags=["BillMilestone"])
app.include_router(CreditBalanceRouter, prefix=ROOT_URL, tags=["CreditBalance"])
app.include_router(LetterRouter, prefix=ROOT_URL, tags=["Letter"])
app.include_router(BillMasterRouter, prefix=ROOT_URL, tags=["BillMaster"])
app.include_router(CorporatesRouter, prefix=ROOT_URL, tags=["Corporates"])
app.include_router(ContractsRouter, prefix=ROOT_URL, tags=["Contracts"])
app.include_router(SubmarineCablesRouter, prefix=ROOT_URL, tags=["SubmarineCables"])
app.include_router(PartiesByContractRouter, prefix=ROOT_URL, tags=["PartiesByContract"])
app.include_router(
    SuppliersByContractRouter, prefix=ROOT_URL, tags=["SuppliersByContract"]
)
app.include_router(UploadFileRouter, prefix=ROOT_URL, tags=["ReceiveFile"])
app.include_router(UsersRouter, prefix=ROOT_URL, tags=["Users"])
app.include_router(UsersServiceRouter, prefix=ROOT_URL, tags=["UsersService"])
app.include_router(BillMasterServiceRouter, prefix=ROOT_URL, tags=["BillMasterService"])
app.include_router(PaymentRouter, prefix=ROOT_URL, tags=["Payment"])
app.include_router(
    InvoiceWKMasterServiceRouter, prefix=ROOT_URL, tags=["InvoiceWKMasterService"]
)
app.include_router(PaymentServiceRouter, prefix=ROOT_URL, tags=["PaymentService"])
app.include_router(GlobalSearchRouter, prefix=ROOT_URL, tags=["GlobalSearch"])

# allow middlewares
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


# ------------------------------ InvoiceWKMaster and InvoiceWKDetail and InvoiceMaster and InvoiceDetail ------------------------------
# for InvoiceWKMaster
@app.post(f"{ROOT_URL}/checkInvoiceNo")
async def checkInvoiceNo(request: Request, db: Session = Depends(get_db)):
    """
    input:
    {"InvoiceNo": "1234567890"}
    """
    crudInvoiceWKMaster = CRUD(db, InvoiceWKMasterDBModel)
    InvoiceNo = (await request.json())["InvoiceNo"]

    InvoiceWKMasterData = crudInvoiceWKMaster.get_with_condition(
        {"InvoiceNo": InvoiceNo}
    )
    if InvoiceWKMasterData:
        return {"message": "InvoiceNo already exist", "isExist": True}
    else:
        return {"message": "InvoiceNo not exist", "isExist": False}


@app.post(f"{ROOT_URL}/generateInvoiceWKMaster&InvoiceWKDetail")
async def generateInvoiceWKMasterInvoiceWKDetailInvoiceMasterInvoiceDetail(
    request: Request,
    db: Session = Depends(get_db),
):
    invoice_data = await request.json()
    CreateDate = convert_time_to_str(datetime.now())
    # ---------- Step1. Generate InvoiceWKMaster ----------

    # get invoice wk master data
    InvoiceWKMasterDictData = invoice_data["InvoiceWKMaster"]

    # set CreateDate
    InvoiceWKMasterDictData["CreateDate"] = CreateDate

    # covert InvoiceWKMasterDictData to Pydantic model
    InvoiceWKMasterSchemaData = InvoiceWKMasterSchema(**InvoiceWKMasterDictData)

    crud = CRUD(db, InvoiceWKMasterDBModel)

    # check if InvoiceNo is existed
    isInvoiced = crud.get_with_condition(
        {"InvoiceNo": InvoiceWKMasterSchemaData.InvoiceNo}
    )
    if isInvoiced:
        return {"message": "InvoiceNo already exist"}

    # save InvoiceWKMaster to db
    addResponse = crud.create(InvoiceWKMasterSchemaData)
    print("-" * 25 + " addResponse " + "-" * 25)
    print(addResponse.WKMasterID)
    print("-" * 25 + " addResponse " + "-" * 25)

    justCreatedInvoiceWKMasterID = addResponse.WKMasterID
    print("justCreatedInvoiceWKMasterID", addResponse.WKMasterID)

    # ---------- Step2. Generate InvoiceWKDetail ----------
    # get invoice wk detail data
    InvoiceWKDetailDictDataList = invoice_data["InvoiceWKDetail"]

    for InvoiceWKDetailDictData in InvoiceWKDetailDictDataList:
        # covert InvoiceWKDetailDictData to Pydantic model
        InvoiceWKDetailDictData["WKMasterID"] = justCreatedInvoiceWKMasterID
        InvoiceWKDetailDictData["InvoiceNo"] = InvoiceWKMasterDictData["InvoiceNo"]
        InvoiceWKDetailDictData["WorkTitle"] = InvoiceWKMasterDictData["WorkTitle"]
        InvoiceWKDetailDictData["SupplierName"] = InvoiceWKMasterDictData[
            "SupplierName"
        ]
        InvoiceWKDetailDictData["SubmarineCable"] = InvoiceWKMasterDictData[
            "SubmarineCable"
        ]
        InvoiceWKDetailSchemaData = InvoiceWKDetailSchema(**InvoiceWKDetailDictData)

        # save InvoiceWKDetail to db
        crud = CRUD(db, InvoiceWKDetailDBModel)
        crud.create(InvoiceWKDetailSchemaData)
    record_log(
        f"{user_name} created InvoiceWKMaster, the InvoiceNo is {InvoiceWKMasterDictData['InvoiceNo']}"
    )
    return {"message": "success"}


@app.get(ROOT_URL + "/getInvoiceWKMaster&InvoiceWKDetail/{urlCondition}")
async def searchInvoiceWKMaster(
    request: Request,
    urlCondition: str,
    db: Session = Depends(get_db),
):
    getResult = []

    # table name
    table_name = "InvoiceWKMaster"

    # init CRUD
    crudInvoiceWKMaster = CRUD(db, InvoiceWKMasterDBModel)
    crudInvoiceWKDetail = CRUD(db, InvoiceWKDetailDBModel)

    BillMilestone = None
    if "BillMilestone" in urlCondition:
        urlCondition, BillMilestone = re_search_url_condition_value(
            urlCondition, "BillMilestone"
        )

    # get query condition
    if urlCondition == "all":
        InvoiceWKMasterDataList = crudInvoiceWKMaster.get_all()
    elif (
        "start" in urlCondition
        and "end" in urlCondition
        and "InvoiceNo" in urlCondition
    ):
        dictCondition = convert_url_condition_to_dict(urlCondition)
        InvoiceNo = dictCondition.pop("InvoiceNo")
        sqlCondition = convert_dict_to_sql_condition(dictCondition, table_name)
        InvoiceWKMasterDataList = crudInvoiceWKMaster.get_all_by_sql_with_like(
            sqlCondition, "InvoiceNo", InvoiceNo
        )
    elif (
        "InvoiceNo" in urlCondition
        and "start" not in urlCondition
        and "end" not in urlCondition
    ):
        dictCondition = convert_url_condition_to_dict_ignore_date(urlCondition)
        InvoiceNo = dictCondition.pop("InvoiceNo")
        InvoiceWKMasterDataList = crudInvoiceWKMaster.get_with_condition_and_like(
            dictCondition, InvoiceWKMasterDBModel.InvoiceNo, InvoiceNo
        )
    else:
        dictCondition = convert_url_condition_to_dict(urlCondition)
        InvoiceWKMasterDataList = crudInvoiceWKMaster.get_with_condition(dictCondition)

    # get InvoiceWKDetail append to getResult
    for InvoiceWKMasterData in InvoiceWKMasterDataList:
        InvoiceWKDetailDataList = crudInvoiceWKDetail.get_with_condition(
            {"WKMasterID": InvoiceWKMasterData.WKMasterID}
        )
        getResult.append(
            {
                "InvoiceWKMaster": InvoiceWKMasterData,
                "InvoiceWKDetail": InvoiceWKDetailDataList,
            }
        )

    if BillMilestone:
        print("-" * 100)
        print(BillMilestone)
        newGetResult = []
        for element in getResult:
            for InvoiceWKDetailData in element["InvoiceWKDetail"]:
                print("-" * 100)
                # pprint(orm_to_dict(InvoiceWKDetailData))

                if InvoiceWKDetailData.BillMilestone == BillMilestone:
                    print(InvoiceWKDetailData.BillMilestone)
                    newGetResult.append(element)
                    break
        print("-" * 100)
        pprint(newGetResult)
        return newGetResult

    return getResult


@app.get(ROOT_URL + "/getInvoiceMaster&InvoiceDetailStream/WKMasterID={WKMasterID}")
async def getInvoiceMasterInvoiceDetailStream(
    request: Request,
    WKMasterID: int,
    db: Session = Depends(get_db),
):
    # Step1. Get InvoiceWKMaster
    InvoiceWKMasterDataList = await InvoiceWKMasterApp.getInvoiceWKMaster(
        request, f"WKMasterID={WKMasterID}", db
    )

    InvoiceWKMasterData = InvoiceWKMasterDataList[0]
    InvoiceWKMasterDictData = orm_to_pydantic(
        InvoiceWKMasterData, InvoiceWKMasterSchema
    ).dict()
    TotalAmount = InvoiceWKMasterDictData.get("TotalAmount")
    WorkTitle = InvoiceWKMasterDictData["WorkTitle"]
    SubmarineCable = InvoiceWKMasterDictData["SubmarineCable"]

    # Step2. Get InvoiceWKDetail
    InvoiceWKDetailDataList = await InvoiceWKDetailApp.getInvoiceWKDetail(
        request, f"WKMasterID={WKMasterID}", db
    )
    InvoiceWKDetailDictDataList = [
        orm_to_pydantic(InvoiceWKDetailData, InvoiceWKDetailSchema).dict()
        for InvoiceWKDetailData in InvoiceWKDetailDataList
    ]

    # get max InvoiceMaster ID and generate InvoiceMasterID
    crud = CRUD(db, InvoiceMasterDBModel)
    InvMasterID = (
        crud.get_max_id(InvoiceMasterDBModel.InvMasterID) + 1
        if crud.get_max_id(InvoiceMasterDBModel.InvMasterID)
        else 1
    )

    if InvoiceWKMasterDictData.get("IsLiability"):
        # Step3. Generate InvoiceMaster
        # get all Liability
        newLiabilityDataList = []
        for InvoiceWKDetailDictData in InvoiceWKDetailDictDataList:
            LiabilityDataList = await LiabilityApp.getLiability(
                request,
                f"SubmarineCable={SubmarineCable}&WorkTitle={WorkTitle}&BillMilestone={InvoiceWKDetailDictData.get('BillMilestone')}&End=false",
                db,
            )
            newLiabilityDataList.append(LiabilityDataList)
        LiabilityDictDataList = [
            orm_to_pydantic(LiabilityData, LiabilitySchema).dict()
            for LiabilityDataList in newLiabilityDataList
            for LiabilityData in LiabilityDataList
        ]

        if not LiabilityDictDataList:
            return {"message": "No Liability Data"}

        LiabilityDataFrameDataList = [
            pd.DataFrame(dict([(k, [v]) for k, v in LiabilityDictData.items()]))
            for LiabilityDictData in LiabilityDictDataList
        ]
        LiabilityDataFrameData = dflist_to_df(LiabilityDataFrameDataList)
        LiabilityDataFrameData = (
            LiabilityDataFrameData.drop_duplicates()
        )  # remove duplicates
        # LiabilityDataFrameData.to_csv("LiabilityDataFrameData.csv", index=False)
        # get all PartyName
        PartyNameList = [LiabilityData.PartyName for LiabilityData in LiabilityDataList]
        PartyNameList = sorted(set(PartyNameList), key=PartyNameList.index)

        InvoiceMasterDictDataList = []
        for i, PartyName in enumerate(PartyNameList):
            InvoiceMasterDictData = {
                "InvMasterID": InvMasterID + i,
                "WKMasterID": WKMasterID,
                "InvoiceNo": InvoiceWKMasterDictData["InvoiceNo"],
                "PartyName": PartyName,
                "SupplierName": InvoiceWKMasterDictData["SupplierName"],
                "SubmarineCable": SubmarineCable,
                "WorkTitle": WorkTitle,
                "IssueDate": convert_time_to_str(InvoiceWKMasterDictData["IssueDate"]),
                "DueDate": convert_time_to_str(InvoiceWKMasterDictData["DueDate"]),
                "IsPro": InvoiceWKMasterDictData["IsPro"],
                "ContractType": InvoiceWKMasterDictData["ContractType"],
                "Status": "",
            }
            InvoiceMasterDictDataList.append(InvoiceMasterDictData)

        print(f"{'-' * 50} InvMasterID {'-' * 50}")
        print(InvMasterID)

        # Step4. Generate InvoiceDetail
        InvoiceDetailDictDataList = []
        for InvoiceMasterDictData in InvoiceMasterDictDataList:
            for InvoiceWKDetailDictData in InvoiceWKDetailDictDataList:
                LBRatio = LiabilityDataFrameData[
                    (
                        LiabilityDataFrameData["PartyName"]
                        == InvoiceMasterDictData["PartyName"]
                    )
                    & (
                        LiabilityDataFrameData["BillMilestone"]
                        == InvoiceWKDetailDictData["BillMilestone"]
                    )
                    & (
                        LiabilityDataFrameData["WorkTitle"]
                        == InvoiceMasterDictData["WorkTitle"]
                    )
                ]["LBRatio"].values[0]

                InvoiceDetailDictData = {
                    "WKMasterID": WKMasterID,
                    "WKDetailID": InvoiceWKDetailDictData["WKDetailID"],
                    "InvMasterID": InvoiceMasterDictData["InvMasterID"],
                    "InvoiceNo": InvoiceWKMasterDictData["InvoiceNo"],
                    "PartyName": InvoiceMasterDictData["PartyName"],
                    "SupplierName": InvoiceMasterDictData["SupplierName"],
                    "SubmarineCable": InvoiceMasterDictData["SubmarineCable"],
                    "WorkTitle": InvoiceMasterDictData["WorkTitle"],
                    "BillMilestone": InvoiceWKDetailDictData["BillMilestone"],
                    "FeeItem": InvoiceWKDetailDictData["FeeItem"],
                    "LBRatio": LBRatio,
                    "FeeAmountPre": InvoiceWKDetailDictData["FeeAmount"],
                    "FeeAmountPost": cal_fee_amount_post(
                        LBRatio, InvoiceWKDetailDictData["FeeAmount"]
                    ),
                    "Difference": 0,
                }
                InvoiceDetailDictDataList.append(InvoiceDetailDictData)
    else:
        # Step1. generate InvoiceMaster
        InvoiceNo = InvoiceWKMasterDictData["InvoiceNo"]
        SupplierName = InvoiceWKMasterDictData["SupplierName"]
        ContractType = InvoiceWKMasterDictData["ContractType"]
        IssueDate = convert_time_to_str(InvoiceWKMasterDictData["IssueDate"])
        DueDate = convert_time_to_str(InvoiceWKMasterDictData["DueDate"])
        PartyName = InvoiceWKMasterDictData["PartyName"]
        IsPro = InvoiceWKMasterDictData["IsPro"]
        InvoiceMasterDictDataList = [
            {
                "InvMasterID": InvMasterID,
                "WKMasterID": WKMasterID,
                "InvoiceNo": InvoiceNo,
                "PartyName": PartyName,
                "SupplierName": SupplierName,
                "SubmarineCable": SubmarineCable,
                "WorkTitle": WorkTitle,
                "ContractType": ContractType,
                "IssueDate": IssueDate,
                "DueDate": DueDate,
                "Status": "",
                "IsPro": IsPro,
            }
        ]

        # Step2. generate InvoiceDetail
        InvoiceDetailDictDataList = []
        for InvoiceWKDetailDictData in InvoiceWKDetailDictDataList:
            InvoiceDetailDictData = {
                "InvMasterID": InvMasterID,
                "WKMasterID": WKMasterID,
                "WKDetailID": InvoiceWKDetailDictData["WKDetailID"],
                "InvoiceNo": InvoiceNo,
                "PartyName": PartyName,
                "SupplierName": SupplierName,
                "SubmarineCable": SubmarineCable,
                "WorkTitle": WorkTitle,
                "BillMilestone": InvoiceWKDetailDictData["BillMilestone"],
                "FeeItem": InvoiceWKDetailDictData["FeeItem"],
                "LBRatio": 100,
                "FeeAmountPre": InvoiceWKDetailDictData["FeeAmount"],
                "FeeAmountPost": cal_fee_amount_post(
                    100, InvoiceWKDetailDictData["FeeAmount"]
                ),
                "Difference": 0,
            }
            InvoiceDetailDictDataList.append(InvoiceDetailDictData)

    streamResponse = {
        "TotalAmount": TotalAmount,
        "InvoiceMaster": InvoiceMasterDictDataList,
        "InvoiceDetail": InvoiceDetailDictDataList,
    }
    return streamResponse


@app.post(ROOT_URL + "/addInvoiceMaster&InvoiceDetail")
async def addInvoiceMasterAndInvoiceDetail(
    request: Request, db: Session = Depends(get_db)
):
    request_data = await request.json()
    InvoiceMasterDictDataList = request_data["InvoiceMaster"]
    InvoiceDetailDictDataList = request_data["InvoiceDetail"]
    pprint(InvoiceMasterDictDataList)
    pprint(InvoiceDetailDictDataList)

    # add InvoiceMaster data to database
    for InvoiceMasterDictData in InvoiceMasterDictDataList:
        InvoiceMasterPydanticData = InvoiceMasterSchema(**InvoiceMasterDictData)
        await InvoiceMasterApp.addInvoiceMaster(request, InvoiceMasterPydanticData, db)

    # add InvoiceDetail data to database
    for InvoiceDetailDictData in InvoiceDetailDictDataList:
        InvoiceDetailDictData["Status"] = "TO_MERGE"
        InvoiceDetailDictData["FeeAmountPost"] += InvoiceDetailDictData["Difference"]
        InvoiceDetailPydanticData = InvoiceDetailSchema(**InvoiceDetailDictData)
        await InvoiceDetailApp.addInvoiceDetail(request, InvoiceDetailPydanticData, db)

    # update InvoiceWKMaster status
    WKMasterID = InvoiceMasterDictDataList[0]["WKMasterID"]
    crud = CRUD(db, InvoiceWKMasterDBModel)
    InvoiceWKMasterData = crud.get_with_condition({"WKMasterID": WKMasterID})[0]
    InvoiceWKMasterDictData = orm_to_dict(InvoiceWKMasterData)
    InvoiceWKMasterDictData["Status"] = "BILLED"
    updatedInvoiceWKMasterData = crud.update(
        InvoiceWKMasterData, InvoiceWKMasterDictData
    )

    record_log(
        f"{user_name} add InvoiceMaster and InvoiceDetail, InvoiceNo: {InvoiceMasterDictDataList[0]['InvoiceNo']}"
    )

    return {
        "message": "success add InvoiceMaster and InvoiceDetail",
        "InvoiceWKMaster status": updatedInvoiceWKMasterData.Status,
    }


# -------------------------------------------------------------------------------------------------------------------------------------


# ------------------------------ Liability ------------------------------
@app.post(ROOT_URL + "/compareLiability")  # input data is "List[LiabilitySchema]"
async def compareLiability(request: Request, db: Session = Depends(get_db)):
    LiabilityDictDataList = await request.json()
    compareResultList = []
    crud = CRUD(db, LiabilityDBModel)
    for LiabilityDictData in LiabilityDictDataList:
        dictCondition = {
            "SubmarineCable": LiabilityDictData["SubmarineCable"],
            "WorkTitle": LiabilityDictData["WorkTitle"],
            "BillMilestone": LiabilityDictData["BillMilestone"],
            "PartyName": LiabilityDictData["PartyName"],
        }
        LiabilityDataList = crud.get_with_condition(dictCondition)
        LiabilityDataList = [
            # if EndDate have value no showing
            LiabilityData
            for LiabilityData in LiabilityDataList
            if not LiabilityData.EndDate
        ]
        if len(LiabilityDataList) != 0:
            for LiabilityData in LiabilityDataList:
                compareResultList.append(LiabilityData)

    if len(compareResultList) == 0:
        return {"message": "No same data", "compareResult": compareResultList}
    else:
        return {"message": "There some same datas", "compareResult": compareResultList}


@app.post(ROOT_URL + "/batchAddLiability")
async def batchAddLiability(request: Request, db: Session = Depends(get_db)):
    LiabilityDictDataList = await request.json()
    newLiabilityDataList = []
    crud = CRUD(db, LiabilityDBModel)
    for LiabilityDictData in LiabilityDictDataList:
        LiabilityDictData["CreateDate"] = convert_time_to_str(datetime.now())
        LiabilityPydanticData = LiabilitySchema(**LiabilityDictData)
        LiabilityPydanticData.BillMilestone = (
            LiabilityPydanticData.BillMilestone.strip()
        )
        newLiabilityData = crud.create(LiabilityPydanticData)
        newLiabilityDataList.append(newLiabilityData)

    # 紀錄使用者操作log
    record_log(f"{user_name} add Liability: {LiabilityDictDataList}")
    return {"message": "success add Liability", "Liability": newLiabilityDataList}


# -----------------------------------------------------------------------
