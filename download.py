import os
import shutil
from tqdm import tqdm
from multiprocessing import Pool
import youtube_dl
import logging
from io import StringIO
# import pandas as pd
from multiprocessing import Manager
import time
import json
import glob

from functools import partial

ext = 'm4a'
sample_rate=16000
files_per_folder = 50
num_processes = os.cpu_count()
cookie_path = '/home/ncl/Downloads/cookies.txt'

indices = open('csvs/class_labels_indices.csv').readlines()[1:]
labels = list(map(lambda x: x.split(',')[0], indices))
tags = list(map(lambda x: x.split(',')[1], indices))
names = list(map(lambda x: '_'.join(x.replace('"','').replace('\n','').replace(' ','_').replace('-','_').replace('(','').replace(')','').replace('.','').replace("'",'').split(',')[2:]),indices))
names = [n.replace('__','_') for n in names]
tag2name = {t:l for t,l in zip(tags, names)}

split = None

def remove_non_ascii(string):
    return string.encode('ascii', errors='ignore').decode()

def clear_intermediate_json(split):
    files =  glob.glob(f"{os.path.join(os.path.abspath('.'),'wavs', split)}/**/*.json", recursive=True)
    p = Pool(num_processes)
    with tqdm(total=len(files),leave=False) as pbar:
        for _ in p.imap_unordered(os.remove, files):
            pbar.update()
    p.close()
    p.join()
             
def merge_all_json(split):
    files =  glob.glob(f"{os.path.join(os.path.abspath('.'),'wavs', split)}/**/*.json", recursive=True)
    manager = Manger()
    def assign(file, meta):
        info = json.load(open(file))
        meta[info['id']] = info
    metadata = manager.dict()
    assign_meta = partial(assign, meta=metadata)
    p = Pool(num_processes)
    with tqdm(total=len(files),leave=False) as pbar:
        for _ in p.imap_unordered(assign_meta, files):
            pbar.update()
    p.close()
    p.join()
    return dict(metadata)
        
def download_audio(video_info, split):
    try:
        file_idx, video_info = video_info
        subfolder_idx = f'{file_idx // files_per_folder:06}'
        video_info = video_info.replace(' ', '').split(',')
        to = float((video_info[2]))
        start = float(video_info[1])
    except IndexError:
        print(video_info)
        
    st = f'{int(start//3600)}:{int(start//60)-60*int(start//3600)}:{start%60}'
    dur = f'{int(to//3600)}:{int(to//60)-60*int(to//3600)}:{to%60}'
    ids = video_info[0]
    categories = [c.replace('"','') for c in video_info[3:]]
    outpath = os.path.join('wavs',split,subfolder_idx)
    os.makedirs(outpath, exist_ok=True)
    if os.path.isfile(os.path.join(outpath, f'id_{ids}.json')):
        pass
    else:
        ytdl_logger = logging.getLogger()
        log_stream = StringIO()    
        logging.basicConfig(stream=log_stream, level=logging.INFO)
        
        ydl_opts = {
            "logger": ytdl_logger,
            'cookiefile' : f'temps/id_{ids}/cookies.txt',
            'ignoreerrors': True,
            'outtmpl':"temps/id_%(id)s/audio.%(ext)s",
            'quiet' : True,
            'format': 'bestaudio/best',
            'postprocessors': [{
                'key': 'FFmpegExtractAudio',
                'preferredcodec': ext
            }],
            'postprocessor_args': ['-ar', str(sample_rate)],
            'external_downloader':'ffmpeg',
            'external_downloader_args':['-ss',st, '-to',dur, '-loglevel', 'quiet']
        }
        url = f'https://www.youtube.com/watch?v={ids}'
        os.makedirs(f'temps/id_{ids}')
        shutil.copy(cookie_path, f'temps/id_{ids}/cookies.txt')
        try:
            with youtube_dl.YoutubeDL(ydl_opts) as ydl:
                file_exist = os.path.isfile(os.path.join(outpath, f'id_{ids}.{ext}'))
                info=ydl.extract_info(url, download=not file_exist)
                filename = f'id_{ids}.{ext}'
                jsonname = f'id_{ids}.json'
                if not file_exist:
                    shutil.move(os.path.join(f'temps/id_{ids}','audio.m4a'), os.path.join(outpath, filename))
                else:
                    pass
                file_meta = {'id':f'id_{ids}','path': os.path.join(outpath, filename),'title': info['title'], 'url':url, 'tags': categories, 'labels':[tag2name[c] for c in categories]}
                json.dump(file_meta, open(os.path.join(outpath, jsonname),'w'))
                shutil.rmtree(f'temps/id_{ids}')
        except Exception as e:
            shutil.rmtree(f'temps/id_{ids}')
            return f'{url} - ytdl : {log_stream.getvalue()}, system : {str(e)}'
    return None

# vid_list = pd.read_csv('balanced_train_segments.csv', sep=',', header = 3)

def download_audioset_split(split):
    filename = f'audioset_{split}_metadata.json'
    if os.path.isfile(filename):
        metadata = json.load(open(filename))
    else:
        os.makedirs(os.path.join('wavs', split), exist_ok=True)
        file = open(f'csvs/{split}_segments.csv', 'r').read()
        rows = file.split('\n')[3:1003]#for debug
        # logs = parmap.map(download_audio, rows, pm_pbar={'leave':False}, pm_processes=num_processes*2, pm_chunksize=10)
        logs = []
        p = Pool(num_processes*2)
        download_audio_split = partial(download_audio, split=split)
        with tqdm(total=len(rows),leave=False) as pbar:
            for log in p.imap_unordered(download_audio_split, enumerate(rows)):
                logs.append(log)
                pbar.update()
        p.close()
        p.join()
        logs = [l for l in logs if l is not None]
        open(f'download_{split}_logs.txt','w').write('\n'.join(logs))
        metadata = merge_all_json(split)
        json.dump(metadata, open(filename,'w'))
        clear_intermediate_json(split)
    return metadata
    
if __name__ == "__main__":
    try:
        shutil.rmtree('temps')
    except FileNotFoundError:
        pass
    os.makedirs('temps', exist_ok=True)

    metadata = {}

    splits = ['eval', 'balanced_train', 'unbalanced_train']
    for split in splits:
        metadata[split] = download_audioset_split(split)
        print(f'{split.upper()} Download Done')
    
    json.dump(metadata, open('audioset_metadata.json','w'))
    breakpoint()

