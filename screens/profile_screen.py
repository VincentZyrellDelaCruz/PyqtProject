from PyQt6.QtWidgets import (
    QWidget, 
    QLabel, 
    QPushButton, 
    QHBoxLayout, 
    QVBoxLayout,
    QFrame, 
    QSizePolicy)
from PyQt6.QtCore import Qt, QSize
from PyQt6.QtGui import QPixmap, QPainter, QPainterPath, QFont, QIcon
import config
import os
class ProfileScreen(QWidget):
    def __init__(self, app_controller=None):
        super().__init__()
        self.app_controller = app_controller
        
        # Set size policy to expand and fill available space dynamically
        self.setSizePolicy(QSizePolicy.Policy.Expanding, QSizePolicy.Policy.Expanding)
        
        # Create UI manually (NO Qt Designer)
        self.create_profile_ui()
        self.load_profile_data()
    
    def create_profile_ui(self):
        """Create the entire profile UI manually"""
        # Set white background and ensure proper sizing
        self.setStyleSheet("ProfileScreen { background-color: #F5F5F5; }")
        
        # Main layout - no scroll area, parent handles scrolling
        main_layout = QVBoxLayout(self)
        main_layout.setContentsMargins(20, 20, 20, 20)
        main_layout.setSpacing(20)
        
        # 1. Profile Header Card
        profile_header = self.create_profile_header()
        main_layout.addWidget(profile_header)
        
        # 2. Recently Played Section
        self.recently_played_frame = self.create_section_card("🎧", "Recently Played")
        main_layout.addWidget(self.recently_played_frame)
        
        # 3. Favorite Songs Section
        self.favorites_frame = self.create_section_card("❤️", "Favorite Songs")
        main_layout.addWidget(self.favorites_frame)
        
        # 4. Developer Info Section
        developer_frame = self.create_developer_section()
        main_layout.addWidget(developer_frame)
        
        # Add stretch to push content to top
        main_layout.addStretch()
    
    def create_profile_header(self):
        """Create the green profile header card"""
        header_frame = QFrame()
        header_frame.setMinimumHeight(340)
        header_frame.setMaximumHeight(400)
        header_frame.setStyleSheet("""
            QFrame {
                background: qlineargradient(x1:0, y1:0, x2:0, y2:1,
                    stop:0 #71C562, stop:1 #5fb052);
                border-radius: 12px;
            }
        """)
        
        header_layout = QVBoxLayout(header_frame)
        header_layout.setSpacing(12)
        header_layout.setContentsMargins(30, 25, 30, 25)
        
        # Logout button in top-right corner
        logout_layout = QHBoxLayout()
        logout_layout.addStretch()
        
        self.logout_btn = QPushButton("Log Out")
        self.logout_btn.setFixedSize(100, 36)
        self.logout_btn.setCursor(Qt.CursorShape.PointingHandCursor)
        self.logout_btn.setFont(QFont("Segoe UI", 10, QFont.Weight.Bold))
        self.logout_btn.setStyleSheet("""
            QPushButton {
                background-color: rgba(255, 255, 255, 0.2);
                color: white;
                border: 2px solid rgba(255, 255, 255, 0.4);
                border-radius: 18px;
                padding: 0px;
            }
            QPushButton:hover {
                background-color: rgba(255, 255, 255, 0.3);
                border: 2px solid rgba(255, 255, 255, 0.6);
            }
            QPushButton:pressed {
                background-color: rgba(255, 255, 255, 0.15);
            }
        """)
        self.logout_btn.clicked.connect(self.logout)
        
        logout_layout.addWidget(self.logout_btn)
        header_layout.addLayout(logout_layout)
        
        # Profile picture
        self.profile_picture = QLabel()
        self.profile_picture.setFixedSize(100, 100)
        self.profile_picture.setAlignment(Qt.AlignmentFlag.AlignCenter)
        self.profile_picture.setStyleSheet("""
            QLabel {
                background-color: white;
                border-radius: 50px;
                border: 3px solid rgba(255, 255, 255, 0.3);
            }
        """)
        
        # Load profile picture
        self.load_profile_picture()
        
        header_layout.addWidget(self.profile_picture, 0, Qt.AlignmentFlag.AlignHCenter)
        
        header_layout.addSpacing(5)
        
        # Username
        self.username_label = QLabel("Music Lover")
        self.username_label.setAlignment(Qt.AlignmentFlag.AlignCenter)
        self.username_label.setFont(QFont("Segoe UI", 26, QFont.Weight.Bold))
        self.username_label.setStyleSheet("""
            QLabel {
                color: white;
                background-color: transparent;
                padding: 4px 0px;
                letter-spacing: -0.5px;
            }
        """)
        header_layout.addWidget(self.username_label)
        
        # Email
        self.email_label = QLabel("musiclover@musicsync.app")
        self.email_label.setAlignment(Qt.AlignmentFlag.AlignCenter)
        self.email_label.setFont(QFont("Segoe UI", 12))
        self.email_label.setStyleSheet("""
            QLabel {
                color: rgba(255, 255, 255, 0.9);
                background-color: transparent;
                padding: 0px 0px 8px 0px;
            }
        """)
        header_layout.addWidget(self.email_label)
        
        header_layout.addSpacing(8)
        
        # Stats section
        stats_layout = QHBoxLayout()
        stats_layout.setSpacing(20)
        stats_layout.setContentsMargins(0, 0, 0, 0)
        
        # Playlists stat
        playlists_widget = self.create_stat_widget("12", "Playlists")
        stats_layout.addWidget(playlists_widget)
        
        # Followers stat
        followers_widget = self.create_stat_widget("156", "Followers")
        stats_layout.addWidget(followers_widget)
        
        # Following stat
        following_widget = self.create_stat_widget("89", "Following")
        stats_layout.addWidget(following_widget)
        
        header_layout.addLayout(stats_layout)
        
        return header_frame
    
    def create_stat_widget(self, value, label):
        """Create a stat widget"""
        stat_widget = QWidget()
        stat_widget.setStyleSheet("""
            QWidget {
                background-color: rgba(255, 255, 255, 0.2);
                border-radius: 8px;
            }
        """)
        stat_layout = QVBoxLayout(stat_widget)
        stat_layout.setSpacing(6)
        stat_layout.setContentsMargins(16, 14, 16, 14)
        
        # Value
        value_label = QLabel(value)
        value_label.setAlignment(Qt.AlignmentFlag.AlignCenter)
        value_label.setFont(QFont("Segoe UI", 20, QFont.Weight.Bold))
        value_label.setStyleSheet("color: white; background-color: transparent;")
        stat_layout.addWidget(value_label)
        
        # Label
        label_widget = QLabel(label)
        label_widget.setAlignment(Qt.AlignmentFlag.AlignCenter)
        label_widget.setFont(QFont("Segoe UI", 11))
        label_widget.setStyleSheet("color: rgba(255, 255, 255, 0.95); background-color: transparent;")
        stat_layout.addWidget(label_widget)
        
        return stat_widget
    
    def load_profile_picture(self):
        """Load and set circular profile picture"""
        profile_pic_path = os.path.join(config.IMAGE_PATH, 'profile_default.png')
        
        # Try to load profile picture
        if os.path.exists(profile_pic_path):
            pixmap = QPixmap(profile_pic_path)
        else:
            # Fallback to Music Sync logo
            logo_path = os.path.join(config.IMAGE_PATH, 'μsic_sync-removebg.png')
            if os.path.exists(logo_path):
                pixmap = QPixmap(logo_path)
            else:
                # Create a white circle as fallback
                pixmap = QPixmap(100, 100)
                pixmap.fill(Qt.GlobalColor.white)
        
        # Make it circular
        circular_pixmap = self.create_circular_pixmap(pixmap, 100)
        self.profile_picture.setPixmap(circular_pixmap)
    
    def create_section_card(self, icon, title):
        """Create a generic section card with icon and title"""
        card_frame = QFrame()
        card_frame.setStyleSheet("""
            QFrame {
                background-color: white;
                border-radius: 12px;
                padding: 0px;
            }
        """)
        
        card_layout = QVBoxLayout(card_frame)
        card_layout.setSpacing(0)
        card_layout.setContentsMargins(0, 0, 0, 0)
        
        # Header section
        header_frame = QFrame()
        header_frame.setStyleSheet("background-color: transparent;")
        header_layout = QHBoxLayout(header_frame)
        header_layout.setSpacing(10)
        header_layout.setContentsMargins(20, 18, 20, 10)
        
        # Title (no icon, just bold text)
        title_label = QLabel(title)
        title_label.setFont(QFont("Segoe UI", 18, QFont.Weight.Bold))
        title_label.setStyleSheet("""
            QLabel {
                color: #1A1A1A;
                background-color: transparent;
                padding: 0px;
                letter-spacing: -0.3px;
            }
        """)
        header_layout.addWidget(title_label)
        header_layout.addStretch()
        
        card_layout.addWidget(header_frame)
        
        # Content frame (white background, no extra frame)
        content_frame = QFrame()
        content_frame.setStyleSheet("""
            QFrame {
                background-color: transparent;
                border-radius: 0px;
                padding: 0px;
            }
        """)
        
        # Content layout (will be populated later)
        content_layout = QVBoxLayout(content_frame)
        content_layout.setSpacing(4)
        content_layout.setContentsMargins(20, 0, 20, 20)
        
        # Store reference to content layout
        if "Recently" in title:
            self.recently_played_layout = content_layout
        elif "Favorite" in title:
            self.favorites_layout = content_layout
        
        card_layout.addWidget(content_frame)
        
        return card_frame
    
    def create_developer_section(self):
        """Create the developer info section"""
        card_frame = QFrame()
        card_frame.setStyleSheet("""
            QFrame {
                background-color: white;
                border-radius: 12px;
                padding: 0px;
            }
        """)
        
        card_layout = QVBoxLayout(card_frame)
        card_layout.setSpacing(0)
        card_layout.setContentsMargins(0, 0, 0, 0)
        
        # Header
        header_frame = QFrame()
        header_frame.setStyleSheet("background-color: transparent;")
        header_layout = QHBoxLayout(header_frame)
        header_layout.setContentsMargins(18, 14, 18, 8)
        
        title_label = QLabel("About Music Sync")
        title_label.setFont(QFont("Segoe UI", 16, QFont.Weight.Bold))
        title_label.setStyleSheet("""
            QLabel {
                color: #1A1A1A;
                background-color: transparent;
                letter-spacing: -0.3px;
            }
        """)
        header_layout.addWidget(title_label)
        header_layout.addStretch()
        
        card_layout.addWidget(header_frame)
        
        # Content
        content_frame = QFrame()
        content_frame.setStyleSheet("background-color: transparent;")
        
        content_layout = QVBoxLayout(content_frame)
        content_layout.setSpacing(10)
        content_layout.setContentsMargins(18, 0, 18, 18)
        
        # Description
        description = QLabel(
            "Music Sync is a modern music player application designed to provide "
            "seamless music playback with lyrics synchronization, local music library "
            "management, and an intuitive user interface."
        )
        description.setWordWrap(True)
        description.setFont(QFont("Segoe UI", 11))
        description.setStyleSheet("color: #5A5A5A; background-color: transparent; line-height: 1.4;")
        content_layout.addWidget(description)
        
        # Divider line
        line = QFrame()
        line.setFrameShape(QFrame.Shape.HLine)
        line.setStyleSheet("background-color: #EFEFEF; margin: 3px 0px;")
        line.setFixedHeight(1)
        content_layout.addWidget(line)
        
        # Developers label
        dev_label = QLabel("Development Team")
        dev_label.setFont(QFont("Segoe UI", 13, QFont.Weight.Bold))
        dev_label.setStyleSheet("color: #1A1A1A; background-color: transparent; padding: 3px 0px 2px 0px;")
        content_layout.addWidget(dev_label)
        
        # Student names
        names = QLabel(
            "• Student Name 1\n"
            "• Student Name 2\n"
            "• Student Name 3\n"
            "• Student Name 4"
        )
        names.setFont(QFont("Segoe UI", 11))
        names.setStyleSheet("color: #5A5A5A; background-color: transparent; line-height: 1.6;")
        content_layout.addWidget(names)
        
        content_layout.addSpacing(3)
        
        # Version
        version = QLabel("Version 1.0.0 | © 2025 Music Sync Team")
        version.setFont(QFont("Segoe UI", 9))
        version.setStyleSheet("color: #999999; background-color: transparent;")
        content_layout.addWidget(version)
        
        card_layout.addWidget(content_frame)
        
        return card_frame
    
    def create_circular_pixmap(self, pixmap, size):
        """Create a circular pixmap from a square one"""
        # Scale the pixmap to the desired size
        scaled_pixmap = pixmap.scaled(size, size, Qt.AspectRatioMode.KeepAspectRatioByExpanding, 
                                       Qt.TransformationMode.SmoothTransformation)
        
        # Create a new pixmap with transparency
        circular = QPixmap(size, size)
        circular.fill(Qt.GlobalColor.transparent)
        
        # Create a circular path
        painter = QPainter(circular)
        painter.setRenderHint(QPainter.RenderHint.Antialiasing)
        
        path = QPainterPath()
        path.addEllipse(0, 0, size, size)
        painter.setClipPath(path)
        
        # Draw the pixmap centered
        x = (size - scaled_pixmap.width()) // 2
        y = (size - scaled_pixmap.height()) // 2
        painter.drawPixmap(x, y, scaled_pixmap)
        painter.end()
        
        return circular
    
    def load_profile_data(self):
        """Load and display profile data"""
        # Load recently played songs
        self.load_recently_played()
        
        # Load favorite songs
        self.load_favorites()
    
    def load_recently_played(self):
        """Load and display recently played songs"""
        # Get local music files (we'll show the first 5 as recently played)
        try:
            local_playlist = sorted(os.listdir(config.LOCAL_MUSIC_PATH))[:5]
            
            if not local_playlist:
                no_songs_label = QLabel("No songs found in your library.\nAdd some music to get started!")
                no_songs_label.setAlignment(Qt.AlignmentFlag.AlignCenter)
                no_songs_label.setFont(QFont("Segoe UI", 13))
                no_songs_label.setStyleSheet("""
                    QLabel {
                        color: #999999;
                        padding: 30px 20px;
                        background-color: transparent;
                    }
                """)
                self.recently_played_layout.addWidget(no_songs_label)
                return
            
            for song in local_playlist:
                song_widget = self.create_song_item(song)
                self.recently_played_layout.addWidget(song_widget)
        except Exception as e:
            print(f"Error loading recently played: {e}")
            error_label = QLabel("Could not load recently played songs.")
            error_label.setAlignment(Qt.AlignmentFlag.AlignCenter)
            error_label.setFont(QFont("Segoe UI", 13))
            error_label.setStyleSheet("color: #999999; padding: 30px 20px; background-color: transparent;")
            self.recently_played_layout.addWidget(error_label)
    
    def load_favorites(self):
        """Load and display favorite songs"""
        # Get local music files (we'll show a different set as favorites)
        try:
            local_playlist = sorted(os.listdir(config.LOCAL_MUSIC_PATH))
            # Show last 5 songs as favorites (or fewer if less songs available)
            favorites = local_playlist[-5:] if len(local_playlist) > 5 else local_playlist
            
            if not favorites:
                no_favorites_label = QLabel("No favorite songs yet.\nStart adding some to your collection!")
                no_favorites_label.setAlignment(Qt.AlignmentFlag.AlignCenter)
                no_favorites_label.setFont(QFont("Segoe UI", 13))
                no_favorites_label.setStyleSheet("""
                    QLabel {
                        color: #999999;
                        padding: 30px 20px;
                        background-color: transparent;
                    }
                """)
                self.favorites_layout.addWidget(no_favorites_label)
                return
            
            for song in favorites:
                song_widget = self.create_song_item(song, is_favorite=True)
                self.favorites_layout.addWidget(song_widget)
        except Exception as e:
            print(f"Error loading favorites: {e}")
            error_label = QLabel("Could not load favorite songs.")
            error_label.setAlignment(Qt.AlignmentFlag.AlignCenter)
            error_label.setFont(QFont("Segoe UI", 13))
            error_label.setStyleSheet("color: #999999; padding: 30px 20px; background-color: transparent;")
            self.favorites_layout.addWidget(error_label)
    
    def create_song_item(self, song_title, is_favorite=False):
        """Create a song item widget"""
        song_widget = QWidget()
        song_layout = QHBoxLayout(song_widget)
        song_layout.setContentsMargins(12, 8, 12, 8)
        song_layout.setSpacing(14)
        
        # Add hover effect
        song_widget.setStyleSheet("""
            QWidget {
                background-color: transparent;
                border-radius: 6px;
            }
            QWidget:hover {
                background-color: #F8F8F8;
            }
        """)
        
        # Song icon/thumbnail
        icon_label = QLabel()
        icon_label.setFixedSize(48, 48)
        icon_label.setStyleSheet("""
            QLabel {
                background: qlineargradient(x1:0, y1:0, x2:1, y2:1,
                    stop:0 #71C562, stop:1 #5fb052);
                border-radius: 6px;
                padding: 0px;
                color: white;
                font-size: 22px;
                font-weight: bold;
            }
        """)
        icon_label.setAlignment(Qt.AlignmentFlag.AlignCenter)
        icon_label.setText("♪")
        
        # Song name
        name_label = QLabel(song_title.replace('.mp3', ''))
        name_label.setFont(QFont("Segoe UI", 14))
        name_label.setStyleSheet("""
            QLabel {
                color: #1A1A1A;
                background-color: transparent;
                font-weight: 500;
            }
        """)
        name_label.setWordWrap(False)
        
        # Play button
        play_btn = QPushButton()
        play_btn.setFixedSize(40, 40)
        play_btn.setCursor(Qt.CursorShape.PointingHandCursor)
        
        # Try to load play icon, fallback to text
        play_icon_path = os.path.join(config.ICON_PATH, 'play.svg')
        if os.path.exists(play_icon_path):
            play_btn.setIcon(QIcon(play_icon_path))
            play_btn.setIconSize(QSize(16, 16))
        else:
            play_btn.setText("▶")
        
        play_btn.setStyleSheet("""
            QPushButton {
                background-color: #71C562;
                border: none;
                border-radius: 20px;
                color: white;
                font-size: 14px;
                font-weight: bold;
            }
            QPushButton:hover {
                background-color: #5fb052;
            }
            QPushButton:pressed {
                background-color: #4a9642;
            }
        """)
        
        # Connect play button to open music player
        play_btn.clicked.connect(lambda: self.play_song(song_title))
        
        song_layout.addWidget(icon_label)
        song_layout.addWidget(name_label, 1)
        song_layout.addWidget(play_btn)
        
        # Style the song widget
        song_widget.setStyleSheet("""
            QWidget {
                background-color: transparent;
                border-radius: 6px;
                padding: 4px;
            }
            QWidget:hover {
                background-color: #F0F0F0;
            }
        """)
        
        return song_widget
    
    def play_song(self, song_title):
        """Play the selected song"""
        if self.app_controller:
            self.app_controller.open_music_player(song_title)
        else:
            print(f"Would play: {song_title}")
    
    def logout(self):
        """Handle logout action - cleanup all resources and reset state"""
        if self.app_controller:
            # Clean up main screen resources (stop music, reset state)
            if hasattr(self.app_controller, 'main'):
                self.app_controller.main.cleanup_on_logout()
            
            # Clear login form fields for security
            if hasattr(self.app_controller, 'login'):
                self.app_controller.login.clear_fields()
            
            # Navigate back to login screen
            self.app_controller.goto_login()
        else:
            print("Logout clicked")
    

