import numpy as np
import soundfile as sf
import logging
from PyQt5.QtWidgets import QWidget
from PyQt5.QtGui import QPainter, QColor, QPen, QImage
from PyQt5.QtCore import Qt, QTimer
import pygame

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger("Visualizer")

class Visualizer(QWidget):
    def __init__(self, parent=None):
        super().__init__(parent)
        self.setMinimumSize(800, 600)
        self.current_song = None
        self.audio_data = None
        self.sample_rate = None
        self.music_playing = False
        self.timer = QTimer(self)
        self.timer.timeout.connect(self.update_visualizer)
        self.wave_offset = 0
        self.play_icon = QImage("player/icons/play.png")
        self.hide()  # Ẩn visualizer khi khởi tạo
        self.effect_index = 0  # Chỉ số hiệu ứng hiện tại

    def load_audio(self, song_path):
        try:
            self.current_song = song_path
            self.audio_data, self.sample_rate = sf.read(song_path)
            logger.info(f"Loaded audio: {song_path}, samples: {len(self.audio_data)}, rate: {self.sample_rate}")
        except Exception as e:
            logger.error(f"Error loading audio {song_path}: {e}")
            self.audio_data = None
            self.sample_rate = None

    def paintEvent(self, event):
        painter = QPainter(self)
        painter.setRenderHint(QPainter.Antialiasing)
        painter.fillRect(self.rect(), Qt.black)

        if self.audio_data is not None and self.music_playing and pygame.mixer.music.get_busy():
            pos = pygame.mixer.music.get_pos() / 1000
            sample_pos = int(pos * self.sample_rate)
            chunk_size = 4096
            start = max(0, sample_pos)
            end = min(len(self.audio_data), start + chunk_size)
            chunk = self.audio_data[start:end]

            if len(chunk) > 0:
                if len(chunk.shape) > 1:
                    chunk = np.mean(chunk, axis=1)

                fft_data = np.abs(np.fft.fft(chunk))[:chunk_size // 2]
                max_amplitude = np.max(fft_data) if np.max(fft_data) > 0 else 1
                fft_data = fft_data / max_amplitude * (self.height() / 2)  # Giảm biên độ

                if self.effect_index == 0:
                    self.effect_waveform(painter, fft_data)
                elif self.effect_index == 1:
                    self.effect_bars(painter, fft_data)
                elif self.effect_index == 2:
                    self.effect_circles(painter, fft_data)

    def effect_waveform(self, painter, fft_data):
        num_points = self.width()
        step = max(1, len(fft_data) // num_points)
        scaled_fft = fft_data[::step][:num_points]

        center_y = self.height() // 2
        for depth in range(3):
            points = []
            offset_y = depth * 20
            for i, amplitude in enumerate(scaled_fft):
                x = int(i * (self.width() / len(scaled_fft)))
                y = center_y - int(amplitude * (1 - depth * 0.2)) + int(20 * np.sin((x + self.wave_offset + depth * 50) / 50))
                points.append((x, y))

            if len(points) > 1:
                pen = QPen()
                pen.setWidth(2)
                for i in range(len(points) - 1):
                    x1, y1 = points[i]
                    x2, y2 = points[i + 1]
                    r = int(100 + depth * 50)
                    g = int(150 - depth * 50)
                    b = int(255 - depth * 50)
                    pen.setColor(QColor(r, g, b))
                    painter.setPen(pen)
                    painter.drawLine(x1, y1, x2, y2)
        self.wave_offset += 5

    def effect_bars(self, painter, fft_data):
        num_bars = self.width() // 10
        step = max(1, len(fft_data) // num_bars)
        scaled_fft = fft_data[::step][:num_bars]

        for i, amplitude in enumerate(scaled_fft):
            x = i * 10
            y = self.height() - int(amplitude)
            painter.setBrush(QColor(100 + i * 5, 150 - i * 5, 255 - i * 5))
            painter.drawRect(x, y, 8, int(amplitude))

    def effect_circles(self, painter, fft_data):
        num_circles = self.width() // 20
        step = max(1, len(fft_data) // num_circles)
        scaled_fft = fft_data[::step][:num_circles]

        center_x = self.width() // 2
        center_y = self.height() // 2
        for i, amplitude in enumerate(scaled_fft):
            radius = int(amplitude)
            painter.setBrush(QColor(100 + i * 5, 150 - i * 5, 255 - i * 5))
            painter.drawEllipse(center_x - radius, center_y - radius, radius * 2, radius * 2)

    def update_visualizer(self):
        self.update()

    def start(self, song_path=None, playing=False):
        if song_path:
            self.load_audio(song_path)
        self.music_playing = playing
        self.show()  # Hiển thị visualizer
        self.timer.start(30)

    def stop(self):
        self.music_playing = False
        self.timer.stop()
        self.hide()  # Ẩn visualizer

    def switch_effect(self):
        self.effect_index = (self.effect_index + 1) % 3  # Chuyển đổi giữa 3 hiệu ứng