import requests
from bs4 import BeautifulSoup, Tag
import os
import re 
import time # Import time for adding a delay between requests

# --- Configuration ---
PARENT_URL = "https://www.tirules.com"
SUBDIRECTORY = "faction_lrr" 

# --- Utility Functions ---

def get_html_content(source):
    """
    Reads HTML content from a local file or fetches it from a URL.
    """
    if source.startswith('http'):
        print(f"Fetching HTML content from URL: {source}")
        try:
            headers = {
                'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36'
            }
            # Adding a small, user-agent specific delay (politeness)
            time.sleep(1) 
            response = requests.get(source, headers=headers, timeout=15)
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

# --- NEW FUNCTION FOR GATHERING ALL FACTION URLs ---

def get_all_faction_urls(parent_url):
    """
    Scrapes the parent page to find all faction links by anchoring on <h1>Faction Notes</h1>
    """
    html_content = get_html_content(parent_url)
    if not html_content:
        return []

    soup = BeautifulSoup(html_content, 'html.parser')
    faction_urls = []

    # 1. Find the anchor heading
    anchor_heading = soup.find('h1', string=re.compile(r'Faction Notes', re.IGNORECASE))

    if not anchor_heading:
        print("ERROR: Could not find the anchor heading '<h1>Faction Notes</h1>'.")
        return []

    # 2. Find the immediate next sibling <ol> tag
    # We loop through siblings in case there's an intervening tag (like a <p> or <div>)
    faction_list = anchor_heading.find_next_sibling('ol')

    if not faction_list:
        print("ERROR: Could not find the <ol> immediately following '<h1>Faction Notes</h1>'.")
        return []

    print("Found faction link list. Extracting URLs...")
    
    # 3. Extract all links from the ordered list
    for li in faction_list.find_all('li'):
        link = li.find('a')
        if link and link.get('href'):
            # Construct the full URL if it's a relative path
            href = link.get('href')
            full_url = requests.compat.urljoin(parent_url, href)
            faction_urls.append(full_url)
    
    print(f"Successfully found {len(faction_urls)} faction URLs.")
    return faction_urls

# --- CORE SCRAPING LOGIC (Modified to accept a URL) ---

