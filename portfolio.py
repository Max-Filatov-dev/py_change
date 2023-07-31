import requests
import json

cash_usd = 4427.77
cash_rub = 62174.91 + 43297.08 + 91735 + 10448.6 + 472033
total_cash = cash_usd + cash_rub

portfolio = {
    "usa": {
        "msft": (1, 309.47),
        "crm": (3, 228.88),
        "vrt": (10, 16.7),
        "sq": (2, 111.88),
        "crwd": (1, 173.25),
        "med": (1, 193.9),
        "ntnx": (16, 28.45),
        "pypl": (6, 151.21),
        "tsm": (5, 119.46),
        "vrtx": (6, 183.79),
    },
    "rus": {
        "irao": (21900, 4.15),
        "gmkn": (4, 19410),
        "phor": (17, 2377),
        "upro": (30000, 1.829),
    },
}

# ------ 2022 ---------
old_year = 1_627_327

# ------ 1.07.2023 -------
old_month = 1_890_825
cur_month = 1_890_825


def get_usd_rub():
    """ """
    url = "https://iss.moex.com/iss/engines/currency/markets/selt/boards/CETS/securities/USD000UTSTOM/.json?iss.meta=off&group_by=type&securities.columns=PREVPRICE&marketdata.columns=LAST,CHANGE,LASTTOPREVPRICE"

    answer = requests.get(url)
    new_vals = json.loads(answer.content)
    cur_market = new_vals["marketdata"]["data"][0][0]
    return cur_market if cur_market else new_vals["securities"]["data"][0][0]


def short_valume():
    """ """
    short_usa = sum(
        [sh_us[0] * sh_us[1] for sh_us in portfolio["usa"].values() if sh_us[0] < 0]
    )
    short_rus = sum(
        [sh_ru[0] * sh_ru[1] for sh_ru in portfolio["rus"].values() if sh_ru[0] < 0]
    )


def get_price(*, country: str, ticker: str):
    """ """
    if country == "rus":
        url_rus = f"https://iss.moex.com/iss/engines/stock/markets/shares/boards/tqbr/securities/{ticker}/.json?iss.meta=off&group_by=type&securities.columns=SECID%2CSHORTNAME%2CISIN%2CPREVPRICE%2CPREVDATE&marketdata.columns=LAST%2CCHANGE%2CLASTTOPREVPRICE%2CUPDATETIME%2CSYSTIME"

        resp_moex = requests.get(url=url_rus)
        data_rus = resp_moex.json()
        change_rus = data_rus["marketdata"]["data"][0][1] * portfolio["rus"][ticker][0]
        print(f"{ticker.upper():<5} {'+' if change_rus > 0 else ''}{round(change_rus)}")
        return change_rus

    elif country == "usa":
        usd_rub = get_usd_rub()
        url_usa = f"https://query2.finance.yahoo.com/v6/finance/quoteSummary/{ticker}?modules=price"
        USER_AGENT = "Mozilla/5.0 (Windows NT 10.0; WOW64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/54.0.2840.99 Safari/537.36"

        header = {
            "Connection": "keep-alive",
            "Expires": "-1",
            "Upgrade-Insecure-Requests": "1",
            "User-Agent": USER_AGENT,
        }
        resp_yahoo = requests.get(url=url_usa, headers=header)
        data_usa = resp_yahoo.json()
        change_usa = (
            data_usa["quoteSummary"]["result"][0]["price"]["regularMarketChange"].get(
                "raw"
            )
            * portfolio["usa"][ticker][0]
            * usd_rub
        )
        print(f"{ticker.upper():<5} {'+' if change_usa > 0 else ''}{round(change_usa)}")
        return change_usa


# def change_month_year(today_val: int):
#     """ """
#     change_month = round(today_val - old_month)
#     change_month_perc = round((today_val / old_month - 1) * 100, 2)
#     total_val = None

#     if change_month > 0:
#         change_month = f"\033[32m+{change_month:_}\033[0m"
#         change_month_perc = f"\033[32m+{change_month_perc:_} % \033[0m"
#     elif change_month < 0:
#         change_month = f"\033[31m{change_month:_}\033[0m"
#         change_month_perc = f"\033[31m{change_month_perc:_} % \033[0m"

#     change_year = round(today_val - old_year)
#     change_year_perc = round((today_val / old_year - 1) * 100, 2)

#     if change_year > 0:
#         change_year = f"\033[32m+{change_year:_}\033[0m"
#         change_year_perc = f"\033[32m+{change_year_perc:_} % \033[0m"
#         total_val = f"\033[32m{today_val:_}\033[0m"
#     elif change_year < 0:
#         change_year = f"\033[31m{change_year:_}\033[0m"
#         change_year_perc = f"\033[31m{change_year_perc:,} % \033[0m"
#         total_val = f"\033[31m{today_val:_}\033[0m"

#     print(
#         f"\nMonth: {change_month} {change_month_perc} YTD: {change_year} {change_year_perc}\n{'='*45}\nTotal: {total_val}\n"
#     )


if __name__ == "__main__":
    # change_month_year(today_val=today_value)
    total_change = 0
    for coun in portfolio:
        print(f"{coun.upper()}\n{'-'*15}")
        tmp_change = 0
        for tick in portfolio[coun]:
            resp_tick = get_price(country=coun, ticker=tick)
            tmp_change += resp_tick if resp_tick else 0
        print(
            f"{'-'*15}\n{coun.upper()}: {'+' if tmp_change > 0 else ''}{round(tmp_change)}\n"
        )
        total_change += tmp_change
    print(f"{'-'*15}\nTotal: {'+' if total_change > 0 else ''}{round(total_change)}\n")
