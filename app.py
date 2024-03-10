from flask import Flask, abort, request, send_file
from tempfile import NamedTemporaryFile
import torch
from faster_whisper import WhisperModel
import time
import math
import ffmpeg
import pathlib

# Check if NVIDIA GPU is available
torch.cuda.is_available()
DEVICE = "cuda" if torch.cuda.is_available() else "cpu"

# Load the Whisper Model
model = WhisperModel("small", device=DEVICE)

# Utility Functions
def format_time(seconds):

    hours = math.floor(seconds / 3600)
    seconds %= 3600
    minutes = math.floor(seconds / 60)
    seconds %= 60
    milliseconds = round((seconds - math.floor(seconds)) * 1000)
    seconds = math.floor(seconds)
    formatted_time = f"{hours:02d}:{minutes:02d}:{seconds:01d},{milliseconds:03d}"

    return formatted_time

app = Flask(__name__)

@app.route("/")
def hello():
    return "Whisper Hello World!"

@app.route("/whisper", methods=[POST])
def handler():
    if not request.files:
        #If no file is submitted return a 400 (Bad Request)
        abort(400)

    # For each file, let's store the results in a list of dictionaries.
    results = []
        
    for filename, handle in request.files.items():
        # Create a temporary file.
        # The location of the temporary file is available in `temp.name`.
        temp = NamedTemporaryFile()
        temp2 = NamedTemporaryFile()
        # Write the user's uploaded file to the temporary file.
        # The file will get deleted when it drops out of scope.
        handle.save(temp)
        # We extract the audio in the file
        stream = ffmpeg.input(temp.name)
        stream = ffmpeg.output(stream, temp2.name)
        ffmpeg.run(stream, overwrite_output=True)
        # Let's get the transcript of the temporary file.
        segments, info = model.transcribe(temp2.name)


        language = info[0]
        segments = list(segments)

        subtitle_file = f"{filename}.{language}.srt"
        text = ""
        for index, segment in enumerate(segments):
            segment_start = format_time(segment.start)
            segment_end = format_time(segment.end)
            text += f"{str(index+1)} \n"
            text += f"{segment_start} --> {segment_end} \n"
            text += f"{segment.text} \n"
            text += "\n"
            
        f = open(subtitle_file, "w")
        f.write(text)
        f.close()

        return send_file(subtitle_file)

