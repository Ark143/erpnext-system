\echo === Desktop Icons with NULL/empty label ===
SELECT "name", "label", "link_to", "link_type" FROM "tabDesktop Icon"
WHERE "label" IS NULL OR "label" = ''
ORDER BY "name";

\echo === Desktop Icons with NULL link_type ===
SELECT "name", "label", "link_to", "link_type" FROM "tabDesktop Icon"
WHERE "link_type" IS NULL OR "link_type" = ''
ORDER BY "name";

\echo === count ===
SELECT count(*) AS total FROM "tabDesktop Icon";
