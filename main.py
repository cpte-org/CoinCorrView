import requests
import pandas as pd
import datetime
import matplotlib.pyplot as plt
import matplotlib.cm as cm
import tkinter as tk
from tkinter import ttk
import numpy as np
import pytz

class CryptoCompare:
    def __init__(self, master):
        self.master = master
        self.master.title("Cryptocurrency Comparison")

        self.endpoint_url = 'https://api.coingecko.com/api/v3/coins/{}/market_chart/range?vs_currency=usd&from={}&to={}'
        
        self.coin_ids = []

        self.create_widgets()

        # Set default values
        current_year = datetime.datetime.now().year
        self.start_date_entry.insert(0, f"01-01-{current_year}")
        self.end_date_entry.insert(0, datetime.datetime.now().strftime("%d-%m-%Y"))
        self.coins_entry.insert(0, "zcash,ethereum,bitcoin")

    def create_widgets(self):
        self.start_date_label = ttk.Label(self.master, text="Start Date (dd-mm-yyyy):")
        self.start_date_label.grid(row=0, column=0, sticky='w')
        self.start_date_entry = ttk.Entry(self.master)
        self.start_date_entry.grid(row=0, column=1)

        self.end_date_label = ttk.Label(self.master, text="End Date (dd-mm-yyyy):")
        self.end_date_label.grid(row=1, column=0, sticky='w')
        self.end_date_entry = ttk.Entry(self.master)
        self.end_date_entry.grid(row=1, column=1)

        self.coins_label = ttk.Label(self.master, text="Cryptocurrencies (comma-separated):")
        self.coins_label.grid(row=2, column=0, sticky='w')
        self.coins_entry = ttk.Entry(self.master)
        self.coins_entry.grid(row=2, column=1)

        self.submit_button = ttk.Button(self.master, text="Submit", command=self.process_input)
        self.submit_button.grid(row=3, columnspan=2)

    def process_input(self):
        start_date = self.start_date_entry.get().strip()
        end_date = self.end_date_entry.get().strip()
        coins = self.coins_entry.get().strip().split(',')

        self.start_unix, self.end_unix = self.convert_dates_to_unix(start_date, end_date)
        self.coin_ids = [coin.strip().lower() for coin in coins]

        self.fetch_data()
        self.plot_data()

    def convert_dates_to_unix(self, start_date, end_date):
        start_datetime = datetime.datetime.strptime(start_date, '%d-%m-%Y')
        end_datetime = datetime.datetime.strptime(end_date, '%d-%m-%Y')
        end_datetime = end_datetime + datetime.timedelta(hours=23, minutes=59, seconds=59)
        
        start_datetime_utc = start_datetime.replace(tzinfo=pytz.UTC)
        end_datetime_utc = end_datetime.replace(tzinfo=pytz.UTC)
        
        start_unix = int(start_datetime_utc.timestamp())
        end_unix = int(end_datetime_utc.timestamp())
        
        return start_unix, end_unix

    def fetch_data(self):
        self.coin_dfs = []
        for coin_id in self.coin_ids:
            response = requests.get(self.endpoint_url.format(coin_id, self.start_unix, self.end_unix))
            if response.status_code == 200:
                coin_df = pd.DataFrame(response.json()['prices'], columns=['timestamp', 'price'])
                coin_df['timestamp'] = pd.to_datetime(coin_df['timestamp'], unit='ms')
                coin_df.set_index('timestamp', inplace=True)
                coin_df = coin_df.resample('D').last()
                coin_df.dropna(inplace=True)
                self.coin_dfs.append(coin_df)
            else:
                print(f"Error fetching data for {coin_id}: {response.status_code} - {response.text}")

    def plot_data(self):
        if not self.coin_dfs:
            print("No data to plot. Please check your input and try again.")
            return

        fig, ax1 = plt.subplots(figsize=(12, 6))
        ax_list = [ax1]
        for i in range(1, len(self.coin_ids)):
            ax_list.append(ax1.twinx())
            rspine = ax_list[-1].spines['right']
            rspine.set_position(('axes', 1 + i * 0.15))
            ax_list[-1].set_frame_on(True)
            ax_list[-1].patch.set_visible(False)
        fig.subplots_adjust(right=0.7)

        colors = cm.viridis(np.linspace(0, 1, len(self.coin_ids)))

        for i, (coin_id, ax, color) in enumerate(zip(self.coin_ids, ax_list, colors)):
            ax.plot(self.coin_dfs[i].index, self.coin_dfs[i]['price'], label=coin_id.capitalize(), color=color)
            ax.set_ylabel(f"{coin_id.capitalize()} Price", color=color)
            ax.yaxis.label.set_color(color)
            ax.tick_params(axis='y', colors=color)
            if i > 0:
                ax.spines["right"].set_position(("axes", 1 + (i - 1) * 0.15))
                ax.tick_params(axis='y', colors=color, pad=20)
            ax.tick_params(axis='x', pad=10)

        ax_list[-1].legend([ax.get_lines()[0] for ax in ax_list], self.coin_ids)
        ax_list[0].set_ylabel(f"{self.coin_ids[0].capitalize()} Price", color=colors[0])
        plt.xlabel("Date")
        plt.title("Cryptocurrency Price Comparison")
        plt.show()

if __name__ == '__main__':
    root = tk.Tk()
    crypto_compare = CryptoCompare(root)
    root.mainloop()