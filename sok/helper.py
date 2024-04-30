from datetime import datetime
import requests
import bs4
from time import sleep
from pathlib import Path

header = {
    'User-Agent': 'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_10_1) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/39.0.2171.95 Safari/537.36'}

current_date = datetime.today().strftime('%Y-%m-%d')

path_base = Path(__file__).parent.resolve().as_posix() + '/'


def connect(url: str) -> requests.Response:
    done = False
    while not done:
        try:
            r = requests.get(url, headers=header)
            done = True
            print(f'connection successful for {url}')
        except requests.exceptions.ConnectionError:
            status_code = "Connection refused"
            sleep(3)
            print(status_code, url)
    return r


def get_content(url: str) -> bs4.BeautifulSoup:
    page = connect(url)
    return bs4.BeautifulSoup(page.content, "html.parser")


def create_directory():
    from pathlib import Path

    Path(path_base + "data").mkdir(parents=True, exist_ok=True)