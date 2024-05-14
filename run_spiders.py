import os


os.chdir(os.path.dirname(os.path.abspath(__file__)))
os.chdir("market_scraper")
os.makedirs("data", exist_ok=True)
os.chdir("data")

spiders = ["migros", "carrefour", "mopas", "sokmarket", "marketpaketi"]

for spider in spiders:
    os.system(f"scrapy crawl {spider}")

os.chdir(os.path.dirname(os.path.abspath(__file__)))
os.system("python merge_data.py")
