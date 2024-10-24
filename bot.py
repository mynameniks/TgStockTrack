import telebot
import time
import threading
from func import Stocks

'''
Этот телеграмм бот использует библиотеку yfinance (от компании yahoo) для получения информации об акциях и торгах, 
а так же библиотеку matplotlib для построения графика цен

В файле bot.py представлены только функции самого бота, 
все дополнительные функции для работы с акциями вынесены в отдельный файл func.py 
'''

API_TOKEN = '' # Вставьте ваш токен сюда
bot = telebot.TeleBot(API_TOKEN)
print('online')
active_tracks = {}


@bot.message_handler(commands=['start'])
def handle_start(message):
    '''
    Функция обрабатывает команду /start
    '''
    bot.send_message(
        chat_id=message.chat.id,
        text='*Приветствую!*\n\n'
             '_Я Ваш помощник в мире акций и инвестиций._\n\n'
             '_Мой функционал:_\n'
             '*• /track* - начать отслеживать цену акции\n'
             '*• /my* - активные отслеживания\n'
             '*• /stop* - перестать отслеживать цену акции\n'
             '*• /stats* - информация о компании\n'
             '*• /history* - график истории цены',
        parse_mode='Markdown'
    )

def get_side(current_price, limit_price, side):
    '''
    Функция возвращает True если акция достигла лимита, False в ином случае
    '''
    if side is True:
        res = current_price >= limit_price
    else:
        res = current_price <= limit_price
    return res


def track_stock_price(chat_id, ticker, limit, side):
    '''
    Функция, которая запускается в качестве паралельного потока и отслеживает цену акции
    '''
    current_price = Stocks(ticker=ticker).get_stock_price()

    if side is True:
        sep = 'выше или равна'
    else:
        sep = 'ниже или равна'

    bot.send_message(
        chat_id=chat_id,
        text=f'Я оповещу Вас, если цена акции {ticker} будет {sep} {limit}$\n\n'
             f'Цена акции на момент отправки сообщения: {current_price}$'
    )

    while (ticker, chat_id) in active_tracks:
        time.sleep(5)
        new_price = Stocks(ticker=ticker).get_stock_price()
        if get_side(new_price, limit, side) == True:
            bot.send_message(chat_id, f"Цена {ticker}: {new_price}$")
            del active_tracks[(ticker, chat_id)]


@bot.message_handler(commands=['track'])
def handle_track(message):
    '''
    Функция обрабатывает команду /track
    '''
    args = message.text.split()
    if len(args) != 4:
        bot.send_message(message.chat.id, "Отправьте сообщение в формате\n"
                                          "/track [акция] [> или <] [цена]\n\n"
                                          "(Пример: /track AAPL выше 250)")
        return

    ticker = args[1].upper()
    if Stocks(ticker=ticker).is_ticker_exists() is False:
        bot.send_message(message.chat.id, "Информация по этой акции отсутствует.")
        return

    try:
        limit = float(args[3])
    except ValueError:
        bot.send_message(message.chat.id, "Укажите число в качетсве третьего параметра")
        return

    if args[2] == '>': side = True
    elif args[2] == '<': side = False
    else: side = None

    if side is not None:
        if (ticker, message.chat.id) not in active_tracks:
            active_tracks[(ticker, message.chat.id)] = True
            threading.Thread(target=track_stock_price, args=(message.chat.id, ticker, limit, side)).start()
        else:
            bot.send_message(message.chat.id, "Вы уже отслеживаете эту акцию!")
    else:
        bot.send_message(message.chat.id, "Можно использовать только '>' или '<'")


@bot.message_handler(commands=['stop'])
def handle_stop(message):
    '''
    Функция обрабатывает команду /stop
    '''
    args = message.text.split()
    if len(args) != 2:
        bot.send_message(message.chat.id, "Используйте: /stop [акция]")
        return

    ticker = args[1].upper()

    if (ticker, message.chat.id) in active_tracks:
        del active_tracks[(ticker, message.chat.id)]
        bot.send_message(message.chat.id, f"Вы прекратили отслеживание {ticker}.")
    else:
        bot.send_message(message.chat.id, f"Вы не отслеживаете {ticker}.")


@bot.message_handler(commands=['my'])
def handle_my(message):
    '''
    Функция обрабатывает команду /my
    '''
    user_tracks = ''
    for item in active_tracks:
        if item[1] == message.chat.id:
            user_tracks += f'• {item[0]}\n'

    if user_tracks == '':
        text = 'Сейчас Вы ничего не отслеживаете!'
    else:
        text = 'Вы отслеживаете:\n\n'

    bot.send_message(
        chat_id=message.chat.id,
        text=text+user_tracks
    )


@bot.message_handler(commands=['stats'])
def handle_stats(message):
    '''
    Функция обрабатывает команду /stats
    '''
    args = message.text.split()
    if len(args) != 2:
        bot.send_message(message.chat.id, "Используйте: /stats [акция]")
        return

    ticker = args[1].upper()

    if Stocks(ticker=ticker).is_ticker_exists():
        market_cap = Stocks(ticker=ticker).get_stock_stats()[0]
        trade_volume = Stocks(ticker=ticker).get_stock_stats()[1]
        price = Stocks(ticker=ticker).get_stock_price()
        bot.send_message(message.chat.id,
                         f"*Статистика для {ticker}:*\n\n"
                         f"Капитализация: {Stocks().format_num(market_cap)}\n"
                         f"Объем торгов: {Stocks().format_num(trade_volume)}\n"
                         f"Текущая цена: {price}$",
                         parse_mode='Markdown')
    else:
        bot.send_message(message.chat.id, "Информация по этой акции отсутствует.")


@bot.message_handler(commands=['history'])
def handle_history(message):
    '''
    Функция обрабатывает команду /history
    '''
    args = message.text.split()
    if (len(args) != 3) or (args[2] not in ('1d', '1w', '2w', '1m', '3m', '6m', '1y', 'all')):
        bot.send_message(message.chat.id, "Используйте: /history [акция] [временной интервал]\n\n"
                                          "(Доступные интервалы: 1d, 1w, 2w, 1m, 3m, 6m, 1y, all)")
        return

    ticker = args[1].upper()
    if Stocks(ticker=ticker).is_ticker_exists() is False:
        bot.send_message(message.chat.id, 'Информация по этой акции отсутствует.')
        return

    Stocks(ticker=ticker).draw_graph(period=args[2])
    with open('temp.png', 'rb') as photo:
        bot.send_photo(
            chat_id=message.chat.id,
            photo=photo
        )
    Stocks().clear_graph()



bot.polling()