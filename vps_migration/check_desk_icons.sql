\echo === Desktop Icons (any null link_to/label?) ===
SELECT "name", "label", "link_to", "link_type", "module_name"
FROM "tabDesktop Icon"
WHERE "link_to" IS NULL OR "link_to" = '' OR "label" IS NULL OR "label" = ''
ORDER BY "name";

\echo === All Desktop Icons ===
SELECT "name", "label", "link_to", "link_type" FROM "tabDesktop Icon" ORDER BY "name";

\echo === Workspace shortcuts (null link?) ===
SELECT "name", "label", "link_to", "type" FROM "tabWorkspace Shortcut"
WHERE "link_to" IS NULL OR "link_to" = '' ORDER BY "name";
