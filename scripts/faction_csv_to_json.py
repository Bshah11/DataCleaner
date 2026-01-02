import csv
import json
import requests
import re
import io
from pathlib import Path

# Execution Paths
SCRIPT_DIR = Path(__file__).resolve().parent
OUTPUT_FILE = SCRIPT_DIR.parent / "structuredData" / "master_data.json"
CSV_URL = "https://docs.google.com/spreadsheets/d/1BlifqMrbobwrL8GKRWDNEUXzUdjEBzSvbBNdghmQ0bE/export?format=csv"

def slugify(text):
    if not text: return ""
    clean = text.split(':')[0].split('(')[0].replace('Ω', '').strip()
    return re.sub(r'\W+', '_', clean).lower().strip('_')

def clean_desc_text(name, text):
    pattern = rf"^{re.escape(name)}\s*[:\s\-]*"
    cleaned = re.sub(pattern, "", text.strip(), flags=re.IGNORECASE)
    return cleaned.strip()

def extract_stats(text):
    stats = {}
    patterns = {
        "cost": r'Cost:\s*([\d\.]+)',
        "combat": r'Combat:\s*(\d+x?\d*)',
        "move": r'Move:\s*(\d+)',
        "capacity": r'Capacity:\s*(\d+)'
    }
    for key, pattern in patterns.items():
        match = re.search(pattern, text)
        if match:
            val = match.group(1)
            stats[key] = float(val) if '.' in val else int(val) if val.isdigit() else val
    return stats

def parse_unit_abilities(text):
    keywords_list = ["SUSTAIN DAMAGE", "ANTI-FIGHTER BARRAGE", "PLANETARY SHIELD", "BOMBARDMENT", "SPACE CANNON", "DEPLOY"]
    found_keywords = []
    prod_match = re.search(r'PRODUCTION[:\s]*(\d+)', text, re.IGNORECASE)
    if prod_match: found_keywords.append(f"PRODUCTION {prod_match.group(1)}")
    
    for k in keywords_list:
        if re.search(rf'\b{k}\b', text, re.IGNORECASE): found_keywords.append(k)
    
    clean_text = text
    stat_patterns = [r'Cost:\s*[\d\.]+', r'Combat:\s*\d+x?\d*', r'Move:\s*\d+', r'Capacity:\s*\d+']
    for p in stat_patterns:
        clean_text = re.sub(p, '', clean_text, flags=re.IGNORECASE)
    for k in keywords_list + ["PRODUCTION"]:
        clean_text = re.sub(rf'{k}[:\s]*\d*|{k}', '', clean_text, flags=re.IGNORECASE)
            
    return {"keywords": found_keywords, "special_text": clean_text}

def parse_home_system(raw_text):
    planets = []
    is_fixed = "Choose" not in raw_text and "or" not in raw_text
    entries = re.split(r'\n|,', raw_text)
    for entry in entries:
        match = re.search(r'([\w\s\-\']+):\s*(\d+)/(\d+)', entry)
        if match:
            planets.append({
                "name": match.group(1).strip(),
                "resources": int(match.group(2)),
                "influence": int(match.group(3)),
                "specialty": None, "trait": None
            })
    return {"is_fixed": is_fixed, "planets": planets}

def parse_tech_setup(tech_raw):
    tech_raw = tech_raw.strip()
    choice_match = re.search(r'Choose\s+(\d+)\s+of', tech_raw, re.IGNORECASE)
    if choice_match:
        count = int(choice_match.group(1))
        options_part = re.split(r'of:?\s*', tech_raw, flags=re.IGNORECASE)[-1]
        options = [slugify(t) for t in re.split(r',|\band\b', options_part) if t.strip()]
        return {"is_fixed": False, "choice_count": count, "options": options}
    if "owned by other players" in tech_raw:
        return {"is_fixed": False, "instruction": tech_raw.replace('\n', ' ')}
    return {"is_fixed": True, "fixed_ids": [slugify(t) for t in tech_raw.splitlines() if t.strip()]}

def parse_fleet_logic(raw_text):
    fleet = {}
    for line in raw_text.splitlines():
        match = re.match(r'(\d+)\s+(.*)', line.strip())
        if match: fleet[slugify(match.group(2))] = int(match.group(1))
    return {"is_fixed": "Choose" not in raw_text, "data": fleet}

def parse_breakthrough(raw_text):
    if not raw_text: return None
    lines = raw_text.strip().splitlines()
    name = lines[0].split(':')[0].strip()
    exchange_match = re.search(r'([RGBY])<>([RGBY])', raw_text)
    interchangeable = []
    if exchange_match:
        c_map = {'G': 'Green', 'R': 'Red', 'B': 'Blue', 'Y': 'Yellow'}
        interchangeable = [c_map[exchange_match.group(1)], c_map[exchange_match.group(2)]]
    return {
        "id": slugify(name), "name": name.replace('Ω', '').strip(),
        "interchangeable_tech": interchangeable, "text": clean_desc_text(name, " ".join(lines[1:]))
    }

