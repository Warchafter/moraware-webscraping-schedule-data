import os
import requests
import pandas as pd
from datetime import date
from bs4 import BeautifulSoup
from dotenv import load_dotenv
from urllib.parse import unquote

# from tkinter import *
# from tkinter import ttk

# Potential graphic interface with Tkinter in the future.
# root = Tk()
# frm = ttk.Frame(root, padding=200)
# frm.grid()
# ttk.Label(frm, text="Hello World!").grid(column=0, row=0)
# ttk.Button(frm, text="Quit", command=root.destroy).grid(column=1, row=0)
# root.mainloop()

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

def generate_excel_file_path(folder_path, date_range, day_count):
    base_filename = f"moraware_data_{date_range}_{day_count}.xlsx"
    filename, file_extension = os.path.splitext(base_filename)
    file_path = os.path.join(folder_path, base_filename)
    counter = 1
    while os.path.exists(file_path):
        new_filename = f"{filename}_{counter}{file_extension}"
        file_path = os.path.join(folder_path, new_filename)
        counter += 1
    return file_path

print('Welcome to the webscraper app developed by Kevin Arriaga')
print('Please, type the date from which you wish to start the data extraction. (Leave empty for today`s date)')

date_range = get_input_range()
day_count = get_day_count()

print(f'[USER={os.getenv("MORAWARE_USERNAME")}]')
print(f'[PASS={os.getenv("MORAWARE_PASSWORD")}]')
print('Attempting to stablish connection to Moraware Servers with credentials.\n')

session = requests.Session()

# Make sure to create a .env with the following variables of user and password for this to work.
payload = {
    'user': os.getenv("MORAWARE_USERNAME"),
    'pwd': os.getenv("MORAWARE_PASSWORD"),
    'redirectURL': data_parameters,
    'LOGIN': 'Sign in'
}

login_response = session.post(login_url, data=payload)

# data_url = f'https://majestic-marble.moraware.net/sys/calendar?&view=123&daycount={day_count}&refreshrate=5&display=3&activitytype=22,23,57&expand=8?16&wrap=1&filters=2|3:1:28:1:5608;0&text=JN1,JA23,JA24,JA25,JA26,AT4&effdate={date_range}'
# url for checking data in browser
# data_url = f'https://majestic-marble.moraware.net/sys/calendar?&view=0&activityType=15,19,59&assigneeId=&effdate=2024-04-15&dayCount=5&display=3&text=JN1,JA23,JA24,JA25,JA26&wrap=1&color=0&total=&expand=8%3F16&refreshRate=5&filters=2|3:1:28:1:5608;0&mrv=184'
data_url = f'https://majestic-marble.moraware.net/sys/calendar?&view=0&activityType=15,19,59&assigneeId=&effdate={date_range}&dayCount={day_count}&display=3&text=JN1,JA23,JA24,JA25,JA26&wrap=1&color=0&total=&expand=8%3F16&refreshRate=5&filters=2|3:1:28:1:5608;0&mrv=184'

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
            print(f'Created moraware_html.html successfully. \n')

        # Find all <td> tags within the <tr> tag
        td_tags = soup.find_all('td', class_="calendarItem")

        data = [] # We initialize the data to be used when creating the excel

        table_from_html = pd.read_html(html)
        table_ex = table_from_html[3]

        print("This is the table:\n", table_ex)

        with open('table_ex.txt', "a", encoding="utf-8") as f:
            f.write(f'table_from_html {table_ex}')
            print(f'Created table_ex.txt successfully. \n')

        # # Flavour context messages of the first 6 data entries for the user in cli
        # for x in range(0, 6):
        #     print(f'Job: {data[x][0]} [{data[x][1]}] - {data[x][2]}') #[0][0] = Job Name, [0][1] = Job Date, [0][2] = Job Material
        # if data[7]:
        #     print('...')

        # # Create a DataFrame from the collected data
        # df = pd.DataFrame(data, columns=['Job Name', 'Date', 'Span Text', 'Span', 'Quantity', 'Note'])
        # excel_file_path = generate_excel_file_path(folder_path, date_range, day_count)
        # print(f'Creating {excel_file_path}...')

        # # Save the DataFrame to an Excel file
        # df.to_excel(excel_file_path, index=False)
        # print(f'Created {excel_file_path} successfully. \n')

    else:
        print("Data request failed. Status code:", data_response.status_code)
else:
    print("Login failed. Status code:", login_response.status_code)
