from networksecurity.components.data_validation import DataValidation
from networksecurity.components.data_ingestion import DataIngestion
from networksecurity.utilities.exception import NetworkSecurityException
from networksecurity.utilities.logger import logger
from networksecurity.entity.config_entity import TrainingPipelineConfig, DataIngestionConfig, DataValidationConfig
import sys

def main():
    try:
        logger.info("="*50)
        logger.info("Starting Network Security Training Pipeline")
        logger.info("="*50)
        
        # Initialize configurations
        logger.info("Initializing pipeline configurations...")
        training_pipeline_config = TrainingPipelineConfig()
        
        # Data Ingestion
        logger.info("\n" + "="*30 + " DATA INGESTION " + "="*30)
        data_ingestion_config = DataIngestionConfig(training_pipeline_config=training_pipeline_config)
        data_ingestion = DataIngestion(data_ingestion_config=data_ingestion_config)
        data_ingestion_artifact = data_ingestion.initiate_data_ingestion()
        logger.info("Data ingestion completed successfully")

        # Data Validation
        logger.info("\n" + "="*30 + " DATA VALIDATION " + "="*30)
        data_validation_config = DataValidationConfig(training_pipeline_config=training_pipeline_config)
        data_validation = DataValidation(
            data_validation_config=data_validation_config,
            data_ingestion_artifact=data_ingestion_artifact
        )
        data_validation_artifact = data_validation.initiate_data_validation()
        
        if data_validation_artifact.validation_status:
            logger.info("Data validation successful")
        else:
            logger.warning("! Data validation completed with issues. Check the validation report.")
            if data_validation_artifact.drift_report_file_path:
                logger.info(f"Drift report available at: {data_validation_artifact.drift_report_file_path}")
        
        logger.info("\n" + "="*50)
        logger.info("Training pipeline completed successfully")
        logger.info("="*50)

    except Exception as e:
        logger.critical("!!! Pipeline failed !!!")
        raise NetworkSecurityException(e, sys)

if __name__ == '__main__':
    main()