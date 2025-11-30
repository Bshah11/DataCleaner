import requests
from bs4 import BeautifulSoup
import re
import os
from typing import List, Dict

# --- Configuration ---
SUBDIRECTORY = "structuredData"
SOURCE_URL = "https://www.tirules.com/"
OUTPUT_FILE_NAME = "web_glossary_RAG.md"
BASE_URL = "https://www.tirules.com" 

# --- Parsing Utilities ---

def clean_text(text: str) -> str:
    """Cleans up text for final markdown output."""
    if not isinstance(text, str): return ""
    text = re.sub(r'\s*\n\s*', ' ', text)
    # Remove HTML artifact tags used by the site (like <sc> and <sub> markers)
    text = re.sub(r'<\/?sc[^>]*>', '', text)
    text = re.sub(r'<\/?sub[^>]*>', '', text)
    return ' '.join(text.split()).strip()

# --- LEVEL 2: Scrape Individual Rule Pages (FINALIZED FOR ATOMIC CHUNKING) ---

def scrape_rule_page(url: str, output_md_name: str) -> bool:
    """Visits a specific rule page and extracts ATOMIC chunks (one per point/paragraph)."""
    
    try:
        response = requests.get(url, timeout=10)
        response.raise_for_status()
    except requests.exceptions.RequestException as e:
        print(f"  !! Error fetching {url}: {e}")
        return False
        
    soup = BeautifulSoup(response.content, 'html.parser')
    
    # 1. Determine the RULE_SOURCE (The page's main subject)
    main_header_tag = soup.find('header')
    rule_source = clean_text(main_header_tag.get_text()) if main_header_tag else os.path.basename(url)

    rule_article = soup.find('article')
    if not rule_article:
        print(f"  !! Warning: Skipping {url} - No article content found.")
        return False

    compiled_rag_content = []
    current_section_id = rule_source 
    
    # Iterate over every element inside the <article> to find all rule points
    for element in rule_article.children:
        chunk_content = None
        
        if element.name in ['h1', 'h2', 'h3', 'h4']:
            # A new major or minor section starts (e.g., Future Sight, Rules Reference)
            current_section_id = clean_text(element.get_text(strip=True))
            continue # Don't chunk the header itself

        elif element.name == 'p':
            # Chunk: Paragraph content
            paragraph_text = clean_text(element.get_text(strip=True))
            if paragraph_text:
                chunk_content = paragraph_text

        elif element.name in ['ol', 'ul']:
            # Chunk: Each list item is its own chunk
            for li in element.find_all('li', recursive=False): # Only top-level LI items in this UL/OL
                # Find all text content (including nested lists) and collapse it
                list_item_text = clean_text(li.get_text(strip=True))
                
                # Check if the list item contains any text (excluding just the bullet marker)
                if list_item_text:
                    # Create the individual chunk here
                    rag_content = "##################################################\n\n"
                    rag_content += f"### RULE_SOURCE: {rule_source}\n" 
                    rag_content += f"--- SECTION_ID: {current_section_id}\n"
                    rag_content += f"--- CONTENT: {list_item_text}\n"
                    compiled_rag_content.append(rag_content)
            
            # Since we processed the entire list in the loop, we continue to the next sibling
            continue

        # If a simple paragraph was found, format it now
        if chunk_content:
            rag_content = "##################################################\n\n"
            rag_content += f"### RULE_SOURCE: {rule_source}\n" 
            rag_content += f"--- SECTION_ID: {current_section_id}\n"
            rag_content += f"--- CONTENT: {chunk_content}\n"
            compiled_rag_content.append(rag_content)

    # 4. Write all compiled content for THIS page to the file
    if compiled_rag_content:
        output_path = os.path.join(SUBDIRECTORY, output_md_name)
        os.makedirs(SUBDIRECTORY, exist_ok=True)
        with open(output_path, 'a', encoding='utf-8') as f:
            f.writelines(compiled_rag_content)
            
        return True
    
    return False

# --- LEVEL 1: Scrape Index and Find Links (Remains Robust) ---

def fetch_links(index_url: str) -> List[str]:
    """Fetches the index page and returns a list of unique rule page URLs using precise selectors."""
    print("-> Fetching index page to discover all rule links...")
    
    try:
        response = requests.get(index_url, timeout=10)
        response.raise_for_status()
    except requests.exceptions.RequestException as e:
        print(f"!! FATAL: Could not fetch index URL {index_url}: {e}")
        return []

    soup = BeautifulSoup(response.content, 'html.parser')
    unique_links = set()
    
    # Selector: ol.lrr a, ol.note a
    link_elements = soup.select('ol.lrr a, ol.note a') 
    
    for link_element in link_elements:
        href = link_element.get('href')
        if href:
            # Reconstruct the absolute URL
            full_url = requests.compat.urljoin(BASE_URL, href)
            
            # Avoid the external link and other noise
            if full_url.startswith(BASE_URL) and full_url != index_url:
                unique_links.add(full_url)
                
    print(f"-> Found {len(unique_links)} unique rule pages to scrape.")
    return list(unique_links)

# --- Main Execution ---

def process_tirules_website():
    """
    Orchestrates the entire scraping process.
    """
    # 1. Prepare output file: Clear the output file before starting
    output_path = os.path.join(SUBDIRECTORY, OUTPUT_FILE_NAME)
    if os.path.exists(output_path):
        os.remove(output_path)
        print(f"-> Cleared existing file: {OUTPUT_FILE_NAME}")

    # 2. Get all target links
    all_rule_links = fetch_links(SOURCE_URL)
    
    if not all_rule_links:
        print("Aborting. No rule links found.")
        return

    # 3. Scrape each link and compile RAG chunks
    print("\n-> Starting Level 2: Scraping individual rule pages...")
    
    for i, link in enumerate(all_rule_links):
        print(f"  Scraping [{i+1}/{len(all_rule_links)}]: {link}")
        
        # Scrape the page and append directly to the file
        success = scrape_rule_page(link, OUTPUT_FILE_NAME)
        if success:
             print(f"  Scraped successfully.")
        else:
             print(f"  Failed/Skipped. Check warnings.")

    print("\n--- Universal Web Scraper Complete. Data is organized in structuredData/web_glossary_RAG.md ---")

if __name__ == '__main__':
    print("--- Starting TI4 Web Rules Processor ---")
    process_tirules_website()