def scrape_and_format_lrr(url, output_subdir):
    """
    Scrapes a single TI4 LRR page and outputs the content in the RAG-optimized Markdown format.
    (Contains the same component processing logic as before)
    """
    html_content = get_html_content(url)
    if not html_content:
        return 0, "Unknown"

    soup = BeautifulSoup(html_content, 'html.parser')
    markdown_output = []
    
    # 1. Extract Faction Name
    faction_header = soup.find('header')
    faction_name = faction_header.get_text(strip=True).replace('Twilight Imperium Rule Help', '').strip() if faction_header else "Unknown Faction"
    if faction_name == "Unknown Faction" or not faction_name:
         print(f"Error: Could not find faction name on page {url}.")
         return 0, "Unknown"
         
    output_filename = f"{faction_name.replace(' ', '_')}_lrr.md"
    
    # --- L1: Document Header and Metadata ---
    markdown_output.append(f"# {faction_name}")
    markdown_output.append(f"* **Document Type:** Faction LRR Notes")
    markdown_output.append("\n---\n")

    # 2. Find all component blocks (Two-Pass Logic)
    article = soup.find('article')
    h1_tags = article.find_all('h1') if article else []
    component_groups = {} 
    promissory_note_encountered = False # For inference logic
    
    # --- Pass 1: Group and Count Revisions & Infer Type ---
    for h1 in h1_tags:
        full_name = h1.get_text(strip=True)
        revision_count = full_name.count('Ω') + full_name.count('ω')
        base_name = re.sub(r'\s*\(.*\)\s*', '', full_name) 
        base_name = base_name.replace('Ω', '').replace('ω', '').strip()
        
        sub_tag = h1.find('sub')
        component_type = None 
        
        if sub_tag:
            component_type = sub_tag.get_text(strip=True).strip('()')
            if "Promissory Note" in component_type:
                promissory_note_encountered = True
        
        elif not promissory_note_encountered:
            component_type = "Faction Ability"
        else:
            component_type = "Faction Component (Type Unknown)"
            
        if component_type:
            if base_name not in component_groups:
                component_groups[base_name] = []
            
            component_groups[base_name].append({
                'h1': h1,
                'full_name': full_name,
                'base_name': base_name,
                'revision_count': revision_count,
                'component_type': component_type
            })

    # --- Pass 2: Format and Tag Status (Conditional Metadata) ---
    for base_name, revisions in component_groups.items():
        max_revision_count = max(r['revision_count'] for r in revisions) if revisions else 0
        revisions.sort(key=lambda x: x['revision_count'])
        
        for rev_data in revisions:
            h1 = rev_data['h1']
            full_name = rev_data['full_name']
            revision_count = rev_data['revision_count']
            component_type = rev_data['component_type']
            
            notes_list = h1.find_next_sibling('ol', class_='note')
            
            if notes_list:
                
                # Determine Base Metadata
                component_id = generate_component_id(faction_name, base_name)
                clean_header_name = base_name

                # Conditional Revision/Status Logic
                if revision_count > 0:
                    source = "Codex"
                    status = "Superseded"
                    if revision_count == max_revision_count:
                        status = "Current"
                    revision_id = generate_revision_id(faction_name, base_name, revision_count)
                
                # --- L2: Component Header and Metadata ---
                markdown_output.append(f"## {clean_header_name}")
                markdown_output.append(f"* **Component ID:** {component_id}") 
                markdown_output.append(f"* **Component Type:** {component_type}")
                
                if revision_count > 0:
                    markdown_output.append(f"* **Revision ID:** {revision_id}")
                    markdown_output.append(f"* **Source:** {source}")
                    markdown_output.append(f"* **Revision Number:** {revision_count}")
                    markdown_output.append(f"* **Status:** {status}")

                # --- L3: Clarification Notes ---
                markdown_output.append("\n### Clarification Notes")
                
                for i, li in enumerate(notes_list.find_all('li'), 1):
                    note_text = li.get_text(strip=True)
                    markdown_output.append(f"{i}. {note_text}")
                    
                markdown_output.append("\n---\n")
            # Else warning is suppressed for cleaner output during bulk scrape

    # 3. Save the formatted content
    if not markdown_output:
        return 0, faction_name

    os.makedirs(output_subdir, exist_ok=True)
    output_path = os.path.join(output_subdir, output_filename)
    
    with open(output_path, 'w', encoding='utf-8') as f:
        f.write('\n'.join(markdown_output))
        
    return len(markdown_output), faction_name


# --- Main Execution ---
if __name__ == "__main__":
    print(f"Starting bulk scrape process from parent URL: {PARENT_URL}")
    
    # 1. Get all faction URLs
    faction_urls = get_all_faction_urls(PARENT_URL)
    
    if not faction_urls:
        print("Process aborted: No faction URLs found.")
    else:
        total_files = 0
        total_lines = 0
        
        # 2. Iterate and scrape each faction page
        for i, url in enumerate(faction_urls):
            print(f"\n--- Scraping Page {i+1} of {len(faction_urls)}: {url} ---")
            lines_written, faction_name = scrape_and_format_lrr(url, SUBDIRECTORY)
            
            if lines_written > 0:
                total_files += 1
                total_lines += lines_written
                print(f"SUCCESS: Saved {faction_name} data.")
            else:
                print(f"FAILURE: Could not process {faction_name} data.")

        print("\n==============================================")
        print(f"✅ BULK SCRAPE COMPLETE: {total_files} files created in '{SUBDIRECTORY}/'")
        print(f"Total lines of structured Markdown content: {total_lines}")
        print("==============================================")