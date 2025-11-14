import os
import re

# --- 1. Data Definitions ---

STRATEGY_CARD_DATA = [
    {
        "Card Name": "Leadership",
        "Card Number": 1,
        "Primary Effect 1": "Gain 3 command tokens.",
        "Primary Effect 2": "Spend any amount of influence to gain 1 command token for every 3 influence spent.",
        "Secondary Prerequisite": "Spend 1 token from your strategy pool.",
        "Secondary Effect": "Spend any amount of influence to gain 1 command token for every 3 influence spent."
    },
    {
        "Card Name": "Diplomacy",
        "Card Number": 2,
        "Primary Effect 1": "Choose 1 system other than the Mecatol Rex system that contains a planet you control; each other player places a command token from his reinforcements in the chosen system.",
        "Primary Effect 2": "Then, ready up to two exhausted planets you control.",
        "Secondary Prerequisite": "Spend 1 token from your strategy pool.",
        "Secondary Effect": "Ready up to 2 exhausted planets you control."
    },
    {
        "Card Name": "Politics",
        "Card Number": 3,
        "Primary Effect 1": "Choose a player other than the speaker. That player gains the speaker token.",
        "Primary Effect 2": "Draw 2 action cards. Look at the top 2 cards of the agenda deck. Place each card on the top or bottom of the deck in any order.",
        "Secondary Prerequisite": "Spend 1 token from your strategy pool.",
        "Secondary Effect": "Draw 2 action cards."
    },
    {
        "Card Name": "Construction II",
        "Card Number": 4,
        "Primary Effect 1": "Either place 1 structure on a planet you control, or use the PRODUCTION ability of 1 of your space docks.",
        "Primary Effect 2": "Place 1 structure on a planet you control.",
        "Secondary Prerequisite": "Spend 1 token from your strategy pool.",
        "Secondary Effect": "Place 1 structure on a planet you control."
    },
    {
        "Card Name": "Trade",
        "Card Number": 5,
        "Primary Effect 1": "Gain 3 trade goods. Replenish commodities.",
        "Primary Effect 2": "Choose any number of other players. Those players use the secondary ability of this strategy card without spending a command token.",
        "Secondary Prerequisite": "Spend 1 token from your strategy pool.",
        "Secondary Effect": "Replenish commodities."
    },
    {
        "Card Name": "Warfare II",
        "Card Number": 6,
        "Primary Effect 1": "Perform a tactical action in any system without placing a command token, even if the system already has your command token in it; that system still counts as being activated.",
        "Primary Effect 2": "You may redistribute your command tokens before and after this action.",
        "Secondary Prerequisite": "Spend 1 token from your strategy pool.",
        "Secondary Effect": "Use the PRODUCTION abilities of the units in your home system."
    },
    {
        "Card Name": "Technology",
        "Card Number": 7,
        "Primary Effect 1": "Research 1 technology.",
        "Primary Effect 2": "Spend 6 resources to research 1 technology.",
        "Secondary Prerequisite": "Spend 1 token from your strategy pool and 4 resources.",
        "Secondary Effect": "Research 1 technology."
    },
    {
        "Card Name": "Imperial",
        "Card Number": 8,
        "Primary Effect 1": "Immediately score 1 public objective if you fulfill its requirements.",
        "Primary Effect 2": "Gain 1 victory point if you control Mecatol Rex; otherwise, draw 1 secret objective.",
        "Secondary Prerequisite": "Spend 1 token from your strategy pool.",
        "Secondary Effect": "Draw 1 secret objective."
    },
]

GENERIC_PN_DATA = [
    {
        "Note Name": "Support to the Throne",
        "Type": "Generic",
        "Acquisition Effect": "If not the (color) player, place it faceup in your play area and gain 1 victory point.",
        "Loss Condition": "Activate a system that contains 1 or more of the (color) player's units, or if the (color) player is eliminated.",
        "Loss Effect": "Lose 1 victory point and return this card to the (color) player."
    },
    {
        "Note Name": "Trade Agreement",
        "Type": "Generic",
        "Trigger": "When the (color) player replenishes commodities.",
        "Effect": "The (color) player gives you all of his commodities. Then, return this card to the (color) player."
    },
    {
        "Note Name": "Political Secret",
        "Type": "Generic",
        "Trigger": "When an agenda is revealed.",
        "Effect": "The (color) player cannot vote, play action cards, or use faction abilities until after that agenda has been resolved. Then, return this card to the (color) player."
    },
    {
        "Note Name": "Ceasefire",
        "Type": "Generic",
        "Trigger": "After the (color) player activates a system that contains 1 or more of your units.",
        "Effect": "The (color) player cannot move units to the active system. Then return this card to the (color) player."
    },
    {
        "Note Name": "Alliance",
        "Type": "Generic",
        "Acquisition Effect": "If not the (color) player, place it faceup in your play area. While this card is in your play area, you can use the (color) player's commander ability, if it is unlocked.",
        "Loss Condition": "When you activate a system that contains 1 or more of the (color) player's units.",
        "Loss Effect": "Return this card to the (color) player."
    },
]

