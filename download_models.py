import os
import requests
import subprocess
from shlex import split

def main():
    """
    Download the models and wav2vec processor required for the application.
    """
    # Define the models to download
    models = {
        "fi_FI-harri-medium.onnx": "https://huggingface.co/spaces/vuxuanhoan/Pipertts/resolve/aa630747d90f7621cfc650eede636736ff24b91c/content/piper/src/python/fi_FI-harri-medium.onnx",
        "fi_FI-harri-medium.onnx.json": "https://huggingface.co/spaces/vuxuanhoan/Pipertts/resolve/aa630747d90f7621cfc650eede636736ff24b91c/content/piper/src/python/fi_FI-harri-medium.onnx.json",
    }

    for filename, url in models.items():
        dest_path = os.path.join("./models", filename)
        download_file(url, dest_path)

    # Create the models directory if it doesn't exist
    os.makedirs("./models", exist_ok=True)
     
    folders = [
        {
            "author": "lmstudio-community",
            "repo": "gemma-3-1B-it-qat-GGUF",
            "dest_dir": "./models/gemma-3-1B-it-qat-GGUF",
        },
        {
            "author": "KalleLaht",
            "repo": "wav2vec2-large-uralic-voxpopuli-v2-finnish-ONNX",
            "dest_dir": "./models/wav2vec2-large-uralic-voxpopuli-v2-finnish-ONNX",
        },
        {
            "author": "Finnish-NLP",
            "repo": "wav2vec2-large-uralic-voxpopuli-v2-finnish",
            "dest_dir": "./models/wav2vec2-large-uralic-voxpopuli-v2-finnish",
        },
        {
            "author": "facebook",
            "repo": "bart-large-cnn",
            "dest_dir": "./models/bart-large-cnn",
        },
        {
            "author": "TurkuNLP",
            "repo": "sbert-cased-finnish-paraphrase",
            "dest_dir": "./models/sbert-cased-finnish-paraphrase",
        },
    ]

    # Download huggingface folders  
    for folder in folders:
        download_folder(folder)


def download_file(url, dest_path):
    """Download a file from a URL to a destination path.

    Args:
        url String: The URL to download the file from.
        dest_path String: The destination path to save the file to.
    """
    if os.path.exists(dest_path):
        print(f"File {dest_path} already exists, skipping download.")
        return

    response = requests.get(url, stream=True)
    response.raise_for_status()
    total_size = int(response.headers.get("content-length", 0))
    block_size = 8192  # 8 Kibibytes
    downloaded_size = 0

    with open(dest_path, "wb") as file:
        for chunk in response.iter_content(chunk_size=block_size):
            downloaded_size += len(chunk)
            file.write(chunk)
            done = int(50 * downloaded_size / total_size)
            # Print a progress bar
            print(
                f"\r{os.path.basename(dest_path)} [{'=' * done}{' ' * (50 - done)}] {downloaded_size / total_size:.2%}",
                end="",
            )
    print()

def download_folder(folder: dict):
    """
    Download an entire folder from a HuggingFace model repository.
    """
    author = folder["author"]
    repo = folder["repo"]
    dest_dir = folder["dest_dir"]

    command = f"huggingface-cli download {author}/{repo} --local-dir {dest_dir}"

    try:
        print(f"Downloading folder: {author}/{repo}")
        args = split(command)
        result = subprocess.run(args, capture_output=True, text=True, check=True)
        print(f"Download successful: {result.stdout}")

    except subprocess.CalledProcessError as e:
        print(f"Error downloading folder {repo}:")
        print(e.stderr)
    except FileNotFoundError:
        print(
            "Error: huggingface-cli not found. Make sure it's installed and in your PATH."
        )

if __name__ == "__main__":
    main()
