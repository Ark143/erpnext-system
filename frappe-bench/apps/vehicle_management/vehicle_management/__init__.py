__version__ = "0.0.1"

# Initialize critical patches for Postgres and Frappe data import
try:
	import vehicle_management.data_import_patch
except Exception:
	pass
