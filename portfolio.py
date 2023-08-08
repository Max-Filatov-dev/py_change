import requests
import json
import os
from datetime import datetime

def get_usd_rub() -> int:
    """ """
    url = "https://iss.moex.com/iss/engines/currency/markets/selt/boards/CETS/securities/USD000UTSTOM/.json?iss.meta=off&group_by=type&securities.columns=PREVPRICE&marketdata.columns=LAST,CHANGE,LASTTOPREVPRICE"

    answer = requests.get(url)
    new_vals = json.loads(answer.content)
    cur_market = new_vals["marketdata"]["data"][0][0]
    return cur_market if cur_market else new_vals["securities"]["data"][0][0]

usd_rub = get_usd_rub()
# ------ 2022 ---------
old_year = 1_627_327

finam_rub = 62174.91 + 43297.08
alor_rub = -380
vtb_rub = 10448.6
alpha_rub = 472033

cash_usd = 4427.77
cash_rub = finam_rub + alor_rub + vtb_rub + alpha_rub

portfolio = {
    "usa": {
        "msft": (2, 309.47),
        "crm": (3, 228.88),
        "vrt": (35, 16.7),
        "sq": (2, 111.88),
        "crwd": (1, 173.25),
        "med": (1, 193.9),
        "ntnx": (16, 28.45),
        "pypl": (6, 151.21),
        "tsm": (5, 119.46),
        "vrtx": (6, 183.79),
    },
    "rus": {
        "mgnt": (-15, 5779),
        "gmkn": (4, 19410),
        "phor": (17, 2377),
        "upro": (30000, 1.829),
        "yndx": (36, 40.58 * usd_rub),
    },
}


def save_value_port(port: tuple):
    """ """
    today = datetime.today()
    path_value_port = f"value_port/{today.year}.json"

    if not os.path.isfile(path_value_port):
        with open(path_value_port, "w") as vl_save:
            json.dump({str(today.date()): port}, vl_save, indent=4)

    elif os.path.isfile(path_value_port):
        with open(path_value_port) as vl_load:
            value_port = json.load(vl_load)

        value_port.update({str(today.date()): port})

        with open(path_value_port, "w") as vl_new_save:
            json.dump(value_port, vl_new_save, indent=4)


def short_valume():
    """ """
    short_usa = sum(
        [sh_us[0] * sh_us[1] for sh_us in portfolio["usa"].values() if sh_us[0] < 0]
    )
    short_rus = sum(
        [sh_ru[0] * sh_ru[1] for sh_ru in portfolio["rus"].values() if sh_ru[0] < 0]
    )


def get_data_usa(*, ticker: str, action: str, show: bool = True):
    """ """
    # usd_rub = get_usd_rub()
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
    change_usa = data_usa["quoteSummary"]["result"][0]["price"][
        "regularMarketChange"
    ].get("raw", None)
    last_price_usa = data_usa["quoteSummary"]["result"][0]["price"][
        "regularMarketPrice"
    ].get("raw", None)
    if action == "change" and change_usa:
        change_usa_rub = change_usa * portfolio["usa"][ticker][0] * usd_rub
        change_usa_str = f"{'+' if change_usa_rub > 0 else ''}{round(change_usa_rub)}"
        print(f"{ticker.upper():<5} {change_usa_str}") if show else None
        return change_usa_rub
    elif action == "price" and last_price_usa:
        ticker_usa_value = portfolio["usa"][ticker][0] * last_price_usa * usd_rub
        return ticker_usa_value


def get_data_rus(*, ticker: str, action: str, show: bool = True):
    """ """
    url_rus = f"https://iss.moex.com/iss/engines/stock/markets/shares/boards/tqbr/securities/{ticker}/.json?iss.meta=off&group_by=type&securities.columns=SECID%2CSHORTNAME%2CISIN%2CPREVPRICE%2CPREVDATE&marketdata.columns=LAST%2CCHANGE%2CLASTTOPREVPRICE%2CUPDATETIME%2CSYSTIME"

    resp_moex = requests.get(url=url_rus)
    data_rus = resp_moex.json()
    change_rus = data_rus["marketdata"]["data"][0][1]
    last_price_rus = data_rus["marketdata"]["data"][0][0]
    if action == "change" and change_rus:
        result_chage_rus = change_rus * portfolio["rus"][ticker][0]
        change_rus_str = f"{'+' if change_rus > 0 else ''}{round(result_chage_rus)}"
        print(f"{ticker.upper():<5} {change_rus_str}") if show else None
        return result_chage_rus
    elif action == "price" and last_price_rus:
        ticker_rus_value = portfolio["rus"][ticker][0] * last_price_rus
        return ticker_rus_value


