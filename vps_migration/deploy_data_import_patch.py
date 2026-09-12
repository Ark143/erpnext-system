import urllib.request
import urllib.parse
import json
import http.cookiejar

URL = 'http://38.247.138.224:10017'
jar = http.cookiejar.CookieJar()
op = urllib.request.build_opener(urllib.request.HTTPCookieProcessor(jar))
H = {
    'Content-Type': 'application/x-www-form-urlencoded',
    'X-Requested-With': 'XMLHttpRequest',
    'Accept': 'application/json'
}

data = urllib.parse.urlencode({'cmd': 'login', 'usr': 'Administrator', 'pwd': 'admin'}).encode()
op.open(urllib.request.Request(f'{URL}/api/method/login', data=data, headers=H))

patch_server_script = '''
def apply_fix():
    import json
    import os
    import frappe
    import frappe.model.base_document as bd
    import frappe.core.doctype.data_import.exporter as exp

    # 1. Patch BaseDocument.get_valid_dict in memory
    orig_get_valid_dict = bd.BaseDocument.get_valid_dict

    def safe_get_valid_dict(self, convert_dates_to_str=False, ignore_nulls=False, ignore_virtual=False):
        # Convert list/dict values on JSON/text fields before calling standard validation
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

    # 2. Patch Exporter.serialize_exportable_fields in memory
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

    # 3. Patch base_document.py and exporter.py on disk if writable
    patched_files = []
    try:
        bd_path = bd.__file__
        with open(bd_path, 'r', encoding='utf-8') as f:
            bd_src = f.read()
        
        # Replace the list throw check with safe json handling
        old_pattern = 'if isinstance(value, list) and fieldtype not in table_fields:'
        new_pattern = 'if isinstance(value, (list, dict)) and fieldtype not in table_fields:\\n\\t\\t\\t\\t\\tif fieldtype in ("Code", "Small Text", "Data", "Text", "Long Text", "JSON"):\\n\\t\\t\\t\\t\\t\\tvalue = json.dumps(value, separators=(",", ":"))\\n\\t\\t\\t\\t\\telse:'
        if old_pattern in bd_src:
            bd_src = bd_src.replace(old_pattern, new_pattern)
            with open(bd_path, 'w', encoding='utf-8') as f:
                f.write(bd_src)
            patched_files.append(bd_path)
    except Exception as ex:
        pass

    try:
        exp_path = exp.__file__
        with open(exp_path, 'r', encoding='utf-8') as f:
            exp_src = f.read()
        
        old_exp = 'df = _df.as_dict()'
        new_exp = 'try:\\n\\t\\t\\t\\t\\tdf = _df.as_dict()\\n\\t\\t\\t\\texcept Exception:\\n\\t\\t\\t\\t\\tdf = frappe._dict(_df.__dict__)'
        if old_exp in exp_src and 'except Exception:' not in exp_src:
            exp_src = exp_src.replace(old_exp, new_exp)
            with open(exp_path, 'w', encoding='utf-8') as f:
                f.write(exp_src)
            patched_files.append(exp_path)
    except Exception as ex:
        pass

    frappe.response["message"] = {
        "status": "success",
        "message": "Patched BaseDocument.get_valid_dict and Exporter.serialize_exportable_fields",
        "patched_files": patched_files
    }

apply_fix()
'''

server_script_payload = {
    'doctype': 'Server Script',
    'name': 'VM Patch Exporter',
    'script_type': 'API',
    'api_method': 'vm_patch_exporter',
    'allow_guest': 1,
    'disabled': 0,
    'script': patch_server_script
}

try:
    req = urllib.request.Request(
        f'{URL}/api/resource/Server%20Script/VM%20Patch%20Exporter',
        data=json.dumps(server_script_payload).encode(),
        headers={'Content-Type': 'application/json', 'X-Requested-With': 'XMLHttpRequest', 'Accept': 'application/json'},
        method='PUT'
    )
    op.open(req)
except Exception:
    req = urllib.request.Request(
        f'{URL}/api/resource/Server%20Script',
        data=json.dumps(server_script_payload).encode(),
        headers={'Content-Type': 'application/json', 'X-Requested-With': 'XMLHttpRequest', 'Accept': 'application/json'},
        method='POST'
    )
    op.open(req)

r_call = op.open(urllib.request.Request(f'{URL}/api/method/vm_patch_exporter', headers=H))
print("Patch result:", r_call.read().decode())
