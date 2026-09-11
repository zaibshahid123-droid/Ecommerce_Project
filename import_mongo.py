"""
Import previously exported JSON files back into MongoDB Atlas.
Reads connection info from .env (same file your Django project uses).
Pairs with export_mongo.py.

Usage:
    python import_mongo.py
"""

import glob
import os
from dotenv import load_dotenv
from bson import json_util
from pymongo import MongoClient

load_dotenv()

MONGO_URI = os.environ.get('MONGO_URI')
if not MONGO_URI:
    raise ValueError("MONGO_URI not found. Make sure .env exists and contains it.")

DB_NAME = MONGO_URI.split('/')[-1].split('?')[0]
INPUT_DIR = "backups/mongo_json"


def main():
    client = MongoClient(MONGO_URI)
    db = client[DB_NAME]

    json_files = glob.glob(os.path.join(INPUT_DIR, "*.json"))
    if not json_files:
        print(f"No JSON files found in {INPUT_DIR}")
        return

    print(f"Connected to database: {DB_NAME}")

    for path in json_files:
        collection_name = os.path.splitext(os.path.basename(path))[0]

        with open(path, "r", encoding="utf-8") as f:
            documents = json_util.loads(f.read())

        if not documents:
            print(f"  Skipping '{collection_name}' - no documents in file.")
            continue

        collection = db[collection_name]
        result = collection.insert_many(documents)
        print(f"  Imported {len(result.inserted_ids)} documents into '{collection_name}'")

    print("\nDone.")


if __name__ == "__main__":
    main()
