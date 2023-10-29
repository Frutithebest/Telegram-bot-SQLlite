# Импортируем все нужные библиотеки
import telebot
from telebot import types
import sqlite3 as sq
#Стартовое письмо , в котором описывается в каком формате вводить данные
with open('start_message.txt') as file:
    start_message = file.read()
#Читаем токен бота из файла
with open('token.txt') as file:
    TOKEN = file.read()
bot =telebot.TeleBot(TOKEN)
#Создаём функцю , которая будет обрабатывать команду start
@bot.message_handler(commands=['start'])
def start(message):

    bot.send_message(message.chat.id,start_message)
    #Создаём базу данных и таблицу в ней
    with sq.connect('shop.db') as con :
        cur = con.cursor()
        cur.execute('''CREATE TABLE IF NOT EXISTS product(
        product_id INTEGER PRIMARY KEY AUTOINCREMENT,
        name TEXT NOT NULL,
        price INTEGER NOT NULL DEFAULT 1,
        quantity_in_store INTEGER NOT NULL DEFAULT 0)''')
    bot.register_next_step_handler(message,new_product)
#Функция принимает данные , обрабатывает их и помещает в таблицу
def new_product(message):

    text = message.text
    product = text.split('/')
    name = '"' + product[0] + '"'
    price = int(product[1])
    quantity_in_store = int(product[2])
    with sq.connect('shop.db') as con:
        cur = con.cursor()
        cur.execute(f'INSERT INTO product(name,price,quantity_in_store) '
                    f'VALUES ({name},{price},{quantity_in_store})')
    #Создём кнопки с действиями
    markup = types.ReplyKeyboardMarkup()
    add_button = types.KeyboardButton('Add')
    markup.row(add_button)
    finish_button = types.KeyboardButton('Finish')
    markup.row(finish_button)

    bot.send_message(message.chat.id, 'Product added',reply_markup=markup)
#Функция , котрая обрабатывает нажатие кнопок
@bot.message_handler()
def callback(message):
    if message.text == 'Add' :
        add(message)
    elif message.text == 'Finish' :
        finish(message)
#Функция , в которую мы вводим данные для добавления в БД
def add(message):
    bot.send_message(message.chat.id,'Enter the product in the same way as the first one')
    bot.register_next_step_handler(message,new_product)
#Функция , которая показывает базу данных
def finish(message):
    table =''
    with sq.connect('shop.db') as con :
        cur = con.cursor()
        cur.execute('''SELECT * FROM product''')
        for info in cur:
            table += (f'ID: {info[0]}: Name: {info[1]} | Price: {info[2]} | Quantity in store: {info[3]}\n')
    bot.send_message(message.chat.id,table)


bot.infinity_polling()