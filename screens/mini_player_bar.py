from PyQt6.QtWidgets import QWidget, QHBoxLayout, QVBoxLayout, QLabel, QPushButton, QSlider
from PyQt6.QtCore import Qt, pyqtSignal, QSize, QTimer
from PyQt6.QtGui import QIcon, QPixmap, QFont
import config

class MiniPlayerBar(QWidget):
    """Persistent mini-player bar at the bottom showing currently playing song"""
    
    # Signal to notify when user wants to expand to full player
    expand_clicked = pyqtSignal()
    play_pause_clicked = pyqtSignal()
    next_clicked = pyqtSignal()
    prev_clicked = pyqtSignal()
    seek_position = pyqtSignal(int)  # New signal for seeking
    
    def __init__(self, parent=None):
        super().__init__(parent)
        self.current_song = None
        self.is_playing = False
        self.is_seeking = False
        self.setup_ui()
        self.hide()  # Hidden by default until a song is played
        
    def setup_ui(self):
        """Create the mini player bar UI"""
        self.setFixedHeight(80)
        self.setStyleSheet("""
            QWidget {
                background-color: #181818;
                border-top: 1px solid #282828;
            }
        """)
        
        # Main vertical layout for progress bar + controls
        main_layout = QVBoxLayout(self)
        main_layout.setContentsMargins(0, 0, 0, 0)
        main_layout.setSpacing(0)
        
        # Progress bar at the very top
        self.progress_bar = QSlider(Qt.Orientation.Horizontal)
        self.progress_bar.setFixedHeight(6)
        self.progress_bar.setStyleSheet("""
            QSlider::groove:horizontal {
                background: #404040;
                height: 6px;
                border: none;
                border-radius: 3px;
            }
            QSlider::handle:horizontal {
                background: white;
                width: 14px;
                height: 14px;
                margin: -4px 0;
                border-radius: 7px;
            }
            QSlider::sub-page:horizontal {
                background: #1DB954;
                border: none;
                border-radius: 3px;
            }
        """)
        self.progress_bar.sliderPressed.connect(self.on_slider_pressed)
        self.progress_bar.sliderReleased.connect(self.on_slider_released)
        self.progress_bar.sliderMoved.connect(self.on_slider_moved)
        main_layout.addWidget(self.progress_bar)
        
        # Controls layout
        controls_container = QWidget()
        controls_layout = QHBoxLayout(controls_container)
        controls_layout.setContentsMargins(16, 0, 16, 0)
        controls_layout.setSpacing(0)
        
        # Left section: Album art + Song info (30% width)
        left_widget = QWidget()
        left_widget.setFixedWidth(300)
        left_layout = QHBoxLayout(left_widget)
        left_layout.setContentsMargins(0, 0, 0, 0)
        left_layout.setSpacing(12)
        
        # Album art thumbnail
        self.album_art = QLabel()
        self.album_art.setFixedSize(48, 48)
        self.album_art.setStyleSheet("""
            QLabel {
                border-radius: 4px;
                background-color: #282828;
            }
        """)
        self.album_art.setScaledContents(True)
        left_layout.addWidget(self.album_art)
        
        # Song info (title + artist)
        info_layout = QVBoxLayout()
        info_layout.setSpacing(2)
        info_layout.setContentsMargins(0, 12, 0, 12)
        
        self.song_title_label = QLabel("No song playing")
        self.song_title_label.setStyleSheet("""
            color: white; 
            font-size: 13px; 
            font-weight: 600;
        """)
        self.song_title_label.setCursor(Qt.CursorShape.PointingHandCursor)
        self.song_title_label.mousePressEvent = lambda e: self.expand_clicked.emit()
        info_layout.addWidget(self.song_title_label)
        
        self.artist_label = QLabel("")
        self.artist_label.setStyleSheet("""
            color: #b3b3b3; 
            font-size: 11px;
        """)
        info_layout.addWidget(self.artist_label)
        
        left_layout.addLayout(info_layout)
        left_layout.addStretch()
        
        controls_layout.addWidget(left_widget)
        
        # Center section: Playback controls (40% width, centered)
        center_widget = QWidget()
        center_layout = QVBoxLayout(center_widget)
        center_layout.setContentsMargins(0, 0, 0, 0)
        center_layout.setSpacing(4)
        center_layout.setAlignment(Qt.AlignmentFlag.AlignCenter)
        
        # Playback control buttons
        playback_controls = QHBoxLayout()
        playback_controls.setSpacing(8)
        playback_controls.setAlignment(Qt.AlignmentFlag.AlignCenter)
        
        # Previous button
        self.prev_btn = QPushButton()
        self.prev_btn.setIcon(QIcon(config.ICON_PATH + "prev.svg"))
        self.prev_btn.setIconSize(QSize(24, 24))
        self.prev_btn.setFixedSize(40, 40)
        self.prev_btn.setCursor(Qt.CursorShape.PointingHandCursor)
        self.prev_btn.setStyleSheet("""
            QPushButton {
                background-color: transparent;
                border: none;
                border-radius: 20px;
            }
            QPushButton:hover {
                background-color: #282828;
            }
        """)
        self.prev_btn.clicked.connect(self.prev_clicked.emit)
        playback_controls.addWidget(self.prev_btn)
        
        # Play/Pause button (same size as others for consistency)
        self.play_pause_btn = QPushButton()
        self.play_pause_btn.setIcon(QIcon(config.ICON_PATH + "play.svg"))
        self.play_pause_btn.setIconSize(QSize(24, 24))
        self.play_pause_btn.setFixedSize(40, 40)
        self.play_pause_btn.setCursor(Qt.CursorShape.PointingHandCursor)
        self.play_pause_btn.setStyleSheet("""
            QPushButton {
                background-color: #1DB954;
                border: none;
                border-radius: 20px;
            }
            QPushButton:hover {
                background-color: #1ed760;
            }
            QPushButton:pressed {
                background-color: #169c46;
            }
        """)
        self.play_pause_btn.clicked.connect(self.play_pause_clicked.emit)
        playback_controls.addWidget(self.play_pause_btn)
        
        # Next button
        self.next_btn = QPushButton()
        self.next_btn.setIcon(QIcon(config.ICON_PATH + "next.svg"))
        self.next_btn.setIconSize(QSize(24, 24))
        self.next_btn.setFixedSize(40, 40)
        self.next_btn.setCursor(Qt.CursorShape.PointingHandCursor)
        self.next_btn.setStyleSheet("""
            QPushButton {
                background-color: transparent;
                border: none;
                border-radius: 20px;
            }
            QPushButton:hover {
                background-color: #282828;
            }
        """)
        self.next_btn.clicked.connect(self.next_clicked.emit)
        playback_controls.addWidget(self.next_btn)
        
        center_layout.addLayout(playback_controls)
        
        # Time labels (current / total) - aligned horizontally
        time_layout = QHBoxLayout()
        time_layout.setSpacing(6)
        time_layout.setAlignment(Qt.AlignmentFlag.AlignCenter)
        
        self.current_time_label = QLabel("0:00")
        self.current_time_label.setStyleSheet("""
            color: #b3b3b3; 
            font-size: 11px; 
            font-weight: 400;
        """)
        self.current_time_label.setAlignment(Qt.AlignmentFlag.AlignRight)
        self.current_time_label.setFixedWidth(35)
        time_layout.addWidget(self.current_time_label)
        
        time_separator = QLabel("•")
        time_separator.setStyleSheet("color: #535353; font-size: 10px;")
        time_layout.addWidget(time_separator)
        
        self.total_time_label = QLabel("0:00")
        self.total_time_label.setStyleSheet("""
            color: #b3b3b3; 
            font-size: 11px; 
            font-weight: 400;
        """)
        self.total_time_label.setAlignment(Qt.AlignmentFlag.AlignLeft)
        self.total_time_label.setFixedWidth(35)
        time_layout.addWidget(self.total_time_label)
        
        center_layout.addLayout(time_layout)
        
        controls_layout.addStretch()
        controls_layout.addWidget(center_widget)
        controls_layout.addStretch()
        
        # Right section: Volume + Expand button (30% width, right-aligned)
        right_widget = QWidget()
        right_widget.setFixedWidth(300)
        right_layout = QHBoxLayout(right_widget)
        right_layout.setContentsMargins(0, 0, 0, 0)
        right_layout.setSpacing(8)
        right_layout.addStretch()
        
        # Volume button
        self.volume_btn = QPushButton()
        self.volume_btn.setIcon(QIcon(config.ICON_PATH + "volume-up.svg"))
        self.volume_btn.setIconSize(QSize(24, 24))
        self.volume_btn.setFixedSize(40, 40)
        self.volume_btn.setCursor(Qt.CursorShape.PointingHandCursor)
        self.volume_btn.setStyleSheet("""
            QPushButton {
                background-color: transparent;
                border: none;
                border-radius: 20px;
            }
            QPushButton:hover {
                background-color: #282828;
            }
        """)
        right_layout.addWidget(self.volume_btn)
        
        # Expand to full player button
        self.expand_btn = QPushButton()
        self.expand_btn.setIcon(QIcon(config.ICON_PATH + "music.png"))
        self.expand_btn.setIconSize(QSize(24, 24))
        self.expand_btn.setFixedSize(40, 40)
        self.expand_btn.setCursor(Qt.CursorShape.PointingHandCursor)
        self.expand_btn.setToolTip("Open Now Playing")
        self.expand_btn.setStyleSheet("""
            QPushButton {
                background-color: transparent;
                border: none;
                border-radius: 16px;
            }
            QPushButton:hover {
                background-color: #282828;
            }
        """)
        self.expand_btn.clicked.connect(self.expand_clicked.emit)
        right_layout.addWidget(self.expand_btn)
        
        controls_layout.addWidget(right_widget)
        
        main_layout.addWidget(controls_container)
    
    def on_slider_pressed(self):
        """Handle slider press - stop auto-update"""
        self.is_seeking = True
    
    def on_slider_released(self):
        """Handle slider release - seek to position"""
        self.is_seeking = False
        self.seek_position.emit(self.progress_bar.value())
    
    def on_slider_moved(self, position):
        """Update time label while dragging"""
        self.current_time_label.setText(self.format_time(position))
    
    def update_position(self, position):
        """Update progress bar and time (called from music player)"""
        if not self.is_seeking:
            self.progress_bar.setValue(position)
            self.current_time_label.setText(self.format_time(position))
    
    def update_duration(self, duration):
        """Update total duration"""
        self.progress_bar.setMaximum(duration)
        self.total_time_label.setText(self.format_time(duration))
    
    def format_time(self, ms):
        """Format milliseconds to MM:SS"""
        seconds = ms // 1000
        minutes = seconds // 60
        seconds = seconds % 60
        return f"{minutes}:{seconds:02d}"
        
    def update_song_info(self, song_title, artist="Unknown Artist", album_art=None):
        """Update the mini player with current song information"""
        self.current_song = song_title
        self.song_title_label.setText(song_title.replace('.mp3', ''))
        self.artist_label.setText(artist)
        
        if album_art and not album_art.isNull():
            scaled_art = album_art.scaled(60, 60, Qt.AspectRatioMode.KeepAspectRatioByExpanding, 
                                         Qt.TransformationMode.SmoothTransformation)
            self.album_art.setPixmap(scaled_art)
        else:
            # Default album art
            self.album_art.setText("🎵")
            self.album_art.setAlignment(Qt.AlignmentFlag.AlignCenter)
            
        self.show()
        
    def update_play_state(self, is_playing):
        """Update play/pause button state"""
        self.is_playing = is_playing
        if is_playing:
            self.play_pause_btn.setIcon(QIcon(config.ICON_PATH + "pause.svg"))
        else:
            self.play_pause_btn.setIcon(QIcon(config.ICON_PATH + "play.svg"))
