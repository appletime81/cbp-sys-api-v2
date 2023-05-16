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
    InvoiceNo       varchar(64),
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
    ToCBAmount      decimal(12, 2) DEFAULT NULL,
    PaidAmount      decimal(12, 2) DEFAULT NULL,
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
    Tel            varchar(32),
    email          varchar(64),
    IssueDate      varchar(32),
    IssueNo        varchar(32),
    OriginalTo     varchar(64),
    CBPBankAcctNo  varchar(20),
    BankAcctName   varchar(100),
    BankName       varchar(100),
    BankAddress    varchar(512),
    BankAcctNo     varchar(32),
    IBAN           varchar(64),
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
    InvoiceNo      varchar(64)    DEFAULT NULL,
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
    Email        varchar(128) DEFAULT NULL,
    Tel          varchar(32)  DEFAULT NULL,
    Fax          varchar(20)  DEFAULT NULL,
    Mobile       varchar(16)  DEFAULT NULL,
    DirectorName varchar(32)  DEFAULT NULL,
    DEmail       varchar(128) DEFAULT NULL,
    DTel         varchar(32)  DEFAULT NULL,
    DFax         varchar(20)  DEFAULT NULL,
    Company      varchar(256) DEFAULT NULL,
    Address      varchar(256) DEFAULT NULL,
    PRIMARY KEY (UserIDNo)
);

CREATE TABLE UserPermissions
(
    UPerMIDNo int         NOT NULL AUTO_INCREMENT,
    UserID    varchar(16) NOT NULL,
    UserCName varchar(16) DEFAULT NULL,
    Liability tinyint     DEFAULT NULL,
    InvoiceWK tinyint     DEFAULT NULL,
    Invoice   tinyint     DEFAULT NULL,
    Bill      tinyint     DEFAULT NULL,
    CB        tinyint     DEFAULT NULL,
    CN        tinyint     DEFAULT NULL,
    Data      tinyint     DEFAULT NULL,
    Report    tinyint     DEFAULT NULL,
    Superior  tinyint     DEFAULT NULL,
    Role      tinyint     DEFAULT NULL,
    PCode     varchar(16) NOT NULL,
    PRIMARY KEY (UPerMIDNo)
);


CREATE TABLE Suppliers
(
    SupplierID     int NOT NULL AUTO_INCREMENT,
    SubmarineCable varchar(10)  DEFAULT NULL,
    WorkTitle      varchar(50)  DEFAULT NULL,
    SupplierName   varchar(100) DEFAULT NULL,
    CompanyName    varchar(256) DEFAULT NULL,
    BankAcctName   varchar(100) DEFAULT NULL,
    BankAcctNo     varchar(32)  DEFAULT NULL,
    SavingAcctNo   varchar(32)  DEFAULT NULL,
    SWIFTCode      varchar(32)  DEFAULT NULL,
    IBAN           varchar(64)  DEFAULT NULL,
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
    Contact        varchar(64),
    Email          varchar(64),
    Tel            varchar(32),
    BankAcctName   varchar(100) DEFAULT NULL,
    BankAcctNo     varchar(32)  DEFAULT NULL,
    SavingAcctNo   varchar(32)  DEFAULT NULL,
    SWIFTCode      varchar(32)  DEFAULT NULL,
    IBAN           varchar(64)  DEFAULT NULL,
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
    TitleID   int NOT NULL AUTO_INCREMENT,
    TitleCode varchar(4),
    Title     varchar(20)  DEFAULT NULL,
    Note      varchar(128) DEFAULT NULL,
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
    IBAN           varchar(64)  DEFAULT NULL,
    ACHNo          varchar(32)  DEFAULT NULL,
    WireRouting    varchar(32)  DEFAULT NULL,
    BankName       varchar(100) DEFAULT NULL,
    Branch         varchar(100) DEFAULT NULL,
    BranchAddress  varchar(512) DEFAULT NULL,
    PRIMARY KEY (CorpID)
);

/* Suppliers */
INSERT INTO cbp_db_test_v2.Suppliers (SupplierID, SubmarineCable, WorkTitle, SupplierName, CompanyName, BankAcctName,
                                      BankAcctNo, SavingAcctNo, SWIFTCode, IBAN, ACHNo, WireRouting, BankName, Branch,
                                      BankAddress)
