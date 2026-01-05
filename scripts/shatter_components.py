import os
import re

def slugify(text):
    """Standardizes strings for filenames and headers."""
    text = str(text).replace("'", "").replace("’", "").replace("–", "-")
    return re.sub(r'\W+', '_', text.lower()).strip('_')

def shatter_component_lrr():
    base_dir = os.path.dirname(os.path.abspath(__file__))
    # Assuming your source files are in a folder called component_lrr
    source_dir = os.path.join(base_dir, "..", "StructuredData", "components")
    output_root = os.path.join(base_dir, "..", "StructuredData", "shattered_component_lrr")

    if not os.path.exists(source_dir):
        print(f"❌ Error: Source directory {source_dir} not found.")
        return

    for filename in os.listdir(source_dir):
        if not filename.endswith(".md"): continue
        
        filepath = os.path.join(source_dir, filename)
        with open(filepath, 'r', encoding='utf-8') as f:
            content = f.read()

        # 1. Extract the Type from "Document Type" header
        # E.g., "Document Type: Relics Reference" -> "relic"
        type_match = re.search(r'\*\*Document Type:\*\*\s+(.*)\sReference', content)
        doc_type = type_match.group(1).strip() if type_match else "Component"
        type_slug = slugify(doc_type).rstrip('s') # Convert "Relics" to "relic"
        
        comp_folder = os.path.join(output_root, slugify(doc_type))
        os.makedirs(comp_folder, exist_ok=True)
        print(f"📦 Shattering Component Type: {doc_type}")

        # 2. Split by horizontal rules (---)
        blocks = re.split(r'\n---\n', content)

        for block in blocks:
            if "##" not in block: continue

            # Extract Name (## Name), ID, and Source
            name_match = re.search(r'##\s+(.*)', block)
            id_match = re.search(r'Component ID:\*\*\s+(.*)', block)
            source_match = re.search(r'Source:\*\*\s+(.*)', block)

            if not name_match: continue

            comp_name = name_match.group(1).strip()
            comp_id = id_match.group(1).strip() if id_match else "unknown_id"
            source_info = source_match.group(1).strip() if source_match else "Unknown"

            # Extract Clarification Notes
            notes_match = re.search(r'### Clarification Notes\n([\s\S]*)', block)
            notes_body = notes_match.group(1).strip() if notes_match else "No specific notes provided."

            # 3. Save Atomic File: [type]_[name].md
            atomic_filename = f"{type_slug}_{slugify(comp_name)}.md"
            
            with open(os.path.join(comp_folder, atomic_filename), 'w', encoding='utf-8') as out_f:
                out_f.write(f"# COMPONENT CLARIFICATION: {doc_type}\n")
                out_f.write(f"## TYPE: {type_slug.capitalize()}\n")
                out_f.write(f"### COMPONENT: {comp_name}\n")
                out_f.write(f"#### ID: {comp_id} | Source: {source_info}\n\n")
                out_f.write(notes_body)

    print(f"✅ Component Shattering complete: {output_root}")

if __name__ == "__main__":
    shatter_component_lrr()