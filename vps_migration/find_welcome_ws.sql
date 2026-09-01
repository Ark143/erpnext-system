\echo === Find the orphan 'Welcome Workspace' link (Workspace Sidebar Item / Link) ===
SELECT "name", "parent", "parentfield", "label", "link_to", "link_type" FROM "tabWorkspace Sidebar Item"
WHERE "link_to" = 'Welcome Workspace' OR "label" = 'Welcome Workspace';

\echo === Workspace 'Welcome Workspace' exists? ===
SELECT "name", "title" FROM "tabWorkspace" WHERE "name" LIKE '%Welcome%' OR "title" LIKE '%Welcome%';

\echo === Core sidebar (parent) ===
SELECT "name", "label", "type" FROM "tabWorkspace Sidebar" WHERE "label" LIKE '%Core%' OR "name" LIKE '%core%';
