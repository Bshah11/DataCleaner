import os
import re

def slugify(text):
    # Standardizing slugs to handle the special characters you noted (✖, –, ’)
    text = str(text).replace("'", "").replace("’", "").replace("✖", "x").replace("–", "-")
    return re.sub(r'\W+', '_', text.lower()).strip('_')

def shatter_lrr_files():
    base_dir = os.path.dirname(os.path.abspath(__file__))
    source_dir = os.path.join(base_dir, "..", "StructuredData", "faction_lrr")
    output_root = os.path.join(base_dir, "..", "StructuredData", "shattered_faction_lrr")

    if not os.path.exists(source_dir):
        print(f"❌ Error: Source directory {source_dir} not found.")
        return

    for filename in os.listdir(source_dir):
        if not filename.endswith(".md"): 
            continue
        
        filepath = os.path.join(source_dir, filename)
        with open(filepath, 'r', encoding='utf-8') as f:
            content = f.read()

        # 1. Extract Faction Name from Header
        faction_match = re.search(r'^#\s+(.*)', content)
        if not faction_match: 
            continue
        faction_name = faction_match.group(1).strip()
        faction_slug = slugify(faction_name)
        
        faction_output_dir = os.path.join(output_root, faction_slug)
        os.makedirs(faction_output_dir, exist_ok=True)
        print(f"📄 Shattering LRR: {faction_name}")

        # 2. Split by horizontal rules (---)
        # Note: The first block is usually the faction header, so we skip index 0
        blocks = re.split(r'\n---\n', content)

        for block in blocks:
            if "##" not in block: 
                continue

            # Extract Name, ID, and Type using multi-line regex
            name_match = re.search(r'##\s+(.*)', block)
            id_match = re.search(r'Component ID:\*\*\s+(.*)', block)
            type_match = re.search(r'Component Type:\*\*\s+(.*)', block)

            if not name_match: 
                continue

            comp_name = name_match.group(1).strip()
            comp_id = id_match.group(1).strip() if id_match else "unknown_id"
            comp_type = type_match.group(1).strip() if type_match else "Clarification"

            # Extract Clarification Notes (Everything after ###)
            notes_match = re.search(r'### Clarification Notes\n([\s\S]*)', block)
            notes_body = notes_match.group(1).strip() if notes_match else "No specific notes provided."

            # 3. Save Atomic File
            # Format: [type]_[name].md
            atomic_filename = f"{slugify(comp_type)}_{slugify(comp_name)}.md"
            with open(os.path.join(faction_output_dir, atomic_filename), 'w', encoding='utf-8') as out_f:
                out_f.write(f"# LRR CLARIFICATION: {faction_name}\n")
                out_f.write(f"## TYPE: {comp_type}\n")
                out_f.write(f"### COMPONENT: {comp_name}\n")
                out_f.write(f"#### ID: {comp_id}\n\n")
                out_f.write(notes_body)

    print(f"✅ LRR Shattering complete. Created: {output_root}")

if __name__ == "__main__":
    shatter_lrr_files()