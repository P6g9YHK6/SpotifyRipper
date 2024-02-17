# Output directory:
output_directory = r"\\XXXXXXXXX"

#API FOR THE EXTRACTOR
SPOTIPY_CLIENT_ID = 'xxxxxxx'
SPOTIPY_CLIENT_SECRET = 'xxxxxxxxx'
SPOTIPY_REDIRECT_URI = 'http://localhost:8888/callback'
SPOTIPY_USERNAME = 'xxxxxxxxxx'


import subprocess
import re
import datetime
import os

def setup_lib():
    try:
        # Upgrade pip
        subprocess.run(["py", "-m", "ensurepip", "--upgrade"])

        # Install spotdl
        subprocess.run(["pip", "install", "spotdl"])

        # Download ffmpeg for spotdl (automatically answer 'y' to overwrite)
        subprocess.run(["spotdl", "--download-ffmpeg"], input=b'n\n')

        # Install pydub
        subprocess.run(["pip", "install", "pydub"])

        # Install mutagen
        subprocess.run(["pip", "install", "mutagen"])

        # Install spotipy
        subprocess.run(["pip", "install", "spotipy"])

        print("Setup completed successfully.")
        return True
    except subprocess.CalledProcessError as e:
        print(f"Error during setup: {e}")
        return False
    except Exception as e:
        print(f"Unexpected error during setup: {e}")
        return False

# Run the setup
setup_lib()

#import after setup
from mutagen.easyid3 import EasyID3
import spotipy
from spotipy.oauth2 import SpotifyOAuth
from pydub import AudioSegment



def fetch_user_data(client_id, client_secret, redirect_uri, username):
    # Set up Spotipy client
    sp_oauth = SpotifyOAuth(client_id=client_id,
                            client_secret=client_secret,
                            redirect_uri=redirect_uri,
                            scope="playlist-read-private user-library-read user-follow-read",
                            username=username)

    # Get authorization URL
    auth_url = sp_oauth.get_authorize_url()

    print("Authorization URL:", auth_url)

    # Continue with authorization flow...
    sp = spotipy.Spotify(auth_manager=sp_oauth)

    # Get user's playlists, saved tracks, followed artists, etc.
    playlists = sp.current_user_playlists()
    excluded_playlist_name = 'Discover Weekly'
    playlists_list = ' '.join([f"https://open.spotify.com/playlist/{playlist['id']}" for playlist in playlists['items'] if playlist['name'] != excluded_playlist_name])
    weekly_url = next((playlist['external_urls']['spotify'] for playlist in playlists['items'] if playlist['name'] == excluded_playlist_name), None)

    saved_tracks_urls = []
    saved_tracks_response = sp.current_user_saved_tracks(limit=50)  # Adjust limit as needed
    saved_tracks_urls.extend([f"https://open.spotify.com/track/{track['track']['id']}" for track in saved_tracks_response['items']])
    while saved_tracks_response['next']:
        saved_tracks_response = sp.next(saved_tracks_response)
        saved_tracks_urls.extend([f"https://open.spotify.com/track/{track['track']['id']}" for track in saved_tracks_response['items']])
    saved_tracks_urls = ' '.join(saved_tracks_urls)

    followed_artists_urls = []
    followed_artists_response = sp.current_user_followed_artists(limit=50)  # Adjust limit as needed
    followed_artists_urls.extend([artist['external_urls']['spotify'] for artist in followed_artists_response['artists']['items']])
    while followed_artists_response['artists']['next']:
        followed_artists_response = sp.next(followed_artists_response['artists'])
        followed_artists_urls.extend([artist['external_urls']['spotify'] for artist in followed_artists_response['artists']['items']])
    followed_artists_urls = ' '.join(followed_artists_urls)

    saved_albums_urls = []
    saved_albums_response = sp.current_user_saved_albums(limit=50)  # Adjust limit as needed
    saved_albums_urls.extend([album['album']['external_urls']['spotify'] for album in saved_albums_response['items']])
    while saved_albums_response['next']:
        saved_albums_response = sp.next(saved_albums_response)
        saved_albums_urls.extend([album['album']['external_urls']['spotify'] for album in saved_albums_response['items']])
    saved_albums_urls = ' '.join(saved_albums_urls)

    return playlists_list, weekly_url, saved_tracks_urls, followed_artists_urls, saved_albums_urls



def run_spotdl(output_directory, subfolder_name, spotdl_command):
    print(f"\nRunning spotdl command for '{subfolder_name}'...")
    print(f"{spotdl_command}")
    # Create the full path to the subfolder
    subfolder_path = os.path.join(output_directory, subfolder_name)

    # Create the subfolder if it doesn't exist
    os.makedirs(subfolder_path, exist_ok=True)

    # Change the current working directory to the subfolder using os.chdir
    os.chdir(subfolder_path)

    # Run spotdl command
    subprocess.run(spotdl_command)

    print(f"Files downloaded to: {subfolder_path}")


