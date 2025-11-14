import os
import re

# --- 1. Data Definition ---

OBJECTIVES_DATA = {
    "Public Objectives": {
        "Stage I (1 VP)": [
            {"Name": "Erect a Monument", "Trigger": "Status Phase", "Condition": "Spend 8 resources."},
            {"Name": "Sway the Council", "Trigger": "Status Phase", "Condition": "Spend 8 influence."},
            {"Name": "Negociate Trade Routes", "Trigger": "Status Phase", "Condition": "Spend 5 trade goods."},
            {"Name": "Lead from the Front", "Trigger": "Status Phase", "Condition": "Spend a total of 3 tokens from your tactic and/or strategy pools."},
            {"Name": "Diversify Research", "Trigger": "Status Phase", "Condition": "Own 2 technologies in each of 2 colors."},
            {"Name": "Establish a Perimeter", "Trigger": "Status Phase", "Condition": "Have 4 PDS units on the game board."},
            {"Name": "Develop Weaponry", "Trigger": "Status Phase", "Condition": "Own 2 unit upgrade technologies."},
            {"Name": "Fuel the War Machine", "Trigger": "Status Phase", "Condition": "Have 3 space docks on the game board."},
            {"Name": "Found Research Outposts", "Trigger": "Status Phase", "Condition": "Control 3 planets that have technology specialties."},
            {"Name": "Monopolize PRODUCTION", "Trigger": "Status Phase", "Condition": "Control 4 industrial planets."},
            {"Name": "Expand Borders", "Trigger": "Status Phase", "Condition": "Control 6 planets in non-home systems."},
            {"Name": "Mine Rare Minerals", "Trigger": "Status Phase", "Condition": "Control 4 hazardous planets."},
            {"Name": "Control the Region", "Trigger": "Status Phase", "Condition": "Have 1 or more ships in 6 systems."},
            {"Name": "Forge an Alliance", "Trigger": "Status Phase", "Condition": "Control 4 cultural planets."},
            {"Name": "Amass Wealth", "Trigger": "Status Phase", "Condition": "Spend 3 influence, 3 resources and 3 trade goods."},
            {"Name": "Build Defenses", "Trigger": "Status Phase", "Condition": "Have 4 or more structures."},
            {"Name": "Discover Lost Outposts", "Trigger": "Status Phase", "Condition": "Control 2 planets that have attachments."},
            {"Name": "Hoard Raw Materials", "Trigger": "Status Phase", "Condition": "Control planets that have a combined resource value of at least 12."},
            {"Name": "Engineer a Marvel", "Trigger": "Status Phase", "Condition": "Have your flagship or a warsun on the board."},
            {"Name": "Explore Deep Space", "Trigger": "Status Phase", "Condition": "Have units in 3 systems that do not contain planets."},
            {"Name": "Occupy the Fringe", "Trigger": "Status Phase", "Condition": "Have 9 or more ground forces on a planet that does not contain 1 of your space docks."},
            {"Name": "Improve Infrastructure", "Trigger": "Status Phase", "Condition": "Have structures on 3 planets outside of your home system."},
            {"Name": "Make History", "Trigger": "Status Phase", "Condition": "Have units in 2 systems that contain legendary planets, Mecatol Rex or anomalies."},
            {"Name": "Populate the Outer Rim", "Trigger": "Status Phase", "Condition": "Have units in 3 systems on the edge of the game board other than your home system."},
            {"Name": "Seize an Icon", "Trigger": "Status Phase", "Condition": "Control a legendary planet."},
            {"Name": "Raise a Fleet", "Trigger": "Status Phase", "Condition": "Have 5 or more non-fighter ships in 1 system."},
            {"Name": "Establish Hegemony", "Trigger": "Status Phase", "Condition": "Control planets that have a combined influence value of at least 12."},
            {"Name": "Strengthen Bonds", "Trigger": "Status Phase", "Condition": "Have another player's promissory note in your play area."}
        ],
        "Stage II (2 VP)": [
            {"Name": "Found a Golden Age", "Trigger": "Status Phase", "Condition": "Spend 16 resources."},
            {"Name": "Manipulate Galactic Law", "Trigger": "Status Phase", "Condition": "Spend 16 influence."},
            {"Name": "Master the Laws of Physics", "Trigger": "Status Phase", "Condition": "Own 4 technologies of the same color."},
            {"Name": "Centralize Galactic Trade", "Trigger": "Status Phase", "Condition": "Spend 10 trade goods."},
            {"Name": "Galvanize the People", "Trigger": "Status Phase", "Condition": "Spend a total of 6 tokens from your tactic and/or strategy pools."},
            {"Name": "Gather a Mighty Fleet", "Trigger": "Status Phase", "Condition": "Have 5 dreadnoughts on the board."},
            {"Name": "Master of Sciences", "Trigger": "Status Phase", "Condition": "Own 2 technologies in each of 4 colors."},
            {"Name": "Revolutionize Warfare", "Trigger": "Status Phase", "Condition": "Own 3 unit upgrade technologies."},
            {"Name": "Form Galactic Brain Trust", "Trigger": "Status Phase", "Condition": "Control 5 planets that have technology specialties."},
            {"Name": "Integrated Economy", "Trigger": "Status Phase", "Condition": "Control 4 industrial planets."}, # Duplicated name/effect removed, checking source
            {"Name": "Subdue the Galaxy", "Trigger": "Status Phase", "Condition": "Control 11 planets in non-home systems."},
            {"Name": "Unify the Colonies", "Trigger": "Status Phase", "Condition": "Control 6 planets that each have the same planet trait."},
            {"Name": "Hold Vast Reserves", "Trigger": "Status Phase", "Condition": "Spend 6 influence, 6 resources, and 6 trade goods."},
            {"Name": "Construct Massive Cities", "Trigger": "Status Phase", "Condition": "Have 7 or more structures."},
            {"Name": "Reclaim Ancient Monuments", "Trigger": "Status Phase", "Condition": "Control 3 planets that have attachments."},
            {"Name": "Achieve Supremacy", "Trigger": "Status Phase", "Condition": "Have your flagship or war sun in another player's home system or the Mecatol Rex system."},
            {"Name": "Patrol Vast Territories", "Trigger": "Status Phase", "Condition": "Have units in 5 systems that do not contain planets."},
            {"Name": "Protect The Border", "Trigger": "Status Phase", "Condition": "Have structures on 5 planets outside of your home system."},
            {"Name": "Become a Legend", "Trigger": "Status Phase", "Condition": "Have units in 4 systems that contain legendary planets, Mecatol Rex, or anomalies."},
            {"Name": "Control the Borderlands", "Trigger": "Status Phase", "Condition": "Have units in 5 systems on the edge of the game board other than your home system."},
            {"Name": "Command an Armada", "Trigger": "Status Phase", "Condition": "Have 8 or more non-fighter ships in 1 system."},
            {"Name": "Dictate Policy", "Trigger": "Agenda Phase", "Condition": "There are 3 or more laws in play."},
            {"Name": "Occupy the Seat of the Empire", "Trigger": "Status Phase", "Condition": "Control Mecatol Rex and have 3 or more ships in its system."}
        ]
    },
    "Secret Objectives": {
        "1 VP each (maximum 3 scored + in hand)": [
            {"Name": "Unveil Flagship", "Trigger": "Action Phase", "Condition": "Win a space combat in a system that contains your flagship. You cannot score this objective if your flagship is destroyed in the combat."},
            {"Name": "Adapt New Strategies", "Trigger": "Status Phase", "Condition": "Own 2 faction technologies. 'Valefar Assimilator' technologies do not count toward this objective."},
            {"Name": "Turn their Fleets to Dust", "Trigger": "Action Phase", "Condition": "Use SPACE CANNON to destroy the last of a player's ships in a system."},
            {"Name": "Destroy their Greatest Ship", "Trigger": "Action Phase", "Condition": "Destroy another player's war sun or flagship."},
            {"Name": "Form a Spy Network", "Trigger": "Status Phase", "Condition": "Discard 5 action cards."},
            {"Name": "Spark a Rebellion", "Trigger": "Action Phase", "Condition": "Win a combat against a player who has the most victory points."},
            {"Name": "Threaten Enemies", "Trigger": "Status Phase", "Condition": "Have 1 or more ships in a system that is adjacent to another player's home system."},
            {"Name": "Make an Example of their World", "Trigger": "Action Phase", "Condition": "Use BOMBARDMENT to destroy the last of a player's ground forces on a planet."},
            {"Name": "Cut Supply Lines", "Trigger": "Status Phase", "Condition": "Have 1 or more ships in the same system as another player's space dock."},
            {"Name": "Become the Gatekeeper", "Trigger": "Status Phase", "Condition": "Have one or more ships in a system that contains an alpha wormhole and 1 or more ships in a system that contains a beta wormhole."},
            {"Name": "Intimidate the Council", "Trigger": "Status Phase", "Condition": "Have 1 or more ships in 2 systems that are adjacent to Mexatol Rex's system."},
            {"Name": "Conquer the Weak", "Trigger": "Status Phase", "Condition": "Control 1 planet that is in another player's home system."},
            {"Name": "Learn the Secrets of the Cosmos", "Trigger": "Status Phase", "Condition": "Have 1 or more ships in 3 systems that are each adjacent to an anomaly."},
            {"Name": "Corner the Market", "Trigger": "Status Phase", "Condition": "Control 4 planets that each have the same planet trait."},
            {"Name": "Betray a Friend", "Trigger": "Action Phase", "Condition": "Win a combat against a player whose promissory note you had in your play area at the start of your tactical action."},
            {"Name": "Foster Cohesion", "Trigger": "Status Phase", "Condition": "Be neighbors with all other players."},
            {"Name": "Reclaim Ancient Monuments", "Trigger": "Status Phase", "Condition": "Control 3 planets that have attachments."},
            {"Name": "Brave the Void", "Trigger": "Action Phase", "Condition": "Win a combat in an anomaly."},
            {"Name": "Darken the Skies", "Trigger": "Action Phase", "Condition": "Win a combat in another player's home system."},
            {"Name": "Mechanize the Military", "Trigger": "Status Phase", "Condition": "Have 1 mech on each of 4 planets."},
            {"Name": "Defy Space and Time", "Trigger": "Status Phase", "Condition": "Have units in the wormhole nexus."},
            {"Name": "Demonstrate your Power", "Trigger": "Action Phase", "Condition": "Have 3 or more non-fighter ships in the active system at the end of a space combat."},
            {"Name": "Produce en Masse", "Trigger": "Status Phase", "Condition": "Have units with a combined PRODUCTION value of at least 8 in a single system."},
            {"Name": "Destroy Heretical Works", "Trigger": "Status Phase", "Condition": "Purge 2 of your relic fragments of any type."},
            {"Name": "Prove Endurance", "Trigger": "Action Phase", "Condition": "Be the last player to pass during a game round."},
            {"Name": "Rule Distant Lands", "Trigger": "Status Phase", "Condition": "Control 2 planets that are each in or adjacent to a different, other player's home system."},
            {"Name": "Drive the Debate", "Trigger": "Agenda Phase", "Condition": "You or a planet you control are elected by an agenda."},
            {"Name": "Stake Your Claim", "Trigger": "Status Phase", "Condition": "Control a planet in a system that contains a planet controlled by another player."},
            {"Name": "Become a Martyr", "Trigger": "Action Phase", "Condition": "Lose control of a planet in a home system."},
            {"Name": "Fight With Precision", "Trigger": "Action Phase", "Condition": "Use ANTI-FIGHTER BARRAGE to destroy the last of a player's fighters in a system."}
        ]
    }
}

