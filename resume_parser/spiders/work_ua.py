import scrapy
from scrapy.http import Response

from resume_parser.spiders.basic import Basic


class WorkUaSpider(Basic):
    name = "work_ua"
    allowed_domains = ["work.ua"]
    start_urls = ["https://www.work.ua/resumes-data+scientist/"]

    def parse(self, response: Response, **kwargs):
        for resume in response.css("div.card-search"):
            arr = resume.css("p.mt-xs.mb-0 span::text").getall()
            if len(arr) > 0:
                if len(arr) == 2:
                    years = None
                    cities = arr[1]
                elif arr[1][0:2] == "\n " and len(arr) == 6:
                    years = int(arr[4][0:2])
                    cities = arr[5]
                elif arr[1][0:2] == "\n " and len(arr) == 5:
                    years = None
                    cities = arr[4]
                else:
                    years = int(arr[1][0:2])
                    cities = arr[2]
                salary = resume.css("p.h5.strong-600.mt-xs.mb-0.nowrap::text").get()
                salary = self.extract_salary(salary)
                info = resume.css("p.mb-0.overflow.wordwrap::text").get()
                if info is None:
                    info = self.clean_text(
                        "".join(resume.css("ul.mt-lg.mb-0 li::text").getall())
                        + "".join(resume.css("ul.mt-lg.mb-0 li span::text").getall())
                    )
                # tech_found = self.descriptions(response.urljoin(resume.css("h2.mt-0 a::attr(href)").get()))
                yield {
                    "job": resume.css("h2.mt-0 a::text").get(),
                    "name": arr[0],
                    "years": years,
                    "cities": cities,
                    "salary": salary,
                    "info": info,
                    # **tech_found
                }

        next_page = response.css(".pagination>li")[-1].css("a::attr(href)").get()
        if next_page is not None:
            next_page_url = response.urljoin(next_page)
            yield scrapy.Request(next_page_url, callback=self.parse, dont_filter=True)