VALUES (1, 'SJC2', 'Construction', 'NEC', 'NEC Corporation, Submarine Network Division', 'NEC Corporation', '',
        '258008', 'SMBCJPJT', '', '', '', 'Sumitomo Mitsui Banking Corporation, Tokyo Main Office (211)', '',
        '3-2, Marunouchi 1-chome, Chiyoda-ku, Tokyo, Japan NEC Corporation');

/* Parties */
INSERT INTO cbp_db_test_v2.Parties (PartyID, SubmarineCable, WorkTitle, PartyCode, PartyName, CompanyName, Address,
                                    Contact, Email, Tel, BankAcctName, BankAcctNo, SavingAcctNo, SWIFTCode, IBAN, ACHNo,
                                    WireRouting, BankName, Branch, BankAddress)
VALUES (1, 'SJC2', 'Construction', 'CI', 'CHT', 'Chunghwa Telecom Co., Ltd. Network Technology Group',
        '31, Aikuo East Road, Taipei, Taiwan 106', '黃宏杰', 'hj-hwang@cht.com.tw', '02-28054246', '', '', '', '', '',
        '', '', '', '', '');
INSERT INTO cbp_db_test_v2.Parties (PartyID, SubmarineCable, WorkTitle, PartyCode, PartyName, CompanyName, Address,
                                    Contact, Email, Tel, BankAcctName, BankAcctNo, SavingAcctNo, SWIFTCode, IBAN, ACHNo,
                                    WireRouting, BankName, Branch, BankAddress)
VALUES (2, 'SJC2', 'Construction', 'CM', 'CM',
        'China Mobile International Limited Transmission Engineering Manager | Planning & Development',
        'Level 30, Tower 1, Kowloon Commerce Centre, No.51 Kwai Cheong Road, Kwai Chung, New Territories, Hong Kong',
        'Anthony Wong (黄明华 WONG Ming Wah)', 'anthonywong@cmi.chinamobile.com', '+852 67656790', '', '', '', '', '',
        '', '', '', '', '');
INSERT INTO cbp_db_test_v2.Parties (PartyID, SubmarineCable, WorkTitle, PartyCode, PartyName, CompanyName, Address,
                                    Contact, Email, Tel, BankAcctName, BankAcctNo, SavingAcctNo, SWIFTCode, IBAN, ACHNo,
                                    WireRouting, BankName, Branch, BankAddress)
VALUES (3, 'SJC2', 'Construction', 'DH', 'DHT', 'Donghua Telecom Co. Ltd.',
        'UNIT A, 7/F, TOWER A, BILLION CENTRE, NO.1 WANG KWONG ROAD, KOWLOON BAY, KOWLOON, HKSAR', 'Frankie',
        'frankie@donghwatele.com', '+852-35862600', '', '', '', '', '', '', '', '', '', '');
INSERT INTO cbp_db_test_v2.Parties (PartyID, SubmarineCable, WorkTitle, PartyCode, PartyName, CompanyName, Address,
                                    Contact, Email, Tel, BankAcctName, BankAcctNo, SavingAcctNo, SWIFTCode, IBAN, ACHNo,
                                    WireRouting, BankName, Branch, BankAddress)
VALUES (4, 'SJC2', 'Construction', 'EG', 'EDGE', 'Edge Network Services Limited',
        '4 Grand Canal Square, Dublin 2, Ireland', 'Nicholas', 'nictanch@fb.com', '+85295384781', '', '', '', '', '',
        '', '', '', '', '');
INSERT INTO cbp_db_test_v2.Parties (PartyID, SubmarineCable, WorkTitle, PartyCode, PartyName, CompanyName, Address,
                                    Contact, Email, Tel, BankAcctName, BankAcctNo, SavingAcctNo, SWIFTCode, IBAN, ACHNo,
                                    WireRouting, BankName, Branch, BankAddress)
VALUES (5, 'SJC2', 'Construction', 'KD', 'KDDI',
        'KDDI Corporation Global Network Engineering and Operations Center (GNOC)',
        'KDDI Bldg., 2-3-2, Nishishinjuku, Shinjuku-ku, Tokyo 163-8003, Japan', 'Mr. Koki Takeshima',
        'gnoc-cable@kddi.com', '+81-3-3347-6064', '', '', '', '', '', '', '', '', '', '');
INSERT INTO cbp_db_test_v2.Parties (PartyID, SubmarineCable, WorkTitle, PartyCode, PartyName, CompanyName, Address,
                                    Contact, Email, Tel, BankAcctName, BankAcctNo, SavingAcctNo, SWIFTCode, IBAN, ACHNo,
                                    WireRouting, BankName, Branch, BankAddress)
