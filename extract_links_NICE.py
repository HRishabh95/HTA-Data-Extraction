import requests
from bs4 import BeautifulSoup
import csv
import psycopg2

conn = psycopg2.connect(
    database="postgres",
    host="localhost",
   user="ricky",
   password="123456",
   port= '5432'
)

conn.autocommit = True

# Creating a cursor object
cur = conn.cursor()

# query to create a database
# Create the table if it does not exist
cur.execute('''
    CREATE TABLE IF NOT EXISTS nice_lists (
        title VARCHAR(500),
        link VARCHAR(500),
        ta_number VARCHAR(50) PRIMARY KEY,
        publication_date DATE,
        last_reviewed DATE
    )
''')

url='https://www.nice.org.uk/guidance/published?ndt=Guidance&ngt=Technology%20appraisal%20guidance&ps=9999'

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

soup = BeautifulSoup(html_content, 'html.parser')

rows = soup.find_all('tr')

with open('evidence_NICE_lists.csv', 'w', newline='', encoding='utf-8') as csvfile:
    csvwriter = csv.writer(csvfile)
    # Write the CSV header
    csvwriter.writerow(['Title', 'Link', 'TA Number', 'Publication Date', 'Last Reviewed'])

    # Iterate over each row in the table
    for row in rows:
        # Extract data from columns
        cols = row.find_all('td')
        if cols:
            a_tag = cols[0].find('a')
            title = a_tag.text.strip() if a_tag else ''
            link = a_tag['href'] if a_tag else ''
            ta_number = cols[1].text.strip()
            publication_date = cols[2].text.strip()
            last_reviewed = cols[3].text.strip()

            # Write the row data to the CSV file
            cur.execute('''
                            INSERT INTO nice_lists (title, link, ta_number, publication_date, last_reviewed)
                            VALUES (%s, %s, %s, %s, %s)
                        ''', (title, link, ta_number, publication_date, last_reviewed))
            conn.commit()
            csvwriter.writerow([title, link, ta_number, publication_date, last_reviewed])

print("CSV file with links has been created successfully.")


