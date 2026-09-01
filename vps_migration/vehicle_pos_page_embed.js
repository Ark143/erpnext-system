frappe.pages["vehicle_pos"].on_page_load = function (wrapper) {
	const page = frappe.ui.make_app_page({
		parent: wrapper,
		title: __("Vehicle POS"),
		single_column: true
	});

	// The desk POS is the full web POS terminal (Web Page "vehicle-pos-terminal",
	// route /pos-terminal), rendered in an iframe. The web terminal has the correct
	// customer<->vehicle linking, so we reuse it verbatim instead of the (buggy)
	// desk implementation.
	page.main.empty();
	page.main.addClass("vehicle-pos-page");
	page.main.css({ "padding": "0", "margin": "0", "height": "100vh", "overflow": "hidden" });

	const iframe = document.createElement("iframe");
	iframe.src = "/pos-terminal";
	iframe.style.cssText = "width:100%;height:100vh;border:0;display:block;";
	iframe.setAttribute("allow", "camera; microphone; clipboard-read; clipboard-write;");
	page.main.append(iframe);
};
