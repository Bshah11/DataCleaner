import os
import re

def sanitize_text(text):
    """Fixes mashed words and punctuation spacing issues."""
    if not text: return ""
    # 1. Fix 'playsBlitz' -> 'plays Blitz' (lower followed by upper)
    # Using a lookbehind/lookahead to avoid splitting acronyms like PDS
    text = re.sub(r'([a-z])([A-Z])', r'\1 \2', text)
    
    # 2. Fix 'ability.If' -> 'ability. If'
    text = re.sub(r'([\.!?])([A-Z])', r'\1 \2', text)
    
    # 3. Clean up double spaces created by regex
    text = text.replace("  ", " ")
    return text.strip()

def write_rule_file(output_dir, title, content):
    """Writes an atomic rule file with Authority 1 headers."""
    filename = f"{title.lower().replace(' ', '_')}.md"
    file_path = os.path.join(output_dir, filename)
    
    with open(file_path, 'w', encoding='utf-8') as f:
        f.write(f"# AUTHORITY 1: General Rule\n")
        f.write(f"## CATEGORY: {title}\n")
        f.write(f"### SOURCE: Living Rules Reference (tirules.com)\n\n")
        f.write(sanitize_text(content))
    print(f"  ✅ Created: {filename}")

def shatter_abilities_monolith():
    base_dir = os.path.dirname(os.path.abspath(__file__))
    # Adjust paths based on your structure
    source_file = os.path.join(base_dir, "..", "StructuredData", "abilities", "Abilities.md")
    output_dir = os.path.join(base_dir, "..", "StructuredData", "shattered_general_rules", "abilities")
    
    if not os.path.exists(source_file):
        print(f"❌ Error: Could not find {source_file}")
        return

    os.makedirs(output_dir, exist_ok=True)

    with open(source_file, 'r', encoding='utf-8') as f:
        full_text = f.read()

    # Define the clusters using Regex based on your MD headers
    # We capture everything between headers
    clusters = {
        "Ability Definitions": r"## Specific rule.*?(?=#### Costs)",
        "Ability Costs and Logic": r"#### Costs.*?(?=#### Timing)",
        "Ability Timing and Priority": r"#### Timing.*?(?=#### Component–specific Rules)",
        "Ability Resolution Order": r"#### Component–specific Rules.*?(?=### related topic)"
    }

    print(f"🚀 Shattering Abilities Monolith...")
    for title, pattern in clusters.items():
        match = re.search(pattern, full_text, re.DOTALL)
        if match:
            content = match.group(0)
            # We clean the content and write it
            write_rule_file(output_dir, title, content)

    # Handle the "Notes" section specifically as it contains the Alice/Bob/Cheng logic
    notes_match = re.search(r"### Notes.*?(?=### related topic)", full_text, re.DOTALL)
    if notes_match:
        write_rule_file(output_dir, "Ability Resolution Procedures", notes_match.group(0))

if __name__ == "__main__":
    shatter_abilities_monolith()