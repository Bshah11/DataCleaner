import os
import re

# Define the subdirectory
SUBDIRECTORY = "structuredData"
def clean_text(text):
    """Cleans up raw text for clean file output."""
    if not isinstance(text, str):
        return ""
    text = text.replace('\n', ' ').replace('\r', ' ').strip()
    text = ' '.join(text.split())
    return text.strip('-').strip()

# --- Data Definitions for Relic Cards ---

RELIC_DATA = [
    {"Name": "Dominus Orb", "Flavor": "Goldos hoisted the ivory orb at the head of their army. At once, the weariness that filled the bodies and minds of each soldier vanished. They strode forth as if fresh from a week's rest.", "Effect": "Before you move units during a tactical action, you may purge this card to move and transport units that are in systems that contain 1 of your command tokens.", "Type": "Action"},
    {"Name": "Maw of Worlds", "Flavor": "No larger than a carrier, the spherical lattice held a captive singularity at its heart. As they dumped the planet's entire energy grid into its core, the black hole began to spin, the complex logic-circuitry along the lattic slowly coming to life.", "Effect": "At the start of the agenda phase, you may purge this card and exhaust all of your planets to gain any 1 technology.", "Type": "Agenda Phase"},
    {"Name": "Scepter of Emelpar", "Flavor": "As the hilt began to fuse with the flesh of her hand, she worried that she should set the scepter aside. But the whispered suggestions in her mind were too valuable and insightful to seriously consider such a rash and illogical act.", "Effect": "When you would spend a token from your strategy pool, you may exhaust this card to spend a token from your reinforcements instead.", "Type": "Passive/Exhaust"},
    {"Name": "Shard of the Throne", "Flavor": "\"What power does a broken piece of the Throne of Emperors hold? To me, none. But to everyone else...\"", "Effect": "When you gain this card, gain 1 victory point; when you lose this card, lose 1 victory point. When a player gains control of a legendary planet you control or a planet you control in your home system, that player gains this card.", "Type": "VP/Transfer"},
    {"Name": "Stellar Converter", "Flavor": "A power great enough to envelop a star, such that its energies might be concentrated...and scattered.", "Effect": "ACTION: Choose 1 non-home, non-legendary planet other than Mecatol Rex in a system that is adjacent to 1 or more of your units that have BOMBARDMENT; destroy all units on that planet and purge its attachments and its planet card. Then, place the destroyed planet token on that planet and purge this card.", "Type": "Action/Purge"},
    {"Name": "The Codex", "Flavor": "No single tome could contain the collected knowledge of millennia of rulers. Thus, the last Emperor built a massive cruiser, its holds bulging with crystal info-matrices. It roams the outer reaches of the Mecatol system, awaiting a summons that will never come.", "Effect": "ACTION: Purge this card to take up to 3 action cards of your choice from the action card discard pile.", "Type": "Action/Purge"},
    {"Name": "The Crown of Emphidia", "Flavor": "The machines of the forgotten throne-world could only be controlled through the data-impulses of the black-barbed crown.", "Effect": "After you perform a tactical action, you may exhaust this card to explore 1 planet you control. At the end of the status phase, if you control the \"Tomb of Emphidia,\" you may purge this card to gain 1 victory point.", "Type": "Passive/Exhaust/VP"},
    {"Name": "The Crown of Thalnos", "Flavor": "A cloud of satellites spewed from the dreadnought's hull, drifting into a halo around the vessel. The battle seemed to pause for one long moment, before the drones' weapons flared, unleashing beams of energy in all directions.", "Effect": "During each combat round, this card's owner may reroll any number of their dice, applying +1 to the results; any units that reroll dice but do not produce at least 1 hit are destroyed.", "Type": "Combat/Passive"},
    {"Name": "The Obsidian", "Flavor": "The inky blackness of the blade evoked feelings of discomfort and nausea in all who saw it. All but Sharsiss. It whispered to him promises of power. Promises of a reckoning that would see the Collective unmade. \"Good,\" he thought. \"Let them burn.\"", "Effect": "When you gain this card, draw 1 secret objective. You can have 1 additional scored or unscored secret objective.", "Type": "Immediate/Passive"},
    {"Name": "The Prophet's Tears", "Flavor": "\"So you're going to drink a vial of murky liquid we found in a stasis vault on a dead world because you think it's the concentrated genetic essence of an entire species' most brilliant minds...and you think I'm being irrational?\"", "Effect": "When you research a technology, you may exhaust this card to ignore 1 prerequisite or draw 1 action card.", "Type": "Tech/Exhaust"},
    {"Name": "Dynamis Core", "Flavor": "N/A", "Effect": "While this card is in your play area, your commodity value is increased by 2. ACTION: Purge this card to gain trade goods equal to your commodity value+2.", "Type": "Passive/Action/Purge"},
    {"Name": "JR-XS455-O", "Flavor": "N/A", "Effect": "ACTION: Exhaust this agent and choose a player; that player may spend 3 resources to place a structure on a planet they control. If they do not, they gain 1 trade good.", "Type": "Action/Exhaust (Agent)"},
    {"Name": "Nanoforge", "Flavor": "N/A", "Effect": "ACTION: Attach this card to a non-legendary, non-home planet you control; its resource and influence values are increased by 2 and it is a legendary planet. This action cannot be performed once attached.", "Type": "Action/Attachment"},
    {"Name": "Circlet of the Void", "Flavor": "N/A", "Effect": "Your units do not roll for gravity rifts, and you ignore the movement effects of other anomalies. ACTION: Exhaust this card to explore a frontier token in a system that does not contain any other players' ships.", "Type": "Passive/Exhaust"},
    {"Name": "Book of Latvinia", "Flavor": "N/A", "Effect": "When you gain this card, research up to 2 technologies that have no prerequisites. ACTION: Purge this card; if you control planets that have all 4 types of technology specialties, gain 1 victory point. Otherwise, gain the speaker token.", "Type": "Immediate/Action/Purge"},
    {"Name": "Neuraloop", "Flavor": "N/A", "Effect": "When a public objective is revealed, you may purge one of your relics to discard that objective and replace it with a random objective from any objective deck; that objective is a public objective, even if it is a secret objective.", "Type": "Objective Phase/Purge"},
    {"Name": "The Silver Flame", "Flavor": "N/A", "Effect": "The Silver Flame may be exchanged as part of a transaction. ACTION: Roll 1 die and purge this card; if the result is a 10, gain 1 victory point. Otherwise, purge your home system and all units in it; you cannot score public objectives. Put The Fracture into play if it is not already.", "Type": "Action/Purge/High Risk"},
    {"Name": "Lightrail Ordnance", "Flavor": "N/A", "Effect": "Your space docks gain SPACE CANNON 5 (x2). You may use your space dock's SPACE CANNON against ships that are adjacent to their systems.", "Type": "Passive/Combat"},
    {"Name": "The Triad", "Flavor": "N/A", "Effect": "This card can be readied and spent as if it were a planet card. Its resource and influence values are equal to 3 plus the number of different types of relic fragments you own. [X resource and X influence icons]", "Type": "Passive/Resource"},
    {"Name": "Metali Void Shielding", "Flavor": "N/A", "Effect": "Each time hits are produced against 1 or more of your non-fighter ships, 1 of those ships may use SUSTAIN DAMAGE as if it had that ability.", "Type": "Passive/Combat"},
    {"Name": "Heart of Ixth", "Flavor": "N/A", "Effect": "After any die is rolled, you may exhaust this card to add or subtract 1 from its result.", "Type": "Exhaust/Die Roll"},
    {"Name": "Metali Void Armaments", "Flavor": "N/A", "Effect": "During the \"ANTI-FIGHTER BARRAGE\" step of space combat, you may resolve ANTI-FIGHTER BARRAGE 6 (x3) against your opponent's units.", "Type": "Passive/Combat"},
    {"Name": "The Quantumcore", "Flavor": "N/A", "Effect": "When you gain this card, gain your breakthrough. You have SYNERGY for all technology types. [four colour SYNERGY icon]", "Type": "Immediate/Passive/Tech"},
]

