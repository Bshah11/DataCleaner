import pandas as pd
import os
import re

# --- Configuration (Based on your DataCleaner project structure) ---
RAW_DOCS_DIR = "RawData"
STRUCTURED_DATA_DIR = "StructuredData"
os.makedirs(STRUCTURED_DATA_DIR, exist_ok=True)

# NOTE: Filename confirmed from your upload and folder checks.
INPUT_CSV_FILENAME = "Copy of TI_4 Evernoob's Super Cheat Sheet 1.6 - Planets.csv" 
OUTPUT_MARKDOWN_FILE = os.path.join(STRUCTURED_DATA_DIR, "ti4_planets_master.md")

INPUT_PATH = os.path.join(RAW_DOCS_DIR, INPUT_CSV_FILENAME)


def format_planets_data_for_rag(file_path):
    """
    Reads the clean, horizontal Planets CSV and converts it into granular, 
    structured Markdown blocks for RAG indexing.
    """
    print(f"Reading clean Planets CSV from: {file_path}...")
    
    try:
        # Read the file assuming it is horizontally structured
        # We need to skip the initial two metadata rows before the actual header
        df = pd.read_csv(file_path, encoding='utf-8', skiprows=2) 
        
        # Clean column names (strip whitespace)
        df.columns = df.columns.str.strip()
        
    except Exception as e:
        print(f"❌ ERROR: Failed to load/parse Planets CSV. Check delimiter or format. Error: {e}")
        return []

    print(f"Formatting {len(df)} planet entries...")
    rag_documents_text = []
    
    # We assume the first column is the unique identifier (Planet Name)
    identifier_column = df.columns[0]
    
    for index, row in df.iterrows():
        planet_name = str(row[identifier_column]).strip()
        
        # --- Create a strongly structured Markdown entry ---
        entry = f"### COMPONENT: {planet_name.upper()}\n"
        entry += f"SOURCE_TYPE: PLANET_DATA\n"
        
        # Add all attributes as clean key-value pairs
        for col in df.columns:
            if col != identifier_column:
                value = str(row[col]).strip()
                
                # Filter out empty or unnecessary values
                if value and value.lower() not in ['nan', 'none', 'n/a', '0', 'false', '0 (x0)', 'nan / nan', '']: 
                    
                    # Clean key name (e.g., 'Planet Trait' -> 'PLANET_TRAIT')
                    clean_key = col.strip().upper().replace(' ', '_').replace('-', '_')
                    
                    entry += f"--- {clean_key}:\n{value}\n"
        
        rag_documents_text.append(entry)
        
    return rag_documents_text

def main():
    # Final path check
    master_csv_path = os.path.join(RAW_DOCS_DIR, INPUT_CSV_FILENAME)
    if not os.path.exists(master_csv_path):
        print(f"❌ ERROR: Input CSV file not found at {master_csv_path}. Please check file name and RawData/ folder.")
        return

    # 1. Format the data into Markdown blocks
    markdown_blocks = format_planets_data_for_rag(master_csv_path)
    
    if not markdown_blocks:
        print("❌ ERROR: No planet data blocks were created. Check input CSV content.")
        return
         
    # 2. Write all data to the designated Markdown file
    with open(OUTPUT_MARKDOWN_FILE, 'w', encoding='utf-8') as f:
        # Separate the blocks with the master separator for clear indexing
        f.write("\n\n##################################################\n\n".join(markdown_blocks))
        
    print(f"\n✅ Data Cleaning Complete: {len(markdown_blocks)} planet blocks saved.")
    print(f"Output saved to: {OUTPUT_MARKDOWN_FILE}")
    print("Review this Markdown file to ensure all attributes are correct.")

if __name__ == "__main__":
    main()