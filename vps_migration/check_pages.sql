\echo === All Workspace Shortcuts (to see naming pattern) ===
SELECT "name", "label", "link_to", "type" FROM "tabWorkspace Shortcut" ORDER BY "name";

\echo === Does a Page 'vehicle_pos' exist in tabPage? ===
SELECT "name", "module", "standard" FROM "tabPage" WHERE "name" IN ('vehicle_pos','vehicle_analytics','pos');