# --- Markdown Generator ---

def generate_relic_markdown(data):
    """Generates the RAG markdown for all relic cards."""
    markdown_output = "## 💎 Relic Cards\n\n"
    markdown_output += "| Relic Name | Effect Summary | Type | Full Effect | Flavor Text |\n"
    markdown_output += "| :--- | :--- | :--- | :--- | :--- |\n"
    
    for relic in data:
        name = f"**{relic['Name']}**"
        
        # A concise summary for quick lookups
        effect_summary = relic['Type'].replace('/', ' / ')
        
        # Full text cleaning
        full_effect = clean_text(relic['Effect'])
        flavor_text = clean_text(relic['Flavor'])
        
        markdown_output += f"| {name} | {effect_summary} | {relic['Type']} | {full_effect} | {flavor_text} |\n"
    
    return markdown_output

# --- File Writing and Execution ---

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

# --- Combined Execution ---

if __name__ == '__main__':
    # 2. Relic Cards
    print("Starting generation of Relic Cards RAG file...")
    relic_markdown_output = generate_relic_markdown(RELIC_DATA)
    write_to_file("relic_cards_RAG.md", relic_markdown_output, subdirectory=SUBDIRECTORY)

    print("\nFile generation complete. Both new files are organized in the 'structuredData' folder.")