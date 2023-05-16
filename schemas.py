from datetime import datetime
from pydantic import BaseModel
from typing import Optional


class InvoiceWKMasterSchema(BaseModel):
    """
    WKMasterID = Column(Integer, primary_key=True, index=True)
    InvoiceNo = Column(String(20))
    SupplierName = Column(String(6))
    SubmarineCable = Column(String(10))
    WorkTitle = Column(String(50))
    ContractType = Column(String(20))
    IssueDate = Column(String(20))
    DueDate = Column(String(20))
    PartyName = Column(String(100))
    IsPro = Column(Boolean)
    IsRecharge = Column(Boolean)
    IsLiability = Column(Boolean)
    TotalAmount = Column(Float)
    PaidAmount = Column(Float)
    CreateDate = Column(String(20))
    PaidDate = Column(String(20))
    Status = Column(String(20))
    """

    WKMasterID: Optional[int]
    InvoiceNo: str
    SupplierName: str
    SubmarineCable: str
    WorkTitle: str
    ContractType: str
    IssueDate: datetime
    DueDate: datetime
    PartyName: Optional[str]
    IsPro: bool
    IsRecharge: bool
    IsLiability: bool
    TotalAmount: float
    PaidAmount: Optional[float] = 0.0
    CreateDate: Optional[datetime]
    PaidDate: Optional[datetime]
    Status: str


class InvoiceWKDetailSchema(BaseModel):
    WKDetailID: Optional[int]
    WKMasterID: Optional[int]
    InvoiceNo: str
    SupplierName: str
    SubmarineCable: str
    WorkTitle: str
    BillMilestone: str
    FeeItem: Optional[str]
    FeeAmount: float


class InvoiceMasterSchema(BaseModel):
    InvMasterID: Optional[int]
    WKMasterID: int
    InvoiceNo: str
    PartyName: str
    SupplierName: str
    SubmarineCable: str
    WorkTitle: str
    ContractType: str
    IssueDate: datetime
    DueDate: datetime
    Status: str
    IsPro: bool


class InvoiceDetailSchema(BaseModel):
    InvDetailID: Optional[int]
    InvMasterID: int
    WKMasterID: int
    WKDetailID: int
    InvoiceNo: str
    PartyName: str
    SupplierName: str
    SubmarineCable: str
    WorkTitle: str
    BillMilestone: str
    FeeItem: str
    FeeAmountPre: float
    LBRatio: float
    FeeAmountPost: float
    Difference: float
    Status: str


class BillMasterSchema(BaseModel):
    """
    BillMasterID = Column(Integer, primary_key=True, index=True)
    BillingNo = Column(String(64))
    PartyName = Column(String(100))
    CreateDate = Column(String(20))
    IssueDate = Column(String(20))
    DueDate = Column(String(20))
    FeeAmountSum = Column(Float)
    ReceivedAmountSum = Column(Float)
    IsPro = Column(Boolean)
    Status = Column(String(20))
    """

    BillMasterID: Optional[int]
    BillingNo: str
    PONo: Optional[str]
    PartyName: str
    SupplierName: Optional[str]
    SubmarineCable: str
    WorkTitle: str
    IssueDate: datetime
    DueDate: datetime
    FeeAmountSum: float
    ReceivedAmountSum: float
    BankFees: Optional[float]
    IsPro: bool
    URI: Optional[str]
    Status: str


class BillDetailSchema(BaseModel):
    BillDetailID: Optional[int]
    BillMasterID: int
    WKMasterID: int
    InvoiceNo: str
    InvDetailID: int
    PartyName: str
    SupplierName: str
    SubmarineCable: str
    WorkTitle: str
    BillMilestone: str
    FeeItem: str
    OrgFeeAmount: float
    DedAmount: float
    FeeAmount: float
    ReceivedAmount: float
    OverAmount: float
    ShortAmount: float
    ShortOverReason: Optional[str]
    WriteOffDate: Optional[datetime]
    ReceiveDate: Optional[datetime]
    Note: Optional[str]
    ToCBAmount: Optional[float]
    PaidAmount: Optional[float]
    Status: str


class CollectStatementSchema(BaseModel):
    CollectID: Optional[int]
    BillingNo: str
    PartyName: str
    SubmarineCable: str
    WorkTitle: str
    FeeAmount: float
    ReceivedAmountSum: float
    BankFee: float
    ReceiveDate: datetime
    Note: Optional[str]


