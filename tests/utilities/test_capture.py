import unittest
from unittest.mock import MagicMock, patch
from utilities.capture import capture_still_request  # type: ignore
import cv2
import numpy as np


class TestCaptureStillRequest(unittest.TestCase):
    @patch("utilities.capture.cv2.cvtColor")
    @patch("utilities.capture.Image.fromarray")
    def test_capture_still_request(self, mock_fromarray, mock_cvtColor):
        # Create a mock camera object.
        cam = MagicMock()
        cam.config = {"image_output_path": "test_path"}
        cam.picam2.capture_metadata.return_value = {"metadata": "test_metadata"}
        cam.picam2.capture_array.return_value = np.zeros((100, 100), dtype=np.uint8)
        cam.make_filename.return_value = "test_image.jpg"

        # Mock the cv2 and PIL functions
        mock_cvtColor.return_value = np.zeros((100, 100, 3), dtype=np.uint8)
        mock_image = MagicMock()
        mock_fromarray.return_value = mock_image

        # Call the function.
        capture_still_request(cam)

        # Assertions
        cam.picam2.capture_metadata.assert_called_once()
        cam.picam2.capture_array.assert_called_once_with("raw")
        cam.make_filename.assert_called_once_with("test_path")

        # Use np.array_equal for array comparisons
        self.assertTrue(
            np.array_equal(
                mock_cvtColor.call_args[0][0], np.zeros((100, 100), dtype=np.uint8)
            )
        )
        self.assertEqual(mock_cvtColor.call_args[0][1], cv2.COLOR_BayerRG2BGR)

        self.assertTrue(
            np.array_equal(
                mock_fromarray.call_args[0][0], np.zeros((100, 100, 3), dtype=np.uint8)
            )
        )

        cam.picam2.helpers.save.assert_called_once_with(
            mock_image, {"metadata": "test_metadata"}, "test_image.jpg"
        )
        cam.generate_thumbnail.assert_called_once_with("i", "test_image.jpg")


if __name__ == "__main__":
    unittest.main()
