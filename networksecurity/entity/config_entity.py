from datetime import datetime
import os

from networksecurity.constants import train_pipeline

class TrainingPipelineConfig:
    def __init__(self, timestamp: datetime = datetime.now()):
        timestamp = timestamp.now().strftime("%m-%d-%Y-%H-%M-%S")

        self.train_pipeline_name = train_pipeline.PIPELINE_NAME
        self.artifact_name = train_pipeline.ARTIFACT_DIR
        self.artifact_dir = os.path.join(self.artifact_name, timestamp)
        self.timestamp = timestamp

class DataIngestionConfig:
    def __init__(self, training_pipeline_config: TrainingPipelineConfig):
        self.data_ingestion_dir = os.path.join(
            training_pipeline_config.artifact_dir,
            train_pipeline.DATA_INGESTION_DIR_NAME
        )
        self.feature_store_file_path = os.path.join(
            self.data_ingestion_dir,
            train_pipeline.DATA_INGESTION_FEATURE_STORE_DIR
        )
        self.train_file_path = os.path.join(
            self.data_ingestion_dir,
            train_pipeline.TRAIN_FILE_NAME
        )
        self.test_file_path = os.path.join(
            self.data_ingestion_dir,
            train_pipeline.TEST_FILE_NAME
        )
        self.train_test_split_ratio = train_pipeline.DATA_INGESTION_TEST_TRAIN_SPLIT
        self.collection_name = train_pipeline.DATA_INGESTION_COLLECTION_NAME
        self.database_name = train_pipeline.DATA_INGESTION_DATABASE_NAME

class DataValidationConfig:
    def __init__(self, training_pipeline_config: TrainingPipelineConfig):
        self.data_validation_dir = os.path.join(
            training_pipeline_config.artifact_dir,
            train_pipeline.DATA_VALIDATION_DIR_NAME
        )
        self.valid_data_dir = os.path.join(
            self.data_validation_dir,
            train_pipeline.DATA_VALIDATION_VALID_DIR
        )
        self.invalid_data_dir = os.path.join(
            self.data_validation_dir,
            train_pipeline.DATA_VALIDATION_INVALID_DIR
        )
        self.valid_train_file_path = os.path.join(
            self.data_validation_dir,
            train_pipeline.TRAIN_FILE_NAME
        )
        self.valid_test_file_path = os.path.join(
            self.data_validation_dir,
            train_pipeline.TEST_FILE_NAME
        )
        self.invalid_train_file_path = os.path.join(
            self.data_validation_dir,
            train_pipeline.TRAIN_FILE_NAME
        )
        self.invalid_test_file_path = os.path.join(
            self.data_validation_dir,
            train_pipeline.TEST_FILE_NAME
        )
        self.drift_report_file_path = os.path.join(
            self.data_validation_dir,
            train_pipeline.DATA_VALIDATION_DRIFT_REPORT_DIR,
            train_pipeline.DATA_VALIDATION_DRIFT_REPORT_FILE_NAME
        )