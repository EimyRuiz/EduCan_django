from pymongo import MongoClient
from decouple import config

# Cliente de conexión a MongoDB Atlas — se crea una sola vez
client = MongoClient(config('MONGO_URI'))

# Selecciona la base de datos específica del proyecto
db = client['EduCan']