class LiabilitySchema(BaseModel):
    LBRawID: Optional[int]
    SubmarineCable: str
    BillMilestone: str
    PartyName: str
    WorkTitle: str
    LBRatio: float
    Note: Optional[str]
    CreateDate: Optional[datetime]
    ModifyNote: Optional[str]
    EndDate: Optional[datetime]


class SuppliersSchema(BaseModel):
    """
    SupplierID = Column(Integer, primary_key=True, index=True)
    SupplierName = Column(String(100))
    BankAcctName = Column(String(100))
    BankAcctNo = Column(String(32))
    SWIFTCode = Column(String(32))
    IBAN = Column(String(32))
    BankName = Column(String(100))
    BankAddress = Column(String(512))
    """

    SupplierID: Optional[int]
    SubmarineCable: Optional[str]
    WorkTitle: Optional[str]
    SupplierName: Optional[str]
    CompanyName: Optional[str]
    BankAcctName: Optional[str]
    BankAcctNo: Optional[str]
    SavingAcctNo: Optional[str]
    SWIFTCode: Optional[str]
    IBAN: Optional[str]
    ACHNo: Optional[str]
    WireRouting: Optional[str]
    BankName: Optional[str]
    Branch: Optional[str]
    BankAddress: Optional[str]


class CorporatesSchema(BaseModel):
    CorpID: Optional[int]
    SubmarineCable: Optional[str]
    WorkTitle: Optional[str]
    Address: Optional[str]
    CreateDate: datetime
    BankAcctName: Optional[str]
    BankAcctNo: Optional[str]
    SavingAcctNo: Optional[str]
    SWIFTCode: Optional[str]
    IBAN: Optional[str]
    ACHNo: Optional[str]
    WireRouting: Optional[str]
    BankName: Optional[str]
    Branch: Optional[str]
    BranchAddress: Optional[str]


class ContractsSchema(BaseModel):
    ContractID: Optional[int]
    ContractName: str
    SubmarineCable: str
    WorkTitle: str
    CreateDate: datetime


class PartiesSchema(BaseModel):
    """
    PartyID = Column(Integer, primary_key=True, index=True)
    SubmarineCable = Column(String(10))
    WorkTitle = Column(String(50))
    PartyCode = Column(String(4))
    PartyName = Column(String(100))
    Address = Column(String(512))
    Contact = Column(String(20))
    Email = Column(String(50))
    Tel = Column(String(20))
    BankAcctName = Column(String(100))
    BankAcctNo = Column(String(32))
    SavingAcctNo = Column(String(32))
    SWIFTCode = Column(String(32))
    IBAN = Column(String(32))
    ACHNo = Column(String(32))
    WireRouting = Column(String(32))
    BankName = Column(String(100))
    Branch = Column(String(100))
    BankAddress = Column(String(512))
    """

    PartyID: Optional[int]
    SubmarineCable: Optional[str]
    WorkTitle: Optional[str]
    PartyCode: Optional[str]
    PartyName: Optional[str]
    CompanyName: Optional[str]
    Address: Optional[str]
    Contact: Optional[str]
    Email: Optional[str]
    Tel: Optional[str]
    BankAcctName: Optional[str]
    BankAcctNo: Optional[str]
    SavingAcctNo: Optional[str]
    SWIFTCode: Optional[str]
    IBAN: Optional[str]
    ACHNo: Optional[str]
    WireRouting: Optional[str]
    BankName: Optional[str]
    Branch: Optional[str]
    BankAddress: Optional[str]


class SubmarineCablesSchema(BaseModel):
    CableID: Optional[int]
    CableCode: Optional[str]
    CableName: str
    Note: Optional[str]


class WorkTitlesSchema(BaseModel):
    Title: str
    Note: Optional[str]


class ContractTypesSchema(BaseModel):
    ContractID: Optional[int]
    Note: Optional[str]


class CreditBalanceSchema(BaseModel):
    """
    CBID           int NOT NULL AUTO_INCREMENT,
    CBType         varchar(20),
    BillingNo      varchar(64),
    BLDetailID     int,
    SubmarineCable varchar(10),
    WorkTitle      varchar(50),
    CurrAmount     decimal(12, 2),
    PartyName      varchar(100),
    CNNo           varchar(64),
    CreateDate     datetime,
    LastUpdDate    datetime,
    Note           varchar(128),
    PRIMARY KEY (CBID)
    """

    CBID: Optional[int]
    CBType: Optional[str]
    BillingNo: Optional[str]
    InvoiceNo: Optional[str]
    BLDetailID: Optional[int]
    SubmarineCable: Optional[str]
    WorkTitle: Optional[str]
    BillMilestone: Optional[str]
    CurrAmount: Optional[float]
    PartyName: Optional[str]
    CNNo: Optional[str]
    CreateDate: Optional[datetime]
    LastUpdDate: Optional[datetime]
    Note: Optional[str]


