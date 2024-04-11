import os
import requests
import pandas as pd
from datetime import date
from datetime import datetime
from bs4 import BeautifulSoup
from dotenv import load_dotenv
from urllib.parse import unquote

import matplotlib.pyplot as plt
import numpy as np

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

def plot_data_week(data):
    # Get unique years in the data
    unique_years = data['Year'].unique()

    # Get the maximum number of weeks across all years
    max_weeks = max(data['Week'])

    # Initialize an array to store the sum of quantities for each week
    total_quantities_by_year = []

    # Calculate total quantities for each year
    for year in unique_years:
        # Filter data for the current year
        year_data = data[data['Year'] == year]
        
        # Initialize an array to store the sum of quantities for each week in the current year
        total_quantities = np.zeros(max_weeks)

        # Sum quantities for each week in the current year
        for week, group in year_data.groupby('Week'):
            total_quantities[week - 1] = group['Quantity'].sum()  # Week index starts from 1

        total_quantities_by_year.append(total_quantities)

    # Plot data for each year
    for i, year_data in enumerate(total_quantities_by_year):
        plt.plot(np.arange(1, max_weeks + 1), year_data, label=f'Year {unique_years[i]}')

    plt.xlabel('Week')
    plt.ylabel('Total Quantity')
    plt.title('Total Quantity vs Week')
    plt.xticks(np.arange(1, max_weeks + 1))  # Set x-ticks to display weeks
    plt.legend()
    plt.show()

def plot_data_by_month(data):
    # Get unique years in the data
    unique_years = data['Year'].unique()

    # Get the maximum number of months across all years
    max_months = max(data['Month'])

    # Initialize an array to store the sum of quantities for each month
    total_quantities_by_year = []

    # Calculate total quantities for each year
    for year in unique_years:
        # Filter data for the current year
        year_data = data[data['Year'] == year]
        
        # Initialize an array to store the sum of quantities for each month in the current year
        total_quantities = np.zeros(max_months)

        # Sum quantities for each month in the current year
        for month, group in year_data.groupby('Month'):
            total_quantities[month - 1] = group['Quantity'].sum()  # Month index starts from 1

        total_quantities_by_year.append(total_quantities)

    # Plot data for each year
    for i, year_data in enumerate(total_quantities_by_year):
        plt.plot(np.arange(1, max_months + 1), year_data, label=f'Year {unique_years[i]}')

    plt.xlabel('Month')
    plt.ylabel('Total Quantity')
    plt.title('Total Quantity vs Month')
    plt.xticks(np.arange(1, max_months + 1))  # Set x-ticks to display months
    plt.legend()
    plt.show()


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

        # Iterate over each <td> tag and extract text from <span> elements
        for td in td_tags:
            job_name = unquote(td.get('jobname'))  # Get jobName attribute
            # Replace the line where job_date is obtained with the actual value from the HTML
            job_date = td.get('dragdate')  # Get dragdate attribute

            # Convert job_date string to datetime object
            date_obj = datetime.strptime(job_date, "%m/%d/%Y")

            # Extract day, month, and year
            day = date_obj.day
            month = date_obj.month
            year = date_obj.year

            # Calculate week number
            week_number = date_obj.isocalendar()[1]

            note = ''
            if job_name:
                # Filter out <span> elements with 'data-mwtooltip' attribute
                span_tags = [span for span in td.find_all('span') if not span.has_attr('data-mwtooltip')]

                # Skip the first instance of <span>
                for span in span_tags[1:]:  # We ignore the first result from the span tag, which contains in this view case the same name of the job
                    span_text = span.get_text(strip=True)  # strip=True it removes any leading and trailing whitespace characters from the extracted text.
                    quantity = 1

                    # If the span text contains a hyphen followed by a number, split the text
                    if '-' in span_text:
                        material, qty_info = span_text.split('-', 1)

                        # Check if qty_info is not empty
                        if qty_info:
                            # If the next character after the number is numeric, extract the quantity
                            if qty_info[0].isdigit():
                                quantity = int(qty_info[0])
                                index = 1

                                # Check for consecutive digits to determine the complete quantity
                                while index < len(qty_info) and qty_info[index].isdigit():
                                    quantity = quantity * 10 + int(qty_info[index])
                                    index += 1

                        # Checking for bigger quantities is basically useless in the code above since I can't control
                        # how data is entered, so anything bigger than 10 at the end of the day will get set to 1 and a
                        # note will be added.
                        # Maybe I'll optimize this in the future so that runtime is shortened significantly
                        if (quantity > 10):
                            quantity = 1
                            note = 'The count exceds 10 and should be looked at.'

                        # Append the entry with the calculated quantity
                        data.extend([[job_name, date_obj, day, month, year, week_number, material, span, quantity, note]])
                    else:
                        # If no hyphen followed by a number is found, consider it as a single material
                        data.append([job_name, date_obj, day, month, year, week_number, material.strip(), span, quantity, note])

        # Flavour context messages of the first 6 data entries for the user in cli
        for x in range(0, 6):
            print(f'Job: {data[x][0]} [{data[x][1]}] - {data[x][2]}') #[0][0] = Job Name, [0][1] = Job Date, [0][2] = Job Material
        if data[7]:
            print('...')

        # Create a DataFrame from the collected data
        df = pd.DataFrame(data, columns=['Job Name', 'Date', 'Day', 'Month', 'Year', 'Week', 'Material', 'Span', 'Quantity', 'Note'])
        # excel_file_path = generate_excel_file_path(folder_path, date_range, day_count)
        # print(f'Creating {excel_file_path}...')

        # # Save the DataFrame to an Excel file
        # df.to_excel(excel_file_path, index=False)
        # print(f'Created {excel_file_path} successfully. \n')


        plot_data_week(df)
        plot_data_by_month(df)

    else:
        print("Data request failed. Status code:", data_response.status_code)
else:
    print("Login failed. Status code:", login_response.status_code)
