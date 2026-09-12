import frappe

EXCLUDED_DOCTYPES = {
	"DocType",
	"DocField",
	"DocPerm",
	"Custom Field",
	"Server Script",
	"Client Script",
	"Property Setter",
	"DocType Layout",
	"Custom DocPerm",
	"Workspace",
	"Workspace Shortcut",
	"Workspace Link",
	"Workspace Quick List",
	"Workspace Sidebar Item",
	"Print Format",
	"Web Page",
	"Page",
	"Web Form",
	"User",
	"Role",
	"Has Role",
	"User Permission",
	"System Settings",
	"Website Settings",
	"Version",
	"Access Log",
	"Activity Log",
	"Patch Log",
	"Installed Application",
	"File",
	"Translation",
	"Log Setting",
	"OAuth Client",
	"OAuth Bearer Token",
	"Scheduled Job Type",
	"Email Account",
	"Email Domain",
	"Email Queue",
	"Notification",
	"Auto Email Report",
	"Prepared Report",
	"Report",
	"Workflow",
	"Workflow State",
	"Workflow Action",
	"Module Def",
	"App Def",
	"Data Import",
	"Data Import Log",
}

EXCLUDED_FIELD_KEYWORDS = (
	"email",
	"password",
	"pwd",
	"api_key",
	"api_secret",
	"secret",
	"token",
	"auth",
	"hash",
	"route",
	"page_name",
	"slug",
	"url",
	"website",
	"domain",
	"file",
	"image",
	"icon",
	"logo",
	"avatar",
	"attachment",
	"css",
	"js",
	"script",
	"json",
	"sql",
	"python",
	"code",
	"html",
	"naming_series",
	"amended_from",
	"reference_doctype",
	"language",
	"locale",
	"color",
	"barcode",
	"workflow_state",
)

CONVERTIBLE_FIELDTYPES = {"Data", "Small Text", "Text", "Long Text"}


def auto_uppercase_doc(doc, method=None):
	"""
	System-wide hook that automatically converts all text and master data fields to ALL CAPS.
	Exempts passwords, emails, URLs, code, and system metadata.
	"""
	if not doc or not getattr(doc, "doctype", None):
		return

	if doc.doctype in EXCLUDED_DOCTYPES:
		return

	# Convert main document fields
	_uppercase_fields(doc)

	# Convert child table fields
	for child in doc.get_all_children():
		if child.doctype not in EXCLUDED_DOCTYPES:
			_uppercase_fields(child)


def _uppercase_fields(d):
	meta = getattr(d, "meta", None)
	if not meta:
		try:
			meta = frappe.get_meta(d.doctype)
		except Exception:
			return

	for df in meta.fields:
		if df.fieldtype not in CONVERTIBLE_FIELDTYPES:
			continue

		fieldname = df.fieldname
		if not fieldname:
			continue

		fn_lower = fieldname.lower()
		if any(kw in fn_lower for kw in EXCLUDED_FIELD_KEYWORDS):
			continue

		# Check field options / special types
		options = str(getattr(df, "options", "") or "").strip().lower()
		if options in ("email", "url", "phone", "password", "attach", "attach image"):
			continue

		val = d.get(fieldname)
		if isinstance(val, str) and val:
			# Do not alter email-like strings
			if "@" in val and "." in val and not any(ch in val for ch in ("\n", " ", ",", ";")):
				continue

			# Do not alter URL-like strings
			if val.startswith("http://") or val.startswith("https://") or val.startswith("/assets/"):
				continue

			# If value is single-line, trim and uppercase; otherwise uppercase multi-line
			if "\n" not in val:
				d.set(fieldname, val.strip().upper())
			else:
				d.set(fieldname, val.upper())
