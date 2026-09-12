import json
import frappe
from frappe import _
import frappe.model.base_document as bd
import frappe.core.doctype.data_import.exporter as exp


def patch_exporter_and_base_document():
	"""
	Patches BaseDocument.get_valid_dict and Exporter.serialize_exportable_fields
	to safely handle DocFields containing list/dict attributes (such as link_filters in PostgreSQL)
	and prevent 'Value for Filters cannot be a list' validation errors.
	"""
	# 1. Patch BaseDocument.get_valid_dict
	if not getattr(bd.BaseDocument, "_vm_data_import_patched", False):
		orig_get_valid_dict = bd.BaseDocument.get_valid_dict

		def safe_get_valid_dict(self, convert_dates_to_str=False, ignore_nulls=False, ignore_virtual=False):
			# Convert list/dict values on JSON/text-like fields before calling standard validation
			for df in (self.meta.get("fields") or []):
				val = self.get(df.fieldname)
				if isinstance(val, (list, dict)) and df.fieldtype not in frappe.model.table_fields:
					if df.fieldtype in ("Code", "Small Text", "Data", "Text", "Long Text", "JSON"):
						self.set(df.fieldname, json.dumps(val, separators=(",", ":")))

			try:
				return orig_get_valid_dict(self, convert_dates_to_str, ignore_nulls, ignore_virtual)
			except Exception as e:
				if "cannot be a list" in str(e):
					res = {}
					for df in (self.meta.get("fields") or []):
						val = self.get(df.fieldname)
						if isinstance(val, (list, dict)) and df.fieldtype not in frappe.model.table_fields:
							val = json.dumps(val, separators=(",", ":"))
						res[df.fieldname] = val
					return res
				raise

		bd.BaseDocument.get_valid_dict = safe_get_valid_dict
		bd.BaseDocument._vm_data_import_patched = True

	# 2. Patch Exporter.serialize_exportable_fields
	if not getattr(exp.Exporter, "_vm_data_import_patched", False):
		def safe_serialize_exportable_fields(self):
			fields = []
			for key, exportable_fields in self.exportable_fields.items():
				for _df in exportable_fields:
					if hasattr(_df, "as_dict"):
						try:
							df = _df.as_dict()
						except Exception:
							df = frappe._dict({k: v for k, v in getattr(_df, "__dict__", {}).items() if not k.startswith("_")})
					elif hasattr(_df, "copy"):
						df = _df.copy()
					else:
						df = frappe._dict(_df)

					df.is_child_table_field = key != self.doctype
					if df.is_child_table_field:
						df.child_table_df = self.meta.get_field(key)
					fields.append(df)
			return fields

		exp.Exporter.serialize_exportable_fields = safe_serialize_exportable_fields
		exp.Exporter._vm_data_import_patched = True


# Apply patches immediately upon module import
try:
	patch_exporter_and_base_document()
except Exception:
	pass


@frappe.whitelist()
def download_template(
	doctype: str,
	export_fields=None,
	export_records=None,
	export_filters=None,
	file_type: str = "CSV",
):
	"""
	Safe handler for downloading Data Import templates across all DocTypes.
	"""
	patch_exporter_and_base_document()
	from frappe.core.doctype.data_import.exporter import Exporter

	if isinstance(export_fields, str):
		export_fields = json.loads(export_fields)
	if isinstance(export_filters, str):
		export_filters = json.loads(export_filters)

	export_data = export_records != "blank_template"

	e = Exporter(
		doctype,
		export_fields=export_fields or {},
		export_data=export_data,
		export_filters=export_filters,
		file_type=file_type,
		export_page_length=5 if export_records == "5_records" else None,
	)
	e.build_response()
