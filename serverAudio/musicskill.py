from ytmusicapi import YTMusic
from pychromecast import get_chromecasts
from pychromecast.controllers.youtube import YouTubeController
import json
from charactercontroller import CharacterController

class MusicSkill(CharacterController):
    def __init__(self, connection, global_timer, google_key, callback, terms, client_id, secret, redirect):
        super().__init__(connection, global_timer, google_key, callback, terms)
        self.yt_music = YTMusic()

    def listen(self, heard):
        if "play" in heard:
            device = self.find_device()
            if device == -1:
                self.talk("no_device.wav")
            else:
                the_song = self.find_song(heard.split("play", 1)[1].strip())
                if the_song[0] == -1:
                    if the_song[1] != "":
                        self.talk(the_song[1])
                else:
                    self.synthesize_text(the_song[1])
                    self.talk("latest_output.wav")
                    try:
                        self.send_command('dab')
                        self.play_song(the_song[2]["videoId"])
                    except:
                        self.talk("backup_song.wav")
        else:
            self.pause_playback()

    def play_song(self, video_id):
        device = self.find_device()
        if device == -1:
            print("error with device")
            self.talk("connect_device.wav")
        else:
            youtube_controller = YouTubeController()
            device.register_handler(youtube_controller)
            youtube_controller.play_video(video_id)

    def pause_playback(self):
        device = self.find_device()
        if device == -1:
            print("error with device")
            self.talk("connect_device.wav")
        else:
            try:
                self.talk("stop_song.wav")
                self.yt_music.pause_playback()
            except:
                print("error attempting to pause")
                self.talk("connect_device.wav")

    def find_song(self, heard):
        loc_attempt = heard.find(" as by ")
        search_query = heard
        if loc_attempt > -1:
            song_info = heard.split(" as by ")
            search_query = song_info[0] + " " + song_info[1]
        if search_query != "":
            song_results = self.yt_music.search(query=search_query, limit=1)
            try:
                song_res = song_results[0]
                result = {"artist": "", "song": "", "videoId": ""}
                artist = song_res["artist"]
                result["videoId"] = song_res["videoId"]
                result["song"] = song_res["title"]
                result["artist"] = artist
                return (1, ("Okay! I'll play %s by %s!" % (result["song"], result["artist"])), result)
            except:
                return (-1, "no_find_song.wav")
        else:
            return (-1, "")

    def find_device(self):
        chromecasts = get_chromecasts()
        if chromecasts:
            cast = chromecasts[0]
            cast.wait()
            return cast
        else:
            return -1
