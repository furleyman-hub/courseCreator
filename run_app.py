import os
import sys
import streamlit.web.cli as stcli

def resolve_path(path):
    if getattr(sys, "frozen", False):
        basedir = sys._MEIPASS
    else:
        basedir = os.path.dirname(__file__)
    return os.path.join(basedir, path)

    app_path = resolve_path("app.py")

    # Manually load secrets.toml from the executable directory if it exists
    # This works around Streamlit looking in the temp _MEI folder
    try:
        import toml
        if getattr(sys, "frozen", False):
            base_dir = os.path.dirname(sys.executable)
        else:
            base_dir = os.path.dirname(__file__)
            
        secrets_path = os.path.join(base_dir, ".streamlit", "secrets.toml")
        
        if os.path.exists(secrets_path):
            print(f"Loading secrets from {secrets_path}")
            with open(secrets_path, "r", encoding="utf-8") as f:
                secrets = toml.load(f)
                for key, value in secrets.items():
                    if isinstance(value, str):
                        os.environ[key] = value
                    elif isinstance(value, dict):
                         # Handle nested secrets if needed, generally env vars are flat
                         pass
    except Exception as e:
        print(f"Warning: Could not load local secrets.toml: {e}")

    sys.argv = [
        "streamlit",
        "run",
        app_path,
        "--global.developmentMode=false",
        "--server.headless=true",
        "--server.enableCORS=false",
        "--server.enableXsrfProtection=false",
        "--server.enableWebsocketCompression=false",
        "--server.address=localhost",
    ]
    sys.exit(stcli.main())