def create_album_playlists(output_directory, subfolder_name):
    print(f"\nCreating playlists for '{subfolder_name}'...")

    playlists_folder = os.path.join(output_directory, subfolder_name)

    # Iterate through subfolders in the specified directory
    for root, dirs, files in os.walk(playlists_folder):
        for folder in dirs:
            folder_path = os.path.join(root, folder)
            mp3_files = [file for file in os.listdir(folder_path) if file.endswith(".mp3")]

            # Only create .m3u file if there are .mp3 files in the subfolder
            if mp3_files:
                playlist_path = os.path.join(folder_path, f"{folder}.m3u")

                # Write the .m3u playlist file
                with open(playlist_path, 'w', encoding='utf-8') as playlist_file:
                    for mp3_file in mp3_files:
                        playlist_file.write(mp3_file + '\n')

                print(f"Playlist created for folder '{folder}' at: {playlist_path}")
            else:
                print(f"No .mp3 files found in folder '{folder}', skipping playlist creation.")


    
def find_and_create_missing_file(output_directory):
    print(f"\nFinding and creating missing.txt file...")

    # Open or create the missing.txt file
    with open(os.path.join(output_directory, '1_missing.txt'), 'w', encoding='utf-8') as missing_file:
        # Iterate through all files in the specified directory and its subdirectories
        for root, dirs, files in os.walk(output_directory):
            for file in files:
                # Check if the file ends with ERR.txt
                if file.endswith('ERR.txt'):
                    full_path = os.path.join(root, file)

                    # Extract content from the current file
                    with open(full_path, 'r', encoding='utf-8', errors='ignore') as current_file:
                        content = current_file.read()

                    # Write full path and content to the missing.txt file
                    missing_file.write(f"{full_path}\n{content}\n\n")

    print("missing.txt file created.")

'''
Cheatlist:
 available variables for file names: {title}, {artists}, {artist}, {album}, {album-artist}, {genre}, {disc-number}, {disc-count}, {duration}, {year}, {original-date}, {track-number}, {tracks-count}, {isrc}, {track-id}, {publisher}, {list-length}, {list-position}, {list-name}, {output-ext}
'''

# Task 0
# Call the function to fetch user data
playlists_list, weekly_url, saved_tracks_url, followed_artists_url, saved_albums_url = fetch_user_data(SPOTIPY_CLIENT_ID, SPOTIPY_CLIENT_SECRET, SPOTIPY_REDIRECT_URI, SPOTIPY_USERNAME)
#debug output
("Generated playlists_list (excluding Discover Weekly):")
print(playlists_list)
print("Generated weekly_url:")
print(weekly_url)
print("Generated saved_tracks_list:")
print(saved_tracks_url)
print("Generated followed_artists_list:")
print(followed_artists_url)
print("Generated saved_albums_list:")
print(saved_albums_url)

# Task 1: liked_songs
subfolder_name_1 = "1_likedsongs"
formatted_output_1 = '{artists} - {title}.{output-ext}'
spotdl_command_1 = f'spotdl sync {get_saved_tracks_list(SPOTIPY_CLIENT_ID, SPOTIPY_CLIENT_SECRET, SPOTIPY_REDIRECT_URI, SPOTIPY_USERNAME)} --format mp3 --sync-without-deleting --user-auth --playlist-numbering --save-errors likedsongsERR.txt --save-file likedsongs.spotdl --output "{formatted_output_1}" --m3u _Liked_Songs.m3u '
run_spotdl(output_directory, subfolder_name_1, spotdl_command_1)

# Task 2: Discover Weekly playlist with week number and year
# Format the week number and year
current_date = datetime.date.today()
formatted_week_and_year = f"{current_date.year % 100:02d}_{current_date.isocalendar()[1]:02d}"
print("Formatted Week and Year:", formatted_week_and_year)

subfolder_name_2 = f"{formatted_week_and_year}"
formatted_output_2 = '{artists} - {title}.{output-ext}'
spotdl_command_2 = f'spotdl sync {weekly_url} --format mp3 --playlist-numbering --save-errors discover_weeklyERR.txt --save-file discover_weekly.spotdl --output "{formatted_output_2}" --m3u {formatted_week_and_year}.m3u '
run_spotdl(output_directory, subfolder_name_2, spotdl_command_2)

# Task 3: all users playlists
subfolder_name_3 = "1_playlists"
formatted_output_3 = '{album}/{artists} - {title}.{output-ext}'
spotdl_command_3 = f'spotdl sync {playlists_list} --format mp3 --sync-without-deleting --playlist-numbering --save-errors playlistsERR.txt --save-file playlists.spotdl --output "{formatted_output_3}" '
run_spotdl(output_directory, subfolder_name_3, spotdl_command_3)

#Create playlists for each album in "playlists" folder --playlist-numbering allow to do this
create_album_playlists(output_directory, subfolder_name_3)

# Task 4: all-user-followed-artists
subfolder_name_4 = "artists"
formatted_output_4 = '{album-artist}/{album}/{artists} - {title}.{output-ext}'
spotdl_command_4 = f'spotdl sync {followed_artists_url} --format mp3 --sync-without-deleting --user-auth --save-errors artistsERR.txt --save-file artists.spotdl --output "{formatted_output_4}" '
run_spotdl(output_directory, subfolder_name_4, spotdl_command_4)

# Task 5: all-user-saved-albums
subfolder_name_5 = "artists"
formatted_output_5 = '{album-artist}/{album}/{artists} - {title}.{output-ext}'
spotdl_command_5 = f'spotdl sync {saved_albums_url} --format mp3 --sync-without-deleting --user-auth --save-errors albumsERR.txt --save-file albums.spotdl --output "{formatted_output_5}" '
run_spotdl(output_directory, subfolder_name_5, spotdl_command_5)

# Task 6: compile error logs
find_and_create_missing_file(output_directory)
