import pandas as pd
import os
import time
from selenium import webdriver
from selenium.webdriver.common.keys import Keys
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
import configparser
import zipfile

config = configparser.ConfigParser()
config.read('config.ini')

readmeio_email = config['Credentials']['readmeio_email']
readmeio_password = config['Credentials']['readmeio_password']

chrome_options = webdriver.ChromeOptions()
script_directory = os.path.dirname(os.path.abspath(__file__))
# chrome_options.add_argument("user-data-dir=/Users/doug5142/Library/Application Support/Google/Chrome/Default")
chrome_options.add_experimental_option('prefs', {
    "download.default_directory": script_directory,  
    "download.prompt_for_download": False,          
    "safebrowsing.enabled": True                    
})
driver = webdriver.Chrome(options=chrome_options)

driver.get("https://dash.readme.com/login")

time.sleep(3) 

email_input_element = WebDriverWait(driver, 10).until(
   EC.element_to_be_clickable((By.ID, 'email')))

email_input_element.send_keys(readmeio_email)

password_input_element = WebDriverWait(driver, 10).until(
   EC.element_to_be_clickable((By.ID, 'password')))

password_input_element.send_keys(readmeio_password)

time.sleep(2) 

login_button = WebDriverWait(driver, 10).until(
    EC.element_to_be_clickable((By.XPATH, "//button[@type='submit' and .//span[text()='Log In']]"))
)

login_button.click()

time.sleep(2) 

driver.get("https://dash.readme.com/project/rackspace-test-1/v1.0/metrics/page-views#top-pages")

first_button = WebDriverWait(driver, 10).until(
    EC.element_to_be_clickable((By.XPATH, "//button[text()='Quarter']"))
)
first_button.click()

export_button = WebDriverWait(driver, 10).until(
    EC.element_to_be_clickable((By.XPATH, "//*[@id='dashReact']/div[1]/div/main/div/div[4]/div[1]/button"))
)
export_button.click()

time.sleep(25)  

desired_file_name = "docViews.csv"
desired_file_path = os.path.join(script_directory, desired_file_name)

# Find the most recently downloaded file in the script's directory
files = os.listdir(script_directory)
csv_files = [f for f in files if f.endswith('.csv')]

if csv_files:
    # Get the most recently modified CSV file
    latest_file = max(csv_files, key=lambda f: os.path.getmtime(os.path.join(script_directory, f)))
    latest_file_path = os.path.join(script_directory, latest_file)
    
    # Rename the latest file to the desired name
    os.rename(latest_file_path, desired_file_path)
    print(f"File renamed to: {desired_file_name}")
else:
    print("No CSV files found in the script directory.")

# Load the renamed CSV file into a DataFrame
df = pd.read_csv(desired_file_path)

#1.) SCAN DOCS VIEWED IN LAST X DAYS
df['page'] = df['page'].apply(lambda x: x.rsplit('/', 1)[-1])

page_list = df['page'].tolist()

page_string = '\n'.join(page_list)

with open('viewed_docs_output.txt', 'w') as f:
    f.write(page_string)
    
#2.) SCAN ALL DOCS

driver.get("https://dash.readme.com/project/rackspace-test-1/v1.0/settings")

# Wait until the first button is present and click it
export_docs_button = WebDriverWait(driver, 10).until(
    EC.element_to_be_clickable((By.XPATH, "//a[@ng-click='export()' and text()='Export Docs']"))
)
export_docs_button.click()

time.sleep(45)  # Adjust the wait time as needed

desired_all_docs_name = "my_project_export.zip"  # Change this to your desired name
desired_all_docs_path = os.path.join(script_directory, desired_all_docs_name)

# List all files in the project directory
files = os.listdir(script_directory)

# Filter for ZIP files
zip_files = [f for f in files if f.endswith('.zip')]

if zip_files:
    # Get the first (and only) ZIP file
    zip_file = zip_files[0]
    zip_file_path = os.path.join(script_directory, zip_file)
    
    # Rename the ZIP file to the desired name
    os.rename(zip_file_path, desired_all_docs_path)
    print(f"File renamed to: {desired_all_docs_name}")
    unzip_directory = os.path.join(script_directory, "all_docs")

    if not os.path.exists(unzip_directory):
        os.makedirs(unzip_directory)

    # Unzip the file
    with zipfile.ZipFile(desired_all_docs_path, 'r') as zip_ref:
        zip_ref.extractall(unzip_directory)
    print(f"File unzipped to: {unzip_directory}")
    
else:
    print("No ZIP files found in the project directory.")

all_docs = './all_docs'

file_names = []

for root, dirs, files in os.walk(all_docs):
    for file in files:
        if file.endswith('.md'):  # Check if the file ends with '.md'
            # Extract the name between the last '/' and '.md'
            file_name = file.rsplit('/', 1)[-1].replace('.md', '')
            # Add the processed file name to the list
            file_names.append(file_name)
            
output_file = 'all_docs_output.txt'

with open(output_file, 'w') as f:
    for name in file_names:
        f.write(name + '\n')

# 3.) SUBTRACT VIEWED DOCS FROM ALL DOCS TO GET UNUSUED DOCS

with open('all_docs_output.txt', 'r') as file_all:
    all_pages = set(line.strip() for line in file_all)

with open('viewed_docs_output.txt', 'r') as file_viewed:
    viewed_pages = set(line.strip() for line in file_viewed)

unviewed_pages = all_pages - viewed_pages

with open('unviewed_docs.txt', 'w') as output_file:
    for page in unviewed_pages:
        output_file.write(page + '\n')







