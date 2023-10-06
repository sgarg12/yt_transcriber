from __future__ import unicode_literals
import yt_dlp
import os


def downloadVideo(url):
    output_path = str(os.path.join(os.getcwd(), "Downloads"))
    try:
        os.mkdir(output_path)
    except:
        print("dir exists")
    ydl_opts = {
    'format': 'bestaudio/best',
    'outtmpl': output_path + '/%(id)s.%(ext)s',
    'postprocessors': [{
        'key': 'FFmpegExtractAudio',
        'preferredcodec': 'wav',
        }],
    }
    with yt_dlp.YoutubeDL(ydl_opts) as ydl:
        info_dict = ydl.extract_info(url, download=True)
        return (str(os.path.join(output_path, info_dict.get("id", None))) + ".wav", info_dict.get('title', None))