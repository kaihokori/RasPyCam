import threading
from picamera2.previews.null_preview import NullPreview


def pytest_configure(config):
    """Monkey patch the NullPreview class to handle the DeprecationWarning."""

    def patched_start(self, picam2):
        self.picam2 = picam2
        picam2.attach_preview(self)
        self._started.clear()
        self._abort.clear()

        self.thread = threading.Thread(target=self.thread_func, args=(picam2,))
        self.thread.daemon = True
        self.thread.start()
        self._started.wait()

    NullPreview.start = patched_start
