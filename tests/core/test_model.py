from datetime import datetime
import os
import unittest
import tempfile
import json
from unittest.mock import call, mock_open, patch, MagicMock
from core.model import CameraCoreModel  # type: ignore


# Base Test Class for CameraCoreModel setup
class TestCameraCoreModelBase(unittest.TestCase):
    @patch("core.model.Picamera2")
    def setUp(self, mock_picamera2):
        """Set up the test case with a mocked Picamera2 instance."""
        self.mock_picamera2 = mock_picamera2.return_value
        self.mock_picamera2.stop_encoder = MagicMock()
        self.mock_picamera2.stop = MagicMock()
        self.mock_picamera2.start = MagicMock()
        self.mock_picamera2.close = MagicMock()
        self.mock_picamera2.capture_request = MagicMock()
        self.mock_picamera2.sensor_resolution = (1920, 1080)
        self.mock_picamera2.camera_config = {
            "main": {"size": (1920, 1080), "format": "YUV420"}
        }
        self.model = CameraCoreModel(0, None)


# Test Initialization Functionality
class TestCameraCoreModelInit(unittest.TestCase):
    @patch("core.model.Picamera2")
    def test_init_no_config_file(self, mock_picamera2):
        """Test initialisation without a configuration file."""
        camera_index = 0
        config_path = None

        mock_picamera2.return_value.camera_config = {
            "main": {"size": (1920, 1080), "format": "YUV420"}
        }
        mock_picamera2.return_value.sensor_resolution = (1920, 1080)

        model = CameraCoreModel(camera_index, config_path)

        self.assertEqual(model.config["preview_size"], (512, 288))
        self.assertEqual(model.config["preview_path"], "/tmp/preview/cam_preview.jpg")
        mock_picamera2.assert_called_once_with(camera_index)

    @patch("core.model.Picamera2")
    def test_init_with_config_file(self, mock_picamera2):
        """Test initialisation with a configuration file."""
        camera_index = 0
        mock_picamera2.return_value.camera_config = {
            "main": {"size": (1920, 1080), "format": "YUV420"}
        }
        mock_picamera2.return_value.sensor_resolution = (1920, 1080)

        with tempfile.NamedTemporaryFile(delete=False, mode="w") as temp_config_file:
            config_data = {
                "preview_size": [768, 432],
                "status_file": "/tmp/status_mjpeg.txt",
                "control_file": "/tmp/FIFO",
                "motion_pipe": "/tmp/motionFIFO",
                "video_width": 1920,
                "video_height": 1080,
                "video_bitrate": 17000000,
                "motion_mode": "internal",
                "motion_threshold": 7.0,
                "motion_initframes": 0,
                "motion_startframes": 3,
                "motion_stopframes": 50,
            }
            json.dump(config_data, temp_config_file)
            config_path = temp_config_file.name

        model = CameraCoreModel(camera_index, config_path)
        self.assertEqual(model.config["preview_size"], [768, 432])
        mock_picamera2.assert_called_once_with(camera_index)
        os.remove(config_path)


class TestCameraCoreModelAutostartAndMotionDetection(unittest.TestCase):
    @patch("core.model.Picamera2")
    def test_autostart_and_motion_detection_enabled(self, mock_picamera2):
        """Test with autostart and motion detection both enabled."""
        camera_index = 0
        mock_picamera2.return_value.camera_config = {
            "main": {"size": (1920, 1080), "format": "YUV420"}
        }
        mock_picamera2.return_value.sensor_resolution = (1920, 1080)

        config = {
            "autostart": True,
            "motion_detection": True,
        }

        with tempfile.NamedTemporaryFile(delete=False, mode="w") as temp_config_file:
            json.dump(config, temp_config_file)
            config_path = temp_config_file.name

        model = CameraCoreModel(camera_index, config_path)

        self.assertTrue(model.motion_detection)
        mock_picamera2.return_value.start.assert_called_once()
        os.remove(config_path)

    @patch("core.model.Picamera2")
    def test_autostart_enabled_motion_detection_disabled(self, mock_picamera2):
        """Test with autostart enabled and motion detection disabled."""
        camera_index = 0
        mock_picamera2.return_value.camera_config = {
            "main": {"size": (1920, 1080), "format": "YUV420"}
        }
        mock_picamera2.return_value.sensor_resolution = (1920, 1080)

        config = {
            "autostart": True,
            "motion_detection": False,
        }

        with tempfile.NamedTemporaryFile(delete=False, mode="w") as temp_config_file:
            json.dump(config, temp_config_file)
            config_path = temp_config_file.name

        model = CameraCoreModel(camera_index, config_path)

        self.assertFalse(model.motion_detection)
        mock_picamera2.return_value.start.assert_called_once()
        os.remove(config_path)

    @patch("core.model.Picamera2")
    @patch("builtins.print")
    def test_autostart_disabled(self, mock_print, mock_picamera2):
        """Test with autostart disabled."""
        camera_index = 0
        mock_picamera2.return_value.camera_config = {
            "main": {"size": (1920, 1080), "format": "YUV420"}
        }
        mock_picamera2.return_value.sensor_resolution = (1920, 1080)

        config = {
            "autostart": False,
        }

        with tempfile.NamedTemporaryFile(delete=False, mode="w") as temp_config_file:
            json.dump(config, temp_config_file)
            config_path = temp_config_file.name

        model = CameraCoreModel(camera_index, config_path)
        self.assertIsNotNone(model)

        mock_print.assert_called_with("no autostart")
        mock_picamera2.return_value.start.assert_not_called()
        os.remove(config_path)


