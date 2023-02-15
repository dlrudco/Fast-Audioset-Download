# Fast-Audioset-Download
Download audioset data super fastly with youtube-dl and Python Multiprocessing

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

```shell
foo@bar:/path/to/this/repo $ python download.py
```
** Resume supported(kind of) in case of crash or keyboard interrupt: Only acquire video meta-information(for creating final metadata.json) without downloading actual audio. 

## Required Packages
youtube-dl, tqdm, ffmpeg(*Allows partial youtube download)
