\echo === POS Opening Entries ===
SELECT "name", "docstatus", "status", "period_start_date", "period_end_date", "pos_profile", "company"
FROM "tabPOS Opening Entry" ORDER BY "period_start_date" DESC;
\echo === POS Profiles ===
SELECT "name", "company", "currency" FROM "tabPOS Profile";
