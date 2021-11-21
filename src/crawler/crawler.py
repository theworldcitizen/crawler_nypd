from typing import List

from bs4 import BeautifulSoup
import requests
from models import Info, Complaints

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

    def get_info(self, fullname: str):
        params = {'q': fullname}
        html = self.make_request("/nypd-ccrb/search", params)
        links = self.get_links(html)
        return self.parse_link(links)

    def get_links(self, html, retries: int = 3):
        while retries > 0:
            retries -= 1

            soup = self.get_soup(html)

            links = []
            all_links = soup.find("div", class_="pr3-ns pt3 w-70-l w-100").find("ul")
            if all_links:
                li = all_links.find_all("li")
            else:
                continue

            for element in li:
                a = element.find("a")
                element_url = a.get("href")
                element_url = element_url
                links.append(element_url)

            return links

    def parse_link(self, links: list) -> tuple[list[Info], list[Complaints]]:
        info_about_policeman = []
        complaints = []
        if links:
            for link in links:
                html = self.make_request(link)
                soup = self.get_soup(html)
                fullname = self.get_fullname(soup)
                if fullname is not None:
                    # description = self.get_description(soup)
                    link = BASE_URL + link
                    rank = self.get_rank(soup)
                    appearance = self.get_appearance(soup)
                    # precinct = self.get_precinct(soup)
                    units = self.get_units(soup)
                    total_substantiated_allegations = self.get_number_of_substantiated_allegations(soup)
                    total_complaints = self.get_number_of_complaints(soup)
                    total_allegations = self.get_number_of_allegations(soup)

                    date_of_complaint = self.get_date_of_complaint(soup)
                    # rank_at_time = self.get_rank_at_time(soup)
                    complainant_info = self.get_complainant_info(soup)

                    policemen = Info(link=link, fullname=fullname, appearance=appearance, rank=rank,
                                     units=units, total_complaints=total_complaints,
                                     total_allegations=total_allegations,
                                     substantiated_allegations=total_substantiated_allegations)
                    info_about_policeman.append(policemen)

                    complaint = Complaints(date=date_of_complaint, officer_details=complainant_info)
                    complaints.append(complaint)
        return info_about_policeman, complaints

    @staticmethod
    def get_fullname(soup: BeautifulSoup):
        try:
            fullname = soup.find("div", class_="fw7 f2-l f4-m f5 lh-title tiempos-text").text
        except AttributeError:
            print("Fullname wasn't found")
            return None
        return fullname

    @staticmethod
    def get_description(soup: BeautifulSoup):
        description = soup.find("div", class_="f5 mw7 tiempos-text pt3")
        description_list = []
        for desc in description:
            short_description = desc.text
            description_list.append(short_description)
        result = ''.join(description_list)
        return result

    @staticmethod
    def get_appearance(soup: BeautifulSoup):
        items = soup.find_all("div", class_="fw5 f4-l f5-m f5 lh-title tiempos-text")
        appearance = items[1].text
        return appearance

    @staticmethod
    def get_rank(soup: BeautifulSoup):
        empty_list = []
        info = soup.find("div", class_="fw5 f4-l f5-m f5 lh-title tiempos-text").text
        empty_list.append(info)
        # rank = [full_info(' ').pop(0) for full_info in empty_list]
        rank = empty_list[-1]
        return rank  # todo: get the 1st element

    @staticmethod
    def get_precinct(soup: BeautifulSoup):
        try:
            full_info = soup.find("div", class_="fw5 f4-l f5-m f5 lh-title tiempos-text")
            a = full_info.find('a')
            precinct = a.text
            return precinct  # todo some has precinct, but others do not
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
        return total_complaints

    @staticmethod
    def get_number_of_allegations(soup: BeautifulSoup):
        all_divs = soup.find_all("div", class_="f4-l f5 lh-title tiempos-text")
        total_allegations = all_divs[2].text
        return total_allegations

    @staticmethod
    def get_number_of_substantiated_allegations(soup: BeautifulSoup):
        all_divs = soup.find_all("div", class_="f4-l f5 lh-title tiempos-text")
        total_substantiated_allegations = all_divs[3].text
        return total_substantiated_allegations

    @staticmethod
    def get_date_of_complaint(soup: BeautifulSoup):
        content = soup.find("h2", class_="f4-l f5 color-dark fw7 lh-title tiempos-text pb3").text
        date = content[22:]  # works, but are there any other methods?
        return date

    @staticmethod
    def get_rank_at_time(soup: BeautifulSoup):
        complaint_details = []
        data = soup.find("div", class_="pr4 pb3 w-100").find("table",
                                                             class_="table medium tablesaw-stack f6 bg tablesaw-sortable").find(
            "tbody")

        content = data.find_all("tr").text
        complaint_details.append(content)
        return complaint_details  # todo: path is wrong

    @staticmethod
    def get_complainant_info(soup: BeautifulSoup):
        content = soup.find("div", class_="pr4 pb3 w-100").find("table").find("tbody").find_all("tr")
        for item in content:
            result = item.find("span", class_="tablesaw-cell-content").text
            return result #todo: path is wrong


if __name__ == "__main__":
    result = Crawler().get_info("Ruslan")
    print(result)
