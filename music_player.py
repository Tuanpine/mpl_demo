import sys
from PyQt5.QtWidgets import QApplication, QMainWindow, QPushButton, QLabel, QListWidget, QVBoxLayout, QHBoxLayout, QWidget, QFileDialog, QMessageBox, QListWidgetItem, QSlider
from PyQt5.QtGui import QIcon
from PyQt5.QtCore import Qt, QTimer
import pygame
import os
import random
from visualizer import Visualizer
import soundfile as sf

class MusicPlayer(QMainWindow):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("Music Player")
        self.setMinimumSize(400, 600)  # Kích thước tối thiểu cho bảng điều khiển

        pygame.mixer.init()
        self.current_song = None
        self.playlist = []
        self.current_index = 0
        self.paused = False
        self.loop = False
        self.shuffle = False
        self.music_playing = False
        self.visualizer = Visualizer(self)
        self.visualizer_active = False

        self.timer = QTimer(self)
        self.timer.timeout.connect(self.check_song_end)
        self.timer.start(100)

        self.time_update_timer = QTimer(self)
        self.time_update_timer.timeout.connect(self.update_time)
        self.time_update_timer.start(1000)

        self.init_ui()
        self.load_playlist()

    def init_ui(self):
        self.central_widget = QWidget()
        self.setCentralWidget(self.central_widget)
        self.main_layout = QHBoxLayout(self.central_widget)

        # Control layout (bảng điều khiển)
        self.control_layout = QVBoxLayout()
        self.control_container = QWidget()
        self.control_container.setLayout(self.control_layout)
        self.control_container.setMaximumWidth(400)

        self.song_label = QLabel("Chưa chọn bài hát", self)
        self.song_label.setAlignment(Qt.AlignCenter)
        self.song_label.setStyleSheet("font-size: 16px; font-weight: bold; color: darkblue;")

        self.playlist_box = QListWidget(self)
        self.playlist_box.itemClicked.connect(self.on_select)
        self.playlist_box.setMinimumWidth(300)

        self.load_music_button = QPushButton("Load Music", self)
        self.load_music_button.setIcon(QIcon("player/icons/load.png"))
        self.load_music_button.clicked.connect(self.load_music)

        self.load_playlist_button = QPushButton("Load Playlist", self)
        self.load_playlist_button.setIcon(QIcon("player/icons/load.png"))
        self.load_playlist_button.clicked.connect(self.load_playlist_from_file)

        self.prev_button = QPushButton("Previous", self)
        self.prev_button.setIcon(QIcon("player/icons/prev.png"))
        self.prev_button.clicked.connect(self.prev_music)

        self.play_button = QPushButton("Play", self)
        self.play_button.setIcon(QIcon("player/icons/play.png"))
        self.play_button.clicked.connect(self.play_music)

        self.next_button = QPushButton("Next", self)
        self.next_button.setIcon(QIcon("player/icons/next.png"))
        self.next_button.clicked.connect(self.next_music)

        self.pause_button = QPushButton("Pause", self)
        self.pause_button.setIcon(QIcon("player/icons/pause.png"))
        self.pause_button.clicked.connect(self.toggle_pause)

        self.stop_button = QPushButton("Stop", self)
        self.stop_button.setIcon(QIcon("player/icons/stop.png"))
        self.stop_button.clicked.connect(self.stop_music)

        self.save_button = QPushButton("Save Playlist", self)
        self.save_button.setIcon(QIcon("player/icons/save.png"))
        self.save_button.clicked.connect(self.save_playlist)

        self.loop_button = QPushButton("Loop Off", self)
        self.loop_button.setIcon(QIcon("player/icons/loop.png"))
        self.loop_button.clicked.connect(self.toggle_loop)

        self.shuffle_button = QPushButton("Shuffle Off", self)
        self.shuffle_button.setIcon(QIcon("player/icons/shuffle.png"))
        self.shuffle_button.clicked.connect(self.toggle_shuffle)

        self.toggle_visualizer_button = QPushButton("Start Visualizer", self)
        self.toggle_visualizer_button.setIcon(QIcon("player/icons/start.png"))
        self.toggle_visualizer_button.clicked.connect(self.toggle_visualizer)

        self.switch_effect_button = QPushButton("Switch Effect", self)
        self.switch_effect_button.setIcon(QIcon("player/icons/switch.png"))
        self.switch_effect_button.clicked.connect(self.switch_effect)

        self.volume_slider = QSlider(Qt.Horizontal, self)
        self.volume_slider.setRange(0, 100)
        self.volume_slider.setValue(50)
        self.volume_slider.valueChanged.connect(self.set_volume)

        self.time_slider = QSlider(Qt.Horizontal, self)
        self.time_slider.setRange(0, 100)
        self.time_slider.setEnabled(False)
        self.time_slider.sliderPressed.connect(self.slider_pressed)
        self.time_slider.sliderReleased.connect(self.slider_released)
        self.time_slider.sliderMoved.connect(self.slider_moved)

        self.time_label = QLabel("00:00 / 00:00", self)
        self.time_label.setAlignment(Qt.AlignCenter)
        self.time_label.setStyleSheet("font-size: 14px; color: darkblue;")

        # Styling buttons
        buttons = [self.load_music_button, self.load_playlist_button, self.prev_button, self.play_button, 
                   self.next_button, self.pause_button, self.stop_button, self.save_button, self.loop_button, 
                   self.shuffle_button, self.toggle_visualizer_button, self.switch_effect_button]
        for button in buttons:
            button.setStyleSheet("""
                QPushButton {
                    background-color: #f0f0f0;
                    border: 1px solid #ccc;
                    border-radius: 5px;
                    padding: 8px;
                    min-width: 100px;
                }
                QPushButton:hover {
                    background-color: #e0e0e0;
                }
                QPushButton:pressed {
                    background-color: #d0d0d0;
                }
            """)

        # Control layout
        self.control_layout.addWidget(self.song_label)
        self.control_layout.addWidget(self.playlist_box)

        button_layout = QVBoxLayout()
        row1 = QHBoxLayout()
        row1.addStretch(1)
        row1.addWidget(self.load_music_button)
        row1.addWidget(self.load_playlist_button)
        row1.addStretch(1)

        row2 = QHBoxLayout()
        row2.addWidget(self.prev_button)
        row2.addWidget(self.play_button)
        row2.addWidget(self.next_button)
        row2.addStretch(1)

        row3 = QHBoxLayout()
        row3.addWidget(self.pause_button)
        row3.addWidget(self.stop_button)
        row3.addWidget(self.save_button)
        row3.addStretch(1)

        row4 = QHBoxLayout()
        row4.addStretch(1)
        row4.addWidget(self.toggle_visualizer_button)
        row4.addWidget(self.switch_effect_button)        
        row4.addStretch(1)

        bottom_row = QHBoxLayout()
        bottom_row.addStretch(1)
        bottom_row.addWidget(self.loop_button)
        bottom_row.addWidget(self.shuffle_button)
        bottom_row.addStretch(1)

        button_layout.addLayout(row1)
        button_layout.addLayout(row2)
        button_layout.addLayout(row3)
        button_layout.addLayout(row4)
        button_layout.addLayout(bottom_row)
        button_layout.addWidget(self.time_slider)
        button_layout.addWidget(self.time_label)
        button_layout.addWidget(self.volume_slider)

        self.control_layout.addLayout(button_layout)

        # Main layout
        self.main_layout.addWidget(self.control_container)
        self.main_layout.addWidget(self.visualizer)
        self.main_layout.addStretch(1)  # Đảm bảo co giãn linh hoạt

    def load_music(self):
        files, _ = QFileDialog.getOpenFileNames(self, "Chọn nhạc", "", "MP3 Files (*.mp3)")
        if files:
            self.playlist = files
            self.current_index = 0
            self.current_song = self.playlist[self.current_index]
            self.song_label.setText(os.path.basename(self.current_song))
            self.update_playlist_box()

    def load_playlist_from_file(self):
        playlist_path, _ = QFileDialog.getOpenFileName(self, "Load Playlist", "", "Text files (*.txt)")
        if playlist_path:
            try:
                with open(playlist_path, "r", encoding="utf-8") as f:
                    self.playlist = [line.strip() for line in f.readlines() if os.path.exists(line.strip())]
                self.current_index = 0
                self.current_song = self.playlist[self.current_index]
                self.song_label.setText(os.path.basename(self.current_song))
                self.update_playlist_box()
            except Exception as e:
                QMessageBox.critical(self, "Lỗi", f"Không thể đọc playlist: {e}")

    def update_playlist_box(self):
        self.playlist_box.clear()
        for song in self.playlist:
            item = QListWidgetItem(QIcon("player/icons/music.png"), os.path.basename(song))
            self.playlist_box.addItem(item)
        if self.current_index < self.playlist_box.count():
            self.playlist_box.setCurrentRow(self.current_index)

    def on_select(self, item):
        self.current_index = self.playlist_box.row(item)
        self.current_song = self.playlist[self.current_index]
        self.play_music()

    def play_music(self):
        if not self.playlist:
            QMessageBox.warning(self, "Cảnh báo", "Vui lòng chọn nhạc trước!")
            return
        if self.current_song and os.path.exists(self.current_song):
            try:
                self.visualizer.stop()
                pygame.mixer.music.load(self.current_song)
                pygame.mixer.music.play()
                self.song_label.setText(os.path.basename(self.current_song))
                self.paused = False
                self.music_playing = True
                self.pause_button.setText("Pause")
                self.time_slider.setEnabled(True)
                if self.visualizer_active:
                    self.visualizer.start(self.current_song, playing=True)
            except pygame.error as e:
                print(f"Error playing music: {e}")
                QMessageBox.critical(self, "Error", f"Could not play music: {e}")
        else:
            QMessageBox.critical(self, "Lỗi", "File nhạc không tồn tại!")

    def toggle_pause(self):
        if self.current_song:
            if self.paused:
                pygame.mixer.music.unpause()
                self.paused = False
                self.music_playing = True
                self.pause_button.setText("Pause")
                if self.visualizer_active:
                    self.visualizer.start(self.current_song, playing=True)
            else:
                pygame.mixer.music.pause()
                self.paused = True
                self.music_playing = False
                self.pause_button.setText("Resume")
                self.visualizer.stop()

    def stop_music(self):
        pygame.mixer.music.stop()
        self.song_label.setText("Đã dừng")
        self.paused = False
        self.music_playing = False
        self.pause_button.setText("Pause")
        self.time_slider.setValue(0)
        self.time_slider.setEnabled(False)
        self.visualizer.stop()

    def next_music(self):
        if self.shuffle:
            self.current_index = random.randint(0, len(self.playlist) - 1)
        elif self.playlist and self.current_index < len(self.playlist) - 1:
            self.current_index += 1
        else:
            return
        self.current_song = self.playlist[self.current_index]
        self.play_music()
        self.update_playlist_box()

    def prev_music(self):
        if self.shuffle:
            self.current_index = random.randint(0, len(self.playlist) - 1)
        elif self.playlist and self.current_index > 0:
            self.current_index -= 1
        else:
            return
        self.current_song = self.playlist[self.current_index]
        self.play_music()
        self.update_playlist_box()

    def check_song_end(self):
        if not pygame.mixer.music.get_busy() and self.music_playing and not self.paused:
            if self.loop:
                self.play_music()
            elif self.current_index < len(self.playlist) - 1:
                self.next_music()
            else:
                self.stop_music()

    def toggle_loop(self):
        self.loop = not self.loop
        self.loop_button.setText("Loop On" if self.loop else "Loop Off")

    def toggle_shuffle(self):
        self.shuffle = not self.shuffle
        self.shuffle_button.setText("Shuffle On" if self.shuffle else "Shuffle Off")

    def set_volume(self, value):
        pygame.mixer.music.set_volume(value / 100)

    def slider_pressed(self):
        self.music_playing_before_slider = self.music_playing
        self.music_playing = False
        pygame.mixer.music.pause()

    def slider_released(self):
        self.music_playing = self.music_playing_before_slider
        self.set_time(self.time_slider.value())

    def slider_moved(self, value):
        self.update_time_label(value)

    def set_time(self, value):
        total_time = self.get_total_time()
        if total_time > 0:
            new_time = total_time * (value / 100)
            pygame.mixer.music.play(start=new_time)
            self.music_playing = True
            self.paused = False
            self.pause_button.setText("Pause")
            if self.visualizer_active:
                self.visualizer.start(self.current_song, playing=True)
            self.update_time()

    def update_time(self):
        if self.music_playing and not self.paused:
            current_time = pygame.mixer.music.get_pos() / 1000
            total_time = self.get_total_time()
            remaining_time = total_time - current_time
            self.time_label.setText(f"{self.format_time(current_time)} / {self.format_time(total_time)} ({self.format_time(remaining_time)} left)")
            if total_time > 0 and not self.time_slider.isSliderDown():
                self.time_slider.setValue(int((current_time / total_time) * 100))

    def update_time_label(self, value):
        total_time = self.get_total_time()
        if total_time > 0:
            new_time = total_time * (value / 100)
            self.time_label.setText(f"{self.format_time(new_time)} / {self.format_time(total_time)}")

    def get_total_time(self):
        if self.current_song and os.path.exists(self.current_song):
            audio_info = sf.info(self.current_song)
            return audio_info.duration
        return 0

    def format_time(self, seconds):
        minutes = int(seconds // 60)
        seconds = int(seconds % 60)
        return f"{minutes:02}:{seconds:02}"
    
    def save_playlist(self):
        playlist_path, _ = QFileDialog.getSaveFileName(self, "Save Playlist", "", "Text files (*.txt)")
        if playlist_path:
            with open(playlist_path, "w", encoding="utf-8") as f:
                for song in self.playlist:
                    f.write(song + "\n")
            QMessageBox.information(self, "Thành công", "Đã lưu playlist!")

    def load_playlist(self):
        playlist_path = "playlist.txt"
        if os.path.exists(playlist_path):
            try:
                with open(playlist_path, "r", encoding="utf-8") as f:
                    self.playlist = [line.strip() for line in f.readlines() if os.path.exists(line.strip())]
            except UnicodeDecodeError:
                with open(playlist_path, "r", encoding="cp1252") as f:
                    self.playlist = [line.strip() for line in f.readlines() if os.path.exists(line.strip())]
            except Exception as e:
                print(f"Không thể đọc playlist.txt: {e}")
                return

            if self.playlist:
                self.current_index = 0
                self.current_song = self.playlist[self.current_index]
                self.song_label.setText(os.path.basename(self.current_song))
                self.update_playlist_box()

    def toggle_visualizer(self):
        if self.visualizer_active:
            self.visualizer.stop()
            self.visualizer_active = False
            self.toggle_visualizer_button.setText("Start Visualizer")
            self.adjust_window_size()
        else:
            if self.current_song:
                self.visualizer.start(self.current_song, playing=self.music_playing)
                self.visualizer_active = True
                self.toggle_visualizer_button.setText("Stop Visualizer")
                self.adjust_window_size()

    def switch_effect(self):
        if self.visualizer_active:
            self.visualizer.switch_effect()

    def adjust_window_size(self):
        if self.visualizer_active:
            self.resize(1200, 600)  # Mở rộng khi visualizer hiển thị
        else:
            self.resize(400, 600)  # Thu nhỏ khi visualizer ẩn
        self.central_widget.adjustSize()  # Điều chỉnh kích thước widget trung tâm

if __name__ == "__main__":
    app = QApplication(sys.argv)
    player = MusicPlayer()
    player.show()
    sys.exit(app.exec_())