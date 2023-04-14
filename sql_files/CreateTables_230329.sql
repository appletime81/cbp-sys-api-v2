CREATE TABLE InvoiceWKMaster
(
    WKMasterID     int NOT NULL AUTO_INCREMENT,
    InvoiceNo      varchar(64)    DEFAULT NULL,
    SupplierName   varchar(100)   DEFAULT NULL,
    SubmarineCable varchar(10)    DEFAULT NULL,
    WorkTitle      varchar(50)    DEFAULT NULL,
    ContractType   varchar(20)    DEFAULT NULL,
    IssueDate      datetime       DEFAULT NULL,
    DueDate        datetime       DEFAULT NULL,
    PartyName      varchar(100)   DEFAULT NULL,
    IsPro          tinyint(1) DEFAULT NULL,
    IsRecharge     tinyint(1) DEFAULT NULL,
    IsLiability    tinyint(1) DEFAULT NULL,
    TotalAmount    decimal(12, 2) DEFAULT NULL,
    PaidAmount     decimal(12, 2) DEFAULT NULL,
    CreateDate     datetime       DEFAULT NULL,
    PaidDate       datetime       DEFAULT NULL,
    Status         varchar(20)    DEFAULT NULL,
    PRIMARY KEY (WKMasterID)
);


CREATE TABLE InvoiceWKDetail
(
    WKDetailID     int NOT NULL AUTO_INCREMENT,
    WKMasterID     int NOT NULL,
    InvoiceNo      varchar(64)    DEFAULT NULL,
    SupplierName   varchar(100)   DEFAULT NULL,
    SubmarineCable varchar(10)    DEFAULT NULL,
    WorkTitle      varchar(50)    DEFAULT NULL,
    BillMilestone  varchar(20)    DEFAULT NULL,
    FeeItem        varchar(100)   DEFAULT NULL,
    FeeAmount      decimal(65, 2) DEFAULT NULL,
    PRIMARY KEY (WKDetailID)
);

CREATE TABLE InvoiceMaster
(
    InvMasterID    int NOT NULL AUTO_INCREMENT,
    WKMasterID     int          DEFAULT NULL,
    InvoiceNo      varchar(64)  DEFAULT NULL,
    PartyName      varchar(100) DEFAULT NULL,
    SupplierName   varchar(100) DEFAULT NULL,
    SubmarineCable varchar(10)  DEFAULT NULL,
    WorkTitle      varchar(50)  DEFAULT NULL,
    ContractType   varchar(20)  DEFAULT NULL,
    IssueDate      datetime     DEFAULT NULL,
    DueDate        datetime     DEFAULT NULL,
    IsPro          tinyint(1) DEFAULT NULL,
    Status         varchar(20)  DEFAULT NULL,
    PRIMARY KEY (InvMasterID)
);

CREATE TABLE InvoiceDetail
(
    InvDetailID    int NOT NULL AUTO_INCREMENT,
    InvMasterID    int NOT NULL,
    WKMasterID     int             DEFAULT NULL,
    WKDetailID     int             DEFAULT NULL,
    InvoiceNo      varchar(64)     DEFAULT NULL,
    PartyName      varchar(100)    DEFAULT NULL,
    SupplierName   varchar(100)    DEFAULT NULL,
    SubmarineCable varchar(10)     DEFAULT NULL,
    WorkTitle      varchar(50)     DEFAULT NULL,
    BillMilestone  varchar(20)     DEFAULT NULL,
    FeeItem        varchar(100)    DEFAULT NULL,
    FeeAmountPre   decimal(12, 2)  DEFAULT NULL,
    LBRatio        decimal(13, 10) DEFAULT NULL,
    FeeAmountPost  decimal(12, 2)  DEFAULT NULL,
    Difference     decimal(3, 2)   DEFAULT NULL,
    PRIMARY KEY (InvDetailID)
);

