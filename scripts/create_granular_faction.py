import os
import pandas as pd
import re
import csv
import io

# --- Configuration ---
RAW_DOCS_DIR = "RawData"
STRUCTURED_DATA_DIR = "StructuredData"
os.makedirs(STRUCTURED_DATA_DIR, exist_ok=True)
# NOTE: Using the file name confirmed in previous steps
INPUT_CSV_FILENAME = "TI_4 Evernoob's Super Cheat Sheet 1.6 - Factions.csv" 
OUTPUT_CSV_FILENAME = "ti4_factions_clean_review.csv"
INPUT_PATH = os.path.join(RAW_DOCS_DIR, INPUT_CSV_FILENAME)
OUTPUT_PATH = os.path.join(STRUCTURED_DATA_DIR, OUTPUT_CSV_FILENAME)

# Columns that contain complex, multi-line nested text (and need to be 'exploded')
COMPLEX_ATTRIBUTES = [
    'Faction Abilities', 'Faction Technologies', 'Special Units', 'Flagship', 
    'Mech', 'Agent', 'Commander', 'Hero', 'Promissory Note', 'Breakthrough', 'Starting Fleet' # Added Starting Fleet as it's multi-line
]

# --- Core Parsing Function (This was the missing definition) ---
def load_and_consolidate_factions(file_path):
    """Reads the vertical CSV and groups attributes into faction blocks."""
    print("Loading CSV using robust vertical parsing...")
    
    # Read the file assuming we skip the initial junk rows
    # We use engine='python' to handle the non-standard CSV structure reliably
    try:
        with open(file_path, 'r', encoding='utf-8') as f:
            # We skip 2 rows to get past the initial junk/header lines
            df = pd.read_csv(f, header=None, skiprows=2, skipinitialspace=True, encoding='utf-8', engine='python')
    except Exception as e:
        print(f"Error reading CSV file with pandas: {e}")
        return None
    
    # We focus on columns 1 (Attribute Key) and 2 (Value)
    keys = df.iloc[:, 1].astype(str).str.strip()
    values = df.iloc[:, 2].astype(str).str.strip()
    
    consolidated_data = {}
    current_faction_name = None
    current_block = {}
    
    for key, value in zip(keys, values):
        key = key.strip()
        value = value.strip()
        
        # Heuristics to detect the start of a new Faction block (e.g., "Arborec" with an empty value)
        if key and value.lower() in ['nan', ''] and len(key) > 3 and key[0].isalpha():
            if current_faction_name:
                consolidated_data[current_faction_name] = current_block
            
            # Start a new block
            current_faction_name = key
            current_block = {"Faction Name": key}
            
        # Extract attribute:value pairs
        elif current_faction_name and key and key.lower() not in ['nan'] and value.lower() not in ['nan']:
            # Clean key name
            clean_key = key.strip()
            # For multi-line attributes, remove internal quotes and flag breaks
            if clean_key in COMPLEX_ATTRIBUTES and value:
                value = value.replace('"', '').replace('\n', ' [RULE_BREAK] ').strip()
            
            current_block[clean_key] = value

    if current_faction_name and current_faction_name not in consolidated_data:
        consolidated_data[current_faction_name] = current_block
        
    return consolidated_data

# --- New Export Function (Filter for Review) ---
def create_clean_review_csv(consolidated_data):
    """Explodes nested attributes and exports a clean CSV containing ONLY necessary columns."""
    
    granular_records = []
    
    for faction_name, data in consolidated_data.items():
        
        # 1. Handle Simple Faction-Level Attributes (e.g., Home System)
        record = {}
        record['Faction_Name'] = faction_name
        record['Component_Type'] = 'FACTION_SUMMARY'
        record['Component_ID'] = faction_name
        
        # Append all simple attributes (Home System, Commodities, Tech etc.)
        for k, v in data.items():
            if k not in COMPLEX_ATTRIBUTES:
                record[k.upper().replace(' ', '_')] = v 
        
        granular_records.append(record)

        # 2. Explode Complex Attributes into new records
        for complex_key in COMPLEX_ATTRIBUTES:
            if complex_key in data:
                # Use the [RULE_BREAK] marker to separate individual rules
                nested_rules = data[complex_key].split(' [RULE_BREAK] ')
                
                for rule_text in nested_rules:
                    if not rule_text.strip():
                        continue
                        
                    # Create a new, distinct record for this component
                    component_record = {}
                    component_record['Faction_Name'] = faction_name
                    component_record['Component_Type'] = complex_key.upper().replace(' ', '_')
                    
                    # Use the first part of the text as the Component ID (e.g., Letani Warrior II)
                    rule_id = rule_text.split(':')[0].split('(')[0].strip()
                    component_record['Component_ID'] = rule_id
                    
                    # Store the full text of the rule/component description
                    component_record['Full_Rule_Text'] = rule_text.strip()
                        
                    granular_records.append(component_record)


    # Create DataFrame from the list of granular records
    final_df = pd.DataFrame(granular_records)
    
    # Fill NaN values with empty string for a cleaner CSV visual
    final_df = final_df.fillna('')

    return final_df

def main():
    # Final path check
    master_csv_path = os.path.join(RAW_DOCS_DIR, INPUT_CSV_FILENAME)
    if not os.path.exists(master_csv_path):
        print(f"❌ ERROR: Master sheet file not found at {master_csv_path}. Please verify the path and filename.")
        return

    # Call the correctly defined function
    consolidated_data = load_and_consolidate_factions(master_csv_path)
    
    if not consolidated_data:
         print("❌ ERROR: No consolidated data found after parsing CSV.")
         return
         
    final_df = create_clean_review_csv(consolidated_data)
    
    if not final_df.empty:
        final_df.to_csv(OUTPUT_PATH, index=False, encoding='utf-8')
        print(f"\n✅ Data Cleaning Complete: {len(final_df)} granular component records saved for review.")
        print(f"Output saved to: {OUTPUT_PATH}")
    else:
        print("❌ ERROR: Final DataFrame is empty. Data processing failed.")

if __name__ == "__main__":
    main()