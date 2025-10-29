import os
import sys
import numpy as np
import pandas as pd

"""
DATA INGESTION CONSTANTS
"""
DATA_INGESTION_COLLECTION_NAME = "phishing_data"
DATA_INGESTION_DATABASE_NAME = "network_security"
DATA_INGESTION_DIR_NAME = "DataIngestion"
DATA_INGESTION_FEATURE_STORE_DIR = "feature_store"
DATA_INGESTION_INGESTED_DIR = "ingested"
DATA_INGESTION_TEST_TRAIN_SPLIT = 0.2

"""
defining common constant variables for training pipeline
"""
TARGET_COLUMN = "Result"
PIPELINE_NAME = "NetworkSecurity"
ARTIFACT_DIR = "Artifacts"
FILE_NAME = "phisingData.csv"

TRAIN_FILE_NAME = "train.csv"
TEST_FILE_NAME = "test.csv"