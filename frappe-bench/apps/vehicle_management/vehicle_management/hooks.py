app_name = "vehicle_management"
app_title = "Vehicle Management"
app_icon = "fa fa-car"
app_publisher = "Autometrik"
app_description = "Vehicle Management Module for Customer Vehicles, Job Orders, and Inspections"
app_email = "admin@erp.local"
app_license = "mit"

# Apps
# ------------------

# required_apps = []

# Each item in the list will be shown as an app in the apps page
add_to_apps_screen = [
	{
		"name": "vehicle_management",
		"logo": "/assets/frappe/images/frappe-framework-logo.svg",
		"title": "Vehicle Management",
		"route": "/desk/vehicle-management",
	}
]

# Includes in <head>
# ------------------

# include js, css files in header of desk.html
app_include_css = "/assets/vehicle_management/css/vehicle_management_desk.css"
app_include_js = [
	"/assets/vehicle_management/js/vehicle_relationship_map.js",
	"/assets/vehicle_management/js/vehicle_management_desk.js"
]

# include js, css files in header of web template
# web_include_css = "/assets/vehicle_management/css/vehicle_management.css"
# web_include_js = "/assets/vehicle_management/js/vehicle_management.js"

# include custom scss in every website theme (without file extension ".scss")
# website_theme_scss = "vehicle_management/public/scss/website"

# include js, css files in header of web form
# webform_include_js = {"doctype": "public/js/doctype.js"}
# webform_include_css = {"doctype": "public/css/doctype.css"}

# include js in page
page_js = {
	"vehicle_pos": "public/js/vehicle_pos.js",
	"vehicle_analytics": "public/js/vehicle_analytics.js",
	"vehicle_relationship_map": "public/js/vehicle_relationship_map.js"
}

doctype_js = {
	"Item": "public/js/item.js",
	"Customer": "public/js/customer.js",
	"Customer Vehicle": "public/js/vehicle_transaction.js",
	"Vehicle Job Order": "public/js/vehicle_transaction.js",
	"Vehicle Estimate": "public/js/vehicle_transaction.js",
	"Vehicle Inspection": "public/js/vehicle_transaction.js",
	"Vehicle POS Invoice": "public/js/vehicle_transaction.js",
	"Quotation": "public/js/vehicle_transaction.js",
	"Sales Order": "public/js/vehicle_transaction.js",
	"Delivery Note": "public/js/vehicle_transaction.js",
	"Sales Invoice": "public/js/vehicle_transaction.js",
	"POS Invoice": "public/js/vehicle_transaction.js",
	"Stock Entry": "public/js/vehicle_transaction.js",
	"Payment Entry": "public/js/vehicle_transaction.js"
}

# Svg Icons
# ------------------
# include app icons in desk
# app_include_icons = "vehicle_management/public/icons.svg"

# Home Pages
# ----------

# application home page (will override Website Settings)
# home_page = "login"

# website user home page (by Role)
# role_home_page = {
# 	"Role": "home_page"
# }

# Generators
# ----------

# automatically create page for each record of this doctype
# website_generators = ["Web Page"]

# automatically load and sync documents of this doctype from downstream apps
# importable_doctypes = [doctype_1]

# Jinja
# ----------

# add methods and filters to jinja environment
# jinja = {
# 	"methods": "vehicle_management.utils.jinja_methods",
# 	"filters": "vehicle_management.utils.jinja_filters"
# }

# Installation
# ------------

# before_install = "vehicle_management.install.before_install"
# after_install = "vehicle_management.install.after_install"

# Uninstallation
# ------------

# before_uninstall = "vehicle_management.uninstall.before_uninstall"
# after_uninstall = "vehicle_management.uninstall.after_uninstall"

# Integration Setup
# ------------------
# To set up dependencies/integrations with other apps
# Name of the app being installed is passed as an argument

# before_app_install = "vehicle_management.utils.before_app_install"
# after_app_install = "vehicle_management.utils.after_app_install"

# Integration Cleanup
# -------------------
# To clean up dependencies/integrations with other apps
# Name of the app being uninstalled is passed as an argument

# before_app_uninstall = "vehicle_management.utils.before_app_uninstall"
# after_app_uninstall = "vehicle_management.utils.after_app_uninstall"

# Build
# ------------------
# To hook into the build process

# after_build = "vehicle_management.build.after_build"

# Desk Notifications
# ------------------
# See frappe.core.notifications.get_notification_config

