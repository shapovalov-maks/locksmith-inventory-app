import requests
from bs4 import BeautifulSoup
import csv
import time

BASE_URL = "https://transpondery.com"

# Пример машин для сбора (можно расширить)
vehicles = [
    {"make": "Honda", "model": "Civic", "year": 2017},
    {"make": "Toyota", "model": "Camry", "year": 2018},
    {"make": "Ford", "model": "F-150", "year": 2016},
]

headers = {
    "User-Agent": "Mozilla/5.0"
}

output = []

for vehicle in vehicles:
    make = vehicle["make"].lower()
    model = vehicle["model"].lower().replace(" ", "-")
    year = str(vehicle["year"])

    url = f"{BASE_URL}/by-vehicle/{make}/{model}/{year}/"
    print(f"Scraping: {url}")

    response = requests.get(url, headers=headers)
    if response.status_code != 200:
        print(f"Failed to fetch {url}")
        continue

    soup = BeautifulSoup(response.text, "html.parser")
    table = soup.find("table")

    if not table:
        print(f"No data for {make} {model} {year}")
        continue

    rows = table.find_all("tr")
    headers_row = [th.text.strip() for th in rows[0].find_all("th")]

    for row in rows[1:]:
        cols = [td.text.strip() for td in row.find_all("td")]
        data = dict(zip(headers_row, cols))
        data["Make"] = vehicle["make"]
        data["Model"] = vehicle["model"]
        data["Year"] = vehicle["year"]
        output.append(data)

    time.sleep(1)  # Не спамим сайт

# Запись в CSV
filename = "transpondery_keys.csv"
with open(filename, "w", newline="", encoding="utf-8") as f:
    if output:
        writer = csv.DictWriter(f, fieldnames=output[0].keys())
        writer.writeheader()
        writer.writerows(output)

print(f"✅ Done! Data saved to {filename}")