CREATE TABLE BillMaster
(
    BillMasterID      int NOT NULL AUTO_INCREMENT,
    BillingNo         varchar(64)    DEFAULT NULL,
    PONo              varchar(32)    DEFAULT NULL,
    SupplierName      varchar(100),
    SubmarineCable    varchar(10),
    WorkTitle         varchar(50),
    PartyName         varchar(100)   DEFAULT NULL,
    IssueDate         datetime       DEFAULT NULL,
    DueDate           datetime       DEFAULT NULL,
    FeeAmountSum      decimal(12, 2) DEFAULT NULL,
    ReceivedAmountSum decimal(12, 2) DEFAULT NULL,
    BankFees          decimal(12, 2) DEFAULT NULL,
    IsPro             tinyint(1) DEFAULT NULL,
    Status            varchar(20)    DEFAULT NULL,
    URI               varchar(128),
    PRIMARY KEY (BillMasterID)
);

CREATE TABLE BillDetail
(
    BillDetailID    int NOT NULL AUTO_INCREMENT,
    BillMasterID    int NOT NULL,
    WKMasterID      int            DEFAULT NULL,
    InvDetailID     int            DEFAULT NULL,
    PartyName       varchar(100)   DEFAULT NULL,
    SupplierName    varchar(100)   DEFAULT NULL,
    SubmarineCable  varchar(10)    DEFAULT NULL,
    WorkTitle       varchar(50)    DEFAULT NULL,
    BillMilestone   varchar(20)    DEFAULT NULL,
    FeeItem         varchar(100)   DEFAULT NULL,
    OrgFeeAmount    decimal(12, 2) DEFAULT NULL,
    DedAmount       decimal(12, 2) DEFAULT NULL,
    FeeAmount       decimal(12, 2) DEFAULT NULL,
    ReceivedAmount  decimal(12, 2) DEFAULT NULL,
    OverAmount      decimal(12, 2) DEFAULT NULL,
    ShortAmount     decimal(12, 2) DEFAULT NULL,
    ToCBAmount      decimal(12, 2),
    ShortOverReason varchar(128)   DEFAULT NULL,
    WriteOffDate    datetime       DEFAULT NULL,
    ReceiveDate     datetime       DEFAULT NULL,
    Note            varchar(128)   DEFAULT NULL,
    Status          varchar(20)    DEFAULT NULL,
    PRIMARY KEY (BillDetailID)
);

CREATE TABLE CollectStatement
(
    CollectID         int NOT NULL AUTO_INCREMENT,
    BillingNo         varchar(64),
    PartyName         varchar(100)   DEFAULT NULL,
    SupplierName      varchar(100)   DEFAULT NULL,
    SubmarineCable    varchar(10)    DEFAULT NULL,
    WorkTitle         varchar(50)    DEFAULT NULL,
    FeeAmount         decimal(12, 2) DEFAULT NULL,
    ReceivedAmountSum decimal(12, 2) DEFAULT NULL,
    BankFees          decimal(12, 2) DEFAULT NULL,
    ReceivedDate      datetime       DEFAULT NULL,
    Note              varchar(128)   DEFAULT NULL,
    PRIMARY KEY (CollectID)
);

CREATE TABLE PayMaster
(
    PayMID      int NOT NULL AUTO_INCREMENT,
    SupplierNam varchar(100),
    FeeAmount   decimal(65, 2),
    PaidAmount  decimal(12, 2),
    PaidDate    datetime,
    Note        varchar(128),
    PRIMARY KEY (PayMID)
);


CREATE TABLE PayStatement
(
    PaySID     int NOT NULL AUTO_INCREMENT,
    PayMID     int,
    WKMasterID int,
    InvoiceNo  varchar(64),
    FeeAmount  decimal(65, 2),
    PaidAmount decimal(12, 2),
    PaidDate   datetime,
    Note       varchar(128),
    Status     varchar(20),
    PRIMARY KEY (PaySID)
);


