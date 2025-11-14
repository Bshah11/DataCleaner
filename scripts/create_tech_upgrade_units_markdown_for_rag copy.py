import os
import re

def clean_text(text):
    """Cleans up raw text, removing extra spaces and newlines."""
    if not isinstance(text, str):
        return ""
    # Replace newlines/extra spaces with a single space
    text = text.replace('\n', ' ').replace('\r', ' ').strip()
    # Replace multiple spaces with a single space
    text = ' '.join(text.split())
    # Safely replace the escaped LaTeX omega
    text = text.replace('\\Omega', '$\Omega$')
    return text.strip('-').strip()

# --- 1. Data Definitions ---

TECH_DATA = {
    "Blue Technology": [
        {"Tech Name": "Antimass Deflectors", "Prereq": "(0)", "Effect 1": "Your ships can move into and through asteroid fields.", "Effect 2": "When other players' units use SPACE CANNON against your units, apply -1 to the result of each die roll."},
        {"Tech Name": "Dark Energy Tap", "Prereq": "(0)", "Effect 1": "After you perform a tactical action in a system that contains a frontier token, if you have 1 or more ships in that system, explore that token.", "Effect 2": "Your ships can retreat into adjacent systems that do not contain other players' units even if you do not have units or control planets in that system."},
        {"Tech Name": "Gravity Drive", "Prereq": "(B)", "Effect 1": "After you activate a system, apply +1 to the move value of 1 of your ships during this tactical action.", "Effect 2": ""},
        {"Tech Name": "Sling Relay", "Prereq": "(B)", "Effect 1": "ACTION: Exhaust this card to produce 1 ship in any system that contains 1 of your space docks.", "Effect 2": ""},
        {"Tech Name": "Fleet Logistics", "Prereq": "(BB)", "Effect 1": "During each of your turns of the action phase, you may perform 2 actions instead of 1.", "Effect 2": ""},
        {"Tech Name": "Light/Wave Deflector", "Prereq": "(BBB)", "Effect 1": "Your ships can move through systems that contain other players' ships.", "Effect 2": ""},
    ],
    "Red Technology": [
        {"Tech Name": "Plasma Scoring", "Prereq": "(0)", "Effect 1": "When 1 or more of your units use BOMBARDMENT or SPACE CANNON, 1 of those units may roll 1 additional die.", "Effect 2": ""},
        {"Tech Name": "AI Development Algorithm", "Prereq": "(0)", "Effect 1": "When you research a unit upgrade technology, you may exhaust this card to ignore any 1 prerequisite.", "Effect 2": "When 1 or more of your units use PRODUCTION, you may exhaust this card to reduce the combined cost of the produced units by the number of unit upgrade technologies that you own."},
        {"Tech Name": "Magen Defense Grid $\Omega$", "Prereq": "(R)", "Effect 1": "At the start of ground combat on a planet that contains 1 or more of your structures, you may produce 1 hit and assign it to 1 of your opponent's ground forces. ($\Omega$)", "Effect 2": "When any player activates a system that contains 1 or more of your structures, place 1 infantry from your reinforcements with each of those structures. At the start of ground combat on a planet that contains 1 or more of your structures, produce 1 hit and assign it to 1 of your opponent's ground forces. (Codex 4)"},
        {"Tech Name": "Self-Assembly Routines", "Prereq": "(R)", "Effect 1": "After 1 or more of your units use PRODUCTION, you may exhaust this card to place 1 mech from your reinforcements on a planet you control in that system.", "Effect 2": "After 1 of your mechs is destroyed, gain 1 trade good."},
        {"Tech Name": "Duranium Armor", "Prereq": "(RR)", "Effect 1": "During each combat round, after you assign hits to your units, repair 1 of your damaged units that did not use Sustain Damage during this combat round.", "Effect 2": ""},
        {"Tech Name": "Assault Cannon", "Prereq": "(RRR)", "Effect 1": "At the start of a space combat in a system that contains 3 or more of your non-fighter ships, your opponent must destroy 1 of his non-fighter ships.", "Effect 2": ""},
    ],
    "Yellow Technology": [
        {"Tech Name": "Sarween Tools", "Prereq": "(0)", "Effect 1": "When 1 or more of your units use PRODUCTION, reduce the combined cost of the produced units by 1.", "Effect 2": ""},
        {"Tech Name": "Scanlink Drone Network", "Prereq": "(0)", "Effect 1": "When you activate a system, you may explore 1 planet in that system that contains 1 or more of your units.", "Effect 2": ""},
        {"Tech Name": "Graviton Laser System", "Prereq": "(Y)", "Effect 1": "You may exhaust this card before 1 or more of your units use SPACE CANNON; hits produced by those units must be assigned to non-fighter ships if able.", "Effect 2": ""},
        {"Tech Name": "Predictive Intelligence", "Prereq": "(Y)", "Effect 1": "At the end of your turn, you may exhaust this card to redistribute your command tokens.", "Effect 2": "When you cast votes during the agenda phase, you may cast 3 additional votes. If you do, and the outcome you voted for is not resolved, exhaust this card."},
        {"Tech Name": "Transit Diodes", "Prereq": "(YY)", "Effect 1": "You may exhaust this card at the start of your turn during the action phase; remove up to 4 of your ground forces from the game board and place them on 1 or more planets you control.", "Effect 2": ""},
        {"Tech Name": "Integrated Economy", "Prereq": "(YYY)", "Effect 1": "After you gain control of a planet, you may produce any number of units on that planet that have a combined cost equal or less than that planet's resource value.", "Effect 2": ""},
    ],
    "Green Technology": [
        {"Tech Name": "Neural Motivator", "Prereq": "(0)", "Effect 1": "During the status phase, draw 2 action cards instead of 1.", "Effect 2": ""},
        {"Tech Name": "Psychoarchaeology", "Prereq": "(0)", "Effect 1": "You can use technology specialties on planets you control without exhausting them, even if those planets are exhausted.", "Effect 2": "During the action phase, you can exhaust planets you control that have technology specialties to gain 1 trade good."},
        {"Tech Name": "Dacxive Animators", "Prereq": "(G)", "Effect 1": "After you win a ground combat, you may place 1 infantry from your reinforcements on that planet.", "Effect 2": ""},
        {"Tech Name": "Bio-Stims", "Prereq": "(G)", "Effect 1": "You may exhaust this card at the end of your turn to ready 1 of your planets that has a technology specialty or 1 of your other technologies.", "Effect 2": ""},
        {"Tech Name": "Hyper Metabolism", "Prereq": "(GG)", "Effect 1": "During the status phase, gain 3 command counters instead of 2", "Effect 2": ""},
        {"Tech Name": "X-89 Bacterial Weapon $\Omega$", "Prereq": "(GGG)", "Effect 1": "After 1 or more of your units use BOMBARDMENT against a planet, if at least 1 of your opponent’s infantry was destroyed, destroy all of your opponent’s infantry on that planet ($\Omega$).", "Effect 2": "Double the hits produced by your units' BOMBARDMENT and ground combat rolls. Exhaust each planet you use BOMBARDMENT against. (Codex 4)"},
    ]
}

