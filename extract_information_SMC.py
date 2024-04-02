import requests
from bs4 import BeautifulSoup
import re
import pandas as pd


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
    html_content = response.text
    return html_content

TAR=pd.read_csv('evidence_SMC_lists.csv',sep=',')
final_csv=[]

for row in TAR.iterrows():
    medicine=row[1]['medicine']
    ID=row[1]['ID']
    print(ID)
    recommendation = 'Not Accepted'
    recommendation_text=''
    under_review= ''
    restrictions=''
    extra_info=''
    html_content=get_url_data('https://'+row[1]['Link'].replace("//",'/'))

    # Parse the HTML content
    soup = BeautifulSoup(html_content, 'html.parser')
    advice_text=soup.find('div',class_='advice')
    if advice_text:
        advice_texts_ps=advice_text.find_all('p')
        for advice_texts_p in advice_texts_ps[1:]:
            info=advice_texts_p.get_text(strip=True)
            if info.startswith(medicine):
                recommendation_text=info
                if "not" not in recommendation_text:
                    recommendation = 'Accepted'
                    if 'restricted' not in recommendation_text:
                        restrictions='no restrictions'
            elif 'Indication under review' in info:
                under_review=info
            elif 'restriction' in info:
                restrictions=info
            else:
                extra_info+=info

        final_csv.append([ID,recommendation,recommendation_text,restrictions,under_review,extra_info])

dd=pd.DataFrame(final_csv)
dd.columns=['SMC ID','Recommendation','Recommendation text','Restrictions'
                                                       ,'Under Review','Extra Information']
dd.to_csv('Recommendations_SMC.csv',sep='\t',index=False)