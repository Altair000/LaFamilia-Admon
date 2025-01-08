import os
import logging
import yaml
import pg8000

# Configuración del logging
logging.basicConfig(filename='app.log', level=logging.INFO)

# Búsqueda del archivo config.yaml
config_path = os.path.join(os.path.dirname(__file__), 'config.yaml')

try:
    with open(config_path, 'r') as file:
        config = yaml.safe_load(file)
    conexion = pg8000.connect(
        user=config['database']['user'],
        password=config['database']['password'],
        host=config['database']['host'],
        port=config['database']['port'],
        database=config['database']['db']
    )
except FileNotFoundError:
    logging.error(f"Archivo config.yaml no encontrado!!")