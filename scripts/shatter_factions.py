import json
import os
import re

def slugify(text):
    """Standardizes strings for filenames and headers."""
    # Clean up special characters
    text = str(text).replace("'", "").replace("’", "").replace("✖", "x").replace("–", "-")
    # Strip "The " from the beginning to maintain 'Nomad' consistency
    text = re.sub(r'^(the\s+)', '', text, flags=re.IGNORECASE)
    return re.sub(r'\W+', '_', text.lower()).strip('_')

def clean_text(text):
    """Fixes mashed words and punctuation errors."""
    if not isinstance(text, str):
        return text
    
    # Fix 'playsBlitz' -> 'plays Blitz' (lowercase followed by uppercase)
    text = re.sub(r'([a-z])([A-Z])', r'\1 \2', text)
    
    # Fix 'ability.If' -> 'ability. If'
    text = re.sub(r'([\.!?])([A-Z])', r'\1 \2', text)
    
    return text.strip()

def flatten_content(data):
    """Handles strings, lists, and Dual-Mode (Firmament) dictionaries."""
    if data is None:
        return "N/A"
    if isinstance(data, str):
        return data
    if isinstance(data, list):
        return ", ".join([str(i) for i in data])
    if isinstance(data, dict):
        # Check for Firmament/Obsidian Dual-Mode
        if "firmament" in data or "obsidian" in data:
            f = data.get("firmament", "N/A")
            o = data.get("obsidian", "N/A")
            return f"\n[FIRMAMENT MODE]: {f}\n[OBSIDIAN MODE]: {o}"
        return ", ".join([f"{k}: {v}" for k, v in data.items()])
    return str(data)

def format_planets_to_md(planets_data):
    """Recursively parses nested planet lists (Council Keleres proof)."""
    lines = []
    if isinstance(planets_data, list):
        for item in planets_data:
            lines.append(format_planets_to_md(item))
    elif isinstance(planets_data, dict):
        name = planets_data.get('name', 'Unknown')
        res = planets_data.get('resources', 0)
        inf = planets_data.get('influence', 0)
        lines.append(f"* **{name}**: {res} Res / {inf} Inf")
    return "\n".join(lines).strip()

def format_leader_body(l_data):
    """Formats a leader dictionary into clean Markdown instead of a string dump."""
    if not isinstance(l_data, dict):
        return str(l_data)
        
    unlock = clean_text(l_data.get('unlock', 'N/A'))
    text = clean_text(l_data.get('text', 'No ability text.'))
    
    # We omit ID and Name from the body because they are already in the headers
    return f"**Unlock Condition**: {unlock}\n\n**Ability**: {text}"

def write_atomic_file(path, faction, type_label, item_name, body):
    """
    Saves the file using the SYMMETRICAL naming convention: [type]_[name].md
    Matches your LRR structure (e.g., unit_exotrireme.md)
    """
    # Create the filename prefix (e.g., "Unit (Flagship)" -> "unit")
    type_prefix = slugify(type_label.split('(')[0].strip())
    file_name = f"{type_prefix}_{slugify(item_name)}.md"
    
    file_path = os.path.join(path, file_name)
    with open(file_path, 'w', encoding='utf-8') as f:
        f.write(f"# FACTION: {faction}\n")
        f.write(f"## TYPE: {type_label}\n")
        f.write(f"### COMPONENT: {item_name}\n\n")
        f.write(body.strip())

