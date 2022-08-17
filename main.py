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



model_file_path = 'deepspeech-0.9.3-models.tflite'
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


if __name__ == "__main__":
    uvicorn.run(app, host="127.0.0.1", port=8000)