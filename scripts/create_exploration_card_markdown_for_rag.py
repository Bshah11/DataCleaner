import os
import re

# Define the subdirectory
SUBDIRECTORY = "structuredData"

# --- Data Definitions for Exploration Cards ---

EXPLORATION_DATA = {
    "Cultural": [
        {"Name": "Freelancers", "Quantity": 3, "Flavor": "As part of the annexation agreement, local artisans would be well paid to lay the groundwork for military installations in the newly acquired territories.", "Effect": "You may produce 1 unit in this system; you may spend influence as if it were resources to produce this unit.", "Type": "Action/Immediate"},
        {"Name": "Mercenary Outfit", "Quantity": 3, "Flavor": "\"My mates and I used to be 4th Air Legion, but we figured we could make more money working freelance.\"", "Effect": "You may place 1 infantry from your reinforcements on this planet.", "Type": "Action/Immediate"},
        {"Name": "Gamma Wormhole", "Quantity": 1, "Flavor": "The gravic sensors howled a warning. Ahead of the ship was a ring of twisted starlight, surrounding a sphere of utter darkness.", "Effect": "Place a gamma wormhole token in this system. Then, purge this card.", "Type": "Immediate/Map"},
        {"Name": "Demilitarized Zone", "Quantity": 1, "Flavor": "N/A", "Effect": "Return all structures on this planet to your reinforcements. Then, return all ground forces on this planet to the space area. Attach: Units cannot be committed to, produced on, or placed on this planet. During the agenda phase, this planet's planet card can be traded as part of a transaction.", "Type": "Attachment"},
        {"Name": "Dyson Sphere", "Quantity": 1, "Flavor": "N/A", "Effect": "Attach: This planet's resource value is increased by 2 and its influence values is increased by 1.", "Type": "Attachment"},
        {"Name": "Paradise World", "Quantity": 1, "Flavor": "N/A", "Effect": "Attach: This planet's influence value is increased by 2.", "Type": "Attachment"},
        {"Name": "Tomb of Emphidia", "Quantity": 1, "Flavor": "N/A", "Effect": "Attach: This planet's influence value is increased by 1. If the player who has the \"Crown of Emphidia\" relic has control of this planet, they can use that relic to gain 1 VP.", "Type": "Attachment"},
        {"Name": "Cultural Relic Fragment", "Quantity": 9, "Flavor": "N/A", "Effect": "ACTION: Purge 3 of your cultural relic fragments to gain 1 relic.", "Type": "Fragment"},
    ],
    "Hazardous": [
        {"Name": "Volatile Fuel Source", "Quantity": 3, "Flavor": "It turned out that the continuous lightning storms were an unlimited source of power, which was little consolation to those assigned to build the collection towers.", "Effect": "If you have at least 1 mech on this planet, or if you remove 1 infantry from this planet, gain 1 command token.", "Type": "Action/Immediate"},
        {"Name": "Expedition", "Quantity": 3, "Flavor": "The Eidolon screamed through the atmosphere, corrosive rain streaming harmlessly off the hull as it began its survey sweep.", "Effect": "If you have at least 1 mech on this planet, or if you remove 1 infantry from this planet, ready this planet.", "Type": "Action/Immediate"},
        {"Name": "Core Mine", "Quantity": 3, "Flavor": "\"If we don't seal it now, this mine is going to erupt and spew those metals you want so badly across the entire continent!\"", "Effect": "If you have at least 1 mech on this planet, or if you remove 1 infantry from this planet, gain 1 trade good.", "Type": "Action/Immediate"},
        {"Name": "Lazax Survivors", "Quantity": 1, "Flavor": "N/A", "Effect": "Attach: This planet's resource value is increased by 1 and its influence value is increased by 2.", "Type": "Attachment"},
        {"Name": "Mining World", "Quantity": 1, "Flavor": "N/A", "Effect": "Attach: This planet's resource value is increased by 2.", "Type": "Attachment"},
        {"Name": "Rich World", "Quantity": 1, "Flavor": "N/A", "Effect": "Attach: This planet's resource value is increased by 1.", "Type": "Attachment"},
        {"Name": "Warfare Research Facility", "Quantity": 1, "Flavor": "N/A", "Effect": "Attach: This planet has a red technology specialty; if this planet already has a technology specialty, this planet's resource and influence values are each increased by 1 instead.", "Type": "Attachment"},
        {"Name": "Hazardous Relic Fragment", "Quantity": 7, "Flavor": "N/A", "Effect": "ACTION: Purge 3 of your hazardous relic fragments to gain 1 relic.", "Type": "Fragment"},
    ],
    "Industrial": [
        {"Name": "Abandoned Warehouses", "Quantity": 4, "Flavor": "Far beneath the storm-wracked seas, vast storage tanks drifted in the lightless depths.", "Effect": "You may gain 2 commoditites, or you may convert up to 2 of your commodities to trade goods.", "Type": "Action/Immediate"},
        {"Name": "Functioning Base", "Quantity": 4, "Flavor": "The Imperial Survey Corp outpost had been abandoned since the Twilight Wars, but the facilities had been built to last for millennia.", "Effect": "You may gain 1 commodity, or you may spend 1 trade good or 1 commodity to draw 1 action card.", "Type": "Action/Immediate"},
        {"Name": "Local Fabricators", "Quantity": 4, "Flavor": "Edict 281: All indigenous PRODUCTION facilities are placed under control of the occupational authorities until further notice.", "Effect": "You may gain 1 commodity, or you may spend 1 trade good or 1 commodity to place 1 mech from your reinforcements on this planet.", "Type": "Action/Immediate"},
        {"Name": "Biotic Research Facility", "Quantity": 1, "Flavor": "N/A", "Effect": "Attach: This planet has a green technology specialty; if this planet already has a technology specialty, this planet's resource and influence values are each increased by 1 instead.", "Type": "Attachment"},
        {"Name": "Cybernetic Research Facility", "Quantity": 1, "Flavor": "N/A", "Effect": "Attach: This planet has a yellow technology specialty; if this planet already has a technology specialty, this planet's resource and influence values are each increased by 1 instead.", "Type": "Attachment"},
        {"Name": "Propulsion Research Facility", "Quantity": 1, "Flavor": "N/A", "Effect": "Attach: This planet has a blue technology specialty; if this planet already has a technology specialty, this planet's resource and influence values are each increased by 1 instead.", "Type": "Attachment"},
        {"Name": "Industrial Relic Fragment", "Quantity": 5, "Flavor": "N/A", "Effect": "ACTION: Purge 3 of your industrial relic fragments to gain 1 relic.", "Type": "Fragment"},
    ],
    "Frontier": [
        {"Name": "Derelict Vessel", "Quantity": 2, "Flavor": "Missing for fifty years, the Errasthua was found drifting off the Celder Nebula with her drive dead and every crewmember vanished.", "Effect": "Draw 1 secret objective.", "Type": "Immediate"},
        {"Name": "Enigmatic Device", "Quantity": 2, "Flavor": "A needle longer than a dreadnought but no wider than a landcar flew through the void, its surface glowing with a pale violet light.", "Effect": "Place this card faceup in your play area. ACTION: You may spend 6 resource and purge this card to research 1 technology.", "Type": "Component/Tech"},
        {"Name": "Gamma Relay", "Quantity": 1, "Flavor": "Old spacers would tell stories of a black gateway in the deep space beyond the outer Oort Cloud.", "Effect": "Place a gamma wormhole token in this system. Then, purge this card.", "Type": "Immediate/Map"},
        {"Name": "Ion Storm", "Quantity": 1, "Flavor": "N/A", "Effect": "Place the ion storm token in this system with either side faceup. Then, place this card in the common play area. At the end of the \"Move Ships\" or \"Retreat\" substep of a tactical action during which 1 or more of your ships use the ion storm wormhole, flip the ion storm token to its opposing side.", "Type": "Immediate/Effect"},
        {"Name": "Lost Crew", "Quantity": 2, "Flavor": "\"Mayday, mayday..this is the free trader Hrothgar...losing pressure fast...abandoning ship...Mayday...\"", "Effect": "Draw 2 action cards.", "Type": "Immediate"},
        {"Name": "Merchant Station", "Quantity": 2, "Flavor": "The deep space freeports tend to be infamous dens of criminals, but also valuable nodes in the interplanetary trade networks.", "Effect": "You may replenish your commodities, or you may convert your commodities to trade goods.", "Type": "Immediate"},
        {"Name": "Mirage", "Quantity": 1, "Flavor": "The star wasn't supposed to have a habitable planet, but one lay directly in the cruiser's path. And a cloud of starfighters was rising from the world's surface to greet it.", "Effect": "Place the Mirage planet token in this system. Gain the Mirage planet card and ready it. Then, purge this card.", "Type": "Immediate/Map"},
        {"Name": "Unknown Relic Fragment", "Quantity": 3, "Flavor": "N/A", "Effect": "The card counts as a relic fragment of any type.", "Type": "Fragment"},
        {"Name": "Dead World", "Quantity": 1, "Flavor": "N/A", "Effect": "Draw 1 relic.", "Type": "Immediate/Relic"},
        {"Name": "Minor Entropic Field", "Quantity": 1, "Flavor": "N/A", "Effect": "Gain 1 command token and 1 trade good.", "Type": "Immediate"},
        {"Name": "Entropic Field", "Quantity": 1, "Flavor": "N/A", "Effect": "Gain 1 command token and 2 trade goods.", "Type": "Immediate"},
        {"Name": "Major Entropic Field", "Quantity": 1, "Flavor": "N/A", "Effect": "Gain 1 command token and 3 trade goods.", "Type": "Immediate"},
        {"Name": "Keleres Ship", "Quantity": 2, "Flavor": "N/A", "Effect": "Gain 2 command tokens.", "Type": "Immediate"},
    ]
}

