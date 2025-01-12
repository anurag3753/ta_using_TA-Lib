import requests
import pandas as pd
from bs4 import BeautifulSoup
from openpyxl import Workbook
from selenium import webdriver
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.common.by import By
from selenium.webdriver.chrome.options import Options
from webdriver_manager.chrome import ChromeDriverManager

# Global vars
use_count = True

def main():
    # Example usage
    url = 'https://www.chittorgarh.com/report/mainboard-ipo-list-in-india-bse-nse/83/'  # All IPOS (SME and Mainboard)
    output_file = 'ipo_data.xlsx'  # Output Excel file path
    parse_webpage(url, output_file)

key_mapping = {
    'Others': 'qib',
    'Qualified Institutional': 'qib',
    'Qualified Institutions' : 'qib',
    'Non Institutional': 'hni',
    'Non-Institutional Buyers*': 'hni',
    'Non-Institutional Buyers': 'hni',
    'Retail Investors' : 'rii',
    'Retail Individual' : 'rii',
    'Total Subscription' : 'total',
    'Total': 'total',
}

def get_subscription_details(url):
    # Send a GET request to the webpage URL
    response = requests.get(url)

    # Create a BeautifulSoup object to parse the HTML content
    soup = BeautifulSoup(response.content, "html.parser")

    # Find the specific elements containing the desired data
    subscription_details = soup.find("div", itemtype='https://schema.org/Table')

    if subscription_details is None:
        print("Subscription details not found on the webpage.")
        return None

    subscription_table = subscription_details.find("table")
    if subscription_table is None:
        print("Subscription table not found on the webpage.")
        return None

    # Extract the subscription details from the table
    data = {}
    mapped_data = {}
    rows = subscription_table.find_all("tr")

    headers = [header.text.strip() for header in subscription_table.select('thead tr th')]

    for row in subscription_table.select('tbody tr'):
        row_data = [data.text.strip() for data in row.select('td')]
        if len(row_data) == len(headers):
            data[row_data[0]] = row_data[1]

    # It checks the above dictionary and maps the irregular ipo category to (qib,rii,hni etc)
    # Also note Others --> qib (is classified as QIB quota only)
    mapped_data = {key_mapping.get(key, key): value for key, value in sorted(data.items())}

    collected_data = {}
    
    selected_keys = ['qib', 'hni', 'rii', 'total']   # select only these fields
    for key in selected_keys:
        if key in mapped_data:
            if mapped_data[key] == "[.]":
                collected_data[key] = 0
            else:
                collected_data[key] = float(mapped_data[key])
        else:
            collected_data[key] = 0
    return collected_data

def parse_webpage(url, output_file):
    # Set up Selenium WebDriver
    chrome_options = Options()
    chrome_options.add_argument("--headless")  # Run in headless mode
    driver = webdriver.Chrome(service=Service(ChromeDriverManager().install()), options=chrome_options)

    # Fetch the webpage
    driver.get(url)

    # Get the page source after JavaScript has rendered the content
    html = driver.page_source

    # Parse the HTML content using BeautifulSoup
    soup = BeautifulSoup(html, 'html.parser')

    # Write the prettified HTML content to a file
    with open("out.txt", 'w', encoding='utf-8') as file:
        file.write(soup.prettify())

    # Find the table of interest based on the id attribute
    table_div = soup.find('div', id='report_data')

    # Extract the table from the div
    table = table_div.find('table')
    print(table)

    # Extract the table headers
    headers = [header.text.strip() for header in table.select('thead tr th')]
    headers.insert(0, 'URL')  # Insert the new header 'URL' at the beginning
    headers.extend(["qib", "hni", "rii", "total"])

    # Extract the table rows
    rows = []
    count = 0
    failed = []
    for row in table.select('tbody tr'):
        # Find the link element in the first column
        link = row.find('a')

        # Extract the URL and title attributes
        href = link['href']
        href = href.replace("/ipo/", "/ipo_subscription/")
        row_data = [href] + [data.text.strip() for data in row.select('td')]

        try:
            # Call the get_subscription_info function to fetch additional stock details
            stock_details = get_subscription_details(href)
            if len(stock_details) == 4:
                row_data.extend(stock_details.values())
                rows.append(row_data)
        except Exception as e:          
            failed.append(row_data)
            print(f"Failed for {row_data}")
        print(row_data)

        count += 1
        if count == 30 and use_count:
            break
        
    # open a txt file to write for failed fetch
    with open("failed.txt", "w") as fh:
        for item in failed:
            fh.write(str(item) + "\n")

    # Convert the data to a pandas DataFrame
    df = pd.DataFrame(rows, columns=headers)
    
    # Drop the specified columns from the DataFrame
    df = df.drop(columns=["Open Date", "Lot Size", "Compare"])
    
    # Column order in which data needs to be printed
    desired_column_order = [ "Close Date",
                    "Issuer Company",
                    "Issue Size (Rs Cr.)",
                    "Issue Price (Rs)",
                    "qib",
                    "hni",
                    "rii",
                    "total",
                    "URL",
                    "Exchange",
                    ]

    # Filter the DataFrame based on the condition 'qib' <= 25
    filtered_df = df[df['qib'] >= 25]

    # # Add an additional condition for 'qib' >= 50 when 'Exchange' is "NSE SME" or "BSE SME"
    # filtered_df = filtered_df[filtered_df.apply(lambda row: row['qib'] >= 50 if row['Exchange'] in ["NSE SME", "BSE SME"] else True, axis=1)]

    # Add an additional condition to exclude 'Exchange' values of "NSE SME" or "BSE SME"
    filtered_df = filtered_df[~((filtered_df['Exchange'] == "NSE SME") | (filtered_df['Exchange'] == "BSE SME"))]

    # Reorder the columns in the filtered DataFrame
    filtered_df = filtered_df[desired_column_order]

    # Export the filtered DataFrame to an Excel file
    filtered_df.to_excel(output_file, index=False)

    # Close the Selenium WebDriver
    driver.quit()
    
if __name__ == "__main__":
    main()
