import os
from unittest.mock import patch
from core.process import setup_fifo  # type: ignore


@patch("os.mkfifo")
@patch("os.open")
def test_setup_fifo(mock_open, mock_mkfifo):
    # Test setting up a FIFO path
    setup_fifo("/tmp/control_fifo")

    # Assert that the FIFO file was created and opened
    mock_mkfifo.assert_called_once_with("/tmp/control_fifo", 0o6666)
    mock_open.assert_called_once_with(
        "/tmp/control_fifo", os.O_RDONLY | os.O_NONBLOCK, 0o666
    )