CREATE TABLE PayDraft
(
    PayDraftID     int NOT NULL AUTO_INCREMENT,
    Payee          varchar(100),
    CableInfo      varchar(64),
    TotalFeeAmount decimal(12, 2),
    Subject        varchar(128),
    Address        varchar(256),
    CtactPerson    varchar(10),
    Tel            varchar(20),
    email          varchar(64),
    IssueDate      varchar(32),
    IssueNo        varchar(32),
    OriginalTo     varchar(64),
    CBPBankAcctNo  varchar(20),
    BankAcctName   varchar(100),
    BankName       varchar(100),
    BankAddress    varchar(512),
    BankAcctNo     varchar(32),
    IBAN           varchar(32),
    SWIFTCode      varchar(32),
    Status         varchar(20),
    PayeeType      varchar(10),
    URI            varchar(128),
    PRIMARY KEY (PayDraftID)
);


CREATE TABLE PayDraftDetail
(
    PayDraftDetailID int NOT NULL AUTO_INCREMENT,
    PayDraftID       int,
    InvoiceNo        varchar(20),
    FeeAmount        varchar(20),
    PRIMARY KEY (PayDraftDetailID)
);


CREATE TABLE Liability
(
    LBRawID        int NOT NULL AUTO_INCREMENT,
    SubmarineCable varchar(10)     DEFAULT NULL,
    WorkTitle      varchar(50)     DEFAULT NULL,
    BillMilestone  varchar(20)     DEFAULT NULL,
    PartyName      varchar(100)    DEFAULT NULL,
    LBRatio        decimal(13, 10) DEFAULT NULL,
    CreateDate     datetime        DEFAULT NULL,
    Note           varchar(128),
    ModifyNote     varchar(128)    DEFAULT NULL,
    EndDate        datetime        DEFAULT NULL,
    PRIMARY KEY (LBRawID)
);


CREATE TABLE CB
(
    CBID           int NOT NULL AUTO_INCREMENT,
    CBType         varchar(20)    DEFAULT NULL,
    BillingNo      varchar(64)    DEFAULT NULL,
    BLDetailID     int            DEFAULT NULL,
    SubmarineCable varchar(10),
    WorkTitle      varchar(50),
    BillMilestone  varchar(20)    DEFAULT NULL,
    PartyName      varchar(100)   DEFAULT NULL,
    CNNo           varchar(64)    DEFAULT NULL,
    CurrAmount     decimal(12, 2) DEFAULT NULL,
    CreateDate     datetime       DEFAULT NULL,
    LastUpdDate    datetime       DEFAULT NULL,
    Note           varchar(128)   DEFAULT NULL,
    PRIMARY KEY (CBID)
);


CREATE TABLE CBStatement
(
    CBStateID   int NOT NULL AUTO_INCREMENT,
    CBID        int            DEFAULT NULL,
    BillingNo   varchar(64)    DEFAULT NULL,
    BLDetailID  int            DEFAULT NULL,
    TransItem   varchar(20)    DEFAULT NULL,
    OrgAmount   decimal(12, 2) DEFAULT NULL,
    TransAmount decimal(12, 2) DEFAULT NULL,
    Note        varchar(128)   DEFAULT NULL,
    CreateDate  datetime       DEFAULT NULL,
    PRIMARY KEY (CBStateID)
);


CREATE TABLE CNDetail
(
    CNDetailID int NOT NULL AUTO_INCREMENT,
    CNID       int            DEFAULT NULL,
    CBStateID  int            DEFAULT NULL,
    CBType     varchar(20)    DEFAULT NULL,
    BillingNo  varchar(64)    DEFAULT NULL,
    CNNo       varchar(64)    DEFAULT NULL,
    CurrAmount decimal(12, 2) DEFAULT NULL,
    CBNote     varchar(128)   DEFAULT NULL,
    PRIMARY KEY (CNDetailID)
);


CREATE TABLE CN
(
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
    PRIMARY KEY (CNID)
);


CREATE TABLE SignRecords
(
    SignID   int NOT NULL AUTO_INCREMENT,
    DocNo    varchar(128) DEFAULT NULL,
    DocType  varchar(8)   DEFAULT NULL,
    SignDate datetime     DEFAULT NULL,
    PRIMARY KEY (SignID)
);


CREATE TABLE UndoActions
(
    UndoID  int NOT NULL AUTO_INCREMENT,
    DocNo   varchar(128) DEFAULT NULL,
    DocType varchar(8)   DEFAULT NULL,
    Status  varchar(20)  DEFAULT NULL,
    Action  varchar(8)   DEFAULT NULL,
    ExeDate datetime     DEFAULT NULL,
    PRIMARY KEY (UndoID)
);

