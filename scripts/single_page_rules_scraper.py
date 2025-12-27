import requests
from bs4 import BeautifulSoup, Tag
import os

# --- Configuration ---
# IMPORTANT: Replace this placeholder with the actual URL of the PHP page you want to scrape.
# The script will now attempt to fetch content from this URL.
TARGET_URL = "https://www.tirules.com/R_action_cards" # Placeholder URL - UPDATE THIS
SUBDIRECTORY = "structuredData" # New subdirectory for output files
OUTPUT_MARKDOWN_FILE = "output.md"

def get_html_content(source):
    """
    Reads HTML content from a local file (for mocking/testing) or fetches
    it from a URL (for a live web scraper).
    """
    # Check if the source is a URL (starts with http)
    if source.startswith('http'):
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

def convert_list_to_markdown(list_tag: Tag, md_type: str = 'numbered', depth: int = 0):
    """
    Recursively converts <ol> or <ul> tags into Markdown lists.
    Handles nested lists correctly by increasing the depth for indentation.

    :param list_tag: The BeautifulSoup Tag object (<ol> or <ul>).
    :param md_type: 'numbered' for <ol> (uses 1., 2., 3., etc.) or 'bullet' for <ul> (uses -).
    :param depth: Current nesting level (used for indentation).
    :return: Formatted Markdown string for the list.
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
        # Use 4 spaces for indentation per level for better visibility/compatibility
        indent = '    ' * depth
        prefix = ''

        if md_type == 'numbered':
            # Numbered lists reset count per level implicitly in Markdown
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

def convert_html_to_markdown(html_content: str) -> str:
    """
    Converts the specific HTML structure to the target Markdown format.
    """
    if not html_content:
        return "Could not retrieve HTML content."

    soup = BeautifulSoup(html_content, 'html.parser')
    markdown_parts = []

    # 1. Extract Rule Topic
    rule_topic_tag = soup.find('header')
    if rule_topic_tag:
        rule_topic = rule_topic_tag.text.strip()
    else:
        rule_topic = soup.find('h1').text.strip() if soup.find('h1') else "Default Rule Topic"

    markdown_parts.append(f"# {rule_topic}")

    # Find the main article content container
    article = soup.find('article')
    if not article:
        return "Error: Could not find the <article> container."

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
        
        # Iterate over all direct children, not just <li>, to catch <h2>, <p>, <li>, AND sibling <ol>
        for child in lrr_list.find_all(recursive=False):
            if not isinstance(child, Tag):
                continue

            li_tag = None
            is_subheading = False
            
            # Case 1: Subheading (h2 containing a li, e.g., <h2><li>Costs</li></h2>)
            if child.name == 'h2':
                li_tag = child.find('li', recursive=False)
                is_subheading = True
            # Case 2: Standard list item (li)
            elif child.name == 'li':
                li_tag = child
            # Case 3: Paragraph inside the list (like "To resolve movement, players perform...")
            elif child.name == 'p':
                 # Format as a blockquote for context, and continue to the next child
                 markdown_parts.append(f"\n> {child.text.strip()}\n")
                 continue
            # Case 4: Sibling Ordered List (<ol>) without a class (the missed sub-rule list)
            elif child.name == 'ol' and not child.get('class'):
                # Treat this as a continuation of the LRR points list, 
                # but nested under the *last* rule point generated.
                # Since the previous child was a rule item, we process this as a nested list
                nested_md = convert_list_to_markdown(child, md_type='numbered', depth=1)
                markdown_parts.append(f"\n{nested_md}")
                continue # Skip to the next sibling, as this list is processed
            
            if not li_tag:
                continue

            # --- Text Extraction from li_tag ---
            li_text_parts = []
            # Check for a nested list that is a CHILD of the li (handled by recursion in convert_list_to_markdown)
            nested_list_tag_child = li_tag.find(['ol', 'ul'], recursive=False)
            
            for content in li_tag.contents:
                if content is nested_list_tag_child:
                    break # Stop at the nested list
                
                if isinstance(content, str):
                    li_text_parts.append(content.strip())
                elif isinstance(content, Tag):
                    # Handle inline tags (like <b>, <i>, <sc>)
                    li_text_parts.append(content.get_text().strip())
            
            li_text = ' '.join(filter(None, li_text_parts))

            if not li_text:
                continue
            
            if is_subheading:
                # Format as a subheading
                markdown_parts.append(f"\n#### {li_text}")
            else:
                # Format as a rule point
                markdown_parts.append(f"{rule_item_count}. {li_text}")
                rule_item_count += 1
                
                # Handle nested list/sub-rules (Recursion) for child lists
                if nested_list_tag_child:
                    # depth=1 for the first level of indentation
                    nested_md = convert_list_to_markdown(nested_list_tag_child, md_type='numbered', depth=1)
                    markdown_parts.append(f"\n{nested_md}") # Add a break before nested list
    else:
        markdown_parts.append("1. No rule points found.")


    # 4. Extract Notes from ol.notes
    markdown_parts.append(f"\n### Notes")
    # Search for both 'notes' and 'note' classes
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
                # Check for a nested list that is a CHILD of the li 
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
                    markdown_parts.append(f"- {li_text}") # Note: Using '-' prefix, no indentation yet
                
                # Handle nested list/sub-notes (Recursion) for child lists
                if nested_list_tag_child:
                    # depth=1 for the first level of indentation
                    nested_md = convert_list_to_markdown(nested_list_tag_child, md_type='bullet', depth=1)
                    markdown_parts.append(f"\n{nested_md}")
            
            # Case 2: Sibling Ordered List (<ol>) without a class (the missed sub-note list)
            elif child.name == 'ol' and not child.get('class'):
                # Treat this as a continuation of the notes list, nested under the *last* note point.
                # depth=1 for the first level of indentation
                nested_md = convert_list_to_markdown(child, md_type='bullet', depth=1)
                markdown_parts.append(f"\n{nested_md}")
            
            # Ignore other tags (like style, script, comments)
            
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


    return "\n".join(markdown_parts)

def main():
    # Attempt to fetch content from the TARGET_URL
    html_content = get_html_content(TARGET_URL)
    
    if html_content:
        markdown_output = convert_html_to_markdown(html_content)
        
        # Construct the full output path
        output_dir = SUBDIRECTORY
        output_path = os.path.join(output_dir, OUTPUT_MARKDOWN_FILE)
        
        # Create the output directory if it doesn't exist (recursive creation)
        os.makedirs(output_dir, exist_ok=True)
        
        # Save the Markdown output
        with open(output_path, 'w', encoding='utf-8') as f:
            f.write(markdown_output)
        
        print(f"\nSuccessfully generated Markdown file: {output_path}")
        print("\n--- Generated Markdown Content ---")
        print(markdown_output)
        print("----------------------------------")
    else:
        print("\nScraping failed. Please check the TARGET_URL and ensure the page is accessible.")


if __name__ == "__main__":
    # Ensure BeautifulSoup and Requests are installed: pip install beautifulsoup4 requests
    main()