from hypercore_ca_distributor import settings

def main():
    print(f"Starting {settings.app_name}...")
    print(f"CA Path: {settings.ca_path}")
    print(f"TLS Cert Path: {settings.tls_cert_path}")
    print(f"TLS Key Path: {settings.tls_key_path}")

    # logic

    print(f"{settings.app_name} is now running.")


if __name__ == "__main__":
    main()
