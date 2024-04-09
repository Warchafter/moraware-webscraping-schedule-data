import requests
import pandas as pd
from bs4 import BeautifulSoup
import os
from dotenv import load_dotenv

load_dotenv()

login_url = 'https://majestic-marble.moraware.net/sys/'
data_url = 'https://majestic-marble.moraware.net/sys/calendar?&view=123&daycount=4&refreshrate=5&display=3&activitytype=22,23,57&expand=8?16&wrap=1&filters=2|3:1:28:1:5608;0&text=JN1,JA23,JA24,JA25,JA26,AT4&effdate=2024-04-08'
data_parameters = '/sys/calendar?&view=123&daycount=365&refreshrate=4&display=3&activitytype=22,23,57&expand=8?16&wrap=1&filters=2|3:1:28:1:5608;0&text=JN1,JA23,JA24,JA25,JA26,AT4&effdate=2024-04-08'

session = requests.Session()

payload = {
    'user': os.getenv("MORAWARE_USERNAME"),
    'pwd': os.getenv("MORAWARE_PASSWORD"),
    'redirectURL': data_parameters,
    'LOGIN': 'Sign in'
}

login_response = session.post(login_url, data=payload)

if login_response.status_code == 200:
    # Use session to make subsequent requests
    data_response = session.get(data_url)

    if data_response.status_code == 200:
        html = data_response.text
        soup = BeautifulSoup(html, 'html.parser')

        folder_path = "./exports"
        os.makedirs(folder_path, exist_ok=True)

        html_file_path = os.path.join(folder_path, "moraware_html.html")

        with open(html_file_path, "a", encoding="utf-8") as f:
            f.write(html)

        # Find all <td> tags within the <tr> tag
        td_tags = soup.find_all('td', class_="calendarItem")

        data = [] # We initialize the data to be used when creating the excel

        # Iterate over each <td> tag and extract text from <span> elements
        for td in td_tags:
            job_name = td.get('jobname')  # Get jobName attribute
            job_date = td.get('dragdate') # Get dragdate attribute
            if job_name:
                print("Job: ", job_name, " [", job_date, "]")
                span_tags = td.find_all('span') # The span is what contains all the data from the slabs that we want to get

                # Skip the first instance of <span>
                for span in span_tags[1:]: # We ignore the first result from the span tag, which contains in this view case the same name of the job
                    span_text = span.get_text(strip=True) # strip=True it removes any leading and trailing whitespace characters from the extracted text.
                    data.append([job_name, job_date, span_text])

        # Create a DataFrame from the collected data
        df = pd.DataFrame(data, columns=['Job Name', 'Date', 'Span Text'])

        excel_file_path = os.path.join(folder_path, "moraware_data.xlsx")

        # Save the DataFrame to an Excel file
        df.to_excel(excel_file_path, index=False)

    else:
        print("Data request failed. Status code:", data_response.status_code)
else:
    print("Login failed. Status code:", login_response.status_code)
