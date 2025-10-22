from PyQt6.QtWidgets import QApplication, QMainWindow
from PyQt6.QtMultimedia import QMediaPlayer, QAudioOutput
from PyQt6.QtCore import Qt, QUrl, QTimer
from PyQt6.QtGui import QIcon, QPixmap, QPainter, QPainterPath
from UI.music_player_ui import Ui_Dialog
import sys, os, config

# Temporary variables
song_title = 'Never Gonna Give You Up.mp3'
song_image = config.IMAGE_PATH + 'NeverGonnaGiveYouUp.jpg'

class MusicPlayer(QMainWindow):
    def __init__(self):
        super().__init__()
        self.ui = Ui_Dialog()
        self.ui.setupUi(self)
        self.init_ui()

        self.rotation_angle = 0
        self.rotation_timer = QTimer(self)
        self.rotation_timer.timeout.connect(self.spin_pixmap)
        self.rotation_timer.start(30)  # ~33 FPS

        self.audio_output = QAudioOutput()
        self.player = QMediaPlayer()
        self.player.setAudioOutput(self.audio_output)

        # Checks if the song is inside the assigned local music folder
        song_path = os.path.join(config.LOCAL_MUSIC_PATH + song_title)
        if not os.path.exists(song_path):
            print("Song file not found:", song_path)
        else:
            self.player.setSource(QUrl.fromLocalFile(song_path))
            self.ui.song_title.setText(os.path.basename(song_path))

        self.isPlaying = True
        self.ui.playButton.clicked.connect(self.toggle_play_pause)

        self.player.positionChanged.connect(self.update_position)
        self.player.durationChanged.connect(self.update_duration)
        # self.ui.progressTime.sliderMoved.connect(self.seek_position)

        self.ui.progressTime.sliderPressed.connect(self.slider_pressed)
        self.ui.progressTime.sliderReleased.connect(self.slider_released)

        self.play()

    def init_ui(self):
        self.ui.playButton.setIcon(QIcon(config.ICON_PATH + "play.svg"))
        self.ui.nextButton.setIcon(QIcon(config.ICON_PATH + "next.svg"))
        self.ui.prevButton.setIcon(QIcon(config.ICON_PATH + "prev.svg"))

        pixmap = QPixmap(song_image)

        if not pixmap.isNull():
            cd_pixmap = self.cd_pixmap(pixmap, self.ui.spinner.width())
            self.fixed_pixmap = cd_pixmap

        self.ui.spinner.setPixmap(cd_pixmap)

    @staticmethod
    def cd_pixmap(pixmap, size, hole_ratio = 0.25):
        # Resize to square
        scaled = pixmap.scaled(size, size, Qt.AspectRatioMode.KeepAspectRatioByExpanding,
                               Qt.TransformationMode.SmoothTransformation)

        # Create base mask
        mask = QPixmap(size, size)
        mask.fill(Qt.GlobalColor.transparent)

        painter = QPainter(mask)
        painter.setRenderHint(QPainter.RenderHint.Antialiasing)

        # Outer circle
        outer_path = QPainterPath()
        outer_path.addEllipse(0, 0, size, size)

        # Inner hole
        hole_size = int(size * hole_ratio)
        hole_offset = (size - hole_size) // 2
        inner_path = QPainterPath()
        inner_path.addEllipse(hole_offset, hole_offset, hole_size, hole_size)

        # Subtract hole from outer circle
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


if __name__ == "__main__":
    app = QApplication(sys.argv)
    window = MusicPlayer()
    window.show()
    sys.exit(app.exec())
