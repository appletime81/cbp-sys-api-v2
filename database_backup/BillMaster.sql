INSERT INTO cbp_db.BillMaster (BillMasterID, BillingNo, PONo, SupplierName, SubmarineCable, WorkTitle, PartyName,
                               IssueDate, DueDate, FeeAmountSum, ReceivedAmountSum, BankFees, IsPro, Status, URI)
VALUES (1, '03UP-CU2303300915', '', 'Ciena-US', 'TPE', 'Upgrade', 'CU', '2023-03-30 09:16:01', '2023-03-30 05:15:45',
        110241.00, 0.00, null, 0, 'INITIAL', null);
INSERT INTO cbp_db.BillMaster (BillMasterID, BillingNo, PONo, SupplierName, SubmarineCable, WorkTitle, PartyName,
                               IssueDate, DueDate, FeeAmountSum, ReceivedAmountSum, BankFees, IsPro, Status, URI)
VALUES (2, '03UP-CT2303300920', '', 'Ciena-US', 'TPE', 'Upgrade', 'CT', '2023-03-30 09:20:47', '2023-03-30 05:20:03',
        73494.00, 0.00, null, 0, 'INITIAL', null);
INSERT INTO cbp_db.BillMaster (BillMasterID, BillingNo, PONo, SupplierName, SubmarineCable, WorkTitle, PartyName,
                               IssueDate, DueDate, FeeAmountSum, ReceivedAmountSum, BankFees, IsPro, Status, URI)
VALUES (3, '03UP-KT2303300924', '', 'Ciena-US', 'TPE', 'Upgrade', 'KT', '2023-03-16 00:00:00', '2023-04-07 00:00:00',
        0.00, 0.00, null, 0, 'SIGNED',
        's3://cht-deploy-bucket-1/TPE Cable Network Upgrade #11 Central Billing Party.pdf');
