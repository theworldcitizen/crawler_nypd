#
#
# def main():
#     links = return_links()
#     for link in links:
#         res = parse_link(link)
#
# def return_links():
#     #make_request
#     #link of oficers
#     pass
#
# def parse_link():
#     # get name
#     # get descrip
#     detail_links = get_more_details()
#     complaints = parse_complaints(detail_links)
#     res = {
#
#     }
#
# def get_more_details(soup: BeautifulSoup) -> list:
#     list_of_more_details = []
#     elements = soup.find_all("div", class_="mb5")
#     for element in elements:
#         a = element.find("a")
#         url_of_element = a.get("href")
#         list_of_more_details.append(url_of_element)
#         # complaints_for_period = []
#         # for link in more_details:
#         #     response = self.make_request(link)
#         #     complaints_for_period.append(response)
#     return list_of_more_details
#
# def parse_complaints(links: str):