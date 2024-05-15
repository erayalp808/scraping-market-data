import traceback
import pandas as pd
import numpy as np
from datetime import date
from pathlib import Path


current_date = date.today()
columns = [
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
]
dtypes = {
    "main_category": str,
    "sub_category": str,
    "lowest_category": str,
    "name": str,
    "price": float,
    "high_price": float,
    "in_stock": bool,
    "product_link": str,
    "page_link": str,
    "date": str
}
daily_data = pd.DataFrame(columns=columns)

for column, dtype in dtypes.items():
    daily_data[column] = daily_data[column].astype(dtype)

spiders = ["migros", "carrefour", "mopas", "marketpaketi", "sokmarket"]

for spider in spiders:
    try:
        market_data = pd.read_csv(f"market_scraper/data/{spider}_{current_date}.csv")
        daily_data = pd.concat([daily_data, market_data], axis=0, ignore_index=True)
        print(f"{spider}_{current_date}.csv merged successfully")
    except:
        traceback.print_exc()

path_base = Path(__file__).parent.resolve().as_posix() + "/"

Path(path_base + "market_scraper/data/merged_data").mkdir(parents=True, exist_ok=True)

path_file = f"{path_base}market_scraper/data/merged_data/market_data_{current_date}.csv"

daily_data.to_csv(path_file, index=False)