# Test stop_all Function
class TestCameraCoreModelStopAll(TestCameraCoreModelBase):
    def test_stop_all(self):
        """Test the stop_all function."""
        self.model.video_encoder = MagicMock()
        self.model.video_encoder.running = True

        self.model.stop_all()

        self.mock_picamera2.stop_encoder.assert_called_once_with(
            self.model.video_encoder
        )
        self.mock_picamera2.stop.assert_called_once()
        self.assertFalse(self.model.capturing_video)
        self.assertFalse(self.model.capturing_still)
        self.assertFalse(self.model.motion_detection)
        self.assertFalse(self.model.timelapse_on)


# Test reset_motion_state Function
class TestCameraCoreModelResetMotionState(TestCameraCoreModelBase):
    def test_reset_motion_state(self):
        """Test the reset_motion_state function."""
        self.model.detected_motion = True
        self.model.motion_still_count = 10
        self.model.motion_active_count = 5

        self.model.reset_motion_state()

        self.assertFalse(self.model.detected_motion)
        self.assertEqual(self.model.motion_still_count, 0)
        self.assertEqual(self.model.motion_active_count, 0)


# Test restart Function
class TestCameraCoreModelRestart(TestCameraCoreModelBase):
    def test_restart(self):
        """Test the restart function."""
        self.mock_picamera2.stop.reset_mock()
        self.mock_picamera2.start.reset_mock()

        self.model.restart()

        self.mock_picamera2.stop.assert_called_once()
        self.mock_picamera2.start.assert_called_once()
        self.assertEqual(self.model.current_status, "ready")


# Test set_status Function
class TestCameraCoreModelSetStatus(TestCameraCoreModelBase):
    def test_set_status_with_custom_status(self):
        """Test setting a custom status directly."""
        self.model.set_status("custom_status")
        self.assertEqual(self.model.current_status, "custom_status")

    def test_set_status_halted(self):
        """Test setting status when camera is not started."""
        self.mock_picamera2.started = False
        self.model.set_status()
        self.assertEqual(self.model.current_status, "halted")

    def test_set_status_video(self):
        """Test setting status when capturing video without motion detection."""
        self.mock_picamera2.started = True
        self.model.capturing_video = True
        self.model.motion_detection = False
        self.model.set_status()
        self.assertEqual(self.model.current_status, "video")

    def test_set_status_video_motion(self):
        """Test setting status when capturing video with motion detection."""
        self.mock_picamera2.started = True
        self.model.capturing_video = True
        self.model.motion_detection = True
        self.model.set_status()
        self.assertEqual(self.model.current_status, "video_motion")

    def test_set_status_image(self):
        """Test setting status when capturing still image."""
        self.mock_picamera2.started = True
        self.model.capturing_still = True
        self.model.set_status()
        self.assertEqual(self.model.current_status, "image")

    def test_set_status_motion(self):
        """Test setting status when not capturing but motion detection is active."""
        self.mock_picamera2.started = True
        self.model.motion_detection = True
        self.model.set_status()
        self.assertEqual(self.model.current_status, "motion")

    def test_set_status_ready(self):
        """Test setting status when the camera is ready (no video or still capture, no motion)."""
        self.mock_picamera2.started = True
        self.model.capturing_video = False
        self.model.capturing_still = False
        self.model.motion_detection = False
        self.model.set_status()
        self.assertEqual(self.model.current_status, "ready")


