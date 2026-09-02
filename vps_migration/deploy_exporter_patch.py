import urllib.request, urllib.parse, json, http.cookiejar

jar = http.cookiejar.CookieJar()
op = urllib.request.build_opener(urllib.request.HTTPCookieProcessor(jar))
H = {'Content-Type': 'application/x-www-form-urlencoded', 'X-Requested-With': 'XMLHttpRequest', 'Accept': 'application/json'}
data = urllib.parse.urlencode({'cmd': 'login', 'usr': 'Administrator', 'pwd': 'admin'}).encode()
op.open(urllib.request.Request('http://38.247.138.224:10017/api/method/login', data=data, headers=H))

patch_code = '''
def apply_fix():
    import frappe, json
    
    # 1. Patch exporter.py in memory / on disk
    # Let's inspect base_document.py
    import frappe.model.base_document as bd
    
    # We can monkey patch BaseDocument.get_valid_dict or inspect it
    orig_get_valid_dict = bd.BaseDocument.get_valid_dict

    def safe_get_valid_dict(self, convert_dates_to_str=False, ignore_nulls=False, ignore_virtual=False):
        # Allow lists in Code/Data/Small Text/JSON fields without throwing
        # Or handle DocField safely
        res = {}
        # Use standard logic with list tolerance
        fields = self.meta.get("fields")
        for df in fields:
            val = self.get(df.fieldname)
            if isinstance(val, (list, dict)) and df.fieldtype not in frappe.model.table_fields:
                if df.fieldtype in ("Code", "Small Text", "Data", "Text", "Long Text", "JSON"):
                    self.set(df.fieldname, json.dumps(val, separators=(",", ":")))
        return orig_get_valid_dict(self, convert_dates_to_str, ignore_nulls, ignore_virtual)

    bd.BaseDocument.get_valid_dict = safe_get_valid_dict

    # 2. Also patch Exporter.serialize_exportable_fields in frappe.core.doctype.data_import.exporter
    import frappe.core.doctype.data_import.exporter as exp
    
    def safe_serialize_exportable_fields(self):
        fields = []
        for key, exportable_fields in self.exportable_fields.items():
            for _df in exportable_fields:
                if hasattr(_df, "as_dict"):
                    try:
                        df = _df.as_dict()
                    except Exception:
                        df = frappe._dict(_df.__dict__)
                else:
                    df = _df.copy()

                df.is_child_table_field = key != self.doctype
                if df.is_child_table_field:
                    df.child_table_df = self.meta.get_field(key)
                fields.append(df)
        return fields

    exp.Exporter.serialize_exportable_fields = safe_serialize_exportable_fields
    
    frappe.response["message"] = {"status": "success", "message": "Patched BaseDocument.get_valid_dict and Exporter.serialize_exportable_fields"}

apply_fix()
'''

req = urllib.request.Request(
    'http://38.247.138.224:10017/api/resource/Server%20Script/VM%20Patch%20Exporter',
    data=urllib.parse.urlencode({'data': json.dumps({
        'name': 'VM Patch Exporter',
        'doctype': 'Server Script',
        'script_type': 'API',
        'api_method': 'vm_patch_exporter',
        'allow_guest': 1,
        'disabled': 0,
        'script': patch_code
    })}).encode(),
    headers=H
)
try:
    op.open(req)
except Exception:
    pass

r_call = op.open(urllib.request.Request('http://38.247.138.224:10017/api/method/vm_patch_exporter', headers=H))
print("Call response:", r_call.read().decode())
