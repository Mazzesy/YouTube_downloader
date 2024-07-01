import streamlit as st
from youtubesearchpython import VideosSearch, Transcript
from pytube import YouTube, Playlist
import os

st.set_page_config(page_title="YTD ", page_icon="🚀", layout="wide", )


def download_audio(yt):
    try:
        audio_stream = yt.streams.filter(only_audio=True).first()
        audio_stream.download(st.session_state.save_path)
        file_path = st.session_state.save_path + audio_stream.default_filename
        with open(file_path, "rb") as f:
            buffer = f.read()
        if st.download_button(
            label="Download Audio",
            data=buffer,
            file_name=audio_stream.default_filename,
            mime="audio/mpeg"):
            st.success('Download Complete', icon="✅")
    except:
        st.error('An error occurred', icon="🚨")


def download_video(yt):
    try:
        video_steam = yt.streams.first()
        video_steam.download(st.session_state.save_path)
        file_path = st.session_state.save_path + video_steam.default_filename
        with open(file_path, "rb") as f:
            buffer = f.read()
        if st.download_button(
                label="Download Video",
                data=buffer,
                file_name=video_steam.default_filename,
                mime="audio/mpeg"):
            st.success('Download Complete', icon="✅")
    except:
        st.error('An error occurred', icon="🚨")


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
    col1, col2, col3, col4, col5, col6, col7 = st.columns((4, 2, 2, 2, 2, 2, 4))
    col1.write(video['title'])
    col2.write(video['duration'])
    col3.write(video['viewCount']["short"])
    col4.write(video['channel']["name"])
    col5.write(video['publishedTime'])
    if st.session_state.show_preview:
        col6.video(video['link'])
    else:
        col6.markdown(f"""<a href={video['link']} target="_blank">
        <!-- Image that serves as the link -->
        <img src={video['thumbnails'][0]['url']} alt="Clickable Image" style="border: 1px solid #000;">
        </a>""", unsafe_allow_html=True)

    with col7:
        buttons_in_table(video)
    st.markdown('---')


def buttons_in_table(video):
    yt = YouTube(video['link'])
    #if st.button('Create Audio Download Link', key=f"audio_{video['id']}"):
    download_audio(yt)
    #if st.button('Create Video Download Link', key=f"video_{video['id']}"):
    download_video(yt)


st.title('Youtube Downloader')

# initialize session state variables
if "search_results" not in st.session_state:
    st.session_state.search_results = None
if "filtered_results" not in st.session_state:
    st.session_state.filtered_results = []
if "save_path" not in st.session_state:
    st.session_state.save_path = ""
if "show_preview" not in st.session_state:
    st.session_state.show_preview = False
if 'all_videos' not in st.session_state:
    st.session_state.all_videos = []

directory = 'downloads/'
if not os.path.exists(directory):
    os.makedirs(directory)
st.session_state.save_path = st.text_input('Enter the path to save the files', value=directory)

tab1, tab2, tab3 = st.tabs(["Search Video", "Download Url", "Download Playlist"])

with tab1:
    with st.form(key="search_form"):
        st.session_state.show_preview = st.toggle('Show Preview', value=False)
        search_term = st.text_input('Enter the search term')
        if st.form_submit_button('Search'):
            st.session_state.search_results = VideosSearch(search_term)
            st.session_state.all_videos = st.session_state.search_results.result()['result']

    if st.session_state.all_videos:
        columns = st.columns((4, 2, 2, 2, 2, 2, 4))
        fields = ["Title", 'Duration', 'Views', 'Channel', "Publication", "Preview", "Download"]
        st.markdown('---')

        # write headers
        for col, field_name in zip(columns, fields):
            col.write(f"**{field_name}**")
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
        st.video(yt.streams.first().url)
        st.write(f"Title: {yt.title}")
        st.write(f"Artist: {yt.author}")
        st.write(f"Length: {yt.length} seconds")
        download_audio(yt)
        download_video(yt)
