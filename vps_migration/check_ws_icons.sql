\echo === Desktop Icons: label with only whitespace, or name!=label mismatch ===
SELECT "name", "label", "link_to", "link_type", char_length("label") AS lab_len
FROM "tabDesktop Icon"
WHERE char_length(btrim(coalesce("label",''))) = 0 OR "label" IS NULL
ORDER BY "name";

\echo === ALL icons with label + link_type + idx (full dump for eyeball) ===
SELECT "name", "label", "link_to", "link_type" FROM "tabDesktop Icon" ORDER BY "name";
