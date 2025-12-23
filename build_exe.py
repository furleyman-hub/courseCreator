import PyInstaller.__main__
import os
import shutil
from PyInstaller.utils.hooks import copy_metadata

def build():
    print("Building executable...")
    
    # helper to get metadata arguments safely
    # We can't use PyInstaller's copy_metadata directly in the args list easily for conditional logic 
    # unless we pre-calculate it, but PyInstaller command line expects --copy-metadata=NAME.
    # If we want to skip if missing, we have to check if it's installed.
    
    packages_to_copy = [
        "streamlit",
        "tqdm",
        "regex",
        "requests",
        "packaging",
        "filelock",
        "numpy",
        "tokenizers",
        "huggingface-hub",
        "safetensors",
        "pyyaml",
    ]

    metadata_args = []
    
    import importlib.metadata
    for package in packages_to_copy:
        try:
            importlib.metadata.distribution(package)
            metadata_args.append(f"--copy-metadata={package}")
        except importlib.metadata.PackageNotFoundError:
            print(f"Warning: Package '{package}' not found, skipping metadata copy.")

    import streamlit
    streamlit_path = os.path.dirname(streamlit.__file__)
    
    # Define the PyInstaller arguments
    args = [
        "run_app.py",  # Your wrapper script
        "--onefile",
        "--name=TrainingClassGenerator",
        "--clean",
        
        # Collect all data files
        "--add-data=app.py;.",
        "--add-data=generator;generator",
        "--add-data=notes_ocr.py;.",
        "--add-data=heygen_client.py;.",
        "--add-data=requirements.txt;.",
        f"--add-data={os.path.join(streamlit_path, 'static')};streamlit/static",
        f"--add-data={os.path.join(streamlit_path, 'runtime')};streamlit/runtime",
        
        # Hidden imports often missed by PyInstaller analysis
        "--hidden-import=streamlit",
        "--hidden-import=streamlit.web.cli",
        "--hidden-import=altair.vegalite.v5",
        "--hidden-import=notes_ocr",
        "--hidden-import=heygen_client",
    ] + metadata_args
    
    PyInstaller.__main__.run(args)
    print("Build complete. Check dist/ directory.")

if __name__ == "__main__":
    build()
