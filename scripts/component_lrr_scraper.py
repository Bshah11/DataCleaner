import requests
from bs4 import BeautifulSoup
import os
import re
import time
from pathlib import Path
from urllib.parse import urljoin

# --- Path Configuration ---
SCRIPT_DIR = Path(__file__).resolve().parent
OUTPUT_BASE_DIR = SCRIPT_DIR.parent / "structuredData" / "components"
PARENT_URL = "https://www.tirules.com"

def clean_id(text):
    """Cleans text into a snake_case ID/Filename."""
    text = text.replace('Ω', '').replace('ω', '').strip()
    key = text.lower()
    key = re.sub(r'[^a-z0-9\s_]', '', key)
    return key.replace(' ', '_').replace('__', '_').strip('_')

def scrape_component_data(url, output_subdir):
    """
    Scrapes an individual component category page.
    """
    try:
        headers = {'User-Agent': 'Mozilla/5.0'}
        # Politeness delay
        time.sleep(0.5) 
        response = requests.get(url, headers=headers, timeout=15)
        response.raise_for_status()
        html_content = response.text
    except Exception as e:
        print(f"Error fetching {url}: {e}")
        return

    soup = BeautifulSoup(html_content, 'html.parser')
    
    header_tag = soup.find('header')
    if not header_tag:
        print(f"Skipping {url}: No <header> found.")
        return
        
    header_name = header_tag.get_text(strip=True) 
    file_id = clean_id(header_name)

    article = soup.find('article')
    if not article: return
    
    markdown_output = []
    
    # Process all H1 sections in the article
    h1_tags = article.find_all('h1')
    if not h1_tags: return

    # Metadata L1
    markdown_output.append(f"# {header_name} Rules and Notes")
    markdown_output.append(f"* **Document Type:** {header_name} Reference")
    markdown_output.append(f"* **Source:** tirules.com")
    markdown_output.append("\n---\n")

    # Grouping revisions by base name to determine "Current" status
    # This is necessary if a page contains multiple different cards (like the Technology page)
    component_groups = {}
    for h1 in h1_tags:
        title_text = h1.get_text(strip=True)
        base_name = title_text.replace('Ω', '').replace('ω', '').strip()
        if base_name not in component_groups:
            component_groups[base_name] = []
        component_groups[base_name].append(h1)

    for base_name, tags in component_groups.items():
        max_rev = max((t.get_text(strip=True).count('Ω') + t.get_text(strip=True).count('ω')) for t in tags)
        
        for h1 in tags:
            title_text = h1.get_text(strip=True)
            rev_count = title_text.count('Ω') + title_text.count('ω')
            status = "Current" if rev_count == max_rev else "Superseded"
            source = "Codex" if rev_count > 0 else "Base Game"
            
            markdown_output.append(f"## {title_text}")
            markdown_output.append(f"* **Component ID:** {clean_id(header_name)}_{clean_id(base_name)}")
            markdown_output.append(f"* **Revision:** {rev_count}")
            markdown_output.append(f"* **Status:** {status}")
            markdown_output.append(f"* **Source:** {source}")
            markdown_output.append("\n### Clarification Notes")
            
            notes_list = h1.find_next_sibling('ol', class_='note')
            if notes_list:
                for i, li in enumerate(notes_list.find_all('li', recursive=False), 1):
                    markdown_output.append(f"{i}. {li.get_text(strip=True)}")
                    sub_list = li.find('ol')
                    if sub_list:
                        for sub_li in sub_list.find_all('li'):
                            markdown_output.append(f"    * {sub_li.get_text(strip=True)}")
            else:
                markdown_output.append("*(No notes provided)*")
            markdown_output.append("\n---\n")

    # Save: [header_name]_lrr.md
    output_subdir.mkdir(parents=True, exist_ok=True)
    filename = f"{file_id}_lrr.md"
    file_path = output_subdir / filename
    
    with open(file_path, 'w', encoding='utf-8') as f:
        f.write('\n'.join(markdown_output))
    print(f"Saved: {filename}")

def get_component_links(parent_url):
    """
    Finds the specific <ol> following the 'Component Notes' H1.
    """
    try:
        response = requests.get(parent_url, timeout=10)
        soup = BeautifulSoup(response.text, 'html.parser')
        
        # Anchor on the H1
        anchor = soup.find('h1', string=re.compile(r'Component Notes', re.I))
        if not anchor:
            print("Could not find 'Component Notes' header on parent page.")
            return []
            
        ol_list = anchor.find_next_sibling('ol', class_='note')
        links = [urljoin(parent_url, a['href']) for a in ol_list.find_all('a', href=True)]
        return links
    except Exception as e:
        print(f"Error mapping parent page: {e}")
        return []

if __name__ == "__main__":
    print("Starting bulk component scrape...")
    target_links = get_component_links(PARENT_URL)
    
    for link in target_links:
        scrape_component_data(link, OUTPUT_BASE_DIR)
        
    print("Done.")