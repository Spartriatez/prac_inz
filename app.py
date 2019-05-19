import os
import shutil
from subprocess import Popen, PIPE

from beets.library import Library
from flask import Flask, render_template, redirect, url_for, request, session

from formencode import variabledecode

import python.beetsCommands as beetsCommands
import python.dictionary as dictionary
import python.gitAnnexLib as gitAnnexLib
from python.gitAnnexLib import get_backup
import tkinter as tk
from tkinter import filedialog
from tkinter import ttk
from os import listdir
from os.path import isfile, join

from python.sshPath import Ssh, check_exist_ssh,split_data

app = Flask(__name__)
app.config.from_object(__name__)
app.secret_key = 'xyz'

color = 'black'


@app.route("/")
def main():
    return redirect(url_for('albumy'))


@app.route('/details', methods=['GET', 'POST'])
def details():
    polish = dictionary.polish()
    dict = dictionary.dictionary(polish)
    albums_id = request.args.getlist('id', type=int)
    action = request.args.getlist('action', type=str)
    expand = request.args.get('expand', type=str)
    saved = request.args.get('remotes', type=str)
    albums = []
    id_arg = ''
    local_repo.get_remotes()
    print("example" + str(local_repo.get_remotes()))
    if saved == 'saved':
        if request.method == 'POST':
            for album_id in albums_id:
                album_dir = beetsCommands.path_to_str(lib.get_album(album_id).item_dir())
                album_dir = album_dir[len(beetsCommands.get_library()) + 1:]
                postvars = variabledecode.variable_decode(request.form, dict_char='_')
                keys = postvars.keys()
                for repo in local_repo.remotes:
                    if repo.name not in keys:
                        local_repo.annex_sync(repo)
                        repo.annex_sync(local_repo)
                        repo.annex_drop(album_dir)
                        repo.annex_sync(local_repo)
                        local_repo.annex_sync(repo)
                    else:
                        local_repo.annex_sync(repo)
                        repo.annex_sync(local_repo)
                        repo.annex_get(local_repo, album_dir)
                        repo.annex_sync(local_repo)
                        local_repo.annex_sync(repo)

                if 'YAMO' not in postvars.keys():
                    local_repo.annex_drop(album_dir)
                else:
                    local_repo.annex_get_from_all(album_dir)

    remote_names = local_repo.remote_names
    remotes_send = []
    for album_id in albums_id:
        if id_arg != '':
            id_arg = id_arg + '&'
        id_arg = id_arg + 'id=' + str(album_id)
        albums.append(lib.get_album(album_id))
        items = albums[-1].items()
        album_dir = beetsCommands.path_to_str(beetsCommands.path_to_str(items[0].path))
        if album_dir:
            album_dir = album_dir[len(beetsCommands.get_library()) + 1:]
            remotes_send.append(local_repo.annex_whereis(album_dir))

    if 'YAMO' not in remote_names:
        remote_names.append('YAMO')

    remote_names_copy = []
    for name in remote_names:
        if name not in remotes_send[0]:
            remote_names_copy.append(name)
    remotes_send.append(remote_names_copy)

    local_repo.annex_direct()
    details = beetsCommands.pack_albums_items(albums)
    local_repo.annex_indirect()

    if expand == 'true':
        if 'edit' in action:
            return edit_data(id_arg, dict, expand, remotes_send)
        else:
            return render_template('expandeddetails.html', details=details, dictionary=dict, id_arg=id_arg,
                                   expanded=expand, remotes=remotes_send)

    polish_short = dictionary.PolishShort()
    dict_short = dictionary.dictionary(polish_short)
    if 'edit' in action:
        return edit_data(id_arg, dict_short, expand, remotes_send)
    print(remotes_send)

    return render_template('expandeddetails.html', details=details, dictionary=dict_short, id_arg=id_arg,
                           expanded=expand, remotes=remotes_send)