def migrate():
    response = requests.get(CSV_URL)
    response.encoding = 'utf-8'
    f = io.StringIO(response.text.replace('"""', '"'))
    reader = csv.reader(f, quotechar='"', delimiter=',', skipinitialspace=True)
    
    factions_raw = []
    current_faction = None
    for row in reader:
        if len(row) < 3: continue
        key, val = row[1].strip(), row[2].strip()
        if key and not val and key not in ["Name", "Plots", "Revision"]:
            current_faction = {"name": key, "raw": {}, "rev": row[3] if len(row) > 3 else ""}
            factions_raw.append(current_faction)
            continue
        if current_faction and key:
            current_faction["raw"][key] = (current_faction["raw"].get(key, "") + "\n\n" + val).strip()

    master_json = []
    for f in factions_raw:
        raw = f["raw"]
        f_name = f["name"]

        def get_simple(key):
            blocks = [b.strip() for b in re.split(r'\n\s*\n', raw.get(key, "")) if b.strip()]
            return [{"id": slugify(b.splitlines()[0]), "name": b.splitlines()[0].split(':')[0].replace('Ω', '').strip(), 
                     "text": clean_desc_text(b.splitlines()[0].split(':')[0], b)} for b in blocks]

        # Units with explicit Unit Type
        units = []
        source_categories = [("Special Units", "Special Unit"), ("Flagship", "Flagship"), ("Mech", "Mech")]
        for cat_key, cat_type in source_categories:
            u_blocks = [b.strip() for b in re.split(r'\n\s*\n', raw.get(cat_key, "")) if b.strip()]
            for b in u_blocks:
                name = b.splitlines()[0].split(':')[0].strip()
                abils = parse_unit_abilities(b)
                units.append({
                    "id": slugify(name), 
                    "name": name.replace('Ω', '').strip(), 
                    "unit_type": cat_type,
                    "is_upgrade": " II" in name,
                    "stats": extract_stats(b), 
                    "abilities": abils["keywords"], 
                    "special_text": clean_desc_text(name, abils["special_text"])
                })

        techs = []
        t_blocks = [b.strip() for b in re.split(r'\n\s*\n', raw.get("Faction Technologies", "")) if b.strip()]
        for b in t_blocks:
            name = b.splitlines()[0].split(':')[0].strip()
            req_match = re.search(r'\((\w+)\)', b.splitlines()[0])
            reqs = []
            if req_match:
                c_map = {'G': 'Green', 'R': 'Red', 'B': 'Blue', 'Y': 'Yellow'}
                for char in req_match.group(1): 
                    if char.upper() in c_map: reqs.append(c_map[char.upper()])
            is_up = any(k in b for k in ["Infantry", "Dreadnought", "Carrier", "Cruiser", "Destroyer", "Fighter", "PDS", "Dock"])
            techs.append({
                "id": slugify(name), "name": name.replace('Ω', '').strip(), "requirements": reqs,
                "is_unit_upgrade": is_up, "unit_id": slugify(name) if is_up else None,
                "text": clean_desc_text(name, b)
            })

        def get_leader(key):
            txt = raw.get(key, "")
            if not txt: return None
            name = txt.splitlines()[0].split(':')[0].strip()
            unlock_match = re.search(r'Unlock:\s*(.*)', txt)
            return {
                "id": slugify(name), "name": name,
                "unlock": unlock_match.group(1).strip() if unlock_match else None,
                "text": clean_desc_text(name, txt.replace(f"Unlock: {unlock_match.group(1)}" if unlock_match else "", ""))
            }

        faction_obj = {
            "faction_id": slugify(f_name), "name": f_name, "expansion": f.get("rev", "Base"),
            "setup": {
                "home_system": parse_home_system(raw.get("Home System", "")),
                "commodities": int(raw.get("Commodities", "0")) if raw.get("Commodities", "0").isdigit() else 0,
                "starting_fleet": parse_fleet_logic(raw.get("Starting Fleet", "")),
                "starting_tech_ids": parse_tech_setup(raw.get("Starting Technologies", ""))
            },
            "abilities": get_simple("Faction Abilities"),
            "breakthrough": parse_breakthrough(raw.get("Breaktrough", "")),
            "units": units,
            "technologies": techs,
            "promissory_note": get_simple("Promissory Note")[0] if raw.get("Promissory Note") else None,
            "leaders": {"agent": get_leader("Agent"), "commander": get_leader("Commander"), "hero": get_leader("Hero")}
        }
        master_json.append(faction_obj)

    OUTPUT_FILE.parent.mkdir(parents=True, exist_ok=True)
    with open(OUTPUT_FILE, "w", encoding="utf-8") as out:
        json.dump(master_json, out, indent=2, ensure_ascii=False)
    print(f"Success. Master file: {OUTPUT_FILE}")

if __name__ == "__main__":
    migrate()