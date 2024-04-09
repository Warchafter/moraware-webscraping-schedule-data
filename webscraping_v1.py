import os
import requests
import pandas as pd
from datetime import date
from bs4 import BeautifulSoup
from dotenv import load_dotenv
from urllib.parse import unquote

load_dotenv()

login_url = 'https://majestic-marble.moraware.net/sys/'
global data_url
global data_parameters
global date_range
global day_count

data_parameters = '/sys/calendar'
date_range = date.today()
day_count = 30


def get_input_range():
    while True:
        print('YYYY-MM-DD Ex. 2023-10-07')
        date_range_input = input('Date Range [Empty for today]: ')
        if len(date_range_input) == 10:
            print(f'The range selected was: {date_range_input}')
            return date_range_input
        if (date_range_input == ""):
            print(f'Default date range will be used {date_range}')
            return date_range
        else:
            print('Invalid date range.')
            print('Please make sure it follows the specified format.')

def get_day_count():
    while True:
        day_count_input = input('Day Count [Default 30]: ')
        if day_count_input.isnumeric:
            print(f'The day count selected was: {day_count_input}')
            return day_count_input
        if (day_count_input == ""):
            print(f'Default day count will be used 30')
            return day_count
        else:
            print('Invalid day count.')
            print('Please make sure it follows the specified format.')



print('Welcome to the webscraper app developed by Kevin Arriaga')
print('Please, type the date from which you wish to start the data extraction. (Leave empty for today`s date)')

date_range = get_input_range()
day_count = get_day_count()

print(f'[USER={os.getenv("MORAWARE_USERNAME")}]')
print(f'[PASS={os.getenv("MORAWARE_PASSWORD")}]')
print('Attempting to stablish connection to Moraware Servers with credentials.\n')

session = requests.Session()

payload = {
    'user': os.getenv("MORAWARE_USERNAME"),
    'pwd': os.getenv("MORAWARE_PASSWORD"),
    'redirectURL': data_parameters,
    'LOGIN': 'Sign in'
}

login_response = session.post(login_url, data=payload)
data_url = f'https://majestic-marble.moraware.net/sys/calendar?&view=123&daycount={day_count}&refreshrate=5&display=3&activitytype=22,23,57&expand=8?16&wrap=1&filters=2|3:1:28:1:5608;0&text=JN1,JA23,JA24,JA25,JA26,AT4&effdate={date_range}'

if login_response.status_code == 200:
    print(f'Successful connection - {login_response}\n')
    # Use session to make subsequent requests
    data_response = session.get(data_url)

    if data_response.status_code == 200:
        html = data_response.text
        soup = BeautifulSoup(html, 'html.parser')

        folder_path = "./exports"
        print(f'Creating folder: {folder_path}')
        os.makedirs(folder_path, exist_ok=True)

        html_file_path = os.path.join(folder_path, "moraware_html.html")
        print(f'Creating moraware_html.html in {html_file_path}...')
        with open(html_file_path, "a", encoding="utf-8") as f:
            f.write(html)
            print(f'Created moraware_html.html in successfully. \n')

        # Find all <td> tags within the <tr> tag
        td_tags = soup.find_all('td', class_="calendarItem")

        data = [] # We initialize the data to be used when creating the excel

        # Iterate over each <td> tag and extract text from <span> elements
        for td in td_tags:
            job_name = unquote(td.get('jobname'))  # Get jobName attribute
            job_date = td.get('dragdate') # Get dragdate attribute
            if job_name:
                # print("Job: ", job_name, " [", job_date, "]")
                span_tags = td.find_all('span') # The span is what contains all the data from the slabs that we want to get

                # Skip the first instance of <span>
                for span in span_tags[1:]: # We ignore the first result from the span tag, which contains in this view case the same name of the job
                    span_text = span.get_text(strip=True) # strip=True it removes any leading and trailing whitespace characters from the extracted text.
                    data.append([job_name, job_date, span_text])

        for x in range(0, 6):
            print(f'Job: {data[x][0]} [{data[x][1]}] - {data[x][2]}') #[0][0] = Job Name, [0][1] = Job Date, [0][2] = Job Material
        if data[7]:
            print('...')

        # Create a DataFrame from the collected data
        df = pd.DataFrame(data, columns=['Job Name', 'Date', 'Span Text'])
        excel_file_path = os.path.join(folder_path, "moraware_data.xlsx")
        print(f'\nCreating moraware_data.xlsx in {excel_file_path}...')

        # Save the DataFrame to an Excel file
        df.to_excel(excel_file_path, index=False)
        print(f'Creating moraware_data.xlsx in successfully. \n')

    else:
        print("Data request failed. Status code:", data_response.status_code)
else:
    print("Login failed. Status code:", login_response.status_code)
