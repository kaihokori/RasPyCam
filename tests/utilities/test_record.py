import unittest
from unittest.mock import MagicMock, patch

from utilities.record import start_recording, stop_recording, toggle_cam_record  # type: ignore


class TestStartRecording(unittest.TestCase):
    def setUp(self):
        self.cam = MagicMock()
        self.cam.config = {"video_output_path": "test_path"}
        self.cam.make_filename.return_value = "test_output.mp4"
        self.cam.video_encoder = MagicMock()
        self.cam.picam2 = MagicMock()
        self.cam.capturing_video = False
        self.cam.current_video_path = None

    @patch("utilities.record.FfmpegOutput")
    def test_start_recording_success(self, MockFfmpegOutput):
        # Test the standard path when the camera is not capturing video
        start_recording(self.cam)
        self.cam.make_filename.assert_called_once_with("test_path")
        self.assertEqual(self.cam.current_video_path, "test_output.mp4")
        MockFfmpegOutput.assert_called_once_with("test_output.mp4")
        self.cam.picam2.start_encoder.assert_called_once_with(
            self.cam.video_encoder, MockFfmpegOutput.return_value, name="main"
        )
        self.assertTrue(self.cam.capturing_video)
        self.cam.set_status.assert_called_once_with("video")

    def test_start_recording_already_capturing(self):
        # Test the path when the camera is already capturing video
        self.cam.capturing_video = True
        start_recording(self.cam)
        self.cam.print_to_logfile.assert_called_once_with("Already capturing. Ignore")
        self.cam.picam2.start_encoder.assert_not_called()
        self.assertTrue(self.cam.capturing_video)


class TestStopRecording(unittest.TestCase):
    def setUp(self):
        self.cam = MagicMock()
        self.cam.video_encoder = MagicMock()
        self.cam.picam2 = MagicMock()
        self.cam.capturing_video = False
        self.cam.current_video_path = "test_output.mp4"

    def test_stop_recording_success(self):
        # Test the standard path when the camera is capturing video
        self.cam.capturing_video = True
        self.cam.video_encoder.running = True
        stop_recording(self.cam)
        self.cam.print_to_logfile.assert_called_once_with("Capturing stopped")
        self.cam.picam2.stop_encoder.assert_called_once()
        self.cam.generate_thumbnail.assert_called_once_with("v", "test_output.mp4")
        self.assertEqual(self.cam.current_video_path, None)
        self.assertFalse(self.cam.capturing_video)
        self.cam.set_status.assert_called_once_with("ready")

    def test_stop_recording_not_capturing(self):
        # Test the path when the camera is not capturing video
        stop_recording(self.cam)
        self.cam.print_to_logfile.assert_called_once_with("Already stopped. Ignore")
        self.cam.picam2.stop_encoder.assert_not_called()


class TestToggleCamRecord(unittest.TestCase):
    def setUp(self):
        self.cam = MagicMock()

    @patch("utilities.record.start_recording")
    def test_toggle_record_start(self, mock_start_recording):
        # Test toggling the camera recording on
        toggle_cam_record(self.cam, True)
        mock_start_recording.assert_called_once_with(self.cam)

    @patch("utilities.record.stop_recording")
    def test_toggle_record_stop(self, mock_stop_recording):
        # Test toggling the camera recording off
        toggle_cam_record(self.cam, False)
        mock_stop_recording.assert_called_once_with(self.cam)


if __name__ == "__main__":
    unittest.main()
