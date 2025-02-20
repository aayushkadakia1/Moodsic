from flask import Flask, request, url_for, session, redirect, render_template
from flask_session import Session
import spotipy
from spotipy.oauth2 import SpotifyOAuth
import time
 
 
app = Flask(__name__)
 
 
# Configure session to use filesystem (instead of signed cookies)
app.config["SESSION_PERMANENT"] = False
app.config["SESSION_TYPE"] = "filesystem"
Session(app)
 
 
@app.route("/")
def index():
   return render_template("landing.html")
 

@app.route("/login")
def login():
   oauth = configure_oauth()
   auth_url = oauth.get_authorize_url()
   return redirect(auth_url)


@app.route("/redirect")
def redirected():
    oauth = configure_oauth()
    session.clear()
    code = request.args.get("code")
    token = oauth.get_access_token(code)
    session[0] = token
    return redirect(url_for('getHistory',  _external=True))
 

@app.route("/history")
def getHistory():
    token = get_token()
    spotify = spotipy.Spotify(auth=token['access_token'])
    long_term_tracks = spotify.current_user_top_tracks(limit=50, time_range="long_term")['items']

    average_valence_long = calculate_average_valence(long_term_tracks)

    medium_term_tracks = spotify.current_user_top_tracks(limit=50, time_range="short_term")

    average_valence_medium = calculate_average_valence(medium_term_tracks)

    short_term_tracks = spotify.current_user_top_tracks(limit=50, time_range="short_term")

    average_valence_short = calculate_average_valence(short_term_tracks)

    return str(average_valence_long), str(average_valence_medium), str(average_valence_short)


def get_token():
    token = session[0]
    if not token:
        return redirect(url_for('login', _external=True))
    current_time = int(time.time())
    expiration = token['expires_at'] - current_time < 60
    if (expiration):
        oauth = configure_oauth()
        token = oauth.refresh_access_token(token['refresh_token'])
    return token
    
 
def configure_oauth():
   return SpotifyOAuth (
       client_id="b29fa8d32fe84c9ab17824fcbc95252c",
       client_secret="7d224df0518d442380093e3316aff493",
       redirect_uri=url_for('redirected', _external=True),
       scope="user-top-read"
   )


#def calculate_average_valence(term_valence):
    token = get_token()
    spotify = spotipy.Spotify(auth=token['access_token'])
    # initialize variables
    valence = 0
    counter = 0
    total_track_valence = 0
    # find valence for each song and create average
    for item in term_valence:
        track = item['id']
        track_features = spotify.audio_features(tracks=track)
        intermediary = track_features[0]
        valence = intermediary['valence']
        total_track_valence += valence
        counter += 1

    average_valence = total_track_valence / counter

    return average_valence