# notification_config = "vehicle_management.notifications.get_notification_config"

# Permissions
# -----------
# Permissions evaluated in scripted ways

permission_query_conditions = {
	"Customer Vehicle": "vehicle_management.permissions.get_customer_vehicle_query_conditions",
	"Vehicle Job Order": "vehicle_management.permissions.get_vehicle_job_order_query_conditions",
	"Vehicle Inspection": "vehicle_management.permissions.get_vehicle_inspection_query_conditions",
	"Vehicle Service Reminder": "vehicle_management.permissions.get_vehicle_service_reminder_query_conditions",
}

has_permission = {
	"Customer Vehicle": "vehicle_management.permissions.has_vehicle_permission",
	"Vehicle Job Order": "vehicle_management.permissions.has_vehicle_permission",
	"Vehicle Inspection": "vehicle_management.permissions.has_vehicle_permission",
	"Vehicle Service Reminder": "vehicle_management.permissions.has_vehicle_permission",
}

# Document Events
# ---------------
# Hook on document methods and events

doc_events = {
	"Sales Invoice": {
		"on_update_after_submit": "vehicle_management.vehicle_management.doctype.vehicle_job_order.vehicle_job_order.sync_invoice_payment_to_job_order",
		"on_cancel": "vehicle_management.vehicle_management.doctype.vehicle_job_order.vehicle_job_order.sync_invoice_payment_to_job_order",
		"on_change": "vehicle_management.vehicle_management.doctype.vehicle_job_order.vehicle_job_order.sync_invoice_payment_to_job_order",
	}
}

# Scheduled Tasks
# ---------------

# scheduler_events = {
# 	"all": [
# 		"vehicle_management.tasks.all"
# 	],
# 	"daily": [
# 		"vehicle_management.tasks.daily"
# 	],
# 	"hourly": [
# 		"vehicle_management.tasks.hourly"
# 	],
# 	"weekly": [
# 		"vehicle_management.tasks.weekly"
# 	],
# 	"monthly": [
# 		"vehicle_management.tasks.monthly"
# 	],
# }

# Testing
# -------

# before_tests = "vehicle_management.install.before_tests"

# Extend DocType Class
# ------------------------------
#
# Specify custom mixins to extend the standard doctype controller.
# extend_doctype_class = {
# 	"Task": "vehicle_management.custom.task.CustomTaskMixin"
# }

# Overriding Methods
# ------------------------------
#
override_whitelisted_methods = {
	"frappe.desk.notifications.get_open_count": "vehicle_management.notifications_patch.get_open_count"
}

#
# each overriding function accepts a `data` argument;
# generated from the base implementation of the doctype dashboard,
# along with any modifications made in other Frappe apps
# override_doctype_dashboards = {
# 	"Task": "vehicle_management.task.get_dashboard_data"
# }

# exempt linked doctypes from being automatically cancelled
#
# auto_cancel_exempted_doctypes = ["Auto Repeat"]

# Ignore links to specified DocTypes when deleting documents
# -----------------------------------------------------------

# ignore_links_on_delete = ["Communication", "ToDo"]

# Request Events
# ----------------
# before_request = ["vehicle_management.utils.before_request"]
# after_request = ["vehicle_management.utils.after_request"]

# Job Events
# ----------
# before_job = ["vehicle_management.utils.before_job"]
# after_job = ["vehicle_management.utils.after_job"]

# User Data Protection
# --------------------

# user_data_fields = [
# 	{
# 		"doctype": "{doctype_1}",
# 		"filter_by": "{filter_by}",
# 		"redact_fields": ["{field_1}", "{field_2}"],
# 		"partial": 1,
# 	},
# 	{
# 		"doctype": "{doctype_2}",
# 		"filter_by": "{filter_by}",
# 		"partial": 1,
# 	},
# 	{
# 		"doctype": "{doctype_3}",
# 		"strict": False,
# 	},
# 	{
# 		"doctype": "{doctype_4}"
# 	}
# ]

# Authentication and authorization
# --------------------------------

# auth_hooks = [
# 	"vehicle_management.auth.validate"
# ]

# Automatically update python controller files with type annotations for this app.
# export_python_type_annotations = True

# default_log_clearing_doctypes = {
# 	"Logging DocType Name": 30  # days to retain logs
# }

# Translation
# ------------
# List of apps whose translatable strings should be excluded from this app's translations.
# ignore_translatable_strings_from = []