UNIT_DATA = [
    # War Sun
    {"Unit": "War Sun", "Type": "Base", "Cost": "N/A (See Upgrade)", "Combat": "N/A", "Move": "N/A", "Capacity": "N/A", "Abilities": "You cannot produce this unit unless you own its unit upgrade technology."},
    {"Unit": "War Sun", "Type": "Upgrade (II)", "Tech Prereq": "(RRRY)", "Cost": "12", "Combat": "3 (x3)", "Move": "2", "Capacity": "6", "Abilities": "Mobile Base. Sustain Damage. BOMBARDMENT 3 (x3). Other players' units in this system lose Planetary Shield."},
    # Cruiser
    {"Unit": "Cruiser", "Type": "Base (I)", "Cost": "2", "Combat": "7", "Move": "2", "Capacity": "0", "Abilities": "None."},
    {"Unit": "Cruiser", "Type": "Upgrade (II)", "Tech Prereq": "(GYR)", "Cost": "2", "Combat": "6", "Move": "3", "Capacity": "1", "Abilities": "Stasis Capsules."},
    # Dreadnought
    {"Unit": "Dreadnought", "Type": "Base (I)", "Cost": "4", "Combat": "5", "Move": "1", "Capacity": "1", "Abilities": "Sustain Damage. BOMBARDMENT 5."},
    {"Unit": "Dreadnought", "Type": "Upgrade (II)", "Tech Prereq": "(BBY)", "Cost": "4", "Combat": "5", "Move": "2", "Capacity": "1", "Abilities": "Type IV Drive. Sustain Damage. BOMBARDMENT 5. This unit cannot be destroyed by 'Direct Hit' action cards."},
    # Destroyer
    {"Unit": "Destroyer", "Type": "Base (I)", "Cost": "1", "Combat": "9", "Move": "2", "Capacity": "0", "Abilities": "ANTI-FIGHTER BARRAGE 9 (x2)."},
    {"Unit": "Destroyer", "Type": "Upgrade (II)", "Tech Prereq": "(RR)", "Cost": "1", "Combat": "8", "Move": "2", "Capacity": "0", "Abilities": "Automated Defense Turrets. ANTI-FIGHTER BARRAGE 6 (x3)."},
    # PDS
    {"Unit": "PDS", "Type": "Base (I)", "Cost": "N/A", "Combat": "N/A", "Move": "N/A", "Capacity": "N/A", "Abilities": "Planetary Shield. SPACE CANNON 6."},
    {"Unit": "PDS", "Type": "Upgrade (II)", "Tech Prereq": "(RY)", "Cost": "N/A", "Combat": "N/A", "Move": "N/A", "Capacity": "N/A", "Abilities": "Deep SPACE CANNON. Planetary Shield. SPACE CANNON 5. You may use this unit's SPACE CANNON against ships that are adjacent to this unit's system."},
    # Carrier
    {"Unit": "Carrier", "Type": "Base (I)", "Cost": "3", "Combat": "9", "Move": "1", "Capacity": "4", "Abilities": "None."},
    {"Unit": "Carrier", "Type": "Upgrade (II)", "Tech Prereq": "(BB)", "Cost": "3", "Combat": "9", "Move": "2", "Capacity": "6", "Abilities": "XRD Transporters."},
    # Fighter
    {"Unit": "Fighter", "Type": "Base (I)", "Cost": "1 (x2)", "Combat": "9", "Move": "0", "Capacity": "0", "Abilities": "None."},
    {"Unit": "Fighter", "Type": "Upgrade (II)", "Tech Prereq": "(GB)", "Cost": "1 (x2)", "Combat": "8", "Move": "2", "Capacity": "0", "Abilities": "Advanced Fighters. This unit may move without being transported. Fighters in excess of your ships' capacity count against your fleet pool."},
    # Infantry
    {"Unit": "Infantry", "Type": "Base (I)", "Cost": "1 (x2)", "Combat": "8", "Move": "N/A", "Capacity": "N/A", "Abilities": "None."},
    {"Unit": "Infantry", "Type": "Upgrade (II)", "Tech Prereq": "(GG)", "Cost": "1 (x2)", "Combat": "7", "Move": "N/A", "Capacity": "N/A", "Abilities": "Gen Synthesis. After this unit is destroyed, roll 1 die. If the result is 6 or greater, place the unit on this card. At the start of your next turn, place each unit that is on this card on a planet you control in your home system."},
    # Space Dock
    {"Unit": "Space Dock", "Type": "Base (I)", "Cost": "N/A", "Combat": "N/A", "Move": "N/A", "Capacity": "N/A", "Abilities": "This unit's PRODUCTION value is equal to 2 more than the resource value of this planet. Up to 3 fighters in this system do not count against your ships' capacity. PRODUCTION X."},
    {"Unit": "Space Dock", "Type": "Upgrade (II)", "Tech Prereq": "(YY)", "Cost": "N/A", "Combat": "N/A", "Move": "N/A", "Capacity": "N/A", "Abilities": "Enviro Compensator. This unit's PRODUCTION value is equal to 4 more than the resource value of this planet. Up to 3 fighters in this system do not count against your ships' capacity. PRODUCTION X."},
]