def edit_data(id_arg, dict, expand, remotes_send):
    if request.method == 'POST':

        postvars = variabledecode.variable_decode(request.form, dict_char='_')
        albums_id = []
        items_id = []
        albums_newdata = []
        items_newdata = []
        items_id_grouped = []  # used to help count number of items
        album_keys_number = len(dict.language_album)
        item_keys_number = len(dict.language_item)
        while (len(albums_id) * album_keys_number + len(items_id_grouped) * item_keys_number) != len(postvars):
            albums_number = len(albums_id)
            album_keys_number = len(dict.language_album)
            item_keys_number = len(dict.language_item)
            current_len = albums_number * album_keys_number + len(items_id_grouped) * item_keys_number
            album_newdata = []
            for k in range(0, album_keys_number):
                album_newdata.append(postvars.get(str(current_len + k)))
            albums_newdata.append(album_newdata)
            albums_id.append(int(album_newdata[6]))
            album = lib.get_album(albums_id[-1])

            album_items_id = []
            for item in album.items():
                album_items_id.append(item.id)
                items_id_grouped.append(item.id)
            items_id.append(album_items_id)
            album_items_newdata = []
            for k in range(0, len(album_items_id)):
                item_newdata = []
                for j in range(0, item_keys_number):
                    item_newdata.append(postvars.get(str(albums_number * album_keys_number + (
                            len(items_id_grouped) - len(
                        album_items_id)) * item_keys_number + album_keys_number + k * item_keys_number + j)))

                album_items_newdata.append(item_newdata)
            items_newdata.append(album_items_newdata)
        local_repo.annex_direct()  # git annex direct mode, so beet can modify files

        albums = []
        items = []
        for a, album_id in enumerate(albums_id):
            albums.append(lib.get_album(album_id))  # getting single album
            for k in range(len(dict.language_album)):
                album_key = dict.album_keys[k]
                if albums[a][album_key] == None:
                    pass
                elif album_key == 'id' or album_key == 'artpath':
                    pass
                elif album_key == 'year':
                    if int(albums_newdata[a][k]) < 10000:
                        albums[a][album_key] = int(albums_newdata[a][k])
                    else:
                        pass

                else:
                    albums[a][album_key] = str(albums_newdata[a][k])

            for i, item_id in enumerate(items_id[a]):
                item = lib.get_item(item_id)
                items.append(item)
                for k in range(len(dict.language_item)):
                    item_key = dict.item_keys[k]
                    if item_key == 'id' or item_key == 'path':
                        pass
                    elif item_key == 'album_id':
                        if int(items_newdata[a][i][k]) in albums_id:
                            item[item_key] = int(items_newdata[a][i][k])
                        else:
                            pass
                    elif item_key == 'disc' or item_key == 'track':
                        if int(items_newdata[a][i][k]) < 100:
                            item[item_key] = int(items_newdata[a][i][k])
                        else:
                            pass
                    else:
                        item[item_key] = str(items_newdata[a][i][k])
                        item['comments'] = 'edited'
                item.try_sync(write=1, move=0)
            albums[a].try_sync(write=True, move=False)
        local_repo.annex_indirect()  # commits changes and goes back to indirect mode

        local_repo.annex_direct()
        details = beetsCommands.pack_albums_items(albums)
        local_repo.annex_indirect()

        return render_template('expandeddetails.html', details=details, dictionary=dict, id_arg=id_arg, expanded=expand,
                               remotes=remotes_send)


@app.route("/import")
def get_import_path():
    return render_template('import.html')


"""
@app.route('/startImporting', methods=['POST'])
def startImporting():
    if request.method == 'POST':
        path = request.form['Path']
        import_to_beets(path, first=1)
        return redirect('/albums')
"""


@app.route('/startImporting')
def startImporting():
    w = tk.Tk()
    w.option_add('*foreground', color)  # set all tk widgets' foreground to red
    w.option_add('*activeForeground', color)  # set all tk widgets' foreground to red

    style = ttk.Style(w)
    style.configure('TLabel', foreground=color)
    style.configure('TEntry', foreground=color)
    style.configure('TMenubutton', foreground=color)
    style.configure('TButton', foreground=color)
    file_path = filedialog.askopenfilename(parent=w, filetypes=(
        ("pliki mp3", "*.mp3"), ("pliki wav", "*.wav"), ("pliki flac", "*.flac"), ("pliki wma", "*.wma"),
        ("pliki ogg", "*.ogg")))

    w.after(0, lambda: w.destroy())  # Destroy the widget after 30 seconds
    w.mainloop()
    if file_path:
        import_to_beets(file_path, first=1)

    return redirect('/albums')


