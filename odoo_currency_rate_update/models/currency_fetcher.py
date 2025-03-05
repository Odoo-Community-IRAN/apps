# Copyright (C) 2024-Today: Odoo Community Iran
# @author: Odoo Community Iran (https://odoo-community.ir/
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl.html).
from lxml import html
from requests.exceptions import Timeout, RequestException
import requests
import time


class CurrencyFetcher:
    def get_currency_data(self, currency_code, transaction_type):
        url = "https://www.tgju.org/profile/sana_sell_usd" if transaction_type == 'sale' else "https://www.tgju.org/profile/sana_buy_usd"
        headers = {
            'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/58.0.3029.110 Safari/537.3'
        }
        max_retries = 5
        initial_delay = 2
        result = {}

        for attempt in range(1, max_retries + 1):
            time.sleep(initial_delay)
            initial_delay += 2

            try:
                response = requests.get(url, headers=headers, timeout=10)
                response.raise_for_status()

                if response.status_code == 200:
                    dollar_price = self._parse_dollar_price(response.text)
                    if dollar_price:
                        result["currency_code"] = currency_code
                        result["dollar_price"] = dollar_price
            except (Timeout, RequestException) as e:
                print(f"Update currency rate failed: {str(e)}")

        return result

    def _parse_dollar_price(self, html_content):
        tree = html.fromstring(html_content)
        xpath = [
            "/html/body/main/div[1]/div[2]/"
            "div[2]/div[1]/div/div[2]/div/"
            "div[1]/table/tbody/tr[1]/td[2]/text()"
        ]
        dollar_price = tree.xpath(xpath[0])
        return float(dollar_price[0].strip().replace(",", "")) or None
