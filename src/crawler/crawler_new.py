from typing import List, Tuple

from bs4 import BeautifulSoup
import requests
from models import Info, Complaint, Data

BASE_URL = "https://projects.propublica.org"


class Crawler:
    headers = {
        'authority': 'projects.propublica.org',
        'sec-ch-ua': '"Google Chrome";v="95", "Chromium";v="95", ";Not A Brand";v="99',
        'sec-ch-ua-platform': '"Linux"',
        'upgrade-insecure-requests': '1',
        'user-agent': 'Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/95.0.4638.69 Safari/537.36',
        'accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,image/avif,image/webp,image/apng,*/*;q=0.8,application/signed-exchange;v=b3;q=0.9',
        'sec-fetch-site': 'same-origin',
        'sec-fetch-mode': 'navigate',
        'sec-fetch-dest': 'document',
        'referer': 'https://projects.propublica.org/',
        'accept-language': 'ru-RU,ru;q=0.9,en-US;q=0.8,en;q=0.7',

    }

    def make_request(self, url: str, params: dict = None):
        response = requests.get(BASE_URL + url, params=params, headers=self.headers)
        if response.ok:
            return response.text

    def get_soup(self, html) -> None:
        soup = BeautifulSoup(html, "html.parser")
        return soup

    def get_main_page(self, fullname: str):
        params = {'q': fullname}
        html = self.make_request("/nypd-ccrb/search", params)
        links = self.get_links(html)
        return self.parse_main_page_of_officer(links, fullname)

    def get_links(self, html, retries: int = 3):  # собираем все совпадения
        while retries > 0:
            retries -= 1

            soup = self.get_soup(html)

            fullname_with_link = []
            all_links = soup.find("div", class_="pr3-ns pt3 w-70-l w-100").find("ul")
            if all_links:
                li = all_links.find_all("li")
            else:
                continue

            for element in li:
                a = element.find("a")
                fullname = a.text
                element_url = a.get("href")
                element_url = element_url
                fullname_with_link.append({'fullname': fullname, 'link': element_url})

            return fullname_with_link

    def parse_main_page_of_officer(self, fullname_with_link: list, fullname_from_request: str):
        info_about_policeman = []

        if fullname_with_link:
            for link in fullname_with_link:
                url = link.get('link')
                fullname = link.get('fullname')
                if fullname.lower() != fullname_from_request.lower():
                    continue
                html = self.make_request(url)
                soup = self.get_soup(html)
                fullname = self.get_fullname(soup)

                if fullname is not None:
                    link = link
                    rank = self.get_rank(soup)
                    appearance = self.get_appearance(soup)
                    precinct = self.get_precinct(soup)
                    units = self.get_units(soup)
                    total_complaints = self.get_number_of_complaints(soup)
                    total_allegations = self.get_number_of_allegations(soup)
                    total_substantiated_allegations = self.get_number_of_substantiated_allegations(soup)

                    policemen = Info(link=link, fullname=fullname, appearance=appearance, rank=rank, precinct=precinct,
                                     units=units, total_complaints=total_complaints,
                                     total_allegations=total_allegations,
                                     substantiated_allegations=total_substantiated_allegations)
                    info_about_policeman.append(policemen)
        return info_about_policeman

    @staticmethod
    def get_fullname(soup: BeautifulSoup):
        try:
            fullname = soup.find("div", class_="fw7 f2-l f4-m f5 lh-title tiempos-text").text
        except AttributeError:
            print("Fullname wasn't found")
            return None
        return fullname

    @staticmethod
    def get_rank(soup: BeautifulSoup):
        info = soup.find("div", class_="fw5 f4-l f5-m f5 lh-title tiempos-text").text
        if info:
            info = info.split(',')
        rank = info[0].strip()
        return rank

    @staticmethod
    def get_appearance(soup: BeautifulSoup):
        items = soup.find_all("div", class_="fw5 f4-l f5-m f5 lh-title tiempos-text")
        appearance = items[1].text
        return appearance

    @staticmethod
    def get_precinct(soup: BeautifulSoup):
        try:
            full_info = soup.find("div", class_="fw5 f4-l f5-m f5 lh-title tiempos-text")
            a = full_info.find('a')
            precinct = a.text
            return precinct  # todo: some has precinct, but others do not
        except Exception as e:
            print("Precinct wasn't found")

    @staticmethod
    def get_units(soup: BeautifulSoup) -> List:
        units = []
        all_units = soup.find("div", class_="f4-l f5 lh-title tiempos-text").text
        units.append(all_units)
        return units

    @staticmethod
    def get_number_of_complaints(soup: BeautifulSoup):
        all_divs = soup.find_all("div", class_="f4-l f5 lh-title tiempos-text")
        total_complaints = all_divs[1].text
        res = int(total_complaints)
        return res

    @staticmethod
    def get_number_of_allegations(soup: BeautifulSoup):
        all_divs = soup.find_all("div", class_="f4-l f5 lh-title tiempos-text")
        total_allegations = all_divs[2].text
        res = int(total_allegations)
        return res

    @staticmethod
    def get_number_of_substantiated_allegations(soup: BeautifulSoup):
        all_divs = soup.find_all("div", class_="f4-l f5 lh-title tiempos-text")
        total_substantiated_allegations = all_divs[3].text
        res = int(total_substantiated_allegations)
        return res

    @staticmethod
    def get_more_details(soup: BeautifulSoup) -> list:
        list_of_more_details = []
        elements = soup.find_all("div", class_="mb5")
        for element in elements:
            a = element.find("a")
            url_of_element = a.get("href")
            list_of_more_details.append(url_of_element)
        return list_of_more_details

    def parse_more_details(self, list_of_more_details: list):
        complaints = []
        if list_of_more_details:
            for link in list_of_more_details:
                html = self.make_request(link)
                soup = self.get_soup(html)

                content = soup.find_all("table", class_="table medium tablesaw-stack f6 tablesaw-sortable").find(
                    "tbody")
                rows = content.find_all("tr")

                for row in rows:
                    content = row.text
                    all_row = content.splitlines()
                    name_of_officer = all_row[0]
                    if name_of_officer == self.get_fullname():
                        date = self.get_date_of_complaint(soup)
                        rank_at_the_time_of_incident = self.get_rank_at_time(soup)
                        officer_details = self.get_info_about_officer(soup)
                        complainant_details = self.get_info_about_complainant(soup)
                        allegations = self.get_allegations(soup)
                        conclusion = self.get_ccrb_conclusion(soup)

                        complaint = Complaint(date=date, rank_at_time=rank_at_the_time_of_incident,
                                              officer_details=officer_details,
                                              complaint_details=complainant_details, allegations=allegations,
                                              ccrb_conclusion=conclusion)

                        complaints.append(complaint)
        return complaints

    def get_info(self):
        result = []
        main_page = self.get_main_page('Sasha Rosen')
        more_details = self.get_more_details()
        parse_more_details = self.parse_more_details(more_details)

        data = Data(info=main_page, complaint=parse_more_details)
        result.append(data)
        return result

    @staticmethod
    def get_date_of_complaint(soup: BeautifulSoup):
        content = soup.find("div", class_="fw7 f2-l f4-m f5 lh-title tiempos-text").text
        date_of_complaint = content[22:]
        return date_of_complaint

    @staticmethod
    def get_rank_at_time(soup: BeautifulSoup):
        content = soup.find("table", class_="table medium tablesaw-stack f6 tablesaw-sortable").find("tbody")
        rows = content.find_all("tr")
        for row in rows:
            content = row.text
            all_row = content.splitlines()
            rank_at_the_time = all_row[2]
            return rank_at_the_time

    @staticmethod
    def get_info_about_officer(soup: BeautifulSoup):
        content = soup.find("table", class_="table medium tablesaw-stack f6 tablesaw-sortable").find("tbody")
        rows = content.find_all("tr")
        for row in rows:
            content = row.text
            all_row = content.splitlines()
            info_about_officer = all_row[3]
            return info_about_officer

    @staticmethod
    def get_info_about_complainant(soup: BeautifulSoup):
        content = soup.find("table", class_="table medium tablesaw-stack f6 tablesaw-sortable").find("tbody")
        rows = content.find_all("tr")
        for row in rows:
            content = row.text
            all_row = content.splitlines()
            info_about_complainant = all_row[4]
            return info_about_complainant

    @staticmethod
    def get_allegations(soup: BeautifulSoup):
        content = soup.find("table", class_="table medium tablesaw-stack f6 tablesaw-sortable").find("tbody")
        rows = content.find_all("tr")
        for row in rows:
            content = row.text
            all_row = content.splitlines()
            allegations = all_row[5]
            return allegations

    @staticmethod
    def get_ccrb_conclusion(soup: BeautifulSoup):
        content = soup.find("table", class_="table medium tablesaw-stack f6 tablesaw-sortable").find("tbody")
        rows = content.find_all("tr")
        for row in rows:
            content = row.text
            all_row = content.splitlines()
            conclusion = all_row[6]
            return conclusion

if __name__ == "__main__":
    result = Crawler().get_info()
    print(result)

