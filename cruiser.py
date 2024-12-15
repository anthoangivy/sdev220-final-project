import os
import pygame
import tkinter as tk
from mutagen.mp3 import MP3
from tkinter import filedialog, messagebox, ttk

class Song:
    def __init__(self, name, path):
        self.name = name
        self.path = path

    def __str__(self):
        return self.name

class Playlist:
    def __init__(self):
        self.songs = []

    def add_song(self, song):
        if song not in self.songs:
            self.songs.append(song)
            return True
        
        return False

    def remove_song(self, song):
        if song in self.songs:
            self.songs.remove(song)
            return True
        
        return False

    def up(self, count):
        if count > 0 and count < len(self.songs):
            self.songs[count], self.songs[count - 1] = self.songs[count - 1], self.songs[count]
            return True
        
        return False

    def down(self, count):
        if count < len(self.songs) - 1:
            self.songs[count], self.songs[count + 1] = self.songs[count + 1], self.songs[count]
            return True
        
        return False

class Player:
    def __init__(self, root):
        self.root = root
        self.root.title("Cruiser")
        self.root.geometry("600x450")
        self.root.resizable(width=False, height=False)

        pygame.mixer.init()

        self.songs = []
        self.playlist = Playlist()
        self.current_song = None
        self.paused = False
        self.directory = ""

        self.song_length = 0

        self.ui()

    def ui(self):
        menubar = tk.Menu(self.root)
        self.root.config(menu=menubar)

        open_menu = tk.Menu(menubar, tearoff=False)
        open_menu.add_command(label="Open...", command=self.loader)
        open_menu.add_command(label="Save Playlist", command=self.save_playlist)
        menubar.add_cascade(label="File", menu=open_menu)

        playlist_menu = tk.Menu(menubar, tearoff=False)
        playlist_menu.add_command(label="View Playlist", command=self.view_playlist)
        menubar.add_cascade(label="Edit", menu=playlist_menu)

        self.songlist = tk.Listbox(self.root, bg="black", fg="white", width=100, height=15)
        self.songlist.pack()
        self.songlist.bind("<ButtonRelease-1>", self.click)

        control_frame = tk.Frame(self.root)
        control_frame.pack()

        play_btn = tk.Button(control_frame, text="Play", command=self.player)
        pause_btn = tk.Button(control_frame, text="Pause", command=self.stopper)
        next_btn = tk.Button(control_frame, text="Next", command=self.skipper)
        prev_btn = tk.Button(control_frame, text="Previous", command=self.backer)

        play_btn.grid(row=0, column=1, padx=7, pady=10)
        pause_btn.grid(row=0, column=0, padx=7, pady=10)
        next_btn.grid(row=0, column=3, padx=7, pady=10)
        prev_btn.grid(row=0, column=2, padx=7, pady=10)

        self.up_btn = tk.Button(control_frame, text="Move Up", command=self.up)
        self.down_btn = tk.Button(control_frame, text="Move Down", command=self.down)
        self.add_btn = tk.Button(control_frame, text="Add to Playlist", command=self.add)
        self.remove_btn = tk.Button(control_frame, text="Remove from Playlist", command=self.remove)
        self.back_btn = tk.Button(control_frame, text="Back", command=self.back_to_main)

        self.up_btn.grid(row=1, column=0, padx=7, pady=10)
        self.down_btn.grid(row=1, column=1, padx=7, pady=10)
        self.add_btn.grid(row=1, column=2, padx=7, pady=10)
        self.remove_btn.grid(row=1, column=3, padx=7, pady=10)
        self.back_btn.grid_forget()

        control_frame.grid_columnconfigure(0, weight=1)
        control_frame.grid_columnconfigure(1, weight=1)
        control_frame.grid_columnconfigure(2, weight=1)
        control_frame.grid_columnconfigure(3, weight=1)

        self.progress = ttk.Progressbar(self.root, orient="horizontal", length=500, mode="determinate")
        self.progress.pack(pady=10)

    def loader(self):
        self.directory = filedialog.askdirectory()

        if self.directory:
            self.songs.clear()
            self.songlist.delete(0, tk.END)

            for song in os.listdir(self.directory):
                name, ext = os.path.splitext(song)
                if ext == ".mp3":
                    song_path = os.path.join(self.directory, song)
                    new_song = Song(name, song_path)
                    self.songs.append(new_song)

            for song in self.songs:
                self.songlist.insert("end", str(song))

            self.songlist.selection_set(0)
            self.current_song = self.songs[self.songlist.curselection()[0]]

    def player(self):
        if not self.paused and self.current_song:
            pygame.mixer.music.load(self.current_song.path)
            pygame.mixer.music.play()
            audio = MP3(self.current_song.path)
            self.song_length = audio.info.length
            self.update_progress_bar()

        elif self.paused:
            pygame.mixer.music.unpause()
            self.paused = False
            self.update_progress_bar()

    def stopper(self):
        if pygame.mixer.music.get_busy():
            pygame.mixer.music.pause()
            self.paused = True

    def skipper(self):
        self.change_song(1)

    def backer(self):
        self.change_song(-1)

    def change_song(self, step):
        try:
            current_list = self.playlist.songs if self.current_song in self.playlist.songs else self.songs
            index = current_list.index(self.current_song) + step
            self.songlist.selection_clear(0, tk.END)
            self.songlist.selection_set(index)
            self.current_song = current_list[index]
            self.player()

        except (IndexError, ValueError):
            pass

    def click(self, event):
        index = self.songlist.curselection()
        if index:
            if self.songlist.size() == len(self.songs):
                self.current_song = self.songs[index[0]]

            else:
                self.current_song = self.playlist.songs[index[0]]
            self.player()

    def update_progress_bar(self):
        if pygame.mixer.music.get_busy():
            current_pos = pygame.mixer.music.get_pos() / 1000
            self.progress["value"] = (current_pos / self.song_length) * 100
            if current_pos < self.song_length:
                self.root.after(500, self.update_progress_bar)

            else:
                self.progress["value"] = 0

    def save_playlist(self):
        if not self.playlist.songs:
            messagebox.showinfo("Playlist", "No songs to save in playlist.")
            return

        file_path = os.path.join(os.path.dirname(__file__), "playlist.txt")
        with open(file_path, "w") as file:
            for song in self.playlist.songs:
                file.write(f"{song.name}\n")

        messagebox.showinfo("Playlist Saved", f"Playlist saved to {file_path}")

    def add(self):
        song = self.current_song
        if song and self.playlist.add_song(song):
            messagebox.showinfo("Playlist", f"{song.name} added to playlist.")

    def remove(self):
        song = self.current_song
        if song and self.playlist.remove_song(song):
            messagebox.showinfo("Playlist", f"{song.name} removed from playlist.")
            self.view_playlist()

    def view_playlist(self):
        if self.playlist.songs:
            self.songlist.delete(0, tk.END)
            for song in self.playlist.songs:
                self.songlist.insert("end", str(song))

            self.up_btn.grid(row=1, column=0, padx=7, pady=10)
            self.down_btn.grid(row=1, column=1, padx=7, pady=10)
            self.add_btn.grid(row=1, column=2, padx=7, pady=10)
            self.remove_btn.grid(row=1, column=3, padx=7, pady=10)
            self.back_btn.grid(row=2, column=0, columnspan=4, padx=7, pady=10)
            
        else:
            messagebox.showinfo("Playlist", "No songs in playlist.")

    def up(self):
        index = self.songlist.curselection()
        if index and index[0] > 0:
            self.playlist.up(index[0])
            self.view_playlist()

    def down(self):
        index = self.songlist.curselection()
        if index:
            self.playlist.down(index[0])
            self.view_playlist()

    def back_to_main(self):
        self.songlist.delete(0, tk.END)
        for song in self.songs:
            self.songlist.insert("end", str(song))

        self.up_btn.grid(row=1, column=0, padx=7, pady=10)
        self.down_btn.grid(row=1, column=1, padx=7, pady=10)
        self.add_btn.grid(row=1, column=2, padx=7, pady=10)
        self.remove_btn.grid(row=1, column=3, padx=7, pady=10)
        self.back_btn.grid_forget()

if __name__ == "__main__":
    root = tk.Tk()
    app = Player(root)
    root.mainloop()