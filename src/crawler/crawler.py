from typing import List, Tuple

from bs4 import BeautifulSoup
import requests
from models import Info, Complaints, Data

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

        data = []
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
                    precinct = self.get_precinct(soup)
                    units = self.get_units(soup)
                    total_substantiated_allegations = self.get_number_of_substantiated_allegations(soup)
                    total_complaints = self.get_number_of_complaints(soup)
                    total_allegations = self.get_number_of_allegations(soup)

                    date_of_complaint = self.get_date_of_complaint(soup)
                    rank_at_time = self.get_rank_at_time(soup)
                    complainant_info = self.get_complainant_info(soup)
                    # info_about_officer = self.get_info_about_officer(soup)
                    allegation = self.get_allegations(soup)
                    conclusion = self.get_ccrb_conclusion(soup)

                    policemen = Info(link=link, fullname=fullname, appearance=appearance, rank=rank, precinct=precinct,
                                     units=units, total_complaints=total_complaints,
                                     total_allegations=total_allegations,
                                     substantiated_allegations=total_substantiated_allegations)
                    info_about_policeman.append(policemen)

                    complaint = Complaints(date=date_of_complaint, rank_at_time=rank_at_time,
                                           complaint_details=complainant_info, allegations=allegation,
                                           ccrb_conclusion=conclusion)
                    complaints.append(complaint)

                    # result = Data(info=info_about_policeman, complaint=complaints)
                    # data.append(result)
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
    def get_appearance(soup: BeautifulSoup):
        items = soup.find_all("div", class_="fw5 f4-l f5-m f5 lh-title tiempos-text")
        appearance = items[1].text
        return appearance

    @staticmethod
    def get_rank(soup: BeautifulSoup):
        info = soup.find("div", class_="fw5 f4-l f5-m f5 lh-title tiempos-text").text
        if info:
            info = info.split(',')
        rank = info[0].strip()
        return rank

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

    # if info:
    #     info = info.split(',')
    # rank = info[0].strip()

    @staticmethod
    def get_number_of_substantiated_allegations(soup: BeautifulSoup):
        all_divs = soup.find_all("div", class_="f4-l f5 lh-title tiempos-text")
        total_substantiated_allegations = all_divs[3].text
        res = int(total_substantiated_allegations)
        return res

    # todo STARTING POINT FOR COMPLAINTS
    @staticmethod
    def get_date_of_complaint(soup: BeautifulSoup) -> List:
        all_contents = soup.find_all("h2", class_="f4-l f5 color-dark fw7 lh-title tiempos-text pb3")
        date_list = []
        for row in all_contents:
            content = row.text
            date = content[22:]
            date_list.append(date)  # works, but are there any other methods?
        return date_list  # -> todo: List[dates]

    # @staticmethod
    # def get_rank_at_time(soup: BeautifulSoup):
    #     list_of_ranks = []
    #     tables = soup.find_all("table", class_="table medium tablesaw-stack f6 bg")
    #     table_rows = tables.find_all('tr')
    #     for tr in table_rows:
    #         td = [td for td in tr.stripped_strings]
    #         print(td)
    #         # td = tr.find_all('td')
    #         # for i in td:
    #         #     row = i.text
    #     return td


    @staticmethod
    def get_rank_at_time(soup: BeautifulSoup):
        list_of_ranks = []
        tables = soup.find_all("table", class_="table medium tablesaw-stack f6 bg")
        for table in tables:  # тут берет только первую таблицу, а нужно было чтобы всё брал
            all_bodies = table.find_all("tbody")
            for body in all_bodies:
                rows = body.find_all("tr")
                for row in rows:
                    content = row.text
                    all_row = content.splitlines()
                    rank_at_time = all_row[3]
                    list_of_ranks.append(rank_at_time)

            return list_of_ranks

    # @staticmethod
    # def get_rank_at_time(soup: BeautifulSoup):
    #     table = soup.find("table", class_="table medium tablesaw-stack f6 bg")
    #     body = table.find("tbody")
    #     rows = body.find_all("tr")
    #     for row in rows:
    #         content = row.text
    #         whole_row = content.splitlines()
    #         rank_at_time = whole_row[3]
    #     return rank_at_time

    @staticmethod
    def get_complainant_info(soup: BeautifulSoup):
        content = soup.find("table", class_="table medium tablesaw-stack f6 bg")
        body = content.find("tbody")
        rows = body.find_all("tr")
        for row in rows:
            content = row.text
            all_row = content.splitlines()
            complaint_info = all_row[2]
            return complaint_info

    @staticmethod
    def get_info_about_officer(soup: BeautifulSoup, self=None):
        content = soup.find("div", class_="mb5")
        a = content.find("a")
        url_of_element = a.get("href")
        response = self.make_request(url_of_element)
        print(response)  # no response

    @staticmethod
    def get_allegations(soup: BeautifulSoup):
        content = soup.find("table", class_="table medium tablesaw-stack f6 bg")
        body = content.find("tbody")
        rows = body.find_all("tr")
        for row in rows:
            content = row.text
            all_row = content.splitlines()
            allegation = all_row[1]
            return allegation

    @staticmethod
    def get_ccrb_conclusion(soup: BeautifulSoup):
        content = soup.find("table", class_="table medium tablesaw-stack f6 bg")
        body = content.find("tbody")
        rows = body.find_all("tr")
        for row in rows:
            content = row.text
            all_row = content.splitlines()
            conclusion = all_row[4]
            return conclusion


if __name__ == "__main__":
    result = Crawler().get_info("Sasha Rosen")
    print(result)

    # Sasha Rosen
