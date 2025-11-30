import os
import re

# Define the subdirectory
SUBDIRECTORY = "structuredData"

# --- Raw Data Input (Concatenated and stripped for parsing) ---

PLANETS_FLAT_DATA = """
Soure Name Type Race Resource Influence Tech Tech Hazard Legendary Ability Neutral Units
Base Abyz Hazardous 3 0 Base
Base Arinam Industrial 1 2
Base Arnor Industrial 2 1
Base Bereg Hazardous 3 1
Base Centauri Cultural 1 3
Base Coorneeq Cultural 1 2
Base Dal Bootha Cultural 0 2
Base Fria Hazardous 2 0
Base Gral Industrial 1 1 Blue
Base Lazar Industrial 1 0 Yellow
Base Lirta IV Hazardous 2 3
Base Lodor Cultural 3 1
Base Lor Industrial 1 2
Base Meer Hazardous 0 4 Red
Base Mehar Xull Hazardous 1 3 Red
Base Mellon Cultural 0 2
Base New Albion Industrial 1 1 Green
Base Quann Cultural 2 1
Base Qucen'n Industrial 1 2
Base Rarron Cultural 0 3
Base Resculon Cultural 2 0
Base Sakulag Hazardous 2 1
Base Saudor Industrial 2 2
Base Starpoint Hazardous 3 1
Base Tar'mann Industrial 1 1 Green
Base Tequ'ran Hazardous 2 0
Base Thibah Industrial 1 1 Blue
Base Torkan Cultural 0 3
Base Vefut II Hazardous 2 2
Base Wellon Industrial 1 2 Yellow
Base Xxehan Cultural 1 1
Base Zohbat Hazardous 3 1
PoK Archon Vail Hazardous 1 3 Blue
PoK Perimeter Industrial 2 1
PoK Ang Industrial 2 0 Red
PoK Sem-Lore Cultural 3 2 Yellow
PoK Vorhal Cultural 0 2 Green
PoK Atlas Hazardous 3 1
PoK Cormund Hazardous 2 0 Gravity Rift
PoK Everra Cultural 3 1 Nebula
PoK Accoen Industrial 2 3
PoK Jeol Ir Industrial 2 3
PoK Kraag Hazardous 2 1
PoK Siig Hazardous 0 2
PoK Alio Prima Cultural 1 1
PoK Ba'kal Industrial 3 2
PoK Lisis Industrial 2 2
PoK Velnor Industrial 2 1 Red
PoK Cealdri Cultural 0 2 Yellow
PoK Xanhact Hazardous 0 1
PoK Vega Major Cultural 2 1
PoK Vega Minor Cultural 1 2 Blue
PoK Abaddon Cultural 1 0
PoK Ashtroth Hazardous 2 0
PoK Loki Cultural 1 2
PoK Rigel I Hazardous 0 1
PoK Rigel II Industrial 1 2
PoK Rigel III Industrial 1 1 Green
PoK Primor Cultural 2 1 Legendary The Atrament:You may exhaust this card at the end of your turn to place up to 2 infantry from your reinforcements on any planet you control.
PoK Hope's End Hazardous 3 0 Legendary Imperial Arms Vault: You may exhaust this card at the end of your turn to place 1 mech from your reinforcements on any planet you control or draw 1 action card.
PoK Mallice Cultural 0 3 Legendary Exterrix Headquarters: You may exhaust this card at the end of your turn to gain 2 trade goods or convert all of your commodities to trade goods.
PoK Mirage Cultural 1 2 Legendary Mirage Flight Academy: You may exhaust this card at the end of your turn to place up to 2 fighters from your reinforcements in any system that contains 1 or more of your ships.
PoK Custodia Vigia - 2 3 Legendary Keleres - While you control Mecatol Rex, it gains SPACE CANNON 5 and PRODUCTION 3. Gain 2 command tokens when another player scores VP using Imperial
Codex Ordinian - 0 0 Legendary Barren Husk - You may exhaust this card when you pass to draw 1 action card and gain 1 command token.
TE Tempesta Hazardous 1 1 Blue Legendary Legendary Ability: You may exhaust this card after you activate a system to apply +1 to the move value of 1 of your ships during this tactical action.
TE Olergodt Cultural / Hazardous 1 2 Yellow Red
TE Andeara Industrial 1 1 Blue
TE Vira-Pics III Cultural / Hazardous 2 3
TE Lesab Hazardous / Industrial 2 1
TE New Terra Industrial 1 1 Green
TE Tinnes Hazardous / Industrial 2 1 Green
TE Cresius Hazardous 0 1
TE Lazul Rex Industrial / Cultural 2 2
TE Tiamat Cultural 1 2 Yellow
TE Hercalor Industrial 1 0
TE Kostboth Cultural 0 1
TE Capha Hazardous 3 0
TE Tsion Station Trade Station 1 1
TE Bellatrix Cultural 1 2
TE El'Nath Hazardous 2 0
TE Horizon Cultural 1 2
TE Luthien VI Hazardous 3 1
TE Tarana Industrial / Cultural 1 2
TE Oluz Station Trade Station 1 1
TE Industrex Industrial 2 0 Red Asteroid Field Legendary Legendary Ability: You may exhaust this card when you pass to place 1 ship that matches a unit upgrade technology you own from your reinforcements into a system that contains your ships.
TE Lemox Industrial 0 3 Entropic Scar
TE The Watchtower Trade Station 1 1 Gravity Rift
TE Faunus Industrial 1 3 Green Legendary Legendary Ability: You may exhaust this card when you pass to gain control of a non-home, non-legendary planet that contains no units and has no attachments.
TE Garbozia Hazardous 2 1 Legendary Legendary Ability: You may exhaust this card when you pass to place 1 action card from the discard pile faceup on this card; you can purge cards on this card to play them as if they were in your hand.
TE Emelpar Cultural 0 2 Legendary Legendary ability: The Acropolis: You may exhaust this card at the end of your turn to ready another component that isn't a strategy card.
TE Styx Fracture 4 0 Legendary Draw a relic. Legendary ability: Song Like Marrow: When you gain this card, gain 1 victory point. When you lose this card, lose 1 victory point. 3 infantry, 1 destroyer, 2 dreadnoughts
TE Cocytus Fracture 3 0 Draw a relic. 2 infantry, 2 cruisers
TE Lethe Fracture 0 2 Legendary Draw a relic. 1 infantry, 4 fighters, 1 carrier
TE Pehelegethon Fracture 1 2 Legendary Draw a relic. 1 infantry, 4 fighters, 1 carrier
TE Avernus Hazardous Muaat 2 0 Legendary Legendary planet ability:The Nucleus ACTION: Exhaust this card to use the Embers of Muaat's Star Forge faction ability without spending a command token.
TE Thunder's Edge - 5 1 Placed after six expeditions (not in a system tile) Legendary ability: Jupiter Brain: Gain your breakthrough when you gain this card if you do not already have it. You may exhaust this card at the end of your turn to perform an action.
TE Mecatol Rex None 1 6 Legendary ability: The Galactic Council You may exhaust this card and discard 1 secret objective at the end of your turn to draw 1 secret objective.
Base Nestphar Arborec 3 2
Base Creuss Creuss 4 2
Base Arretze Hacan 2 0
Base Hercant Hacan 1 1
Base Kamdorn Hacan 0 1
Base Jol Jol-Nar 1 2
Base Nar Jol-Nar 2 3
Base [0.0.0] L1Z1X 5 0
Base Arc Prime Letnev 4 0
Base Wren Terra Letnev 2 1
Base Moll Primus Mentak 4 1
Base Muaat Muaat 4 1
Base Druaa Naalu 3 1
Base Maaluuk Naalu 0 2
Base Mordai II Nekro Virus 4 0
Base Lisis II Saar 1 0
Base Ragh Saar 2 1
Base Quinarra Sardakk N'orr 3 1
Base Tren'lak Sardakk N'orr 1 0
Base Jord Sol 4 2
Base Winnu Winnu 3 4
Base Archon Ren Xxcha 2 3
Base Archon Tau Xxcha 1 1
Base Darien Yin 4 4
Base Retillion Yssaril 2 3
Base Shalloq Yssaril 1 2
PoK Ixth Mahact 3 5
PoK Arcturus Nomad 4 4
PoK Acheron Vuil'raith 4 0
PoK Elysium Titans 4 1
PoK The Dark Empyrean 3 4
PoK Naazir Naaz-Rokha 2 1
PoK Rokha Naaz-Rokha 1 2
PoK Avar Argent 1 1
PoK Valk Argent 2 0
PoK Ylir Argent 0 2
TE Ordinian Last Bastion 0 0
TE Revelation Last Bastion 1 2
TE Mez Lo Orz Fei Zsha Ral-Nel 2 1
TE Rep Lo Orz Oet Ral-Nel 1 3
TE Ikatena Deep Wrought 4 4
TE Cronos Firmament 2 1
TE Tallin Firmament 1 2
TE Cronos Hollow Obsidian 3 0
TE Tallin Hollow Obsidian 3 0
TE Ankh Creux Crimson Rebellion 4 2 Epsilon Wormhole
Base Empty Space
Base Empty Space
Base Empty Space
Base Empty Space
Base Empty Space
Base ⍺-Wormhole
Base β-Wormhole
Base Asteroid Field
Base Asteroid Field
Base Gravity Rift
Base Nebula
Base Supernova
TE Entropic Scar Entropic Scar
TE β-Wormhole + Gravity Rift
"""

