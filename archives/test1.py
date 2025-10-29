from pymongo.mongo_client import MongoClient
from dotenv import load_dotenv
import os

load_dotenv()
uri = os.getenv("MONGODB_URI")

if not uri:
    raise ValueError("MONGODB_URI not found in .env file")

client = MongoClient(uri)

try:
    client.admin.command('ping')
    print("Pinged your deployment. You successfully connected to MongoDB!")
except Exception as e:
    print(f"Error: {e}")
finally:
    client.close()