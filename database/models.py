from sqlalchemy import Column, Integer, String, Boolean, Float, JSON
from .engine import Base


class InvoiceWKMasterDBModel(Base):
    """
    WKMasterID     int NOT NULL AUTO_INCREMENT,
    InvoiceNo      varchar(64),
    SupplierName   varchar(100),
    SubmarineCable varchar(10),
    WorkTitle      varchar(50),
    ContractType   varchar(20),
    IssueDate      datetime,
    DueDate        datetime,
    PartyName      varchar(100),
    IsPro          tinyint(1),
    IsRecharge     tinyint(1),
    IsLiability    tinyint(1),
    TotalAmount    decimal(12, 2),
    PaidAmount     decimal(12, 2),
    CreateDate     datetime,
    PaidDate       datetime,
    Status         varchar(20),
    """

    __tablename__ = "InvoiceWKMaster"
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


class InvoiceWKDetailDBModel(Base):
    __tablename__ = "InvoiceWKDetail"
    WKDetailID = Column(Integer, primary_key=True, index=True)
    WKMasterID = Column(Integer)
    InvoiceNo = Column(String(20))
    SupplierName = Column(String(6))
    SubmarineCable = Column(String(10))
    WorkTitle = Column(String(50))
    BillMilestone = Column(String(20))
    FeeItem = Column(String(100))
    FeeAmount = Column(Float)


class InvoiceMasterDBModel(Base):
    __tablename__ = "InvoiceMaster"
    InvMasterID = Column(Integer, primary_key=True, index=True)
    WKMasterID = Column(Integer)
    InvoiceNo = Column(String(20))
    PartyName = Column(String(100))
    SupplierName = Column(String(6))
    SubmarineCable = Column(String(10))
    WorkTitle = Column(String(50))
    ContractType = Column(String(20))
    IssueDate = Column(String(20))
    DueDate = Column(String(20))
    IsPro = Column(Boolean)


class InvoiceDetailDBModel(Base):
    __tablename__ = "InvoiceDetail"
    InvDetailID = Column(Integer, primary_key=True, index=True)
    InvMasterID = Column(Integer)
    WKMasterID = Column(Integer)
    WKDetailID = Column(Integer)
    InvoiceNo = Column(String(20))
    PartyName = Column(String(100))
    SupplierName = Column(String(100.0))
    SubmarineCable = Column(String(10))
    WorkTitle = Column(String(50))
    BillMilestone = Column(String(20))
    FeeItem = Column(String(100))
    FeeAmountPre = Column(Float)
    LBRatio = Column(Float)
    FeeAmountPost = Column(Float)
    Difference = Column(Float)
    Difference = Column(Float)
    Status = Column(String(20))


class BillMasterDBModel(Base):
    """
    BillMasterID      int NOT NULL AUTO_INCREMENT,
    BillingNo         varchar(64),
    PONo              varchar(32),
    SupplierName      varchar(100),
    SubmarineCable    varchar(10),
    WorkTitle         varchar(50),
    PartyName         varchar(100),
    IssueDate         datetime,
    DueDate           datetime,
    FeeAmountSum      decimal(12, 2),
    ReceivedAmountSum decimal(12, 2),
    IsPro             tinyint(1),
    Tel               varchar(20),
    Fax               varchar(20),
    TitleInfo         varchar(32),
    Status            varchar(20),
    URI               varchar(128),
    """

    __tablename__ = "BillMaster"
    BillMasterID = Column(Integer, primary_key=True, index=True)
    BillingNo = Column(String(20))
    PONo = Column(String(20))
    SubmarineCable = Column(String(10))
    SupplierName = Column(String(100))
    WorkTitle = Column(String(50))
    PartyName = Column(String(100))
    IssueDate = Column(String(20))
    DueDate = Column(String(20))
    FeeAmountSum = Column(Float)
    ReceivedAmountSum = Column(Float)
    BankFees = Column(Float)
    IsPro = Column(Boolean)
    Status = Column(String(20))
    URI = Column(String(128))