# Test Make Filename Function
class TestCameraCoreModelMakeFilename(unittest.TestCase):
    @patch("core.model.datetime")
    @patch("core.model.Picamera2")
    def test_make_filename(self, mock_picamera2, mock_datetime):
        """Test the make_filename function with a mock datetime and image/video index."""

        mock_datetime.now.return_value = datetime(2024, 12, 25, 14, 0, 0, 123000)

        mock_picamera2_instance = MagicMock()
        mock_picamera2_instance.camera_config = {
            "main": {"size": (1920, 1080), "format": "RGB888"}
        }
        mock_picamera2_instance.sensor_resolution = (1920, 1080)
        mock_picamera2.return_value = mock_picamera2_instance

        model = CameraCoreModel(0, None)

        model.still_image_index = 5
        model.video_file_index = 10

        filename_template = "im_%i_%Y%M%D_%h%m%s.jpg"
        expected_filename = "im_0005_20241225_140000.jpg"
        generated_filename = model.make_filename(filename_template)

        self.assertEqual(generated_filename, expected_filename)

        filename_template = "vi_%v_%Y%M%D_%h%m%s.mp4"
        expected_filename = "vi_0010_20241225_140000.mp4"
        generated_filename = model.make_filename(filename_template)

        self.assertEqual(generated_filename, expected_filename)


# Test Make Filecounts Function
class TestCameraCoreModelMakeFilecounts(TestCameraCoreModelBase):
    @patch("os.listdir")
    def test_make_filecounts(self, mock_listdir):
        """Test make_filecounts with both image and video thumbnails."""
        mock_listdir.return_value = [
            "im_0001.th",
            "im_0003.th",
            "vi_0002.th",
            "vi_0005.th",
        ]

        self.model.make_filecounts()

        self.assertEqual(self.model.still_image_index, 4)
        self.assertEqual(self.model.video_file_index, 6)

    @patch("os.listdir")
    def test_make_filecounts_with_no_files(self, mock_listdir):
        """Test make_filecounts when there are no thumbnails."""
        mock_listdir.return_value = []

        self.model.make_filecounts()

        self.assertEqual(self.model.still_image_index, 1)
        self.assertEqual(self.model.video_file_index, 1)

    @patch("os.listdir")
    def test_make_filecounts_with_invalid_files(self, mock_listdir):
        """Test make_filecounts when there are invalid filenames in the directory."""
        mock_listdir.return_value = ["im_invalid.th", "vi_invalid.th", "randomfile.txt"]

        self.model.make_filecounts()

        self.assertEqual(self.model.still_image_index, 1)
        self.assertEqual(self.model.video_file_index, 1)

    @patch("os.listdir")
    def test_make_filecounts_mixed_filenames(self, mock_listdir):
        """Test make_filecounts when there is a mix of valid and invalid files."""
        mock_listdir.return_value = [
            "im_0001.th",
            "vi_0002.th",
            "invalidfile.txt",
            "im_invalid.th",
        ]

        self.model.make_filecounts()

        self.assertEqual(self.model.still_image_index, 2)
        self.assertEqual(self.model.video_file_index, 3)

    @patch("os.listdir")
    def test_make_filecounts_with_large_index(self, mock_listdir):
        """Test make_filecounts with large image and video indexes."""
        mock_listdir.return_value = ["im_0999.th", "vi_1000.th"]

        self.model.make_filecounts()

        self.assertEqual(self.model.still_image_index, 1000)
        self.assertEqual(self.model.video_file_index, 1001)


# Test teardown Function
class TestCameraCoreModelTeardown(unittest.TestCase):
    @patch("core.model.Picamera2")
    @patch("os.path.exists")
    @patch("os.remove")
    @patch("os.makedirs")
    def test_teardown(self, mock_makedirs, mock_remove, mock_exists, mock_picamera2):
        """Test the teardown function."""
        mock_picamera2_instance = mock_picamera2.return_value
        mock_picamera2_instance.stop_encoder = MagicMock()
        mock_picamera2_instance.stop = MagicMock()
        mock_picamera2_instance.close = MagicMock()

        mock_picamera2_instance.sensor_resolution = (1920, 1080)
        mock_picamera2_instance.camera_config = {
            "main": {"size": (1920, 1080), "format": "YUV420"}
        }

        mock_exists.side_effect = lambda path: path in [
            "/tmp/preview/cam_preview.jpg",
            "/tmp/preview/cam_preview.jpg.part.jpg",
        ]

        model = CameraCoreModel(0, None)
        model.video_encoder = MagicMock()
        model.video_encoder.running = True

        model.teardown()

        mock_picamera2_instance.stop_encoder.assert_called_once_with(
            model.video_encoder
        )
        mock_picamera2_instance.stop.assert_called_once()
        mock_picamera2_instance.close.assert_called_once()

        mock_remove.assert_any_call("/tmp/preview/cam_preview.jpg")
        mock_remove.assert_any_call("/tmp/preview/cam_preview.jpg.part.jpg")