CREATE TABLE Users
(
    UserIDNo     int         NOT NULL AUTO_INCREMENT,
    UserID       varchar(16) NOT NULL,
    UserName     varchar(32)  DEFAULT NULL,
    UserCName    varchar(16)  DEFAULT NULL,
    PCode        varchar(16)  DEFAULT NULL,
    Email        varchar(128) DEFAULT NULL,
    Tel          varchar(20)  DEFAULT NULL,
    Fax          varchar(20)  DEFAULT NULL,
    Mobile       varchar(16)  DEFAULT NULL,
    DirectorName varchar(32)  DEFAULT NULL,
    DEmail       varchar(128) DEFAULT NULL,
    DTel         varchar(20)  DEFAULT NULL,
    DFax         varchar(20)  DEFAULT NULL,
    Company      varchar(256) DEFAULT NULL,
    Address      varchar(256) DEFAULT NULL,
    PRIMARY KEY (UserIDNo)
);

CREATE TABLE PermissionsMap
(
    PCode     varchar(16) NOT NULL,
    Liability tinyint DEFAULT NULL,
    InvoiceWK tinyint DEFAULT NULL,
    Invoice   tinyint DEFAULT NULL,
    Bill      tinyint DEFAULT NULL,
    CB        tinyint DEFAULT NULL,
    CN        tinyint DEFAULT NULL,
    Report    tinyint DEFAULT NULL,
    Data      tinyint DEFAULT NULL,
    Superior  tinyint DEFAULT NULL,
    Role      tinyint DEFAULT NULL,
    PRIMARY KEY (PCode)
);


CREATE TABLE Suppliers
(
    SupplierID     int NOT NULL AUTO_INCREMENT,
    SubmarineCable varchar(10)  DEFAULT NULL,
    WorkTitle      varchar(50)  DEFAULT NULL,
    SupplierName   varchar(100) DEFAULT NULL,
    BankAcctName   varchar(100) DEFAULT NULL,
    BankAcctNo     varchar(32)  DEFAULT NULL,
    SavingAcctNo   varchar(32)  DEFAULT NULL,
    SWIFTCode      varchar(32)  DEFAULT NULL,
    IBAN           varchar(32)  DEFAULT NULL,
    ACHNo          varchar(32)  DEFAULT NULL,
    WireRouting    varchar(32)  DEFAULT NULL,
    BankName       varchar(100) DEFAULT NULL,
    Branch         varchar(100) DEFAULT NULL,
    BankAddress    varchar(512) DEFAULT NULL,
    PRIMARY KEY (SupplierID)
);


CREATE TABLE Contracts
(
    ContractID     int NOT NULL AUTO_INCREMENT,
    ContractName   varchar(20) DEFAULT NULL,
    SubmarineCable varchar(10) DEFAULT NULL,
    WorkTitle      varchar(20) DEFAULT NULL,
    CreateDate     datetime    DEFAULT NULL,
    PRIMARY KEY (ContractID)
);


CREATE TABLE Parties
(
    PartyID        int          NOT NULL AUTO_INCREMENT,
    SubmarineCable varchar(10)  DEFAULT NULL,
    WorkTitle      varchar(50)  DEFAULT NULL,
    PartyCode      varchar(4)   NOT NULL,
    PartyName      varchar(100) NOT NULL,
    CompanyName    varchar(256) NOT NULL,
    Address        varchar(512) DEFAULT NULL,
    Contact        varchar(20)  DEFAULT NULL,
    Email          varchar(50)  DEFAULT NULL,
    Tel            varchar(20)  DEFAULT NULL,
    BankAcctName   varchar(100) DEFAULT NULL,
    BankAcctNo     varchar(32)  DEFAULT NULL,
    SavingAcctNo   varchar(32)  DEFAULT NULL,
    SWIFTCode      varchar(32)  DEFAULT NULL,
    IBAN           varchar(32)  DEFAULT NULL,
    ACHNo          varchar(32)  DEFAULT NULL,
    WireRouting    varchar(32)  DEFAULT NULL,
    BankName       varchar(100) DEFAULT NULL,
    Branch         varchar(100) DEFAULT NULL,
    BankAddress    varchar(512) DEFAULT NULL,
    PRIMARY KEY (PartyID)
);


