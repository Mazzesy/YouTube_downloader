import streamlit as st
from youtubesearchpython import VideosSearch, Transcript
from pytube import YouTube, Playlist
import os
import sys


if sys.platform == "win32":  # Windows
    desktop_path = os.path.join(os.path.expanduser('~'), 'Desktop')
elif sys.platform == "darwin":  # MacOS
    desktop_path = os.path.join(os.path.expanduser('~'), 'Desktop')
else:  # Linux
    desktop_path = os.path.join(os.path.expanduser('~'), 'Desktop')

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
        col6.markdown(f"<a href='{video['link']}' target='_blank'>Preview</a>", unsafe_allow_html=True)

    with col7:
        buttons_in_table(video)
    st.markdown('---')

def buttons_in_table(video):
    yt = YouTube(video['link'])
    if st.button('Download Audio', key=f"audio_{video['id']}"):
        audio_stream = yt.streams.filter(only_audio=True).first()
        audio_stream.download(st.session_state.save_path)
    if st.button('Download Video', key=f"video_{video['id']}"):
        video_steam = yt.streams.first()
        video_steam.download(st.session_state.save_path)
    if st.button('Transcript', key=f"transcript_{video['id']}"):
        transcript = Transcript.get(video['id'])
        # write the transcript to txt file
        with open(f"{video['title']}.txt", "w") as file:
            # write dictionary to file
            for key, value in transcript.items():
                file.write(f"{key}: {value}\n")

def main():
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

    st.session_state.save_path = st.text_input('Enter the path to save the files', value=desktop_path)

    with st.expander("Search Video", expanded=False):
        with st.form(key="search_form"):
            st.session_state.show_preview = st.toggle('Show Preview', value=False)
            search_term = st.text_input('Enter the search term')
            if st.form_submit_button('Search'):
                st.session_state.search_results = VideosSearch(search_term)
                st.session_state.all_videos = st.session_state.search_results.result()['result']

    with st.expander("Download Video", expanded=False):
        with st.form(key="download_video"):
            video_url = st.text_input('Enter the video url')
            if st.form_submit_button('Download Audio'):
                yt = YouTube(video_url)
                audio_stream = yt.streams.filter(only_audio=True).first()
                audio_stream.download(st.session_state.save_path)
            if st.form_submit_button('Download Video'):
                yt = YouTube(video_url)
                video_steam = yt.streams.first()
                video_steam.download(st.session_state.save_path)

    with st.expander("Download Playlist", expanded=False):
        with st.form(key="download_playlist"):
            playlist_url = st.text_input('Enter the playlist url')
            if st.form_submit_button('Download Videos'):
                playlist = Playlist(playlist_url)
                for video in playlist.videos:
                    yt = YouTube(video['link'])
                    audio_stream = yt.streams.filter(only_audio=True).first()
                    audio_stream.download(st.session_state.save_path)
            if st.form_submit_button('Download Audios'):
                playlist = Playlist(playlist_url)
                for video in playlist.videos:
                    yt = YouTube(video['link'])
                    video_steam = yt.streams.first()
                    video_steam.download(st.session_state.save_path)

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


# Run the Streamlit app
if __name__ == "__main__":
    main()