class CreditBalanceStatementSchema(BaseModel):
    """
    CBStateID   int NOT NULL AUTO_INCREMENT,
    CBID        int,
    TransItem   varchar(20),
    OrgAmount   decimal(12, 2),
    TransAmount decimal(12, 2),
    Note        varchar(128),
    CreateDate  datetime,
    Oprcode     varchar(6),
    PRIMARY KEY (CBStateID)
    """

    CBStateID: Optional[int]
    CBID: int
    BillingNo: Optional[str]
    BLDetailID: Optional[int]
    TransItem: str
    OrgAmount: float
    TransAmount: float
    Note: Optional[str]
    CreateDate: datetime


class CreditNoteSchema(BaseModel):
    """
    CNID           int NOT NULL AUTO_INCREMENT,
    CNNo           varchar(128)   DEFAULT NULL,
    CNType         varchar(20)    DEFAULT NULL,
    SubmarineCable varchar(10)    DEFAULT NULL,
    WorkTitle      varchar(50)    DEFAULT NULL,
    PartyName      varchar(100)   DEFAULT NULL,
    CurrAmount     decimal(12, 2) DEFAULT NULL,
    IssueDate      datetime       DEFAULT NULL,
    Note           varchar(128)   DEFAULT NULL,
    URI            varchar(128),
    """

    CNID: Optional[int]
    CNNo: str
    CNType: str
    SubmarineCable: str
    WorkTitle: str
    PartyName: str
    CurrAmount: float
    IssueDate: datetime
    Note: Optional[str]
    URI: Optional[str]


class CreditNoteDetailSchema(BaseModel):
    """
    CNDetailID int NOT NULL AUTO_INCREMENT,
    CNID       int            DEFAULT NULL,
    CBID       int            DEFAULT NULL,
    CBType     varchar(20)    DEFAULT NULL,
    BillingNo  varchar(64)    DEFAULT NULL,
    CNNo       varchar(64)    DEFAULT NULL,
    CurrAmount decimal(12, 2) DEFAULT NULL,
    CBNote     varchar(128)   DEFAULT NULL,
    """

    CNDetailID: Optional[int]
    CNID: int
    CBStateID: int
    CBType: Optional[str]
    BillingNo: Optional[str]
    CNNo: Optional[str]
    CurrAmount: float
    CBNote: Optional[str]


class PartiesByContractSchema(BaseModel):
    """
    ContractID int NOT NULL,
    PartyName  varchar(100),
    PRIMARY KEY (ContractID)
    """

    ContractID: Optional[int]
    PartyName: str


class SuppliersByContractSchema(BaseModel):
    """
    ContractID   int not null,
    SupplierName varchar(100),
    PRIMARY KEY (ContractID)
    """

    ContractID: Optional[int]
    SupplierName: str


class UsersSchema(BaseModel):
    """
    UserID = Column(String(16), primary_key=True, index=True)
    UserName = Column(String(16))
    PCode = Column(String(16))
    Email = Column(String(128))
    Tel = Column(String(20))
    Fax = Column(String(20))
    Mobile = Column(String(16))
    DirectorName = Column(String(32))
    DEmail = Column(String(128))
    DTel = Column(String(20))
    DFax = Column(String(20))
    Company = Column(String(256))
    Address = Column(String(256))
    """

    UserIDNo: Optional[int]
    UserID: Optional[str]
    UserName: Optional[str]
    UserCName: Optional[str]
    Email: Optional[str]
    Tel: Optional[str]
    Fax: Optional[str]
    Mobile: Optional[str]
    DirectorName: Optional[str]
    DEmail: Optional[str]
    DTel: Optional[str]
    DFax: Optional[str]
    Company: Optional[str]
    Address: Optional[str]


class CBIDSchema(BaseModel):
    CBID: int


class DownloadBillDraftSchema(BaseModel):
    """
    {
        "BillMasterID": 1,
        "UserID": "chang_ty",
        "IssueDate": "2023/04/01",
        "DueDate": "2023/04/30",
        "WorkTitle": "Construction #11",
        "InvoiceName": "",
        "SubmarineCable": "SJC2"
    }
    """

    BillMasterID: int
    UserID: str
    IssueDate: str
    DueDate: str
    WorkTitle: str
    InvoiceName: str


class LoginSchema(BaseModel):
    username: str
    password: str
