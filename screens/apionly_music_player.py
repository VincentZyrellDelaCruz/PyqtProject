import os
import tempfile
import requests
import vlc
import yt_dlp
from functools import partial
from PyQt6.QtWidgets import QDialog, QWidget, QScrollArea, QPushButton, QButtonGroup, QVBoxLayout
from PyQt6.QtCore import Qt, QTimer
from PyQt6.QtGui import QIcon, QPixmap, QPainter, QPainterPath, QImage
from UI.music_player_ui import Ui_Dialog
import config


class ApiMusicPlayer(QDialog):
    def __init__(self, song_metadata, playlist=None, parent=None):
        super().__init__(parent)

        # UI setup
        self.ui = Ui_Dialog()
        self.ui.setupUi(self)

        self.song_metadata = song_metadata
        self.temp_dir = tempfile.TemporaryDirectory()
        self.temp_file_path = None
        self.playlist = playlist

        # Playback options
        self.repeat = 0
        self.rotation_angle = 0
        self.scroll_offset = 0
        self.artist_full_text = ""
        self.isPlaying = False
        self.current_lyric_index = 0

        # VLC instance
        self.instance = vlc.Instance('--quiet', '--no-video')
        self.player = self.instance.media_player_new()

        # Timers
        self.rotation_timer = QTimer(self)
        self.rotation_timer.timeout.connect(self.spin_pixmap)
        self.rotation_timer.start(30)  # ~33 FPS

        self.position_timer = QTimer(self)
        self.position_timer.timeout.connect(self.update_position_and_duration)
        self.position_timer.start(100)

        self.scroll_timer = QTimer(self)
        self.scroll_timer.timeout.connect(self.scroll_artist_name)
        self.scroll_timer.start(150)

        # Button group for playlist
        self.button_group = QButtonGroup(self)

        # Load music and setup UI
        self.load_music()
        self.display_playlist([])  # Empty by default
        self.init_ui()
        self.play()

    # Cleanup method to stop playback and timers
    def cleanup(self):
        # Cleanup method to stop playback and timers
        if hasattr(self, 'player') and self.player:
            self.player.stop()
        if hasattr(self, 'rotation_timer'):
            self.rotation_timer.stop()
        if hasattr(self, 'scroll_timer'):
            self.scroll_timer.stop()
        if hasattr(self, 'position_timer'):
            self.position_timer.stop()
        if hasattr(self, 'temp_dir'):
            self.temp_dir.cleanup()

    # Stop playback and clean up on close
    def closeEvent(self, event):
        # Stop playback and clean up on close
        self.cleanup()
        event.accept()

    # Setup UI signals and default values
    def init_ui(self):
        self.ui.lyrics_tab.hide()

        if not self.playlist:
            self.ui.playback_tab.hide()
            self.ui.list_tab.hide()
            self.ui.loop_shuffle.hide()

        # Setup UI signals and default values
        self.ui.playButton.setIcon(QIcon(config.ICON_PATH + "play.svg"))
        self.ui.nextButton.setIcon(QIcon(config.ICON_PATH + "next.svg"))
        self.ui.prevButton.setIcon(QIcon(config.ICON_PATH + "prev.svg"))
        self.ui.loop_shuffle.setIcon(QIcon(config.ICON_PATH + "continue.svg"))
        self.ui.volume.setIcon(QIcon(config.ICON_PATH + "volume-up.svg"))

        self.ui.volume_frame.setVisible(False)

        self.ui.loop_shuffle.clicked.connect(self.loop_shuffle)
        self.ui.playButton.clicked.connect(self.toggle_play_pause)

        self.ui.playback_tab.clicked.connect(lambda: self.ui.stackedWidget.setCurrentIndex(0))
        self.ui.list_tab.clicked.connect(lambda: self.ui.stackedWidget.setCurrentIndex(1))
        self.ui.lyrics_tab.clicked.connect(lambda: self.ui.stackedWidget.setCurrentIndex(2))

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

    # Download image from URL and return as QPixmap
    def pixmap_from_url(self, url):
        try:
            resp = requests.get(url)
            resp.raise_for_status()
            image = QImage()
            image.loadFromData(resp.content)
            return QPixmap.fromImage(image)
        except Exception as e:
            print("Failed to load pixmap from URL:", e)
            return None

    # Download audio via yt-dlp and load into VLC
    def load_music(self):
        video_id = self.song_metadata.get("videoId")
        if not video_id:
            print("No videoId for song")
            return

        ydl_opts = {
            "format": "bestaudio/best",
            "outtmpl": os.path.join(self.temp_dir.name, "%(title)s.%(ext)s"),
            "quiet": True,
            "nocheckcertificate": True,
        }
        url = f"https://www.youtube.com/watch?v={video_id}"
        try:
            with yt_dlp.YoutubeDL(ydl_opts) as ydl:
                info = ydl.extract_info(url, download=True)
                self.temp_file_path = ydl.prepare_filename(info)
        except Exception as e:
            print("Error downloading audio:", e)
            return

        if not os.path.exists(self.temp_file_path):
            print("Downloaded file not found")
            return

        media = self.instance.media_new(self.temp_file_path)
        self.player.set_media(media)

        title = self.song_metadata.get("title", "Unknown Title")
        artist = self.song_metadata.get("artist", "Unknown Artist")

        thumbnails = self.song_metadata.get("thumbnails", [])
        thumbnail_url = thumbnails if thumbnails else ""
        pixmap = self.pixmap_from_url(thumbnail_url) if thumbnail_url else None

        self.ui.song_title.setText(title)
        self.artist_full_text = artist
        self.ui.artist_name.setText(artist)
        self.scroll_offset = 0
        self.setWindowTitle('Now Playing: ' + title)

        if pixmap and not pixmap.isNull():
            size = max(1, self.ui.spinner.width())
            cd_pixmap = self.cd_pixmap(pixmap, size)
            self.fixed_pixmap = cd_pixmap
            self.ui.spinner.setPixmap(cd_pixmap)

        self.ui.progressTime.setValue(0)
        self.ui.currentTime.setText("00:00")
        self.ui.totalTime.setText("00:00")

        QTimer.singleShot(100, self.play)  # safe delayed play

    def play(self):
        if self.temp_file_path:
            self.player.play()
            self.isPlaying = True
            self.ui.playButton.setIcon(QIcon(config.ICON_PATH + "pause.svg"))

    def pause(self):
        self.player.pause()
        self.isPlaying = False
        self.ui.playButton.setIcon(QIcon(config.ICON_PATH + "play.svg"))

    def toggle_play_pause(self):
        if self.isPlaying:
            self.pause()
        else:
            self.play()

    def loop_shuffle(self):
        self.repeat = (self.repeat + 1) % 3
        if self.repeat == 0:
            self.ui.loop_shuffle.setIcon(QIcon(config.ICON_PATH + "continue.svg"))
        elif self.repeat == 1:
            self.ui.loop_shuffle.setIcon(QIcon(config.ICON_PATH + "loop.svg"))
        elif self.repeat == 2:
            self.ui.loop_shuffle.setIcon(QIcon(config.ICON_PATH + "shuffle.svg"))

    def slider_pressed(self):
        self.is_seeking = True

    def slider_released(self):
        self.is_seeking = False
        position = self.ui.progressTime.value()
        if self.player.get_length() > 0:
            self.player.set_time(position)

    def update_position_and_duration(self):
        if not self.player or not self.player.get_media():
            return

        duration = self.player.get_length()
        position = self.player.get_time()

        if duration > 0:
            self.ui.progressTime.setMaximum(duration)
            self.ui.totalTime.setText(self.format_time(duration))

        if not getattr(self, "is_seeking", False):
            self.ui.progressTime.setValue(position)
            self.ui.currentTime.setText(self.format_time(position))

    # Displays buttons for each song (empty for now, extend as needed)
    def display_playlist(self, playlist):
        scroll_area = QScrollArea()
        scroll_area.setWidgetResizable(True)
        content_widget = QWidget()
        content_layout = QVBoxLayout(content_widget)
        for i, song in enumerate(playlist):
            btn = QPushButton(song.get("title", "Unknown"))
            btn.setCheckable(True)
            btn.clicked.connect(partial(self.change_music, song))
            self.button_group.addButton(btn, i)
            content_layout.addWidget(btn)
        scroll_area.setWidget(content_widget)
        self.ui.list_layout.addWidget(scroll_area)

    def change_music(self, song):
        self.song_metadata = song
        self.load_music()
        self.play()

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
            painter.translate(size.width()/2, size.height()/2)
            painter.rotate(self.rotation_angle)
            painter.translate(-size.width()/2, -size.height()/2)
            painter.drawPixmap(0, 0, self.fixed_pixmap)
            painter.end()
            self.ui.spinner.setPixmap(rotated_canvas)

    def scroll_artist_name(self):
        label = self.ui.artist_name
        text = self.artist_full_text
        if not text:
            return
        fm = label.fontMetrics()
        text_width = fm.horizontalAdvance(text)
        label_width = label.width()
        if text_width > label_width:
            self.scroll_offset = (self.scroll_offset + 3) % (text_width + 30)
            display_text = text + "   " + text
            label.setText(display_text)
            label.setIndent(-self.scroll_offset)
        else:
            label.setText(text)
            label.setIndent(0)

    @staticmethod
    def format_time(ms):
        if ms < 0:
            return "00:00"
        seconds = ms // 1000
        minutes = seconds // 60
        seconds %= 60
        return f"{minutes:02}:{seconds:02}"

'''
if __name__ == "__main__":
    from ytmusicapi import YTMusic
    ytmusic = YTMusic()
    results = ytmusic.search("Never Gonna Give You Up", filter="songs")
    if results:
        song_metadata = {
            "title": results[0]["title"],
            "artist": results[0]["artists"][0]["name"],
            "videoId": results[0]["videoId"],
            "thumbnails": results[0]["thumbnails"]
        }
        app = QApplication(sys.argv)
        window = ApiMusicPlayer(song_metadata)
        window.show()
        sys.exit(app.exec())
'''