# --- 2. Core Logic Functions ---

def clean_text(text):
    """Cleans up raw text for clean file output."""
    if not isinstance(text, str):
        return ""
    text = text.replace('\n', ' ').replace('\r', ' ').strip()
    text = ' '.join(text.split())
    return text.strip('-').strip()

def generate_strategy_markdown(data):
    """Generates the RAG markdown for all strategy cards."""
    markdown_output = "## 📜 Core Game Components: Strategy Cards\n\n"
    markdown_output += "| Card | Primary Effect 1 | Primary Effect 2 | Secondary Prerequisite | Secondary Effect |\n"
    markdown_output += "| :--- | :--- | :--- | :--- | :--- |\n"

    for card in data:
        card_name = f"**{card['Card Name']} ({card['Card Number']})**"
        
        markdown_output += f"| {card_name} | {card['Primary Effect 1']} | {card['Primary Effect 2']} | {card['Secondary Prerequisite']} | {card['Secondary Effect']} |\n"
        
    return markdown_output

def generate_pn_markdown(data):
    """Generates the RAG markdown for all generic promissory notes."""
    markdown_output = "## 🤝 Core Game Components: Generic Promissory Notes\n\n"
    markdown_output += "| Note Name | Type | Trigger / Acquisition | Effect / Loss Condition |\n"
    markdown_output += "| :--- | :--- | :--- | :--- |\n"

    for note in data:
        name = f"**{note['Note Name']}**"
        note_type = note.get('Type', 'N/A')
        
        # Format Acquisition/Loss Pattern
        if note['Note Name'] in ["Support to the Throne", "Alliance"]:
            acquisition_text = note.get('Acquisition Effect', 'N/A')
            loss_text = f"**Loss Condition:** {note.get('Loss Condition', 'N/A')} **Loss Effect:** {note.get('Loss Effect', 'N/A')}"
            markdown_output += f"| {name} | {note_type} | {acquisition_text} | {loss_text} |\n"
        # Format Trigger/Effect Pattern
        else:
            trigger_text = note.get('Trigger', 'N/A')
            effect_text = note.get('Effect', 'N/A')
            markdown_output += f"| {name} | {note_type} | {trigger_text} | {effect_text} |\n"
            
    return markdown_output

def write_to_file(filename, content, subdirectory="structuredData"):
    """Creates the subdirectory if it doesn't exist and writes the content to the file."""
    try:
        # Create the subdirectory
        os.makedirs(subdirectory, exist_ok=True)
        
        # Write the file
        file_path = os.path.join(subdirectory, filename)
        with open(file_path, 'w', encoding='utf-8') as f:
            f.write(content)
        
        print(f"Successfully created: {file_path}")
    except Exception as e:
        print(f"Error writing file {file_path}: {e}")

# --- 3. Execution ---

if __name__ == '__main__':
    # 1. Generate and save Strategy Cards MD
    for card in STRATEGY_CARD_DATA:
        for key, value in card.items():
            card[key] = clean_text(value)

    strategy_markdown_output = generate_strategy_markdown(STRATEGY_CARD_DATA)
    write_to_file("strategy_cards_RAG.md", strategy_markdown_output)
    
    # 2. Generate and save Generic Promissory Notes MD
    for note in GENERIC_PN_DATA:
        for key, value in note.items():
            note[key] = clean_text(value)
            
    pn_markdown_output = generate_pn_markdown(GENERIC_PN_DATA)
    write_to_file("generic_promissory_notes_RAG.md", pn_markdown_output)

    print("\nFile generation complete. The files are organized in the 'structuredData' folder.")