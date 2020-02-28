Small project I did to allow me to import Spotify playlists to a Youtube playlist.

I typically use Youtube for music, but the playlist selection is rather small. Spotify community playlists are awesome, but only when you have Spotify!
Takes advantage of multiprocessing, Spotify API, and Google API. 

For large playlists, adding matched videos to a Youtube playlist can sometimes error out. Looking into using async requests to potentially solve this.

Requirements:
Google API key, and "client_secret.json" file
Spotify API client ID and secret
Links included for this in "links.txt"

To use:
* "pip install -r requirements.txt"
* Make sure you have a "client_secret.json" from Google to allow this program to OAUTH to your Google/Youtube account.
* Run "python secrets.py" to create a "secrets.json" file with your Google API key, as well as Spotify client ID and secret.
* Lastly, run "python main.py" and follow prompts.
