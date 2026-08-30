import frappe
frappe.init(site="site1.local", sites_path="/workspace/frappe-bench/sites"); frappe.connect()

# --- Executive Dashboard API: fix augmented assignment on dict items ---
d = frappe.get_doc("Server Script", "Executive Dashboard API")
s = d.script
s = s.replace('zone_map[z]["bins_count"] += 1', 'zone_map[z]["bins_count"] = zone_map[z]["bins_count"] + 1')
s = s.replace('zone_map[z]["active_count"] += 1', 'zone_map[z]["active_count"] = zone_map[z]["active_count"] + 1')
assert '+= 1' not in s, "leftover += found"
d.script = s
d.save()
print("Executive Dashboard API: fixed augmented assignment")

# --- VM Company Dashboard API: fix date.replace() (RestrictedPython blocks __import__) ---
d2 = frappe.get_doc("Server Script", "VM Company Dashboard API")
s2 = d2.script
# Replace date.replace() calls with safe f-string date construction
s2 = s2.replace('today.replace(day=1).strftime("%Y-%m-%d")', 'f"{today.year}-{today.month:02d}-01"')
s2 = s2.replace('today.replace(month=1, day=1).strftime("%Y-%m-%d")', 'f"{today.year}-01-01"')
s2 = s2.replace('today.replace(year=today.year - 1, month=1, day=1).strftime("%Y-%m-%d")', 'f"{today.year - 1:04d}-01-01"')
s2 = s2.replace('today.replace(year=today.year - 1, month=12, day=31).strftime("%Y-%m-%d")', 'f"{today.year - 1:04d}-12-31"')
assert 'today.replace' not in s2, "leftover date.replace found"
d2.script = s2
d2.save()
print("VM Company Dashboard API: fixed date.replace")
frappe.db.commit()
