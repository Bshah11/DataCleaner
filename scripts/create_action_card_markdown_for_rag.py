import os
import re

# Define the subdirectory
SUBDIRECTORY = "structuredData"

# --- 1. Data Definition ---

ACTION_CARD_DATA = [
    {"Name": "Sabotage", "Quantity": 4, "Phase": "Any", "When to play": "When another player plays an action card other than \"Sabotage\"", "Effect": "Cancel that action card.", "Note": "Cannot be sabotaged."},
    {"Name": "Direct Hit", "Quantity": 4, "Phase": "Action", "When to play": "After another player's ship uses Sustain Damage to cancel a hit produced by your units:", "Effect": "Destroy that ship.", "Note": "After card is played."},
    {"Name": "Flank Speed", "Quantity": 4, "Phase": "Action (Activation)", "When to play": "After you activate a system:", "Effect": "Apply +1 to the move value of each of your ships during this tactical action.", "Note": "Before moving any ships."},
    {"Name": "Maneuvering Jets", "Quantity": 4, "Phase": "Action (Movement/ Invasion)", "When to play": "Before you assign hits produced by another player's SPACE CANNON roll:", "Effect": "Cancel 1 hit.", "Note": "After making PDS rolls."},
    {"Name": "Morale Boost", "Quantity": 4, "Phase": "Action (Space Combat/ Invasion)", "When to play": "At the start of a combat round:", "Effect": "Apply +1 to the result of each of your unit's combat rolls during this combat round.", "Note": "Before making rolls."},
    {"Name": "Shields Holding", "Quantity": 4, "Phase": "Action (Space Combat)", "When to play": "Before you assign hits to your ships during a space combat:", "Effect": "Cancel up to 2 hits.", "Note": "After card is played."},
    {"Name": "Skilled Retreat", "Quantity": 4, "Phase": "Action (Space Combat)", "When to play": "At the start of a combat round:", "Effect": "Move all of your ships from the active system into an adjacent system that does not contain another player's ships; the space combat ends in a draw. Then, place a command token from your reinforcements in that system.", "Note": "Before moving ships."},
    {"Name": "War Machine", "Quantity": 4, "Phase": "Action", "When to play": "When 1 or more of your units use PRODUCTION", "Effect": "Apply +4 to the total PRODUCTION value of your units and reduce the combined cost of the produced units by 1.", "Note": "N/A"},
    
    # Generic Single-Use Cards
    {"Name": "Ancient Burial Sites", "Quantity": 1, "Phase": "Agenda", "When to play": "At the start of the agenda phase:", "Effect": "Choose 1 player. Exhaust each cultural planet owned by that player.", "Note": "After the player is chosen."},
    {"Name": "Assassinate Representative", "Quantity": 1, "Phase": "Agenda", "When to play": "After an agenda is revealed:", "Effect": "Choose 1 player. That player cannot vote on this agenda.", "Note": "After the player is chosen."},
    {"Name": "Bribery", "Quantity": 1, "Phase": "Agenda", "When to play": "After the speaker votes on an agenda:", "Effect": "Spend any number of trade goods. For each trade good spent, cast 1 additional vote for any outcome.", "Note": "TGs are not lost this way."},
    {"Name": "Bunker", "Quantity": 1, "Phase": "Action (Invasion)", "When to play": "At the start of an invasion:", "Effect": "During this invasion, apply -4 to the result of each BOMBARDMENT roll against planets you control.", "Note": "Before BOMBARDMENT rolls."},
    {"Name": "Confusing Legal Text", "Quantity": 1, "Phase": "Agenda", "When to play": "When you are elected as the outcome of an agenda:", "Effect": "Choose 1 player. That player is the elected player instead.", "Note": "After the player is chosen."},
    {"Name": "Construction Rider", "Quantity": 1, "Phase": "Agenda", "When to play": "After an agenda is revealed:", "Effect": "You cannot vote on this agenda. Predict aloud an outcome of this agenda. If your prediction is correct, place 1 space dock from your reinforcements on a planet you control.", "Note": "After the outcome is chosen."},
    {"Name": "Courageous to the End", "Quantity": 1, "Phase": "Action (Space Combat)", "When to play": "After 1 of your ships is destroyed during a space combat:", "Effect": "Roll 2 dice. For each result equal to or greater than that ship's combat value, your opponent must choose and destroy 1 of his ships.", "Note": "Before making the rolls."},
    {"Name": "Cripple Defenses", "Quantity": 1, "Phase": "Action", "When to play": "ACTION:", "Effect": "Choose 1 planet. Destroy each PDS on that planet.", "Note": "After the planet is chosen."},
    {"Name": "Diplomacy Rider", "Quantity": 1, "Phase": "Agenda", "When to play": "After an agenda is revealed:", "Effect": "You cannot vote on this agenda. Predict aloud an outcome of this agenda. If your prediction is correct, choose 1 system that contains a planet you control. Each other player places a command token from their reinforcements in that system.", "Note": "After the outcome is chosen."},
    {"Name": "Disable", "Quantity": 1, "Phase": "Action (Invasion)", "When to play": "At the start of an invasion in a system that contains 1 or more of your opponents' PDS units:", "Effect": "Your opponents' PDS units lose Planetary Shield and SPACE CANNON during this invasion.", "Note": "Before PDS rolls."},
    {"Name": "Distinguished Councilor", "Quantity": 1, "Phase": "Agenda", "When to play": "After you cast votes on an outcome of an agenda:", "Effect": "Cast 5 additional votes for that outcome.", "Note": "Before next player votes. And/OR before resolving agenda."},
    {"Name": "Economic Initiative", "Quantity": 1, "Phase": "Action", "When to play": "ACTION:", "Effect": "Ready each cultural planet you control.", "Note": "After planets are chosen."},
    {"Name": "Emergency Repairs", "Quantity": 1, "Phase": "Action (Space Combat)", "When to play": "At the start or end of a combat round", "Effect": "Repair all of your units that have Sustain Damage in the active system.", "Note": "After choosing sustained ships."},
    {"Name": "Experimental Battlestation", "Quantity": 1, "Phase": "Action (Movement)", "When to play": "After another player moves ships into a system during a tactical ACTION:", "Effect": "Choose 1 of your space docks that is either in or adjacent to that system. That space dock uses SPACE CANNON 5 (x3) against ships in the active system.", "Note": "Before making rolls."},
    {"Name": "Fighter Prototype", "Quantity": 1, "Phase": "Action (Space Combat)", "When to play": "At the start of the first round of a space combat:", "Effect": "Apply +2 to the result of each of your fighters' combat rolls during this combat round.", "Note": "Before making rolls."},
    {"Name": "Fire Team", "Quantity": 1, "Phase": "Action (Invasion)", "When to play": "After your ground forces make combat rolls during a round of ground combat:", "Effect": "Reroll any number of your dice.", "Note": "Before making rolls."},
    {"Name": "Focused Research", "Quantity": 1, "Phase": "Action", "When to play": "ACTION:", "Effect": "Spend 4 trade goods to research 1 technology", "Note": "Before spending the TGs."},
    {"Name": "Frontline Deployment", "Quantity": 1, "Phase": "Action", "When to play": "ACTION:", "Effect": "Place 3 infantry from your reinforcements on 1 planet you control.", "Note": "After choosing the planet."},
    {"Name": "Ghost Ship", "Quantity": 1, "Phase": "Action", "When to play": "ACTION:", "Effect": "Place 1 destroyer from your reinforcements in a non-home system that contains a wormhole and does not contain other players' ships.", "Note": "After a wormhole is chosen."},
    {"Name": "Imperial Rider", "Quantity": 1, "Phase": "Agenda", "When to play": "After an agenda is revealed:", "Effect": "You cannot vote on this agenda. Predict aloud an outcome of this agenda. If your prediction is correct, gain 1 victory point.", "Note": "After the outcome is chosen."},
    {"Name": "In The Silence Of Space", "Quantity": 1, "Phase": "Action (Activation)", "When to play": "After you activate a system:", "Effect": "Choose 1 system. During this tactical action, your ships in the chosen system can move through systems that contain other players' ships.", "Note": "After choosing the system."},
    {"Name": "Industrial Initiative", "Quantity": 1, "Phase": "Action", "When to play": "ACTION:", "Effect": "Gain 1 trade good for each industrial planet you control.", "Note": "Before gaining TGs"},
    {"Name": "Infiltrate", "Quantity": 1, "Phase": "Action (Invasion)", "When to play": "When you gain control of a planet:", "Effect": "Replace each PDS and space dock that is on that planet with a matching unit from your reinforcements.", "Note": "Before placing units on the board."},
    {"Name": "Insubordination", "Quantity": 1, "Phase": "Action", "When to play": "ACTION:", "Effect": "Remove 1 token from another player's tactic pool and return it to his reinforcements.", "Note": "After payer is chosen."},
    {"Name": "Intercept", "Quantity": 1, "Phase": "Action (Space Combat)", "When to play": "After your opponent declares a retreat during a space combat:", "Effect": "Your opponent cannot retreat during this round of space combat.", "Note": "After card is played"},
    {"Name": "Leadership Rider", "Quantity": 1, "Phase": "Agenda", "When to play": "After an agenda is revealed:", "Effect": "You cannot vote on this agenda. Predict aloud an outcome of this agenda. If your prediction is correct, gain 3 command tokens.", "Note": "After the outcome is chosen"},
    {"Name": "Lost Star Chart", "Quantity": 1, "Phase": "Action (Activation)", "When to play": "After you activate a system:", "Effect": "During this tactical action, systems that contain alpha and beta wormholes are adjacent to each other.", "Note": "Before moving ships."},
    {"Name": "Lucky Shot", "Quantity": 1, "Phase": "Action", "When to play": "ACTION:", "Effect": "Destroy 1 dreadnought, cruiser, or destroyer in a system that contains a planet you control.", "Note": "After choosing the ship."},
    {"Name": "Mining Initiative", "Quantity": 1, "Phase": "Action", "When to play": "ACTION:", "Effect": "Gain trade goods equal to the resource value of 1 planet you control.", "Note": "After choosing a planet."},
    {"Name": "Parley", "Quantity": 1, "Phase": "Action (Invasion)", "When to play": "After another player commits units to land on a planet you control:", "Effect": "Return the committed units to the space area.", "Note": "After card is played."},
    {"Name": "Plague", "Quantity": 1, "Phase": "Action", "When to play": "ACTION:", "Effect": "Choose 1 planet that is controlled by another player. Roll 1 die for each infantry on that planet. For each result of 6 or greater, destroy 1 of those units.", "Note": "After choosing the planet."},
    {"Name": "Political Stability", "Quantity": 1, "Phase": "Status", "When to play": "When you would return your strategy card(s) during the status phase:", "Effect": "Do not return your strategy card(s). You do not choose strategy cards during the next strategy phase.", "Note": "After card is played."},
    {"Name": "Politics Rider", "Quantity": 1, "Phase": "Agenda", "When to play": "After an agenda is revealed:", "Effect": "You cannot vote on this agenda. Predict aloud an outcome of this agenda. If your prediction is correct, draw 3 action cards and gain the speaker token.", "Note": "After the outcome is chosen"},
    {"Name": "Public Disgrace", "Quantity": 1, "Phase": "Strategy", "When to play": "When another player chooses a strategy card during the strategy phase:", "Effect": "That player must choose a different strategy card instead, if able.", "Note": "After card is played."},
    {"Name": "Reactor Meltdown", "Quantity": 1, "Phase": "Action", "When to play": "ACTION:", "Effect": "Destroy 1 space dock in a non-home system.", "Note": "After the space dock is chosen."},
    {"Name": "Reparations", "Quantity": 1, "Phase": "Action (Invasion)", "When to play": "After another player gains control of a planet you control:", "Effect": "Exhaust 1 planet that player controls and ready 1 planet you control.", "Note": "After card is played"},
    {"Name": "Repeal Law", "Quantity": 1, "Phase": "Action", "When to play": "ACTION:", "Effect": "Discard 1 law from play.", "Note": "After the law is chosen"},
    {"Name": "Rise of a Messiah", "Quantity": 1, "Phase": "Action", "When to play": "ACTION:", "Effect": "Place 1 infantry from your reinforcements on each planet you control.", "Note": "Before placing units."},
    {"Name": "Salvage", "Quantity": 1, "Phase": "Action (Space Combat)", "When to play": "After you win a space combat:", "Effect": "Your opponent gives you all of his commodities.", "Note": "Before taking commodities."},
    {"Name": "Signal Jamming", "Quantity": 1, "Phase": "Action", "When to play": "ACTION:", "Effect": "Chose 1 non-home system that contains or is adjacent to 1 of your ships. Place a command token from another player's reinforcements in that system.", "Note": "After the system is chosen."},
    {"Name": "Spy", "Quantity": 1, "Phase": "Action", "When to play": "ACTION:", "Effect": "Choose 1 player. That player gives you 1 random action card from his hand.", "Note": "After the player is chosen."},
    {"Name": "Summit", "Quantity": 1, "Phase": "Strategy", "When to play": "At the start of the strategy phase:", "Effect": "Gain 2 command tokens.", "Note": "After card is played."},
    {"Name": "Tactical BOMBARDMENT", "Quantity": 1, "Phase": "Action", "When to play": "ACTION:", "Effect": "Choose 1 system that contains 1 or more of your units that have BOMBARDMENT. Exhaust each planet controlled by other players in that system.", "Note": "After system is chosen."},
    {"Name": "Technology Rider", "Quantity": 1, "Phase": "Agenda", "When to play": "After an agenda is revealed:", "Effect": "You cannot vote on this agenda. Predict aloud an outcome of this agenda. If your prediction is correct, research 1 technology.", "Note": "After the outcome is chosen"},
    {"Name": "Trade Rider", "Quantity": 1, "Phase": "Agenda", "When to play": "After an agenda is revealed:", "Effect": "You cannot vote on this agenda. Predict aloud an outcome of this agenda. If your prediction is correct, gain 5 trade goods.", "Note": "After the outcome is chosen"},
    {"Name": "Unexpected Action", "Quantity": 1, "Phase": "Action", "When to play": "ACTION:", "Effect": "Remove 1 of your command tokens from the game board and return it to your reinforcements.", "Note": "After counter is chosen."},
    {"Name": "Unstable Planet", "Quantity": 1, "Phase": "Action", "When to play": "ACTION:", "Effect": "Choose 1 harzadrous planet. Exhaust that planet and destroy up to 3 infantry on it.", "Note": "After planet is chosen"},
    {"Name": "Upgrade", "Quantity": 1, "Phase": "Action (Activation)", "When to play": "After you activate a system that contains 1 or more of your ships:", "Effect": "Replace 1 of your cruisers in that system with 1 dreadnought from your reinforcements.", "Note": "After unit is chosen."},
    {"Name": "Uprising", "Quantity": 1, "Phase": "Action", "When to play": "ACTION:", "Effect": "Exhaust 1 non-home planet controlled by another player. Then gain trade goods equal to its resource value.", "Note": "After planet is chosen."},
    {"Name": "Veto", "Quantity": 1, "Phase": "Agenda", "When to play": "When an agenda is revealed:", "Effect": "Discard that agenda and reveal 1 agenda from the top of the deck. players vote on this agenda instead.", "Note": "After card is played."},
    {"Name": "War Effort", "Quantity": 1, "Phase": "Action", "When to play": "ACTION:", "Effect": "Place 1 cruiser from your reinforcements in a system that contains 1 or more of your ships.", "Note": "After system is chosen."},
    {"Name": "Warfare Rider", "Quantity": 1, "Phase": "Agenda", "When to play": "After an agenda is revealed:", "Effect": "You cannot vote on this agenda. Predict aloud an outcome of this agenda. If your prediction is correct, place 1 dreadnought from your reinforcements in a system that contains 1 or more of your ships.", "Note": "After the outcome is chosen"},
    {"Name": "Blitz", "Quantity": 1, "Phase": "Action", "When to play": "At the start of an invasion", "Effect": "Each of your non-fighter ships in the active system that do not have BOMBARDMENT gain BOMBARDMENT 6 until the end of the invasion.", "Note": "N/A"},
    {"Name": "Counterstroke", "Quantity": 1, "Phase": "Action", "When to play": "After a player activates a system that contains 1 of your command tokens", "Effect": "Return that command token to your tactic pool.", "Note": "N/A"},
    {"Name": "Fighter Conscription", "Quantity": 1, "Phase": "Action", "When to play": "Action", "Effect": "Place 1 fighter from your reinforcements in each system that contains 1 or more of your space docks or units that have capacity; they cannot be placed in systems that contain other players' ships.", "Note": "N/A"},
    {"Name": "Forward Supply Base", "Quantity": 1, "Phase": "Action", "When to play": "After another player activates a system that contains your units", "Effect": "Gain 3 trade goods. Then, choose another player to gain 1 trade good.", "Note": "N/A"},
    {"Name": "Ghost Squad", "Quantity": 1, "Phase": "Action", "When to play": "After a player commits units to land on a planet you control", "Effect": "Move any number of ground forces from any planet you control in the active system to any other planet you control in the active system.", "Note": "N/A"},
    {"Name": "Hack Election", "Quantity": 1, "Phase": "Agenda", "When to play": "After an agenda is revealed", "Effect": "During this agenda, voting begins with the player to the right of the speaker and continues counterclockwise.", "Note": "N/A"},
    {"Name": "Harness Energy", "Quantity": 1, "Phase": "Action", "When to play": "After you activate an anomaly", "Effect": "Replenish your commodities.", "Note": "N/A"},
    {"Name": "Impersonation", "Quantity": 1, "Phase": "Action", "When to play": "Action", "Effect": "Spend 3 influence to draw 1 secret objective.", "Note": "N/A"},
    {"Name": "Insider Information", "Quantity": 1, "Phase": "Agenda", "When to play": "After an agenda is revealed", "Effect": "Look at the top 3 Cards of the agenda deck.", "Note": "N/A"},
    {"Name": "Master Plan", "Quantity": 1, "Phase": "Action", "When to play": "After you perform an action", "Effect": "You may perform an additional action this turn.", "Note": "N/A"},
    {"Name": "Plagiarize", "Quantity": 1, "Phase": "Action", "When to play": "Action", "Effect": "Spend 5 influence and choose a non-faction technology owned by 1 of your neighbors; gain that technology.", "Note": "N/A"},
    {"Name": "Rally", "Quantity": 1, "Phase": "Action", "When to play": "After you activate a system that contains another player's ships", "Effect": "Place 2 command tokens from your reinforcements in your fleet pool.", "Note": "N/A"},
    {"Name": "Reflective Shielding", "Quantity": 1, "Phase": "Action", "When to play": "When one of your ships uses Sustain Damage during combat", "Effect": "Produce 2 hits against your opponent's ships in the active system.", "Note": "N/A"},
    {"Name": "Sanction", "Quantity": 1, "Phase": "Agenda", "When to play": "After an agenda is revealed", "Effect": "You cannot vote on this agenda. Predict aloud an outcome of this agenda. If your prediction is correct, each player that voted for that outcome returns 1 command token from their fleet supply to their reinforcements.", "Note": "N/A"},
    {"Name": "Scramble Frequency", "Quantity": 1, "Phase": "Action", "When to play": "After another player makes a BOMBARDMENT, SPACE CANNON, or ANTI-FIGHTER BARRAGE roll:", "Effect": "That player rerolls all of their dice.", "Note": "N/A"},
    {"Name": "Solar Flare", "Quantity": 1, "Phase": "Action", "When to play": "After you activate a system", "Effect": "During this movement, other players cannot use SPACE CANNON against your ships.", "Note": "N/A"},
    {"Name": "Archaeological Expedition", "Quantity": 1, "Phase": "Action", "When to play": "Action", "Effect": "Reveal the top 3 cards of an exploration deck that matches a planet you control; gain any relic fragments that you reveal and discard the rest.", "Note": "N/A"},
    {"Name": "Confounding Legal Text", "Quantity": 1, "Phase": "Agenda", "When to play": "When another player is elected as the outcome of an agenda", "Effect": "You are the elected player instead.", "Note": "N/A"},
    {"Name": "Coup D'etat", "Quantity": 1, "Phase": "Action", "When to play": "When another player would perform a strategic ACTION:", "Effect": "End that player's turn; the strategic action is not resolved and the strategy card is not exhausted.", "Note": "N/A"},
    {"Name": "Deadly Plot", "Quantity": 1, "Phase": "Agenda", "When to play": "During the agenda phase when an outcome would be resolved", "Effect": "If you voted for or predicted another outcome, discard the agenda instead; the agenda is resolved with no effect and it is not replaced. Then, exhaust all of your planets.", "Note": "N/A"},
    {"Name": "Decoy Operation", "Quantity": 1, "Phase": "Action", "When to play": "After another player activates a system that contains 1 or more of your structures", "Effect": "Remove up to 2 of your ground forces from the game board and place them on a planet you control in the active system.", "Note": "N/A"},
    {"Name": "Diplomatic Pressure", "Quantity": 4, "Phase": "Agenda", "When to play": "When an agenda is revealed", "Effect": "Choose another player; that player must give you 1 promissory note from their hand.", "Note": "N/A"},
    {"Name": "Divert Funding", "Quantity": 1, "Phase": "Action", "When to play": "Action", "Effect": "Return a non-unit upgrade, non-faction technology that you own to your technology deck. Then, research another technology.", "Note": "N/A"},
    {"Name": "Exploration Probe", "Quantity": 1, "Phase": "Action", "When to play": "Action", "Effect": "Explore a frontier token that is in or adjacent to a system that contains 1 or more of your ships.", "Note": "N/A"},
    {"Name": "Manipulate Investments", "Quantity": 1, "Phase": "Strategy", "When to play": "At the start of the strategy phase:", "Effect": "Place a total of 5 trade goods from the supply on strategy cards of your choice; you must place these tokens on at least 3 different cards.", "Note": "N/A"},
    {"Name": "Nav Suite", "Quantity": 1, "Phase": "Action", "When to play": "After you activate a system", "Effect": "During the \"Movement\" step of this tactical action, ignore the effect of anomalies.", "Note": "N/A"},
    {"Name": "Refit Troops", "Quantity": 1, "Phase": "Action", "When to play": "Action", "Effect": "Choose 1 or 2 of your infantry on the game board; replace each of those infantry with mechs.", "Note": "N/A"},
    {"Name": "Reveal Prototype", "Quantity": 1, "Phase": "Action", "When to play": "At the start of a combat", "Effect": "Spend 4 resources to research a unit upgrade technology of the same type as 1 of your units that is participating in this combat.", "Note": "N/A"},
    {"Name": "Reverse Engineer", "Quantity": 1, "Phase": "Any", "When to play": "After another player discards an action card that has a component ACTION:", "Effect": "Take that action card from the discard pile.", "Note": "N/A"},
    {"Name": "Rout", "Quantity": 1, "Phase": "Action", "When to play": "At the start of the \"Announce Retreats\" step of space combat, if you are the defender", "Effect": "Your opponent must announce a retreat, if able.", "Note": "N/A"},
    {"Name": "Scuttle", "Quantity": 1, "Phase": "Action", "When to play": "Action", "Effect": "Choose 1 or 2 of your non-fighter ships on the game board and return them to your reinforcements; gain trade goods equal to the combined cost of those ships.", "Note": "N/A"},
    {"Name": "Seize Artifact", "Quantity": 1, "Phase": "Action", "When to play": "Action", "Effect": "Choose 1 of your neighbors that has 1 or more relic fragments. That player must give you 1 relic fragment of your choice.", "Note": "N/A"},
    {"Name": "Waylay", "Quantity": 1, "Phase": "Action", "When to play": "Before you roll dice for ANTI-FIGHTER BARRAGE", "Effect": "Hits from this roll are produced against all ships (not just fighters).", "Note": "N/A"},
    {"Name": "Black Market Dealings", "Quantity": 1, "Phase": "During a Transaction", "When to play": "When you are negotiating a transaction:", "Effect": "You and the other player can include relics, action cards, and unscored secret objectives as part of the transaction. This card cannot be canceled.", "Note": "N/A"},
    {"Name": "Brilliance", "Quantity": 1, "Phase": "Action", "When to play": "ACTION:", "Effect": "Ready 1 of your planets that has a technology specialty or choose 1 player to gain their breakthrough.", "Note": "N/A"},
    {"Name": "Crash Landing", "Quantity": 1, "Phase": "After space combat", "When to play": "When your last ship in the active system is destroyed:", "Effect": "Place 1 of your ground forces from the space area of the active system onto a planet in that system other than Mecatol Rex; if the planet contains other players' units, place your ground force into coexistence.", "Note": "N/A"},
    {"Name": "Crisis", "Quantity": 1, "Phase": "Action Phase", "When to play": "At the end of any player's turn, if there are at least 2 players who have not passed:", "Effect": "Skip the next player's turn.", "Note": "N/A"},
    {"Name": "Exchange Program", "Quantity": 1, "Phase": "Action", "When to play": "ACTION:", "Effect": "Choose another player. You and that player may agree to place 1 infantry from each of you reinforcements into coexistence on a planet the other player controls that contains their ground forces; if no agreement is reached, you each discard 1 token from your fleet pool.", "Note": "N/A"},
    {"Name": "Extreme Duress", "Quantity": 1, "Phase": "Action Phase", "When to play": "At the start of another player's turn, if they have a readied strategy card:", "Effect": "If that player's next action is not a strategic action, they discard all of their action cards, gives you all of their trade goods, and shows you all of their secret objectives.", "Note": "N/A"},
    {"Name": "Lie in Wait", "Quantity": 1, "Phase": "After a Transaction", "When to play": "After 2 of your neighbours resolve a transaction:", "Effect": "Look at each of those player's hands of action cards, then choose and take 1 action card from each.", "Note": "N/A"},
    {"Name": "Mercenary Contract", "Quantity": 1, "Phase": "Action", "When to play": "ACTION:", "Effect": "Spend 2 trade goods to place 2 neutral infantry on any non-home planet that contains no units; if that planet was owned by another player, they return its planet card to the planet card deck.", "Note": "N/A"},
    {"Name": "Pirate Contract", "Quantity": 4, "Phase": "Action", "When to play": "ACTION:", "Effect": "Place 1 neutral destroyer in a non-home system that contains no non-neutral ships.", "Note": "N/A"},
    {"Name": "Pirate Fleet", "Quantity": 1, "Phase": "Action", "When to play": "ACTION:", "Effect": "Spend 3 resources to place 1 neutral carrier, 1 neutral cruiser, 1 neutral destroyer, and 2 neutral fighters in a non-home system that contains no ships.", "Note": "N/A"},
    {"Name": "Rescue", "Quantity": 1, "Phase": "After movement", "When to play": "After another player moves ships into a system that contains your ships:", "Effect": "You may move 1 of your ships into the active system from any system that does not contain one of your command tokens.", "Note": "N/A"},
    {"Name": "Strategize", "Quantity": 4, "Phase": "Action", "When to play": "ACTION:", "Effect": "Perform the secondary ability of any readied or unchosen strategy card", "Note": "N/A"},
    {"Name": "Overrule", "Quantity": 1, "Phase": "Action", "When to play": "ACTION:", "Effect": "Perform the primary ability of any readied or unchosen strategy card", "Note": "N/A"},
]

