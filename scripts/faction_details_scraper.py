import requests
import re
import io
from pathlib import Path

# Execution Paths
SCRIPT_DIR = Path(__file__).resolve().parent
OUTPUT_DIR = SCRIPT_DIR.parent / "structuredData" / "factions"
CSV_URL = "https://docs.google.com/spreadsheets/d/1BlifqMrbobwrL8GKRWDNEUXzUdjEBzSvbBNdghmQ0bE/export?format=csv"

def slugify(text):
    if not text: return ""
    # Remove things like "(GG)" or "Ω" for the ID, then slugify
    clean = re.sub(r'\(.*?\)', '', text)
    return re.sub(r'\W+', '_', clean).lower().strip('_')

def atomic_split(text):
    """
    Splits text into atomic units based on 'Title:' pattern at the start of lines.
    Protects unit stats and handles trailing garbage quotes.
    """
    # Fix triple quotes and clean up padding
    text = text.replace('"""', '"').strip()
    if text.endswith('"'): text = text[:-1]
    
    # Negative Lookahead to protect stats
    ignore_list = "Cost|Combat|Move|Capacity|Unlock|Sustain|PRODUCTION|Strategic|ACTION|After|When|During|At|Other|Each|If|You|Your|Apply"
    pattern = rf'\n(?=[A-Z][\w\s\-\'Ω]+:)(?!\s*(?:{ignore_list}))'
    
    # Split by double newline OR the pattern
    blocks = re.split(rf'(\n\s*\n|{pattern})', text)
    return [b.strip() for b in blocks if b and b.strip() and len(b.strip()) > 1]

def get_rows_manually(raw_text):
    """
    Custom state-machine to yield rows of exactly 4 columns.
    Ensures internal commas and quotes don't break the row structure.
    """
    # Standardize quotes to handle the Hacan Hero bug
    raw_text = raw_text.replace('"""', '"')
    
    # Use regex to find all matches of: (Quoted Content) OR (Non-Comma Content)
    # This specifically looks for the 4-column structure
    pattern = re.compile(r',(?=(?:[^"]*"[^"]*")*[^"]*$)')
    
    lines = raw_text.splitlines()
    buffer = ""
    for line in lines:
        buffer += ("\n" + line if buffer else line)
        # Only process if quotes are balanced
        if buffer.count('"') % 2 == 0:
            parts = pattern.split(buffer)
            # Clean up quotes and whitespace from each column
            clean_parts = [p.strip().strip('"').replace('""', '"') for p in parts]
            if len(clean_parts) >= 2:
                yield clean_parts
            buffer = ""

def parse_factions():
    response = requests.get(CSV_URL)
    response.encoding = 'utf-8'
    
    factions = {}
    current_faction = None

    for row in get_rows_manually(response.text):
        key = row[1].strip()
        
        # Stop at footer
        if any(x in key for x in ["Special thanks", "Revision", "All card texts"]):
            break
            
        # Detect Faction Header
        is_val_empty = len(row) > 2 and not row[2].strip()
        if key and is_val_empty and key not in ["Name", "Plots"]:
            current_faction = key
            factions[current_faction] = []
            continue

        if current_faction and key and len(row) > 2 and row[2].strip():
            factions[current_faction].append({
                "key": key,
                "value": row[2].strip(),
                "rev": row[3].strip() if len(row) > 3 else ""
            })

    OUTPUT_DIR.mkdir(parents=True, exist_ok=True)

    for name, attributes in factions.items():
        f_id = slugify(name)
        with open(OUTPUT_DIR / f"{f_id}.md", "w", encoding="utf-8") as f:
            f.write(f"---\nid: {f_id}\nname: {name}\ntype: faction_sheet\n---\n\n# {name}\n\n")
            
            meta_keys = ["Home System", "Commodities", "Starting Fleet", "Starting Technologies"]
            f.write("## Setup Information\n")
            for attr in attributes:
                if attr['key'] in meta_keys:
                    f.write(f"- **{attr['key']}**: {attr['value'].replace(chr(10), ', ')}\n")
            
            for attr in attributes:
                if attr['key'] in meta_keys: continue
                
                blocks = atomic_split(attr['value'])
                for block in blocks:
                    # Logic to extract clean sub-title
                    title_match = re.match(r'^([\w\s\-\'Ω]+):', block)
                    block_title = title_match.group(1).strip() if title_match else attr['key']
                    
                    # Prevent stats from becoming headers
                    if block_title in ["Cost", "Combat", "Move", "Capacity"]:
                        block_title = attr['key']

                    display_name = f"{attr['key']}: {block_title}" if len(blocks) > 1 else attr['key']
                    
                    f.write(f"\n## {display_name}\n")
                    f.write(f"- **id**: {f_id}_{slugify(display_name)}\n")
                    f.write(f"- **type**: {slugify(attr['key'])}\n")
                    if attr['rev']: f.write(f"- **rev**: {attr['rev']}\n")
                    f.write(f"- **text**: |\n  {block.replace('\n', '\n  ')}\n")
        
        print(f"Generated: {f_id}.md")

if __name__ == "__main__":
    parse_factions()