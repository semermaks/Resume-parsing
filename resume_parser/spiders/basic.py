import os
import re

import requests
import scrapy
from selenium import webdriver
from selenium.webdriver.common.by import By
from dotenv import load_dotenv
import os

load_dotenv()
technologies = os.getenv("TECHNOLOGIES").split(",")


class Basic(scrapy.Spider):
    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        self.driver = webdriver.Chrome()

    def close(self, reason):
        self.driver.close()

    def _parse_resume_details(self, url: str, **kwargs):
        self.driver.get(url)
        try:
            job_description = self.driver.find_element(By.ID, "add_info")
            return job_description.text
        except Exception as e:
            self.logger.error(f"Error extracting job description from {url}: {e}")
            return ""

    @staticmethod
    def get_exchange_rate():
        api_key = os.getenv('API_KEY')
        if not api_key:
            raise ValueError("API key not found in environment variables")
        url = f"https://v6.exchangerate-api.com/v6/{api_key}/latest/USD"
        response = requests.get(url)
        data = response.json()
        return data['conversion_rates']['UAH']

    @staticmethod
    def extract_salary(text):
        if text:
            multiply = False
            if "$" in text:
                multiply = True
            cleaned_text = text.strip().replace('\xa0', ' ')
            pattern = r'\d+\s?\d+\s?'
            match = re.search(pattern, cleaned_text)
            if match and not multiply:
                return int(match.group(0).replace(' ', ''))
            elif match:
                return round(int(match.group(0).replace(' ', '')) * Basic.get_exchange_rate(), 0)
        return None

    @staticmethod
    def clean_text(text):
        if text:
            text = re.sub(r',.*', '', text)
            text = text.replace('\xa0', ' ').strip()
        return text

    def descriptions(self, job_url):
        description = Basic._parse_resume_details(self, job_url).lower()

        tech_found = {}
        for tech in technologies:
            tech_found[tech] = description.find(tech.lower()) != -1
        return tech_found
