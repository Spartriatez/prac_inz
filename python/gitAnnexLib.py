from subprocess import PIPE, Popen, check_output
import python.beetsCommands as beetsCommands
from python.sshPath import split_data, Ssh
import socket
import getpass
import os

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
            self.annex_init(0)
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

        print("remotedssdsddsddsdssdsdsddsddsd "+self.path)
        p = Popen(['git', 'remote', '-v'], cwd=self.path, stdin=PIPE, stdout=PIPE, stderr=PIPE, bufsize=1)
        remote_names = []
        remote_paths = []
        autopushing_names = self.get_autopushing_names()
        autogetting_names = self.get_autogetting_names()
        for remote in p.stdout:
            remote_str = remote.decode('UTF-8')[:-1]
            #print("sfadsgfdhgfhgdjhfkgjlk;hjjhdsfgdsghfjhkjjrseadfbghngjkgvcfh " + remote_str)
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
    def init(self,if_ssh):
        if(if_ssh==1):
            username,host,path=split_data(self.path)
            password=[]
            connection = Ssh(host, username, password)
            command="cd "+path+" && git init "+path
            cmdAnswer=connection.git_Command(command)
        else:
            cmdAnswer = check_output(['git','init', self.path]).decode('UTF-8')
            print(cmdAnswer)
        if cmdAnswer[:32] == 'Initialized empty Git repository':
            if self.logs == 1: print('Repository initialized')
            #return 0
        elif cmdAnswer[:37] == 'Reinitialized existing Git repository':
            if self.logs == 1: print('Repository reinitialized')
            #return 0
        else:
            if self.logs == 1: print('Initialization failed')
            #return 1

    """
    Wywołanie git annex init <ścieżka>
    0-repo initialized, 1-fail
    """
    def annex_init(self,if_ssh):
        self.init(if_ssh)
        if(if_ssh==1):
            username, host, path = split_data(self.path)
            password = []
            connection = Ssh(host, username, password)
            command = "cd " + path + " && git annex init "+path
            cmdAnswer = connection.git_Command(command)
            lines=cmdAnswer.split(" ")
            for line in lines:
                if("ok" in line):
                    print('Annex repository initialized')
                else: print(line+" ")
        else:
            p = Popen(['git', 'annex', 'init', self.path], cwd=self.path, stdin=PIPE, stdout=PIPE, stderr=PIPE, bufsize=1)
            for line in p.stdout:
                line = line.decode('UTF-8')[:-1]
                if "ok" in line:
                    if self.logs == 1:
                        print('Annex repository initialized')
                        #return 0
                else: print(line)
        #if self.logs == 1:
            #print('Annex initialization failed')
        #return 1

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
        return addedFiles

    def annex_ssh_add(self, username,host,path):
        print('git annex add ' + path)
        password = []
        connection = Ssh(host, username, password)
        command = "cd " + path + " && git annex add ."
        cmdAnswer, cmdErr = connection.git_Command2(command)
        print(cmdAnswer)


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

        return 0

    def annex_ssh_sync(self,username,host,path, remote):
        print("annex synccccccccccc")
        password = []
        connection = Ssh(host, username, password)
        command = "cd " + path + " && git annex sync " + remote.name
        cmdAnswer, cmdErr = connection.git_Command2(command)
        print(cmdErr)
        print(cmdAnswer)
        return 0
    """
    Wywołuje git annex get w celu pobrania plikow ktore nie znajduja sie w repozytorium
    """
    def annex_get(self, source, path='.'):
        print('git annex get -f '+source.name+' '+path)
        p = Popen(['git', 'annex', 'get', '-f', source.name, path], cwd=self.path, stdin=PIPE, stdout=PIPE, stderr=PIPE, bufsize=1)

        for line in p.stderr:
            print(line.decode('UTF-8')[-1])
        for line in p.stdout:
            print(line)
        print('getting finished')

    def annex_ssh_get(self,username,host,path_local ,source, path='.'):
        print('git annex get -f '+source.name+' '+path)
        password = []
        connection = Ssh(host, username, password)
        command = "cd " + path_local + " && git annex get -f "+source.name+" "+path
        cmdAnswer, cmdErr = connection.git_Command2(command)
        print(cmdErr)
        print(cmdAnswer)
        print('getting finished')


    def annex_get_from_all(self, path='.'):
        print('git annex get  '+path)
        p = Popen(['git', 'annex', 'get', path], cwd=self.path, stdin=PIPE, stdout=PIPE, stderr=PIPE, bufsize=1)

        for line in p.stderr:
            print(line.decode('UTF-8')[-1])
        for line in p.stdout:
            print(line)
        print('getting finished')



    def annex_drop(self, path='.'):
        print('git annex drop', path)
        p = Popen(['git', 'annex', 'drop', path], cwd=self.path, stdin=PIPE, stdout=PIPE, stderr=PIPE, bufsize=1)

        for line in p.stderr:
            print(line.decode('UTF-8')[:-1])
        for line in p.stdout:
            line = line.decode('UTF-8')[:-1]
            if line[0:6] == 'failed':
                return 1
        print('getting finished')
        return 0

    def annex_ssh_drop(self,username,host,path_local, path='.'):
        password = []
        connection = Ssh(host, username, password)
        command = "cd " + path_local + " && git annex drop " + path
        cmdAnswer, cmdErr = connection.git_Command2(command)
        print(cmdErr)
        print(cmdAnswer)
        print('getting finished')
        return 0

    def annex_unlock(self, path='.'):
        p = Popen(['git', 'annex', 'unlock', path], cwd=self.path, stdin=PIPE, stdout=PIPE, stderr=PIPE, bufsize=1)

    def annex_direct(self):
        p = Popen(['git', 'annex', 'direct'], cwd=self.path, stdin=PIPE, stdout=PIPE, stderr=PIPE, bufsize=1)

    def annex_indirect(self):
        p = Popen(['git', 'annex', 'indirect'], cwd=self.path, stdin=PIPE, stdout=PIPE, stderr=PIPE, bufsize=1)

    def annex_ssh_direct(self,username,host,path):
        password = []
        connection = Ssh(host, username, password)
        command = "cd " + path + " && git annex direct"
        cmdAnswer, cmdErr = connection.git_Command2(command)
        print(cmdErr)
        print(cmdAnswer)

    def annex_ssh_indirect(self,username,host,path):
        password = []
        connection = Ssh(host, username, password)
        command = "cd " + path + " && git annex indirect"
        cmdAnswer, cmdErr = connection.git_Command2(command)
        print(cmdErr)
        print(cmdAnswer)

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

    def get_ssh_from(self, username,host,path,repo):
        self.annex_indirect()
        repo.annex_ssh_indirect(username,host,path)
        repo.annex_ssh_add(username,host,path)
        repo.annex_ssh_sync(username,host,path,self)
        self.annex_sync(repo)
        self.annex_get(repo)

    def get_ssh_from_v2(self, username,host,path,repo):
        self.annex_ssh_indirect(username,host,path)
        repo.annex_indirect()
        repo.annex_add()
        repo.annex_sync(repo)
        self.annex_ssh_sync(username,host,path,self)
        self.annex_ssh_get(username,host,path,repo)
    #tworzenie to samo ale dla

