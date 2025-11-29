"""Request manager to handle debouncing and prevent UI freezing."""
from PyQt6.QtCore import QTimer, QObject, pyqtSignal
from functools import wraps
import time


class DebouncedFunction:
    """Debounce rapid function calls."""
    def __init__(self, delay_ms=300):
        self.delay_ms = delay_ms
        self.timer = None
        self.pending_call = None
    
    def __call__(self, func):
        @wraps(func)
        def wrapper(*args, **kwargs):
            # Cancel previous timer if exists
            if self.timer is not None:
                self.timer.stop()
            
            # Create new timer
            self.timer = QTimer()
            self.timer.setSingleShot(True)
            self.timer.timeout.connect(lambda: func(*args, **kwargs))
            self.timer.start(self.delay_ms)
        
        return wrapper


class RequestThrottle:
    """Throttle requests to prevent too many rapid calls."""
    def __init__(self, min_interval_ms=500):
        self.min_interval = min_interval_ms / 1000.0  # Convert to seconds
        self.last_call_time = 0
    
    def can_proceed(self):
        """Check if enough time has passed since last call."""
        current_time = time.time()
        if current_time - self.last_call_time >= self.min_interval:
            self.last_call_time = current_time
            return True
        return False
    
    def wait_time(self):
        """Get remaining wait time in milliseconds."""
        current_time = time.time()
        elapsed = current_time - self.last_call_time
        remaining = self.min_interval - elapsed
        return max(0, int(remaining * 1000))


class LoadingStateManager(QObject):
    """Manage loading states to prevent multiple simultaneous operations."""
    loading_started = pyqtSignal()
    loading_finished = pyqtSignal()
    
    def __init__(self):
        super().__init__()
        self._is_loading = False
        self._load_count = 0
    
    def start_loading(self):
        """Start a loading operation."""
        self._load_count += 1
        if not self._is_loading:
            self._is_loading = True
            self.loading_started.emit()
    
    def finish_loading(self):
        """Finish a loading operation."""
        self._load_count = max(0, self._load_count - 1)
        if self._load_count == 0 and self._is_loading:
            self._is_loading = False
            self.loading_finished.emit()
    
    def is_loading(self):
        """Check if currently loading."""
        return self._is_loading
    
    def reset(self):
        """Reset loading state."""
        self._load_count = 0
        self._is_loading = False
        self.loading_finished.emit()


# Decorator for debouncing
def debounce(delay_ms=300):
    """Decorator to debounce function calls."""
    return DebouncedFunction(delay_ms)


# Singleton loading manager
_global_loading_manager = LoadingStateManager()


def get_loading_manager():
    """Get the global loading state manager."""
    return _global_loading_manager
