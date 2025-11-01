from PyQt6.QtWidgets import QApplication, QDialog, QWidget, QScrollArea, QPushButton, QButtonGroup, QVBoxLayout
from PyQt6.QtMultimedia import QMediaPlayer, QAudioOutput
from PyQt6.QtCore import Qt, QUrl, QTimer
from PyQt6.QtGui import QIcon, QPixmap, QPainter, QPainterPath
from functools import partial
from UI.music_player_ui import Ui_Dialog
from eyed3.id3.frames import ImageFrame
import sys, os, random, config, eyed3

# Temporary variables
# song_title = 'Never Gonna Give You Up.mp3'
# song_image = config.IMAGE_PATH + 'NeverGonnaGiveYouUp.jpg'

class MusicPlayer(QDialog):
    def __init__(self):
        super().__init__()

        # Loads the UI
        self.ui = Ui_Dialog()
        self.ui.setupUi(self)

        # Gets all existing music file inside local_music folder
        local_playlist = sorted(os.listdir(config.LOCAL_MUSIC_PATH))
        self.song_title = local_playlist[0] if local_playlist else ""

        # Sets to continue/non-loop by default
        self.repeat = 0

        # Sets rotation for pixmap
        self.rotation_angle = 0
        self.rotation_timer = QTimer(self)

        self.button_group = QButtonGroup(self)

        self.display_local_playlist(local_playlist)

        # Sets audio
        self.audio_output = QAudioOutput()
        self.player = QMediaPlayer()

        self.load_music()

        # Marquee-like effect
        self.scroll_timer = QTimer(self)
        self.scroll_timer.timeout.connect(self.scroll_artist_name)
        self.scroll_offset = 0
        self.artist_full_text = ""
        self.scroll_timer.start(150)  # speed (ms)

        self.isPlaying = True

        self.init_ui()

        self.play()

    def closeEvent(self, event):
        """Override close event to stop playback when dialog is closed"""
        self.player.stop()
        self.rotation_timer.stop()
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
        self.player.setAudioOutput(self.audio_output)

        self.ui.playback_tab.clicked.connect(self.switch_to_playback)
        self.ui.list_tab.clicked.connect(self.switch_to_playlist)

        self.rotation_timer.timeout.connect(self.spin_pixmap)
        self.rotation_timer.start(30)  # ~33 FPS

        self.ui.playButton.clicked.connect(self.toggle_play_pause)

        self.player.positionChanged.connect(self.update_position)
        self.player.durationChanged.connect(self.update_duration)

        self.player.mediaStatusChanged.connect(self.check_song_end)

        self.ui.progressTime.sliderPressed.connect(self.slider_pressed)
        self.ui.progressTime.sliderReleased.connect(self.slider_released)

        self.ui.volume_slider.setRange(0, 100)
        self.ui.volume_slider.setValue(config.DEFAULT_VOLUME)
        self.audio_output.setVolume(config.DEFAULT_VOLUME / 100)
        self.ui.volume_label.setText(str(config.DEFAULT_VOLUME))

        self.ui.volume_slider.valueChanged.connect(self.change_volume)

    def change_volume(self, value):
        volume = value / 100
        self.audio_output.setVolume(volume)
        self.ui.volume_label.setText(str(value))

    # Function that gets selected music/song file, including its metadata (images and artist).
    def load_music(self):
        song_path = os.path.join(config.LOCAL_MUSIC_PATH + self.song_title)

        # Checks if the song is inside the assigned local music folder
        if not os.path.exists(song_path):
            print("Song file not found:", song_path)
            return

        self.player.setSource(QUrl.fromLocalFile(song_path))
        self.ui.song_title.setText(os.path.basename(song_path).removesuffix('.mp3'))
        self.setWindowTitle('Now playing: ' + self.song_title.replace('.mp3', '_'))

        # For extracting music file's embedded image
        pixmap = None
        try:
            audiofile = eyed3.load(song_path)
            if audiofile and audiofile.tag:
                image_data = None

                artist = audiofile.tag.artist if audiofile.tag.artist else "Unknown Artist"
                self.artist_full_text = artist
                self.scroll_offset = 0
                self.ui.artist_name.setText(artist)

                for image in audiofile.tag.images:
                    if image.picture_type == ImageFrame.FRONT_COVER:
                        image_data = image.image_data
                        break

                if not image_data and audiofile.tag.images:
                    image_data = list(audiofile.tag.images)[0].image_data

                if image_data:
                    pixmap = QPixmap()
                    if pixmap.loadFromData(image_data):
                        print("Album art loaded from:", song_path)
                    else:
                        pixmap = None

        except Exception as e:
            print("Error extraction album art: ", e )

        # If artist name not set due to missing tag, set default
        if not getattr(self.ui.artist_name, "text", lambda: "")():
            self.ui.artist_name.setText("Unknown Artist")

        if not pixmap or pixmap.isNull():
            fallback_path = os.path.join(config.IMAGE_PATH, "default.png")
            pixmap = QPixmap(fallback_path)

        if not pixmap.isNull():
            cd_pixmap = self.cd_pixmap(pixmap, self.ui.spinner.width())
            self.fixed_pixmap = cd_pixmap
            self.ui.spinner.setPixmap(cd_pixmap)

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

        # print(''.join(filename for filename in filenames))

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
            # Padding spaces so the text restarts smoothly
            display_text = text + "   " + text
            label.setText(display_text)
            label.setIndent(-self.scroll_offset)
        else:
            # Reset text alignment when short
            label.setText(text)
            label.setIndent(0)

    @staticmethod
    def cd_pixmap(pixmap, size, hole_ratio = 0.25):
        # Step 1: Crop the original to a 1:1 square before scaling
        w, h = pixmap.width(), pixmap.height()
        if w != h:
            side = min(w, h)
            x = (w - side) // 2
            y = (h - side) // 2
            pixmap = pixmap.copy(x, y, side, side)

        # Step 2: Scale perfectly to the CD size (no aspect stretch)
        scaled = pixmap.scaled(size, size, Qt.AspectRatioMode.IgnoreAspectRatio,
                               Qt.TransformationMode.SmoothTransformation)

        # Step 3: Create transparent CD mask
        mask = QPixmap(size, size)
        mask.fill(Qt.GlobalColor.transparent)

        painter = QPainter(mask)
        painter.setRenderHint(QPainter.RenderHint.Antialiasing)

        # Outer circle (CD)
        outer_path = QPainterPath()
        outer_path.addEllipse(0, 0, size, size)

        # Inner hole
        hole_size = int(size * hole_ratio)
        hole_offset = (size - hole_size) // 2
        inner_path = QPainterPath()
        inner_path.addEllipse(hole_offset, hole_offset, hole_size, hole_size)

        # Combine (subtract hole)
        final_path = outer_path.subtracted(inner_path)
        painter.setClipPath(final_path)
        painter.drawPixmap(0, 0, scaled)
        painter.end()

        return mask

    def spin_pixmap(self):
        if hasattr(self, "fixed_pixmap") and not self.fixed_pixmap.isNull():
            self.rotation_angle = (self.rotation_angle + 2) % 360

            # Create a constant-size empty canvas
            size = self.fixed_pixmap.size()
            rotated_canvas = QPixmap(size)
            rotated_canvas.fill(Qt.GlobalColor.transparent)

            # Paint the rotated image centered on the canvas
            painter = QPainter(rotated_canvas)
            painter.setRenderHint(QPainter.RenderHint.SmoothPixmapTransform)
            painter.translate(size.width() / 2, size.height() / 2)
            painter.rotate(self.rotation_angle)
            painter.translate(-size.width() / 2, -size.height() / 2)
            painter.drawPixmap(0, 0, self.fixed_pixmap)
            painter.end()

            self.ui.spinner.setPixmap(rotated_canvas)

    def switch_to_playback(self):
        self.ui.stackedWidget.setCurrentIndex(0)

    def switch_to_playlist(self):
        self.ui.stackedWidget.setCurrentIndex(1)

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

        if self.repeat >= 3: self.repeat = 0

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
        # Stop auto-updating while dragging
        self.is_seeking = True

    def slider_released(self):
        # When the user releases the slider, seek to that position
        self.is_seeking = False
        self.player.setPosition(self.ui.progressTime.value())

    def update_position(self, position):
        # Only update if the user is NOT dragging
        if not getattr(self, "is_seeking", False):
            self.ui.progressTime.setValue(position)
            self.ui.currentTime.setText(self.format_time(position))

    def update_duration(self, duration):
        self.ui.progressTime.setMaximum(duration)
        self.ui.totalTime.setText(self.format_time(duration))

    def seek_position(self, position):
        self.player.setPosition(position)

    def format_time(self, ms):
        seconds = ms // 1000
        minutes = seconds // 60
        seconds = seconds % 60
        return f"{minutes:02}:{seconds:02}"

    # Function that interacts after the song ends (3 modes)
    def check_song_end(self, status):
        # Check if the current song has ended
        if status == QMediaPlayer.MediaStatus.EndOfMedia:
            # Loop mode
            # Continue mode (play next)
            if self.repeat == 0:
                print("Continue mode - next song")
                local_playlist = sorted(os.listdir(config.LOCAL_MUSIC_PATH))
                current_index = local_playlist.index(self.song_title)
                next_index = (current_index + 1) % len(local_playlist)
                self.change_music(local_playlist[next_index])
            elif self.repeat == 1:
                print("Looping current song...")
                self.player.setPosition(0)
                self.player.play()
            # Shuffle mode
            elif self.repeat == 2:
                print("Shuffle mode - random song")
                local_playlist = sorted(os.listdir(config.LOCAL_MUSIC_PATH))

                next_song = random.choice(local_playlist)
                self.change_music(next_song)


if __name__ == "__main__":
    app = QApplication(sys.argv)
    window = MusicPlayer()
    window.show()
    sys.exit(app.exec())