# --- Shared Utility Function ---

def clean_text(text):
    """Cleans up raw text for clean file output."""
    if not isinstance(text, str):
        return ""
    text = text.replace('\n', ' ').replace('\r', ' ').strip()
    text = ' '.join(text.split())
    # Clean up excess quotes from input
    text = text.strip('"')
    return text.strip('-').strip()

# --- Markdown Generator ---

def generate_exploration_markdown(data):
    """Generates the RAG markdown for all exploration cards."""
    markdown_output = "## 🗺️ Exploration Cards\n\n"
    
    for card_type, cards in data.items():
        markdown_output += f"### 🟢 {card_type} Exploration Cards\n\n"
        markdown_output += "| Card Name | Quantity | Effect / Attachments | Type | Flavor Text |\n"
        markdown_output += "| :--- | :--- | :--- | :--- | :--- |\n"
        
        for card in cards:
            name = f"**{card['Name']}**"
            quantity = card['Quantity']
            effect = clean_text(card['Effect'])
            card_type_tag = card['Type']
            flavor = clean_text(card['Flavor'])
            
            markdown_output += f"| {name} | {quantity} | {effect} | {card_type_tag} | {flavor} |\n"
        
        markdown_output += "\n"
        
    return markdown_output

# --- File Writing ---

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

# --- Execution ---

if __name__ == '__main__':
    print("Starting generation of Exploration Cards RAG file...")

    exploration_markdown_output = generate_exploration_markdown(EXPLORATION_DATA)
    write_to_file("exploration_cards_RAG.md", exploration_markdown_output, subdirectory=SUBDIRECTORY)

    print("\nExploration Card file generation complete.")