CREATE TABLE SubmarineCables
(
    CableID   int NOT NULL AUTO_INCREMENT,
    CableCode varchar(4),
    CableName varchar(64)  DEFAULT NULL,
    Note      varchar(128) DEFAULT NULL,
    PRIMARY KEY (CableID)
);

CREATE TABLE WorkTitles
(
    TitleID int NOT NULL AUTO_INCREMENT,
    Title   varchar(20)  DEFAULT NULL,
    Note    varchar(128) DEFAULT NULL,
    PRIMARY KEY (TitleID)
);

CREATE TABLE ContractTypes
(
    ContractTypeID int NOT NULL AUTO_INCREMENT,
    ContractName   varchar(20)  DEFAULT NULL,
    Note           varchar(128) DEFAULT NULL,
    PRIMARY KEY (ContractTypeID)
);

CREATE TABLE PartiesByContract
(
    ContractID int NOT NULL,
    PartyName  varchar(100) DEFAULT NULL,
    PRIMARY KEY (ContractID)
);


CREATE TABLE SuppliersByContract
(
    ContractID   int NOT NULL,
    SupplierName varchar(100) DEFAULT NULL,
    PRIMARY KEY (ContractID)
);


CREATE TABLE Corporates
(
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
    PRIMARY KEY (CorpID)
);

/*
ALTER TABLE cbp_db.Parties 
ADD COLUMN BankAcctName VARCHAR(100) NULL AFTER Tel,
ADD COLUMN BankAcctNo VARCHAR(32) NULL AFTER BankAcctName,
ADD COLUMN SWIFTCode  VARCHAR(32) NULL AFTER BankAcctNo,
ADD COLUMN IBAN VARCHAR(32) NULL AFTER SWIFTCode,
ADD COLUMN ACHNo VARCHAR(32) NULL AFTER IBAN,
ADD COLUMN WireRouting VARCHAR(32) NULL AFTER ACHNo,
ADD COLUMN BankName VARCHAR(100) NULL AFTER WireRouting,
ADD COLUMN Branch VARCHAR(100) NULL AFTER BankName,
ADD COLUMN BankAddress  VARCHAR(512) NULL AFTER Branch;
*/

insert into Liability (SubmarineCable, WorkTitle, BillMilestone, PartyName, LBRatio, CreateDate, ModifyNote, EndDate)
values ('SJC2', 'Construction', 'BM9a', 'CHT', 7.1428571429, '2022-12-27 14:30:00', null, null);
insert into Liability (SubmarineCable, WorkTitle, BillMilestone, PartyName, LBRatio, CreateDate, ModifyNote, EndDate)
values ('SJC2', 'Construction', 'BM9a', 'CMI', 28.5714285714, '2022-12-27 14:30:00', null, null);
insert into Liability (SubmarineCable, WorkTitle, BillMilestone, PartyName, LBRatio, CreateDate, ModifyNote, EndDate)
values ('SJC2', 'Construction', 'BM9a', 'DHT', 3.5714285714, '2022-12-27 14:30:00', null, null);
insert into Liability (SubmarineCable, WorkTitle, BillMilestone, PartyName, LBRatio, CreateDate, ModifyNote, EndDate)
values ('SJC2', 'Construction', 'BM9a', 'Edge', 28.5714285714, '2022-12-27 14:30:00', null, null);
insert into Liability (SubmarineCable, WorkTitle, BillMilestone, PartyName, LBRatio, CreateDate, ModifyNote, EndDate)
values ('SJC2', 'Construction', 'BM9a', 'KDDI', 0.0793650794, '2022-12-27 14:30:00', null, null);
insert into Liability (SubmarineCable, WorkTitle, BillMilestone, PartyName, LBRatio, CreateDate, ModifyNote, EndDate)
values ('SJC2', 'Construction', 'BM9a', 'Singtel', 7.0634920635, '2022-12-27 14:30:00', null, null);
insert into Liability (SubmarineCable, WorkTitle, BillMilestone, PartyName, LBRatio, CreateDate, ModifyNote, EndDate)
values ('SJC2', 'Construction', 'BM9a', 'SKB', 7.1428571429, '2022-12-27 14:30:00', null, null);
insert into Liability (SubmarineCable, WorkTitle, BillMilestone, PartyName, LBRatio, CreateDate, ModifyNote, EndDate)
values ('SJC2', 'Construction', 'BM9a', 'Telin', 3.5714285714, '2022-12-27 14:30:00', null, null);
insert into Liability (SubmarineCable, WorkTitle, BillMilestone, PartyName, LBRatio, CreateDate, ModifyNote, EndDate)
values ('SJC2', 'Construction', 'BM9a', 'TRUE', 7.1428571429, '2022-12-27 14:30:00', null, null);
insert into Liability (SubmarineCable, WorkTitle, BillMilestone, PartyName, LBRatio, CreateDate, ModifyNote, EndDate)
values ('SJC2', 'Construction', 'BM9a', 'VNPT', 7.1428571429, '2022-12-27 14:30:00', null, null);

