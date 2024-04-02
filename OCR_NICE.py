import pdfplumber
import re



def find_toc_start_page(pdf):
    """
    Find the page number where the Table of Contents starts.
    """
    for i, page in enumerate(pdf.pages):
        text = page.extract_text(x_tolerance=3, y_tolerance=3)
        if text:
            # Assuming the ToC starts with "Content" or "Table of Contents" at the beginning of the page
            if text.strip().startswith(("Content", "Table of Contents")):
                return i  # Return the page index where ToC is found
    return None  # Return None if ToC is not found

def clean_toc_entry(toc_entry):
    # Remove trailing dots and page number, keeping only the title
    return re.sub(r'\.{2,}\s*$', '', toc_entry).strip()

def parse_toc(pdf, toc_start_page_index):
    """
    Parse the Table of Contents to extract section titles.
    """
    toc_text = pdf.pages[toc_start_page_index].extract_text(x_tolerance=3, y_tolerance=3)
    toc_entries = []
    # Adjust the pattern if your section titles have a different format
    pattern = re.compile(r'(B\.\d+\.?\s+)([^.]+)')
    for match in re.finditer(pattern, toc_text):
        section = match.group(1).strip()
        title = match.group(2).strip().replace('\n',' ')
        # Combine the section and title for the full header
        full_title = f"{section} {title}"
        cleaned_title = clean_toc_entry(full_title)
        toc_entries.append(cleaned_title)
    return toc_entries[:3]


def find_section_start_page(pdf, section_title):
    """
    Find the start page of a section given its title.
    """
    for i, page in enumerate(pdf.pages):
        text = page.extract_text(x_tolerance=3, y_tolerance=3)
        text=text.replace("\n"," ").lower()
        if text:
            if text.strip().startswith((section_title)):
                return i
    return None

def is_word_in_tables(word, tables):
    """
    Check if the word's bounding box overlaps with any of the tables.
    """
    for table in tables:
        # Get the bounding box of the table
        table_bbox = table.bbox
        # Check if the word is within the bounding box of the table
        if word['x0'] >= table_bbox[0] and word['x1'] <= table_bbox[2] \
                and word['top'] >= table_bbox[1] and word['bottom'] <= table_bbox[3]:
            return True
    return False

def extract_text_ignore_tables(page):
    """
    Extract text from the page and ignore text that is part of a table.
    """
    words = page.extract_words()
    tables = page.find_tables()
    text = ' '.join(word['text'] for word in words if not is_word_in_tables(word, tables))
    footer_pattern = re.compile(
        r'\s*All rights reserved Page \d+ of \d+\s*|\©\s+Britannia\s+.*?\)', re.IGNORECASE)

    text_without_footer = re.sub(footer_pattern, '', text)

    return text_without_footer


import os
path_pdf='./committee_papers'
list_of_papers=os.listdir(path_pdf)
#pdf_path = "/Users/ricky/Downloads/committee-papers.pdf"
sections_contents=[]
for list_of_paper in list_of_papers[:10]:
    pdf_path=f'''{path_pdf}/{list_of_paper}'''

    ID=pdf_path.split("_")[-1].split(".")[0]
    print(pdf_path,ID)
    with pdfplumber.open(pdf_path) as pdf:
        toc_start_page_index = find_toc_start_page(pdf)
        if toc_start_page_index is not None:
            toc_entries = parse_toc(pdf, toc_start_page_index)
            sections_content = []
            # toc_entries=[i for i in toc_entries if len(i.split(" ")[0].split("."))==2]
            for i, title in enumerate(toc_entries):
                start_page_index = find_section_start_page(pdf, title.lower())
                if start_page_index is not None:
                    # Assuming each section ends when the next one starts, except for the last section.
                    end_page_index = (find_section_start_page(pdf, toc_entries[i + 1].lower())
                                      if i + 1 < len(toc_entries)
                                      else len(pdf.pages))
                    section_pages = [extract_text_ignore_tables(pdf.pages[j]) for j in
                                     range(start_page_index, end_page_index)]
                    section_text = " ".join(filter(None, section_pages)).strip()
                    sections_content.append([ID,title, section_text])
                else:
                    print(f"Could not find the start page for section '{title}'.")
            sections_contents.append(sections_content)
        else:
            print("Table of Contents not found.")

section_content_list=[]

for section_content in sections_contents:
    if len(section_content)==3:
        section_content_list.append([section_content[0][0],section_content[0][2],section_content[1][2],section_content[2][2]])
    elif len(section_content)==2:
        section_content_list.append([section_content[0][0],section_content[0][2], section_content[1][2], ''])
import pandas as pd

df_sections=pd.DataFrame(section_content_list,columns=['ID','Intro','Clinical','Cost'])

df_sections.to_csv('sections_tmp.csv',sep='\t')