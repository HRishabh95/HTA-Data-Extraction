# Importing necessary libraries
import requests  # For making HTTP requests to fetch web content
from bs4 import BeautifulSoup  # For parsing HTML content
import re  # For regular expressions (though not used in this specific code)
import pandas as pd  # For handling data in DataFrame structures


def get_url_data(url):
    """
    Fetches the HTML content from a given URL with specified headers.

    Parameters:
        url (str): The URL to fetch the HTML content from.

    Returns:
        str: The HTML content of the page.
    """
    headers = {
        'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/58.0.3029.110 Safari/537.3',
        'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,image/webp,*/*;q=0.8',
        'Accept-Language': 'en-US,en;q=0.5',
        'DNT': '1',  # Do Not Track Request Header
        'Connection': 'keep-alive'
    }

    # Make the GET request with the specified headers
    response = requests.get(url, headers=headers)
    html_content = response.text
    return html_content


# Read the CSV file containing SMC guidance data
TAR = pd.read_csv('evidence_SMC_lists.csv', sep=',')

# Initialize an empty list to store the final CSV data
final_csv = []

# Iterate through each row in the CSV file
for row in TAR.iterrows():
    medicine = row[1]['medicine']
    ID = row[1]['ID']
    print(ID)  # Print the ID for tracking progress

    # Initialize default values for various fields
    recommendation = 'Not Accepted'
    recommendation_text = ''
    under_review = ''
    restrictions = ''
    extra_info = ''

    # Fetch the HTML content from the given link
    html_content = get_url_data('https://' + row[1]['Link'].replace("//", '/'))

    # Parse the HTML content
    soup = BeautifulSoup(html_content, 'html.parser')

    # Find the div containing the advice text
    advice_text = soup.find('div', class_='advice')
    if advice_text:
        # Extract all paragraph elements within the advice div
        advice_texts_ps = advice_text.find_all('p')

        # Iterate through each paragraph, starting from the second one
        for advice_texts_p in advice_texts_ps[1:]:
            info = advice_texts_p.get_text(strip=True)
            if info.startswith(medicine):
                recommendation_text = info
                if "not" not in recommendation_text:
                    recommendation = 'Accepted'
                    if 'restricted' not in recommendation_text:
                        restrictions = 'no restrictions'
            elif 'Indication under review' in info:
                under_review = info
            elif 'restriction' in info:
                restrictions = info
            else:
                extra_info += info

        # Append the extracted data to the final CSV list
        final_csv.append([ID, recommendation, recommendation_text, restrictions, under_review, extra_info])

# Create a DataFrame from the collected data and save it to a CSV file
dd = pd.DataFrame(final_csv)
dd.columns = ['SMC ID', 'Recommendation', 'Recommendation text', 'Restrictions', 'Under Review', 'Extra Information']
dd.to_csv('Recommendations_SMC.csv', sep='\t', index=False)
