import requests
import re


headers = {
    'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/58.0.3029.110 Safari/537.3',
    'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,image/webp,*/*;q=0.8',
    'Accept-Language': 'en-US,en;q=0.5',
    'DNT': '1',  # Do Not Track Request Header
    'Connection': 'keep-alive'
}

final_smc=[]
for i in range(1,95):
    url=f'''https://www.scottishmedicines.org.uk/umbraco/Api/ListMedicineAdviceApi/GetResultsByType?active-tab=0&node-id=6990&keywords=&filter-3561=&filter-3567=&filter-3803=&from=&to=&total-results-0=1876&current-page-0={i}&max-page-0=94&total-results-1=30&current-page-1=1&max-page-1=2'''
    # Make the GET request with the specified headers
    response = requests.get(url, headers=headers)
    if response.status_code==200:
        html_content = response.json()
        if 'SearchResults' in html_content:
            search_results = html_content['SearchResults']
            for search_result in search_results:
                medicine = search_result['Heading'].split("(")[0]
                if "(" in search_result['Heading']:
                    medicine_extra = search_result['Heading'].split("(")[-1].split(")")[0]
                else:
                    medicine_extra=''
                published_date=search_result['PublishedDateText']
                advice_date=search_result['AdviceDueDateText']
                meeting_date=search_result['MeetingDateText']
                ID=search_result['DrugId']
                indication=search_result['Indication']
                indication = re.sub('<[^<]+?>', '', indication)  # Removes HTML tags
                submission_type=search_result['SubmissionType']
                if search_result['Link']['IsValid']:
                    Link=f'''www.scottishmedicines.org.uk/{search_result['Link']['Url']}'''
                else:
                    Link=''

                final_smc.append([ID,medicine,medicine_extra,indication,submission_type,published_date,advice_date,meeting_date,Link])
    else:
        continue

import pandas as pd

final_smc_df=pd.DataFrame(final_smc)
final_smc_df.columns=['ID','medicine','medicine (other name)','indication','submissiontype','publiseddate','advicedate','meetingdate','Link']
final_smc_df.to_csv('evidence_SMC_lists.csv',sep=',',index=None)


