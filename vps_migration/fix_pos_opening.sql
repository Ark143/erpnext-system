-- Force-close the outdated open POS Opening Entry (data fix, after backup).
UPDATE "tabPOS Opening Entry"
SET "docstatus" = 2, "status" = 'Closed'
WHERE "name" = 'POS-OPE-2026-00002' AND "status" = 'Open';
SELECT "name", "docstatus", "status" FROM "tabPOS Opening Entry" ORDER BY "name";
