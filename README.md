# Fast-Audioset-Download
Download audioset data super fastly with youtube-dl and Python Multiprocessing. This repo only downloads audio(dataset size issue)!! If you want to download as a video, Follow instructions [below](#down-as-video).

After the download, files will be stored under the 'wavs' folder. 

One can acquire each file's information(including url, stored path(relative), tags, labels interpreted from tags ...) by parsing the metadata json file. 

## Cookies.txt
Cookies are required to suppress the auth related warnings(+erros) of youtube-dl([reference](https://github.com/ytdl-org/youtube-dl/issues/31250))
You can download a cookies.txt by 
 1. Run firefox web browser on the desired machine(PC, or Server)
 2. Install [firefox extension](https://addons.mozilla.org/ko/firefox/addon/cookies-txt/)
 3. Go to [youtube](https://youtube.com)
 4. Make sure you are logged out(Creating cookie while logged in might cause severe instability to your youtube streaming elsewhere)
 5. Download cookie to desired location.
 6. Modify donwload.py specifying the path of your downloaded cookie file
## How to Use
 1. First download unbalanced_train_segments.csv from http://storage.googleapis.com/us_audioset/youtube_corpus/v1/csv/unbalanced_train_segments.csv
 2. Move the downloaded csv file under csvs folder
 3. Run download.py

```shell
foo@bar:/path/to/this/repo $ python download.py
```
** Resume supported(kind of) in case of crash or keyboard interrupt: Only acquire video meta-information(for creating final metadata.json) without downloading actual audio. 

## Required Packages
youtube-dl, tqdm, ffmpeg(*Allows partial youtube download)

## Downloading in a video(mp4) format<a name="down-as-video"></a>
youtube-dl and ffmpeg also support video downloading. Naturally, my repo can do that with a simple change in the code.

 1. Change the 'ext' global variable from m4a(default) to mp4 in the download.py
 2. Change the ydl_opts on the line 81 like below.
 ```python
ext = 'mp4'
...
    ydl_opts = {
                "logger": ytdl_logger,
                'cookiefile' : f'temps/id_{ids}/cookies.txt',
                'ignoreerrors': True,
                'outtmpl':"temps/id_%(id)s/audio.%(ext)s",
                'quiet' : True,
                'format': 'bestvideo[ext=mp4]+bestaudio[ext=m4a]/bestvideo+bestaudio',
                'postprocessor_args': ['-ar', str(sample_rate)],
                'external_downloader':'ffmpeg',
                'external_downloader_args':['-ss',st, '-to',dur, '-loglevel', 'quiet']
            }
...
 ```
