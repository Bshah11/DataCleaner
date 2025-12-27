import requests
from bs4 import BeautifulSoup, Tag
import os
import re # Added for file name sanitization

# --- Configuration ---
DOMAIN = "https://www.tirules.com"
INDEX_URL = "https://www.tirules.com/" # The home page to scrape for links
SUBDIRECTORY = "structuredData" # Subdirectory for output files
FILE_EXTENSION = ".md" 
# Note: TARGET_URL and OUTPUT_MARKDOWN_FILE are now handled dynamically in main()

def get_html_content(source):
    """
    Reads HTML content from a local file (for mocking/testing) or fetches
    it from a URL (for a live web scraper).
    """
    # Check if the source is a URL (starts with http)
    if source.startswith('http'):
        # In a multi-threaded or production scraper, implement exponential backoff here.
        # For simplicity in this single script, we rely on the requests module's reliability.
        print(f"Fetching HTML content from URL: {source}")
        try:
            # Setting a user-agent helps prevent some sites from blocking the request
            headers = {
                'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36'
            }
            response = requests.get(source, headers=headers, timeout=10)
            response.raise_for_status() # Raise an HTTPError for bad responses (4xx or 5xx)
            return response.text
        except requests.exceptions.Timeout:
            print(f"Error: Request to {source} timed out after 10 seconds.")
            return None
        except requests.exceptions.RequestException as e:
            print(f"Error fetching URL: {e}")
            return None
    # Fallback/Test: Check if the source is a local file path
    elif os.path.exists(source):
        print(f"Reading HTML content from local file: {source}")
        with open(source, 'r', encoding='utf-8') as f:
            return f.read()
    else:
        print(f"Error: Source '{source}' not recognized as a valid URL or local file.")
        return None

def get_rule_links(index_url, domain):
    """
    Fetches the index page and extracts all rule links from ol.lrr.
    """
    print(f"Fetching index page from: {index_url}")
    index_html = get_html_content(index_url)
    if not index_html:
        return []

    soup = BeautifulSoup(index_html, 'html.parser')
    link_list = soup.find('ol', class_='lrr')
    
    if not link_list:
        print("Error: Could not find the main rule link list (<ol class='lrr'>) on the index page.")
        return []

    links = []
    for li in link_list.find_all('li', recursive=False):
        a_tag = li.find('a', href=True)
        if a_tag:
            relative_path = a_tag['href']
            full_url = domain + relative_path
            links.append(full_url)
    
    return links

def convert_list_to_markdown(list_tag: Tag, md_type: str = 'numbered', depth: int = 0):
    """
    Recursively converts <ol> or <ul> tags into Markdown lists.
    Handles nested lists correctly by increasing the depth for indentation.
    """
    markdown_content = []
    list_item_count = 1 

    # Look for direct <li> children
    for li in list_tag.find_all('li', recursive=False):
        
        li_text_parts = []
        nested_list_tag = None
        
        # 1. Extract only the content BEFORE the nested list
        for content in li.contents:
            if isinstance(content, Tag) and content.name in ['ol', 'ul']:
                # Found the nested list, stop processing text here
                nested_list_tag = content
                break 
            
            if isinstance(content, str):
                li_text_parts.append(content.strip())
            elif isinstance(content, Tag):
                # Handle other inline tags (like <b>, <i>, <sc>)
                li_text_parts.append(content.get_text().strip())
        
        # Join the text parts, ensuring no excessive whitespace
        li_text = ' '.join(filter(None, li_text_parts))
        
        # 2. Determine prefix and add the main line
        # Use 4 spaces for indentation per level
        indent = '    ' * depth
        prefix = ''

        if md_type == 'numbered':
            prefix = f"{indent}{list_item_count}. "
            list_item_count += 1
        elif md_type == 'bullet':
            prefix = f"{indent}- "
        
        # Add the main list item line
        if li_text:
             markdown_content.append(f"{prefix}{li_text}")
        
        # 3. Handle nested lists (Recursion)
        if nested_list_tag:
            nested_md_type = 'numbered' if nested_list_tag.name == 'ol' else 'bullet'
            
            # Recursively call the function with increased depth
            nested_md = convert_list_to_markdown(nested_list_tag, nested_md_type, depth + 1)
            # Add an extra blank line before the nested content for cleaner Markdown structure
            markdown_content.append(f"\n{nested_md}")
    
    # Filter out any resulting blank lines and join
    return "\n".join(filter(None, markdown_content))

