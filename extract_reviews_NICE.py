from bs4 import BeautifulSoup
import pandas as pd
import requests

def get_url_data(url):

    headers = {
        'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/58.0.3029.110 Safari/537.3',
        'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,image/webp,*/*;q=0.8',
        'Accept-Language': 'en-US,en;q=0.5',
        'DNT': '1',  # Do Not Track Request Header
        'Connection': 'keep-alive'
    }


    # Make the GET request with the specified headers
    response = requests.get(url, headers=headers)
    if response.status_code==200:
        html_content = response.text
        return html_content
    else:
        return None


TAR=pd.read_csv('evidence_NICE_lists.csv',sep=',')

# extensions=['/guidance/ta949','guidance/ta950','guidance/ta951','guidance/ta948']
final_csv=[]


for row in TAR.iterrows():
    title=row[1]['Title']
    TAnumber=row[1]['TA Number']
    print(TAnumber)

    url=f'''{row[1]['Link']}/chapter/3-Committee-discussion'''
    html_content = get_url_data(url)
    soup = BeautifulSoup(html_content, 'html.parser')
    if "Committee" in soup.find('title').string and "discussion" in soup.find('title').string:
        # Find all <li> elements
        li_elements = soup.select('.in-page-nav__list .in-page-nav__item')

        # Initialize an empty list to store the data
        data = []

        # Loop through each <li> element
        for li in li_elements:
            a_tag = li.find('a')
            section_title = a_tag.text.strip()
            section_link = a_tag['href'].strip()

            # Find the corresponding <div> with the matching title
            div_section = soup.find('div', title=section_title)

            # Extract text from the found <div> if it exists
            div_section_p=div_section.find_all('p')
            div_texts=''
            for i in div_section_p:
                div_texts+=i.get_text(strip=True, separator=' ')

            # Append the extracted information to the data list
            data.append([section_title, section_link, div_texts])

# Convert the list to a pandas DataFrame
df = pd.DataFrame(data, columns=['Section Title', 'Link', 'Section Text'])

# Save the DataFrame to a CSV file
csv_file_path = '/mnt/data/extracted_sections.csv'
df.to_csv(csv_file_path, index=False)

