import requests
import pandas as pd
import datetime
import matplotlib.pyplot as plt
import matplotlib.cm as cm
from flask import Flask, render_template, request, Response
import numpy as np
import pytz
import io  # Import io module
import matplotlib
matplotlib.use('Agg')  # Use non-interactive backend

app = Flask(__name__)

class CryptoCompare:
    def __init__(self):
        self.endpoint_url = 'https://api.coingecko.com/api/v3/coins/{}/market_chart/range?vs_currency=usd&from={}&to={}'
        self.coin_ids = []

    def fetch_data(self, coin_ids, start_unix, end_unix):
        coin_dfs = []
        for coin_id in coin_ids:
            response = requests.get(self.endpoint_url.format(coin_id, start_unix, end_unix))
            coin_df = pd.DataFrame(response.json()['prices'], columns=['timestamp', 'price'])
            coin_df['timestamp'] = pd.to_datetime(coin_df['timestamp'], unit='ms')
            coin_df.set_index('timestamp', inplace=True)
            coin_df = coin_df.resample('D').last()
            coin_df.dropna(inplace=True)
            coin_dfs.append(coin_df)
        return coin_dfs

    def plot_data(self, coin_dfs, coin_ids):
        fig, ax1 = plt.subplots(figsize=(12, 6))
        ax_list = [ax1]
        for i in range(1, len(coin_ids)):
            ax_list.append(ax1.twinx())
            rspine = ax_list[-1].spines['right']
            rspine.set_position(('axes', 1 + i * 0.15))
            ax_list[-1].set_frame_on(True)
            ax_list[-1].patch.set_visible(False)
        fig.subplots_adjust(right=0.7)

        colors = cm.viridis(np.linspace(0, 1, len(coin_ids)))

        for i, (coin_id, ax, color) in enumerate(zip(coin_ids, ax_list, colors)):
            ax.plot(coin_dfs[i].index, coin_dfs[i]['price'], label=coin_id.capitalize(), color=color)
            ax.set_ylabel(coin_id.capitalize() + ' Price', color=color)
            ax.yaxis.label.set_color(color)
            ax.tick_params(axis='y', colors=color)
            if i > 0:
                ax.spines["right"].set_position(("axes", 1 + (i - 1) * 0.15))
                ax.tick_params(axis='y', colors=color, pad=20)
            ax.tick_params(axis='x', pad=10)

        ax_list[-1].legend([ax.get_lines()[0] for ax in ax_list], coin_ids)
        ax_list[0].set_ylabel(coin_ids[0].capitalize() + ' Price', color=colors[0])
        plt.xlabel("Date")
        plt.title("Cryptocurrency Price Comparison")

        # Save the plot to a BytesIO object
        img_io = io.BytesIO()
        plt.savefig(img_io, format='png')
        img_io.seek(0)

        plt.close()

        return img_io.getvalue()

crypto_compare = CryptoCompare()

@app.route('/', methods=['GET', 'POST'])
def index():
    if request.method == 'POST':
        start_date = request.form['start_date']
        end_date = request.form['end_date']
        coins = request.form['coins'].split(',')

        start_unix, end_unix = convert_dates_to_unix(start_date, end_date)
        coin_dfs = crypto_compare.fetch_data(coins, start_unix, end_unix)
        plot_image = crypto_compare.plot_data(coin_dfs, coins)

        return Response(plot_image, content_type='image/png')

    return render_template('index.html')

def convert_dates_to_unix(start_date, end_date):
    start_datetime = datetime.datetime.strptime(start_date, '%d-%m-%Y')
    end_datetime = datetime.datetime.strptime(end_date, '%d-%m-%Y')
    end_datetime = end_datetime + datetime.timedelta(hours=23, minutes=59, seconds=59)

    start_datetime_utc = start_datetime.replace(tzinfo=pytz.UTC)
    end_datetime_utc = end_datetime.replace(tzinfo=pytz.UTC)

    start_unix = int(start_datetime_utc.timestamp())
    end_unix = int(end_datetime_utc.timestamp())

    return start_unix, end_unix

if __name__ == '__main__':
    app.run(debug=True)
