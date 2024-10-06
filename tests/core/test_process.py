import unittest
from unittest.mock import patch, MagicMock, mock_open
import os
import signal
import threading
import time
import pytest

from core.process import (  # type: ignore
    on_sigint_sigterm,
    update_status_file,
    setup_fifo,
    parse_incoming_commands,
    read_pipe,
    execute_command,
    show_preview,
    start_background_process,
)


# Test for the on_sigint_sigterm function
class TestOnSigintSigterm(unittest.TestCase):
    @patch("core.process.CameraCoreModel")
    def test_on_sigint_sigterm(self, mock_model):
        on_sigint_sigterm(signal.SIGINT, None)
        mock_model.process_running = False


# Test for the update_status_file function
class TestUpdateStatusFile(unittest.TestCase):
    @patch("os.makedirs")
    @patch("os.path.exists", return_value=False)
    @patch("builtins.open", new_callable=mock_open)
    def test_update_status_file(self, mock_open, mock_exists, mock_makedirs):
        mock_model = MagicMock()
        mock_model.current_status = "ready"
        mock_model.config = {"status_file": "/path/to/status_file"}

        update_status_file(mock_model)

        mock_makedirs.assert_called_once_with("/path/to")
        mock_open.assert_called_once_with("/path/to/status_file", "w")
        mock_open().write.assert_called_once_with("ready")


# Test for the setup_fifo function
class TestSetupFifo(unittest.TestCase):
    @patch("os.makedirs")
    @patch("os.path.exists", side_effect=[False, False])
    @patch("os.mkfifo")
    @patch("os.open")
    @patch("os.read", side_effect=BlockingIOError)
    def test_setup_fifo(
        self, mock_read, mock_open, mock_mkfifo, mock_exists, mock_makedirs
    ):
        result = setup_fifo("/path/to/fifo")
        self.assertFalse(result)
        mock_makedirs.assert_called_once_with("/path/to")
        mock_mkfifo.assert_called_once_with("/path/to/fifo", 0o6666)
        mock_open.assert_called_once_with(
            "/path/to/fifo", os.O_RDONLY | os.O_NONBLOCK, 0o666
        )


# Test for the parse_incoming_commands function
class TestParseIncomingCommands(unittest.TestCase):
    @patch("os.read", return_value=b"ru 1")
    @patch("core.process.read_pipe")
    @patch("core.process.CameraCoreModel")
    def test_parse_incoming_commands(self, mock_model, mock_read_pipe, mock_read):
        mock_model.process_running = True
        mock_model.fifo_fd = 1
        mock_model.fifo_interval = 0.01
        mock_model.command_queue = []
        mock_model.cmd_queue_lock = threading.Lock()

        mock_read_pipe.return_value = ("ru", "1")

        thread = threading.Thread(target=parse_incoming_commands)
        thread.start()
        time.sleep(0.005)
        mock_model.process_running = False
        thread.join()

        self.assertEqual(mock_model.command_queue, [("ru", "1")])


# Test for the read_pipe function
class TestReadPipe(unittest.TestCase):
    @patch("os.read", return_value=b"ru 1")
    @patch("core.process.CameraCoreModel")
    def test_read_pipe(self, mock_model, mock_read):
        mock_model.MAX_COMMAND_LEN = 1024
        mock_model.VALID_COMMANDS = ["ru", "im", "ca", "md"]

        result = read_pipe(1)
        self.assertEqual(result, ("ru", "1"))


# Test for the execute_command function
class TestExecuteCommand(unittest.TestCase):
    @patch("core.process.update_status_file")
    @patch("core.process.capture_still_request")
    @patch("core.process.toggle_cam_record")
    @patch("core.process.CameraCoreModel")
    def test_execute_command(self, mock_model, mock_toggle, mock_capture, mock_update):
        mock_model.current_status = "ready"
        mock_model.motion_detection = False

        mock_thread1 = MagicMock(spec=threading.Thread)
        mock_thread2 = MagicMock(spec=threading.Thread)
        mock_threads = [mock_thread1, mock_thread2]

        # Test for 'ru' command (restart)
        execute_command(("ru", "1"), mock_model, threads=mock_threads)
        mock_model.restart.assert_called_once()

        # Test for 'im' command (image capture)
        execute_command(("im", ""), mock_model, threads=mock_threads)
        mock_capture.assert_called_once_with(mock_model)

        # Test for 'ca' command (start video recording)
        execute_command(("ca", "1"), mock_model, threads=mock_threads)
        mock_toggle.assert_called_once_with(mock_model, True)

        # Test for 'md' command (motion detection on)
        execute_command(("md", "1"), mock_model, threads=mock_threads)
        self.assertTrue(mock_model.motion_detection)

        # Test for 'md' command (motion detection off)
        execute_command(("md", "0"), mock_model, threads=mock_threads)
        self.assertFalse(mock_model.motion_detection)


# Test for the show_preview function
class TestShowPreview(unittest.TestCase):
    @patch("core.process.generate_preview")
    @patch("core.process.CameraCoreModel")
    def test_show_preview(self, mock_camera, mock_generate_preview):
        mock_camera_instance = mock_camera.return_value
        mock_camera_instance.current_status = "running"

        mock_request = MagicMock()
        mock_camera_instance.capture_request.return_value = mock_request

        def stop_preview():
            time.sleep(0.1)
            mock_camera_instance.current_status = "halted"

        stop_thread = threading.Thread(target=stop_preview)
        stop_thread.start()

        show_preview(mock_camera_instance)

        mock_camera_instance.capture_request.assert_called()
        mock_generate_preview.assert_called_with(mock_camera_instance, mock_request)
        mock_request.release.assert_called()

        stop_thread.join()


# Test for the start_background_process function
class TestStartBackgroundProcess(unittest.TestCase):
    @pytest.mark.skip(reason="Skipping this test temporarily")
    @patch("core.process.Picamera2.global_camera_info", return_value=[{"Num": 0}])
    @patch("core.process.CameraCoreModel")
    @patch("core.process.setup_fifo", return_value=True)
    @patch("core.process.setup_motion_pipe")
    @patch("core.process.update_status_file")
    @patch("threading.Thread")
    def test_start_background_process(
        self,
        mock_thread,
        mock_update,
        mock_setup_motion,
        mock_setup_fifo,
        mock_model,
        mock_camera_info,
    ):
        mock_model_instance = mock_model.return_value
        mock_model_instance.config = {
            "control_file": "/path/to/control_file",
            "motion_pipe": "/path/to/motion_pipe",
        }
        mock_model_instance.command_queue = MagicMock()
        mock_model_instance.command_queue.pop.side_effect = [("ru", "1")]

        start_background_process("/path/to/config")

        mock_camera_info.assert_called_once()
        mock_model.assert_called_once_with(0, "/path/to/config")
        mock_setup_fifo.assert_called_once_with("/path/to/control_file")
        mock_setup_motion.assert_called_once_with("/path/to/motion_pipe")
        mock_update.assert_called()
        mock_thread.assert_called()


if __name__ == "__main__":
    unittest.main()
