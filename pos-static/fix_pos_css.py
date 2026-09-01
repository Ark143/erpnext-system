import io
p = "/workspace/frappe-bench/apps/vehicle_management/vehicle_management/vehicle_management/page/vehicle_pos/vehicle_pos.js"
s = open(p, encoding="utf-8").read()

reps = [
 # 1) app -> grid 220px | items 1fr | order 1fr  (50/50)
 ("\t\t.vpos-app { display: flex; height: calc(100vh - 46px); min-height: 520px; }",
  "\t\t.vpos-app { display: grid; grid-template-columns: 220px 1fr 1fr; height: calc(100vh - 46px); min-height: 520px; }"),
 # 2) sidebar -> grid col 1, contain overflow
 ("\t\t.vpos-side { flex: 0 0 220px; background: #ffffff; border-right: 1px solid #d7ecea; display: flex; flex-direction: column; padding: 16px 12px; }",
  "\t\t.vpos-side { flex: 0 0 220px; grid-column: 1; min-height: 0; overflow-y: auto; background: #ffffff; border-right: 1px solid #d7ecea; display: flex; flex-direction: column; padding: 16px 12px; }"),
 # 3) main (items) -> grid col 2, contain overflow (fixes overlap)
 ("\t\t.vpos-main { flex: 1 1 auto; display: flex; flex-direction: column; min-width: 0; padding: 14px 16px; gap: 12px; }",
  "\t\t.vpos-main { flex: 1 1 auto; grid-column: 2; overflow: hidden; display: flex; flex-direction: column; min-width: 0; padding: 14px 16px; gap: 12px; }"),
 # 4) order (cart) -> grid col 3, 50% width, contain overflow (fixes overlap + 50/50)
 ("\t\t.vpos-order { flex: 0 0 380px; background: #ffffff; border-left: 1px solid #d7ecea; display: flex; flex-direction: column; padding: 14px; gap: 12px; }",
  "\t\t.vpos-order { flex: none; grid-column: 3; min-width: 0; overflow-y: auto; background: #ffffff; border-left: 1px solid #d7ecea; display: flex; flex-direction: column; padding: 14px; gap: 12px; }"),
]

for old, new in reps:
    if old not in s:
        print("MISS:", repr(old[:60]))
    else:
        s = s.replace(old, new, 1)
        print("OK replaced:", old[:50])

# 5) insert responsive @media before </style>
marker = "\t</style>"
resp = ("\t\t/* RESPONSIVE: tablet + mobile (fix overlap + 50/50 on all sizes) */\n"
        "\t\t@media (max-width: 1024px) {\n"
        "\t\t\t.vpos-app { grid-template-columns: 200px 1fr 1fr; }\n"
        "\t\t\t.vpos-products { grid-template-columns: repeat(auto-fill, minmax(140px, 1fr)); }\n"
        "\t\t}\n"
        "\t\t@media (max-width: 768px) {\n"
        "\t\t\t.vpos-app { display: flex; flex-direction: column; height: auto; min-height: 0; }\n"
        "\t\t\t.vpos-side { flex: 0 0 auto; width: 100%; flex-direction: row; flex-wrap: wrap; align-items: center; border-right: none; border-bottom: 1px solid #d7ecea; padding: 10px 12px; }\n"
        "\t\t\t.vpos-main { overflow: visible; }\n"
        "\t\t\t.vpos-order { width: 100%; border-left: none; border-top: 1px solid #d7ecea; max-height: 65vh; }\n"
        "\t\t\t.vpos-products { grid-template-columns: repeat(2, 1fr); }\n"
        "\t\t}\n")
if marker not in s:
    print("MISS marker </style>")
else:
    s = s.replace(marker, resp + marker, 1)
    print("OK inserted responsive block")

open(p, "w", encoding="utf-8").write(s)
print("WROTE", p)
