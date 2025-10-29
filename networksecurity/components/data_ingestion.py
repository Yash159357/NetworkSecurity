from networksecurity.utilities.exception import NetworkSecurityException
from networksecurity.utilities.logger import logger
from networksecurity.entity.config_entity import DataIngestionConfig, TrainingPipelineConfig
from networksecurity.entity.artifact_entity import DataIngestionArtifact

import os
import sys
import numpy as np
import pandas as pd
from sklearn.model_selection import train_test_split
from dotenv import load_dotenv
import certifi
import pymongo

load_dotenv()
MONGODB_URI = os.getenv("MONGODB_URI")
if not MONGODB_URI:
    raise ValueError("MONGODB_URI environment variable is not set")

class DataIngestion:
    def __init__(self, data_ingestion_config: DataIngestionConfig):
        try:
            self.data_ingestion_config = data_ingestion_config
        except Exception as e:
            raise NetworkSecurityException(e, sys)

    def get_data_from_mongodb(self):
        client = None
        try:
            client = pymongo.MongoClient(
                MONGODB_URI,
                tlsCAFile=certifi.where(),
                serverSelectionTimeoutMS=5000  # 5 second timeout
            )
            # Test the connection
            client.server_info()

            db_name = self.data_ingestion_config.database_name
            collection_name = self.data_ingestion_config.collection_name
            collection = client[db_name][collection_name]

            # Get data with a reasonable timeout
            cursor = collection.find()
            df = pd.DataFrame(list(cursor))

            if df.empty:
                raise NetworkSecurityException("No data found in MongoDB collection", sys)

            if "_id" in df.columns:
                df = df.drop(columns=["_id"], axis=1)
            df.replace({"na": np.nan}, inplace=True)

            return df

        except Exception as e:
            raise NetworkSecurityException(f"Error fetching data from MongoDB: {str(e)}", sys)
        finally:
            if client:
                client.close()

    def export_data_to_feature_store(self, df: pd.DataFrame):
        try:
            feature_store_path = self.data_ingestion_config.feature_store_file_path

            # Skip if feature store already exists
            if os.path.exists(feature_store_path):
                logger.info(f"Feature store already exists at: {feature_store_path}")
                return

            dir_path = os.path.dirname(feature_store_path)
            os.makedirs(dir_path, exist_ok=True)

            # Validate dataframe before saving
            if df.empty:
                raise ValueError("Cannot save empty DataFrame to feature store")

            df.to_csv(feature_store_path, index=False)
            logger.info(f"Feature store created at: {feature_store_path}")

        except Exception as e:
            raise NetworkSecurityException(f"Error exporting data to feature store: {str(e)}", sys)

    def split_and_store_train_test(self, df: pd.DataFrame):
        try:
            train_path = self.data_ingestion_config.train_file_path
            test_path = self.data_ingestion_config.test_file_path

            train_dir_path = os.path.dirname(train_path)
            test_dir_path = os.path.dirname(test_path)

            os.makedirs(train_dir_path, exist_ok=True)
            os.makedirs(test_dir_path, exist_ok=True)

            train_df, test_df = train_test_split(df, test_size=0.2, random_state=42)

            train_df.to_csv(train_path, index=False)
            test_df.to_csv(test_path, index=False)

            logger.info(f"Train and test datasets saved at: {train_path} and {test_path}")

            return DataIngestionArtifact(train_path=train_path, test_path=test_path)

        except Exception as e:
            raise NetworkSecurityException(e, sys)

    def initiate_data_ingestion(self):
        try:
            logger.info("Starting data ingestion process")

            # Get data from MongoDB
            logger.info("Fetching data from MongoDB...")
            df = self.get_data_from_mongodb()
            logger.info(f"Successfully retrieved {len(df)} records from MongoDB")

            # Export to feature store
            logger.info("Exporting data to feature store...")
            self.export_data_to_feature_store(df)

            # Split and store train/test data
            logger.info("Splitting data into training and test sets...")
            ingestion_artifact: DataIngestionArtifact = self.split_and_store_train_test(df)

            logger.info("Data ingestion completed successfully")
            return ingestion_artifact

        except Exception as e:
            logger.error(f"Error during data ingestion: {str(e)}")
            raise NetworkSecurityException(f"Failed to complete data ingestion: {str(e)}", sys)

if __name__ == "__main__":
    """
    Main entry point for running data ingestion as a standalone script
    """
    try:
        # Initialize configuration

        training_pipeline_config = TrainingPipelineConfig()
        data_ingestion_config = DataIngestionConfig(training_pipeline_config=training_pipeline_config)

        # Initialize and run data ingestion
        data_ingestion = DataIngestion(data_ingestion_config=data_ingestion_config)
        artifact = data_ingestion.initiate_data_ingestion()

        # Log completion
        logger.info("-"*60)
        logger.info("Data Ingestion Completed Successfully")
        logger.info(f"Train file: {artifact.train_path}")
        logger.info(f"Test file: {artifact.test_path}")
        logger.info("="*60)

        # Exit with success code
        sys.exit(0)

    except Exception as e:
        logger.error("!"*60)
        logger.error(f"Data Ingestion Failed: {str(e)}")
        logger.error("!"*60)
        # Exit with error code
        sys.exit(1)