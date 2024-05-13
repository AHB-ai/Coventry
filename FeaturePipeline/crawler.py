import requests
import csv
import os
import time
from bs4 import BeautifulSoup
import pandas as pd

def csv_writer(data, file_name, headers=None):
    directory = "data/all_data"
    os.makedirs(directory, exist_ok=True)
    file_path = os.path.join(directory, file_name)
    with open(file_path, 'w', newline='', encoding='utf-8') as file:
        writer = csv.writer(file)
        if headers:
            writer.writerow(headers)
        for item in data:
            writer.writerow(item)
    return f"Successfully saved {file_name} file"

class Crawler:
    def __init__(self, base_url="https://www.coventry.gov.uk"):
        self.base_url = base_url.rstrip('/')  

    def extract_A2Z(self):
        response = requests.get(self.base_url)
        soup = BeautifulSoup(response.text, 'html.parser')
        letter_links = [self.base_url + link['href'] for link in soup.find_all("a", class_="button button--secondary") if link['href'].startswith('/')]
        return csv_writer(letter_links, "main_urls.csv")

    def service_urls(self,file_name):
        df = pd.read_csv("data/main_urls.csv",names=['cols'])
        filtered_links = []
        for page_link in df['cols']:
            print(f"Extracting url {page_link}")
            response = requests.get(page_link)
            soup = BeautifulSoup(response.text, 'html.parser')
            links = [self.base_url + link['href'] for link in soup.find_all("a", class_="list__link") if link['href'].startswith('/a-to-z/service')]
            filtered_links.extend(links)
        links_str = '\n'.join(filtered_links)
    
    # Write the links string to the CSV file
        with open(f"data/all_data/{file_name}", 'w', newline='') as csvfile:
            csvfile.write(links_str)
        return "Finish"

    def page_urls(self):
        df = pd.read_csv("data/all_data/all_service_urls.csv", names=["cols"])
        all_links = []
        for url in df['cols']:
            response = requests.get(url)
            soup = BeautifulSoup(response.text, 'html.parser')
            links = [link['href'] for link in soup.find_all("a", class_="service__link") if link['href'].startswith('/')]
            all_links.extend([self.base_url + link for link in links])
        links_str = '\n'.join(all_links)
    
    # Write the links string to the CSV file
        with open(f"data/all_data/service_links_filter.csv", 'w', newline='') as csvfile:
            csvfile.write(links_str)
        return "Finish"

    def get_page_content_links(self):
        df = pd.read_csv("data/all_data/page_content4link.csv", names=['cols'])
        filtered_links = []
        for link in df['cols']:
            print(link)
            response = requests.get(link)
            soup = BeautifulSoup(response.text, 'html.parser')
            page_links = soup.find_all("a", class_="service__link")
            if page_links:
                try:
                    max_page = int(soup.find("span", class_="nav__toggle-pages").get_text()[-1])
                    filtered_links.extend([link[:-1] + str(j) for j in range(1, max_page + 1)])
                except Exception as e:
                    print(f"Error processing link {link}: {e}")
            else:
                filtered_links.append(link)

        links_str = '\n'.join(filtered_links)

        with open(f"data/all_data/page_content_links.csv", 'w', newline='') as csvfile:
            csvfile.write(links_str)
        return "Finish"
    
    def crawl_content(self):
        df = pd.read_csv("data/all_data/page_content_links.csv", names=["cols"])     
        data = []

        for idx, link in enumerate(df['cols']):
            print(link)
            response = requests.get(link)
            soup = BeautifulSoup(response.text, 'html.parser')
            li_tags = soup.find_all('li')
            li_tags_without_class = [tag for tag in li_tags if not tag.get("class")]
            li_texts = " "  
            p_texts = " "
            for li_tag in li_tags_without_class:
                li_texts += li_tag.text.strip() + " "

            p_tags = soup.find_all("p")
            p_without_class = [tag for tag in p_tags if not tag.get("class")]

            for p_tag in p_without_class:
                p_texts += p_tag.text.strip() + " "

            data.append(li_texts + p_texts)

        links_str = '\n'.join(data)

        # Write the links string to a text file
        with open("data/all_data/extracted_texts.txt", 'w', encoding='utf-8') as textfile:
            textfile.write(links_str)

        return "Finish"