def remote_ssh_add(new_repo,local_repo):
    name = local_repo.name
    if name not in new_repo.remote_names:
        local_user=getpass.getuser()
        username, host, path = split_data(new_repo.path)
        password = []
        hostname=socket.gethostname()
        ip=socket.gethostbyname(hostname)
        connection = Ssh(host, username, password)
        command = "cd " + path + " && git remote add "+name+" ssh://"+local_user+"@"+ip+local_repo.path
        cmdAnswer, cmdErr = connection.git_Command2(command)
        if (cmdAnswer[:-1] == '') & (cmdErr == ''):
            print('Remote added')
            new_repo.remotes.append(local_repo)
            new_repo.remote_names.append(name)
            return 0
    return 1

def annex_ssh_sync(new_repo, remote):
    print('git annex sync '+remote.name)

    username, host, path = split_data(new_repo.path)
    password = []
    connection = Ssh(host, username, password)
    command = "cd " + path + " && git annex sync "+ remote.name
    cmdAnswer, cmdErr = connection.git_Command2(command)
    if (cmdAnswer[:-1] == '') & (cmdErr == ''):
        print('Repo synced')
    else:
        print('Failed repo synced')
    return 0

def create_repository(local_repo, path, name,if_ssh):
    local_repo.annex_init(0)
    new_repo = Repo(name, path, logs=1)
    new_repo.annex_init(if_ssh)
    if(if_ssh==1):
        res=remote_ssh_add(new_repo,local_repo)
        res2=local_repo.remote_add(new_repo)
        if(res==res2):
            print("Remoted repos")
        else:
            print("Failed connected repos")
        local_repo.annex_sync(new_repo)
        annex_ssh_sync(new_repo,local_repo)
    else:
        local_repo.connect_remotes(new_repo)
        local_repo.annex_sync(new_repo)
        new_repo.annex_sync(local_repo)

def get_backup(path):
    back_path=path+'-copy'
    if not os.path.exists(back_path):
       os.makedirs(back_path)
       print("created directory")
       p = Popen(['git', 'init', back_path], cwd=back_path, stdin=PIPE, stdout=PIPE, stderr=PIPE,
                 bufsize=1)
       for line in p.stderr:
           print(line.decode('UTF-8')[:-1])
       for line in p.stdout:
           print(line.decode('UTF-8')[:-1])
       p = Popen(['git','annex' ,'init', back_path], cwd=back_path, stdin=PIPE, stdout=PIPE, stderr=PIPE,
                 bufsize=1)
       for line in p.stderr:
           print(line.decode('UTF-8')[:-1])
       for line in p.stdout:
           print(line.decode('UTF-8')[:-1])

    tmp=path+'/.'
    p = Popen(['git', 'annex', 'import','--duplicate',tmp], cwd=back_path, stdin=PIPE, stdout=PIPE, stderr=PIPE, bufsize=1)
    for line in p.stderr:
        print(line.decode('UTF-8')[:-1])
    for line in p.stdout:
        print(line.decode('UTF-8')[:-1])

def from_backup(path):
    back_path=path+'-copy'
    tmp = back_path + '/.'
    p = Popen(['git', 'annex', 'import', '--duplicate', tmp], cwd=path, stdin=PIPE, stdout=PIPE, stderr=PIPE,
              bufsize=1)
    for line in p.stderr:
        print(line.decode('UTF-8')[:-1])
    for line in p.stdout:
        print(line.decode('UTF-8')[:-1])