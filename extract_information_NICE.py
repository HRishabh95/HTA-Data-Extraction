# Importing necessary libraries
import requests  # For making HTTP requests to fetch web content
from bs4 import BeautifulSoup  # For parsing HTML content
import os  # For interacting with the operating system, like creating directories
import pandas as pd  # For handling data in DataFrame structures
import re  # For regular expressions, used here for parsing text
from sentence_transformers import SentenceTransformer, util  # For text classification using pre-trained models
import torch  # For tensor operations, used with SentenceTransformer

# Load the pre-trained SentenceTransformer model
model = SentenceTransformer('sentence-transformers/all-MiniLM-L6-v2')

def get_url_data(extension):
    """
    Fetches the HTML content from a given URL extension on the NICE website.
    """
    url = f'''https://www.nice.org.uk{extension}'''

    headers = {
        'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/58.0.3029.110 Safari/537.3',
        'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,image/webp,*/*;q=0.8',
        'Accept-Language': 'en-US,en;q=0.5',
        'DNT': '1',  # Do Not Track Request Header
        'Connection': 'keep-alive'
    }

    # Make the GET request with the specified headers
    response = requests.get(url, headers=headers)
    if response.status_code == 200:
        return response.text
    else:
        return None

def get_guidance_menu_links(soup):
    """
    Extracts links from the guidance menu on the NICE website.
    """
    guidance_menu = soup.find('nav', class_='stacked-nav')
    final_links = []
    if guidance_menu:
        links = guidance_menu.find_all('a')
        for link in links[1:]:
            final_links.append([link.get_text(strip=True), link.get('href')])
        return final_links
    else:
        return []

def classify_nice_guidance(text):
    """
    Classifies NICE guidance into categories based on the presence of key phrases in the text.
    """
    if 'cancer drugs fund' in text.lower():
        CDF = True
    else:
        CDF = False
    if "is not recommended" in text:
        return "Not Recommended", CDF
    elif "recommended as an option for" in text and "only if" in text:
        return "Optimised", CDF
    elif "recommended, within its marketing authorisation" in text or "recommended" in text:
        return "Recommended", CDF
    else:
        return "Uncategorized", CDF

def classify_nice_guidance_dynamic(text):
    """
    Dynamically classifies NICE guidance using SentenceTransformer to find the closest matching category.
    """
    # Predefined category descriptions
    categories = {
        "Recommended": "recommended within its marketing authorisation.",
        "Optimised": "recommended with specific conditions.",
    }

    # Embed the input text and category descriptions
    text_embedding = model.encode(text, convert_to_tensor=True)
    category_embeddings = model.encode(list(categories.values()), convert_to_tensor=True)

    if 'cancer drugs fund' in text.lower():
        CDF = True
    else:
        CDF = False

    # Compute cosine similarities and find the highest similarity
    cosine_scores = util.pytorch_cos_sim(text_embedding, category_embeddings)
    highest_score_index = torch.argmax(cosine_scores).item()
    category = list(categories.keys())[highest_score_index]

    return category, CDF

def get_recommendation_reason(div_soup):
    """
    Extracts the recommendation text and reasons from the given HTML content.
    """
    reason_text = ''
    recommendation_text = ''
    recommendation_cat = ''
    CDF = False
    if div_soup.find('div'):
        recommendation_text = div_soup.find('div').get_text(strip=True)
        recommendation_cat, CDF = classify_nice_guidance(recommendation_text)
        strong_tag = div_soup.find('strong', string="Why the committee made these recommendations")
        if strong_tag:
            for next_p in strong_tag.find_all_next('p'):
                reason_text += next_p.get_text(strip=True) + " "
        return recommendation_text, recommendation_cat, CDF, reason_text
    else:
        return recommendation_text, recommendation_cat, CDF, reason_text

def extract_size(size_str):
    """
    Extracts the numerical value from a size string (e.g., "15 MB") and converts it to MB.
    """
    match = re.search(r'(\d+(\.\d+)?)\s*(MB|KB)', size_str, re.I)
    if match:
        size = float(match.group(1))
        unit = match.group(3).upper()
        if unit == 'KB':
            size = size / 1024  # Convert KB to MB
        return size
    return 0

def get_eol_sm(url):
    """
    Checks if the terms 'end of life' and 'severity' appear on the given webpage.
    """
    response = requests.get(url)
    end_of_life = False
    severity = False
    if response.status_code == 200:
        soup = BeautifulSoup(response.text, 'html.parser')
        soup_text = soup.get_text()
        if 'end of life' in soup_text.lower():
            end_of_life = True
        if 'severity' in soup_text.lower():
            severity = True
    return end_of_life, severity

