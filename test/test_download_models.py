import pytest
import os
import requests
from unittest.mock import patch, mock_open, MagicMock
from download_models import download_file, download_folder, main


class TestDownloadFile:
    @pytest.mark.unit()
    @patch("os.path.exists")
    @patch("requests.get")
    def test_download_file_new_file(self, mock_get, mock_exists):
        """
        Test downloading a new file that doesn't exist locally.
        """
        mock_exists.return_value = False
        mock_response = MagicMock()
        mock_response.headers = {"content-length": "1000"}
        mock_response.iter_content.return_value = [b"chunk1", b"chunk2"]
        mock_response.raise_for_status.return_value = None
        mock_get.return_value = mock_response

        m = mock_open()

        with patch("builtins.open", m):
            download_file("http://example.com/file.txt", "/path/to/file.txt")

        mock_get.assert_called_once_with("http://example.com/file.txt", stream=True)
        m.assert_called_once_with("/path/to/file.txt", "wb")
        handle = m()
        assert handle.write.call_count == 2

    @pytest.mark.unit()
    @patch("os.path.exists")
    def test_download_file_exists(self, mock_exists):
        """
        Test that download is skipped when file exists
        """
        mock_exists.return_value = True

        with patch("builtins.print") as mock_print:
            download_file("http://example.com/file.txt", "/path/to/file.txt")

        mock_print.assert_called_once_with(
            "File /path/to/file.txt already exists, skipping download."
        )

    @pytest.mark.unit()
    @patch("os.path.exists")
    @patch("requests.get")
    def test_download_file_http_error(self, mock_get, mock_exists):
        """
        Test handling of HTTP errors
        """
        mock_exists.return_value = False
        mock_response = MagicMock()
        mock_response.raise_for_status.side_effect = requests.HTTPError("Error")

        mock_get.return_value = mock_response

        with pytest.raises(requests.HTTPError):
            download_file("http://example.com/file.txt", "/path/to/file.txt")


class TestDownloadFolder:
    @pytest.mark.unit()
    @patch("os.makedirs")
    @patch("requests.get")
    def test_download_folder_bart(self, mock_get, mock_makedirs):
        """
        Test downloading a BART model folder with required files.
        """

        repo_url = "facebook/bart-large-cnn"
        folder_path = ""
        dest_path = "/path/to/bart"

        api_response = [
            {"type": "file", "path": "config.json"},
            {"type": "file", "path": "model.safetensors"},
            {"type": "file", "path": "tokenizer.json"},
            {"type": "file", "path": "unwanted_file.txt"},
            {"type": "directory", "path": "subfolder"},
        ]

        mock_api = MagicMock()
        mock_api.json.return_value = api_response
        mock_api.raise_for_status.return_value = None

        mock_get.side_effect = [mock_api]

        with patch("download_models.download_file") as mock_download:
            with patch("download_models.download_folder") as mock_subfolder:
                download_folder(repo_url, folder_path, dest_path)

        mock_makedirs.assert_called_once_with(dest_path, exist_ok=True)
        assert mock_download.call_count == 3

        mock_subfolder.assert_called_once_with(
            repo_url, "subfolder", os.path.join(dest_path, "subfolder")
        )

    @pytest.mark.unit()
    @patch("requests.get")
    def test_download_folder_api_error(self, mock_get):
        """Test handling of API errors."""
        mock_response = MagicMock()
        mock_response.raise_for_status.side_effect = requests.HTTPError("API Error")

        mock_get.return_value = mock_response
        with pytest.raises(requests.HTTPError):
            download_folder("repo", "folder", "/path")


class TestMain:
    @pytest.mark.unit()
    @patch("os.makedirs")
    @patch("download_models.download_file")
    @patch("download_models.download_folder")
    def test_main(self, mock_download_folder, mock_download_file, mock_makedirs):
        """
        Test the main function downloads all required models.
        """

        main()

        mock_makedirs.assert_called_once_with("./models", exist_ok=True)

        assert mock_download_file.call_count == 4
        calls = [call[0][1] for call in mock_download_file.call_args_list]
        assert "./models/google_gemma-3-1b-it-Q4_0.gguf" in calls
        assert "./models/fi_FI-harri-medium.onnx" in calls
        assert "./models/fi_FI-harri-medium.onnx.json" in calls
        assert "./models/wav2vec2_model.onnx" in calls

        assert mock_download_folder.call_count == 3
        folder_calls = [call[0][2] for call in mock_download_folder.call_args_list]
        assert "./models/wav2vec2_processor" in folder_calls
        assert "./models/bart-large-cnn/" in folder_calls
        assert "./models/sbert-cased-finnish-paraphrase/" in folder_calls

    @pytest.mark.unit()
    @patch("os.makedirs")
    def test_main_creates_models_dir(self, mock_makedirs):
        """
        Test that main creates the models directory
        """
        with patch("download_models.download_file"), patch(
            "download_models.download_folder"
        ):
            main()
        mock_makedirs.assert_called_once_with("./models", exist_ok=True)
