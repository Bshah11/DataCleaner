import json
import os
import re

def slugify(text):
    """Converts 'Hope's End' to 'hopes_end' for clean, searchable filenames."""
    text = str(text).replace("'", "") 
    return re.sub(r'\W+', '_', text.lower()).strip('_')

def shatter_library():
    # Define paths relative to the /scripts folder
    base_dir = os.path.dirname(os.path.abspath(__file__))
    source_root = os.path.join(base_dir, "..", "structuredData", "master_json")
    output_root = os.path.join(base_dir, "..", "structuredData", "shattered_md")

    if not os.path.exists(source_root):
        print(f"❌ Error: Source directory not found at {source_root}")
        return

    print(f"🚀 Starting Data Migration...")
    print(f"📁 Source: {source_root}")
    print(f"📁 Destination: {output_root}\n")

    for filename in os.listdir(source_root):
        if not filename.endswith(".json"):
            continue
        
        category = filename.replace(".json", "")
        category_dir = os.path.join(output_root, category)
        os.makedirs(category_dir, exist_ok=True)

        with open(os.path.join(source_root, filename), 'r', encoding='utf-8') as f:
            try:
                data = json.load(f)
            except json.JSONDecodeError:
                print(f"⚠️ Skipping {filename}: Invalid JSON format.")
                continue

        count = 0
        for entry in data:
            # Fallback to ID if Name is missing, though we expect Name
            name = entry.get("name") or entry.get("card_id") or entry.get("tech_id") or entry.get("unit_id")
            if not name:
                continue

            file_slug = slugify(name)
            md_path = os.path.join(category_dir, f"{file_slug}.md")

            with open(md_path, 'w', encoding='utf-8') as md:
                # Primary Markdown Header
                md.write(f"# {category.replace('_', ' ').title()}: {name}\n\n")

                # Iterate through all key-value pairs
                for key, value in entry.items():
                    if key == "name": continue
                    
                    clean_key = key.replace("_", " ").title()
                    
                    # Handle nested objects (like base_stats or metadata)
                    if isinstance(value, dict):
                        md.write(f"## {clean_key}\n")
                        for sub_k, sub_v in value.items():
                            md.write(f"* **{sub_k.replace('_', ' ').title()}**: {sub_v}\n")
                    # Handle lists (like clarifications or traits)
                    elif isinstance(value, list):
                        md.write(f"## {clean_key}\n")
                        for item in value:
                            md.write(f"* {item}\n")
                    # Handle standard strings/numbers
                    elif value is not None:
                        md.write(f"* **{clean_key}**: {value}\n")
                
                md.write("\n---\n")
                count += 1
        
        print(f"✅ Shattered {filename}: Created {count} files in /{category}/")

if __name__ == "__main__":
    shatter_library()
    print("\n[MIGRATION COMPLETE] Every component is now an atomic Markdown file.")