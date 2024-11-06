import json
import spotipy
from spotipy.oauth2 import SpotifyClientCredentials
import pandas as pd
import time
from datetime import date
import os
import glob
from tqdm import tqdm
import random

client_credentials_manager = SpotifyClientCredentials(client_id='YOUR_CLIENT_API_ID',client_secret='YOUR_CLIENT_API_SECRET')
spotify = spotipy.Spotify(client_credentials_manager=client_credentials_manager)

today = date.today().isoformat()
file_path = f"raw_data/{today}"

def get_playlist_data():
    playlists = pd.read_excel("playlist.xlsx")
    for index, row in playlists.iterrows():
        pais = row["COUNTRY"]
        playlist_id = row["ID"]
        playlist_name = row["NAME"]
        playlists_file_path = f"{file_path}/playlist_items"
        file_name = f'{playlists_file_path}/{pais}-{playlist_id}.json'

        if not os.path.exists(playlists_file_path):
            os.makedirs(playlists_file_path)

        if os.path.exists(file_name):
            print(f"Playlist {playlist_id} - {pais} yet downloaded")
            pass

        else:
            print(f"Getting Data for {pais} - {playlist_id}")
            api_response = spotify.playlist_items(playlist_id)
            with open(file_name, 'w', encoding='utf-8') as f:
                json.dump(api_response, f, ensure_ascii=False, indent=4)
            time.sleep(2)

