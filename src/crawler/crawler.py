from typing import List

from bs4 import BeautifulSoup
import requests
from models import User

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

    def parse_link(self, links: list) -> List[User]:
        result = []
        if links:
            for link in links:
                html = self.make_request(link)
                soup = self.get_soup(html)
                fullname = self.get_fullname(soup)
                if fullname is not None:
                    description = self.get_description(soup)
                    user = User(fullname=fullname, description=description, link=link)
                    result.append(user)
        return result

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


if __name__ == "__main__":
    result = Crawler().get_info("Matthew")
    print(result)
