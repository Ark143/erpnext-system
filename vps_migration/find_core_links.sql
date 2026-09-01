\echo === Workspace Sidebar for Core module (Build/Data/Users/System) ===
SELECT "name", "title", "module" FROM "tabWorkspace Sidebar" WHERE "module" = 'Core';

\echo === Workspace Link child table: all links with link_type=Workspace ===
SELECT "name", "parent", "label", "link_to", "link_type" FROM "tabWorkspace Link" WHERE "link_type" = 'Workspace' ORDER BY "parent", "idx";

\echo === Workspace Link for Core/Build sidebar parents ===
SELECT "name", "parent", "parentfield", "label", "link_to", "link_type" FROM "tabWorkspace Link" WHERE "parent" IN ('Build','System','Users','Data','Core') ORDER BY "parent";