def pharse_playlist_data_to_xlsx():
    files = glob.glob(f"{file_path}/playlist_items/*.json")
    print(f"Pharsing data from {len(files)} playlists JSON FILES")

    for file in tqdm(files):
        playlist_data = []
        try:
            pais = file.split("-")[-2].split("/")[-1]
            playlist_id = file.split("-")[-1].split(".")[0]
        except:
            pais = file.split("-")[-2].split("\\")[-1]
            playlist_id = file.split("-")[-1].split(".")[0]

        export_file_name = f'{file_path}/playlist_items/{pais}-{playlist_id}.xlsx'

        # Lista para almacenar los datos de una playlist
        with open(file, 'r', encoding='utf-8') as f:
            data = json.load(f)

            for item in data["items"]:
                track_data = {}
                # Track Data
                track_data["artists"] = [artists["name"] for artists in item["track"]["album"]["artists"]]
                track_data["track_name"] = item["track"]["name"]
                track_data["popularity"] = item["track"]["popularity"]
                track_data["playlist"] = pais
                track_data["track_id"] = item["track"]["id"]
                # Track Duration
                track_data["duration_ms"] = item["track"]["duration_ms"]
                track_data["duration_sec"] = track_data["duration_ms"]/1000
                def ms_to_min_and_secs(ms):
                    total_segundos = ms / 1000  # Convertir milisegundos a segundos
                    minutos = int(total_segundos // 60)  # Obtener los minutos completos
                    segundos = int(total_segundos % 60)  # Obtener los segundos restantes
                    return f"{minutos}.{segundos:02d}"  # Formato mm:ss con dos dígitos para los segundos
                track_data["duration_min"] = float(ms_to_min_and_secs(track_data["duration_ms"]))
                # Explicit Content
                track_data["explicit"] = item["track"]["explicit"]
                # First artist (main artist) ID AND NAME
                track_data["primer_artista_name"] = item["track"]["artists"][0]["name"]
                track_data["primer_artista_id"] = item["track"]["artists"][0]["id"]
                # Playlist contextual Info
                track_data["playlist_url"] = data["href"]
                track_data["playlist_id"] = playlist_id
                # Track Album Data
                track_data["album_name"] = item["track"]["album"]["name"]
                track_data["album_id"] = item["track"]["album"]["id"]
                track_data["album_release_date"] = item["track"]["album"]["release_date"]
                track_data["album_total_tracks"] = item["track"]["album"]["total_tracks"]
                track_data["album_main_artist"] = item["track"]["album"]["artists"][0]["name"]
                track_data["album_main_artist_id"] = item["track"]["album"]["artists"][0]["id"]
                track_data["track_number_in_album"] = item["track"]["track_number"]
                playlist_data.append(track_data)

        df = pd.DataFrame(playlist_data)
        df.to_excel(export_file_name,index=False)

    # Join all playlists in same file
    all_dfs = glob.glob(f"{file_path}/playlist_items/*.xlsx")
    global_df = pd.concat([pd.read_excel(file) for file in all_dfs])
    global_df.to_excel(f"raw_data/{today}/{today}-all_playlists_items.xlsx", index=False)


def get_audio_features():
    def get_features_api_data(track_id):
        try:
            audio_features = spotify.audio_features(track_id)
            data = pd.DataFrame.from_dict(audio_features, orient='columns')
            data["track_id"] = track_id
            data.to_excel(f"{file_path}/audio_features/{track_id}-audio_features.xlsx", index=False)

        except spotipy.exceptions.SpotifyException as e:
            if e.http_status == 429:
                print(e)
                print("Error 409 Retry in 5 minutes")
                time.sleep(300)
                get_features_api_data(track_id)
            if e.http_status == 503:
                print(e)
                print("Error 503 Retry in 5 minutes")
                time.sleep(300)
                get_features_api_data(track_id)
            else:
                raise e

    df = pd.read_excel(f"raw_data/{today}/{today}-all_playlists_items.xlsx")

    tracks = df["track_id"].unique()
    tracks = tracks.tolist()
    print("Getting Audio Features")
    if not os.path.exists(f"{file_path}/audio_features/"):
            os.makedirs(f"{file_path}/audio_features/")

    for track in tqdm(tracks):
        wait_time = random.randint(1,2)
        path = f"{file_path}/audio_features/{track}-audio_features.xlsx"
        if not os.path.exists(path):
            get_features_api_data(track)
            time.sleep(wait_time)
        else:
            print(f"Audio Features for track with ID:{track} Downloaded")
            pass
    all_features = glob.glob(f"{file_path}/audio_features/*.xlsx")
    concat_features = pd.concat([pd.read_excel(file) for file in all_features])
    concat_features.drop(['duration_ms', "type","uri","analysis_url"], axis=1, inplace=True)
    concat_features.track_id = concat_features.track_id.astype(str)
    main_frame = pd.read_excel(f"{file_path}/{today}-all_playlists_items.xlsx")
    main_frame = main_frame.merge(concat_features, on="track_id", how="left")
    main_frame.to_excel(f"raw_data/{today}/{today}-all_playlists_items.xlsx", index=False)


def get_artist_info():
    def get_artists_api_data(artist_id):
        try:
            artist_info = spotify.artist(artist_id)
            # Guardem la ROW amb les dades noves en una llista
            data = {}
            data["artist_followers"] = artist_info["followers"]["total"]
            data["artist_genres"] = artist_info["genres"]
            data["artist_main_genres"] = artist_info["genres"][0]
            data["primer_artista_id"] = artist_id
            data["artist_popularity"] = artist_info["popularity"]
            final = pd.DataFrame.from_dict([data], orient='columns')
            final.to_excel(f"{file_path}/artist_info/{artist}-artist_info.xlsx", index=False)

        except spotipy.exceptions.SpotifyException as e:
            if e.http_status == 429:
                print(e)
                print("Error 429 Too many requests Retry in 5 minutes")
                time.sleep(300)
                get_artists_api_data(artist_id)
            if e.http_status == 503:
                print(e)
                print("Error 503 Retry in 5 minutes")
                time.sleep(300)
                get_artists_api_data(artist_id)
            else:
                raise e

    df = pd.read_excel(f"raw_data/{today}/{today}-all_playlists_items.xlsx")
    artist_ids = df["primer_artista_id"].unique()
    artist_ids  = artist_ids.tolist()
    print("Getting Artists Info")
    if not os.path.exists(f"{file_path}/artist_info/"):
        os.makedirs(f"{file_path}/artist_info/")

    for artist in tqdm(artist_ids):
        wait_time = random.randint(1,2)
        path = f"{file_path}/artist_info/{artist}-artist_info.xlsx"
        if not os.path.exists(path):
            get_artists_api_data(artist)
            time.sleep(wait_time)
        else:
            print(f"Data from Artist: {artist} yet downloaded")
            pass

    all_artists = glob.glob(f"{file_path}/artist_info/*.xlsx")
    concat_artists = pd.concat([pd.read_excel(file) for file in all_artists])
    main_frame = pd.read_excel(f"{file_path}/{today}-all_playlists_items.xlsx")
    main_frame = main_frame.merge(concat_artists, on="primer_artista_id", how="left")
    main_frame.to_excel(f"raw_data/{today}/{today}-all_playlists_items.xlsx", index=False)


get_playlist_data()
pharse_playlist_data_to_xlsx()
get_audio_features()
get_artist_info()