def download_committee_papers(url, download_folder):
    """
    Downloads the largest committee paper from the given URL and saves it to the specified folder.
    """
    # Ensure the download folder exists
    if not os.path.exists(download_folder):
        os.makedirs(download_folder)

    # Fetch the HTML content
    response = requests.get(url)
    if response.status_code != 200:
        print("Failed to retrieve webpage")
        return None
    soup = BeautifulSoup(response.content, 'html.parser')

    # Find all links that include "Committee papers" in their text
    committee_papers_elements = soup.find_all('a', string=lambda text: text and 'Committee papers' in text.replace(u'\xa0', u' '))
    largest_file = None
    largest_size = 0
    if committee_papers_elements:
        for link in committee_papers_elements:
            size_text = link.get_text()
            if size_text:
                size = extract_size(size_text)
                if size > largest_size:
                    largest_size = size
                    largest_file = link['href']

        if largest_file:
            if not largest_file.startswith('http'):
                largest_file = requests.compat.urljoin('https://www.nice.org.uk', largest_file)

            pdf_response = requests.get(largest_file)
            if pdf_response.status_code == 200:
                filename = f'''{largest_file.split('/')[-1]}_{largest_file.split("/")[-3]}.pdf'''
                file_path = os.path.join(download_folder, filename)
                if not os.path.isfile(file_path):
                    with open(file_path, 'wb') as f:
                        f.write(pdf_response.content)
                    print(f"Downloaded the largest Committee paper: {file_path}")
                else:
                    print(f'file already exists')
                return file_path

    print("No Committee papers found or failed to download.")
    return None

def get_information_medicine(div_soup):
    """
    Extracts marketing authorisation, dosage, and price information from the given HTML content.
    """
    authorisation = ''
    dosage = ''
    price = ''
    if div_soup.find('div', title='Marketing authorisation indication'):
        authorisation = div_soup.find('div', title='Marketing authorisation indication').find('p').get_text(strip=True)
    if div_soup.find('div', title='Dosage in the marketing authorisation'):
        dosage = div_soup.find('div', title='Dosage in the marketing authorisation').find('p').get_text(strip=True)
    if div_soup.find('div', title='Price'):
        price = div_soup.find('div', title='Price').find('p').get_text(strip=True)

    return authorisation, dosage, price

# Read the CSV file containing NICE guidance data
TAR = pd.read_csv('evidence_NICE_lists.csv', sep=',')

final_csv = []

# Iterate through each row in the CSV file
for row in TAR.iterrows():
    title = row[1]['Title']
    TAnumber = row[1]['TA Number']
    print(TAnumber)
    extension = f'''/{"/".join(row[1]['Link'].split("/")[-2:])}'''
    authorization, dosage, price = '', '', ''
    html_content = get_url_data(extension)
    if 'terminated' in title:
        recommendation, reason = 'Terminated', ''
        recommendation_cat = 'Terminated'
    else:
        recommendation, reason = 'Not Recommended', ''
        recommendation_cat = 'Not Recommended'
    CDF = False
    end_of_life = False
    severity_modifiers = False

    # Parse the HTML content
    soup = BeautifulSoup(html_content, 'html.parser')
    guidance_menus = get_guidance_menu_links(soup)

    url = f'''{row[1]['Link']}/history/'''
    file_path = download_committee_papers(url, './committee_papers')

    url = f'''{row[1]['Link']}/chapter/3-Committee-discussion'''
    end_of_life, severity_modifiers = get_eol_sm(url)

    for guidance_menu_lists in guidance_menus[:2]:
        guidance_menu_list = guidance_menu_lists[1]
        make_id = f'''{guidance_menu_list.split("/")[2]}-{guidance_menu_list.split("/")[4].lower()}'''
        soup = BeautifulSoup(get_url_data(guidance_menu_list), 'html.parser')
        if soup.find('div', id=make_id):
            div_soup = soup.find('div', id=make_id)
        else:
            div_soup = soup.find('div', title=guidance_menu_lists[0])
        # Find the recommendation and reason sections
        if "recommendation" in make_id:
            recommendation, recommendation_cat, CDF, reason = get_recommendation_reason(div_soup)
        if 'information-about' in make_id:
            authorization, dosage, price = get_information_medicine(div_soup)

    final_csv.append([TAnumber, title, recommendation, recommendation_cat, CDF, reason, authorization, dosage, price,
                      end_of_life, severity_modifiers, file_path])

# Create a DataFrame from the collected data and save it to a TSV file
dd = pd.DataFrame(final_csv)
dd.columns = ['TA_Number', 'Indication', 'Outcome', 'Category', 'CDF', 'Reasons', 'Initial Authorization',
              'Dosage', 'Price', 'EoL', 'Severity Modifiers', 'committee_file_path']
dd.to_csv('Recommendations_NICE_papers.tsv', sep='\t', index=False)
