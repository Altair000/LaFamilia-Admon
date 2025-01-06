import yaml
import pg8000

# Cargar configuración desde el archivo JSON
def load_config(file_path="config.yaml"):
    try:
        with open(file_path, "r") as file:
            return yaml.safe_load(file)
    except FileNotFoundError:
        print("Error: El archivo de configuración no se encontró.")
        return None
    except yaml.YAMLError:
        print("Error: El archivo de configuración tiene un formato inválido.")
        return None

# Conexión a la base de datos usando la configuración
def connect_to_database():
    config = load_config()
    if not config:
        return None

    try:
        # Conexión a la base de datos usando pg8000
        connection = pg8000.connect(
            user=config["database"]["user"],
            password=config["database"]["password"],
            host=config["database"]["host"],
            port=config["database"]["port"],
            database=config["database"]["dbname"]
        )
        print("Conexión exitosa a la base de datos.")
        return connection
    except Exception as e:
        print("Error conectando a la base de datos:", e)
        return None
