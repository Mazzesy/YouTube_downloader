import streamlit as st
from youtubesearchpython import VideosSearch, Transcript, Playlist
from pytube import YouTube
import os
from io import BytesIO
from pathlib import Path


st.set_page_config(page_title="YTD ", page_icon="🚀", layout="wide", )

def download_to_buffer(url, video=True):
    buffer = BytesIO()
    youtube_video = YouTube(url)
    if video:
        stream = youtube_video.streams.get_highest_resolution()
    else:
        stream = youtube_video.streams.get_audio_only()
    default_filename = stream.default_filename
    stream.stream_to_buffer(buffer)
    return default_filename, buffer

def download_transcript(video):
    try:
        transcript = Transcript.get(video['id'])
        # write the transcript to txt file
        with open(f"{video['title']}.txt", "w") as file:
            # write dictionary to file
            for key, value in transcript.items():
                file.write(f"{key}: {value}\n")
        st.success('Transcript Downloaded', icon="✅")
    except:
        st.error('An error occurred', icon="🚨")


def fill_table(video):
    col1, col2 = st.columns((1,1))
    with col1:
        if st.session_state.show_preview:
            st.video(video['link'])
        else:
            st.markdown(f"""<a href={video['link']} target="_blank">
            <!-- Image that serves as the link -->
            <img src={video['thumbnails'][0]['url']} alt="Clickable Image" style="border: 1px solid #000;">
            </a>""", unsafe_allow_html=True)
    with col2:
        st.write(f"__Title:__ {video['title']}")
        st.write(f"__Duration:__ {video['duration']}")
        if video.get('viewCount'):
            st.write(f"__Views:__ {video['viewCount']['short']}")
        if video.get('channel'):
            st.write(f"__Channel:__ {video['channel']['name']}")
        if video.get('publishedTime'):
            st.write(f"__Publication:__ {video['publishedTime']}")
        buttons_in_table(video)
        st.markdown('---')

def download_audio(url):
    with st.spinner("Downloading Audio Stream from Youtube..."):
        default_filename, buffer = download_to_buffer(url, False)
        title_vid = Path(default_filename).with_suffix(".mp3").name
        if st.download_button(
            label="Save Audio",
            data=buffer,
            file_name=title_vid,
            mime="audio/mpeg"):
            st.success('Download Complete', icon="✅")

def download_video(url):
    with st.spinner("Downloading Video Stream from Youtube..."):
        default_filename, buffer = download_to_buffer(url)
    title_vid = Path(default_filename).with_suffix(".mp4").name
    if st.download_button(
        label="Save Video",
        data=buffer,
        file_name=title_vid,
        mime="audio/mpeg"):
        st.success('Download Complete', icon="✅")

def buttons_in_table(video):
    url = video['link']
    col1, col2 = st.columns((1, 1))
    with col1:
        if st.button('Prepare Audio for Download', key=f"audio_{video['id']}"):
            with col2:
                download_audio(url)
    with col2:
        st.write("")

    with col1:
        if st.button('Prepare Video for Download', key=f"video_{video['id']}"):
            with col2:
                download_video(url)
    with col2:
        st.write("")


st.title('Youtube Downloader')

# initialize session state variables
if "search_results" not in st.session_state:
    st.session_state.search_results = None
if "show_preview" not in st.session_state:
    st.session_state.show_preview = False
if 'all_videos' not in st.session_state:
    st.session_state.all_videos = []

st.session_state.show_preview = st.toggle('Show Preview', value=False)

tab1, tab2, tab3 = st.tabs(["Search Video", "Download Url", "Download Playlist"])

with tab1:
    with st.form(key="search_form"):
        search_term = st.text_input('Enter the search term')
        if st.form_submit_button('Search'):
            st.session_state.search_results = VideosSearch(search_term)
            st.session_state.all_videos = st.session_state.search_results.result()['result']

    if st.session_state.all_videos:
        for video in st.session_state.all_videos:
            fill_table(video)

        if st.button('Show more'):
            if st.session_state.search_results.next():
                st.session_state.search_results.next()
                st.session_state.all_videos.extend(st.session_state.search_results.result()['result'])
                st.rerun()

with tab2:
    video_url = st.text_input('Enter the video url')
    if video_url:
        yt = YouTube(video_url)
        if st.session_state.show_preview:
            st.video(yt.streams.first().url)
        else:
            st.image(yt.thumbnail_url)
        st.write(f"Title: {yt.title}")
        st.write(f"Artist: {yt.author}")
        st.write(f"Length: {yt.length} seconds")

        download_audio(video_url)
        download_video(video_url)

with tab3:
    playlist_url = st.text_input('Enter the playlist url')
    if playlist_url:
        playlist = Playlist(playlist_url)
        for video in playlist.videos:
            fill_table(video)
