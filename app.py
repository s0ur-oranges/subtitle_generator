# -*- coding: utf-8 -*-

# !apt install imagemagick

# !cat /etc/ImageMagick-6/policy.xml | sed 's/none/read,write/g'> /etc/ImageMagick-6/policy.xml

# Place files in this path or modify the paths to point to where the files are
srtfilename = "subtitles.txt"
mp4filename = "video.mp4"

import sys
import pysrt
import os
import subprocess
from moviepy.editor import VideoFileClip, TextClip, CompositeVideoClip
import streamlit as st
from faster_whisper import WhisperModel
import time

filename="videofile"
def save_uploadedfile(uploadedfile):
     with open(filename,"wb") as f:
         f.write(uploadedfile.getbuffer())

def time_to_seconds(time_obj):
    return time_obj.hours * 3600 + time_obj.minutes * 60 + time_obj.seconds + time_obj.milliseconds / 1000


def create_subtitle_clips(subtitles, videosize,fontsize=24, font='Arial', color='yellow', debug = False):
    subtitle_clips = []

    for subtitle in subtitles:
        start_time = time_to_seconds(subtitle.start)
        end_time = time_to_seconds(subtitle.end)
        duration = end_time - start_time

        video_width, video_height = videosize

        text_clip = TextClip(subtitle.text, fontsize=fontsize, font=font, color=color, bg_color = 'black',size=(video_width*3/4, None), method='caption').set_start(start_time).set_duration(duration)
        subtitle_x_position = 'center'
        subtitle_y_position = video_height* 4 / 5

        text_position = (subtitle_x_position, subtitle_y_position)
        subtitle_clips.append(text_clip.set_position(text_position))

    return subtitle_clips

def video2mp3(video_file, output_ext="mp3"):
    filename, ext = os.path.splitext(video_file)
    subprocess.call(["ffmpeg", "-y", "-i", video_file, f"{filename}.{output_ext}"], 
                    stdout=subprocess.DEVNULL,
                    stderr=subprocess.STDOUT)
    return f"{filename}.{output_ext}"

def translate(audio , model):
    options = dict(beam_size=5, best_of=5)
    translate_options = dict(task="translate", **options)
    result,info = model.transcribe(audio_file,**translate_options)
    return result

def format_timestamp(time):
    if(time< 0): return "timestamp cannot be negative"
    time_in_ms = round(time* 1000.0)

    hours = time_in_ms // 3_600_000
    time_in_ms -= hours * 3_600_000

    minutes = time_in_ms // 60_000
    time_in_ms -= minutes * 60_000

    seconds = time_in_ms // 1_000
    time_in_ms -= seconds * 1_000

    return f"{hours}:{minutes:02d}:{seconds:02d},{time_in_ms:03d}"

def write_srt(segments,filename):
    index=1
    file1 = open(filename, "w")  # append mode

    for segment in segments:
          file1.write( f"{index}\n"
          f"{format_timestamp(segment.start)} --> "
          f"{format_timestamp(segment.end)}\n"
          f"{segment.text.strip().replace('-->', '->')}\n\n",)
          index+=1


def progressbar():
    my_bar = st.progress(0)
    for percent_complete in range(100):
        time.sleep(0.01)
        my_bar.progress(percent_complete + 1)

print("hello")
st.write("hello")

uploaded_file = st.file_uploader("Upload your file here...")

model_size = "large-v2"

# or run on CPU with INT8
model = WhisperModel(model_size, device="cpu", compute_type="int8")

if uploaded_file:
            save_uploadedfile(uploaded_file)
            print('file saved')
             
            input_video = filename
            audio_file = video2mp3(input_video)

            progressbar()

            result = translate(audio_file,model) 

            print('audio translated')   
            subtitle_filename='subtitles.txt'
            write_srt(result,subtitle_filename)

            print('subtitle generated')

            with open(subtitle_filename, "rb") as file:
                btn = st.download_button(
                        label="Download file",
                        data=file,
                        file_name="subtitles.txt"
                    )

            st.stop()