# --- 2. Core Logic Functions ---

def clean_text(text):
    """Cleans up raw text for clean file output."""
    if not isinstance(text, str):
        return ""
    text = text.replace('\n', ' ').replace('\r', ' ').strip()
    text = ' '.join(text.split())
    return text.strip('-').strip()

def generate_action_cards_markdown(data):
    """Generates the RAG markdown for all action cards."""
    markdown_output = "## 🃏 Action Cards\n\n"
    markdown_output += "| Card Name | Quantity | Phase | When to Play (Trigger) | Effect | Play Note |\n"
    markdown_output += "| :--- | :--- | :--- | :--- | :--- | :--- |\n"

    for card in data:
        name = f"**{card['Name']}**"
        
        # Combine the Phase and Trigger columns for clear context
        phase = clean_text(card['Phase'])
        trigger = clean_text(card['When to play'])
        
        # Clean the rest of the fields
        quantity = card['Quantity']
        effect = clean_text(card['Effect'])
        note = clean_text(card['Note']) or "N/A"
        
        markdown_output += f"| {name} | {quantity} | {phase} | {trigger} | {effect} | {note} |\n"
        
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
    print("Starting generation of Action Cards RAG file...")

    action_markdown_output = generate_action_cards_markdown(ACTION_CARD_DATA)
    write_to_file("action_cards_RAG.md", action_markdown_output, subdirectory=SUBDIRECTORY)

    print("\nAction Card file generation complete.")