def import_to_beets(path, first=0):
    local_repo.annex_direct()
    albums_id = beetsCommands.beetImport(path)

    paths_in_repo = []
    for album_id in albums_id:
        album = lib.get_album(album_id)
        albumpath = beetsCommands.path_to_str(album.item_dir())
        paths_in_repo.append(albumpath[len(local_repo.path) + 1:])
        if first == 1:
            for item in album.items():
                item.comments = 'unedited'
                item.write()
            album.store()
            album.load()
    local_repo.annex_indirect()
    for path in paths_in_repo:
        local_repo.annex_add(path)

ssh_path=''
host=''
username=''
dirs=[]
@app.route('/sshActions', methods=['POST', 'GET'])
def sshActions():
    global host, username, ssh_path,dirs
    if request.method == 'POST':
        password = []
        host = request.form['hostname']
        username = request.form['username']
        if ssh_path == '':
            connection = Ssh(host, username, password)
            ssh_path=connection.send_path("pwd")
            connection = Ssh(host, username, password)
            folders = connection.sendCommand("ls -d */")
            folders=folders[:-1]
        return render_template('sshActions.html', folders=folders,ssh_path=ssh_path)
    else:
        print(ssh_path+" "+host+" "+username)
        password = []
        req=request.args.get('dirname')
        if req!= '..':
            dirs.append(request.args.get('dirname'))
            path='/'.join(dirs)
        else:
            if len(dirs)>0:
                del dirs[-1]
                path = '/'.join(dirs)
            else:
                path='.'
        connection = Ssh(host, username, password)
        command="cd "+path+" && ls -d */"
        folders = connection.sendCommand(command)
        folders = folders[:-1]
        return render_template('sshActions.html', folders=folders,ssh_path=ssh_path+"/"+path)


@app.route('/repositories', methods=['POST', 'GET'])
def repositories():
    local_repo.get_remotes()
    global ssh_path
    if request.method == 'POST':
        postvars = variabledecode.variable_decode(request.form, dict_char=',')
        """print(request.form)
        print(postvars)
        repositories_action(postvars)  # get, send, change settings"""

        path = request.form['path']
        path = os.path.expanduser(path)
        name = request.form['remote_name']
        if path and name:
            return repositories_add_remote(path, name)

    repos_packed = pack_remotes(local_repo)

    return render_template('newrepository.html', local_repo=local_repo, repos_packed=repos_packed)

@app.route('/repositories2', methods=['POST', 'GET'])
def repositories2():
    local_repo.get_remotes()
    global ssh_path
    if request.method == 'POST':
        postvars = variabledecode.variable_decode(request.form, dict_char=',')
        repositories_action(postvars)  # get, send, change setting

    repos_packed = pack_remotes(local_repo)

    return render_template('newrepository.html', local_repo=local_repo, repos_packed=repos_packed)

@app.route('/returnPathname')
def returnPathname():
    w = tk.Tk()
    w.option_add('*foreground', color)  # set all tk widgets' foreground to red
    w.option_add('*activeForeground', color)  # set all tk widgets' foreground to red

    style = ttk.Style(w)
    style.configure('TLabel', foreground=color)
    style.configure('TEntry', foreground=color)
    style.configure('TMenubutton', foreground=color)
    style.configure('TButton', foreground=color)
    directory_path = filedialog.askdirectory()
    w.after(0, lambda: w.destroy())  # Destroy the widget after 30 seconds
    w.mainloop()
    local_repo.get_remotes()
    repos_packed = pack_remotes(local_repo)

    return render_template('newrepository.html', directory_path=directory_path, local_repo=local_repo,
                           repos_packed=repos_packed)

@app.route('/returnSshPathname')
def returnSshPathname():
    global host, username, ssh_path, dirs
    path='/'.join(dirs)
    ssh_directory='ssh://'+username+"@"+host+ssh_path+"/"+path
    local_repo.get_remotes()
    repos_packed = pack_remotes(local_repo)
    return render_template('newrepository.html', directory_path=ssh_directory, local_repo=local_repo,
                           repos_packed=repos_packed)


