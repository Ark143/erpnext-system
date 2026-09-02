# Copy of full technical and functional documentation
with open(r'C:\Users\josem\.gemini\antigravity-ide\brain\ad9d29ca-966c-454f-b5c8-9ae935c95822\full_technical_and_functional_documentation.md', 'r', encoding='utf-8') as f:
    content = f.read()

import os
os.makedirs(r'c:\Users\josem\erpnext-system\docs', exist_ok=True)
with open(r'c:\Users\josem\erpnext-system\docs\FULL_TECHNICAL_AND_FUNCTIONAL_DOCUMENTATION.md', 'w', encoding='utf-8') as f:
    f.write(content)

print("Saved documentation to c:\\Users\\josem\\erpnext-system\\docs\\FULL_TECHNICAL_AND_FUNCTIONAL_DOCUMENTATION.md")
