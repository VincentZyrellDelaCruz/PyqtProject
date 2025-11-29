from PyQt6.QtWidgets import (QWidget, QLabel, QPushButton, QHBoxLayout, QVBoxLayout, 
                             QFrame, QSizePolicy, QScrollArea, QStackedWidget, QTextEdit)
from PyQt6.QtCore import Qt, QSize, QThreadPool
from PyQt6.QtGui import QPixmap, QFont, QIcon
from controllers.movie_api_client import (fetch_trending_movies_sync, fetch_trending_tv_shows_sync,
                                           fetch_kdramas_sync, fetch_movie_details, fetch_tv_details,
                                           get_image_url, MOVIE_GENRES)
from controllers.clickable import ClickableLabel
from controllers.async_loader import ImageLoader, load_placeholder_pixmap
import os, config

try:
    import vlc
    VLC_AVAILABLE = True
except ImportError:
    VLC_AVAILABLE = False
    print("VLC not available. Install python-vlc to enable trailer playback.")

try:
    import yt_dlp
    YT_DLP_AVAILABLE = True
except ImportError:
    YT_DLP_AVAILABLE = False
    print("yt-dlp not available. Install yt-dlp for better YouTube playback.")

class MovieHomeScreen(QWidget):
    def __init__(self, app_controller=None):
        super().__init__()

        self.app_controller = app_controller
        self.active_loaders = []
        self.active_workers = []
        self.vlc_instance = None
        self.media_player = None
        self.video_frame = None

        self.setSizePolicy(QSizePolicy.Policy.Expanding, QSizePolicy.Policy.Expanding)
        self.setStyleSheet("background-color: #121212;")

        self._placeholder = load_placeholder_pixmap()

        # Stacked widget to switch between list and detail views
        self.stack = QStackedWidget()
        main_layout = QVBoxLayout(self)
        main_layout.setContentsMargins(0, 0, 0, 0)
        main_layout.addWidget(self.stack)

        # Create list view
        self.list_widget = QWidget()
        self.init_list_ui()
        self.stack.addWidget(self.list_widget)

        # Create detail view
        self.detail_widget = QWidget()
        self.init_detail_ui()
        self.stack.addWidget(self.detail_widget)

        self.stack.setCurrentIndex(0)  # Start with list view

    def init_list_ui(self):
        # Main scroll area for all sections
        main_scroll = QScrollArea()
        main_scroll.setWidgetResizable(True)
        main_scroll.setHorizontalScrollBarPolicy(Qt.ScrollBarPolicy.ScrollBarAlwaysOff)
        main_scroll.setStyleSheet("background: #121212; border: none;")

        scroll_content = QWidget()
        layout = QVBoxLayout(scroll_content)
        layout.setContentsMargins(0, 20, 0, 20)
        layout.setSpacing(30)

        # Trending Movies Section
        trending_movies_section = self.create_netflix_row("Trending Movies", "movies")
        layout.addWidget(trending_movies_section)

        # Trending TV Shows Section
        trending_tv_section = self.create_netflix_row("Trending TV Shows", "tv")
        layout.addWidget(trending_tv_section)

        # K-Dramas Section
        kdrama_section = self.create_netflix_row("Popular K-Dramas", "kdrama")
        layout.addWidget(kdrama_section)

        layout.addStretch()
        
        main_scroll.setWidget(scroll_content)
        
        list_layout = QVBoxLayout(self.list_widget)
        list_layout.setContentsMargins(0, 0, 0, 0)
        list_layout.addWidget(main_scroll)

    def init_detail_ui(self):
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

    def create_netflix_row(self, title, content_type):
        """Create a Netflix-style horizontal scrolling row."""
        container = QWidget()
        container_layout = QVBoxLayout(container)
        container_layout.setContentsMargins(24, 0, 24, 0)
        container_layout.setSpacing(10)

        # Row title
        title_label = QLabel(title)
        title_label.setFont(QFont("Segoe UI", 18, QFont.Weight.Bold))
        title_label.setStyleSheet("color: white;")
        container_layout.addWidget(title_label)

        # Horizontal scroll area
        scroll_area = QScrollArea()
        scroll_area.setWidgetResizable(False)
        scroll_area.setHorizontalScrollBarPolicy(Qt.ScrollBarPolicy.ScrollBarAsNeeded)
        scroll_area.setVerticalScrollBarPolicy(Qt.ScrollBarPolicy.ScrollBarAlwaysOff)
        scroll_area.setFixedHeight(290)
        scroll_area.setStyleSheet("""
            QScrollArea {
                background: transparent;
                border: none;
            }
            QScrollBar:horizontal {
                background: #1E1E1E;
                height: 8px;
                border-radius: 4px;
            }
            QScrollBar::handle:horizontal {
                background: #E50914;
                border-radius: 4px;
                min-width: 20px;
            }
            QScrollBar::add-line:horizontal,
            QScrollBar::sub-line:horizontal {
                width: 0;
                height: 0;
            }
        """)

        # Content widget
        scroll_content = QWidget()
        content_layout = QHBoxLayout(scroll_content)
        content_layout.setContentsMargins(0, 0, 0, 10)
        content_layout.setSpacing(15)

        # Load content based on type
        if content_type == "movies":
            items = fetch_trending_movies_sync() or []
            for item in items:
                card = self.create_netflix_card(item, "movie")
                content_layout.addWidget(card)
        elif content_type == "tv":
            items = fetch_trending_tv_shows_sync() or []
            for item in items:
                card = self.create_netflix_card(item, "tv")
                content_layout.addWidget(card)
        elif content_type == "kdrama":
            items = fetch_kdramas_sync() or []
            for item in items:
                card = self.create_netflix_card(item, "tv")
                content_layout.addWidget(card)

        content_layout.addStretch()
        scroll_content.setFixedHeight(270)
        scroll_area.setWidget(scroll_content)
        container_layout.addWidget(scroll_area)

        return container

    def create_netflix_card(self, item, item_type):
        """Create a Netflix-style card."""
        card = QFrame()
        card.setFixedSize(180, 270)
        card.setCursor(Qt.CursorShape.PointingHandCursor)
        card.setStyleSheet("""
            QFrame {
                background-color: #1E1E1E;
                border-radius: 6px;
            }
            QFrame:hover {
                background-color: #2A2A2A;
                transform: scale(1.05);
            }
        """)

        card_layout = QVBoxLayout(card)
        card_layout.setContentsMargins(0, 0, 0, 0)
        card_layout.setSpacing(8)

        # Poster
        poster_label = ClickableLabel()
        poster_label.setFixedSize(180, 240)
        poster_label.setScaledContents(True)
        poster_label.setStyleSheet("border-radius: 6px 6px 0 0; background-color: #000;")
        poster_label.setPixmap(self._placeholder)

        # Load poster image
        poster_url = get_image_url(item.get("poster_path"), "w342")
        if poster_url:
            def on_finished(url, data):
                if not data.isEmpty():
                    pixmap = QPixmap()
                    pixmap.loadFromData(data)
                    if not pixmap.isNull():
                        poster_label.setPixmap(pixmap)

            loader = ImageLoader(poster_url)
            loader.signals.finished.connect(on_finished)
            self.active_loaders.append(loader)
            QThreadPool.globalInstance().start(loader)

        # Click handler
        item_id = item.get("id")
        if item_type == "movie":
            poster_label.clicked.connect(lambda iid=item_id: self.show_movie_details(iid))
        else:
            poster_label.clicked.connect(lambda iid=item_id: self.show_tv_details(iid))

        card_layout.addWidget(poster_label)

        # Rating badge
        rating = item.get("vote_average", 0)
        if rating > 0:
            rating_label = QLabel(f"⭐ {rating:.1f}")
            rating_label.setFont(QFont("Segoe UI", 9, QFont.Weight.Bold))
            rating_label.setStyleSheet("color: #FFD700; padding: 0 8px 4px 8px; background: transparent;")
            rating_label.setAlignment(Qt.AlignmentFlag.AlignCenter)
            card_layout.addWidget(rating_label)

        return card

    def show_tv_details(self, tv_id):
        """Show TV show details in the same tab."""
        # Clear previous details
        for i in reversed(range(self.detail_layout.count())): 
            widget = self.detail_layout.itemAt(i).widget()
            if widget:
                widget.deleteLater()

        # Show loading
        loading = QLabel("Loading TV show details...")
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

            # Create TV detail view
            self.create_tv_detail_view(details)

        def on_error(error_msg):
            loading.setText(f"Error loading details: {error_msg}")

        worker = fetch_tv_details(tv_id, on_details_loaded, on_error)
        self.active_workers.append(worker)
        QThreadPool.globalInstance().start(worker)

    def create_tv_detail_view(self, show):
        """Create detailed TV show view (similar to movie view)."""
        self.create_detail_view(show, is_tv=True)

    def show_movie_details(self, movie_id):
        """Show movie details in the same tab."""
        # Clear previous details
        for i in reversed(range(self.detail_layout.count())): 
            widget = self.detail_layout.itemAt(i).widget()
            if widget:
                widget.deleteLater()

        # Show loading
        loading = QLabel("Loading movie details...")
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
            self.create_detail_view(details)

        def on_error(error_msg):
            loading.setText(f"Error loading details: {error_msg}")

        worker = fetch_movie_details(movie_id, on_details_loaded, on_error)
        self.active_workers.append(worker)
        QThreadPool.globalInstance().start(worker)

    def create_detail_view(self, content, is_tv=False):
        """Create detailed view for movie or TV show."""
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
        title_text = content.get("name" if is_tv else "title", "Unknown")
        title = QLabel(title_text)
        title.setFont(QFont("Segoe UI", 28, QFont.Weight.Bold))
        title.setStyleSheet("color: white;")
        title.setWordWrap(True)
        content_layout.addWidget(title)

        # Info row
        info_layout = QHBoxLayout()
        if is_tv:
            year = content.get("first_air_date", "")[:4] if content.get("first_air_date") else "N/A"
            seasons = content.get("number_of_seasons", 0)
            episodes = content.get("number_of_episodes", 0)
            rating = content.get("vote_average", 0)
            info_label = QLabel(f"{year}  •  {seasons} Seasons  •  {episodes} Episodes  •  ⭐ {rating:.1f}/10")
        else:
            year = content.get("release_date", "")[:4] if content.get("release_date") else "N/A"
            runtime = content.get("runtime", 0)
            runtime_text = f"{runtime} min" if runtime else "N/A"
            rating = content.get("vote_average", 0)
            info_label = QLabel(f"{year}  •  {runtime_text}  •  ⭐ {rating:.1f}/10")
        
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

        # Director (movies only)
        if not is_tv:
            director = content.get("director", "N/A")
            director_label = QLabel(f"<b>Director:</b> {director}")
            director_label.setFont(QFont("Segoe UI", 13))
            director_label.setStyleSheet("color: white;")
            content_layout.addWidget(director_label)

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

        # Trailer player section - Below cast with margins
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
            content_type = "TV show" if is_tv else "movie"
            no_trailer_msg = QLabel(f"ℹ️ No trailer available for this {content_type}.\nThis content may not have a trailer in TMDB database.")
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
                # Use specific VLC options for better compatibility
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
                    'format': 'best[height<=720]/best',  # Get best quality up to 720p
                    'quiet': True,
                    'no_warnings': True,
                    'extract_flat': False,
                }
                with yt_dlp.YoutubeDL(ydl_opts) as ydl:
                    info = ydl.extract_info(youtube_url, download=False)
                    stream_url = info['url']
                    
                    media = self.vlc_instance.media_new(stream_url)
                    self.media_player.set_media(media)
                    
                    # Connect buttons
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
        if self.media_player:
            self.media_player.stop()
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

    def cleanup(self):
        """Clean up active loaders and workers when widget is destroyed."""
        # Stop and release VLC player
        if self.media_player:
            self.media_player.stop()
            self.media_player.release()
            self.media_player = None
        
        if self.vlc_instance:
            self.vlc_instance.release()
            self.vlc_instance = None
        
        for loader in self.active_loaders:
            loader.cancel()
        self.active_loaders.clear()
        
        for worker in self.active_workers:
            worker.cancel()
        self.active_workers.clear()

    def __del__(self):
        self.cleanup()
