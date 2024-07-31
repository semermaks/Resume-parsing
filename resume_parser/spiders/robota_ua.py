import requests
import pandas as pd
from resume_parser.spiders.basic import Basic


def convert_info_to_text(info_list):
    text_parts = []
    for item in info_list:
        text_parts.append(f"{item['position']} at {item['company']} ({item['startDate']} - {item['endDate']}, {item['datesDiff']})")
    return "; ".join(text_parts)


url = "https://employer-api.robota.ua/cvdb/resumes?KeyWords=data%20scientist%20"

response = requests.get(url)
data = response.json()

documents = data.get('documents', [])

resumes = []
for doc in documents:
    resume = {
        "job": doc.get("speciality", ""),
        "name": doc.get("fullName", ""),
        "years": doc.get("age", "")[0:2],
        "cities": doc.get("cityName", ""),
        "salary": Basic.extract_salary(doc.get("salary", "")),
        "info": convert_info_to_text(doc.get("experience", "")),
    }
    resumes.append(resume)

df = pd.DataFrame(resumes, columns=["job", "name", "years", "cities", "salary", "info"])

df.to_csv('robota_ua.csv', index=False, encoding='utf-8-sig')
