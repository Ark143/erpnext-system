\echo === All Workspace Sidebar Item rows referencing Welcome ===
SELECT "name", "parent", "parentfield", "label", "link_to", "link_type", "type" FROM "tabWorkspace Sidebar Item"
WHERE "link_to" ILIKE '%welcome%' OR "label" ILIKE '%welcome%';

\echo === Which sidebar has 'core' items? list distinct parents + their sidebar title ===
SELECT DISTINCT s."name" AS sidebar_name, s."title" AS sidebar_title, s."module"
FROM "tabWorkspace Sidebar" s
JOIN "tabWorkspace Sidebar Item" i ON i."parent" = s."name"
ORDER BY s."name";

\echo === Sidebar items whose parent sidebar module = Core ===
SELECT i."name", i."parent", i."label", i."link_to", i."link_type", i."type"
FROM "tabWorkspace Sidebar Item" i
JOIN "tabWorkspace Sidebar" s ON s."name" = i."parent"
WHERE s."module" = 'Core'
ORDER BY i."parent", i."idx";