# Test make_output_directories Function
class TestCameraCoreModelMakeOutputDirectories(unittest.TestCase):
    @patch("os.makedirs")
    @patch("os.path.exists")
    def test_make_output_directories(self, mock_exists, mock_makedirs):
        """Test the make_output_directories function."""
        mock_exists.return_value = False
        model = CameraCoreModel(0, None)
        model.make_output_directories()

        expected_calls = [
            call(os.path.dirname(model.config["preview_path"])),
            call(os.path.dirname(model.config["image_output_path"])),
            call(os.path.dirname(model.config["lapse_output_path"])),
            call(os.path.dirname(model.config["video_output_path"])),
            call(os.path.dirname(model.config["media_path"])),
            call(os.path.dirname(model.config["status_file"])),
        ]
        mock_makedirs.assert_has_calls(expected_calls, any_order=True)


# Test config handling functions
class TestCameraCoreModelConfig(unittest.TestCase):
    @patch("core.model.Picamera2", autospec=True)
    @patch(
        "builtins.open",
        new_callable=mock_open,
        read_data='{"preview_size": [1024, 768]}',
    )
    def test_read_config_file(self, mock_file, MockPicamera2):
        """Test the read_config_file function."""
        mock_picamera = MockPicamera2.return_value
        mock_picamera.camera_config = {
            "main": {"size": (1920, 1080), "format": "YUV420"}
        }
        mock_picamera.sensor_resolution = (1920, 1080)

        model = CameraCoreModel(0, None)
        model.read_config_file("dummy_path")

        self.assertEqual(model.config["preview_size"], [1024, 768])

    @patch("core.model.Picamera2", autospec=True)
    def test_process_configs_from_file(self, MockPicamera2):
        """Test the process_configs_from_file function."""
        mock_picamera = MockPicamera2.return_value
        mock_picamera.camera_config = {
            "main": {"size": (1920, 1080), "format": "YUV420"}
        }
        mock_picamera.sensor_resolution = (1920, 1080)

        model = CameraCoreModel(0, None)
        parsed_configs = {"preview_size": [1024, 768]}
        model.process_configs_from_file(parsed_configs)

        self.assertEqual(model.config["preview_size"], [1024, 768])


# Test capture_request Function
class TestCameraCoreModelCaptureRequest(TestCameraCoreModelBase):
    def test_capture_request(self):
        """Test the capture_request function."""
        # Setup mock for capture_request return value
        self.mock_picamera2.capture_request.return_value = "mocked_capture_request"

        # Call the capture_request method
        result = self.model.capture_request()

        # Assert that capture_request was called and returned the correct value
        self.mock_picamera2.capture_request.assert_called_once()
        self.assertEqual(result, "mocked_capture_request")


