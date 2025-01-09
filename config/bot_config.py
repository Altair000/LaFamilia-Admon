import os
import yaml
import telebot
import logging

# Configuración del logging
logging.basicConfig(filename='app.log', level=logging.INFO)

# Búsqueda del archivo config.yaml
config_path = os.path.join(os.path.dirname(__file__), 'config.yaml')

try:
    with open(config_path, 'r') as file:
        config = yaml.safe_load(file)
    TOKEN = config['bot']['token']
    bot = telebot.TeleBot(TOKEN)
except FileNotFoundError:
    logging.error(f"Archivo config.yaml no encontrado!!")

def get_admin_ids():
    try:
        with open(config_path, 'r') as file:
            config = yaml.safe_load(file)
        admin_id = config['admin']['id']
        return admin_id
    except FileNotFoundError:
        logging.error(f"Archivo config.yaml no encontrado!!")
