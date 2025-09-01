import time
import ssl
from pathlib import Path
from hypercore_ca_distributor import settings
from httpx import Client, BasicAuth
import logging

logging.basicConfig(level=logging.DEBUG)
logger = logging.getLogger("tls_distributor")

def http_client():
    if not settings.ca_path or not Path(settings.ca_path).exists():
        raise FileNotFoundError(f"CA file not found at {settings.ca_path}")
    if not settings.tls_cert_path or not settings.tls_key_path:
        raise ValueError("TLS certificate and key paths must be provided.")
    if not Path(settings.tls_cert_path).exists():
        raise FileNotFoundError(f"TLS certificate file not found at {settings.tls_cert_path}")
    if not Path(settings.tls_key_path).exists():
        raise FileNotFoundError(f"TLS key file not found at {settings.tls_key_path}")

    context = ssl.create_default_context(
        ssl.Purpose.SERVER_AUTH,
        cafile=settings.ca_path
    )
    auth = BasicAuth(settings.hypercore_username, settings.hypercore_password)
    return Client(verify=context, auth=auth, timeout=10.0)

def main():
    logger.info(f"Starting {settings.app_name}...")
    client = http_client()
    endpoints = [ep.strip() for ep in settings.hypercore_endpoints.split(",") if ep.strip()]

    for endpoint in endpoints:
        try:
            response = client.get(f"{endpoint}/rest/v1/ping")
            response.raise_for_status()
            logger.info(f"Successfully connected to {endpoint}: {response.json()}")
        except Exception as e:
            logger.error(f"Failed to connect to {endpoint}: {e}")
            raise
    logger.info(f"{settings.app_name} is now running and connected to all endpoints.")

    for endpoint in endpoints:
        try:
            payload = {
                "certificate": Path(settings.tls_cert_path).read_text(),
                "privateKey": Path(settings.tls_key_path).read_text()
            }
            response = client.post(f"{endpoint}/rest/v1/Certificate", json=payload)
            response.raise_for_status()
            task_id = None
            task_id = response.json().get("taskTag")

            retries = 10

            while retries >= 0:
                status_response = client.get(f"{endpoint}/rest/v1/TaskTag/{task_id}")
                status_response.raise_for_status()
                status = status_response.json()[0].get("state")

                if status.lower() == "complete":
                    logger.info(f"Certificates for {endpoint} have been updated.")
                    break
                elif status.lower() == "error":
                    logger.error(f"Error updating certificates on {endpoint}: {status_response.json()}")
                    break
                else:
                    logger.info(f"Waiting for certificate update on {endpoint}. Current status: {status}")
                    time.sleep(1)
                    retries -= 1
        except Exception as e:
            logger.error(f"Failed to update certificates on {endpoint}: {e}")


if __name__ == "__main__":
    main()
