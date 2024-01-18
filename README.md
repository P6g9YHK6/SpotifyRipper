## Spotify Music Ripper

Created this tool because Lidarr wasn't working for me. I utilize Spotify as a dashboard to control the downloads, the .py script to download and listen to music through [Navidrome](https://www.navidrome.org/) and it's galaxy of [mobile apps](https://www.reddit.com/r/navidrome/comments/n9gncz/which_android_app_are_you_all_using_with_navidrome/).

All of which seems to be the least problematic FOSS/self-hosted/homelab system for unconventional music tastes.


### Functionality:
Downloads liked songs, all saved playlist, saved albums, saved artists, the current week's Discover Weekly and it will keep them organised for long term storage. Generates .m3u files for Navidrome/Jellyfin and outputs missing items in a `.txt` file.


### Curent State:
Functional

### TODO:
- Determine how to handle `missing.txt` to automate downloads.
- Investigate why it doesn't run in headless mode—possibly requires API tokens.
- Find a solution for [issue 1970](https://github.com/spotDL/spotify-downloader/issues/1970) regarding 10h/1h files.
- Until [Issue 2000](https://github.com/spotDL/spotify-downloader/issues/2000): `--m3u {list}.m3u` is not added to playlist downloads. Once fixed, the create playlist functions can be removed. (would it play nice with subfolders ?)
- if [this issue](https://github.com/spotDL/spotify-downloader/issues/1998) is resolved, remove the api scraper and reset the weekly manualy.
- troubleshoot --sponsor-block check why ffmpeg issue it would be nice to be a default everywhere in any case
- automate the variables
- setup the requirement in the script


### How to use:
- https://www.python.org/downloads/
- py -m ensurepip --upgrade
- pip install spotdl
- spotdl --download-ffmpeg
- pip install pydub

then:

Fill in the variables and run the script.
