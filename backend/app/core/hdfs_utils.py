
from pyhdfs import HdfsClient
from app.core.config import settings
from loguru import logger
from tenacity import retry, stop_after_attempt, wait_exponential
from typing import List, Dict, Any
import json

class HDFSClient:
    """HDFS client for data storage and retrieval"""

    def __init__(self):
        try:
            self.hdfs = HdfsClient(
                hosts=f"{settings.HDFS_HOST}:{settings.HDFS_PORT}",
                user_name=settings.HDFS_USER,
                timeout=10
            )
            logger.info("HDFS client initialized successfully")
        except Exception as e:
            logger.error(f"Failed to initialize HDFS client: {e}")
            raise

    @retry(stop=stop_after_attempt(3), wait=wait_exponential(multiplier=1, min=4, max=10))
    def save_data(self, data: bytes, hdfs_path: str) -> bool:
        """
        Save data to HDFS with retry logic
        
        Args:
            data: Data to save (bytes)
            hdfs_path: HDFS file path
        
        Returns:
            bool: True if successful
        
        Raises:
            Exception: If all retries fail
        """
        try:
            self.hdfs.write(hdfs_path, data)
            logger.info(f"Data saved to HDFS at {hdfs_path}")
            return True
        except Exception as e:
            logger.error(f"Failed to save data to HDFS at {hdfs_path}: {e}")
            raise

    @retry(stop=stop_after_attempt(3), wait=wait_exponential(multiplier=1, min=4, max=10))
    def read_data(self, hdfs_path: str) -> bytes:
        """
        Read data from HDFS with retry logic
        
        Args:
            hdfs_path: HDFS file path
        
        Returns:
            bytes: Data read from HDFS
        
        Raises:
            Exception: If all retries fail
        """
        try:
            data = self.hdfs.read(hdfs_path)
            logger.info(f"Data read from HDFS at {hdfs_path}")
            return data
        except Exception as e:
            logger.error(f"Failed to read data from HDFS at {hdfs_path}: {e}")
            raise

    def save_batch_data(self, records: List[Dict[str, Any]], base_path: str) -> List[str]:
        """
        Save multiple records to HDFS in batch
        
        Args:
            records: List of records to save
            base_path: Base HDFS path for records
        
        Returns:
            List[str]: List of HDFS paths where data was saved
        """
        try:
            paths = []
            for i, record in enumerate(records):
                hdfs_path = f"{base_path}/record_{i}.json"
                self.save_data(json.dumps(record).encode(), hdfs_path)
                paths.append(hdfs_path)
            logger.info(f"Batch saved to HDFS at {base_path}")
            return paths
        except Exception as e:
            logger.error(f"Failed to save batch data to HDFS: {e}")
            raise