VALUES (6, 'SJC2', 'Construction', 'ST', 'Singtel', 'Singapore Telecommunications Limited',
        'COM3, #06-01, 31C Exeter Road Singapore 239734', 'Yue Meng Fai', 'mengfai@singtel.com', '+65 68872921', '', '',
        '', '', '', '', '', '', '', '');
INSERT INTO cbp_db_test_v2.Parties (PartyID, SubmarineCable, WorkTitle, PartyCode, PartyName, CompanyName, Address,
                                    Contact, Email, Tel, BankAcctName, BankAcctNo, SavingAcctNo, SWIFTCode, IBAN, ACHNo,
                                    WireRouting, BankName, Branch, BankAddress)
VALUES (7, 'SJC2', 'Construction', 'SK', 'SKB', 'SK Broadband Co., Ltd. (SKB)',
        '8F, SK Namsan Green Bldg., 24, Toegye-ro, Jung-gu, Seoul 04637, Korea', 'SUN JIN KUK (Chris)',
        'chris.sun@sk.com', '+82-10-3702-0461', '', '', '', '', '', '', '', '', '', '');
INSERT INTO cbp_db_test_v2.Parties (PartyID, SubmarineCable, WorkTitle, PartyCode, PartyName, CompanyName, Address,
                                    Contact, Email, Tel, BankAcctName, BankAcctNo, SavingAcctNo, SWIFTCode, IBAN, ACHNo,
                                    WireRouting, BankName, Branch, BankAddress)
VALUES (8, 'SJC2', 'Construction', 'TE', 'Telin',
        'PT. Telekomunikasi Indonesia International (Telin) Digital & Service Planning and Development',
        'Telkom Landmark Tower (TLT), Tower 2, 16thand 17th Floor,  Jalan Jendral Gatot Subroto, Kavling 52,Jakarta Selatan, Indonesia 12710',
        'Mr. Edward Natanael', 'edward.natanael@telin.net', '+62 21 2995 2300', '', '', '', '', '', '', '', '', '', '');
INSERT INTO cbp_db_test_v2.Parties (PartyID, SubmarineCable, WorkTitle, PartyCode, PartyName, CompanyName, Address,
                                    Contact, Email, Tel, BankAcctName, BankAcctNo, SavingAcctNo, SWIFTCode, IBAN, ACHNo,
                                    WireRouting, BankName, Branch, BankAddress)
VALUES (9, 'SJC2', 'Construction', 'TC', 'TICC',
        'True Internet Corporation Co., Ltd (TICC) International Gateway Business',
        '18, True Tower, Ratchadapisek Road, Huai Khwang, Bangkok 10310, Thailand', 'Wachira Parathum',
        'wachira_par@trueintergateway.com', '+669 5651 5394', '', '', '', '', '', '', '', '', '', '');
INSERT INTO cbp_db_test_v2.Parties (PartyID, SubmarineCable, WorkTitle, PartyCode, PartyName, CompanyName, Address,
                                    Contact, Email, Tel, BankAcctName, BankAcctNo, SavingAcctNo, SWIFTCode, IBAN, ACHNo,
                                    WireRouting, BankName, Branch, BankAddress)
VALUES (10, 'SJC2', 'Construction', 'VN', 'VNPT', 'VNPT NET Corporation (VNPT-NET)',
        'Level 10, VNPT Net Building International Network Development Division 30 Pham Hung Street, My Dinh 1 Ward, Nam Tu Liem District, Hanoi, Vietnam',
        'Minh Hien', 'nguyenthiminhhien@vnpt.vn', '+84 912312598', '', '', '', '', '', '', '', '', '', '');

/* Corporates */
INSERT INTO cbp_db_test_v2.Corporates (CorpID, SubmarineCable, WorkTitle, Address, CreateDate, BankAcctName, BankAcctNo,
                                       SavingAcctNo, SWIFTCode, IBAN, ACHNo, WireRouting, BankName, Branch,
                                       BranchAddress)
VALUES (1, 'SJC2', 'Upgrade', '31 Aikuo E. Rd., Taipei, Taiwan, 106', '2023-04-14 03:36:23',
        'SJC2 Central Billing Party of Chunghwa Telecom (International Business Group)', '054007501968', '',
        'BKTWTWTP054', '', '', '', 'Bank of Taiwan, Hsinyi Branch', '', '88, Sec. 2, Sinyi Road, Taipei');