class BillDetailDBModel(Base):
    """
    BillDetailID    int NOT NULL AUTO_INCREMENT,
    BillMasterID    int NOT NULL,
    WKMasterID      int,
    InvoiceNo       varchar(64),
    InvDetailID     int,
    PartyName       varchar(100),
    SupplierName    varchar(100),
    SubmarineCable  varchar(10),
    WorkTitle       varchar(50),
    BillMilestone   varchar(20),
    FeeItem         varchar(100),
    OrgFeeAmount    decimal(12, 2),
    DedAmount       decimal(12, 2),
    FeeAmount       decimal(12, 2),
    ReceivedAmount  decimal(12, 2),
    OverAmount      decimal(12, 2),
    ShortAmount     decimal(12, 2),
    ToCBAmount      decimal(12, 2),
    ShortOverReason varchar(128),
    WriteOffDate    datetime,
    ReceiveDate     datetime,
    Note            varchar(128),
    Status          varchar(20)
    """

    __tablename__ = "BillDetail"
    BillDetailID = Column(Integer, primary_key=True, index=True)
    BillMasterID = Column(Integer)
    WKMasterID = Column(Integer)
    InvoiceNo = Column(String(64))
    InvDetailID = Column(Integer)
    PartyName = Column(String(100))
    SupplierName = Column(String(100))
    SubmarineCable = Column(String(10))
    WorkTitle = Column(String(50))
    BillMilestone = Column(String(20))
    FeeItem = Column(String(100))
    OrgFeeAmount = Column(Float)
    DedAmount = Column(Float)
    FeeAmount = Column(Float)
    ReceivedAmount = Column(Float)
    OverAmount = Column(Float)
    ShortAmount = Column(Float)
    ToCBAmount = Column(Float)
    ShortOverReason = Column(String(128))
    WriteOffDate = Column(String(20))
    ReceiveDate = Column(String(20))
    Note = Column(String(128))
    Status = Column(String(20))


class CollectStatementDBModel(Base):
    __tablename__ = "CollectStatement"
    CollectID = Column(Integer, primary_key=True, index=True)
    BillingNo = Column(String(64))
    PartyName = Column(String(100))
    SubmarineCable = Column(String(10))
    WorkTitle = Column(String(50))
    FeeAmount = Column(Float)
    ReceivedAmountSum = Column(Float)
    BankFee = Column(Float)
    ReceiveDate = Column(String(20))
    Note = Column(String(128))


class LiabilityDBModel(Base):
    __tablename__ = "Liability"
    LBRawID = Column(Integer, primary_key=True, index=True)
    SubmarineCable = Column(String(10))
    BillMilestone = Column(String(20))
    WorkTitle = Column(String(50))
    PartyName = Column(String(100))
    Note = Column(String(128))
    LBRatio = Column(Float)
    CreateDate = Column(String(20))
    ModifyNote = Column(String(128))
    EndDate = Column(String(20))


class PartiesDBModel(Base):
    __tablename__ = "Parties"
    """
    PartyID        int          NOT NULL AUTO_INCREMENT,
    SubmarineCable varchar(10),
    WorkTitle      varchar(50),
    PartyCode      varchar(4)   NOT NULL,
    PartyName      varchar(100) NOT NULL,
    CompanyName    varchar(256),
    Address        varchar(512),
    Contact        varchar(20),
    Email          varchar(50),
    Tel            varchar(20),
    BankAcctName   varchar(100),
    BankAcctNo     varchar(32),
    SavingAcctNo   varchar(32),
    SWIFTCode      varchar(32),
    IBAN           varchar(32),
    ACHNo          varchar(32),
    WireRouting    varchar(32),
    BankName       varchar(100),
    Branch         varchar(100),
    BankAddress    varchar(512),
    """
    PartyID = Column(Integer, primary_key=True, index=True)
    SubmarineCable = Column(String(10))
    WorkTitle = Column(String(50))
    PartyCode = Column(String(4))
    PartyName = Column(String(100))
    CompanyName = Column(String(256))
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


