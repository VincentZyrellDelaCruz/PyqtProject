from functools import partial
from PyQt6.QtCore import Qt, QSize
from PyQt6.QtWidgets import QMainWindow, QVBoxLayout, QPushButton, QButtonGroup, QScrollArea, QWidget, QSizePolicy
from PyQt6.QtGui import QIcon, QFont, QPixmap
from UI.main_screen_ui import Ui_MainWindow
from screens.profile_screen import ProfileScreen
from screens.music_player import MusicPlayer
from screens.mini_player_bar import MiniPlayerBar
import config, os
import controllers.music_metadata as metadata

class MainScreen(QMainWindow):
    def __init__(self, app_controller):
        super().__init__()
        self.ui = Ui_MainWindow()
        self.ui.setupUi(self)
        
        # Hide menubar and statusbar to eliminate bottom gap
        self.menuBar().hide()
        self.statusBar().hide()

        self.button_group = QButtonGroup(self)

        self.local_playlist = sorted(os.listdir(config.LOCAL_MUSIC_PATH))

        self.app_controller = app_controller
        self.init_ui()
        self.connect_signals()
        self.display_local_playlist()
        self.add_profile_page()
        self.add_mini_player_bar()
        
        # Initialize music player variable (will be created when needed)
        self.current_music_player = None
        self.currently_playing_song = None  # Track which song is playing

    def init_ui(self):
        pixmap1 = QPixmap(config.IMAGE_PATH + 'μsic_sync-removebg.png').scaled(
            150, 150)
        self.ui.logo_1.setPixmap(pixmap1)

        pixmap2 = QPixmap(config.IMAGE_PATH + 'μsic_sync_with_name-removebg.png').scaled(
            200, 100)
        self.ui.logo_2.setPixmap(pixmap2)

        self.ui.home1.setIcon(QIcon(config.ICON_PATH + 'music.png'))
        self.ui.home2.setIcon(QIcon(config.ICON_PATH + 'music.png'))

        self.ui.local1.setIcon(QIcon(config.ICON_PATH + 'local-play-button.png'))
        self.ui.local2.setIcon(QIcon(config.ICON_PATH + 'local-play-button.png'))

        self.ui.about1.setIcon(QIcon(config.ICON_PATH + 'info.png'))
        self.ui.about2.setIcon(QIcon(config.ICON_PATH + 'info.png'))

        self.ui.user1.setIcon(QIcon(config.ICON_PATH + 'user.png'))
        self.ui.user2.setIcon(QIcon(config.ICON_PATH + 'user.png'))

        self.ui.burger_icon.setIcon(QIcon(config.ICON_PATH + 'burger-bar.png'))

        self.ui.widget_icontexts.setHidden(True)

        self.button_group.setExclusive(True)

    def connect_signals(self):
        self.ui.local1.clicked.connect(self.app_controller.goto_local)
        self.ui.local2.clicked.connect(self.app_controller.goto_local)

        self.ui.home1.clicked.connect(self.app_controller.goto_home)
        self.ui.home2.clicked.connect(self.app_controller.goto_home)

        self.ui.user1.clicked.connect(self.app_controller.goto_profile)
        self.ui.user2.clicked.connect(self.app_controller.goto_profile)
    
    def add_profile_page(self):
        """Add profile screen to the home stack"""
        # Create profile screen widget
        profile_widget = ProfileScreen(self.app_controller)
        
        # Make it expand properly to fill available space
        profile_widget.setSizePolicy(QSizePolicy.Policy.Expanding, QSizePolicy.Policy.Expanding)
        profile_widget.setMinimumSize(0, 0)
        profile_widget.setMaximumSize(16777215, 16777215)  # Remove fixed size constraints
        
        # Make it scrollable if it's taller than the screen
        scroll_area = QScrollArea()
        scroll_area.setWidgetResizable(True)
        scroll_area.setFrameShape(QScrollArea.Shape.NoFrame)
        scroll_area.setWidget(profile_widget)
        scroll_area.setHorizontalScrollBarPolicy(Qt.ScrollBarPolicy.ScrollBarAlwaysOff)
        
        # Style the scrollbar
        scroll_area.setStyleSheet("""
            QScrollArea {
                border: none;
                background-color: #F5F5F5;
            }
            QScrollBar:vertical {
                border: none;
                background: #E0E0E0;
                width: 10px;
                border-radius: 5px;
                margin: 2px;
            }
            QScrollBar::handle:vertical {
                background: #71C562;
                border-radius: 5px;
                min-height: 40px;
            }
            QScrollBar::handle:vertical:hover {
                background: #5fb052;
            }
            QScrollBar::add-line:vertical, QScrollBar::sub-line:vertical {
                height: 0px;
            }
        """)
        
        # Add to stacked widget (this is the content area beside the sidebar)
        self.ui.home_stack.addWidget(scroll_area)
    
    def add_mini_player_bar(self):
        """Add persistent mini-player bar integrated into the main layout"""
        # Find the main vertical layout that contains header and main_screen
        # We'll add the mini player at the bottom
        
        # The verticalLayout_7 contains [header, main_screen]
        # We need to add mini_player after main_screen
        
        self.mini_player = MiniPlayerBar(self)
        
        # Connect signals
        self.mini_player.expand_clicked.connect(self.show_now_playing)
        self.mini_player.play_pause_clicked.connect(self.toggle_playback)
        self.mini_player.next_clicked.connect(self.play_next_song)
        self.mini_player.prev_clicked.connect(self.play_prev_song)
        self.mini_player.seek_position.connect(self.seek_to_position)
        
        # Access the vertical layout from UI (contains header + main_screen)
        # We'll add it directly after finding the layout
        # The main_layout contains the horizontal layout with sidebar + content
        # We need to add mini_player to the vertical layout
        
        # Get the parent layout of main_screen
        try:
            # Find verticalLayout_7 which is part of main_layout
            for i in range(self.ui.main_layout.count()):
                item = self.ui.main_layout.itemAt(i)
                if item and item.layout():
                    layout = item.layout()
                    # This should be verticalLayout_7
                    if layout.objectName() == 'verticalLayout_7':
                        # Add mini player at the bottom
                        layout.addWidget(self.mini_player)
                        break
        except:
            # Fallback: add to status bar area
            pass

    def display_local_playlist(self):
        if self.local_playlist is None:
            return

        scroll_area = QScrollArea()
        scroll_area.setWidgetResizable(True)
        scroll_area.setHorizontalScrollBarPolicy(Qt.ScrollBarPolicy.ScrollBarAlwaysOff)
        scroll_area.setStyleSheet("""
            QScrollArea {
                border: none;
            }
            QScrollArea QWidget {
                background-color: #555;
            }
        """)

        content_widget = QWidget()
        content_layout = QVBoxLayout(content_widget)
        content_layout.setContentsMargins(0, 0, 0, 0)
        content_layout.setSpacing(6)

        for i, song_title in enumerate(self.local_playlist):
            song_btn = QPushButton(f"{' '*3}{song_title.replace('.mp3', '')}")
            song_btn.setFont(QFont('Arial', 15))
            song_btn.setCheckable(True)
            song_btn.setIcon(QIcon(metadata.get_embedded_image(config.LOCAL_MUSIC_PATH + song_title, square=True)))
            song_btn.setIconSize(QSize(64, 64))
            song_btn.setStyleSheet('''
                QPushButton { 
                    color: #fff; 
                    text-align: left; 
                    background-color: transparent; 
                    padding: 8px 10px;
                    border: none;
                    border-radius: 5px; 
                }
                QPushButton:hover {
                    background-color: #3a3a3a;
                }
                QPushButton:checked {
                    background-color: #1DB954;
                }
                QIcon {
                    border-radius: 5px;
                }
            ''')
            song_btn.clicked.connect(partial(self.app_controller.open_music_player, song_title))

            self.button_group.addButton(song_btn, id=i)
            content_layout.addWidget(song_btn)

        scroll_area.setWidget(content_widget)
        self.ui.list_layout.addWidget(scroll_area)

    def show_music_player(self, song_title):
        """Show music player embedded in the main screen"""
        # Update currently playing song
        self.currently_playing_song = song_title
        
        # Update highlighted song in playlist
        self.highlight_playing_song(song_title)
        
        # Clean up previous music player if it exists and it's a different song
        if self.current_music_player is not None:
            # If same song, just switch to player view
            if hasattr(self.current_music_player, 'song_title') and self.current_music_player.song_title == song_title:
                # Just show the existing player
                return
            
            self.current_music_player.cleanup()
            # Remove from stacked widget
            widget_index = self.ui.home_stack.indexOf(self.current_music_player)
            if widget_index >= 0:
                self.ui.home_stack.removeWidget(self.current_music_player)
            self.current_music_player.deleteLater()
        
        # Create new music player widget
        self.current_music_player = MusicPlayer(song_title, parent=self)
        
        # Connect music player signals to mini-player updates
        self.current_music_player.player.positionChanged.connect(self.mini_player.update_position)
        self.current_music_player.player.durationChanged.connect(self.mini_player.update_duration)
        
        # Make it expand to fill the space
        self.current_music_player.setSizePolicy(QSizePolicy.Policy.Expanding, QSizePolicy.Policy.Expanding)
        
        # Add to stacked widget (index 3 - after homepage, local_page, profile)
        if self.ui.home_stack.count() <= 3:
            self.ui.home_stack.addWidget(self.current_music_player)
        else:
            # Replace existing music player at index 3
            self.ui.home_stack.removeWidget(self.ui.home_stack.widget(3))
            self.ui.home_stack.insertWidget(3, self.current_music_player)
        
        # Update mini player bar
        artist, album_art = metadata.get_music_metadata(config.LOCAL_MUSIC_PATH + song_title)
        self.mini_player.update_song_info(song_title, artist or "Unknown Artist", album_art)
        self.mini_player.update_play_state(True)
    
    def show_now_playing(self):
        """Navigate to Now Playing view"""
        if self.current_music_player:
            self.app_controller.main.ui.page_label.setText('NOW PLAYING')
            self.ui.home_stack.setCurrentIndex(3)
    
    def toggle_playback(self):
        """Toggle play/pause from mini player"""
        if self.current_music_player:
            self.current_music_player.toggle_play_pause()
            self.mini_player.update_play_state(self.current_music_player.isPlaying)
    
    def play_next_song(self):
        """Play next song from mini player"""
        if self.currently_playing_song:
            current_index = self.local_playlist.index(self.currently_playing_song)
            next_index = (current_index + 1) % len(self.local_playlist)
            next_song = self.local_playlist[next_index]
            self.show_music_player(next_song)
            # Update view to show player
            self.app_controller.main.ui.page_label.setText('NOW PLAYING')
            self.ui.home_stack.setCurrentIndex(3)
    
    def play_prev_song(self):
        """Play previous song from mini player"""
        if self.currently_playing_song:
            current_index = self.local_playlist.index(self.currently_playing_song)
            prev_index = (current_index - 1) % len(self.local_playlist)
            prev_song = self.local_playlist[prev_index]
            self.show_music_player(prev_song)
            # Update view to show player
            self.app_controller.main.ui.page_label.setText('NOW PLAYING')
            self.ui.home_stack.setCurrentIndex(3)
    
    def highlight_playing_song(self, song_title):
        """Highlight the currently playing song in the playlist"""
        # Find and check the button for the playing song
        for i in range(len(self.local_playlist)):
            button = self.button_group.button(i)
            if button:
                if self.local_playlist[i] == song_title:
                    button.setChecked(True)
                # Don't uncheck others - button group handles that
    
    def seek_to_position(self, position):
        """Seek to a specific position in the song"""
        if self.current_music_player:
            self.current_music_player.player.setPosition(position)
    
    def cleanup_on_logout(self):
        """Clean up all resources and reset state when logging out"""
        # Stop and cleanup music player
        if self.current_music_player:
            self.current_music_player.cleanup()
            widget_index = self.ui.home_stack.indexOf(self.current_music_player)
            if widget_index >= 0:
                self.ui.home_stack.removeWidget(self.current_music_player)
            self.current_music_player.deleteLater()
            self.current_music_player = None
        
        # Reset playing state
        self.currently_playing_song = None
        
        # Reset mini player display
        if hasattr(self, 'mini_player'):
            self.mini_player.song_title_label.setText("No song playing")
            self.mini_player.artist_label.setText("")
            self.mini_player.current_time_label.setText("0:00")
            self.mini_player.total_time_label.setText("0:00")
            self.mini_player.progress_bar.setValue(0)
            self.mini_player.play_pause_btn.setIcon(QIcon(config.ICON_PATH + "play.svg"))
        
        # Uncheck all playlist buttons
        if self.button_group:
            checked_button = self.button_group.checkedButton()
            if checked_button:
                self.button_group.setExclusive(False)
                checked_button.setChecked(False)
                self.button_group.setExclusive(True)
        
        # Reset to home view
        self.ui.page_label.setText('HOME')
        self.ui.home_stack.setCurrentIndex(0)