# --- 2. Core Logic Functions (Re-using the safe functions) ---

def clean_text(text):
    """Cleans up raw text for clean file output."""
    if not isinstance(text, str):
        return ""
    text = text.replace('\n', ' ').replace('\r', ' ').strip()
    text = ' '.join(text.split())
    return text.strip('-').strip()

def generate_objectives_markdown(data):
    """Generates the RAG markdown for Public and Secret Objectives."""
    markdown_output = "## ⭐ Galactic Objectives and Secrets\n\n"
    
    for category, tiers in data.items():
        markdown_output += f"### 📊 {category}\n\n"
        
        for tier, objectives in tiers.items():
            markdown_output += f"#### {tier}\n\n"
            markdown_output += "| Objective Name | Trigger Phase | Condition |\n"
            markdown_output += "| :--- | :--- | :--- |\n"
            
            for obj in objectives:
                name = f"**{obj['Name']}**"
                trigger = obj['Trigger']
                condition = clean_text(obj['Condition'])
                
                markdown_output += f"| {name} | {trigger} | {condition} |\n"
            
            markdown_output += "\n"
        
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
    print("Starting generation of Objectives RAG file...")

    # Clean the data (though done in the object, this is safe)
    # The data structure is nested, so cleaning inside the loop is easiest, but let's confirm the data is ready.
    # The structure looks solid, so we proceed directly to generation.

    objective_markdown_output = generate_objectives_markdown(OBJECTIVES_DATA)
    write_to_file("objectives_RAG.md", objective_markdown_output)

    print("\nFile generation complete. The file is organized in the 'structuredData' folder.")