from yandex_music import Client
import requests
import os
import music_tag
from config import ya_token, download_path

client = Client(token=ya_token)
client.init()

def search_and_download_artist(search:str):
    '''Ищем лучший результат по запросу артиста и скачиваем все его песни в папку download с разбивкой по альбомам'''

    search_result = client.search(search, type_="artist", page=0, nocorrect=False) # поиск
    artist_id = search_result['artists']['results'][0]['id']
    artist_name = search_result['artists']['results'][0]['name']

    print('Artist ID: ', artist_id) # вывод ID
    print(search_result['artists']['results'][0]['name']) # вывод названия артиста
    print('Direct albums: ',search_result['artists']['results'][0]['counts']['direct_albums']) # вывод количества его альбомов

    artist_cover_link = client.artistsBriefInfo(artist_id=artist_id)['artist']['cover']['uri'].replace('%%', '1000x1000')
    artist_folder = f"{download_path}/{artist_name}"
    artist_cover_pic = f"{artist_folder}/artist.jpg"

    os.makedirs(os.path.dirname(f"{artist_folder}/"),exist_ok=True)
    with open(artist_cover_pic, 'wb') as f:  # качаем обложку артиста
        rec = requests.get('http://' + artist_cover_link)
        f.write(rec.content)

    # находим список альбомов артиста с информацией
    direkt_albums = client.artistsDirectAlbums(artist_id=artist_id)
    # проходимся по каждому альбому
    for album in direkt_albums:
        print('id_album: ', album['id'], ' - ', album['title'])

        #создаем папку для альбома
        album_folder = f"{artist_folder}/{album['title']} ({album['year']})"
        os.makedirs(os.path.dirname(f"{album_folder}/"),exist_ok=True)
        album_cover_pic = f"{album_folder}/cover.jpg"
        # качаем обложку альбома
        with open(album_cover_pic, 'wb') as f:
            rec = requests.get('http://' + album['cover_uri'].replace('%%', '1000x1000'))
            f.write(rec.content)

        # проходимся по каждому диску в альбоме
        volumes = client.albumsWithTracks(album_id=album['id'])['volumes']
        n_volume = 1
        for disk in volumes[:1]:
            print('Volume №: ', n_volume, "из ", len(volumes))
            n_volume += 1

            for track in disk: # проходимся по каждому треку в диске
                track_info = client.tracks_download_info(track_id=track['id'], get_direct_links=True) # узнаем информацию о треке
                print('ID: ', track['id'], track['title'],'bitrate:', track_info[1]['bitrate_in_kbps'], 'Download: ', track_info[1]['direct_link'])
                tag_info = client.tracks(track['id'])[0]
                info = {
                    'title': tag_info['title'],
                    'volume_number': tag_info['albums'][0]['track_position']['volume'],
                    'total_volumes': len(volumes),
                    'track_position': tag_info['albums'][0]['track_position']['index'],
                    'total_track': album['track_count'],
                    'genre': tag_info['albums'][0]['genre'],
                    'artist': artist_name,
                    'album_artist': [artist['name'] for artist in album['artists']],
                    'album': album['title'],
                    'album_year': album['release_date'][:10],
                }

                disk_folder = f"{album_folder}/Disk {info['volume_number']}"
                os.makedirs(os.path.dirname(f"{disk_folder}/"), exist_ok=True)
                track_file = f"{disk_folder}/{info['track_position']} - {info['title'].replace('/', '_')}.mp3"
                client.request.download(
                    url=track_info[1]['direct_link'],
                    filename=track_file
                )
                #начинаем закачивать тэги в трек
                mp3 = music_tag.load_file(track_file)
                mp3['tracktitle'] = info['title']
                if album['version'] != None:
                    mp3['album'] = info['album'] + ' ' + album['version']
                else:
                    mp3['album'] = info['album']
                mp3['discnumber'] = info['volume_number']
                mp3['totaldiscs'] = info['total_volumes']
                mp3['tracknumber'] = info['track_position']
                mp3['totaltracks'] = info['total_track']
                mp3['genre'] = info['genre']
                mp3['Year'] = info['album_year']
                if tag_info['version'] != None:
                    mp3['comment'] = f"{tag_info['version']} / Release date {info['album_year']}"
                else:
                    mp3['comment'] = f"Release date {info['album_year']}"
                mp3['artist'] = info['artist']
                mp3['album_artist'] = info['album_artist']
                mp3['lyrics'] = client.trackSupplement(178499)['lyrics']['full_lyrics']
                with open(album_cover_pic, 'rb') as img_in:               #ложим картинку в тег "artwork"
                    mp3['artwork'] = img_in.read()

                mp3.save()

type_to_name = {
    'track': 'трек',
    'artist': 'исполнитель',
    'album': 'альбом',
    'playlist': 'плейлист',
    'video': 'видео',
    'user': 'пользователь',
    'podcast': 'подкаст',
    'podcast_episode': 'эпизод подкаста',
}


def send_search_request_and_print_result(query):
    search_result = client.search(query)

    text = [f'Результаты по запросу "{query}":', '']

    best_result_text = ''
    if search_result.best:
        type_ = search_result.best.type
        best = search_result.best.result

        text.append(f'❗️Лучший результат: {type_to_name.get(type_)}')

        if type_ in ['track', 'podcast_episode']:
            artists = ''
            if best.artists:
                artists = ' - ' + ', '.join(artist.name for artist in best.artists)
            best_result_text = best.title + artists
        elif type_ == 'artist':
            best_result_text = best.name
        elif type_ in ['album', 'podcast']:
            best_result_text = best.title
        elif type_ == 'playlist':
            best_result_text = best.title
        elif type_ == 'video':
            best_result_text = f'{best.title} {best.text}'

        text.append(f'Содержимое лучшего результата: {best_result_text}\n')

    if search_result.artists:
        text.append(f'Исполнителей: {search_result.artists.total}')
    if search_result.albums:
        text.append(f'Альбомов: {search_result.albums.total}')
    if search_result.tracks:
        text.append(f'Треков: {search_result.tracks.total}')
    if search_result.playlists:
        text.append(f'Плейлистов: {search_result.playlists.total}')
    if search_result.videos:
        text.append(f'Видео: {search_result.videos.total}')

    text.append('')
    print('\n'.join(text))


if __name__ == '__main__':
    input_query = input('Введите поисковой запрос: ')
    search_and_download_artist(input_query)