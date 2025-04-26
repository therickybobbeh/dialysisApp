"""
Azure integration module for the Peritoneal Dialysis Management Application.
Provides integration with Azure services including Application Insights,
Key Vault, and Managed Identity.
"""

import logging
import os
from functools import lru_cache
from opencensus.ext.azure.log_exporter import AzureLogHandler
from opencensus.ext.azure.trace_exporter import AzureExporter
from opencensus.trace.samplers import ProbabilitySampler
from opencensus.trace.tracer import Tracer
from opencensus.ext.azure import metrics_exporter
from opencensus.ext.logging import azure_monitor_handler
from opencensus.trace.config import Config as TraceConfig
from azure.keyvault.secrets import SecretClient
from azure.identity import DefaultAzureCredential, ManagedIdentityCredential

from app.core.config import settings

logger = logging.getLogger(__name__)

@lru_cache(maxsize=1)
def get_credential():
    """
    Get Azure credential based on environment.
    Returns DefaultAzureCredential which tries multiple authentication methods.
    """
    try:
        if settings.AZURE_DEPLOYMENT:
            logger.info("Using Azure DefaultAzureCredential for authentication")
            return DefaultAzureCredential()
        else:
            logger.info("Azure authentication not configured - running in local mode")
            return None
    except Exception as e:
        logger.error(f"Error setting up Azure authentication: {str(e)}")
        return None

def setup_azure_app_insights():
    """
    Configure Azure Application Insights for monitoring and telemetry.
    """
    if not settings.ENABLE_APP_INSIGHTS or not settings.APPLICATION_INSIGHTS_CONNECTION_STRING:
        logger.info("Application Insights not configured - skipping setup")
        return None, None
    
    try:
        # Setup Azure metrics exporter
        metrics_exporter_options = {
            'connection_string': settings.APPLICATION_INSIGHTS_CONNECTION_STRING,
            'instrumentation_key': None  # Will be extracted from connection string
        }
        exporter = metrics_exporter.new_metrics_exporter(**metrics_exporter_options)
        
        # Setup Azure trace exporter
        tracer = Tracer(
            exporter=AzureExporter(
                connection_string=settings.APPLICATION_INSIGHTS_CONNECTION_STRING
            ),
            sampler=ProbabilitySampler(1.0),
            config=TraceConfig(
                # Configure with service name and version for better categorization in Azure
                service_name='pd_management_app',
                service_version=os.getenv('APP_VERSION', '1.0.0')
            )
        )
        
        logger.info("Successfully configured Azure Application Insights")
        return exporter, tracer
    except Exception as e:
        logger.error(f"Error setting up Azure Application Insights: {str(e)}")
        return None, None

def setup_azure_log_handler():
    """
    Configure Azure Log Handler for sending logs to Application Insights.
    """
    if not settings.ENABLE_APP_INSIGHTS or not settings.APPLICATION_INSIGHTS_CONNECTION_STRING:
        return None
    
    try:
        # Create an Azure Monitor handler for Python logging
        azure_handler = azure_monitor_handler.AzureMonitorHandler(
            connection_string=settings.APPLICATION_INSIGHTS_CONNECTION_STRING
        )
        
        # Add custom properties to logs
        azure_handler.add_telemetry_processor(
            lambda envelope: envelope.data.baseData.update({
                'properties': {
                    'environment': os.getenv('ENVIRONMENT', 'development'),
                    'service': 'pd_management_app'
                }
            })
        )
        
        return azure_handler
    except Exception as e:
        logger.error(f"Error setting up Azure Log Handler: {str(e)}")
        return None

@lru_cache(maxsize=1)
def get_key_vault_client():
    """
    Get Azure Key Vault client for retrieving secrets.
    """
    if not settings.KEY_VAULT_NAME:
        logger.info("Key Vault name not configured - skipping setup")
        return None
    
    try:
        credential = get_credential()
        if not credential:
            logger.warning("No Azure credential available - cannot access Key Vault")
            return None
            
        vault_url = f"https://{settings.KEY_VAULT_NAME}.vault.azure.net/"
        client = SecretClient(vault_url=vault_url, credential=credential)
        logger.info(f"Successfully initialized Key Vault client for {settings.KEY_VAULT_NAME}")
        
        return client
    except Exception as e:
        logger.error(f"Error setting up Azure Key Vault client: {str(e)}")
        return None

def get_secret(secret_name):
    """
    Retrieve a secret from Azure Key Vault.
    
    Args:
        secret_name: The name of the secret to retrieve
        
    Returns:
        The secret value or None if not found
    """
    client = get_key_vault_client()
    if not client:
        logger.warning(f"Cannot retrieve secret '{secret_name}' - Key Vault client not available")
        return None
        
    try:
        secret = client.get_secret(secret_name)
        logger.debug(f"Successfully retrieved secret '{secret_name}' from Key Vault")
        return secret.value
    except Exception as e:
        logger.error(f"Error retrieving secret '{secret_name}' from Key Vault: {str(e)}")
        return None