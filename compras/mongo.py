import os

try:
    from pymongo import MongoClient
except ImportError:
    MongoClient = None

MONGO_HOST = os.getenv("MONGO_HOST", "localhost")
MONGO_PORT = int(os.getenv("MONGO_PORT", 27017))
MONGO_DB = os.getenv("MONGO_DB", "think_ps")

class UnavailableCollection:
    def __getattr__(self, name):
        raise RuntimeError("pymongo nao esta instalado neste ambiente.")


if MongoClient is None:
    client = None
    db = None
    compras_collection = UnavailableCollection()
    produtos_collection = UnavailableCollection()
else:
    client = MongoClient(host=MONGO_HOST, port=MONGO_PORT, serverSelectionTimeoutMS=2000)
    db = client[MONGO_DB]

    compras_collection = db["compras"]
    produtos_collection = db["produtos"]
