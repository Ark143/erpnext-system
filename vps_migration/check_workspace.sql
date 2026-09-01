\echo === Vehicle Management Workspace content ===
SELECT "name", "label", "title" FROM "tabWorkspace" WHERE "name" LIKE '%ehicle%';

\echo === Workspace Shortcut full list ===
SELECT "name", "label", "link_to", "type", "icon" FROM "tabWorkspace Shortcut" ORDER BY "name";
