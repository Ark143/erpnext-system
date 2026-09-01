\echo === Items ===
SELECT 'item_total' AS k, count(*) AS v FROM "tabItem";
SELECT 'item_company_set' AS k, count(*) AS v FROM "tabItem" WHERE "company" IS NOT NULL AND "company" <> '';
SELECT DISTINCT "company" FROM "tabItem" WHERE "company" IS NOT NULL AND "company" <> '' LIMIT 10;

\echo === Customers ===
SELECT 'customer_total' AS k, count(*) AS v FROM "tabCustomer";
SELECT 'customer_company_set' AS k, count(*) AS v FROM "tabCustomer" WHERE "company" IS NOT NULL AND "company" <> '';
SELECT DISTINCT "company" FROM "tabCustomer" WHERE "company" IS NOT NULL AND "company" <> '' LIMIT 10;

\echo === Suppliers ===
SELECT 'supplier_total' AS k, count(*) AS v FROM "tabSupplier";
SELECT 'supplier_company_set' AS k, count(*) AS v FROM "tabSupplier" WHERE "company" IS NOT NULL AND "company" <> '';
SELECT DISTINCT "company" FROM "tabSupplier" WHERE "company" IS NOT NULL AND "company" <> '' LIMIT 10;

\echo === User Permissions ===
SELECT count(*) AS user_permissions FROM "tabUser Permission";
SELECT DISTINCT "for_value", "allow" FROM "tabUser Permission";

\echo === Companies ===
SELECT "name", "is_group" FROM "tabCompany" ORDER BY "is_group", "name";
