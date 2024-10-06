import unittest
from unittest.mock import MagicMock, patch
from utilities.preview import generate_preview  # type: ignore


class TestGeneratePreview(unittest.TestCase):
    @patch("os.rename")
    def test_generate_preview(self, mock_rename):
        # Mock camera and request objects
        cam = MagicMock()
        request = MagicMock()

        # Set up mock configurations
        cam.config = {
            "preview_path": "/mock/path/preview.jpg",
            "preview_size": (640, 480),
        }

        # Mock the methods of request
        request.make_image.return_value = "mock_image"
        request.get_metadata.return_value = "mock_metadata"

        # Mock the save method
        cam.picam2.helpers.save = MagicMock()

        # Call the function
        generate_preview(cam, request)

        # Check if make_image was called with correct parameters
        request.make_image.assert_called_once_with("main", 640, 480)

        # Check if save was called with correct parameters
        cam.picam2.helpers.save.assert_called_once_with(
            "mock_image", "mock_metadata", "/mock/path/preview.jpg.part.jpg"
        )

        # Check if os.rename was called with correct parameters
        mock_rename.assert_called_once_with(
            "/mock/path/preview.jpg.part.jpg", "/mock/path/preview.jpg"
        )


if __name__ == "__main__":
    unittest.main()