# --- 2. Core Logic Functions ---

def clean_text(text):
    """Cleans up raw text, removing extra spaces and newlines."""
    if not isinstance(text, str):
        return ""
    text = text.replace('\n', ' ').replace('\r', ' ').strip()
    text = ' '.join(text.split())
    text = text.strip('-').strip()
    return text

def parse_planets_flat_data(raw_data):
    """
    Parses the massive flat text block into a list of structured dictionaries,
    using a defensive mapping approach.
    """
    lines = [line.strip() for line in raw_data.strip().split('\n') if line.strip() and not line.startswith('Soure')]
    parsed_planets = []
    
    # Define keywords for easy lookup within the free-form text chunk
    TECH_KEYWORDS = ['Blue', 'Red', 'Yellow', 'Green', 'Epsilon Wormhole', 'Entropic Scar']
    MODIFIER_KEYWORDS = ['Legendary', 'Gravity Rift', 'Nebula', 'Asteroid Field', 'Supernova', 'Fracture', 'Trade Station']
    
    for line in lines:
        parts = line.split()
        if not parts: continue
        
        # 1. Initialize a defensive dictionary
        planet_data = {
            'Source': parts[0] if parts else 'N/A',
            'Name': parts[1] if len(parts) > 1 else 'N/A',
            'R': 'N/A',
            'I': 'N/A',
            'Type': 'N/A',
            'Tech': 'N/A',
            'Modifiers': 'N/A',
            'Race/HS': 'N/A',
            'Ability': 'N/A',
            'Neutral Units': 'N/A'
        }
        
        # Check if this is a generic system tile (no R/I)
        is_tile = any(s in planet_data['Name'] for s in ['Wormhole', 'Asteroid', 'Gravity', 'Nebula', 'Supernova', 'Empty'])
        
        # 2. Positional and Keyword Parsing
        
        # Step through the parts, starting after 'Source' and 'Name'
        current_index = 2
        remaining_parts = parts[current_index:]
        
        if is_tile or not remaining_parts:
            # Handle simple system tiles and empty space
            planet_data['Type'] = 'System Tile'
            planet_data['Modifiers'] = " ".join(remaining_parts)
            parsed_planets.append(planet_data)
            continue
            
        # Try to find R/I by parsing backwards from the end of the line, or by known numeric positions
        r_val, i_val = 'N/A', 'N/A'
        
        # --- Attempt to locate R/I values ---
        
        # The values are floats/ints. We look for the first two numeric values after index 2
        numeric_indices = [i for i, p in enumerate(remaining_parts) if re.match(r'^\d+(\.\d)?$', p)]
        
        if len(numeric_indices) >= 2:
            r_val = remaining_parts[numeric_indices[0]]
            i_val = remaining_parts[numeric_indices[1]]
            
            # The part *before* R is the Type and/or Race
            type_race_parts = remaining_parts[:numeric_indices[0]]
            
            # 3. Determine Type, Race, and R/I
            
            # Type is always the first word(s)
            planet_data['Type'] = " ".join(type_race_parts)
            
            # Extract R/I
            planet_data['R'] = r_val.replace('.0', '')
            planet_data['I'] = i_val.replace('.0', '')
            
            # Remove R/I and the parts leading up to them from the remaining text
            current_index += numeric_indices[1] + 1
            remaining_parts = parts[current_index:]
            
            # 4. Keyword Parsing for Modifiers/Tech/Ability
            
            Techs = []
            Modifiers = []
            Ability_parts = []
            
            for part in remaining_parts:
                part_clean = part.strip().strip(':')
                
                if part_clean in TECH_KEYWORDS:
                    Techs.append(part_clean)
                elif part_clean in MODIFIER_KEYWORDS:
                    Modifiers.append(part_clean)
                elif re.match(r'^[A-Z]{3,}', part) and part_clean in ['Arborec', 'Hacan', 'Jol-Nar', 'L1Z1X', 'Letnev', 'Mentak', 'Muaat', 'Naalu', 'Nekro', 'Saar', 'Sardakk', 'Sol', 'Winnu', 'Xxcha', 'Yin', 'Yssaril', 'Mahact', 'Nomad', 'Vuil\'raith', 'Titans', 'Empyrean', 'Naaz-Rokha', 'Argent', 'Last', 'Ral-Nel', 'Deep', 'Firmament', 'Obsidian', 'Crimson']:
                    planet_data['Race/HS'] = part_clean
                else:
                    Ability_parts.append(part)
            
            planet_data['Tech'] = " / ".join(Techs) if Techs else 'N/A'
            planet_data['Modifiers'] = ", ".join(Modifiers) if Modifiers else 'N/A'
            
            # If a Race/HS was found, it was wrongly included in Type, so clean Type
            if planet_data['Race/HS'] != 'N/A':
                 planet_data['Type'] = " ".join([w for w in planet_data['Type'].split() if w.lower() not in planet_data['Race/HS'].lower()])
                 if not planet_data['Type']: planet_data['Type'] = '-'
            
            # Reconstruct the Ability/Neutral Units from remaining text
            full_ability_text = " ".join(Ability_parts)
            
            if 'Draw a relic' in full_ability_text or 'infantry' in full_ability_text:
                if 'Neutral Units' in full_ability_text:
                    ability_split = full_ability_text.split('Neutral Units:')
                    planet_data['Ability'] = clean_text(ability_split[0])
                    planet_data['Neutral Units'] = clean_text(ability_split[1])
                else:
                    planet_data['Ability'] = clean_text(full_ability_text)

        # 5. Finalize the Type/R/I check (for any remaining errors)
        if planet_data['R'] == 'N/A' and planet_data['I'] == 'N/A':
            # This is a fallback for tiles that were misclassified (e.g., TE Thunder's Edge)
            if 'Legendary' in planet_data['Ability'] or 'Legendary' in planet_data['Modifiers']:
                # Attempt to parse R/I from the first number after the name, just before 'Legendary'
                # This is highly brittle, so we only do it if the line looks like a Legendary Planet.
                number_match = re.findall(r'(\d)\s+(\d)\s+Legendary', line)
                if number_match:
                    planet_data['R'] = number_match[0][0]
                    planet_data['I'] = number_match[0][1]
                    
        parsed_planets.append(planet_data)

    return parsed_planets

