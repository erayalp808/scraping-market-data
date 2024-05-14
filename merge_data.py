import pandas as pd
import numpy as np
from datetime import date
from pathlib import Path


current_date = date.today()
daily_data = pd.DataFrame(columns=[
    "main_category",
    "sub_category",
    "lowest_category",
    "name",
    "price",
    "high_price",
    "in_stock",
    "product_link",
    "page_link",
    "date"
])
spiders = ["migros", "carrefour", "sokmarket", "mopas", "marketpaketi"]

for spider in spiders:
    market_data = pd.read_csv(f"market_scraper/data/{spider}_{current_date}.csv")
    daily_data = pd.concat([daily_data, market_data], axis=0, ignore_index=True)

path_base = Path(__file__).parent.resolve().as_posix() + "/"

Path(path_base + "market_scraper/data/merged_data").mkdir(parents=True, exist_ok=True)

path_file = f"{path_base}market_scraper/data/merged_data/market_data_{current_date}.csv"

daily_data.to_csv(path_file, index=False)
