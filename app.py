from flask import Flask, render_template, redirect, url_for, request
from beets.library import Library
import python.beetsCommands as beetsCommands
import python.gitAnnexLib as gitAnnexLib
import python.dictionary as dictionary
import os
from formencode import variabledecode



app = Flask(__name__)


@app.route("/")
def main():
    return redirect(url_for('albumy'))


@app.route('/details', methods = ['GET', 'POST'])
def details():
    polish = dictionary.polish()
    dict = dictionary.dictionary(polish)
    albums_id = request.args.getlist('id',type=int)
    action = request.args.getlist('action', type=str)
    expand = request.args.get('expand', type=str)
    saved = request.args.get('remotes', type=str)
    albums = []
    id_arg = ''
    local_repo.get_remotes()
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
    print(remote_names)
    remotes_send = []
    for album_id in albums_id:
        if id_arg != '':
            id_arg = id_arg + '&'
        id_arg = id_arg+'id='+str(album_id)
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
    print(remote_names_copy)
    remotes_send.append(remote_names_copy)

    details = beetsCommands.pack_albums_items(albums)

    if expand == 'true':
        if 'edit' in action:
            return edit_data(id_arg, dict, expand)
        else:
            return render_template('expandeddetails.html', details=details, dictionary=dict, id_arg=id_arg, expanded=expand, remotes=remotes_send)

    polish_short = dictionary.PolishShort()
    dict_short = dictionary.dictionary(polish_short)
    if 'edit' in action:
        return edit_data(id_arg, dict_short, expand, remotes_send)


    return render_template('expandeddetails.html', details=details, dictionary=dict_short, id_arg=id_arg, expanded=expand, remotes=remotes_send)


def edit_data(id_arg, dict, expand, remotes_send):
    if request.method == 'POST':

        postvars = variabledecode.variable_decode(request.form, dict_char='_')

        albums_id = []
        items_id = []
        albums_newdata = []
        items_newdata = []
        items_id_grouped = []       #used to help count number of items
        album_keys_number = len(dict.language_album)
        item_keys_number = len(dict.language_item)

        while (len(albums_id)*album_keys_number+len(items_id_grouped)*item_keys_number) != len(postvars):
            albums_number = len(albums_id)

            album_keys_number = len(dict.language_album)
            item_keys_number = len(dict.language_item)
            current_len = albums_number * album_keys_number + len(items_id_grouped) * item_keys_number
            album_newdata = []
            for k in range(0, album_keys_number):
                album_newdata.append(postvars.get(str(current_len + k)))
            albums_newdata.append(album_newdata)
            albums_id.append(int(album_newdata[-1]))
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
                    item_newdata.append(postvars.get(str(albums_number * album_keys_number + (len(items_id_grouped)-len(album_items_id)) * item_keys_number + album_keys_number + k * item_keys_number + j)))

                album_items_newdata.append(item_newdata)
            items_newdata.append(album_items_newdata)

        local_repo.annex_direct()                               # git annex direct mode, so beet can modify files

        albums = []
        items = []
        for a, album_id in enumerate(albums_id):
            albums.append(lib.get_album(album_id))              # getting single album
            for k in range(len(dict.language_album)):
                album_key = dict.album_keys[k]
                if album_key == 'id' or album_key == 'artpath':
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
                if k == 1:
                    print(item[item_key])
            albums[a].try_sync(write=True,move=False)
        local_repo.annex_indirect()                                     # commits changes and goes back to indirect mode


        details = beetsCommands.pack_albums_items(albums)

        return render_template('expandeddetails.html', details=details, dictionary=dict, id_arg=id_arg, expanded=expand, remotes=remotes_send)

@app.route("/import")
def get_import_path():
    return render_template('import.html')


@app.route('/startImporting', methods=['POST'])
def startImporting():
    if request.method == 'POST':
        path = request.form['Path']
        import_to_beets(path, first=1)

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

@app.route('/repositories', methods=['POST', 'GET'])
def repositories():
    local_repo.get_remotes()
    action = request.args.get('action', type=str)

    if request.method == 'POST':
        postvars = variabledecode.variable_decode(request.form, dict_char='_')
        repositories_action(postvars)                               #get, send, change settings

        path = request.form['path']
        path = os.path.expanduser(path)
        name = request.form['remote_name']
        if path and name:
            return repositories_add_remote(path, name)


    repos_packed = pack_remotes(local_repo)

    return render_template('newrepository.html', local_repo=local_repo, repos_packed=repos_packed)


def repositories_action(postvars):
    remember_get, get, remember_send, send, drop = ([] for i in range(5))

    for key in postvars:
        if str(postvars.get(key)) == 'remember':
            key = str(key)
            if key[-1] == 'g':
                remember_get.append((key[:-1]))
            elif key[-1] == 's':
                remember_send.append(key[:-1])
        elif str(postvars.get(key)) == 'Pobierz':
            get.append(str(key))
        elif str(postvars.get(key)) == 'Wyślij':
            send.append(str(key))
        elif str(postvars.get(key)) == 'Wyczyść':
            drop.append(str(key))
            print('--------------------', drop)
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
            repo.get_from(local_repo)
            import_to_beets(local_repo.path, first=1)
        if repo.name in get:
            local_repo.get_from(repo)
            import_to_beets(local_repo.path, first=1)
        if repo.name in drop:
            local_repo.annex_sync(repo)
            repo.annex_sync(local_repo)
            repo.annex_drop()
            repo.annex_sync(local_repo)
            local_repo.annex_sync(repo)

def repositories_add_remote(path, name):
    warning = []
    # validation

    if not os.path.exists(path):
        warning.append('Ścieżka musi wskazywać na istniejący folder')
    if name in local_repo.remote_names:
        if warning == []:
            warning.append([])
        warning.append('Nazwa musi być unikalna')

    if warning == []:
        gitAnnexLib.create_repository(local_repo, path, name)

    repos_packed = pack_remotes(local_repo)

    return render_template('newrepository.html', warning=warning, local_repo=local_repo, repos_packed=repos_packed)



def pack_remotes(repository):

    repo_fullsync = []
    repo_autoget = []
    repo_autopush = []
    repo_manual = []
    for repo in repository.remotes:
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
    alb_sort_album = beetsCommands.pack_albums_items(sorted(albums, key=lambda x: x.album))
    alb_sort_artist = beetsCommands.pack_albums_items(sorted(albums, key=lambda x: x.albumartist))
    alb_sort_year = beetsCommands.pack_albums_items(sorted(albums, key=lambda x: x.year))


    return render_template('albums.html',albums=alb_sort_album, artists=alb_sort_artist, years=alb_sort_year)

@app.route("/artists")
def artysci():
    return render_template('artists.html')

@app.route("/songs")
def muzyka():
    return render_template('songs.html')




if __name__ == "__main__":
    print(beetsCommands.get_library())
    local_repo = gitAnnexLib.Repo(path=beetsCommands.get_library(), local=1)
    lib = Library(beetsCommands.get_database())
    import_to_beets(local_repo.path, first=1)
    for autopush in local_repo.autopushing:
        autopush.get_from(local_repo)
    for autoget in local_repo.autogetting:
        local_repo.get_from(autoget)

    app.run(debug=True, use_reloader=True)
