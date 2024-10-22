import spotipy
from spotipy.oauth2 import SpotifyOAuth
import cohere
from datetime import datetime

# Configuración de la autenticación de Spotify
sp = spotipy.Spotify(auth_manager=SpotifyOAuth(
    client_id="TU_CLIENT_ID",
    client_secret="TU_CLIENT_SECRET",
    redirect_uri="TU_REDIRECT_URI",
    scope="playlist-modify-public playlist-modify-private"
))

# Configuración de la API de Cohere
co = cohere.Client('Cohere_API_KEY')

# ID de la playlist
playlist_id = "PLAYLIST_ID"

# Lista para almacenar las canciones eliminadas
deleted_tracks = []
spanish_tracks = []

def is_track_spanish_using_cohere(track_name, artist_name):
    """Función para determinar si una canción es en español usando Cohere."""
    prompt = f"La canción '{track_name}' de '{artist_name}' está en español, inglés, u otro idioma? Responde solo con el nombre del idioma."
    
    try:
        response = co.generate(
            model='command-xlarge-nightly',  # Puedes usar otros modelos como 'medium' si es más adecuado
            prompt=prompt,
            max_tokens=10,
            temperature=0.5
        )
        
        # Extraemos la respuesta
        answer = response.generations[0].text.strip().lower()
        print(f"Cohere Response for '{track_name}' by '{artist_name}': {answer}")
        
        # Comprobamos si el modelo identificó el idioma como español
        return "español" in answer
    except Exception as e:
        print(f"Error al consultar Cohere para '{track_name}' de '{artist_name}': {e}")
        return False

def get_spanish_tracks():
    """Obtiene todas las canciones en español de la playlist."""
    results = sp.playlist_tracks(playlist_id)
    tracks = results["items"]
    for track in tracks:
        track_name = track["track"]["name"]
        artist_name = track["track"]["artists"][0]["name"]
        track_uri = track["track"]["uri"]
        
        if is_track_spanish_using_cohere(track_name, artist_name):
            spanish_tracks.append((track_name, track_uri))

def show_spanish_tracks():
    """Muestra las canciones en español encontradas y permite al usuario seleccionar cuáles mantener."""
    print("Se han encontrado las siguientes canciones en español en la playlist:")
    for idx, track in enumerate(spanish_tracks):
        print(f"[{idx + 1}] {track[0]}")
    
    to_keep = input("Selecciona las canciones que NO quieres eliminar separadas por comas: ")
    try:
        to_keep = [int(x.strip()) - 1 for x in to_keep.split(',')]
        return [spanish_tracks[i] for i in to_keep if 0 <= i < len(spanish_tracks)]
    except ValueError:
        print("Entrada no válida. Asegúrate de ingresar números separados por comas.")
        return []

def remove_tracks(tracks_to_remove):
    """Elimina las canciones de la playlist y guarda un registro en un archivo."""
    for track_name, track_uri in tracks_to_remove:
        try:
            # Usamos el método correcto para eliminar las canciones
            sp.playlist_remove_all_occurrences_of_items(playlist_id, [track_uri])
            deleted_tracks.append(track_name)
        except Exception as e:
            print(f"Error al eliminar '{track_name}': {e}")
    
    # Registrar las canciones eliminadas con timestamp
    with open("deleted_tracks.log", "a") as file:
        timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        file.write(f"Eliminación de canciones en {timestamp}:\n")
        for track in deleted_tracks:
            file.write(f"{track}\n")
        file.write("\n")

def main():
    """Función principal del programa."""
    get_spanish_tracks()
    if not spanish_tracks:
        print("No se encontraron canciones en español en la playlist.")
        return
    
    tracks_to_keep = show_spanish_tracks()
    tracks_to_remove = [track for track in spanish_tracks if track not in tracks_to_keep]
    
    if not tracks_to_remove:
        print("No se eliminarán canciones en español.")
        return
    
    confirm = input(f"Se eliminarán {len(tracks_to_remove)} canciones en español. ¿Estás seguro? (s/n): ").lower()
    if confirm == 's':
        remove_tracks(tracks_to_remove)
        print(f"Eliminadas {len(tracks_to_remove)} canciones en español de la playlist.")
    else:
        print("Operación cancelada. No se eliminó ninguna canción.")

if __name__ == "__main__":
    main()