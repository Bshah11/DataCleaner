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
