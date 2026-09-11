"""
Export all collections from MongoDB Atlas to JSON files.
Reads connection info from .env (same file your Django project uses).

Usage:
    python export_mongo.py
"""

import json
import os
from datetime import datetime
from dotenv import load_dotenv
from bson import json_util
from pymongo import MongoClient

load_dotenv()

MONGO_URI = os.environ.get('MONGO_URI')
if not MONGO_URI:
    raise ValueError("MONGO_URI not found. Make sure .env exists and contains it.")

# Extract db name from the URI itself (after the last '/' and before '?')
DB_NAME = MONGO_URI.split('/')[-1].split('?')[0]
OUTPUT_DIR = "backups/mongo_json"


def main():
    os.makedirs(OUTPUT_DIR, exist_ok=True)

    client = MongoClient(MONGO_URI)
    db = client[DB_NAME]

    collection_names = db.list_collection_names()
    print(f"Connected to database: {DB_NAME}")
    print(f"Found {len(collection_names)} collections: {collection_names}")

    for name in collection_names:
        collection = db[name]
        documents = list(collection.find())

        output_path = os.path.join(OUTPUT_DIR, f"{name}.json")
        with open(output_path, "w", encoding="utf-8") as f:
            f.write(json_util.dumps(documents, indent=2))

        print(f"  Exported {len(documents)} documents from '{name}' -> {output_path}")

    print(f"\nDone. Backup timestamp: {datetime.utcnow().isoformat()}Z")


if __name__ == "__main__":
    main()