def convert_html_to_markdown(html_content: str) -> tuple[str, str]:
    """
    Converts the specific HTML structure to the target Markdown format.
    Returns the markdown content and the extracted rule topic name.
    """
    if not html_content:
        return "Could not retrieve HTML content.", "Error"

    soup = BeautifulSoup(html_content, 'html.parser')
    markdown_parts = []

    # 1. Extract Rule Topic (for header and filename)
    rule_topic_tag = soup.find('header')
    if rule_topic_tag:
        rule_topic = rule_topic_tag.text.strip()
    else:
        # Fallback to the first <h1> if <header> is missing
        rule_topic = soup.find('h1').text.strip() if soup.find('h1') else "Default Rule Topic"

    markdown_parts.append(f"# {rule_topic}")

    # Find the main article content container
    article = soup.find('article')
    if not article:
        return "Error: Could not find the <article> container.", rule_topic

    # 2. Extract Specific Rule - [rule topic description]
    rule_h1 = article.find('h1', string=lambda t: t and 'rules reference' in t.lower())
    rule_description = ""
    
    if rule_h1:
        # Use find_next('p') to ignore intermediate tags like <style>
        rule_description_p = rule_h1.find_next('p')
        if rule_description_p:
            rule_description = rule_description_p.text.strip()
    
    markdown_parts.append(f"## Specific rule - [{rule_description}]")

    # 3. Extract Rule points from ol.lrr
    markdown_parts.append(f"### Rule points")
    lrr_list = article.find('ol', class_='lrr')
    
    if lrr_list:
        rule_item_count = 1
        
        # Iterate over all direct children to catch <h2>, <p>, <li>, AND sibling <ol>
        for child in lrr_list.find_all(recursive=False):
            if not isinstance(child, Tag):
                continue

            li_tag = None
            is_subheading = False
            
            # Case 1: Subheading (h2 containing a li)
            if child.name == 'h2':
                li_tag = child.find('li', recursive=False)
                is_subheading = True
            # Case 2: Standard list item (li)
            elif child.name == 'li':
                li_tag = child
            # Case 3: Paragraph inside the list
            elif child.name == 'p':
                 markdown_parts.append(f"\n> {child.text.strip()}\n")
                 continue
            # Case 4: Sibling Ordered List (<ol>) without a class (the missed sub-rule list)
            elif child.name == 'ol' and not child.get('class'):
                nested_md = convert_list_to_markdown(child, md_type='numbered', depth=1)
                markdown_parts.append(f"\n{nested_md}")
                continue
            
            if not li_tag:
                continue

            # --- Text Extraction from li_tag ---
            li_text_parts = []
            nested_list_tag_child = li_tag.find(['ol', 'ul'], recursive=False)
            
            for content in li_tag.contents:
                if content is nested_list_tag_child:
                    break # Stop at the nested list
                
                if isinstance(content, str):
                    li_text_parts.append(content.strip())
                elif isinstance(content, Tag):
                    li_text_parts.append(content.get_text().strip())
            
            li_text = ' '.join(filter(None, li_text_parts))

            if not li_text:
                continue
            
            if is_subheading:
                markdown_parts.append(f"\n#### {li_text}")
            else:
                markdown_parts.append(f"{rule_item_count}. {li_text}")
                rule_item_count += 1
                
                # Handle nested list/sub-rules (Recursion) for child lists
                if nested_list_tag_child:
                    nested_md = convert_list_to_markdown(nested_list_tag_child, md_type='numbered', depth=1)
                    markdown_parts.append(f"\n{nested_md}") 
    else:
        markdown_parts.append("1. No rule points found.")


    # 4. Extract Notes from ol.notes
    markdown_parts.append(f"\n### Notes")
    notes_list = article.find('ol', class_=['notes', 'note'])
    
    if notes_list:
        # Iterate over all direct children, to catch <li> and sibling <ol>
        for child in notes_list.find_all(recursive=False):
            if not isinstance(child, Tag):
                continue
            
            # Case 1: Standard list item (li)
            if child.name == 'li':
                li_tag = child
                
                # --- Text Extraction from li_tag ---
                li_text_parts = []
                nested_list_tag_child = li_tag.find(['ol', 'ul'], recursive=False)
                
                for content in li_tag.contents:
                    if content is nested_list_tag_child:
                        break # Stop at the nested list
                    
                    if isinstance(content, str):
                        li_text_parts.append(content.strip())
                    elif isinstance(content, Tag):
                        li_text_parts.append(content.get_text().strip())
                
                li_text = ' '.join(filter(None, li_text_parts))

                if li_text:
                    markdown_parts.append(f"- {li_text}") 
                
                # Handle nested list/sub-notes (Recursion) for child lists
                if nested_list_tag_child:
                    nested_md = convert_list_to_markdown(nested_list_tag_child, md_type='bullet', depth=1)
                    markdown_parts.append(f"\n{nested_md}")
            
            # Case 2: Sibling Ordered List (<ol>) without a class (the missed sub-note list)
            elif child.name == 'ol' and not child.get('class'):
                nested_md = convert_list_to_markdown(child, md_type='bullet', depth=1)
                markdown_parts.append(f"\n{nested_md}")
            
    else:
        markdown_parts.append("- No notes found.")

    # 5. Extract Related Topics from ul
    markdown_parts.append(f"\n### related topic")
    related_h1 = article.find('h1', string=lambda t: t and 'related topics' in t.lower())
    if related_h1 and related_h1.find_next_sibling('ul'):
        related_ul = related_h1.find_next_sibling('ul')
        
        related_topics_md = []
        for li in related_ul.find_all('li'):
            topic_text = li.text.strip()
            related_topics_md.append(f"- {topic_text}")
        
        markdown_parts.append("\n".join(related_topics_md))
    else:
        markdown_parts.append("- No related topics found.")


    return "\n".join(markdown_parts), rule_topic

