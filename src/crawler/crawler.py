from bs4 import BeautifulSoup
import requests


class Police_department:
    headers = {
        'authority': 'api.sail-personalize.com',
        'sec-ch-ua': '"Google Chrome";v="95", "Chromium";v="95", ";Not A Brand";v="99"',
        'x-lib-version': 'v1.0.1',
        'sec-ch-ua-mobile': '?0',
        'authorization': 'Bearer c1d320b4976cc13366759531bf948c3a',
        'content-type': 'application/json',
        'accept': 'application/json',
        'user-agent': 'Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/95.0.4638.69 Safari/537.36',
        'x-referring-url': 'https://projects.propublica.org/nypd-ccrb/search?q=Matthew',
        'sec-ch-ua-platform': '"Linux"',
        'origin': 'https://projects.propublica.org',
        'sec-fetch-site': 'cross-site',
        'sec-fetch-mode': 'cors',
        'sec-fetch-dest': 'empty',
        'referer': 'https://projects.propublica.org/',
        'accept-language': 'ru-RU,ru;q=0.9,en-US;q=0.8,en;q=0.7',
    }

    params = (
        ('pageviews', '9'),
        ('isMobile', '0'),
        ('page', 'q=Matthew'),
        ('visitorId', 'd1775018-91cf-4dd0-b63d-8047c6f43264'),
        ('content',
         'f34d7b53a60083cf80a6023607c20d948f5593e58c2e6b393b03d24efdd64b0630d17ae660218a72664188a446fba9eadead7d12ef0b870cd7bf03b6c85caa1c1bb602ede1cab9b22ce5a80b2a9dbc83744efcc450bd64064b9dcbfb86a237b285ffbbcad6993b9c83e4e387678edc27'),
    )

    def __init__(self, main_url):
        self.main_url = main_url

    def make_request(self, url):
        response = requests.get(url=url)
        return response.text

    def get_object(self):
        response = requests.get('https://api.sail-personalize.com/v1/personalize/simple', headers=self.headers,
                                params=self.params)
        return response

    def search(self):
        pass


    def get_proxy(self):
        url = "https://api.getproxylist.com/proxy?apiKey=f6c61e5fd4f84be48eecb62b8ceed766e7009340&maxConnectTime=1&minUptime=80&protocol=http&allowsHttps=1"

        response = requests.get(url)
        res = response.json()
        ip = res.get('ip')
        port = res.get('port')
        print(ip, port)

        proxy = {
            "http": f"http://{ip}:{port}",
            "https": f"http://{ip}:{port}"
        }
        return proxy

    def get_links(self, url, retries: int = 3):
        while retries > 0:
            retries -= 1
            html = self.make_request(url)
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
                element_url = self.main_url + element_url
                links.append(element_url)
            return links

    def get_soup(self, html):
        return BeautifulSoup(html, "html.parser")

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
            print("This policeman is without a name")
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

    def loop(self):
        links = self.get_links(self.main_url)
        return self.parse_link(links)


if __name__ == "__main__":
    Police_department("https://projects.propublica.org/nypd-ccrb/search?q=Gregory+Smith").loop()
