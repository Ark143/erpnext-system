\echo === Welcome Workspace flags ===
SELECT "name", "title", "public", "is_hidden", "module", "type" FROM "tabWorkspace" WHERE "name" = 'Welcome Workspace';

\echo === Workspace Link table (child links) ===
SELECT "name", "parent", "label", "link_to", "link_type" FROM "tabWorkspace Link" WHERE "link_to" LIKE '%Welcome%' OR "label" LIKE '%Welcome%';

\echo === Workspace Sidebar table columns ===
SELECT column_name FROM information_schema.columns WHERE table_name = 'tabWorkspace Sidebar' ORDER BY ordinal_position;

\echo === Workspace Sidebar rows (top) ===
SELECT * FROM "tabWorkspace Sidebar" LIMIT 5;
