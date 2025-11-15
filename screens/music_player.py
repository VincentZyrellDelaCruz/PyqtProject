from PyQt6.QtWidgets import QApplication, QDialog, QWidget, QScrollArea, QPushButton, QButtonGroup, QVBoxLayout, QLabel
from PyQt6.QtCore import Qt, QUrl, QTimer
from PyQt6.QtGui import QIcon, QPixmap, QPainter, QPainterPath
from functools import partial
from UI.music_player_ui import Ui_Dialog
import sys, os, random, config
from controllers.music_metadata import get_music_metadata, get_lyrics
import vlc

class MusicPlayer(QDialog):
    def __init__(self, song_title, parent=None):
        super().__init__(parent)

        # Loads the UI
        self.ui = Ui_Dialog()
        self.ui.setupUi(self)

        # Gets all existing music file inside local_music folder
        local_playlist = sorted(os.listdir(config.LOCAL_MUSIC_PATH))
        self.song_title = song_title

        # Sets to continue/non-loop by default
        self.repeat = 0

        # Sets rotation for pixmap
        self.rotation_angle = 0
        self.rotation_timer = QTimer(self)

        self.button_group = QButtonGroup(self)

        self.display_local_playlist(local_playlist)

        # === VLC Instance & Player ===
        self.instance = vlc.Instance('--quiet', '--no-video')  # No video, quiet mode
        self.player = self.instance.media_player_new()

        # Polling timer for position/duration (VLC has no signals)
        self.position_timer = QTimer(self)
        self.position_timer.timeout.connect(self.update_position_and_duration)
        self.position_timer.start(100)  # Update every 100ms

        self.load_music()

        # Marquee-like effect
        self.scroll_timer = QTimer(self)
        self.scroll_timer.timeout.connect(self.scroll_artist_name)
        self.scroll_offset = 0
        self.artist_full_text = ""
        self.scroll_timer.start(150)  # speed (ms)

        self.setup_lyrics_display()

        self.isPlaying = True

        self.init_ui()

        self.play()

    def cleanup(self):
        """Cleanup method to stop playback and timers"""
        if hasattr(self, 'player') and self.player:
            self.player.stop()
        if hasattr(self, 'rotation_timer'):
            self.rotation_timer.stop()
        if hasattr(self, 'scroll_timer'):
            self.scroll_timer.stop()
        if hasattr(self, 'position_timer'):
            self.position_timer.stop()

    def closeEvent(self, event):
        """Override close event to stop playback when widget is closed"""
        self.cleanup()
        event.accept()

    def init_ui(self):
        # Sets icon for each push buttons
        self.ui.playButton.setIcon(QIcon(config.ICON_PATH + "play.svg"))
        self.ui.nextButton.setIcon(QIcon(config.ICON_PATH + "next.svg"))
        self.ui.prevButton.setIcon(QIcon(config.ICON_PATH + "prev.svg"))
        self.ui.loop_shuffle.setIcon(QIcon(config.ICON_PATH + "continue.svg"))
        self.ui.volume.setIcon(QIcon(config.ICON_PATH + "volume-up.svg"))

        self.ui.loop_shuffle.clicked.connect(self.loop_shuffle)

        self.ui.volume_frame.setVisible(False)
        self.button_group.setExclusive(True)

        self.ui.playback_tab.clicked.connect(lambda: self.ui.stackedWidget.setCurrentIndex(0))
        self.ui.list_tab.clicked.connect(lambda: self.ui.stackedWidget.setCurrentIndex(1))
        self.ui.lyrics_tab.clicked.connect(lambda: self.ui.stackedWidget.setCurrentIndex(2))

        self.rotation_timer.timeout.connect(self.spin_pixmap)
        self.rotation_timer.start(30)  # ~33 FPS

        self.ui.playButton.clicked.connect(self.toggle_play_pause)

        # Simulate signals via polling
        # (handled in update_position_and_duration)

        self.ui.progressTime.sliderPressed.connect(self.slider_pressed)
        self.ui.progressTime.sliderReleased.connect(self.slider_released)

        self.ui.volume_slider.setRange(0, 100)
        self.ui.volume_slider.setValue(config.DEFAULT_VOLUME)
        self.player.audio_set_volume(config.DEFAULT_VOLUME)
        self.ui.volume_label.setText(str(config.DEFAULT_VOLUME))

        self.ui.volume_slider.valueChanged.connect(self.change_volume)

    def change_volume(self, value):
        self.player.audio_set_volume(value)
        self.ui.volume_label.setText(str(value))

    # Function that gets selected music/song file, including its metadata (images and artist).
    def load_music(self):
        song_path = os.path.join(config.LOCAL_MUSIC_PATH, self.song_title)
        if not os.path.exists(song_path):
            print("Song file not found:", song_path)
            return

        try:
            media = self.instance.media_new(song_path)
            self.player.set_media(media)
        except Exception as e:
            print("Warning: Failed to load media:", e)

        self.ui.song_title.setText(os.path.basename(song_path).removesuffix('.mp3'))
        self.setWindowTitle('Now playing: ' + self.song_title.replace('.mp3', ''))

        # Get metadata (artist + album art)
        artist, pixmap = get_music_metadata(song_path)
        self.artist_full_text = artist or "Unknown Artist"
        self.ui.artist_name.setText(artist)
        self.scroll_offset = 0

        # Ensure CD label display remains centered and fills properly
        if pixmap is not None and hasattr(pixmap, "isNull") and not pixmap.isNull():
            try:
                size = max(1, self.ui.spinner.width())  # avoid zero
                cd_pixmap = self.cd_pixmap(pixmap, size)
                self.fixed_pixmap = cd_pixmap
                self.ui.spinner.setPixmap(cd_pixmap)
            except Exception as e:
                print("Error handling album art pixmap:", e)

        # Load lyrics
        try:
            self.lyrics_data = get_lyrics(song_path) or []
        except Exception as e:
            print("Error loading lyrics:", e)
            self.lyrics_data = []

        self.current_lyric_index = 0

        # Display the lyrics if available
        if getattr(self, "lyrics_label", None) is not None:
            if self.lyrics_data:
                try:
                    self.lyrics_label.setText(self.lyrics_data[0][1])
                except Exception:
                    self.lyrics_label.setText("No lyrics available.")
            else:
                self.lyrics_label.setText("No lyrics available.")

        # Reset progress
        self.ui.progressTime.setValue(0)
        self.ui.currentTime.setText("00:00")
        self.ui.totalTime.setText("00:00")

    # Function that changes the song
    def change_music(self, song):
        self.song_title = song
        self.load_music()
        self.play()

    # Displays all songs inside the assigned folder
    def display_local_playlist(self, local_playlist=None):
        if local_playlist is None:
            return

        scroll_area = QScrollArea()
        scroll_area.setWidgetResizable(True)
        scroll_area.setHorizontalScrollBarPolicy(Qt.ScrollBarPolicy.ScrollBarAlwaysOff)
        scroll_area.setStyleSheet("QScrollArea { background: transparent; border: none;}")

        content_widget = QWidget()
        content_layout = QVBoxLayout(content_widget)
        content_layout.setContentsMargins(0, 0, 0, 0)
        content_layout.setSpacing(6)

        for i, song_title in enumerate(local_playlist):
            song_btn = QPushButton(song_title.replace('.mp3', ''))
            song_btn.setCheckable(True)
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
            ''')
            song_btn.clicked.connect(partial(self.change_music, song_title))

            self.button_group.addButton(song_btn, id=i)
            content_layout.addWidget(song_btn)

        scroll_area.setWidget(content_widget)
        self.ui.list_layout.addWidget(scroll_area)

    def scroll_artist_name(self):
        label = self.ui.artist_name
        text = self.artist_full_text

        if not text:
            return

        fm = label.fontMetrics()
        text_width = fm.horizontalAdvance(text)
        label_width = label.width()

        # Only scroll if text is wider than label
        if text_width > label_width:
            self.scroll_offset = (self.scroll_offset + 3) % (text_width + 30)
            display_text = text + "   " + text
            label.setText(display_text)
            label.setIndent(-self.scroll_offset)
        else:
            label.setText(text)
            label.setIndent(0)

    def setup_lyrics_display(self):
        """Create scrollable lyrics area dynamically inside lyrics_layout."""
        if not hasattr(self.ui, "lyrics_layout") or self.ui.lyrics_layout is None:
            print("UI does not have lyrics_layout; skipping lyrics setup.")
            return

        self.lyrics_scroll = QScrollArea()
        self.lyrics_scroll.setWidgetResizable(True)
        self.lyrics_scroll.setHorizontalScrollBarPolicy(Qt.ScrollBarPolicy.ScrollBarAlwaysOff)
        self.lyrics_scroll.setStyleSheet("QScrollArea { background: transparent; border: none;}")

        self.lyrics_container = QWidget()
        self.lyrics_layout_inner = QVBoxLayout(self.lyrics_container)
        self.lyrics_layout_inner.setContentsMargins(15, 15, 15, 15)
        self.lyrics_layout_inner.setSpacing(10)

        self.lyrics_label = QLabel("No lyrics loaded.")
        self.lyrics_label.setWordWrap(True)
        self.lyrics_label.setAlignment(Qt.AlignmentFlag.AlignHCenter | Qt.AlignmentFlag.AlignTop)
        self.lyrics_label.setStyleSheet("QLabel { color: white; font-size: 16px; }")

        self.lyrics_layout_inner.addWidget(self.lyrics_label)
        self.lyrics_scroll.setWidget(self.lyrics_container)

        try:
            self.ui.lyrics_layout.addWidget(self.lyrics_scroll)
        except Exception as e:
            print("Could not add lyrics_scroll to lyrics_layout:", e)

    def sync_lyrics(self, position):
        """Update displayed lyric based on current song position (position is ms)."""
        if not getattr(self, "lyrics_data", None):
            return

        if len(self.lyrics_data) == 1 and self.lyrics_data[0][0] == 0:
            try:
                self.lyrics_label.setText(self.lyrics_data[0][1])
            except Exception:
                pass
            return

        idx = 0
        for i, (timestamp, text) in enumerate(self.lyrics_data):
            try:
                if position < int(timestamp):
                    break
                idx = i
            except Exception:
                continue

        self.current_lyric_index = idx

        if 0 <= self.current_lyric_index < len(self.lyrics_data):
            try:
                self.lyrics_label.setText(self.lyrics_data[self.current_lyric_index][1])
            except Exception:
                pass

        try:
            sb = self.lyrics_scroll.verticalScrollBar()
            maximum = sb.maximum()
            denom = max(len(self.lyrics_data), 1)
            fraction = self.current_lyric_index / denom
            value = int(maximum * fraction)
            sb.setValue(value)
        except Exception:
            pass

    @staticmethod
    def cd_pixmap(pixmap, size, hole_ratio=0.25):
        w, h = pixmap.width(), pixmap.height()
        if w != h:
            side = min(w, h)
            x = (w - side) // 2
            y = (h - side) // 2
            pixmap = pixmap.copy(x, y, side, side)

        scaled = pixmap.scaled(size, size, Qt.AspectRatioMode.IgnoreAspectRatio,
                               Qt.TransformationMode.SmoothTransformation)

        mask = QPixmap(size, size)
        mask.fill(Qt.GlobalColor.transparent)

        painter = QPainter(mask)
        painter.setRenderHint(QPainter.RenderHint.Antialiasing)

        outer_path = QPainterPath()
        outer_path.addEllipse(0, 0, size, size)

        hole_size = int(size * hole_ratio)
        hole_offset = (size - hole_size) // 2
        inner_path = QPainterPath()
        inner_path.addEllipse(hole_offset, hole_offset, hole_size, hole_size)

        final_path = outer_path.subtracted(inner_path)
        painter.setClipPath(final_path)
        painter.drawPixmap(0, 0, scaled)
        painter.end()

        return mask

    def spin_pixmap(self):
        if hasattr(self, "fixed_pixmap") and not self.fixed_pixmap.isNull():
            self.rotation_angle = (self.rotation_angle + 2) % 360

            size = self.fixed_pixmap.size()
            rotated_canvas = QPixmap(size)
            rotated_canvas.fill(Qt.GlobalColor.transparent)

            painter = QPainter(rotated_canvas)
            painter.setRenderHint(QPainter.RenderHint.SmoothPixmapTransform)
            painter.translate(size.width() / 2, size.height() / 2)
            painter.rotate(self.rotation_angle)
            painter.translate(-size.width() / 2, -size.height() / 2)
            painter.drawPixmap(0, 0, self.fixed_pixmap)
            painter.end()

            self.ui.spinner.setPixmap(rotated_canvas)

    def switch_to_playback(self):
        pass

    def switch_to_playlist(self):
        pass

    # Unified play/pause toggle
    def toggle_play_pause(self):
        if not self.isPlaying:
            self.play()
        else:
            self.pause()

    def play(self):
        self.player.play()
        self.isPlaying = True
        self.ui.playButton.setIcon(QIcon(config.ICON_PATH + "pause.svg"))
        self.start_spin()

    def pause(self):
        self.player.pause()
        self.isPlaying = False
        self.ui.playButton.setIcon(QIcon(config.ICON_PATH + "play.svg"))
        self.pause_spin()

    def loop_shuffle(self):
        self.repeat += 1
        if self.repeat >= 3:
            self.repeat = 0

        if self.repeat == 0:
            self.ui.loop_shuffle.setIcon(QIcon(config.ICON_PATH + "continue.svg"))
            print('continue')
        elif self.repeat == 1:
            self.ui.loop_shuffle.setIcon(QIcon(config.ICON_PATH + "loop.svg"))
            print('loop')
        elif self.repeat == 2:
            self.ui.loop_shuffle.setIcon(QIcon(config.ICON_PATH + "shuffle.svg"))
            print('shuffle')

    def start_spin(self):
        if hasattr(self, "rotation_timer") and not self.rotation_timer.isActive():
            self.rotation_timer.start(30)

    def pause_spin(self):
        if hasattr(self, "rotation_timer") and self.rotation_timer.isActive():
            self.rotation_timer.stop()

    def slider_pressed(self):
        self.is_seeking = True

    def slider_released(self):
        self.is_seeking = False
        position = self.ui.progressTime.value()
        duration = self.player.get_length()
        if duration > 0:
            self.player.set_time(position)

    def update_position_and_duration(self):
        """Poll VLC for position and duration, simulate Qt signals"""
        if not self.player or not self.player.get_media():
            return

        duration = self.player.get_length()  # in ms
        position = self.player.get_time()     # in ms

        # Update duration once
        if duration > 0 and self.ui.progressTime.maximum() != duration:
            self.ui.progressTime.setMaximum(duration)
            self.ui.totalTime.setText(self.format_time(duration))

        # Update position
        if not getattr(self, "is_seeking", False) and position >= 0:
            self.ui.progressTime.setValue(position)
            self.ui.currentTime.setText(self.format_time(position))

            # Sync lyrics
            if hasattr(self, "lyrics_data") and self.lyrics_data:
                self.sync_lyrics(position)

        # Check for end of media
        if duration > 0 and position >= duration - 500:  # near end
            if hasattr(self, "_end_checked") and self._end_checked:
                return
            self._end_checked = True
            self.check_song_end()
        else:
            self._end_checked = False

    def seek_position(self, position):
        self.player.set_time(position)

    def format_time(self, ms):
        if ms < 0:
            return "00:00"
        seconds = ms // 1000
        minutes = seconds // 60
        seconds = seconds % 60
        return f"{minutes:02}:{seconds:02}"

    # Function that interacts after the song ends (3 modes)
    def check_song_end(self):
        if self.repeat == 0:
            print("Continue mode - next song")
            local_playlist = sorted(os.listdir(config.LOCAL_MUSIC_PATH))
            current_index = local_playlist.index(self.song_title)
            next_index = (current_index + 1) % len(local_playlist)
            self.change_music(local_playlist[next_index])
        elif self.repeat == 1:
            print("Looping current song...")
            self.player.set_time(0)
            self.player.play()
        elif self.repeat == 2:
            print("Shuffle mode - random song")
            local_playlist = sorted(os.listdir(config.LOCAL_MUSIC_PATH))
            next_song = random.choice(local_playlist)
            self.change_music(next_song)