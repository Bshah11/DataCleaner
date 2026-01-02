import json
import os
from pathlib import Path

# --- CONFIGURATION ---
# The script will now automatically generate both versions for dual factions.
# Standard factions will only generate one file.
SCRIPT_PATH = Path(__file__).resolve()
BASE_DIR = SCRIPT_PATH.parent.parent
INPUT_FILE = BASE_DIR / "rawData" / "master_json" / "factions.json"
OUTPUT_DIR = BASE_DIR / "StructuredData" / "factions"

def get_val(node, is_obsidian_mode):
    """
    State-aware value retriever. 
    Swaps data based on whether we are generating the 'flipped' version.
    """
    if isinstance(node, list):
        return [get_val(item, is_obsidian_mode) for item in node]
    
    if not isinstance(node, dict):
        return node
    
    # Handle Faction State Toggle (Firmament vs Obsidian)
    if "firmament" in node or "obsidian" in node:
        state = "obsidian" if is_obsidian_mode else "firmament"
        return node.get(state, node.get("firmament", "N/A"))
    
    # Handle Home System Flipped Planets
    if is_obsidian_mode and "flipped" in node:
        return node["flipped"]

    return node

def process_planets(planet_data, is_obsidian_mode):
    """Recursively flattens complex planet structures (like Council Keleres)."""
    lines = []
    if isinstance(planet_data, list):
        for item in planet_data:
            if isinstance(item, list):
                # Handle nested variant groups (Council Keleres)
                group = ", ".join([p['name'] for p in item])
                lines.append(f"* **Variant Choice Group:** {group}")
            else:
                p = get_val(item, is_obsidian_mode)
                ability = f" (Ability: {p['text']})" if 'text' in p else ""
                lines.append(f"* **{p['name']}**: {p.get('resources', 0)} Resources / {p.get('influence', 0)} Influence{ability}")
    return lines

def generate_md(f, is_obsidian_mode):
    """Generates the full printed material breakdown for a faction."""
    is_dual = f.get("state_toggle") == "is_obsidian"
    mode_label = "OBSIDIAN" if (is_dual and is_obsidian_mode) else "FIRMAMENT"
    
    title = f"{f['name']} ({mode_label})" if is_dual else f['name']
    md = f"# {title}\n"
    md += f"**Expansion:** {f.get('expansion', 'Standard')}\n\n"

    # --- SETUP ---
    md += "## Setup\n"
    md += f"* **Commodities:** {f['setup']['commodities']}\n"
    
    st = f['setup']['starting_tech_ids']
    if isinstance(st, dict):
        tech_str = st.get('instruction') or st.get('options') or ", ".join(st.get('fixed_ids', []))
    else:
        tech_str = ", ".join(st)
    md += f"* **Starting Tech:** {tech_str}\n"
    
    md += "### Home Planets\n"
    md += "\n".join(process_planets(f['setup']['home_system']['planets'], is_obsidian_mode))
    
    md += "\n\n---\n\n"

    # --- ABILITIES ---
    md += "## Faction Abilities\n"
    for ab in f['abilities']:
        mode = ab.get('mode')
        if not mode or mode == mode_label.lower():
            md += f"### {ab['name']}\n{ab['text']}\n\n"

    # --- LEADERS ---
    md += "## Leaders\n"
    for l_type in ['agent', 'commander', 'hero']:
        leader = f['leaders'].get(l_type)
        if not leader: continue
        
        if l_type == 'hero' and not leader.get('name') and 'options' in leader:
            opts = ", ".join(leader['options'])
            md += f"### Hero: Dynamic Choice\n* **Options:** {opts}\n* **Note:** Hero is determined by faction choice.\n\n"
        else:
            l_data = get_val(leader, is_obsidian_mode)
            md += f"### {l_type.capitalize()}: {l_data['name']}\n"
            if l_data.get('unlock'):
                md += f"* **Unlock:** {l_data['unlock']}\n"
            md += f"{l_data['text']}\n\n"

    # --- UNITS ---
    md += "## Units\n"
    for unit in f['units']:
        name = get_val(unit.get('name', unit['id']), is_obsidian_mode)
        stats = get_val(unit.get('stats'), is_obsidian_mode)
        special = get_val(unit.get('special_text'), is_obsidian_mode) or get_val(unit.get('modes'), is_obsidian_mode)
        
        md += f"### {name}\n"
        if isinstance(stats, dict):
            stat_line = " | ".join([f"**{k.capitalize()}** {v}" for k, v in stats.items() if v is not None])
            md += f"* {stat_line}\n"
        if unit.get('abilities'):
            md += f"* **Keywords:** {', '.join(unit['abilities'])}\n"
        md += f"* **Special Ability:** {special}\n\n"

    # --- TECH & BREAKTHROUGHS ---
    md += "## Technologies & Breakthroughs\n"
    for tech in f.get('technologies', []):
        md += f"### {tech['name']}\n"
        reqs = get_val(tech.get('requirements'), is_obsidian_mode)
        md += f"* **Prerequisites:** {', '.join(reqs) if reqs else 'None'}\n"
        md += f"{get_val(tech.get('text'), is_obsidian_mode)}\n\n"

    bt = f.get('breakthrough')
    if bt:
        md += f"### Breakthrough: {get_val(bt.get('name'), is_obsidian_mode)}\n"
        if bt.get('interchangeable_tech'):
            md += f"* **Colors:** {', '.join(bt['interchangeable_tech'])}\n"
        md += f"{get_val(bt.get('text'), is_obsidian_mode)}\n\n"

    # --- PROMISSORY NOTE ---
    note = f.get('promissory_note')
    if note:
        md += "## Promissory Note\n"
        n_data = get_val(note, is_obsidian_mode)
        md += f"### {n_data['name']}\n{n_data['text']}\n\n"

    # --- PLOTS ---
    if 'plots' in f and is_obsidian_mode:
        md += "## Plot Deck\n"
        for plot in f['plots']:
            md += f"### {plot['name']}\n{plot.get('text', plot.get('effect'))}\n\n"

    return md

def main():
    OUTPUT_DIR.mkdir(parents=True, exist_ok=True)

    if not INPUT_FILE.exists():
        print(f"Error: {INPUT_FILE} not found.")
        return

    with open(INPUT_FILE, 'r') as file:
        data = json.load(file)
    
    factions = data if isinstance(data, list) else [data]

    for faction in factions:
        # 1. Standard/Firmament generation
        filename = OUTPUT_DIR / f"{faction['faction_id']}.md"
        with open(filename, 'w') as f_out:
            f_out.write(generate_md(faction, is_obsidian_mode=False))
        
        # 2. Dual state generation (Obsidian)
        if faction.get('state_toggle') == "is_obsidian":
            obs_filename = OUTPUT_DIR / f"{faction['faction_id']}_obsidian.md"
            with open(obs_filename, 'w') as f_out:
                f_out.write(generate_md(faction, is_obsidian_mode=True))
            print(f"Created Firmament and Obsidian files for {faction['name']}")
        else:
            print(f"Created {faction['name']}")

if __name__ == "__main__":
    main()