# -*- coding: utf-8 -*-

# !apt install imagemagick

# !cat /etc/ImageMagick-6/policy.xml | sed 's/none/read,write/g'> /etc/ImageMagick-6/policy.xml

# Place files in this path or modify the paths to point to where the files are
srtfilename = "subtitles.txt"
mp4filename = "Apna Bana Le Song Full Screen-(MirchiStatus.com).mp4"

import sys
import pysrt
import os
import subprocess
from moviepy.editor import VideoFileClip, TextClip, CompositeVideoClip
import streamlit as st
import whisper
import pickle

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
    result = model.transcribe(audio_file,**translate_options)
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
          f"{format_timestamp(segment['start'])} --> "
          f"{format_timestamp(segment['end'])}\n"
          f"{segment['text'].strip().replace('-->', '->')}\n\n",)
          index+=1

print("hello")
st.write("hello")

model=whisper.load_model('medium')
print('model loaded')


uploaded_file = st.file_uploader("Upload your file here...")


if uploaded_file:
            save_uploadedfile(uploaded_file)
            print('file saved')
             
            input_video = filename
            audio_file = video2mp3(input_video)

            result = translate(audio_file,model) 

            print('audio translated')   
            subtitle_filename='subtitles.txt'
            write_srt(result['segments'],subtitle_filename)

            print('subtitle generated')
            
                        # Load video and SRT file
            video = VideoFileClip(filename)
            subtitles = pysrt.open(srtfilename)

            begin,end= mp4filename.split(".mp4")
            output_video_file = begin+'_subtitled'+".mp4"

            print ("Output file name: ",output_video_file)

            # Create subtitle clips
            subtitle_clips = create_subtitle_clips(subtitles,video.size)

            # Add subtitles to the video
            final_video = CompositeVideoClip([video] + subtitle_clips)

            # Write output video file
            final_video.write_videofile(output_video_file)

            video_file = open(output_video_file, 'rb')
            video_bytes = video_file.read()


            with open(output_video_file, "rb") as file:
                btn = st.download_button(
                        label="Download video",
                        data=file,
                        file_name="video.mp4"
                    )

            st.stop()


# from IPython.display import HTML
# from base64 import b64encode
# mp4 = open(output_video_file,'rb').read()
# data_url = "data:video/mp4;base64," + b64encode(mp4).decode()
# HTML("""
# <video width=400 controls>
#       <source src="%s" type="video/mp4">
# </video>
# """ % data_url)