/* InvoiceWKMaster */
INSERT INTO cbp_db_test_v2.InvoiceWKMaster (WKMasterID, InvoiceNo, SupplierName, SubmarineCable, WorkTitle,
                                            ContractType, IssueDate, DueDate, PartyName, IsPro, IsRecharge, IsLiability,
                                            IsCreditMemo, TotalAmount, DedAmount, PaidAmount, CreateDate, PaidDate,
                                            Status)
VALUES (1, 'DT0170168-1', 'NEC', 'SJC2', 'Construction', 'SC', '2023-06-25 07:38:40', '2023-06-30 07:38:40', '', 0, 0,
        1, null, 2776483.86, 0.00, 0.00, '2023-06-25 07:44:51', null, 'TEMPORARY');
INSERT INTO cbp_db_test_v2.InvoiceWKMaster (WKMasterID, InvoiceNo, SupplierName, SubmarineCable, WorkTitle,
                                            ContractType, IssueDate, DueDate, PartyName, IsPro, IsRecharge, IsLiability,
                                            IsCreditMemo, TotalAmount, DedAmount, PaidAmount, CreateDate, PaidDate,
                                            Status)
VALUES (2, 'DT0170168-2', 'NEC', 'SJC2', 'Construction', 'SC', '2023-06-25 07:42:15', '2023-06-30 07:42:15', '', 0, 0,
        1, null, 2805528.86, 0.00, 0.00, '2023-06-25 07:44:51', null, 'TEMPORARY');

/* InvoiceWKDetail */
INSERT INTO cbp_db_test_v2.InvoiceWKDetail (WKDetailID, WKMasterID, InvoiceNo, SupplierName, SubmarineCable, WorkTitle,
                                            BillMilestone, FeeItem, FeeAmount)
VALUES (1, 1, 'DT0170168-1', 'NEC', 'SJC2', 'Construction', 'BM9a',
        'BM9a Sea cable manufactured (except 8.5km spare cable))- Equipment', 1288822.32);
INSERT INTO cbp_db_test_v2.InvoiceWKDetail (WKDetailID, WKMasterID, InvoiceNo, SupplierName, SubmarineCable, WorkTitle,
                                            BillMilestone, FeeItem, FeeAmount)
VALUES (2, 1, 'DT0170168-1', 'NEC', 'SJC2', 'Construction', 'BM12', 'BM12 Branching Units (100%)-Service', 1487661.54);
INSERT INTO cbp_db_test_v2.InvoiceWKDetail (WKDetailID, WKMasterID, InvoiceNo, SupplierName, SubmarineCable, WorkTitle,
                                            BillMilestone, FeeItem, FeeAmount)
VALUES (3, 2, 'DT0170168-2', 'NEC', 'SJC2', 'Construction', 'BM9a',
        'BM9a Sea cable manufactured (except 8.5km spare cable))- Service', 1178227.94);
INSERT INTO cbp_db_test_v2.InvoiceWKDetail (WKDetailID, WKMasterID, InvoiceNo, SupplierName, SubmarineCable, WorkTitle,
                                            BillMilestone, FeeItem, FeeAmount)
VALUES (4, 2, 'DT0170168-2', 'NEC', 'SJC2', 'Construction', 'BM12', 'BM12 Branching Units (100%)-Equipment',
        1627300.92);