def format_str(data: dict):
    """ """
    check_none_change = [(t, v) for c in data for t, v in data[c].items() if v is None]
    if check_none_change:
        return dict(check_none_change)
    else:
        usa_value = sum([us for us in data["usa"].values()])
        rus_value = sum([ru for ru in data["rus"].values()])
        total_value = usa_value + rus_value
        usa_str = f"{'+' if usa_value > 0 else ''}{usa_value}"
        rus_str = f"{'+' if rus_value > 0 else ''}{rus_value}"
        total_str = f"{'+' if total_value > 0 else ''}{total_value}"
        return {"usa": usa_str, "rus": rus_str, "today": total_str}


def get_change():
    """ """
    total_change = {"usa": {}, "rus": {}}
    for coun_ch in portfolio:
        for tick_ch in portfolio[coun_ch]:
            if coun_ch == "usa":
                change_ticker_usa = get_data_usa(
                    ticker=tick_ch, action="change", show=False
                )
                total_change[coun_ch].update(
                    {tick_ch: round(change_ticker_usa) if change_ticker_usa else None}
                )
            elif coun_ch == "rus":
                change_ticker_rus = get_data_rus(
                    ticker=tick_ch, action="change", show=False
                )
                total_change[coun_ch].update(
                    {tick_ch: round(change_ticker_rus) if change_ticker_rus else None}
                )
    return format_str(data=total_change)


def get_last_price():
    """ """
    last_price, usd_rub = {"usa": {}, "rus": {}}, get_usd_rub()
    for coun_pr in portfolio:
        for tick_pr in portfolio[coun_pr]:
            if coun_pr == "usa":
                price_ticker_usa = get_data_usa(
                    ticker=tick_pr, action="price", show=False
                )
                last_price[coun_pr].update(
                    {tick_pr: round(price_ticker_usa) if price_ticker_usa else None}
                )
            elif coun_pr == "rus":
                price_ticker_rus = get_data_rus(
                    ticker=tick_pr, action="price", show=False
                )
                last_price[coun_pr].update(
                    {tick_pr: round(price_ticker_rus) if price_ticker_rus else None}
                )
    check_none_price = [
        (t, v) for c in last_price for t, v in last_price[c].items() if v is None
    ]
    if check_none_price:
        return dict(check_none_price)
    elif usd_rub:
        value_price = sum([i for k in last_price for i in last_price[k].values()])
        total_value_rub = cash_usd * usd_rub + cash_rub + value_price
        profit_ytd = total_value_rub - old_year
        profit_ytd_perc = profit_ytd / old_year * 100
        return round(total_value_rub), round(profit_ytd), round(profit_ytd_perc, 2)


if __name__ == "__main__":
    # change_month_year(today_val=today_value)
    total_change = 0
    for coun in portfolio:
        print(f"{coun.upper()}\n{'-'*15}")
        tmp_change = 0
        for tick in portfolio[coun]:
            if coun == "usa":
                price_ticker_usa = get_data_usa(ticker=tick, action="change")
                tmp_change += price_ticker_usa if price_ticker_usa else 0
            elif coun == "rus":
                price_ticker_rus = get_data_rus(ticker=tick, action="change")
                tmp_change += price_ticker_rus if price_ticker_rus else 0
        print(
            f"{'-'*15}\n{coun.upper()}: {'+' if tmp_change > 0 else ''}{round(tmp_change)}\n"
        )
        total_change += tmp_change
    print(
        f"{'-'*15}\nTotal: {'+' if total_change > 0 else '':>1}{round(total_change)}\n"
    )
