import urllib.request, json

opener = urllib.request.build_opener(urllib.request.HTTPCookieProcessor())
opener.open('http://38.247.138.224:10017/api/method/login', data=b'usr=Administrator&pwd=admin')
H = {'Content-Type': 'application/json', 'Accept': 'application/json'}

# 1. Client Script for Vehicle Job Order
vjo_js = """
frappe.ui.form.on('Vehicle Job Order', {
    setup: function(frm) {
        if (frm.meta && frm.meta.__dashboard) {
            frm.meta.__dashboard.method = "vm_get_open_count";
            frm.meta.__dashboard.internal_links = {
                "Customer Vehicle": "vehicle",
                "Customer": "customer",
                "Vehicle Estimate": "estimate",
                "Sales Invoice": "sales_invoice"
            };
            if (frm.meta.__dashboard.non_standard_fieldnames) {
                delete frm.meta.__dashboard.non_standard_fieldnames["Customer"];
                delete frm.meta.__dashboard.non_standard_fieldnames["Customer Vehicle"];
            }
        }
    },
    onload_post_render: function(frm) {
        if (frm.dashboard && frm.dashboard.data) {
            frm.dashboard.data.method = "vm_get_open_count";
            frm.dashboard.data.internal_links = {
                "Customer Vehicle": "vehicle",
                "Customer": "customer",
                "Vehicle Estimate": "estimate",
                "Sales Invoice": "sales_invoice"
            };
            if (frm.dashboard.data.non_standard_fieldnames) {
                delete frm.dashboard.data.non_standard_fieldnames["Customer"];
                delete frm.dashboard.data.non_standard_fieldnames["Customer Vehicle"];
            }
            frm.dashboard.set_open_count();
        }
    },
    refresh: function(frm) {
        if (frm.dashboard && frm.dashboard.data) {
            frm.dashboard.data.method = "vm_get_open_count";
            frm.dashboard.data.internal_links = {
                "Customer Vehicle": "vehicle",
                "Customer": "customer",
                "Vehicle Estimate": "estimate",
                "Sales Invoice": "sales_invoice"
            };
            if (frm.dashboard.data.non_standard_fieldnames) {
                delete frm.dashboard.data.non_standard_fieldnames["Customer"];
                delete frm.dashboard.data.non_standard_fieldnames["Customer Vehicle"];
            }
        }
    }
});
"""

script_doc = {
    'doctype': 'Client Script',
    'name': 'Vehicle Job Order Dashboard Fix',
    'dt': 'Vehicle Job Order',
    'view': 'Form',
    'enabled': 1,
    'script': vjo_js
}

try:
    req = urllib.request.Request('http://38.247.138.224:10017/api/resource/Client%20Script/Vehicle%20Job%20Order%20Dashboard%20Fix', data=json.dumps(script_doc).encode(), headers=H, method='PUT')
    res = opener.open(req)
    print("Updated Client Script 'Vehicle Job Order Dashboard Fix'")
except Exception:
    req = urllib.request.Request('http://38.247.138.224:10017/api/resource/Client%20Script', data=json.dumps(script_doc).encode(), headers=H, method='POST')
    res = opener.open(req)
    print("Created Client Script 'Vehicle Job Order Dashboard Fix'")


