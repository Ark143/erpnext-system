# POS reconciliation deployment sources

The five Python files in this directory are the exact Server Script bodies deployed by `deploy_reconciliation_fix.py`. `pos_terminal.html` is deployed to the `vehicle-pos-terminal` Web Page and mirrored in the app source.

The close-shift flow now scopes submitted POS invoices to the cashier's open POS profile, carries all unreconciled invoices (including older dates), shows reconciliation status in history, supports select all/manual selection, and calculates each payment method and cash drawer expected amount. The APIs use row locks and stale-selection checks so concurrent closes cannot double-capture an invoice.
