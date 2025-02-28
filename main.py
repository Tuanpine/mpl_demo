import tkinter as tk
from tkinter import filedialog
import pygame
import os
from visualizer import Visualizer

class MusicPlayer:
    def __init__(self, root):
        self.root = root
        self.root.title("Music Player")
        self.root.geometry("500x400")
        self.root.config(bg="lightblue")

        # Khởi tạo pygame mixer để phát nhạc
        pygame.mixer.init()
        self.current_song = None
        self.playlist = []
        self.current_index = 0
        self.visualizer = Visualizer()

        # Giao diện
        self.song_label = tk.Label(root, text="Chưa chọn bài hát", font=("Arial", 14), bg="lightblue")
        self.song_label.pack(pady=10)

        # Listbox để hiển thị danh sách bài hát
        self.playlist_box = tk.Listbox(root, selectmode=tk.SINGLE, font=("Arial", 12), bg="white", fg="black")
        self.playlist_box.pack(pady=10, fill=tk.BOTH, expand=True)
        self.playlist_box.bind('<<ListboxSelect>>', self.on_select)

        # Frame cho các nút điều khiển
        control_frame = tk.Frame(root, bg="lightblue")
        control_frame.pack(pady=20)

        # Nút điều khiển
        tk.Button(control_frame, text="Chọn nhạc", command=self.load_music, font=("Arial", 12), bg="white").grid(row=0, column=0, padx=10)
        tk.Button(control_frame, text="Play", command=self.play_music, font=("Arial", 12), bg="white").grid(row=0, column=1, padx=10)
        tk.Button(control_frame, text="Pause", command=self.pause_music, font=("Arial", 12), bg="white").grid(row=0, column=2, padx=10)
        tk.Button(control_frame, text="Stop", command=self.stop_music, font=("Arial", 12), bg="white").grid(row=0, column=3, padx=10)
        tk.Button(control_frame, text="Next", command=self.next_music, font=("Arial", 12), bg="white").grid(row=0, column=4, padx=10)
        tk.Button(control_frame, text="Previous", command=self.prev_music, font=("Arial", 12), bg="white").grid(row=0, column=5, padx=10)
        tk.Button(control_frame, text="Save Playlist", command=self.save_playlist, font=("Arial", 12), bg="white").grid(row=1, column=0, columnspan=6, pady=10)
        tk.Button(control_frame, text="Visualizer", command=self.start_visualizer, font=("Arial", 12), bg="white").grid(row=2, column=0, columnspan=6, pady=10)

        # Load playlist khi khởi động
        self.load_playlist()

    def load_music(self):
        # Mở file explorer để chọn file MP3
        files = filedialog.askopenfilenames(filetypes=[("MP3 Files", "*.mp3")])
        if files:
            self.playlist = list(files)
            self.current_index = 0
            self.current_song = self.playlist[self.current_index]
            self.song_label.config(text=os.path.basename(self.current_song))
            self.update_playlist_box()
            self.save_playlist()

    def update_playlist_box(self):
        self.playlist_box.delete(0, tk.END)
        for song in self.playlist:
            self.playlist_box.insert(tk.END, os.path.basename(song))

    def on_select(self, event):
        if self.playlist_box.curselection():
            self.current_index = self.playlist_box.curselection()[0]
            self.current_song = self.playlist[self.current_index]
            self.play_music()

    def play_music(self):
        if self.current_song:
            pygame.mixer.music.load(self.current_song)
            pygame.mixer.music.play()
            self.song_label.config(text=os.path.basename(self.current_song))

    def pause_music(self):
        pygame.mixer.music.pause()

    def stop_music(self):
        pygame.mixer.music.stop()
        self.song_label.config(text="Đã dừng")

    def next_music(self):
        if self.playlist and self.current_index < len(self.playlist) - 1:
            self.current_index += 1
            self.current_song = self.playlist[self.current_index]
            self.play_music()

    def prev_music(self):
        if self.playlist and self.current_index > 0:
            self.current_index -= 1
            self.current_song = self.playlist[self.current_index]
            self.play_music()

    def save_playlist(self):
        playlist_path = filedialog.asksaveasfilename(defaultextension=".txt", filetypes=[("Text files", "*.txt")])
        if playlist_path:
            with open(playlist_path, "w", encoding="utf-8") as f:
                for song in self.playlist:
                    f.write(song + "\n")
            tk.messagebox.showinfo("Thành công", "Đã lưu playlist!")

    def load_playlist(self):
        playlist_path = os.path.join(os.path.dirname(__file__), "playlist.txt")
        if os.path.exists(playlist_path):
            with open(playlist_path, "r") as f:
                self.playlist = [line.strip() for line in f.readlines()]
                if self.playlist:
                    self.current_index = 0
                    self.current_song = self.playlist[self.current_index]
                    self.song_label.config(text=os.path.basename(self.current_song))
                    self.update_playlist_box()

    def start_visualizer(self):
        self.visualizer.start()

# Khởi chạy ứng dụng
if __name__ == "__main__":
    root = tk.Tk()
    app = MusicPlayer(root)
    root.mainloop()