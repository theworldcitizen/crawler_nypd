import requests


class Proxy:

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
