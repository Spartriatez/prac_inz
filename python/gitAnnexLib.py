from subprocess import PIPE, Popen, check_output
import python.beetsCommands as beetsCommands


autopush_log = beetsCommands.get_server_path()+'/static/remote_repos/autopush'

autoget_log = beetsCommands.get_server_path()+'/static/remote_repos/autoget'


class Repo:

    def __init__(self, name='YAMO_local', path='.', local=0, logs = 1):
        self.name = name
        self.path = path
        self.logs = logs
        self.remotes = []
        self.remote_names = []
        self.autogetting = []
        self.autopushing = []
        if local == 1:
            self.annex_init()
            self.get_remotes()




    def get_names(self):
        for remote in self.remotes:
            if remote.name not in self.remote_names:
                self.remote_names.append(remote.name)
        return self.remote_names



    """
    Wywołuje git remote w lokalizacji self.path aby pobrać listę zdalnych repozytoriów.
    """
    def get_remotes(self):


        p = Popen(['git', 'remote', '-v'], cwd=self.path, stdin=PIPE, stdout=PIPE, stderr=PIPE, bufsize=1)
        remote_names = []
        remote_paths = []
        autopushing_names = self.get_autopushing_names()
        autogetting_names = self.get_autogetting_names()
        for remote in p.stdout:
            remote_str = remote.decode('UTF-8')[:-1]
            find_tab = remote_str.find('\t')
            if find_tab:
                remote_name = (remote_str[:find_tab])
                if remote_name not in remote_names:
                    remote_names.append(remote_name)
                    find_bracket = remote_str.rfind('(')
                    if find_bracket:
                        remote_paths.append(remote_str[find_tab+1:find_bracket-1])

        current_remotes = self.get_names()
        print(current_remotes, '------current remotes------------')
        for i, remote_name in enumerate(remote_names):
            if remote_name not in current_remotes:
                new_remote = Repo(remote_names[i], remote_paths[i])
                self.remotes.append(new_remote)
                current_remotes.append(remote_name)
                if remote_name in autopushing_names:
                    self.autopushing.append(new_remote)
                if remote_name in autogetting_names:
                    self.autogetting.append(new_remote)

        return self.remotes

    """
    Wywołanie git init <ścieżka>
    0-repo initialized, 0-repo reinitialized, 1-fail
    """
    def init(self):
        cmdAnswer = check_output(['git','init', self.path]).decode('UTF-8')
        if cmdAnswer[:32] == 'Initialized empty Git repository':
            if self.logs == 1: print('Repository initialized')
            return 0
        elif cmdAnswer[:37] == 'Reinitialized existing Git repository':
            if self.logs == 1: print('Repository reinitialized')
            return 0
        else:
            if self.logs == 1: print('Initialization failed')
            return 1

    """
    Wywołanie git annex init <ścieżka>
    0-repo initialized, 1-fail
    """
    def annex_init(self):
        self.init()
        p = Popen(['git', 'annex', 'init', self.path], cwd=self.path, stdin=PIPE, stdout=PIPE, stderr=PIPE, bufsize=1)
        for line in p.stdout:
            line = line.decode('UTF-8')[:-1]
            if "ok" in line:
                if self.logs == 1:
                    print('Annex repository initialized')
                    return 0
            else: print(line)
        if self.logs == 1:
            print('Annex initialization failed')
        return 1

    """
    Dodanie nowego repozytorium. 
    Funkcja wywołuje git remote add <name> <path> w lokalizacji, w której znajduje się repozytorium self.
    0 - success. 1 - fail
    """
    def remote_add(self, object):
        name = object.name
        if name not in self.remote_names:
            p = Popen(['git','remote', 'add', name, object.path], cwd=self.path, stdin=PIPE, stdout=PIPE, stderr=PIPE, bufsize=1)
            cmdErr = p.stderr.readline().decode('UTF-8')
            cmdAnswer = p.stdout.readline().decode('UTF-8')
            if (cmdAnswer[:-1] == '') & (cmdErr == ''):
                print('Remote added')
                self.remotes.append(object)
                self.remote_names.append(name)
                return 0
        return 1


    """
    Dwustronne łączenie repozytoriów.
    remoteName - nazwa repozytorium zdalnego w repozytorium lokalnym (self)
    localName - nazwa repozytorium lokalnego w repozytorium zdalnym
    0 - succes, 1 - fail
    """
    def connect_remotes(self, object):
        if (self.remote_add(object)) or (object.remote_add(self)):
            if self.logs == 1:
                print('connecting failed')
            return 1
        else:
            return 0


    #Wywołanie git annex add <path> w lokalizacji self.path.
    #Zwraca listę dodanych plików
    #@TODO dodawanie kilku plikow naraz

    def annex_add(self, path='.'):
        print('git annex add '+path)
        addedFiles = []
        p = Popen(['git','annex', 'add', path], cwd=self.path, stdin=PIPE, stdout=PIPE, stderr=PIPE, bufsize=1)
        for line in p.stdout:
            cmdAnswer = line.decode('UTF-8')[:-1]
            print(cmdAnswer)
            if cmdAnswer == '(recording state in git...)':
                if self.logs == 1: print(len(addedFiles),'files added')
                break
            else:
                addedFiles.append(cmdAnswer[4:-3])
        print()
        return addedFiles


    def commit(self, message='adding files', path='.'):
        p = Popen(['git','commit', path, '-m', message], cwd=self.path, stdin=PIPE, stdout=PIPE, stderr=PIPE, bufsize=1)
        if p.stderr.readline().decode('UTF-8')[:-1] =='ok':
            if self.logs == 1: print('commiting: '+p.stdout.readline().decode('UTF-8')[:-1])
            return 0
        else:
            if self.logs == 1: print('commiting failed')
            return 1



    """
    #Wywołuje git annex whereis <path>, czyli
    #szuka repozytoriów, w których występuje plik <path>
    #zwraca liste repozytoriow, lub 0 gdy nie znaleziono pliku
    ##sciezka skracana jest o sciezke repozytorium
    """
    def annex_whereis(self, path):
        remotes = []
        containsPath = path.find(self.path)
        if containsPath>=0:
            path = path[len(self.path)+1:]

        p = Popen(['git','annex', 'whereis', path], cwd=self.path, stdin=PIPE, stdout=PIPE, stderr=PIPE, bufsize=1)
        p.stdout.readline()
        for cmdAnswer in p.stdout:
            cmdAnswer = cmdAnswer.decode('UTF-8')[:-1]
            index = cmdAnswer.rfind('[')
            index2 = cmdAnswer.rfind(']')
            if index>0 and index2>0:
                remote = cmdAnswer[index+1:index2]
                if remote == 'here':
                    remote = ('YAMO')
                if remote not in remotes:
                    remotes.append(remote)

        return remotes

    """
    #Wywołuje git annex sync w self.path
    #0 - no errors, 1 - error
    """
    def annex_sync(self, remote):
        print('git annex sync '+remote.name)
        p = Popen(['git','annex', 'sync', remote.name], cwd=self.path, stdin=PIPE, stdout=PIPE, stderr=PIPE, bufsize=1)

        # for line in p.stderr:
        #     print(line.decode('UTF-8')[:-1])
        # print()
        return 0

    """
    Wywołuje git annex get w celu pobrania plikow ktore nie znajduja sie w repozytorium
    #1 - brak bledu, lub 0 - blad
    #@TODO zwracanie listy plikow
    """
    def annex_get(self, source, path='.'):
        print('git annex get -f '+source.name+' '+path)
        print(self.path, '-------------salefpath-')
        p = Popen(['git', 'annex', 'get', '-f', source.name, path], cwd=self.path, stdin=PIPE, stdout=PIPE, stderr=PIPE)

        for line in p.stderr:
            print(line.decode('UTF-8')[-1])
        for line in p.stdout:
            print(line)
        print('getting finished')

    def annex_get_from_all(self, path='.'):
        print('git annex get  '+path)
        print(self.path, '-------------salefpath-')
        p = Popen(['git', 'annex', 'get', path], cwd=self.path, stdin=PIPE, stdout=PIPE, stderr=PIPE)

        for line in p.stderr:
            print(line.decode('UTF-8')[-1])
        for line in p.stdout:
            print(line)
        print('getting finished')



    def annex_drop(self, path='.'):
        print('git annex drop', path)
        p = Popen(['git', 'annex', 'drop', path], cwd=self.path, stdin=PIPE, stdout=PIPE, stderr=PIPE)

        for line in p.stderr:
            print(line.decode('UTF-8')[:-1])
        for line in p.stdout:
            line = line.decode('UTF-8')[:-1]
            if line[0:6] == 'failed':
                return 1
        print('getting finished')
        return 0

    """
    #return w przypadku ponizszych 3 funkcji zostanie dopisany w razie potrzeby
    """

    def annex_unlock(self, path='.'):
        p = Popen(['git', 'annex', 'unlock', path], cwd=self.path, stdin=PIPE, stdout=PIPE, stderr=PIPE, bufsize=1)

    def annex_direct(self):
        p = Popen(['git', 'annex', 'direct'], cwd=self.path, stdin=PIPE, stdout=PIPE, stderr=PIPE, bufsize=1)
        # for line in p.stdout:
        #     line = line.decode('UTF-8')[:-1]
        #     print(line)
        # for line in p.stderr:
        #     line = line.decode('UTF-8')[:-1]
        #     print(line)

    def annex_indirect(self):
        p = Popen(['git', 'annex', 'indirect'], cwd=self.path, stdin=PIPE, stdout=PIPE, stderr=PIPE, bufsize=1)
        # for line in p.stdout:
        #     line = line.decode('UTF-8')[:-1]
        #     print(line)
        # for line in p.stderr:
        #     line = line.decode('UTF-8')[:-1]
        #     print(line)

    def get_autopushing_names(self):
        names = []
        try:
            f = open(autopush_log, mode='r')
            for remotename in f:
                remotename = remotename[:-1]
                if remotename != '':
                    if remotename not in self.autopushing:
                        names.append(str(remotename))
            f.close()
            return names
        except:
            return []


    def drop_autopushing(self, repo):
        try:
            old = open(autopush_log, mode='r')
            new = open(autopush_log, mode='w')
            for line in old:
                if line != repo.name+'\n':
                    new.write(line)
            old.close()
            new.close()
            self.autopushing.remove(repo)
            return 0
        except:
            return 1
        self.autopushing.remove(repo)


    def add_autopushing(self, repo):
        if repo not in self.autopushing:
            try:
                f = open(autopush_log, mode='a+')
                f.write(repo.name+'\n')
                f.close()
                self.autopushing.append(repo)
                return 0
            except:
                return 1



    def drop_autogetting(self, repo):
        try:
            old = open(autoget_log, mode='r')
            new = open(autoget_log, mode='w')
            for line in old:
                if line != repo.name+'\n':
                    new.write(line)
            old.close()
            new.close()
            self.autogetting.remove(repo)
            return 0
        except:
            return 1
        self.autogetting.remove(repo)


    def get_autogetting_names(self):
        names = []
        try:
            f = open(autoget_log, mode='r')
            for remotename in f:
                remotename = remotename[:-1]
                if remotename != '':
                    if remotename not in self.autopushing:
                        names.append(str(remotename))
            f.close()
            return names
        except:
            return []


    def add_autogetting(self, repo):
        if repo not in self.autogetting:
            try:
                f = open(autoget_log, mode='a+')
                f.write(repo.name+'\n')
                f.close()
                self.autogetting.append(repo)

                return 0
            except:
                return 1



    def get_from(self, repo):
        self.annex_indirect()
        repo.annex_indirect()
        repo.annex_add()
        repo.annex_sync(self)
        self.annex_sync(repo)
        self.annex_get(repo)


def create_repository(local_repo, path, name):
    local_repo.annex_init()
    new_repo = Repo(name, path, logs=1)
    new_repo.annex_init()
    local_repo.connect_remotes(new_repo)
    local_repo.annex_sync(new_repo)
    new_repo.annex_sync(local_repo)