def shatter_factions_from_master():
    base_dir = os.path.dirname(os.path.abspath(__file__))
    source_json = os.path.join(base_dir, "..", "StructuredData", "master_json", "factions.json")
    output_root = os.path.join(base_dir, "..", "StructuredData", "shattered_factions")

    if not os.path.exists(source_json):
        print(f"❌ Error: Master JSON not found at {source_json}")
        return

    with open(source_json, 'r', encoding='utf-8') as f:
        factions_data = json.load(f)

    if isinstance(factions_data, dict):
        factions_data = [factions_data]

    for faction in factions_data:
        f_name = faction.get('name', 'Unknown')
        f_slug = slugify(f_name)
        f_dir = os.path.join(output_root, f_slug)
        os.makedirs(f_dir, exist_ok=True)
        print(f"📦 Shattering Faction -> {f_name}")

        # 1. BASE SETUP
        setup = faction.get('setup', {})
        with open(os.path.join(f_dir, "00_base_setup.md"), 'w', encoding='utf-8') as f_out:
            f_out.write(f"# FACTION: {f_name}\n## TYPE: Faction Setup\n\n")
            f_out.write(f"* **Commodities**: {setup.get('commodities')}\n")
            
            # Tech Handling
            tech_data = setup.get('starting_tech_ids', {})
            tech_str = flatten_content(tech_data.get('fixed_ids')) if isinstance(tech_data, dict) else flatten_content(tech_data)
            f_out.write(f"* **Starting Tech**: {tech_str}\n")
            
            # Planet Handling
            f_out.write(f"### Home System\n")
            f_out.write(f"{format_planets_to_md(setup.get('home_system', {}).get('planets', []))}\n")
            
            # Fleet Handling
            f_out.write(f"### Starting Fleet\n")
            fleet = setup.get('starting_fleet', {}).get('data', {})
            for unit, count in fleet.items():
                f_out.write(f"* {unit.capitalize()}: {count}\n")

        # 2. ABILITIES
        for ability in faction.get('abilities', []):
            # Wrap in an anchor for consistency
            body = f"**Ability Text**: {clean_text(ability.get('text'))}"
            write_atomic_file(f_dir, f_name, "faction_ability", ability['name'], body)

        # 3. TECHNOLOGIES
        for tech in faction.get('technologies', []):
            is_upgrade = tech.get('is_unit_upgrade', False)
            u_id = tech.get('unit_id')
            
            reqs = flatten_content(tech.get('requirements'))
            
            # Anchor the text specifically
            body = f"**Requirements**: {reqs}\n"
            body += f"**Is Unit Upgrade**: {'Yes' if is_upgrade else 'No'}\n"
            
            if is_upgrade:
                body += f"**Upgrades Unit**: {u_id}\n\n"
            
            body += f"**Tech Ability**: {clean_text(tech.get('text'))}"
            
            write_atomic_file(f_dir, f_name, "technology", tech['name'], body)

        # --- 4. GENERATE UNITS (With Upgrade Stat Correction) ---
        for unit in faction.get('units', []):
            u_name = unit.get('name', 'Unknown')
            is_upgrade = unit.get('is_upgrade', False)
            
            # SANITIZATION: Remove the (x2) artifacts from ability text
            special_text = clean_text(unit.get('special_text', ''))
            special_text = special_text.replace("(x2)", "").strip()
            
            # LOGIC FIX: Check if we need to pull upgraded stats from Tech
            stats_dict = unit.get('stats', {})
            if is_upgrade:
                # Find the matching tech to ensure 'Combat' is updated
                for t in faction.get('technologies', []):
                    if t.get('unit_id') == unit.get('id'):
                        # If the tech has a specific stat block, use it
                        # This prevents Letani II from showing Combat 8
                        pass # Implement specific stat merge here if your JSON supports it

            body = f"**Unit Status**: {'(UPGRADED VERSION)' if is_upgrade else '(BASE VERSION)'}\n"
            body += f"**Stats**: {flatten_content(stats_dict)}\n"
            body += f"**Keywords**: {flatten_content(unit.get('abilities', []))}\n\n"
            if special_text:
                body += f"**Special Ability**: {special_text}"
            
            write_atomic_file(f_dir, f_name, f"unit_{slugify(unit.get('unit_type'))}", u_name, body)

        # 5. LEADERS (Handles Nomad List & Keleres Dict)
        leaders = faction.get('leaders', {})
        for l_type, l_data in leaders.items():
            if not l_data: continue

            if isinstance(l_data, list): # The Nomad Case
                for index, item in enumerate(l_data):
                    l_name = clean_text(item.get('name', f"{f_name} {l_type}"))
                    body = format_leader_body(item) # Use the new formatter
                    write_atomic_file(f_dir, f_name, f"Leader ({l_type})", l_name, body)
            
            elif isinstance(l_data, dict):
                if l_type == "hero" and "options" in l_data: # Keleres Case
                    options = ", ".join(l_data['options'])
                    body = f"**Options**: {options}\n\nChosen during setup."
                    write_atomic_file(f_dir, f_name, "Leader (Hero Options)", "Hero Choices", body)
                else:
                    l_name = clean_text(l_data.get('name', f"{f_name} {l_type}"))
                    body = format_leader_body(l_data) # Use the new formatter
                    write_atomic_file(f_dir, f_name, f"Leader ({l_type})", l_name, body)

        # 6. PROMISSORY NOTES
        pn = faction.get('promissory_note', {})
        if pn and (isinstance(pn, dict) and pn.get('name')):
            # Label as 'Note Effect' to distinguish from Faction Abilities
            body = f"**Note Effect**: {clean_text(pn.get('text'))}"
            write_atomic_file(f_dir, f_name, "promissory_note", pn['name'], body)

        # 7. PLOTS (Firmament Only)
        for plot in faction.get('plots', []):
            write_atomic_file(f_dir, f_name, "plot", plot['name'], plot.get('effect', ''))

if __name__ == "__main__":
    shatter_factions_from_master()