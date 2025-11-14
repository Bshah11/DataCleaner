import pandas as pd
import os
import re
import io
import csv

## --- Configuration (FIXED PATHS) ---
RAW_DOCS_DIR = "RawData"
STRUCTURED_DATA_DIR = "StructuredData"
os.makedirs(STRUCTURED_DATA_DIR, exist_ok=True) # Ensure this folder is created

# Corrected Input and Output Path Definitions
INPUT_CSV_FILENAME = "factions.csv" 
OUTPUT_MARKDOWN_FILENAME = "ti4_factions_final_rag.md" 

# CORRECTED OUTPUT PATH: Use os.path.join only with the top-level directory name
INPUT_PATH = os.path.join(RAW_DOCS_DIR, INPUT_CSV_FILENAME)
OUTPUT_PATH = os.path.join(STRUCTURED_DATA_DIR, OUTPUT_MARKDOWN_FILENAME)


# --- Corrected Core Parsing and Formatting ---

def load_and_format_factions_eav(file_path):
    """
    Reads the EAV (Entity-Attribute-Value) structured CSV, consolidates all attributes 
    for each faction, and returns RAG Markdown blocks.
    """
    print("Loading EAV CSV and structuring data...")
    
    try:
        # Read the file assuming standard comma delimiter and no skipped rows (since it's a clean copy)
        df = pd.read_csv(file_path, encoding='utf-8', skipinitialspace=True)
    except Exception as e:
        print(f"Error reading CSV file with pandas: {e}")
        return []

    # CRITICAL FIX: Convert the 'Attribute' column to string type first, handling NaN
    df['Attribute'] = df['Attribute'].astype(str).str.strip()
    df['Value'] = df['Value'].astype(str).str.strip()
    
    
    # Fill down the Faction Name for easier grouping later
    # The 'Faction Name' row is identified by the 'Attribute' column having the value 'Faction Name'.
    
    # 1. Temporarily identify the rows that define the Faction Name and extract the Value
    df['Faction_Name_ID'] = df.apply(
        lambda row: row['Value'].strip() 
                    if row['Attribute'].strip() == 'Faction Name' 
                    else None, 
        axis=1
    )
    
    # 2. Forward fill the Faction_Name_ID down the entire block
    df['Faction_Name_ID'] = df['Faction_Name_ID'].ffill()
    
    # Filter out initial metadata rows, keeping only the rows that define attributes
    df_clean = df[df['Attribute'] != 'Faction Name'].copy()
    
    # --- Now proceed with grouping and consolidation ---
    
    grouped = df_clean.groupby('Faction_Name_ID')
    all_markdown_blocks = []
    
    for faction_name, group in grouped:
        
        markdown_block_lines = [f"[FACTION: {faction_name.strip()}]"]
        
        # Dictionary to temporarily hold attributes for pairing (e.g., Name/Effect)
        complex_attributes = {}
        
        # 3. Consolidate and Format
        for index, row in group.iterrows():
            attribute = row['Attribute'].strip()
            value = str(row['Value']).strip() # Already stripped above, but safe

            # Standardize key for processing
            clean_key = re.sub(r'[\s\-()$\\]', '_', attribute).upper()

            # --- Pair Consolidation Logic ---
            if clean_key.endswith('_NAME') and attribute in ['Ability 1 Name', 'Ability 2 Name', 'Hero Ability Name', 'PN Name', 'Tech Name']:
                complex_attributes[clean_key] = value 
            
            elif clean_key.endswith('_EFFECT') or clean_key.endswith('_TEXT'):
                # Handle Ability/Hero/PN Effect pairing
                
                # Dynamically determine the base key (e.g., ABILITY_1)
                base_key_parts = clean_key.split('_')
                base_key = "_".join(base_key_parts[:-1]) # ABILITY_1 or PN
                name_key = base_key + "_NAME"

                if name_key in complex_attributes:
                    item_name = complex_attributes.pop(name_key)
                    markdown_block_lines.append(f"- {attribute.split(' ')[0]}: {item_name}: {value}")
                
                else:
                    # Output as a standalone key/value if no pair found
                    markdown_block_lines.append(f"- {attribute}: {value}")
            
            # --- Complex Unit/Tech (Standalone Logic) ---
            elif clean_key in ['UNIT_NAME', 'SHIP_NAME', 'MECH_NAME', 'AGENT_NAME', 'COMMANDER_NAME']:
                # For units and leaders, output the name line and the rest of the attributes follow
                markdown_block_lines.append(f"- {attribute.split(' ')[0]}: {value}")

            # --- All other simple attributes ---
            else:
                 markdown_block_lines.append(f"- {attribute}: {value}")


        all_markdown_blocks.append('\n'.join(markdown_block_lines))
        
    return all_markdown_blocks

def main():
    # Final path check
    master_csv_path = os.path.join(RAW_DOCS_DIR, INPUT_CSV_FILENAME)
    if not os.path.exists(master_csv_path):
        print(f"❌ ERROR: Input CSV file not found at {master_csv_path}. Please verify the path and filename.")
        return

    # 1. Format the data into Markdown blocks
    markdown_blocks = load_and_format_factions_eav(master_csv_path)
    
    if not markdown_blocks:
        print("❌ ERROR: No markdown blocks were created. Check input CSV content.")
        return
         
    # 2. Write all data to the designated Markdown file
    with open(OUTPUT_PATH, 'w', encoding='utf-8') as f:
        # Join all faction blocks with a strong separator for clear indexing
        f.write("\n\n##################################################\n\n".join(markdown_blocks))
        
    print(f"\n✅ Final Markdown conversion complete: {len(markdown_blocks)} faction blocks saved.")
    print(f"Output saved to: {OUTPUT_PATH}")
    print("This file is the optimal structured input for your RAG indexer.")

if __name__ == "__main__":
    main()