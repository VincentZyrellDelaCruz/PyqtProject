"""
Mixin class for movie/TV show detail views with trailer support.
"""
from PyQt6.QtWidgets import (QWidget, QLabel, QPushButton, QHBoxLayout, QVBoxLayout, 
                             QFrame, QSizePolicy, QScrollArea, QStackedWidget)
from PyQt6.QtCore import Qt, QThreadPool
from PyQt6.QtGui import QPixmap, QFont
from controllers.movie_api_client import fetch_movie_details, fetch_tv_details, get_image_url
from controllers.async_loader import ImageLoader
import os

try:
    import vlc
    VLC_AVAILABLE = True
except ImportError:
    VLC_AVAILABLE = False

try:
    import yt_dlp
    YT_DLP_AVAILABLE = True
except ImportError:
    YT_DLP_AVAILABLE = False


class DetailViewMixin:
    """Mixin to add detail view functionality to movie/TV screens."""
    
    def setup_detail_view(self):
        """Initialize the stacked widget for list/detail view switching."""
        # Create stacked widget if not exists
        if not hasattr(self, 'stack'):
            self.stack = QStackedWidget()
            
            # Move existing content to list view
            self.list_widget = QWidget()
            list_layout = QVBoxLayout(self.list_widget)
            list_layout.setContentsMargins(0, 0, 0, 0)
            
            # Transfer main_layout contents
            while self.main_layout.count():
                item = self.main_layout.takeAt(0)
                if item.widget():
                    list_layout.addWidget(item.widget())
                elif item.layout():
                    list_layout.addLayout(item.layout())
            
            # Create detail view
            self.detail_widget = QWidget()
            self.init_detail_ui()
            
            # Add to stack
            self.stack.addWidget(self.list_widget)
            self.stack.addWidget(self.detail_widget)
            
            # Add stack to main layout
            self.main_layout.addWidget(self.stack)
            
            # Initialize VLC
            self.vlc_instance = None
            self.media_player = None
            self.video_frame = None
    
    def init_detail_ui(self):
        """Initialize detail view UI."""
        layout = QVBoxLayout(self.detail_widget)
        layout.setContentsMargins(0, 0, 0, 0)
        layout.setSpacing(0)

        # Scroll area for details
        scroll_area = QScrollArea()
        scroll_area.setWidgetResizable(True)
        scroll_area.setHorizontalScrollBarPolicy(Qt.ScrollBarPolicy.ScrollBarAlwaysOff)
        scroll_area.setStyleSheet("background: #121212; border: none;")

        self.detail_content = QWidget()
        self.detail_layout = QVBoxLayout(self.detail_content)
        self.detail_layout.setContentsMargins(0, 0, 0, 0)
        self.detail_layout.setSpacing(0)

        scroll_area.setWidget(self.detail_content)
        layout.addWidget(scroll_area)
    
    def show_movie_details(self, movie_id):
        """Show movie details in the same tab with throttling."""
        # Check if throttle exists and can proceed
        if hasattr(self, 'click_throttle') and not self.click_throttle.can_proceed():
            print(f"Throttled: Please wait {self.click_throttle.wait_time()}ms")
            return
        self._show_details('movie', movie_id, fetch_movie_details)
    
    def show_tv_details(self, tv_id):
        """Show TV show details in the same tab with throttling."""
        # Check if throttle exists and can proceed
        if hasattr(self, 'click_throttle') and not self.click_throttle.can_proceed():
            print(f"Throttled: Please wait {self.click_throttle.wait_time()}ms")
            return
        self._show_details('tv', tv_id, fetch_tv_details)
    
    def _show_details(self, content_type, content_id, fetch_function):
        """Generic method to show movie or TV details."""
        # Clear previous details
        for i in reversed(range(self.detail_layout.count())): 
            widget = self.detail_layout.itemAt(i).widget()
            if widget:
                widget.deleteLater()

        # Show loading
        loading = QLabel("Loading details...")
        loading.setFont(QFont("Segoe UI", 16))
        loading.setStyleSheet("color: white; padding: 40px;")
        loading.setAlignment(Qt.AlignmentFlag.AlignCenter)
        self.detail_layout.addWidget(loading)

        # Switch to detail view
        self.stack.setCurrentIndex(1)

        # Load details in background
        def on_details_loaded(details):
            # Remove loading
            for i in reversed(range(self.detail_layout.count())): 
                widget = self.detail_layout.itemAt(i).widget()
                if widget:
                    widget.deleteLater()

            # Create detail view
            if content_type == 'movie':
                self.create_movie_detail_view(details)
            else:
                self.create_tv_detail_view(details)

        def on_error(error_msg):
            loading.setText(f"Error loading details: {error_msg}")

        worker = fetch_function(content_id, on_details_loaded, on_error)
        self.active_workers.append(worker)
        QThreadPool.globalInstance().start(worker)
    
    def create_movie_detail_view(self, movie):
        """Create detailed movie view."""
        self._create_detail_view(movie, 'movie')
    
    def create_tv_detail_view(self, show):
        """Create detailed TV show view."""
        self._create_detail_view(show, 'tv')
    
    def _create_detail_view(self, content, content_type):
        """Generic detail view creation for movie or TV."""
        # Back button
        back_btn = QPushButton("← Back to List")
        back_btn.setFixedHeight(40)
        back_btn.setCursor(Qt.CursorShape.PointingHandCursor)
        back_btn.setStyleSheet("""
            QPushButton {
                background-color: #E50914;
                color: white;
                border: none;
                padding: 10px 20px;
                font-size: 14px;
                font-weight: bold;
                text-align: left;
            }
            QPushButton:hover {
                background-color: #B2070F;
            }
        """)
        back_btn.clicked.connect(lambda: self.go_back_to_list())
        self.detail_layout.addWidget(back_btn)

        # Backdrop image
        backdrop_container = QLabel()
        backdrop_container.setFixedHeight(400)
        backdrop_container.setScaledContents(True)
        backdrop_container.setStyleSheet("background-color: #000;")
        backdrop_url = get_image_url(content.get("backdrop_path"), "w780")
        if backdrop_url:
            def on_backdrop_loaded(url, data):
                if not data.isEmpty():
                    pixmap = QPixmap()
                    pixmap.loadFromData(data)
                    if not pixmap.isNull():
                        backdrop_container.setPixmap(pixmap)
            
            loader = ImageLoader(backdrop_url)
            loader.signals.finished.connect(on_backdrop_loaded)
            self.active_loaders.append(loader)
            QThreadPool.globalInstance().start(loader)
        self.detail_layout.addWidget(backdrop_container)

        # Content area
        content_widget = QWidget()
        content_widget.setStyleSheet("background-color: #1E1E1E;")
        content_layout = QVBoxLayout(content_widget)
        content_layout.setContentsMargins(30, 30, 30, 30)
        content_layout.setSpacing(20)

        # Title
        title_text = content.get("title" if content_type == 'movie' else "name", "Unknown")
        title = QLabel(title_text)
        title.setFont(QFont("Segoe UI", 28, QFont.Weight.Bold))
        title.setStyleSheet("color: white;")
        title.setWordWrap(True)
        content_layout.addWidget(title)

        # Info row
        info_layout = QHBoxLayout()
        if content_type == 'movie':
            year = content.get("release_date", "")[:4] if content.get("release_date") else "N/A"
            runtime = content.get("runtime", 0)
            runtime_text = f"{runtime} min" if runtime else "N/A"
            rating = content.get("vote_average", 0)
            info_label = QLabel(f"{year}  •  {runtime_text}  •  ⭐ {rating:.1f}/10")
        else:
            year = content.get("first_air_date", "")[:4] if content.get("first_air_date") else "N/A"
            seasons = content.get("number_of_seasons", 0)
            episodes = content.get("number_of_episodes", 0)
            rating = content.get("vote_average", 0)
            info_label = QLabel(f"{year}  •  {seasons} Seasons  •  {episodes} Episodes  •  ⭐ {rating:.1f}/10")
        
        info_label.setFont(QFont("Segoe UI", 14))
        info_label.setStyleSheet("color: #BBB;")
        info_layout.addWidget(info_label)
        info_layout.addStretch()
        content_layout.addLayout(info_layout)

        # Genres
        genres = content.get("genres", [])
        if genres:
            genre_layout = QHBoxLayout()
            for genre in genres[:5]:
                genre_btn = QPushButton(genre)
                genre_btn.setStyleSheet("""
                    QPushButton {
                        background-color: #E50914;
                        color: white;
                        border: none;
                        border-radius: 4px;
                        padding: 6px 12px;
                        font-size: 12px;
                    }
                """)
                genre_layout.addWidget(genre_btn)
            genre_layout.addStretch()
            content_layout.addLayout(genre_layout)

        # Overview
        overview_label = QLabel("Overview")
        overview_label.setFont(QFont("Segoe UI", 16, QFont.Weight.Bold))
        overview_label.setStyleSheet("color: white;")
        content_layout.addWidget(overview_label)

        overview_text = QLabel(content.get("overview", "No overview available."))
        overview_text.setFont(QFont("Segoe UI", 13))
        overview_text.setStyleSheet("color: #CCC; line-height: 1.6;")
        overview_text.setWordWrap(True)
        content_layout.addWidget(overview_text)

        # Director/Creator
        if content_type == 'movie':
            director = content.get("director", "N/A")
            director_label = QLabel(f"<b>Director:</b> {director}")
            director_label.setFont(QFont("Segoe UI", 13))
            director_label.setStyleSheet("color: white;")
            content_layout.addWidget(director_label)
        else:
            creators = content.get("created_by", [])
            if creators:
                creator_text = ", ".join(creators)
                creator_label = QLabel(f"<b>Created by:</b> {creator_text}")
                creator_label.setFont(QFont("Segoe UI", 13))
                creator_label.setStyleSheet("color: white;")
                content_layout.addWidget(creator_label)

        # Cast
        cast = content.get("cast", [])
        if cast:
            cast_label = QLabel("Cast")
            cast_label.setFont(QFont("Segoe UI", 16, QFont.Weight.Bold))
            cast_label.setStyleSheet("color: white;")
            content_layout.addWidget(cast_label)

            cast_text = ", ".join([f"{c['name']} ({c['character']})" for c in cast[:5]])
            cast_info = QLabel(cast_text)
            cast_info.setFont(QFont("Segoe UI", 12))
            cast_info.setStyleSheet("color: #CCC;")
            cast_info.setWordWrap(True)
            content_layout.addWidget(cast_info)

        # Trailer player section
        trailer_key = content.get("trailer_key")
        if trailer_key and VLC_AVAILABLE and YT_DLP_AVAILABLE:
            trailer_section = self.create_trailer_player(trailer_key)
            content_layout.addWidget(trailer_section)
        elif trailer_key and VLC_AVAILABLE:
            # VLC available but no yt-dlp
            vlc_msg = QLabel("📹 Trailer available but yt-dlp is not installed.\nRun: pip install yt-dlp")
            vlc_msg.setFont(QFont("Segoe UI", 12))
            vlc_msg.setStyleSheet("color: #FFA500; background-color: #2A2A2A; padding: 15px; border-radius: 8px;")
            vlc_msg.setAlignment(Qt.AlignmentFlag.AlignCenter)
            vlc_msg.setFixedHeight(80)
            vlc_msg.setWordWrap(True)
            content_layout.addWidget(vlc_msg)
        elif trailer_key:
            # Show message that VLC is not available
            vlc_msg = QLabel("📹 Trailer available but VLC is not installed.\nRun: pip install python-vlc yt-dlp")
            vlc_msg.setFont(QFont("Segoe UI", 12))
            vlc_msg.setStyleSheet("color: #FFA500; background-color: #2A2A2A; padding: 15px; border-radius: 8px;")
            vlc_msg.setAlignment(Qt.AlignmentFlag.AlignCenter)
            vlc_msg.setFixedHeight(80)
            vlc_msg.setWordWrap(True)
            content_layout.addWidget(vlc_msg)
        else:
            # No trailer available
            no_trailer_msg = QLabel("ℹ️ No trailer available for this " + ("movie" if content_type == 'movie' else "TV show") + ".\nThis content may not have a trailer in TMDB database.")
            no_trailer_msg.setFont(QFont("Segoe UI", 12))
            no_trailer_msg.setStyleSheet("color: #888; background-color: #2A2A2A; padding: 15px; border-radius: 8px;")
            no_trailer_msg.setAlignment(Qt.AlignmentFlag.AlignCenter)
            no_trailer_msg.setFixedHeight(80)
            no_trailer_msg.setWordWrap(True)
            content_layout.addWidget(no_trailer_msg)

        content_layout.addStretch()
        self.detail_layout.addWidget(content_widget)
    
    def create_trailer_player(self, trailer_key):
        """Create VLC player for YouTube trailer."""
        # Container with margins
        container = QWidget()
        container_layout = QVBoxLayout(container)
        container_layout.setContentsMargins(0, 20, 0, 0)
        
        # Trailer header
        trailer_header = QLabel("🎬 Official Trailer")
        trailer_header.setFont(QFont("Segoe UI", 16, QFont.Weight.Bold))
        trailer_header.setStyleSheet("color: white;")
        container_layout.addWidget(trailer_header)
        
        player_container = QFrame()
        player_container.setStyleSheet("""
            QFrame {
                background-color: #000;
                border-radius: 8px;
            }
        """)
        player_container.setFixedHeight(450)
        
        player_layout = QVBoxLayout(player_container)
        player_layout.setContentsMargins(0, 0, 0, 0)
        player_layout.setSpacing(5)

        # Video frame
        self.video_frame = QFrame()
        self.video_frame.setStyleSheet("background-color: #000;")
        self.video_frame.setFixedHeight(400)
        player_layout.addWidget(self.video_frame)

        # Controls
        controls_layout = QHBoxLayout()
        controls_layout.setContentsMargins(10, 5, 10, 5)
        
        play_btn = QPushButton("▶ Play Trailer")
        play_btn.setFixedSize(120, 35)
        play_btn.setCursor(Qt.CursorShape.PointingHandCursor)
        play_btn.setStyleSheet("""
            QPushButton {
                background-color: #E50914;
                color: white;
                border: none;
                border-radius: 4px;
                font-size: 13px;
                font-weight: bold;
            }
            QPushButton:hover {
                background-color: #B2070F;
            }
        """)
        
        pause_btn = QPushButton("⏸ Pause")
        pause_btn.setFixedSize(100, 35)
        pause_btn.setCursor(Qt.CursorShape.PointingHandCursor)
        pause_btn.setStyleSheet("""
            QPushButton {
                background-color: #444;
                color: white;
                border: none;
                border-radius: 4px;
                font-size: 13px;
                font-weight: bold;
            }
            QPushButton:hover {
                background-color: #555;
            }
        """)
        
        stop_btn = QPushButton("⏹ Stop")
        stop_btn.setFixedSize(100, 35)
        stop_btn.setCursor(Qt.CursorShape.PointingHandCursor)
        stop_btn.setStyleSheet("""
            QPushButton {
                background-color: #444;
                color: white;
                border: none;
                border-radius: 4px;
                font-size: 13px;
                font-weight: bold;
            }
            QPushButton:hover {
                background-color: #555;
            }
        """)

        status_label = QLabel("Ready to play")
        status_label.setStyleSheet("color: #AAA; font-size: 12px;")

        controls_layout.addWidget(play_btn)
        controls_layout.addWidget(pause_btn)
        controls_layout.addWidget(stop_btn)
        controls_layout.addWidget(status_label)
        controls_layout.addStretch()
        
        player_layout.addLayout(controls_layout)
        container_layout.addWidget(player_container)

        # Initialize VLC
        try:
            if not self.vlc_instance:
                self.vlc_instance = vlc.Instance('--quiet', '--no-xlib' if os.name != 'nt' else '')
            
            self.media_player = self.vlc_instance.media_player_new()
            
            # Set video output to the frame
            if os.name == 'nt':  # Windows
                self.media_player.set_hwnd(int(self.video_frame.winId()))
            elif os.name == 'darwin':  # macOS
                self.media_player.set_nsobject(int(self.video_frame.winId()))
            else:  # Linux
                self.media_player.set_xwindow(int(self.video_frame.winId()))
            
            # YouTube trailer URL
            youtube_url = f"https://www.youtube.com/watch?v={trailer_key}"
            status_label.setText("Extracting stream URL...")
            
            # Get streamable URL using yt-dlp
            try:
                ydl_opts = {
                    'format': 'best[height<=720]/best',
                    'quiet': True,
                    'no_warnings': True,
                    'extract_flat': False,
                }
                with yt_dlp.YoutubeDL(ydl_opts) as ydl:
                    info = ydl.extract_info(youtube_url, download=False)
                    stream_url = info['url']
                    
                    media = self.vlc_instance.media_new(stream_url)
                    self.media_player.set_media(media)
                    
                    play_btn.clicked.connect(lambda: self.play_trailer(status_label))
                    pause_btn.clicked.connect(lambda: self.pause_trailer(status_label))
                    stop_btn.clicked.connect(lambda: self.stop_trailer(status_label))
                    
                    status_label.setText("Trailer ready - Click Play to watch")
                    
            except Exception as e:
                print(f"yt-dlp extraction error: {e}")
                error_text = str(e)
                if "Video unavailable" in error_text or "Private video" in error_text:
                    status_label.setText("❌ Trailer not available on YouTube")
                elif "This video is not available" in error_text:
                    status_label.setText("❌ TMDB trailer link is broken or private")
                else:
                    status_label.setText(f"❌ Could not load trailer: Connection issue")
                # Disable buttons
                play_btn.setEnabled(False)
                pause_btn.setEnabled(False)
                stop_btn.setEnabled(False)
            
        except Exception as e:
            status_label.setText(f"Error initializing player: {str(e)[:50]}")
            print(f"VLC error: {e}")
        
        return container
    
    def go_back_to_list(self):
        """Go back to list view and stop any playing media."""
        if hasattr(self, 'media_player') and self.media_player:
            self.media_player.stop()
        if hasattr(self, 'stack'):
            self.stack.setCurrentIndex(0)
    
    def play_trailer(self, status_label):
        """Play the trailer."""
        if self.media_player:
            self.media_player.play()
            status_label.setText("▶ Playing...")

    def pause_trailer(self, status_label):
        """Pause the trailer."""
        if self.media_player:
            self.media_player.pause()
            status_label.setText("⏸ Paused")

    def stop_trailer(self, status_label):
        """Stop the trailer."""
        if self.media_player:
            self.media_player.stop()
            status_label.setText("⏹ Stopped")
    
    def cleanup_detail_view(self):
        """Clean up VLC resources."""
        if hasattr(self, 'media_player') and self.media_player:
            self.media_player.stop()
            self.media_player.release()
            self.media_player = None
        
        if hasattr(self, 'vlc_instance') and self.vlc_instance:
            self.vlc_instance.release()
            self.vlc_instance = None
