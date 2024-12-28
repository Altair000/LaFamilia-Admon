import telebot
from productos import agregar_producto, eliminar_producto, editar_precio_producto, obtener_listado_productos, editar_cantidad_vendida
from login import verificar_si_es_admin
from db import connect_to_database

# CONSTANTES ###########
bot = telebot.TeleBot("8038530686:AAHouv6fyKfJGpAcwUgBcNFSd1CKPP4MRBo")

conn = connect_to_database()

# COMANDOS #############
@bot.message_handler(commands=['start'])
def start(message):
    chat_id = message.chat.id
    bot.send_message(chat_id, f"Hola, este es el bot de admón de 'La Familia'. Use el comando '/login' para iniciar sesión")

@bot.message_handler(commands=['login'])
def login(message):
    chat_id = message.chat.id
    user_id = message.text.split()[1]
    verificar_si_es_admin(conn, chat_id, bot, user_id)  

@bot.message_handler(commands=['admin_help'])
def admin_help(message):
    chat_id = message.chat.id
    info = f'''
    (/help) - Muestra este mensaje.
    (/list) - Muestra un listado de los productos. Uso (/list)
    (/add) - Agrega productos al listado. Uso (/add [nombre_producto] [cantidad] [precio])
    (/del) - Elimina productos del listado. Uso (/del [nombre_producto])
    (/price) - Edita el precio de X producto. Uso (/price [nombre_producto] [nuevo_precio])
    (/sell) - Establece la cantidad de producto vendida. Uso (/sell [nombre_producto] [cantidad_vendida])
    '''
    bot.send_message(chat_id, info)

@bot.message_handler(commands=['help'])
def help(message):
    chat_id = message.chat.id
    info = f'''
    (/list) - Muestra un listado de los productos. Uso (/list)
    (/sell) - Establece la cantidad de producto vendida. Uso (/sell [nombre_producto] [cantidad_vendida])
    '''
    bot.send_message(chat_id, info)

@bot.message_handler(commands=['list'])
def listado(message):
    chat_id = message.chat.id
    obtener_listado_productos(conn, bot, chat_id)

@bot.message_handler(commands=['add'])
def add(message):
    chat_id = message.chat.id
    producto, cantidad, precio = message.text.split()[1:]
    agregar_producto(conn, producto, cantidad, precio, bot, chat_id)

@bot.message_handler(commands=['del'])
def delete(message):
    chat_id = message.chat.id
    producto = message.text.split()[1]
    eliminar_producto(conn, producto, bot, chat_id)

@bot.message_handler(commands=['price'])
def price(message):
    chat_id = message.chat.id
    producto, nuevo_precio = message.text.split()[1:]
    editar_precio_producto(conn, producto, nuevo_precio, bot, chat_id)

@bot.message_handler(commands=['sell'])
def sell(message):
    chat_id = message.chat.id
    producto, cantidad_vendida = message.text.split()[1:]
    editar_cantidad_vendida(conn, producto, cantidad_vendida, chat_id, bot)

if __name__ == '__main__':
    print('Bot iniciado...')
    bot.infinity_polling()