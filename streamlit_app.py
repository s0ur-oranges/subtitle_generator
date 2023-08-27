# -*- coding: utf-8 -*-

# !apt install imagemagick

# !cat /etc/ImageMagick-6/policy.xml | sed 's/none/read,write/g'> /etc/ImageMagick-6/policy.xml

# Place files in this path or modify the paths to point to where the files are
srtfilename = "subtitles.txt"
mp4filename = "video.mp4"

import sys
import os
import subprocess
import streamlit as st
from faster_whisper import WhisperModel
import time

def save_uploadedfile(uploadedfile):
     with open(filename,"wb") as f:
         f.write(uploadedfile.getbuffer())

def time_to_seconds(time_obj):
    return time_obj.hours * 3600 + time_obj.minutes * 60 + time_obj.seconds + time_obj.milliseconds / 1000

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



#############
#PAGE SET UP
#############

st.set_page_config(page_title="CaptionsCraft", 
                   page_icon=":pen:",
                   layout="wide",
                   initial_sidebar_state="expanded"
                   )


#########
#SIDEBAR
########

st.sidebar.header('Navigate to:')
nav = st.sidebar.radio('',['Go to homepage', 'Generate subtitles'])
st.sidebar.write('')
st.sidebar.write('')
st.sidebar.write('')
st.sidebar.write('')
st.sidebar.write('')


#HOME
#####

if nav == 'Go to homepage':

    st.markdown("<h1 style='text-align: center; color: white; font-size:28px;'>CaptionCraft</h1>", unsafe_allow_html=True)
    st.markdown("<h3 style='text-align: center; font-size:56px;'<p>&#127916;&#9998;</p></h3>", unsafe_allow_html=True)
    st.markdown("<h3 style='text-align: center; color: grey; font-size:20px;'>Utilizing advanced Whisper AI, it effortlessly converts any language spoken in a video into accurate English subtitles. Bridging communication gaps seamlessly. </h3>", unsafe_allow_html=True)
   
    st.markdown('___')
   
    st.markdown("<h3 style='text-align: left; color:#F63366; font-size:18px;'><b>What is this App about?<b></h3>", unsafe_allow_html=True)
    st.write("""This app harnesses the cutting-edge power of the Whisper model to provide you with an unparalleled video subtitle generation experience.

\n\nImagine watching a video in a language you don't understand, but with our app, you won't miss a single detail. Whether it's a captivating foreign short film, an informative documentary, or a heartwarming vlog, our app steps in to bridge the linguistic gap.

\n\nPowered by Whisper AI, our app listens to the spoken words in the video and expertly converts them into accurate and contextually relevant English subtitles. It's like having your own personal interpreter working in real-time, enabling you to enjoy content from around the world without missing out on any crucial information.""")
    
    st.markdown("<h3 style='text-align: left; color:#F63366; font-size:18px;'><b>How to use the app?<b></h3>", unsafe_allow_html=True)
    st.write("""1) Navigate to the 'Generate subtitles' page using navigation bar on the left , and upload the video file. 
             \n\n 2) Choose the whisper model size \n\n 3) Upload your file (limit is 500 mb) \n\n 4) Your subtitles.txt file will be downloaded 
             \n\n 5) Using the file , subtitles can be imposed on any video using any standard video player application.""")
    st.write("Here is the repo link : [GitHub] (https://github.com/dlopezyse/Synthia)")


if nav == 'Generate subtitles':
        filename="videofile"

        print("hello")
        st.write("Choose a model size from the following: ")

        model_size= st.radio("",["no model selected" , "tiny","base","small","medium","large-v2"] , index=0)

        st.write("")
        st.write("")
        uploaded_file = st.file_uploader("Upload your file here...")


        if model_size=="no model selected":
             st.write("Select a model size to continue")
            
        else:
            # or run on CPU with INT8
            model = WhisperModel(model_size, device="cpu", compute_type="int8")

            if uploaded_file:
                        save_uploadedfile(uploaded_file)
                        print('file saved')
                        
                        input_video = filename
                        audio_file = video2mp3(input_video)

                        result = translate(audio_file,model) 

                        print('audio translated')   
                        subtitle_filename='subtitles.txt'
                        write_srt(result,subtitle_filename)

                        print('subtitle generated')

                        with open(subtitle_filename, "rb") as file:
                            btn = st.download_button(
                                
                                    label="Download file",
                                    data=file,
                                    file_name="subtitles.txt",
                                    label_visibility="collapsed"
                                )

                        st.stop()
