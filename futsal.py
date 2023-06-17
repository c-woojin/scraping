import csv
import time

import requests

url: str = "https://map.naver.com/v5/api/search"
headers: dict = {
    "User-Agent": "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/113.0.0.0 Safari/537.36",
    "Referer": "https://map.naver.com/",
}
params: dict = dict(
    caller="pcweb",
    query="풋살장",
    type="place",
    searchCoord="126.92230604042447;37.55050794649084",
    page="1",
    displayCount="20",
    boundary="126.72458516926054;37.403033175604605;127.31446551165061;37.67730950413737",
    lang="ko",
)

f = open('futsal.csv', 'w', newline='')
wr = csv.writer(f)
i = 1

while True:
    response: requests.Response = requests.get(url, params=params, headers=headers)
    data: dict = response.json()
    if data.get("error"):
        print(data["error"])
        break

    places: list = data["result"]["place"]["list"]

    for place in places:
        wr.writerow(
            [
                i,
                place["name"],
                place["address"],
                place["roadAddress"],
                place["category"],
                place["homePage"],
                place["tel"],
            ]
        )
        i += 1

    params["page"] = str(int(params["page"]) + 1)
    time.sleep(1)

f.close()
