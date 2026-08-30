SELECT datname FROM pg_database WHERE datistemplate=false;

SELECT 'distinct vehicles referenced in Job Order' AS what, count(DISTINCT "vehicle") FROM "tabVehicle Job Order" WHERE "vehicle" IS NOT NULL;
SELECT 'distinct vehicles referenced in Customer Vehicle' AS what, count(DISTINCT "vehicle") FROM "tabCustomer Vehicle" WHERE "vehicle" IS NOT NULL;
SELECT 'distinct vehicles referenced in Inspection' AS what, count(DISTINCT "vehicle") FROM "tabVehicle Inspection" WHERE "vehicle" IS NOT NULL;
