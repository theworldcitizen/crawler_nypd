from bs4 import BeautifulSoup
import requests

BASE_URL = "https://projects.propublica.org"


class Police_department:

    def make_request(self, url: str, params: dict = None):
        response = requests.get(BASE_URL + url, params=params)
        if response.ok:
            return response.text

    def get_soup(self, html):
        response = BeautifulSoup(html, "html.parser")
        return response

    def get_info(self, fullname: str):
        params = {'q': fullname}
        response = self.make_request("/nypd-ccrb/search", params)
        links = self.get_links(response)
        return self.parse_link(links)

    def get_links(self, html, retries: int = 3):
        while retries > 0:
            retries -= 1

            soup = BeautifulSoup(html, "html.parser")

            links = []
            all_links = soup.find("div", class_="pr3-ns pt3 w-70-l w-100").find("ul")
            if all_links:
                li = all_links.find_all("li")
            else:
                continue

            for element in li:
                a = element.find("a")
                element_url = a.get("href")
                element_url =  element_url
                links.append(element_url)

            return links

    def parse_link(self, links: list):
        result = []
        if links:
            for link in links:
                html = self.make_request(link)
                soup = self.get_soup(html)
                fullname = self.get_fullname(soup)
                if fullname is not None:
                    description = self.get_description(soup)

                    res = {
                        'fullname': fullname,
                        'description': description,
                        'link': link
                    }
                    result.append(res)
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
        desc_list = []
        for desc in description:
            short_description = desc.text
            desc_list.append(short_description)
        result = ''.join(desc_list)
        return result


if __name__ == "__main__":
    result = Police_department().get_info("Matthew")
    print(result)

