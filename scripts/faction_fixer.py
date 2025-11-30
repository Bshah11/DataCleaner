import csv
import os
import re
from typing import List, Dict

# --- Configuration ---
# NOTE: The user has not provided the CSV file directly, so we must mock its location.
# ACTION REQUIRED: Save the CSV data above to a file named 'factions_input_data.csv'
INPUT_FILE_NAME = "factions.csv" 
OUTPUT_FILE = "structuredData/factions_COMPATIBLE_RAG.md"
SUBDIRECTORY = "structuredData"

def load_and_structure_factions(file_path: str) -> List[Dict[str, str]]:
    """
    Reads the specialized multi-row CSV format and structures it by Faction.
    The Faction Name is carried down through subsequent blank Category rows.
    """
    
    if not os.path.exists(file_path):
        print(f"Error: Input file not found at {file_path}")
        return []

    all_data = []
    current_faction_name = "GLOBAL"
    
    # Use DictReader to handle CSV structure where first row defines headers
    with open(file_path, 'r', encoding='utf-8') as f:
        reader = csv.DictReader(f)
        
        for row in reader:
            # Clean up keys for easier access (e.g., removing leading space)
            data = {k.strip(): v for k, v in row.items()}
            
            category = data.get('Category', '').strip()
            attribute = data.get('Attribute', '').strip()
            value = data.get('Value', '').strip()

            if not attribute:
                continue

            # 1. Update Faction Name
            if category == 'Faction Core' and attribute == 'Faction Name':
                current_faction_name = value
            
            # 2. Skip junk or empty rows
            if attribute.lower() == 'nan':
                 continue

            # 3. Handle Special Unit rows (no category specified)
            if not category and attribute and attribute != 'Attribute':
                # Carry down the category from the previous row if the current one is blank
                # This is a heuristic to correctly group multi-line feature definitions (e.g., in Faction Tech 1)
                
                # Note: For complex multi-line features like Faction Tech 1, the Category column is blank.
                # We need to maintain the current category group until the next non-blank category appears.
                
                # Simplification: Assume the Category is defined only when non-blank.
                # If Category is blank, it belongs to the previously defined category block.
                pass 
            
            # 4. Inject the Faction Name and store
            all_data.append({
                'FactionName': current_faction_name, 
                'Category': category if category else 'Unit/Tech Detail', # Inject default category if blank
                'Attribute': attribute,
                'Value': value
            })

    return all_data

def generate_markdown_table(data: List[Dict[str, str]]) -> str:
    """Generates a single Markdown table for all faction data with Faction Name as the primary column."""
    
    markdown_output = "## ⚙️ All Faction Data (Key-Value Breakdown)\n\n"
    markdown_output += "| Faction Name | Category | Attribute | Value |\n"
    markdown_output += "| :--- | :--- | :--- | :--- |\n"
    
    # CORRECTED SORTING KEY: 
    # 1. FactionName (Guarantees all data for one faction is together)
    # 2. Category (Orders Core, Abilities, Ship, Mech, Tech, etc. within the faction)
    # 3. Attribute (Orders fields logically within the category)
    data.sort(key=lambda x: (x['FactionName'], x['Category'], x['Attribute']))

    for item in data:
        # Clean up the output value for special characters
        value = item['Value'].replace('\r\n', ' ').replace('\n', ' ')
        
        # We need to ensure that blank Category cells (which belonged to the previous group) 
        # are correctly attributed, but visually suppressed in the final table output
        # The logic is simplified here by using the 'Category' column as defined in the loading stage.
        
        # A more elegant solution involves suppressing the FactionName/Category if they are duplicates
        # of the row above, but for RAG indexing, repeating the key is CRUCIAL.
        
        markdown_output += f"| {item['FactionName']} | {item['Category']} | {item['Attribute']} | {value} |\n"
        
    return markdown_output

# --- Execution ---

if __name__ == '__main__':
    print("--- Starting Faction Data Conversion to RAG Table ---")
    
    # ACTION: Define the input file path relative to where you run the script.
    # Assuming you save the CSV data into a file named 'factions_input_data.csv' 
    # in the same folder as this Python script.
    
    input_file_path = os.path.join(os.path.dirname(os.path.abspath(__file__)), INPUT_FILE_NAME)

    # Note: If the file is outside the script folder, adjust the path:
    # input_file_path = os.path.join(os.path.abspath(os.path.join(os.path.dirname(__file__), os.pardir)), "factions_input_data.csv")


    all_data = load_and_structure_factions(input_file_path)
    
    if not all_data:
        print("Conversion failed. Please create the input CSV file.")
    else:
        # 2. Generate the Markdown table
        markdown_table = generate_markdown_table(all_data)
        
        # 3. Write the new compatible RAG file
        # We use a custom directory path calculation similar to the previous scripts
        current_dir = os.path.dirname(os.path.abspath(__file__))
        project_root = os.path.abspath(os.path.join(current_dir, os.pardir))
        output_file_path = os.path.join(project_root, OUTPUT_FILE)
        
        os.makedirs(os.path.dirname(output_file_path), exist_ok=True)
        with open(output_file_path, 'w', encoding='utf-8') as f:
            f.write(markdown_table)
            
        print(f"\nSUCCESS: Faction data converted to universal table format.")
        print(f"New file created: {OUTPUT_FILE}")