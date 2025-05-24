# Requirements: Run `pip install requests beautifulsoup4 pandas` to install dependencies

import requests
from bs4 import BeautifulSoup
import pandas as pd
import time

# Function to fetch and parse a webpage
def fetch_page(url):
    try:
        headers = {'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36'}
        response = requests.get(url, headers=headers, timeout=10)
        response.raise_for_status()  # Raise an error for bad status codes
        return BeautifulSoup(response.text, 'html.parser')
    except requests.RequestException as e:
        print(f"Error fetching page {url}: {e}")
        return None

# Function to extract project details from the detail page
def extract_project_details(detail_url):
    soup = fetch_page(detail_url)
    if not soup:
        return None, None, None
    
    try:
        # Navigate to Promoter Details tab (assumed to be in a specific section)
        promoter_details = soup.find('div', class_='tab-content')  # Adjust based on actual HTML structure
        if not promoter_details:
            return None, None, None
        
        # Extract Promoter Name (Company Name)
        promoter_name = None
        name_elements = promoter_details.find_all('p')  # Assuming promoter name is in a <p> tag
        for element in name_elements:
            if 'Company Name' in element.text or 'Promoter Name' in element.text:
                promoter_name = element.text.split(':')[-1].strip()
                break
        
        # Extract Registered Office Address
        address = None
        for element in name_elements:
            if 'Registered Office Address' in element.text or 'Address' in element.text:
                address = element.text.split(':')[-1].strip()
                break
        
        # Extract GST No
        gst_no = None
        for element in name_elements:
            if 'GST No' in element.text or 'GST' in element.text:
                gst_no = element.text.split(':')[-1].strip()
                break
        
        return promoter_name, address, gst_no
    except Exception as e:
        print(f"Error extracting details from {detail_url}: {e}")
        return None, None, None

# Main function to scrape the first 6 projects
def scrape_rera_projects():
    base_url = 'https://rera.odisha.gov.in'
    project_list_url = f'{base_url}/projects/project-list'
    
    # Fetch the project list page
    soup = fetch_page(project_list_url)
    if not soup:
        print("Failed to fetch project list page.")
        return
    
    # Find the table containing registered projects
    table = soup.find('table', class_='table')  # Adjust class based on actual HTML
    if not table:
        print("Project table not found.")
        return
    
    # Initialize list to store project data
    projects = []
    
    # Get table rows (skip header)
    rows = table.find_all('tr')[1:7]  # Fetch first 6 projects
    
    for row in rows:
        cols = row.find_all('td')
        if len(cols) < 3:
            continue
        
        # Extract RERA Regd. No and Project Name
        rera_regd_no = cols[1].text.strip()  # Adjust index based on table structure
        project_name = cols[2].text.strip()  # Adjust index based on table structure
        
        # Find the "View Details" link
        detail_link = cols[-1].find('a', href=True)
        if not detail_link:
            print(f"No details link found for project {project_name}")
            continue
        
        detail_url = base_url + detail_link['href']
        
        # Extract promoter details
        promoter_name, address, gst_no = extract_project_details(detail_url)
        
        # Append data to projects list
        projects.append({
            'RERA Regd. No': rera_regd_no,
            'Project Name': project_name,
            'Promoter Name': promoter_name if promoter_name else 'Not Found',
            'Address of Promoter': address if address else 'Not Found',
            'GST No': gst_no if gst_no else 'Not Found'
        })
        
        # Add delay to avoid overwhelming the server
        time.sleep(1)
    
    # Create a DataFrame for better display
    df = pd.DataFrame(projects)
    print("\nScraped Projects:")
    print(df)
    
    # Save to CSV (optional)
    df.to_csv('odisha_rera_projects.csv', index=False)
    print("\nData saved to 'odisha_rera_projects.csv'")

# Run the scraper
if __name__ == "__main__":
    scrape_rera_projects()
