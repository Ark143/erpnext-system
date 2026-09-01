\echo === Workspace Card "POS" ===
SELECT "name", "label", "link_to", "type" FROM "tabWorkspace Card" WHERE "name" LIKE '%POS%' OR "label" LIKE '%POS%';

\echo === Workspace Shortcut "POS" or "Vehicle Analytics" ===
SELECT "name", "label", "link_to", "type" FROM "tabWorkspace Shortcut" WHERE "name" LIKE '%POS%' OR "label" LIKE '%POS%' OR "label" = 'Vehicle Analytics';
