import os
import shutil
from tqdm import tqdm
import parmap
import youtube_dl
import logging
from io import StringIO
# import pandas as pd
from multiprocessing import Manager
import time
import json

split = None
ext = 'm4a'
def remove_non_ascii(string):
    return string.encode('ascii', errors='ignore').decode()

def download_audio(video_info, metadata):
    try:
        video_info = video_info.replace(' ', '').split(',')
        to = float((video_info[2]))
        start = float(video_info[1])
    except IndexError:
        print(video_info)
    st = f'{int(start//3600)}:{int(start//60)-60*int(start//3600)}:{start%60}'
    dur = f'{int(to//3600)}:{int(to//60)-60*int(to//3600)}:{to%60}'
    ids = video_info[0]
    categories = [c.replace('"','') for c in video_info[3:]]

    ytdl_logger = logging.getLogger()
    log_stream = StringIO()    
    logging.basicConfig(stream=log_stream, level=logging.INFO)
    
    ydl_opts = {
        "logger": ytdl_logger,
        'cookiefile' : f'temps/id_{ids}.txt',
        'ignoreerrors': True,
        'outtmpl':"temps/id_%(id)s.%(ext)s",
        'quiet' : True,
        'format': 'bestaudio/best',
        'postprocessors': [{
            'key': 'FFmpegExtractAudio',
            'preferredcodec': ext
        }],
        'postprocessor_args': ['-ar', '16000'],
        'external_downloader':'ffmpeg',
        'external_downloader_args':['-ss',st, '-to',dur, '-loglevel', 'quiet']
    }
    url = f'https://www.youtube.com/watch?v={ids}'
    count = 0
    while count < 5:
        shutil.copy('/home/ncl/Downloads/cookies.txt', f'temps/id_{ids}.txt')
        try:
            with youtube_dl.YoutubeDL(ydl_opts) as ydl:
                file_exist = os.path.isfile(os.path.join('wavs', split, f'id_{ids}.{ext}'))
                info=ydl.extract_info(url, download=not file_exist)
                filename = f'id_{info["id"]}.{ext}'   
                if not file_exist:
                    shutil.move(os.path.join('temps',filename), os.path.join('wavs', split, filename))
                else:
                    pass
                metadata[filename] = {'title': info['title'], 'url':url, 'tags': categories, 'labels': [tag2name[c] for c in categories]}
                os.remove(f'temps/id_{ids}.txt')
            return None
        except FileNotFoundError:
            count += 1
            time.sleep(1)
            if count == 5:
                print('Hello')
                os.remove(f'temps/id_{ids}.txt')
                return f'{url} - ytdl : {log_stream.getvalue()}, system : Retry failed. Try manual download.'
        except Exception as e:
            os.remove(f'temps/id_{ids}.txt')
            return f'{url} - ytdl : {log_stream.getvalue()}, system : {str(e)}'
    

# vid_list = pd.read_csv('balanced_train_segments.csv', sep=',', header = 3)
if __name__ == "__main__":
    os.system('rm -rf temps')
    os.makedirs('temps', exist_ok=True)
    indices = open('csvs/class_labels_indices.csv').readlines()[1:]
    labels = list(map(lambda x: x.split(',')[0], indices))
    tags = list(map(lambda x: x.split(',')[1], indices))
    names = list(map(lambda x: '_'.join(x.replace('"','').replace('\n','').replace(' ','_').replace('-','_').replace('(','').replace(')','').replace('.','').replace("'",'').split(',')[2:]),indices))
    names = [n.replace('__','_') for n in names]
    tag2name = {t:l for t,l in zip(tags, names)}

    manager = Manager()
    metadata = {}

    split = 'eval'
    os.makedirs(os.path.join('wavs', split), exist_ok=True)
    file = open('csvs/eval_segments.csv', 'r').read()
    rows = file.split('\n')[3:-1]
    eval_metadata = manager.dict()
    logs = parmap.map(download_audio, rows, eval_metadata, pm_pbar=True, pm_processes=64, pm_chunksize=2)
    logs = [l for l in logs if l is not None]
    open('download_eval_logs.txt','w').write('\n'.join(logs))
    metadata['eval'] = dict(eval_metadata)
    json.dump(metadata['eval'], open('audioset_eval_metadata.json','w'))
    print('Eval Download Done')

    split = 'balanced'
    os.makedirs(os.path.join('wavs', split), exist_ok=True)
    file = open('csvs/balanced_train_segments.csv', 'r').read()
    rows = file.split('\n')[3:-1]
    balance_metadata = manager.dict()
    logs = parmap.map(download_audio, rows, balance_metadata, pm_pbar=True, pm_processes=64, pm_chunksize=2)
    logs = [l for l in logs if l is not None]
    open('download_train-bal_logs.txt','w').write('\n'.join(logs))
    metadata['balanced_train'] = dict(balance_metadata)
    json.dump(metadata['balanced_train'], open('audioset_balanced_metadata.json','w'))
    print('Train-Balanced Download Done')

    split = 'unbalanced'
    os.makedirs(os.path.join('wavs', split), exist_ok=True)
    file = open('csvs/unbalanced_train_segments.csv', 'r').read()
    rows = file.split('\n')[3:-1]
    unbalance_metadata = manager.dict()
    logs = parmap.map(download_audio, rows, unbalance_metadata, pm_pbar=True, pm_processes=64, pm_chunksize=2)
    logs = [l for l in logs if l is not None]
    open('download_train-unbal_logs.txt','w').write('\n'.join(logs))
    metadata['unbalanced_train'] = dict(unbalance_metadata)
    json.dump(metadata['unbalanced_train'], open('audioset_balanced_metadata.json','w'))
    print('Train-Unbalanced Download Done')

    
    json.dump(metadata, open('audioset_metadata.json','w'))
    breakpoint()

