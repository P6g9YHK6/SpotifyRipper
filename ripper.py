import os
import subprocess
import datetime
from mutagen.easyid3 import EasyID3
import re
import spotipy
from spotipy.oauth2 import SpotifyOAuth
from pydub import AudioSegment

# Output directory:
output_directory = r"\\XXXXXXXXX"

#API FOR THE EXTRACTOR
SPOTIPY_CLIENT_ID = 'xxxxxxx'
SPOTIPY_CLIENT_SECRET = 'xxxxxxxxx'
SPOTIPY_REDIRECT_URI = 'https://xxxxxxxxxx'
SPOTIPY_USERNAME = 'xxxxxxxxxx'

def populate_playlists_and_weekly_url(client_id, client_secret, redirect_uri, username):
    # Set up Spotipy client
    sp = spotipy.Spotify(auth_manager=SpotifyOAuth(client_id=client_id,
                                                   client_secret=client_secret,
                                                   redirect_uri=redirect_uri,
                                                   scope="playlist-read-private",
                                                   username=username))

    # Get user's playlists
    playlists = sp.current_user_playlists()

    # Exclude Discover Weekly playlist
    excluded_playlist_name = 'Discover Weekly'
    playlists_list = ' '.join([f"https://open.spotify.com/playlist/{playlist['id']}" for playlist in playlists['items'] if playlist['name'] != excluded_playlist_name])

    # Get the URL for the user's Discover Weekly playlist
    weekly_url = next((playlist['external_urls']['spotify'] for playlist in playlists['items'] if playlist['name'] == excluded_playlist_name), None)

    return playlists_list, weekly_url


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


def delete_long_songs(output_directory):
    print("\nDeleting songs longer than 59 minutes...")

    # Open or create the deletedERR.txt file
    with open(os.path.join(output_directory, 'deletedERR.txt'), 'w', encoding='utf-8') as deleted_file:
        # Iterate through all files in the specified directory and its subdirectories
        for root, dirs, files in os.walk(output_directory):
            for file in files:
                # Check if the file ends with .mp3
                if file.endswith('.mp3'):
                    full_path = os.path.join(root, file)

                    try:
                        # Load the audio file using pydub
                        audio = AudioSegment.from_file(full_path)

                        # Get the duration in minutes
                        duration_minutes = len(audio) / (60 * 1000)

                        # Delete the file if duration is longer than 59 minutes
                        if duration_minutes > 59:
                            os.remove(full_path)
                            deleted_file.write(f"{os.path.splitext(file)[0]}\n")
                            print(f"Deleted: {file}")
                    except Exception as e:
                        print(f"Error processing '{file}': {e}")

    print("Deletion of long songs completed.")


#Each task is independant and can be commented out

'''
#Link to weekly discovery playlist if you want to set manually the list without the api commentent task 0
weekly_url = "https://open.spotify.com/playlist/XXXXXXXXXXXXXXXX"
# List of playlists to download if you want to set manually the list without the api
playlists_list = "https://open.spotify.com/playlist/XXXXXXXXXXXXXXXXXXXXXXX https://open.spotify.com/playlist/XXXXXXXXXXXXXXXXXXXXXXX"
'''
'''
Cheatlist:
 available variables for file names: {title}, {artists}, {artist}, {album}, {album-artist}, {genre}, {disc-number}, {disc-count}, {duration}, {year}, {original-date}, {track-number}, {tracks-count}, {isrc}, {track-id}, {publisher}, {list-length}, {list-position}, {list-name}, {output-ext}
'''

# Task 0: build playlist list
playlists_list, weekly_url = populate_playlists_and_weekly_url(SPOTIPY_CLIENT_ID, SPOTIPY_CLIENT_SECRET, SPOTIPY_REDIRECT_URI, SPOTIPY_USERNAME)
print("Generated playlists_list (excluding Discover Weekly):")
print(playlists_list)
print("Generated weekly_url:")
print(weekly_url)

# Task 1: liked_songs
subfolder_name_1 = "1_likedsongs"
formatted_output_1 = '{artists} - {title}.{output-ext}'
spotdl_command_1 = f'spotdl sync saved --format mp3 --sync-without-deleting --user-auth --playlist-numbering --save-errors likedsongsERR.txt --save-file likedsongs.spotdl --output "{formatted_output_1}" --m3u 1_Liked_Songs.m3u '
run_spotdl(output_directory, subfolder_name_1, spotdl_command_1)

# Task 2: Discover Weekly playlist with week number and year
#Format the week numer
iso_calendar_date = datetime.date.today().isocalendar()
formatted_week_and_year = f"Week_{iso_calendar_date.week}_{iso_calendar_date.year}"
print("Formatted Week and Year:", formatted_week_and_year)

subfolder_name_2 = f"1_discover_weekly\\{formatted_week_and_year}"
formatted_output_2 = '{artists} - {title}.{output-ext}'
spotdl_command_2 = f'spotdl sync {weekly_url} --format mp3 --user-auth --playlist-numbering --save-errors discover_weeklyERR.txt --save-file discover_weekly.spotdl --output "{formatted_output_2}" --m3u {formatted_week_and_year}.m3u '
run_spotdl(output_directory, subfolder_name_2, spotdl_command_2)

# Task 3: all-user-saved-playlists
subfolder_name_3 = "1_playlists"
formatted_output_3 = '{album}/{artists} - {title}.{output-ext}'
spotdl_command_3 = f'spotdl sync {playlists_list} --format mp3 --sync-without-deleting --user-auth --playlist-numbering --save-errors playlistsERR.txt --save-file playlists.spotdl --output "{formatted_output_3}" '
run_spotdl(output_directory, subfolder_name_3, spotdl_command_3)

#Create playlists for each album in "playlists" folder --playlist-numbering allow to do this
create_album_playlists(output_directory, subfolder_name_3)

# Task 4: all-user-followed-artists
subfolder_name_4 = "artists"
formatted_output_4 = '{album-artist}/{album}/{artists} - {title}.{output-ext}'
spotdl_command_4 = f'spotdl sync all-user-followed-artists --format mp3 --sync-without-deleting --user-auth --save-errors artistsERR.txt --save-file artists.spotdl --output "{formatted_output_4}" '
run_spotdl(output_directory, subfolder_name_4, spotdl_command_4)

# Task 5: all-user-saved-albums
subfolder_name_5 = "artists"
formatted_output_5 = '{album-artist}/{album}/{artists} - {title}.{output-ext}'
spotdl_command_5 = f'spotdl sync all-user-saved-albums --format mp3 --sync-without-deleting --user-auth --save-errors albumsERR.txt --save-file albums.spotdl --output "{formatted_output_5}" '
run_spotdl(output_directory, subfolder_name_5, spotdl_command_5)



# Task 6: delete fuckups and compile error logs
#delete_long_songs(output_directory)
find_and_create_missing_file(output_directory)
