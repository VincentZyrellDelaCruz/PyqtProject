import os
import config
from functools import lru_cache
from concurrent.futures import ThreadPoolExecutor

from PyQt6.QtCore import (
    Qt, QSize, QUrl, QByteArray,
    QThreadPool, QRunnable, pyqtSignal, QObject
)
from PyQt6.QtGui import QPixmap, QIcon
from PyQt6.QtNetwork import QNetworkAccessManager, QNetworkRequest

import requests


_network_manager = QNetworkAccessManager()
_thread_pool = ThreadPoolExecutor(max_workers=8)

@lru_cache(maxsize=256)
def _cached_image_bytes(url: str) -> QByteArray:

    try:
        response = requests.get(url, timeout=6)
        response.raise_for_status()
        data = response.content

        return QByteArray(data)
    except Exception:
        return QByteArray()

class ImageLoaderSignals(QObject):
    finished = pyqtSignal(str, QByteArray)  # url, image_data

class ImageLoader(QRunnable):
    def __init__(self, url: str):
        super().__init__()
        self.url = url
        self.signals = ImageLoaderSignals()
        self._cancelled = False

    # Mark this loader as cancelled. The run() method will abort early.
    def cancel(self):
        self._cancelled = True

    def run(self):
        if self._cancelled:
            return
        data = _cached_image_bytes(self.url)
        if not self._cancelled:
            self.signals.finished.emit(self.url, data)

# Load placeholder once
def load_placeholder_pixmap() -> QPixmap:
    """Load placeholder image from assets. Returns gray square if missing."""
    path = os.path.join(config.BASE_DIR, "assets", "placeholder.png")
    pix = QPixmap()
    if os.path.exists(path):
        pix.load(path)
    if pix.isNull():
        pix = QPixmap(64, 64)
        pix.fill(Qt.GlobalColor.gray)
    return pix