class SuppliersDBModel(Base):
    """
    SupplierID   int NOT NULL AUTO_INCREMENT,
    CableName    varchar(64),
    SupplierName varchar(100),
    BankAcctName varchar(100),
    BankAcctNo   varchar(32),
    SavingAcctNo varchar(32),
    SWIFTCode    varchar(32),
    IBAN         varchar(32),
    ACHNo        varchar(32),
    WireRouting  varchar(32),
    BankName     varchar(100),
    Branch       varchar(100),
    BankAddress  varchar(512),
    """

    __tablename__ = "Suppliers"
    SupplierID = Column(Integer, primary_key=True, index=True)
    SubmarineCable = Column(String(10))
    WorkTitle = Column(String(50))
    SupplierName = Column(String(100))
    CompanyName = Column(String(256))
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


class CorporatesDBModel(Base):
    """
    CorpID         int NOT NULL AUTO_INCREMENT,
    SubmarineCable varchar(10)  DEFAULT NULL,
    WorkTitle      varchar(50)  DEFAULT NULL,
    Address        varchar(512) DEFAULT NULL,
    CreateDate     datetime     DEFAULT NULL,
    BankAcctName   varchar(100) DEFAULT NULL,
    BankAcctNo     varchar(32)  DEFAULT NULL,
    SavingAcctNo   varchar(32)  DEFAULT NULL,
    SWIFTCode      varchar(32)  DEFAULT NULL,
    IBAN           varchar(32)  DEFAULT NULL,
    ACHNo          varchar(32)  DEFAULT NULL,
    WireRouting    varchar(32)  DEFAULT NULL,
    BankName       varchar(100) DEFAULT NULL,
    Branch         varchar(100) DEFAULT NULL,
    BranchAddress  varchar(512) DEFAULT NULL,
    """

    __tablename__ = "Corporates"
    CorpID = Column(Integer, primary_key=True, index=True)
    SubmarineCable = Column(String(10))
    WorkTitle = Column(String(50))
    Address = Column(String(512))
    CreateDate = Column(String(20))
    BankAcctName = Column(String(100))
    BankAcctNo = Column(String(32))
    SavingAcctNo = Column(String(32))
    SWIFTCode = Column(String(32))
    IBAN = Column(String(32))
    ACHNo = Column(String(32))
    WireRouting = Column(String(32))
    BankName = Column(String(100))
    Branch = Column(String(100))
    BranchAddress = Column(String(512))


class ContractsDBModel(Base):
    __tablename__ = "Contracts"
    ContractID = Column(Integer, primary_key=True, index=True)
    ContractName = Column(String(20))
    SubmarineCable = Column(String(20))
    WorkTitle = Column(String(20))
    CreateDate = Column(String(20))


class SubmarineCablesDBModel(Base):
    __tablename__ = "SubmarineCables"
    CableID = Column(Integer, primary_key=True, index=True)
    CableCode = Column(String(4))
    CableName = Column(String(20))
    Note = Column(String(128))


class CreditBalanceDBModel(Base):
    """
    CREATE TABLE CB
    (
        CBID           int NOT NULL AUTO_INCREMENT,
        CBType         varchar(20),
        BillingNo      varchar(64),
        BLDetailID     int,
        SubmarineCable varchar(10),
        WorkTitle      varchar(50),
        CurrAmount     decimal(12, 2),
        PartyName      varchar(100),
        CONo           varchar(64),
        CreateDate     datetime,
        LastUpdDate    datetime,
        Note           varchar(128),
        PRIMARY KEY (CBID)
    );
    """

    __tablename__ = "CB"
    CBID = Column(Integer, primary_key=True, index=True)
    CBType = Column(String(20))
    BillingNo = Column(String(64))
    InvoiceNo = Column(String(64))
    BLDetailID = Column(Integer)
    SubmarineCable = Column(String(10))
    WorkTitle = Column(String(50))
    BillMilestone = Column(String(20))
    CurrAmount = Column(Float)
    PartyName = Column(String(100))
    CNNo = Column(String(64))
    CreateDate = Column(String(20))
    LastUpdDate = Column(String(20))
    Note = Column(String(128))


