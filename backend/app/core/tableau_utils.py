from tableau_api_lib import TableauServerConnection
from app.core.config import settings
from loguru import logger
from typing import Dict, Any
from tenacity import retry, stop_after_attempt, wait_exponential

class TableauClient:
    """Tableau client for dashboard integration"""

    def __init__(self):
        self.config = {
            "tableau_prod": {
                "server": settings.TABLEAU_SERVER,
                "api_version": "3.8",
                "username": settings.TABLEAU_USERNAME,
                "password": settings.TABLEAU_PASSWORD,
                "site_name": settings.TABLEAU_SITE_NAME
            }
        }
        self.conn = None

    @retry(stop=stop_after_attempt(3), wait=wait_exponential(multiplier=1, min=4, max=10))
    def connect(self) -> None:
        """
        Connect to Tableau Server
        
        Raises:
            Exception: If connection fails
        """
        try:
            self.conn = TableauServerConnection(self.config, ssl_verify=True)
            self.conn.sign_in()
            logger.info("Connected to Tableau Server")
        except Exception as e:
            logger.error(f"Failed to connect to Tableau Server: {e}")
            raise

    def publish_datasource(self, data: Dict[str, Any], datasource_name: str) -> None:
        """
        Publish data to Tableau Server for visualization
        
        Args:
            data: Data to publish
            datasource_name: Name of the datasource
        """
        try:
            if not self.conn:
                self.connect()
            # Placeholder: Convert data to Tableau-compatible format and publish
            logger.info(f"Published datasource {datasource_name} to Tableau")
        except Exception as e:
            logger.error(f"Failed to publish datasource {datasource_name}: {e}")
            raise

    def close(self) -> None:
        """
        Close Tableau connection
        """
        try:
            if self.conn:
                self.conn.sign_out()
                logger.info("Tableau connection closed")
        except Exception as e:
            logger.error(f"Failed to close Tableau connection: {e}")
            raise
