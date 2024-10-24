import os
import yfinance as yf
import matplotlib.pyplot as plt
from datetime import datetime, timedelta


class Stocks:
    '''
    Все функции, работающие с акциями представленны в этом классе
    '''
    def __init__(self, ticker=None):
        self.ticker = ticker

    def is_ticker_exists(self):
        '''
        Функция возвращает True если акция существует, False в противном случае
        '''
        try:
            stock = yf.Ticker(self.ticker)
            historical_data = stock.history(period='1d')
            if historical_data.empty:
                return False
            else:
                return True
        except Exception:
            return False

    def get_stock_price(self):
        '''
        Функция возвращает цену акции
        '''
        stock = yf.Ticker(self.ticker)
        price = round((stock.history(period="1d")['Close'].iloc[0]), 2)
        return price

    def get_stock_stats(self):
        '''
        Функция возвращает основную информацию об акции за сутки
        '''
        stock = yf.Ticker(self.ticker)
        market_cap = stock.info.get('marketCap')
        trade_volume = (stock.history(period='1d'))['Volume'].iloc[0]
        return market_cap, trade_volume

    @staticmethod
    def format_num(num):
        '''
        Функция округляет число до тысяч, миллионов, миллиардов и триллионов
        '''
        num = abs(num)
        if num < 10**3: return f'{num}$'
        elif num in range(10**3, 10**6): div, sep = 10**3, 'K'
        elif num in range(10**6, 10**9): div, sep = 10**6, 'M'
        elif num in range(10**9, 10**12): div, sep = 10**9, 'B'
        else: div, sep = 10**12, 'T'
        return f'{(num/div):.2f}{sep}$'

    def draw_graph(self, period):
        '''
        Функция рисует график цены акции за определенный период времени и сохраняет его как temp.png
        '''
        periods = {
            '1d': (datetime.now() - timedelta(days=2), 'день'),
            '1w': (datetime.now() - timedelta(days=8), 'неделю'),
            '2w': (datetime.now() - timedelta(days=16), 'две недели'),
            '1m': (datetime.now() - timedelta(days=30), 'месяц'),
            '3m': (datetime.now() - timedelta(days=90), 'три месяца'),
            '6m': (datetime.now() - timedelta(days=180), 'пол года'),
            '1y': (datetime.now() - timedelta(days=365), 'год'),
            'all': ('1900-01-01', 'все время')
        }
        start_date = periods[period][0]
        sep = periods[period][1]
        end_date = datetime.now()

        data = yf.download(self.ticker, start=start_date, end=end_date)

        plt.switch_backend('Agg')
        fig, ax = plt.subplots(figsize=(14, 8), facecolor='#222222')

        ax.set_facecolor('#333333')
        for pos in ('top', 'right', 'left', 'bottom'):
            ax.spines[pos].set_color('#d2d2d2')
            ax.spines[pos].set_linewidth(3)

        ax.tick_params(axis='x', colors='#999999', labelsize=10)
        ax.tick_params(axis='y', colors='#999999', labelsize=10)

        ax.grid(color='#999999', linestyle='-', linewidth=1)  # Установка цвета, стиля и толщины сетки

        ax.plot(data.index, data['Close'], label='Цена закрытия', color='#0008ff')
        ax.plot(data.index, data['Open'], label='Цена открытия', color='#6fa8dc')

        ax.set_title(f'Цена акций {self.ticker} за {sep} ($)',
                     fontdict={'fontsize': 26, 'fontweight': 'bold', 'color': '#F0F0F0'})

        legend = plt.legend()
        for text in legend.get_texts():
            text.set_color('#F0F0F0')
        frame = legend.get_frame()
        frame.set_edgecolor('#F0F0F0')  # Меняем цвет рамки на красный
        frame.set_facecolor('#333333')  # Меняем цвет фона рамки

        plt.savefig('temp.png')

    @staticmethod
    def clear_graph():
        '''
        Функция удаляет график после того как он был отправлен пользователю
        '''
        os.remove('temp.png')