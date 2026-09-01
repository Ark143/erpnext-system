\echo === Workspace child tables (Card vs Shortcut) ===
SELECT table_name FROM information_schema.tables WHERE table_name LIKE '%Workspace%' ORDER BY table_name;

\echo === Workspace Card sample (does 'Selling' card exist?) ===
SELECT "name", "label", "link_to", "type" FROM "tabWorkspace Card" WHERE "label" IN ('Selling','Point of Sale','Financial Statements','Assets') LIMIT 20;
