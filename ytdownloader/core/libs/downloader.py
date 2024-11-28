import yt_dlp as yt

class Downloader:


    @staticmethod
    def download_video(opts: dict, url: str) -> None:
        with yt.YoutubeDL(opts) as ydl:
            ydl.download([url])