def main():
    # 0. Setup paths
    output_dir = SUBDIRECTORY
    os.makedirs(output_dir, exist_ok=True)
    
    # 1. Get Links from the index page
    rule_urls = get_rule_links(INDEX_URL, DOMAIN)
    
    if not rule_urls:
        print("No rule links found. Exiting.")
        return

    # 2. Loop through all links
    print(f"\nFound {len(rule_urls)} rule topics. Starting scraping process...")
    
    for i, url in enumerate(rule_urls):
        print(f"\n[{i+1}/{len(rule_urls)}] Processing: {url}")
        
        # 2a. Fetch HTML
        html_content = get_html_content(url)
        
        if not html_content:
            print(f"Skipping {url} due to fetch error.")
            continue
        
        # 2b. Convert to MD and get Topic Name
        markdown_output, rule_topic = convert_html_to_markdown(html_content)
        
        # Sanitize rule_topic for use as filename: replace characters that are unsafe/illegal
        # Example: 'Technology (S.C.)' -> 'Technology_SC'
        sanitized_topic = re.sub(r'[^\w\s-]', '', rule_topic).replace(' ', '_').strip()
        
        if not sanitized_topic:
             # Fallback if topic name is empty after sanitization
             sanitized_topic = f"topic_{i}"

        # 2c. Save to file
        filename = f"{sanitized_topic}{FILE_EXTENSION}"
        output_path = os.path.join(output_dir, filename)
        
        try:
            with open(output_path, 'w', encoding='utf-8') as f:
                f.write(markdown_output)
            print(f"SUCCESS: Saved to {output_path}")
        except Exception as e:
            print(f"ERROR: Could not save file {output_path}. Error: {e}")

    print("\n\n--- Multi-Page Scraping Complete ---")


if __name__ == "__main__":
    # Ensure BeautifulSoup and Requests are installed: pip install beautifulsoup4 requests
    main()