from beets.library import Library
from unidecode import unidecode
from subprocess import PIPE, Popen
from beets.library import PathType
from os import path, remove
from shutil import copy2, rmtree
from inspect import getfile, currentframe
from os import listdir
from os.path import isfile, join
import os
def reset_beets():
    remove(path.expanduser('~/.config/beets/state.pickle'))

"""
#Klasa album przechowuje ['artpath'] jako objekt PathType
#PathType.format(path) konwertuje path do stringa
#Funkcja napisana aby kod był przejrzystszy
"""
def path_to_str(path):
    pathconverter = PathType()
    return pathconverter.format(path)

def get_str_paths(albums):
    str_paths = []
    for album in albums:
        str_paths.append(path_to_str(album.artpath))
    return str_paths


def get_server_path():
    serverpath = path.dirname(path.abspath(getfile(currentframe())))
    serverpath = serverpath[:-7]  # takes 'python/' away
    return serverpath


"""
Na wejściu wprowadzadź obiekt biblioteki
#Funkcja kopiuje okładki albumów do folderu ./static/images,
#a następnie nadpisuje album.artpath każdego albumu biblioteki 
#do formatu html-friendly (../static/images)
#Zwraca liste ścieżek
"""
def get_covers(albumlist):
    nonepath = '../static/images/image-not-found.jpg'
    paths = []
    imagespath = get_server_path()
    for album in albumlist:
        album_art_path = path_to_str(album.artpath)
        if path.exists(album_art_path):
            newCoverPath = "/static/images/art" + str(album.id) + ".jpg"
            if path.exists(imagespath+newCoverPath):
                remove(imagespath+newCoverPath)
            copy2(album_art_path, imagespath+newCoverPath)
            paths.append('..'+newCoverPath)
        else:
            paths.append(nonepath)
    return paths



def get_library():
    """
    #ponieważ config.yaml na różnych systemach znajduje sie w różnych miejscach,
    #lepiej wywolac beet config niz bezposrednio otwierac plik open('/home/dominik/.config/beets/config.yaml', 'r')
    """
    p = Popen(['beet','config'], stdin=PIPE, stdout=PIPE, stderr=PIPE, bufsize=1)

    for line in p.stdout:
        line = line.decode('UTF-8')[:-1]
        if "directory: " in line:
            line = line[11:]
            if not path.exists(line):			#w przypadku gdy ścieżka podana jest z użyciem '~/'
                line = path.expanduser(line)
            return line


def get_database():
    """
    #ponieważ config.yaml na różnych systemach znajduje sie w różnych miejscach,
    #lepiej wywolac beet config niz bezposrednio otwierac plik open('/home/dominik/.config/beets/config.yaml', 'r')
    """
    p = Popen(['beet','config'], stdin=PIPE, stdout=PIPE, stderr=PIPE, bufsize=1)
    for line in p.stdout:
        line = line.decode('UTF-8')[:-1]
        if "library: " in line:
            line = line[9:]
            if not path.exists(line):			#w przypadku gdy ścieżka podana jest z użyciem '~/'
                line = path.expanduser(line)
            return line

def beetImport(path='.', logs=0):
    #lista id nowo dodanych albumow
    albumsId = []
    pathname=get_library()+'/*.*'
    print(pathname)
    print("werrrrrrrrrrrrrrrrryloooooooooooooooong")
    """onlyfiles = [f for f in listdir(path) if isfile(join(path, f))]
    print(onlyfiles)
    onlydirs=[ name for name in os.listdir(path) if os.path.isdir(os.path.join(path, name)) ]
    print(onlydirs)"""

    p = Popen(['beet','import', path, '-A', '-P', '-i', 'c'], stdin=PIPE, stdout=PIPE, stderr=PIPE, bufsize=1)

    """p = Popen(['beet', 'import', path, '-Pqgs'], stdin=PIPE, stdout=PIPE, stderr=PIPE, bufsize=1)
    for line in p.stdout.readlines():
        print(line)
    p = Popen(['beet', 'import',path], stdin=PIPE, stdout=PIPE, stderr=PIPE, bufsize=1)
    for line in p.stdout.readlines():
        print(line)"""
    if logs == 1: print('wykonano import\nsciezki zaimportowanych plikow:')
    albumPath = []
    for line in p.stderr:
        #zapisywanie ścieżek albumów do listy. ścieżki typu byte
        albumPath.append(line.decode('UTF-8')[:-1])
        if logs == 1: print(line.decode('UTF-8')[:-1])
    for album in albumPath:
        #wyświetla id albumu
        a = Popen(['beet', 'list', album, '-a', '-f', '$id'], stdin=PIPE, stdout=PIPE, stderr=PIPE, bufsize=1)
        for id in a.stdout:
            albumsId.append(int(id.decode('UTF-8')[:-1]))
    if logs == 1: print(albumsId)
    return albumsId


"""
Funkcja napisana aby ułatwić HTMLowi wyświetlanie obrazu
Album.artpath przechowywane jest jako obiekt klasy PathType
pack_albums() przyjmuje jako atrybut liste albumów,
z każdego wyciąga artpath, konwertuje go do stringa i
tworzy podlisty [album,ścieżka]. Zwracana jest lista podlist.

#W przyszlosci rozbudowane zostanie o liste zdalnych repozytoriow
"""
def pack_albums(albums):
    paths = get_covers(albums)
    albums_packed = []
    for i, album in enumerate(albums):
        pack = [album, paths[i]]
        albums_packed.append(pack)
    return albums_packed


"""
To samo co pack_albums ale zwraca liste podlist [album, ścieżka, items, items_number_so_far]
"""
def pack_albums_items(albums):
    paths = get_covers(albums)
    items_packed = []
    items_count = []
    for i, album in enumerate(albums):
        items = []
        for item in album.items():
            items.append(item)
            items_count.append(item)
        pack = [album, paths[i], items, len(items_count)]
        items_packed.append(pack)

    return items_packed