def generate_planets_markdown(data):
    """Generates the final RAG markdown table for all planets and systems."""
    
    markdown_output = "## 🪐 Galactic Planets and Systems (Static Map Data)\n\n"
    markdown_output += "| Source | Name | R/I | Type/Trait | Tech Specialty | Modifiers | Race/HS | Ability/Neutral Units |\n"
    markdown_output += "| :--- | :--- | :--- | :--- | :--- | :--- | :--- | :--- |\n"

    for planet in data:
        # Skip generic system tile duplicates/blanks that don't need a row
        if planet['Name'].replace(' ', '') in ['beta-Wormhole+GravityRift', 'beta-Wormhole', '⍺-Wormhole', 'AsteroidField', 'GravityRift', 'Nebula', 'Supernova', 'EntropicScar']: continue

        # Standardize R/I and handle special cases
        r_val = planet['R'].replace('.0', '')
        i_val = planet['I'].replace('.0', '')
        ri = f"R{r_val} / I{i_val}" if r_val != 'N/A' else 'N/A'
        
        # Use the name as the type for simple tiles like Empty Space
        planet_type = planet['Type'] if planet['Type'] != 'N/A' else planet['Name']
        
        # Remove redundant tech names from the type field
        techs_in_type = [t for t in planet['Tech'].split(' / ') if t in planet_type]
        for t in techs_in_type:
            planet_type = planet_type.replace(t, '').strip()
        
        # Final cleanup for table readability
        ability_text = planet['Ability']
        if planet['Neutral Units'] != 'N/A':
            ability_text += f" **Units:** {planet['Neutral Units']}"

        markdown_output += (
            f"| {planet['Source']} "
            f"| **{planet['Name']}** "
            f"| {ri} "
            f"| {planet_type} "
            f"| {planet['Tech']} "
            f"| {planet['Modifiers']} "
            f"| {planet['Race/HS']} "
            f"| {ability_text} |\n"
        )
        
    return markdown_output

def write_to_file(filename, content, subdirectory="structuredData"):
    """Creates the subdirectory if it doesn't exist and writes the content to the file."""
    try:
        os.makedirs(subdirectory, exist_ok=True)
        file_path = os.path.join(subdirectory, filename)
        with open(file_path, 'w', encoding='utf-8') as f:
            f.write(content)
        print(f"Successfully created: {file_path}")
    except Exception as e:
        print(f"Error writing file {file_path}: {e}")

# --- 3. Execution ---

if __name__ == '__main__':
    print("Starting generation of Planets and Systems RAG file...")

    # Clean the data one last time to catch stray spaces before output
    for line in PLANETS_FLAT_DATA.split('\n'):
        line = clean_text(line)

    parsed_data = parse_planets_flat_data(PLANETS_FLAT_DATA)
    planets_markdown_output = generate_planets_markdown(parsed_data)
    
    write_to_file("planets_systems_RAG.md", planets_markdown_output, subdirectory=SUBDIRECTORY)

    print("\nPlanets and Systems file generation complete. The core of your TI4 data structure is now complete! 🚀")