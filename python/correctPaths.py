from beets.library import Item, Library, PathType
from os import path
from shutil import copy2
from inspect import getfile, currentframe




"""
Na wejściu wprowadzadź obiekt biblioteki
#Funkcja kopiuje okładki albumów do folderu ./static/images,
#a następnie nadpisuje album.artpath każdego albumu biblioteki 
#do formatu html-friendly (../static/images)
#Zwraca 0 gdy nie napotka błędów. Else zwraca liste niepoprawnych artpath
"""
def correctPaths(object):

	NonePath = '../static/images/image-not-found.jpg'
	imagespath=os.path.dirname(os.path.abspath(inspect.getfile(inspect.currentframe())))
	failed = []
	albums = object.albums()
	for album in albums:
		fail = 0
		newCoverPath = "/static/images/cover"+str(album.id)+".jpg"
		artpath = album.artpath
		artpath = pathToStr(artpath)
		if artpath == 'None':
			album.artpath = NonePath
			print(album.artpath)
		elif artpath == NonePath: 	pass
		elif artpath[0:3] == '../': 	pass
		else: 
			if os.path.exists(artpath):
				shutil.copy2(artpath, imagespath+newCoverPath)
				album.artpath = '..'+newCoverPath
			else: 
				fail = 1
				failed.append(artpath)
				pass


		album.store()

	if fail==0:	return fail
	else:		return failed


"""
#Klasa album przechowuje ['artpath'] jako objekt PathType
#PathType.format(path) konwertuje path do stringa
#Funkcja napisana aby kod był przejrzystszy
"""
def pathToStr(path):
	pathConverter = PathType()
	return pathConverter.format(path)


"""
Just uncomment if u want to test it :)


#from subprocess import PIPE, Popen

def getLibPath():
	
	#ponieważ config.yaml na różnych systemach znajduje sie w różnych miejscach, 
	#lepiej wywolac beet config niz bezposrednio otwierac plik open('/home/dominik/.config/beets/config.yaml', 'r')
	
	p = Popen(['beet','config'], stdin=PIPE, stdout=PIPE, stderr=PIPE, bufsize=1)
	for line in p.stdout:
		line = line.decode('UTF-8')[:-1]
		if "library: " in line:
			line = line[9:]
			if not os.path.exists(line):			#w przypadku gdy ścieżka podana jest z użyciem '~/'
				line = os.path.expanduser(line)
			return line\

if __name__ == "__main__":

	libpath = getLibPath()
	lib = Library(libpath)
	print(correctPaths(lib))

"""
