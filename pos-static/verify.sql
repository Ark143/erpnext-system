SELECT 'Customer' AS doc, count(*) FROM "tabCustomer"
UNION ALL SELECT 'Item', count(*) FROM "tabItem"
UNION ALL SELECT 'Sales Invoice', count(*) FROM "tabSales Invoice"
UNION ALL SELECT 'Vehicle (MASTER)', count(*) FROM "tabVehicle"
UNION ALL SELECT 'Vehicle Job Order', count(*) FROM "tabVehicle Job Order"
UNION ALL SELECT 'Vehicle Inspection', count(*) FROM "tabVehicle Inspection"
UNION ALL SELECT 'Customer Vehicle', count(*) FROM "tabCustomer Vehicle";

SELECT 'orphaned Job Order refs (vehicle missing)' AS check, count(*) FROM "tabVehicle Job Order" WHERE "vehicle" NOT IN (SELECT name FROM "tabVehicle");
