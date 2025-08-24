from pydantic_settings import BaseSettings

class Settings(BaseSettings):
    model_config = {
        "env_file": ".env",
        "env_prefix": "HYPERCORE_CA_DISTRIBUTOR_",
    }
    app_name: str = "Hypercore CA Distributor"
    ca_path: str = "/app/certificates/ca.crt"
    tls_cert_path: str = "/app/certificates/tls.crt"
    tls_key_path: str = "/app/certificates/tls.key"

settings = Settings()
