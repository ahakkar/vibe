import pytest
import os
from download_models import download_file
from tempfile import TemporaryDirectory

class TestDownloadModels:
    @pytest.mark.unit()
    def test_download_file(self):
        with TemporaryDirectory() as temp_dir:
            download_file("https://example.com/file.txt", temp_dir)
            assert os.path.exists(temp_dir)