insert into Liability (SubmarineCable, WorkTitle, BillMilestone, PartyName, LBRatio, CreateDate, ModifyNote, EndDate)
values ('SJC2', 'Construction', 'BM12', 'CHT', 7.1428571429, '2022-12-27 14:30:00', null, null);
insert into Liability (SubmarineCable, WorkTitle, BillMilestone, PartyName, LBRatio, CreateDate, ModifyNote, EndDate)
values ('SJC2', 'Construction', 'BM12', 'CMI', 28.5714285714, '2022-12-27 14:30:00', null, null);
insert into Liability (SubmarineCable, WorkTitle, BillMilestone, PartyName, LBRatio, CreateDate, ModifyNote, EndDate)
values ('SJC2', 'Construction', 'BM12', 'DHT', 3.5714285714, '2022-12-27 14:30:00', null, null);
insert into Liability (SubmarineCable, WorkTitle, BillMilestone, PartyName, LBRatio, CreateDate, ModifyNote, EndDate)
values ('SJC2', 'Construction', 'BM12', 'Edge', 28.5714285714, '2022-12-27 14:30:00', null, null);
insert into Liability (SubmarineCable, WorkTitle, BillMilestone, PartyName, LBRatio, CreateDate, ModifyNote, EndDate)
values ('SJC2', 'Construction', 'BM12', 'KDDI', 0.0793650794, '2022-12-27 14:30:00', null, null);
insert into Liability (SubmarineCable, WorkTitle, BillMilestone, PartyName, LBRatio, CreateDate, ModifyNote, EndDate)
values ('SJC2', 'Construction', 'BM12', 'Singtel', 7.0634920635, '2022-12-27 14:30:00', null, null);
insert into Liability (SubmarineCable, WorkTitle, BillMilestone, PartyName, LBRatio, CreateDate, ModifyNote, EndDate)
values ('SJC2', 'Construction', 'BM12', 'SKB', 7.1428571429, '2022-12-27 14:30:00', null, null);
insert into Liability (SubmarineCable, WorkTitle, BillMilestone, PartyName, LBRatio, CreateDate, ModifyNote, EndDate)
values ('SJC2', 'Construction', 'BM12', 'Telin', 3.5714285714, '2022-12-27 14:30:00', null, null);
insert into Liability (SubmarineCable, WorkTitle, BillMilestone, PartyName, LBRatio, CreateDate, ModifyNote, EndDate)
values ('SJC2', 'Construction', 'BM12', 'TRUE', 7.1428571429, '2022-12-27 14:30:00', null, null);
insert into Liability (SubmarineCable, WorkTitle, BillMilestone, PartyName, LBRatio, CreateDate, ModifyNote, EndDate)
values ('SJC2', 'Construction', 'BM12', 'VNPT', 7.1428571429, '2022-12-27 14:30:00', null, null);