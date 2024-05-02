import requests
import csv
import os
import time
from bs4 import BeautifulSoup
import pandas as pd

def csv_writer(data, file_name, headers=None):
    directory = "data"
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

    def service_urls(self, page_link):
        response = requests.get(page_link)
        soup = BeautifulSoup(response.text, 'html.parser')
        filtered_links = [self.base_url + link['href'] for link in soup.find_all("a", class_="list__link") if link['href'].startswith('/a-to-z/service')]
        return csv_writer(filtered_links, "service_urls.csv")

    def page_urls(self):
        df = pd.read_csv("data/service_urls.csv", names=["cols"])
        all_links = []
        for url in df['cols']:
            response = requests.get(url)
            soup = BeautifulSoup(response.text, 'html.parser')
            links = [link['href'] for link in soup.find_all("a", class_="service__link") if link['href'].startswith('/')]
            all_links.extend([self.base_url + link for link in links])
        return csv_writer(all_links, "service_links_filter.csv")

    def get_page_content_links(self):
        df = pd.read_csv("data/page_content4link.csv", names=['cols'])
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
            # time.sleep(30)
        return csv_writer(filtered_links, "page_content_links.csv")
    
    def crawl_content(self):
        df = pd.read_csv("data/page_content_links.csv", names=["cols"])     
        data = []

        for idx, link in enumerate(df['cols']):
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

            data.append([link, li_texts + p_texts])

        headers = ["Link", "Text"]
        return csv_writer(data, "crawled_content.csv", headers)

