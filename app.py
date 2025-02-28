import sys
from PyQt5.QtWidgets import QApplication
from music_player import MusicPlayer

# Khởi chạy ứng dụng
if __name__ == "__main__":
    app = QApplication(sys.argv)
    player = MusicPlayer()
    player.show()
    sys.exit(app.exec_())