import os
import datetime
import json
import srt
from youtube_transcript_api import YouTubeTranscriptApi, TranscriptsDisabled
from pytube import YouTube
from deepspeech import Model
import subprocess
from fastapi import FastAPI, UploadFile, File
import shutil

app = FastAPI()

output_base_path = './output_files/'
youtube_audio_path = './youtube_audios/'
audio_paths = 'youtube_audios/'

model_file_path = 'deepspeech-0.9.3-models.pbmm'
lm_file_path = 'deepspeech-0.9.3-models.scorer' 

def download_audio(video_id:str):
    url = "https://www.youtube.com/watch?v="+video_id
    yt = YouTube(url)
    video = yt.streams.filter(only_audio=True).first()

    out_file = video.download(output_path=youtube_audio_path)

    base, ext = os.path.splitext(out_file)
    print(base)
    print(ext)
    new_file = video_id + '.mp3'
    os.rename(out_file, youtube_audio_path+new_file)


def get_srt_from_audio(audio_paths: str, video_id: str):
    path_fileName = audio_paths + video_id + '.mp3'
    command = f'python3 autosub/main.py --model {model_file_path} --scorer {lm_file_path} --file {path_fileName} --format srt'
    os.system(command)

    output_path = './output/'+video_id+'.srt'
    lines = list()

    # Now read the file
    with open(output_path) as f:
        lines = f.read()

    return lines

def get_srt_from_file(path: str, fileName: str):
    path_fileName = f'{path}{fileName}'
    command = f'python3 autosub/main.py --model {model_file_path} --scorer {lm_file_path} --file {path_fileName} --format srt'
    os.system(command)

    file_name = fileName[:-4]
    output_path = './output/'+file_name+'.srt'
    lines = list()

    # Now read the file
    with open(output_path) as f:
        lines = f.read().splitlines()

    return lines


def process(video_id:str):

    lines = list()

    try:
        sub = YouTubeTranscriptApi.get_transcript(video_id)
        print(f"subtitles are available for {video_id}")

        sub_frames = []
        for i, s in enumerate(sub):
            sub_frames.append(srt.Subtitle(
                index=i + 1,
                start=datetime.timedelta(s['start']),
                end=datetime.timedelta(s['start'] + s['duration']),
                content=s['text']
            ))
        lines = srt.compose(sub_frames)

        # output_path = output_base_path+video_id
        # with open(output_path, "w") as sub_file:
        #     sub_file.write(sub_srt)

    except TranscriptsDisabled:
        print(f"subtitles are missing for {video_id}")
        download_audio(video_id)
        print("Downloaded audio for the given video ID.")
        lines = get_srt_from_audio(audio_paths, video_id)
        print("Download the SRT too.")

    return lines


@app.get("/srtgenerator/{video_id}")
async def srt_gen(video_id):
    return process(video_id)

@app.post("/externalfile/", tags=['Currently we support .mp3 and .mp4 files with english audio language.'])
async def external_file(file: UploadFile = File(...)):
    with open(f'{audio_paths}{file.filename}', "wb") as buffer:
        shutil.copyfileobj(file.file, buffer)

    return get_srt_from_file(audio_paths, file.filename)