# --- 2. Markdown Generation Functions ---

def generate_tech_markdown(tech_data):
    """Generates the RAG markdown for all generic technologies."""
    markdown_output = "## ⚙️ Generic Technologies (Blue, Red, Yellow, Green)\n\n"
    
    for color, techs in tech_data.items():
        markdown_output += f"### 🔹 {color}\n\n"
        markdown_output += "| Tech Name | Prerequisite | Effect 1 | Effect 2 |\n"
        markdown_output += "| :--- | :--- | :--- | :--- |\n"
        
        for tech in techs:
            name = f"**{tech['Tech Name']}**"
            prereq = tech['Prereq']
            effect1 = clean_text(tech['Effect 1'])
            effect2 = clean_text(tech['Effect 2']) or "N/A"
            
            markdown_output += f"| {name} | {prereq} | {effect1} | {effect2} |\n"
        
        markdown_output += "\n"
        
    return markdown_output

def generate_unit_markdown(unit_data):
    """Generates the RAG markdown for all generic units and their upgrades."""
    markdown_output = "## 🚀 Generic Unit Base Stats & Upgrades\n\n"
    markdown_output += "| Unit Type | Status | Cost | Combat | Move | Capacity/AFB | Tech Prereq | Special Abilities |\n"
    markdown_output += "| :--- | :--- | :--- | :--- | :--- | :--- | :--- | :--- |\n"
    
    for unit in unit_data:
        # Determine the Capacity/AFB column content based on unit type
        cap_afb = unit.get('Capacity', unit.get('Abilities'))
        if unit['Unit'] in ["Destroyer", "Fighter"]:
            cap_afb = unit.get('Abilities') # AFB is the primary stat here
        
        # Clean up the abilities field for the final cell
        abilities_text = clean_text(unit['Abilities'])
        
        markdown_output += f"| **{unit['Unit']}** | {unit['Type']} | {unit['Cost']} | {unit['Combat']} | {unit['Move']} | {cap_afb} | {unit.get('Tech Prereq', 'N/A')} | {abilities_text} |\n"
        
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
    print("Starting generation of Generic Technology and Unit files...")

    # 1. Generate and save Generic Technology MD
    tech_markdown_output = generate_tech_markdown(TECH_DATA)
    write_to_file("generic_technologies_RAG.md", tech_markdown_output)
    
    # 2. Generate and save Generic Unit/Upgrade MD
    unit_markdown_output = generate_unit_markdown(UNIT_DATA)
    write_to_file("generic_units_RAG.md", unit_markdown_output)

    print("\nFile generation complete. The files are organized in the 'structuredData' folder.")