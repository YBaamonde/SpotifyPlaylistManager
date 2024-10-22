# ---------------------------------------------------- #
# Este script usa la API de Spotify para eliminar las canciones posteriores al año 2010 de una playlist. #
# ---------------------------------------------------- #


import spotipy
from spotipy.oauth2 import SpotifyOAuth
from datetime import datetime

# Configuración de la autenticación de Spotify
sp = spotipy.Spotify(auth_manager=SpotifyOAuth(
    client_id="TU_CLIENT_ID",
    client_secret="TU_CLIENT_SECRET",
    redirect_uri="TU_REDIRECT_URI",
    scope="playlist-modify-public playlist-modify-private"
))

# ID de la playlist
playlist_id = "TU_PLAYLIST_ID"

# Lista para almacenar las canciones eliminadas
deleted_tracks = []
recent_tracks = []

def is_track_recent(track):
    """Función para determinar si una canción fue lanzada después de 2010."""
    release_date = track["track"]["album"]["release_date"]
    # Extraemos el año de la fecha de lanzamiento
    release_year = int(release_date.split("-")[0])
    return release_year > 2010, release_year

def get_recent_tracks():
    """Obtiene todas las canciones lanzadas después de 2010 de la playlist."""
    results = sp.playlist_tracks(playlist_id)
    tracks = results["items"]
    for track in tracks:
        track_name = track["track"]["name"]
        artist_name = track["track"]["artists"][0]["name"]
        track_uri = track["track"]["uri"]
        is_recent, release_year = is_track_recent(track)
        
        if is_recent:
            recent_tracks.append((track_name, artist_name, track_uri, release_year))

def show_recent_tracks():
    """Muestra las canciones lanzadas después de 2010 y permite al usuario seleccionar cuáles mantener."""
    print("Se han encontrado las siguientes canciones lanzadas después de 2010 en la playlist:")
    for idx, track in enumerate(recent_tracks):
        print(f"[{idx + 1}] {track[0]} - {track[1]} ({track[3]})")
    
    to_keep = input("Selecciona las canciones que NO quieres eliminar separadas por comas: ")
    try:
        to_keep = [int(x.strip()) - 1 for x in to_keep.split(',')]
        return [recent_tracks[i] for i in to_keep if 0 <= i < len(recent_tracks)]
    except ValueError:
        print("Entrada no válida. Asegúrate de ingresar números separados por comas.")
        return []

def remove_tracks(tracks_to_remove):
    """Elimina las canciones de la playlist y guarda un registro en un archivo."""
    for track_name, artist_name, track_uri, release_year in tracks_to_remove:
        try:
            # Usamos el método correcto para eliminar las canciones
            sp.playlist_remove_all_occurrences_of_items(playlist_id, [track_uri])
            deleted_tracks.append((track_name, artist_name, release_year))
        except Exception as e:
            print(f"Error al eliminar '{track_name}' de '{artist_name}': {e}")
    
    # Registrar las canciones eliminadas con timestamp
    with open("deleted_tracks.log", "a") as file:
        timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        file.write(f"Eliminación de canciones en {timestamp}:\n")
        for track_name, artist_name, release_year in deleted_tracks:
            file.write(f"{track_name} - {artist_name} ({release_year})\n")
        file.write("\n")

def main():
    """Función principal del programa."""
    get_recent_tracks()
    if not recent_tracks:
        print("No se encontraron canciones lanzadas después de 2010 en la playlist.")
        return
    
    tracks_to_keep = show_recent_tracks()
    tracks_to_remove = [track for track in recent_tracks if track not in tracks_to_keep]
    
    if not tracks_to_remove:
        print("No se eliminarán canciones lanzadas después de 2010.")
        return
    
    confirm = input(f"Se eliminarán {len(tracks_to_remove)} canciones lanzadas después de 2010. ¿Estás seguro? (s/n): ").lower()
    if confirm == 's':
        remove_tracks(tracks_to_remove)
        print(f"Eliminadas {len(tracks_to_remove)} canciones lanzadas después de 2010 de la playlist.")
    else:
        print("Operación cancelada. No se eliminó ninguna canción.")

if __name__ == "__main__":
    main()