import requests
from bs4 import BeautifulSoup, Tag
import os
import re 

# --- Configuration ---
TARGET_URL = "https://www.tirules.com/F_naalu" 
SUBDIRECTORY = "faction_lrr" 

# --- Utility Function ---
def get_html_content(source):
    # (Function implementation remains the same for fetching content)
    if source.startswith('http'):
        print(f"Fetching HTML content from URL: {source}")
        try:
            headers = {
                'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36'
            }
            response = requests.get(source, headers=headers, timeout=10)
            response.raise_for_status() 
            return response.text
        except requests.exceptions.RequestException as e:
            print(f"Error fetching URL: {e}")
            return None
    elif os.path.exists(source):
        with open(source, 'r', encoding='utf-8') as f:
            return f.read()
    else:
        print(f"Error: Source '{source}' not recognized as a valid URL or local file.")
        return None

def clean_name_to_key(name):
    """ Cleans and lowers a name for use in IDs. Handles Omega symbols explicitly. """
    key = name.lower().strip()
    key = key.replace('ω', 'omega').replace('Ω', 'omega') 
    key = re.sub(r'[^a-z0-9\s_]', '', key)
    return key.replace(' ', '_').replace('__', '_').strip('_')

def generate_component_id(faction_name, base_name):
    """ Generates the static, revision-independent Component ID (e.g., naalu_mech). """
    faction_key = clean_name_to_key(faction_name)
    component_key = clean_name_to_key(base_name)
    return f"{faction_key}_{component_key}"

def generate_revision_id(faction_name, base_name, revision_number):
    """ Generates the revision-specific ID (e.g., naalu_mech_2). """
    component_id = generate_component_id(faction_name, base_name)
    return f"{component_id}_{revision_number}"


def scrape_and_format_lrr(url, output_subdir):
    """
    Scrapes the TI4 LRR page and outputs the content in the RAG-optimized Markdown format,
    using positional logic to infer component type when necessary.
    """
    html_content = get_html_content(url)
    if not html_content:
        return

    soup = BeautifulSoup(html_content, 'html.parser')
    markdown_output = []
    
    # 1. Extract Faction Name
    faction_header = soup.find('header')
    faction_name = faction_header.get_text(strip=True).replace('Twilight Imperium Rule Help', '').strip() if faction_header else "Unknown Faction"
    if faction_name == "Unknown Faction" or not faction_name:
         print("Error: Could not find faction name.")
         return
         
    print(f"Faction Name Found: {faction_name}")
    output_filename = f"{faction_name.replace(' ', '_')}_lrr.md"
    
    # --- L1: Document Header and Metadata ---
    markdown_output.append(f"# {faction_name}")
    markdown_output.append(f"* **Document Type:** Faction LRR Notes")
    markdown_output.append(f"* **LRR Source Version:** LRR v2.5 (or latest scraped version)")
    markdown_output.append("\n---\n")

    # 2. Find all component blocks (Two-Pass Logic)
    article = soup.find('article')
    h1_tags = article.find_all('h1') if article else []
    component_groups = {} 
    
    # New state variable for positional inference
    promissory_note_encountered = False
    
    # --- Pass 1: Group and Count Revisions & Infer Type ---
    for h1 in h1_tags:
        full_name = h1.get_text(strip=True)
        revision_count = full_name.count('Ω') + full_name.count('ω')
        
        # Determine the base name (remove type and all omega symbols)
        base_name = re.sub(r'\s*\(.*\)\s*', '', full_name) 
        base_name = base_name.replace('Ω', '').replace('ω', '').strip()
        
        # Extract component type
        sub_tag = h1.find('sub')
        component_type = None # Start with None
        
        if sub_tag:
            # Type is explicitly defined, use it.
            component_type = sub_tag.get_text(strip=True).strip('()')
            
            # Check for the key marker word
            if "Promissory Note" in component_type:
                promissory_note_encountered = True
        
        # --- Positional Inference Logic ---
        elif not promissory_note_encountered:
            # If no <sub> tag was found AND we haven't seen a Promissory Note yet, 
            # assume it is a Faction Ability (or similar base ability).
            component_type = "Faction Ability"
            print(f"Inferred type for '{base_name}' as 'Faction Ability' (Missing <sub> tag).")
            
        else:
            # If no <sub> tag was found, but we HAVE seen a Promissory Note, 
            # we must default to a generic name and log a warning.
            component_type = "Faction Component (Type Unknown)"
            print(f"WARNING: Skipping inference for '{base_name}'. Missing <sub> tag after Promissory Note marker.")
            
        # Only process if we have a type (or a type was inferred)
        if component_type:
            if base_name not in component_groups:
                component_groups[base_name] = []
            
            component_groups[base_name].append({
                'h1': h1,
                'full_name': full_name,
                'base_name': base_name,
                'revision_count': revision_count,
                'component_type': component_type # Store the determined type
            })

    # --- Pass 2: Format and Tag Status (Conditional Metadata) ---
    for base_name, revisions in component_groups.items():
        max_revision_count = max(r['revision_count'] for r in revisions) if revisions else 0
        revisions.sort(key=lambda x: x['revision_count'])
        
        for rev_data in revisions:
            h1 = rev_data['h1']
            full_name = rev_data['full_name']
            revision_count = rev_data['revision_count']
            component_type = rev_data['component_type'] # Retrieve the stored type
            
            notes_list = h1.find_next_sibling('ol', class_='note')
            
            if notes_list:
                
                # Determine Base Metadata
                component_id = generate_component_id(faction_name, base_name)
                clean_header_name = base_name

                # --- Conditional Revision/Status Logic ---
                
                # If revision exists (Codex item)
                if revision_count > 0:
                    source = "Codex"
                    status = "Superseded"
                    if revision_count == max_revision_count:
                        status = "Current"
                    revision_id = generate_revision_id(faction_name, base_name, revision_count)
                
                # --- L2: Component Header and Metadata ---
                markdown_output.append(f"## {clean_header_name}")
                markdown_output.append(f"* **Component ID:** {component_id}") 
                markdown_output.append(f"* **Component Type:** {component_type}") # Use the determined type
                
                # Add conditional fields only if a revision exists
                if revision_count > 0:
                    markdown_output.append(f"* **Revision ID:** {revision_id}")
                    markdown_output.append(f"* **Source:** {source}")
                    markdown_output.append(f"* **Revision Number:** {revision_count}")
                    markdown_output.append(f"* **Status:** {status}")

                # --- L3: Clarification Notes ---
                markdown_output.append("\n### Clarification Notes")
                
                # Extract individual notes from <li> tags
                for i, li in enumerate(notes_list.find_all('li'), 1):
                    note_text = li.get_text(strip=True)
                    markdown_output.append(f"{i}. {note_text}")
                    
                markdown_output.append("\n---\n")
            else:
                print(f"Warning: Skipping component '{full_name}' (No <ol class='note'> found immediately after).")

    # 3. Save the formatted content
    if not markdown_output:
        print("Scraping completed, but no content was extracted.")
        return

    os.makedirs(output_subdir, exist_ok=True)
    output_path = os.path.join(output_subdir, output_filename)
    
    with open(output_path, 'w', encoding='utf-8') as f:
        f.write('\n'.join(markdown_output))
        
    print(f"\nSuccessfully scraped and saved data to: {output_path}")

# --- Main Execution ---
if __name__ == "__main__":
    scrape_and_format_lrr(TARGET_URL, SUBDIRECTORY)