def repositories_action(postvars):
    remember_get, get, remember_send, send, drop = ([] for i in range(5))
    path_get,path_send,path_drop=([] for i in range(3))
    print(postvars)
    for key in postvars:
        print(key)
        if str(postvars.get(key)) == 'remember':
            key = str(key)
            if key[-1] == 'g':
                remember_get.append((key[:-1]))
            elif key[-1] == 's':
                remember_send.append(key[:-1])
        elif str(postvars.get(key)) == 'Pobierz':
            tmp=str(key)
            tmp=tmp.split('-')
            get.append(tmp[0])
            path_get.append(tmp[1])
        elif str(postvars.get(key)) == 'Wyślij':
            tmp = str(key)
            tmp = tmp.split('-')
            send.append(tmp[0])
            path_send.append(tmp[1])
        elif str(postvars.get(key)) == 'Wyczyść':
            tmp = str(key)
            tmp = tmp.split('-')
            drop.append(tmp[0])
            path_drop.append(tmp[1])

    for repo in local_repo.remotes:
        if repo.name in remember_get:
            local_repo.add_autogetting(repo)
        else:
            local_repo.drop_autogetting(repo)
        if repo.name in remember_send:
            local_repo.add_autopushing(repo)
        else:
            local_repo.drop_autopushing(repo)

        if repo.name in send:
            path = ''
            for i in range(len(send)):
                if (repo.name == send[i]):
                    path = path_send[i]
            check = path.split('://')
            if (check[0] == 'ssh'):
                username, host, path = split_data(path)
                local_repo.annex_sync(repo)
                repo.get_ssh_from_v2(username, host, path,local_repo)
                repo.annex_ssh_sync(username, host, path,local_repo)
                local_repo.annex_sync(repo)
                local_repo.annex_direct()
                import_to_beets(local_repo.path, first=1)
                get_backup(local_repo.path)
                local_repo.annex_indirect()
            else:
                local_repo.annex_sync(repo)
                repo.get_from(local_repo)
                repo.annex_sync(local_repo)
                local_repo.annex_sync(repo)
                local_repo.annex_direct()
                import_to_beets(local_repo.path, first=1)
                get_backup(local_repo.path)
                local_repo.annex_indirect()

        if repo.name in get:
            path=''
            for i in range(len(get)):
                if(repo.name==get[i]):
                    path=path_get[i]
            check=path.split('://')
            if(check[0]=='ssh'):
                username, host, path = split_data(path)
                repo.annex_ssh_sync(username,host,path,local_repo)
                local_repo.annex_sync(repo)
                local_repo.get_ssh_from(username,host,path,repo)
                local_repo.annex_sync(repo)
                local_repo.annex_direct()
                get_backup(local_repo.path)
                import_to_beets(local_repo.path, first=1)
                get_backup(local_repo.path)
                local_repo.annex_indirect()
            else:
                repo.annex_sync(local_repo)
                local_repo.annex_sync(repo)
                local_repo.get_from(repo)
                local_repo.annex_sync(repo)
                local_repo.annex_direct()
                import_to_beets(local_repo.path, first=1)
                get_backup(local_repo.path)
                local_repo.annex_indirect()

        if repo.name in drop:
            path = ''
            for i in range(len(drop)):
                if (repo.name == drop[i]):
                    path = path_drop[i]
            check = path.split('://')
            if (check[0] == 'ssh'):
                username, host, path = split_data(path)
                local_repo.annex_sync(repo)
                repo.annex_ssh_sync(username, host, path ,local_repo)
                repo.annex_ssh_drop(username, host, path)
                repo.annex_ssh_sync(username, host, path, local_repo)
                local_repo.annex_sync(repo)
            else:
                local_repo.annex_sync(repo)
                repo.annex_sync(local_repo)
                repo.annex_drop()
                repo.annex_sync(local_repo)
                local_repo.annex_sync(repo)


def repositories_add_remote(path, name):
    warning = []
    # validation
    if(check_exist_ssh(path)==1):
        if name in local_repo.remote_names:
            if warning == []:
                warning.append([])
            warning.append('Nazwa musi być unikalna')

        if warning == []:
            gitAnnexLib.create_repository(local_repo, path, name,1)
        global ssh_path,host,username,dirs
        ssh_path=''
        host=''
        username=''
        dirs=[]
    else:
        if not os.path.exists(path):
            warning.append('Ścieżka musi wskazywać na istniejący folder')
        if name in local_repo.remote_names:
            if warning == []:
                warning.append([])
            warning.append('Nazwa musi być unikalna')

        if warning == []:
            gitAnnexLib.create_repository(local_repo, path, name,0)

    repos_packed = pack_remotes(local_repo)

    return render_template('newrepository.html', warning=warning, local_repo=local_repo, repos_packed=repos_packed)


