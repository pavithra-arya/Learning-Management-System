import os
import glob

template_dir = r"c:\Users\Pavih\OneDrive\Desktop\project\lms_project\templates"
files = glob.glob(os.path.join(template_dir, "**", "*.html"), recursive=True)

for file_path in files:
    with open(file_path, 'r', encoding='utf-8') as f:
        content = f.read()
    
    # Apply new teal emerald UI color schemes
    # Instead of rose -> teal
    content = content.replace("rose-", "teal-")
    # Gradients with orange -> emerald
    content = content.replace("orange-", "emerald-")
    # Base amber highlights -> cyan
    content = content.replace("amber-", "cyan-")
    # Keep slate as is
    
    # Specific navbar and hero highlights
    content = content.replace("bg-gradient-to-r from-rose-600 to-orange-500", "bg-gradient-to-r from-teal-600 to-emerald-500")

    with open(file_path, 'w', encoding='utf-8') as f:
        f.write(content)

print(f"Successfully updated theme colors in {len(files)} template files.")
