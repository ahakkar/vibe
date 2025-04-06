import pytest
from unittest.mock import MagicMock, patch
from src.backend.app import AppManager
from local.constants import Srv

with patch.dict(
    "sys.modules",
    {
        "argparse": MagicMock(),
        "shutil": MagicMock(),
        "dotenv": MagicMock(),
        "os": MagicMock(),
        "audio": MagicMock(),
    },
):
    from src.backend.app import AppManager

class TestAppManager:
    """
    Test class for AppManager"
    """

    def setup_method(self):
        """
        Setup method to run before each test
        """
        with patch("argparse.ArgumentParser", return_value=MagicMock()), \
             patch.object(AppManager, "_find_project_root", return_value="/mock/root/"), \
             patch.object(AppManager, "_setup_env", return_value=None), \
             patch.object(AppManager, "_load_services", return_value=None):
            self.app = AppManager()

        self.app.services = {
            Srv.STT: MagicMock(),
            Srv.TTS: MagicMock(),
            Srv.TEXT_GEN: MagicMock(),
            Srv.IR: MagicMock(),
            Srv.AUDIO: MagicMock(),
            Srv.CLI: MagicMock(),
            Srv.WEATHER: MagicMock(),
            Srv.NEWS: MagicMock(),
        }

    def teardown_method(self):
        """
        Teardown method to run after each test
        """
        self.app = None

    @pytest.mark.unit()
    def test_app_init(self):
        """
        Test AppManager initialization.
        """
        assert self.app is not None
        assert self.app.services is not None
        assert self.app.ENV_PATH == "/mock/root/src/backend"

    @pytest.mark.unit()
    @pytest.mark.parametrize(
        "is_recording, audio_data, cli",
        [
            (False, None, False),
            (True, None, True),
            (True, MagicMock(), False),
        ],
    )
    def test_toggle_recording(self, is_recording, audio_data, cli):
        """
        Test the start of audio recording.
        """
        with patch.object(self.app.services[Srv.AUDIO], "is_recording"
                 , is_recording), \
             patch.object(self.app.services[Srv.AUDIO], "start_recording"
                 , return_value=False), \
             patch.object(self.app.services[Srv.AUDIO], "stop_recording"
                 , return_value=audio_data), \
             patch.object(self.app.args, "cli"
                 , cli), \
             patch.object(self.app, "_process_recording"
                 , return_value=None), \
             patch.object(self.app.services[Srv.CLI], "print_text", 
                 return_value=None) as mock_print_text:
            
            self.app.toggle_recording(False)

            if is_recording:
                assert self.app.services[Srv.AUDIO].stop_recording.called
                if audio_data is not None:
                    assert self.app._process_recording.called
                elif cli:
                    mock_print_text.assert_called_once_with("No audio recorded.")
            else:
                assert self.app.services[Srv.AUDIO].start_recording.called

    @pytest.mark.unit()
    @pytest.mark.parametrize(
        "all, intent, cli",
        [
            (True, MagicMock(), True),
            (False, None, False),
        ],
    )
    def test_process_recording(self, all, intent, cli):
        """
        Test the processing of audio recording.
        """
        with patch.object(self.app.services[Srv.STT], "transcribe"
                 , return_value="mocked_transcription"), \
             patch.object(self.app.services[Srv.IR], "recognize_intent"
                 , return_value=intent), \
             patch.object(self.app.services[Srv.IR], "process_intent"
                 , return_value="mocked_response"), \
             patch.object(self.app.args, "cli", cli), \
             patch.object(self.app.services[Srv.CLI], "print_text", 
                 return_value=None) as mock_print_text:

            self.app._process_recording("mocked_recording", all)

            if all:
                assert self.app.services[Srv.STT].transcribe.called
                if intent is not None:
                    assert self.app.services[Srv.IR].recognize_intent.called
                    assert self.app.services[Srv.IR].process_intent.called
                    if cli:
                        mock_print_text.assert_called_once_with("mocked_response")
                else:
                    assert self.app.text_gen.called
            else:
                assert not self.app.services[Srv.IR].recognize_intent.called
        
    @pytest.mark.unit()
    def test_get_service(self):
        """
        Test the retrieval of a service.
        """
        service = self.app.get_service(Srv.STT)
        assert service == self.app.services[Srv.STT]

    @pytest.mark.unit()
    def test_exit(self):
        pass

    @pytest.mark.unit()
    def test_run(self):
        """
        Test the run method.
        """
        with patch.object(self.app, "_run_cli", return_value=None):
            self.app.run()
            assert self.app._run_cli.called
    
    @pytest.mark.skip()
    @pytest.mark.unit()
    def test_run_cli(self):
        """
        Test the run_cli method.
        """
        with patch.object(self.app.services[Srv.CLI], "display_cli", return_value=None), \
             patch.object(self.app, "exit", return_value=None):
            self.app._run_cli()
            assert self.app.services[Srv.CLI].display_cli.called
            assert self.app.exit.called

    @pytest.mark.unit()
    def test_load_services_try(self):
        """
        Test the loading of services.
        """
        with patch("local.audio.AudioService.__new__", return_value=MagicMock()) as mock_audio, \
             patch("local.stt.SpeechToTextService.__new__", return_value=MagicMock()) as mock_stt, \
             patch("local.tts.TextToSpeech.__new__", return_value=MagicMock()) as mock_tts, \
             patch("local.text_gen.TextGenService.__new__", return_value=MagicMock()) as mock_text_gen, \
             patch("local.ir_service.IrService.__new__", return_value=MagicMock()) as mock_ir, \
             patch("local.weather.Weather.__new__", return_value=MagicMock()) as mock_weather, \
             patch("local.yle.YleNewsApi.__new__", return_value=MagicMock()) as mock_news:
            self.app._load_services()

            # Assert that the services are correctly assigned
            assert self.app.services[Srv.AUDIO] == mock_audio.return_value
            assert self.app.services[Srv.STT] == mock_stt.return_value
            assert self.app.services[Srv.TTS] == mock_tts.return_value
            assert self.app.services[Srv.TEXT_GEN] == mock_text_gen.return_value
            assert self.app.services[Srv.IR] == mock_ir.return_value
            assert self.app.services[Srv.WEATHER] == mock_weather.return_value
            assert self.app.services[Srv.NEWS] == mock_news.return_value

    @pytest.mark.unit()
    @pytest.mark.parametrize(
        "service",
        [
            "local.audio.AudioService.__new__",
            "local.stt.SpeechToTextService.__new__",
            "local.tts.TextToSpeech.__new__",
            "local.text_gen.TextGenService.__new__",
            "local.ir_service.IrService.__new__",
            "local.weather.Weather.__new__",
            "local.yle.YleNewsApi.__new__",
        ],
    )
    def test_load_services_except(self, service):
        """
        Test the loading of services with exceptions.
        """
        with patch(service, side_effect=Exception), \
             patch.object(self.app, "exit", return_value=None), \
             patch.object(self.app.logger, "error", return_value=None):
            self.app._load_services()
            assert self.app.logger.error.called
            assert self.app.exit.called
    
    @pytest.mark.unit()
    def test_setup_env(self):
        """
        Test the setup_env method.
        """
        with patch("os.path.exists", return_value=False), \
             patch.object(self.app, "_create_env_file", return_value=None):
            self.app._setup_env()
            assert self.app._create_env_file.called

    @pytest.mark.skip()
    @pytest.mark.unit()
    def test_find_project_root(self):
        """
        Test the find_project_root method.
        """
        with patch("pathlib.Path.exists", return_value=True):
            root = self.app._find_project_root()
            assert root == "/mock/root"