# 2. Client Script for Vehicle Estimate
ve_js = """
frappe.ui.form.on('Vehicle Estimate', {
    setup: function(frm) {
        if (frm.meta && frm.meta.__dashboard) {
            frm.meta.__dashboard.method = "vm_get_open_count";
            frm.meta.__dashboard.internal_links = {
                "Customer Vehicle": "vehicle",
                "Customer": "customer",
                "Vehicle Job Order": "job_order"
            };
            if (frm.meta.__dashboard.non_standard_fieldnames) {
                delete frm.meta.__dashboard.non_standard_fieldnames["Customer"];
                delete frm.meta.__dashboard.non_standard_fieldnames["Customer Vehicle"];
            }
        }
    },
    onload_post_render: function(frm) {
        if (frm.dashboard && frm.dashboard.data) {
            frm.dashboard.data.method = "vm_get_open_count";
            frm.dashboard.data.internal_links = {
                "Customer Vehicle": "vehicle",
                "Customer": "customer",
                "Vehicle Job Order": "job_order"
            };
            if (frm.dashboard.data.non_standard_fieldnames) {
                delete frm.dashboard.data.non_standard_fieldnames["Customer"];
                delete frm.dashboard.data.non_standard_fieldnames["Customer Vehicle"];
            }
            frm.dashboard.set_open_count();
        }
    },
    refresh: function(frm) {
        if (frm.dashboard && frm.dashboard.data) {
            frm.dashboard.data.method = "vm_get_open_count";
            frm.dashboard.data.internal_links = {
                "Customer Vehicle": "vehicle",
                "Customer": "customer",
                "Vehicle Job Order": "job_order"
            };
            if (frm.dashboard.data.non_standard_fieldnames) {
                delete frm.dashboard.data.non_standard_fieldnames["Customer"];
                delete frm.dashboard.data.non_standard_fieldnames["Customer Vehicle"];
            }
        }
    }
});
"""

script_doc = {
    'doctype': 'Client Script',
    'name': 'Vehicle Estimate Dashboard Fix',
    'dt': 'Vehicle Estimate',
    'view': 'Form',
    'enabled': 1,
    'script': ve_js
}

try:
    req = urllib.request.Request('http://38.247.138.224:10017/api/resource/Client%20Script/Vehicle%20Estimate%20Dashboard%20Fix', data=json.dumps(script_doc).encode(), headers=H, method='PUT')
    res = opener.open(req)
    print("Updated Client Script 'Vehicle Estimate Dashboard Fix'")
except Exception:
    req = urllib.request.Request('http://38.247.138.224:10017/api/resource/Client%20Script', data=json.dumps(script_doc).encode(), headers=H, method='POST')
    res = opener.open(req)
    print("Created Client Script 'Vehicle Estimate Dashboard Fix'")


# 3. Client Script for Customer Vehicle
cv_js = """
frappe.ui.form.on('Customer Vehicle', {
    setup: function(frm) {
        if (frm.meta && frm.meta.__dashboard) {
            frm.meta.__dashboard.method = "vm_get_open_count";
            frm.meta.__dashboard.internal_links = {
                "Customer": "customer"
            };
        }
    },
    onload_post_render: function(frm) {
        if (frm.dashboard && frm.dashboard.data) {
            frm.dashboard.data.method = "vm_get_open_count";
            frm.dashboard.data.internal_links = {
                "Customer": "customer"
            };
            frm.dashboard.set_open_count();
        }
    },
    refresh: function(frm) {
        if (frm.dashboard && frm.dashboard.data) {
            frm.dashboard.data.method = "vm_get_open_count";
            frm.dashboard.data.internal_links = {
                "Customer": "customer"
            };
        }
    }
});
"""

script_doc = {
    'doctype': 'Client Script',
    'name': 'Customer Vehicle Dashboard Fix',
    'dt': 'Customer Vehicle',
    'view': 'Form',
    'enabled': 1,
    'script': cv_js
}

try:
    req = urllib.request.Request('http://38.247.138.224:10017/api/resource/Client%20Script/Customer%20Vehicle%20Dashboard%20Fix', data=json.dumps(script_doc).encode(), headers=H, method='PUT')
    res = opener.open(req)
    print("Updated Client Script 'Customer Vehicle Dashboard Fix'")
except Exception:
    req = urllib.request.Request('http://38.247.138.224:10017/api/resource/Client%20Script', data=json.dumps(script_doc).encode(), headers=H, method='POST')
    res = opener.open(req)
    print("Created Client Script 'Customer Vehicle Dashboard Fix'")

print("All Form Dashboard Client Scripts successfully deployed!")
