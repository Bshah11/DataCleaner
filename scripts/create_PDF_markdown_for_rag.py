import os
import re
from typing import List, Dict
import pdfplumber

# --- Configuration ---
SUBDIRECTORY = "structuredData"

# The core pattern for TI4 rules: [Number.Number Optional dot] [Space] [Title]
HEADING_PATTERN = re.compile(r'(\n\s*\d+\.\d+\.?\s+[A-Z][a-zA-Z\s,;]+)\n', re.DOTALL)

def clean_text(text: str) -> str:
    """
    Cleans up raw PDF text, removing excess newlines, common artifacts, and spacing.
    """
    if not isinstance(text, str):
        return ""
    
    # 1. Normalize spacing: replace newlines, tabs, and multiple spaces with a single space
    text = re.sub(r'\s*\n\s*', ' ', text)
    text = re.sub(r'\s{2,}', ' ', text)
    
    # 2. Remove common PDF artifacts (page numbers, document titles)
    text = re.sub(r'Page\s+\d+\s+of\s+\d+', '', text)
    text = re.sub(r'Twilight Imperium[:]? Quatrième Edition Rules Reference', '', text, flags=re.IGNORECASE)
    text = re.sub(r'Living Rules Reference Version \d+\.\d+\s*', '', text)
    
    return text.strip()

def extract_text_from_pdf(pdf_path: str) -> str:
    """Uses pdfplumber to extract text from all pages of the PDF."""
    print(f"-> ATTEMPTING EXTRACTION from PATH: {pdf_path}")
    
    full_text = ""
    try:
        with pdfplumber.open(pdf_path) as pdf:
            # Extract text page by page, separated by a distinct newline for later regex
            for page in pdf.pages:
                full_text += page.extract_text() + "\n\n"
        
        print("-> EXTRACTION SUCCESSFUL.")
        return full_text
        
    except FileNotFoundError:
        # **Enhanced Error Reporting**
        print("!! ERROR: FILE NOT FOUND !!")
        print(f"!! Please verify the path: {pdf_path} is correct.")
        return ""
    except Exception as e:
        print(f"!! FATAL EXTRACTION ERROR: {e}")
        return ""


def semantic_chunking(full_text: str, source_name: str) -> List[Dict[str, str]]:
    """
    Splits the document based on numerical headings (e.g., 75.0, 75.5) 
    to create semantically coherent rule chunks.
    """
    chunks = []
    
    # Ensure text is cleaned up before splitting, primarily ensuring clean newlines around headings
    text = full_text.replace('\r', '\n')
    
    # 1. Split the text using the heading pattern
    segments = HEADING_PATTERN.split(text)
    
    # 2. Process the preamble (un-numbered intro text)
    if segments[0].strip():
        chunks.append({
            "RULE_SOURCE": source_name,
            "SECTION_ID": "Preamble/Introduction",
            "CONTENT": clean_text(segments[0])
        })
    
    # 3. Process the segments in pairs (heading + content)
    for i in range(1, len(segments), 2):
        heading_text = segments[i].strip()
        content_text = segments[i+1]

        if not heading_text or not content_text.strip():
            continue
            
        chunks.append({
            "RULE_SOURCE": source_name,
            "SECTION_ID": heading_text,
            "CONTENT": clean_text(content_text)
        })

    print(f"-> Created {len(chunks)} semantic rule sections.")
    return chunks

# ... (generate_rules_markdown, write_to_file remain the same) ...

def generate_rules_markdown(chunks: List[Dict[str, str]]) -> str:
    """Generates the final RAG markdown format for unstructured rules."""
    
    # The title will be dynamically set by the file name
    markdown_output = f"## 📚 Unstructured Rules Data: {RULE_BOOK_TITLE}\n\n"
    
    for chunk in chunks:
        markdown_output += "##################################################\n\n"
        # We use the dynamic source name (derived from file name)
        markdown_output += f"### RULE_SOURCE: {chunk['RULE_SOURCE']}\n" 
        # The section is the numerical heading (e.g., 75.0 SPACE COMBAT)
        markdown_output += f"--- SECTION_ID: {chunk['SECTION_ID']}\n"
        # The content is the actual rule text
        markdown_output += f"--- CONTENT: {chunk['CONTENT']}\n"
        
    return markdown_output

def write_to_file(filename: str, content: str, subdirectory: str):
    """Creates the subdirectory if it doesn't exist and writes the content to the file."""
    try:
        os.makedirs(subdirectory, exist_ok=True)
        file_path = os.path.join(subdirectory, filename)
        with open(file_path, 'w', encoding='utf-8') as f:
            f.write(content)
        print(f"Successfully wrote RAG markdown to: {file_path}")
    except Exception as e:
        print(f"Error writing file {file_path}: {e}")

# --- Universal Execution Function ---

def process_rulebook(input_pdf_name: str, output_md_name: str, pdf_dir: str = "unstructuredData"):
    """
    Consumes a single rules PDF, chunks it semantically, and writes the RAG markdown file.
    """
    global RULE_BOOK_TITLE
    
    pdf_path = os.path.join(pdf_dir, input_pdf_name)
    
    # Use a descriptive title derived from the PDF name for better RAG context
    RULE_BOOK_TITLE = input_pdf_name.upper().replace(".PDF", "").replace("_", " ")

    # STEP 1: Extract Text
    full_rules_text = extract_text_from_pdf(pdf_path)
    
    if not full_rules_text:
        print(f"Skipping processing for {input_pdf_name}.")
        return

    # STEP 2: Chunk and Structure
    structured_chunks = semantic_chunking(full_rules_text, RULE_BOOK_TITLE)
    
    if not structured_chunks:
         print(f"Warning: No structural headings found in {input_pdf_name}. File might be purely lore or require manual review.")

    # STEP 3: Generate Markdown
    rules_markdown_output = generate_rules_markdown(structured_chunks)
    
    # STEP 4: Write to File
    write_to_file(output_md_name, rules_markdown_output, subdirectory=SUBDIRECTORY)

# --- Main Execution Block ---

if __name__ == '__main__':
    print("--- Starting Universal TI4 Rules Processor ---")
    
    # Fix 1: Base Rules PDF (Using RawData as the source directory)
    process_rulebook(
        input_pdf_name="ti10_rulebook_web-good.pdf",
        output_md_name="base_rules_RAG.md",
        pdf_dir="RawData" # <--- FIXED: Pointing to the directory confirmed by 'ls'
    )
    
    print("--- Universal Processing Complete ---")