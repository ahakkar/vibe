import os
import requests


def download_file(url, dest_path):
    """ Download a file from a URL to a destination path.

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


def download_folder(repo_url, folder_path, dest_path):
    """ Download an entire folder from a Hugging Face model repository.

    Args:
        repo_url String: The Hugging Face model repository base URL.
        folder_path String: The subpath to the folder to download.
        dest_path String: The destination path to save the folder to.
    """
    api_url = f"https://huggingface.co/api/models/{repo_url}/tree/main/{folder_path}"
    response = requests.get(api_url)
    response.raise_for_status()
    files = response.json()

    os.makedirs(dest_path, exist_ok=True)

    for file in files:
        if file["type"] == "file":
            file_url = f"https://huggingface.co/{repo_url}/resolve/main/{file['path']}"
            file_dest_path = os.path.join(dest_path, os.path.basename(file["path"]))
            download_file(file_url, file_dest_path)


def main():
    """
    Download the models and wav2vec processor required for the application.
    """
    # Define the models to download
    models = {
        "Gemma2:2b_unsloth.Q4_K_M.gguf": "https://huggingface.co/KalleLaht/Gemma2_2b-fine-tuned-finnish/resolve/main/Gemma2%3A2b_unsloth.Q4_K_M.gguf",
        "fi_FI-harri-medium.onnx": "https://huggingface.co/spaces/vuxuanhoan/Pipertts/resolve/aa630747d90f7621cfc650eede636736ff24b91c/content/piper/src/python/fi_FI-harri-medium.onnx",
        "fi_FI-harri-medium.onnx.json": "https://huggingface.co/spaces/vuxuanhoan/Pipertts/resolve/aa630747d90f7621cfc650eede636736ff24b91c/content/piper/src/python/fi_FI-harri-medium.onnx.json",
        "wav2vec2_model.onnx": "https://huggingface.co/KalleLaht/wav2vec2-large-uralic-voxpopuli-v2-finnish-ONNX/resolve/main/wav2vec2_model.onnx",
    }

    # Create the models directory if it doesn't exist
    os.makedirs("./models", exist_ok=True)

    # Download each model
    for filename, url in models.items():
        dest_path = os.path.join("./models", filename)
        download_file(url, dest_path)

    # Download the processor folder
    repo_url = "KalleLaht/wav2vec2-large-uralic-voxpopuli-v2-finnish-ONNX"
    folder_path = "wav2vec2_processor"
    dest_path = os.path.join("./models", folder_path)
    download_folder(repo_url, folder_path, dest_path)


if __name__ == "__main__":
    main()
