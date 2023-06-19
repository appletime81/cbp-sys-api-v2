INSERT INTO cbp_db_test_v2.BillDetail (BillDetailID, BillMasterID, WKMasterID, InvoiceNo, InvDetailID, PartyName,
                                       SupplierName, SubmarineCable, WorkTitle, BillMilestone, FeeItem, OrgFeeAmount,
                                       DedAmount, FeeAmount, ReceivedAmount, OverAmount, ShortAmount, ToCBAmount,
                                       PaidAmount, ShortOverReason, WriteOffDate, ReceiveDate, Note, Status)
VALUES (3, 2, 1, 'DT0170168-1', 2, 'CHT', 'NEC', 'SJC2', 'Construction', 'BM12', 'BM12 Branching Units (100%)-Service',
        106261.54, 0.00, 106261.54, 0.00, 0.00, 0.00, 0.00, 0.00, '', null, null, '', '');
INSERT INTO cbp_db_test_v2.BillDetail (BillDetailID, BillMasterID, WKMasterID, InvoiceNo, InvDetailID, PartyName,
                                       SupplierName, SubmarineCable, WorkTitle, BillMilestone, FeeItem, OrgFeeAmount,
                                       DedAmount, FeeAmount, ReceivedAmount, OverAmount, ShortAmount, ToCBAmount,
                                       PaidAmount, ShortOverReason, WriteOffDate, ReceiveDate, Note, Status)
VALUES (4, 2, 2, 'DT0170168-2', 21, 'CHT', 'NEC', 'SJC2', 'Construction', 'BM9a',
        'BM9a Sea cable manufactured (except 8.5km spare cable))- Service', 84159.14, 0.00, 84159.14, 0.00, 0.00, 0.00,
        0.00, 0.00, '', null, null, '', '');

INSERT INTO cbp_db_test_v2.BillMaster (BillMasterID, BillingNo, PONo, SubmarineCable, WorkTitle, PartyName, IssueDate,
                                       DueDate, FeeAmountSum, ReceivedAmountSum, BankFees, IsPro, Status, URI)
VALUES (2, '02CO-CI2306191434', '', 'SJC2', 'Construction', 'CHT', '2023-06-19 14:34:58', '2023-06-30 14:34:42',
        190420.68, 0.00, null, 0, 'INITIAL', null);
