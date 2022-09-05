import datetime
import uvicorn
from deepspeech import Model
import numpy as np
import os
import wave
import json
import subprocess
import shutil
import scipy
from fastapi import FastAPI, File, UploadFile
from fastapi.responses import JSONResponse
from os.path import exists
import srt
from youtube_transcript_api import YouTubeTranscriptApi, TranscriptsDisabled
from youtube_transcript_api import YouTubeTranscriptApi
from youtube_transcript_api._errors import TranscriptsDisabled
from fastapi import FastAPI, Depends, HTTPException,  Request
from fastapi.responses import JSONResponse
from fastapi.exceptions import RequestValidationError
from fastapi.responses import PlainTextResponse
import shutil
from fastapi import FastAPI, File, UploadFile
import uvicorn
import time

class UnicornException(Exception):
    def __init__(self, name: str):
        self.name = name


app = FastAPI()

@app.post("/files/" , tags=['rename the file to "video.mp4" before uploading'])
async def create_file(file: UploadFile = File(...)):
    if not file:
        return {"message": "No file sent"}
    else:
        with open(f'{file.filename}',"wb") as buffer:
            shutil.copyfileobj(file.file, buffer)
        return {"filename": file.filename}



model_file_path = 'deepspeech-0.9.3-models.pbmm'
lm_file_path = 'deepspeech-0.9.3-models.scorer' 


list =[]

@app.post("/deepspeechsrt/")
async def main():
    command = f"python3 autosub/main.py --model {model_file_path} --scorer {lm_file_path} --file video.mp4 --format srt"
    
    ret = subprocess.call(command, shell=True)
    mysrt =""

    with open("output/video.srt", 'r') as srtfile :
        for line in srtfile:
            Remove_last = line[:-1]
            list.append(Remove_last)
            # list.append(line)
    # for x in list:
        # mysrt += ' ' +x
    return list
if os.path.exists('output/video.srt'):
    os.remove("output/video.srt")




def convertTime(seconds):
    return time.strftime("%H:%M:%S",time.gmtime(seconds))

@app.exception_handler(UnicornException)
async def unicorn_exception_handler(request: Request, exc: UnicornException):
    return JSONResponse(
        status_code=418,
        content={"message": f"Oops! {exc.name} did something. There goes a rainbow..."},
    )

@app.get("/srtgenerator/{url}")
async def srt_gen(url):     
    try:
        sub = YouTubeTranscriptApi.get_transcript(url)
        print(f"subtitles are available for {url}")
        
        sub_frames = []
        for i, s in enumerate(sub):
            sub_frames.append(srt.Subtitle(
                index=i+1,
                start=datetime.timedelta(s['start']),
                end=datetime.timedelta(s['start']+s['duration']),
                content=s['text']
            ))
        sub_srt = srt.compose(sub_frames)
        
        with open("output_path.txt", "w") as sub_file:
            sub_file.write(sub_srt)
            
    except TranscriptsDisabled:
        print(f"subtitles are missing for {url}")
        # continue


if __name__ == "__main__":
    uvicorn.run(app, host="127.0.0.1", port=8000)