def pack_remotes(repository):
    repo_fullsync = []
    repo_autoget = []
    repo_autopush = []
    repo_manual = []
    print("repo remotes")
    print(repository.remotes)
    for repo in repository.remotes:
        print("repository autogetting")
        print(repository.autogetting)
        print("localrepo autopusshing")
        print(local_repo.autopushing)
        if repo in repository.autogetting and repo in local_repo.autopushing:
            repo_fullsync.append(repo)
        elif repo in repository.autogetting:
            repo_autoget.append(repo)
        elif repo in repository.autopushing:
            repo_autopush.append(repo)
        else:
            repo_manual.append(repo)

    repos_packed = [repo_manual, repo_autoget, repo_autopush, repo_fullsync]
    return repos_packed

@app.route("/deleteAlbum",methods=['POST', 'GET'])
def deleteAlbum():
    print("deleted")
    album=request.form['album']
    artist=request.form['artist']
    if(album!=''):
        p = Popen(['beet','remove','-a', album], stdin=PIPE, stdout=PIPE, stderr=PIPE, bufsize=1)
        for line in p.stderr:
            print(line.decode('UTF-8')[-1])
        onlyfiles = [f for f in listdir(beetsCommands.get_library())]
        for dirn in onlyfiles:
            if artist in dirn:
                shutil.rmtree(beetsCommands.get_library()+'/'+dirn)
        print("artist"+artist)

    else:
        print("fdfd")
        p = Popen(['beet', 'remove', artist], stdin=PIPE, stdout=PIPE, stderr=PIPE, bufsize=1)
        for line in p.stderr:
            print(line.decode('UTF-8')[-1])
        onlyfiles = [f for f in listdir(beetsCommands.get_library())]
        for dirn in onlyfiles:
            if artist in dirn:
                shutil.rmtree(beetsCommands.get_library() + '/' + dirn)
    return redirect('/albums')

@app.route("/reset")
def reset_database():
    try:
        beetsCommands.reset_beets()

    except:
        warning = 'Reseting database failed. Please remove "~/.config/beets/state.pickle" manualy'
        return render_template('reset.html', warning)
    import_to_beets(local_repo)
    return redirect('/albums')


@app.route("/albums")
def albumy():
    albums = lib.albums()
    for album in albums:
        album.load()
    local_repo.annex_direct()
    alb_sort_album = beetsCommands.pack_albums_items(sorted(albums, key=lambda x: x.album))
    alb_sort_artist = beetsCommands.pack_albums_items(sorted(albums, key=lambda x: x.albumartist))
    alb_sort_year = beetsCommands.pack_albums_items(sorted(albums, key=lambda x: x.year))
    local_repo.annex_indirect()
    return render_template('albums.html', reload="no", albums=alb_sort_album, artists=alb_sort_artist,
                           years=alb_sort_year)

@app.route("/rBackup")
def rBackup():
    gitAnnexLib.from_backup(beetsCommands.get_library())
    return redirect('/albums')


@app.route("/artists")
def artysci():
    return render_template('artists.html')


@app.route("/songs")
def muzyka():
    return render_template('songs.html')


local_repo = gitAnnexLib.Repo(path=beetsCommands.get_library(), local=1)
lib = Library(beetsCommands.get_database())
local_repo.annex_direct()
get_backup(local_repo.path)
import_to_beets(local_repo.path, first=1)
get_backup(local_repo.path)
local_repo.annex_indirect()
#print("local repo autopushing  sdsdfsdfdsfdsfsdfs")
#print(local_repo.autopushing)
for autopush in local_repo.autopushing:
    autopush.get_from(local_repo)
#print("local repo autogetting  sdsdfsdfdsfdsfsdfs")
#print(local_repo.autogetting)
for autoget in local_repo.autogetting:
    local_repo.get_from(autoget)

if __name__ == "__main__":
    app.run(debug=True, use_reloader=True)
