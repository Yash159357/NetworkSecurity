from networksecurity.entity.artifact_entity import DataValidationArtifact, DataIngestionArtifact
from networksecurity.entity.config_entity import DataValidationConfig
from networksecurity.constants.train_pipeline import SCHEMA_FILE_PATH
from networksecurity.utilities.utils import read_yaml_file, write_yaml_file
from networksecurity.utilities.exception import NetworkSecurityException
from networksecurity.utilities.logger import logger
from scipy.stats import ks_2samp

import os, sys
import pandas as pd
import numpy as np


class DataValidation:
    def __init__(self, data_validation_config: DataValidationConfig, data_ingestion_artifact: DataIngestionArtifact):
        try:
            logger.info("Initializing DataValidation component.")
            self.data_validation_config = data_validation_config
            self.data_ingestion_artifact = data_ingestion_artifact
            self._schema_config = read_yaml_file(SCHEMA_FILE_PATH)
            logger.info(f"Schema file loaded successfully from {SCHEMA_FILE_PATH}")
        except Exception as e:
            logger.error("Error occurred while initializing DataValidation.")
            raise NetworkSecurityException(e, sys)

    @staticmethod
    def drift_checking(base_df, current_df, threshold=0.05):
        try:
            logger.info("Starting data drift checking between base and current datasets.")
            is_drift = False
            drift_report = {}

            for col in base_df.columns:
                d1 = current_df[col]
                d2 = base_df[col]
                stat, p_val = ks_2samp(d1, d2)

                drift_detected = bool(p_val < threshold)
                drift_report[col] = {
                    "p_val": float(p_val),  # ✅ convert numpy.float64 -> float
                    "drift_detected": drift_detected  # ✅ convert numpy.bool_ -> bool
                }

                if drift_detected:
                    logger.warning(f"Data drift detected in feature: {col} (p-value: {p_val:.5f})")

            is_drift = any(v["drift_detected"] for v in drift_report.values())
            logger.info(f"Data drift checking complete. Drift detected: {is_drift}")

            return is_drift, drift_report

        except Exception as e:
            raise NetworkSecurityException(e, sys)

    def validate_dataset(self, df: pd.DataFrame):
        try:
            logger.info("Validating dataset schema.")
            df_col = set(df.columns)
            schema_col = set(self._schema_config["columns"])

            if df_col != schema_col:
                missing_cols = schema_col - df_col
                extra_cols = df_col - schema_col
                logger.warning(f"Schema mismatch detected. Missing: {missing_cols}, Extra: {extra_cols}")
                return False

            logger.info("Dataset schema validation successful.")
            return True
        except Exception as e:
            logger.error("Error occurred during schema validation.")
            raise NetworkSecurityException(e, sys)

    def initiate_data_validation(self) -> DataValidationArtifact:
        try:
            logger.info("Initiating data validation process.")

            train_file_path = self.data_ingestion_artifact.train_path
            test_file_path = self.data_ingestion_artifact.test_path

            # Read data
            logger.info(f"Reading training data from {train_file_path}")
            train_df = pd.read_csv(train_file_path)
            logger.info(f"Reading test data from {test_file_path}")
            test_df = pd.read_csv(test_file_path)

            # Validate schema
            logger.info("Validating training dataset schema.")
            train_valid = self.validate_dataset(train_df)
            logger.info(f"Training dataset valid: {train_valid}")

            logger.info("Validating test dataset schema.")
            test_valid = self.validate_dataset(test_df)
            logger.info(f"Test dataset valid: {test_valid}")

            # Check for data drift
            logger.info("Performing data drift analysis.")
            is_drifted, drift_report = self.drift_checking(train_df, test_df)

            # Add overall drift status to the report
            drift_report["overall_drift_status"] = {
                "is_drift_detected": bool(is_drifted),
                "message": "Significant drift detected in one or more features"
                if is_drifted else "No significant drift detected across features"
            }

            # Log drift summary
            if is_drifted:
                drifted_features = [
                    col for col, stats in drift_report.items()
                    if isinstance(stats, dict) and stats.get("drift_detected")
                ]
                logger.warning(f"Drift detected in features: {', '.join(drifted_features)}")
            else:
                logger.info("No significant drift detected in dataset.")

            # Save drift report
            drift_dir = os.path.dirname(self.data_validation_config.drift_report_file_path)
            os.makedirs(drift_dir, exist_ok=True)
            write_yaml_file(
                file_path=self.data_validation_config.drift_report_file_path,
                content=drift_report
            )
            logger.info(f"Drift report saved successfully to {self.data_validation_config.drift_report_file_path}")

            # Prepare output directories
            base_dir = os.path.dirname(self.data_validation_config.drift_report_file_path)
            valid_dir = os.path.join(base_dir, "validated")
            invalid_dir = os.path.join(base_dir, "invalid")

            os.makedirs(valid_dir, exist_ok=True)
            os.makedirs(invalid_dir, exist_ok=True)

            # Decide where to save files
            if not train_valid or not test_valid or is_drifted:
                logger.warning("Invalid dataset detected — saving to invalid folder.")
                invalid_train_file_path = os.path.join(invalid_dir, "train.csv")
                invalid_test_file_path = os.path.join(invalid_dir, "test.csv")
                valid_train_file_path = None
                valid_test_file_path = None

                # Save invalid data
                train_df.to_csv(invalid_train_file_path, index=False)
                test_df.to_csv(invalid_test_file_path, index=False)

            else:
                logger.info("All datasets validated successfully — saving to validated folder.")
                valid_train_file_path = os.path.join(valid_dir, "train.csv")
                valid_test_file_path = os.path.join(valid_dir, "test.csv")
                invalid_train_file_path = None
                invalid_test_file_path = None

                # Save valid data
                train_df.to_csv(valid_train_file_path, index=False)
                test_df.to_csv(valid_test_file_path, index=False)

            # Create final artifact
            data_validation_artifact = DataValidationArtifact(
                validation_status=bool(all([train_valid, test_valid, not is_drifted])),
                valid_train_file_path=valid_train_file_path,
                valid_test_file_path=valid_test_file_path,
                invalid_train_file_path=invalid_train_file_path,
                invalid_test_file_path=invalid_test_file_path,
                drift_report_file_path=self.data_validation_config.drift_report_file_path,
            )

            logger.info("Data validation process completed successfully.")
            return data_validation_artifact

        except Exception as e:
            logger.error(f"Error during data validation: {e}")
            raise NetworkSecurityException(e, sys)