class CreditBalanceStatementDBModel(Base):
    """
    CREATE TABLE CBStatement
    (
        CBStateID   int NOT NULL AUTO_INCREMENT,
        CBID        int,
        TransItem   varchar(20),
        OrgAmount   decimal(12, 2),
        TransAmount decimal(12, 2),
        Note        varchar(128),
        CreateDate  datetime,
        Oprcode     varchar(6),
        PRIMARY KEY (CBStateID)
    );
    """

    __tablename__ = "CBStatement"
    CBStateID = Column(Integer, primary_key=True, index=True)
    CBID = Column(Integer)
    BillingNo = Column(String(64))
    BLDetailID = Column(Integer)
    TransItem = Column(String(20))
    OrgAmount = Column(Float)
    TransAmount = Column(Float)
    Note = Column(String(128))
    CreateDate = Column(String(20))


class CreditNoteDBModel(Base):
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

    __tablename__ = "CN"
    CNID = Column(Integer, primary_key=True, index=True)
    CNNo = Column(String(128))
    CNType = Column(String(20))
    SubmarineCable = Column(String(10))
    WorkTitle = Column(String(50))
    PartyName = Column(String(100))
    CurrAmount = Column(Float)
    IssueDate = Column(String(20))
    Note = Column(String(128))
    URI = Column(String(128))


class CreditNoteDetailDBModel(Base):
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

    __tablename__ = "CNDetail"
    CNDetailID = Column(Integer, primary_key=True, index=True)
    CNID = Column(Integer)
    CBStateID = Column(Integer)
    CBType = Column(String(20))
    BillingNo = Column(String(64))
    CNNo = Column(String(64))
    CurrAmount = Column(Float)
    CBNote = Column(String(128))


class PartiesByContractDBModel(Base):
    """
    CREATE TABLE PartiesByContract
    (
        ContractID int NOT NULL,
        PartyName  varchar(100),
        PRIMARY KEY (ContractID)
    );
    """

    __tablename__ = "PartiesByContract"
    ContractID = Column(Integer, primary_key=True, index=True)
    PartyName = Column(String(100))


class CBPBankAccountDBModel(Base):
    """
    CREATE TABLE CBPBankAccount
    (
        CorpID    int NOT NULL AUTO_INCREMENT,
        CorpName  varchar(64),
        AcctName  varchar(100),
        AcctNo    varchar(32),
        SWIFTCode varchar(32),
        IBAN      varchar(32),
        Name      varchar(100),
        Address   varchar(512),
        PRIMARY KEY (CorpID)
    );
    """

    __tablename__ = "CBPBankAccount"
    CorpID = Column(Integer, primary_key=True, index=True)
    CorpName = Column(String(64))
    AcctName = Column(String(100))
    AcctNo = Column(String(32))
    SWIFTCode = Column(String(32))
    IBAN = Column(String(32))
    Name = Column(String(100))
    Address = Column(String(512))


class SuppliersByContractDBModel(Base):
    """
    CREATE TABLE SuppliersByContract
    (
        ContractID   int not null,
        SupplierName varchar(100),
        PRIMARY KEY (ContractID)
    );
    """

    __tablename__ = "SuppliersByContract"
    ContractID = Column(Integer, primary_key=True, index=True)
    SupplierName = Column(String(100))


class UsersDBModel(Base):
    """
    UserID       varchar(16) NOT NULL,
    UserName     varchar(16),
    PCode        varchar(16),
    Email        varchar(128),
    Tel          varchar(20),
    Fax          varchar(20),
    Mobile       varchar(16),
    DirectorName varchar(32),
    DEmail       varchar(128),
    DTel         varchar(20),
    DFax         varchar(20),
    Company      varchar(256),
    Address      varchar(256),
    """

    __tablename__ = "Users"
    UserID = Column(String(16), primary_key=True, index=True)
    UserName = Column(String(16))
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


class WaterBillDBModel(Base):
    """
    CREATE TABLE WaterBill
    (
        WBID              INT AUTO_INCREMENT PRIMARY KEY,
        InvoiceDetailList JSON NOT NULL
    );
    """

    __tablename__ = "WaterBill"
    WBID = Column(Integer, primary_key=True, index=True)
    InvoiceDetailList = Column(JSON)
