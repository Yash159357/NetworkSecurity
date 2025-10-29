import os
import sys
import json
import certifi

from dotenv import load_dotenv

load_dotenv()

MONGODB_URL = os.getenv("MONGODB_URL")
ca = certifi.where()

import pandas as pd
import numpy as np
import pymongo

from networksecurity.utilities.logger import logger
from networksecurity.utilities.exception import NetworkSecurityException

class NetworkDataExtract:
    def __init__(self, database: str, collection: str, mongodb_uri:str = None):
        self._MONGODB_URI = mongodb_uri or os.getenv("MONGODB_URI")
        self.db_name = database
        self.collection_name = collection
        self._client = None
        self._collection = None
        self._connect()

    def _connect(self):
        """Establish MongoDB connection and get collection."""
        try:
            self._client = pymongo.MongoClient(
                self._MONGODB_URI,
                tlsCAFile=certifi.where()
            )
            self._client.admin.command('ping')
            self._collection = self._client[self.db_name][self.collection_name]
            logger.info(f"Successfully connected to MongoDB: {self.db_name}.{self.collection_name}")
        except Exception as e:
            error_msg = f"Failed to connect to MongoDB: {str(e)}"
            logger.error(error_msg)
            raise NetworkSecurityException(error_msg, sys)

    def _csv_to_records(self, filepath: str) -> list:
        """Convert CSV file to list of records."""
        try:
            if not os.path.exists(filepath):
                raise FileNotFoundError(f"File not found: {filepath}")
                
            data = pd.read_csv(filepath)
            records = data.to_dict('records')
            logger.info(f"Read {len(records)} records from {filepath}")
            return records
        except Exception as e:
            error_msg = f"Error reading {filepath}: {str(e)}"
            logger.error(error_msg)
            raise NetworkSecurityException(error_msg, sys)

    def insert_from_csv(self, filepath: str) -> int:
        """Insert records from CSV into MongoDB.
        
        Args:
            filepath: Path to the CSV file
        Returns:
            int: Number of documents inserted
        """
        try:
            logger.info(f"Starting to process {filepath}")
            records = self._csv_to_records(filepath)
            
            if not records:
                logger.warning(f"No records found in {filepath}")
                return 0
                
            result = self._collection.insert_many(records)
            count = len(result.inserted_ids)
            logger.info(f"Successfully inserted {count} documents into {self.db_name}.{self.collection_name}")
            return count
            
        except Exception as e:
            error_msg = f"Failed to insert records: {str(e)}"
            logger.error(error_msg)
            raise NetworkSecurityException(error_msg, sys)

    def __del__(self):
        """Clean up resources."""
        if hasattr(self, '_client') and self._client:
            self._client.close()
            logger.info("MongoDB connection closed")


if __name__ == '__main__':
    extractor = None
    try:
        # Initialize the extractor
        extractor = NetworkDataExtract(
            database="network_security",
            collection="phishing_data"
        )
        
        # Insert data from CSV
        csv_path = "Network_Data/phisingData.csv"  # Update path if needed
        count = extractor.insert_from_csv(csv_path)
        
        logger.info(f"Successfully inserted {count} documents into MongoDB")
        
    except Exception as e:
        logger.error(f"Error: {str(e)}")
        raise
    finally:
        # Explicitly close the MongoDB connection
        if extractor is not None and hasattr(extractor, '_client') and extractor._client:
            extractor._client.close()
            logger.info("MongoDB connection closed")