# Test generate_thumbnail Function
class TestGenerateThumbnail(unittest.TestCase):
    @patch("shutil.copyfile")
    @patch("core.model.Picamera2")
    def test_generate_thumbnail_image(self, mock_picamera2, mock_copyfile):
        """Test thumbnail generation for image files ('i')."""
        mock_picamera2_instance = mock_picamera2.return_value
        mock_picamera2_instance.stop_encoder = MagicMock()
        mock_picamera2_instance.stop = MagicMock()
        mock_picamera2_instance.start = MagicMock()
        mock_picamera2_instance.close = MagicMock()
        mock_picamera2_instance.sensor_resolution = (1920, 1080)
        mock_picamera2_instance.camera_config = {
            "main": {"size": (1920, 1080), "format": "YUV420"}
        }

        model = CameraCoreModel(0, None)
        model.still_image_index = 5
        model.config["preview_path"] = "/tmp/preview/cam_preview.jpg"

        filetype = "i"
        filepath = "/tmp/media/im_0005_20240101_120000.jpg"

        model.generate_thumbnail(filetype, filepath)

        expected_thumbnail_path = "/tmp/media/im_0005_20240101_120000.i5.th.jpg"
        mock_copyfile.assert_called_once_with(
            "/tmp/preview/cam_preview.jpg", expected_thumbnail_path
        )
        self.assertEqual(model.still_image_index, 6)

    @patch("shutil.copyfile")
    @patch("core.model.Picamera2")
    def test_generate_thumbnail_video(self, mock_picamera2, mock_copyfile):
        """Test thumbnail generation for video files ('v')."""
        mock_picamera2_instance = mock_picamera2.return_value
        mock_picamera2_instance.stop_encoder = MagicMock()
        mock_picamera2_instance.stop = MagicMock()
        mock_picamera2_instance.start = MagicMock()
        mock_picamera2_instance.close = MagicMock()
        mock_picamera2_instance.sensor_resolution = (1920, 1080)
        mock_picamera2_instance.camera_config = {
            "main": {"size": (1920, 1080), "format": "YUV420"}
        }

        model = CameraCoreModel(0, None)
        model.video_file_index = 3
        model.config["preview_path"] = "/tmp/preview/cam_preview.jpg"

        filetype = "v"
        filepath = "/tmp/media/vi_0003_20240101_120000.mp4"

        model.generate_thumbnail(filetype, filepath)

        expected_thumbnail_path = "/tmp/media/vi_0003_20240101_120000.v3.th.jpg"
        mock_copyfile.assert_called_once_with(
            "/tmp/preview/cam_preview.jpg", expected_thumbnail_path
        )
        self.assertEqual(model.video_file_index, 4)

    @patch("shutil.copyfile")
    @patch("core.model.Picamera2")
    def test_generate_thumbnail_timelapse(self, mock_picamera2, mock_copyfile):
        """Test thumbnail generation for timelapse files ('t')."""
        mock_picamera2_instance = mock_picamera2.return_value
        mock_picamera2_instance.stop_encoder = MagicMock()
        mock_picamera2_instance.stop = MagicMock()
        mock_picamera2_instance.start = MagicMock()
        mock_picamera2_instance.close = MagicMock()
        mock_picamera2_instance.sensor_resolution = (1920, 1080)
        mock_picamera2_instance.camera_config = {
            "main": {"size": (1920, 1080), "format": "YUV420"}
        }

        model = CameraCoreModel(0, None)
        model.still_image_index = 8
        model.config["preview_path"] = "/tmp/preview/cam_preview.jpg"

        filetype = "t"
        filepath = "/tmp/media/tl_0008_20240101_120000.jpg"

        model.generate_thumbnail(filetype, filepath)

        expected_thumbnail_path = "/tmp/media/tl_0008_20240101_120000.t8.th.jpg"
        mock_copyfile.assert_called_once_with(
            "/tmp/preview/cam_preview.jpg", expected_thumbnail_path
        )
        self.assertEqual(model.still_image_index, 9)


# Test print_to_logfile Function
class TestCameraCoreModelPrintToLogfile(TestCameraCoreModelBase):
    @patch("os.open")
    @patch("os.fdopen")
    def test_print_to_logfile(self, mock_fdopen, mock_open):
        """Test the print_to_logfile function."""
        mock_open.return_value = 1
        mock_file = MagicMock()
        mock_fdopen.return_value = mock_file

        test_message = "This is a test log message."

        self.model.config["log_size"] = 5000

        self.model.print_to_logfile(test_message)

        mock_open.assert_called_once_with(
            self.model.config["log_file"], os.O_RDWR | os.O_NONBLOCK, 0o777
        )

        mock_fdopen.assert_called_once_with(1, "a")

        expected_timestring = "{" + datetime.now().strftime("%Y/%m/%d %H:%M:%S") + "} "
        expected_contents = expected_timestring + test_message + "\n"
        mock_file.write.assert_called_once_with(expected_contents)

        mock_file.close.assert_called_once()

    @patch("os.open")
    @patch("os.fdopen")
    def test_print_to_logfile_log_size_zero(self, mock_fdopen, mock_open):
        """Test that print_to_logfile does not write when log_size is 0."""
        self.model.config["log_size"] = 0

        self.model.print_to_logfile("This message should not be logged.")

        mock_open.assert_not_called()
        mock_fdopen.assert_not_called()


if __name__ == "__main__":
    unittest.main()
