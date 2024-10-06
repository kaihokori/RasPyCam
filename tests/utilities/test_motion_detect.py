import os
import unittest
from unittest.mock import patch, MagicMock
from utilities.motion_detect import (  # type: ignore
    setup_motion_pipe,
    send_motion_command,
)


class TestMotionDetect(unittest.TestCase):
    @patch("os.path.exists")
    @patch("os.makedirs")
    @patch("os.mkfifo")
    def test_setup_motion_pipe(self, mock_mkfifo, mock_makedirs, mock_exists):
        # Test when directory and pipe do not exist
        mock_exists.side_effect = [False, False]
        setup_motion_pipe("/fake/path/motion_pipe")
        mock_makedirs.assert_called_once_with("/fake/path")
        mock_mkfifo.assert_called_once_with("/fake/path/motion_pipe", 0o6666)

        # Reset mocks
        mock_makedirs.reset_mock()
        mock_mkfifo.reset_mock()
        mock_exists.reset_mock()

        # Test when directory exists but pipe does not
        mock_exists.side_effect = [True, False]
        setup_motion_pipe("/fake/path/motion_pipe")
        mock_makedirs.assert_not_called()
        mock_mkfifo.assert_called_with("/fake/path/motion_pipe", 0o6666)

        # Reset mocks
        mock_makedirs.reset_mock()
        mock_mkfifo.reset_mock()
        mock_exists.reset_mock()

        # Test when both directory and pipe exist
        mock_exists.side_effect = [True, True]
        setup_motion_pipe("/fake/path/motion_pipe")
        mock_makedirs.assert_not_called()
        mock_mkfifo.assert_not_called()

    @patch("os.open")
    @patch("os.fdopen")
    def test_send_motion_command(self, mock_fdopen, mock_open):
        mock_file = MagicMock()
        mock_fdopen.return_value = mock_file

        send_motion_command("/fake/path/motion_pipe", "1")
        mock_open.assert_called_once_with(
            "/fake/path/motion_pipe", os.O_RDWR | os.O_NONBLOCK, 0o666
        )
        mock_fdopen.assert_called_once_with(mock_open.return_value, "w")
        mock_file.write.assert_called_once_with("1")
        mock_file.close.assert_called_once()

    # @patch("utilities.motion_detect.send_motion_command")
    # @patch("core.model.CameraCoreModel.process_running", new_callable=MagicMock)
    # def test_motion_detection_thread(
    #     self, mock_process_running, mock_send_motion_command
    # ):
    #     mock_process_running.side_effect = [True, False]  # Run loop once

    #     cam = MagicMock()
    #     cam.picam2.camera_configuration.return_value = {"lores": {"size": (640, 480)}}
    #     cam.config = {
    #         "motion_initframes": 1,
    #         "motion_threshold": 7,
    #         "motion_mode": "monitor",
    #         "motion_startframes": 1,
    #         "motion_stopframes": 1,
    #         "motion_pipe": "/fake/path/motion_pipe",
    #     }
    #     cam.picam2.capture_buffer.return_value = np.zeros((640 * 480,), dtype=np.uint8)
    #     cam.motion_detection = True
    #     cam.detected_motion = False
    #     cam.motion_active_count = 0
    #     cam.motion_still_count = 0

    #     # Add a timeout to prevent infinite loop
    #     import threading

    #     def run_thread():
    #         print("Starting motion detection thread...")
    #         motion_detection_thread(cam)
    #         print("Motion detection thread finished.")

    #     thread = threading.Thread(target=run_thread)
    #     thread.start()
    #     thread.join(timeout=5)  # Timeout after 5 seconds.

    #     if thread.is_alive():
    #         self.fail("motion_detection_thread did not exit in time")

    #     self.assertEqual(cam.motion_active_count, 1)
    #     self.assertTrue(cam.detected_motion)
    #     mock_send_motion_command.assert_called_once_with("/fake/path/motion_pipe", "1")


if __name__ == "__main__":
    unittest.main()
