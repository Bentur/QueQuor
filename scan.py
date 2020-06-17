import os

path_base_films = "data\\path_scan_films.txt"
path_base_series = "data\\path_scan_series.txt"

def get_path_base_films():
	"""
	:return: le chemin jusqu'au fichier où se trouve les paths où chercher les films
	"""
	return path_base_films

def get_path_base_series():
	"""
	:return: le chemin jusqu'au fichier où se trouve les paths où chercher les series
	"""
	return path_base_series

def get_sources_films(path = path_base_films):
	"""
	retourne les sources enregistrées
	:param path: chemin vers le fichier contenant les sources
	:return:
	"""
	f = open(path, 'r', encoding='UTF-8')
	sources = f.readlines()
	f.close()
	return sources

def add_source_films(source, path = path_base_films):
	sources = get_sources_films(path)
	sources.append(source)
	f = open(path, 'w', encoding='UTF-8')
	f.writelines(sources)
	f.close()

def delete_source_films(source, path = path_base_films):
	sources = get_sources_films(path)
	try:
		i = sources.index(source)
		sources.pop(i)

		f = open(path, 'w', encoding='UTF-8')
		f.writelines(sources)
		f.close()
	except ValueError:
		print("The source you are trying to delete does not exist")

def scan_all_films(path = path_base_films):
	"""
	:param path: le chemin vers le fichier contenant tous les paths à scanner
	:return: la liste de tous les films dans tous les chemins scannés
	"""
	f = open(path, 'r', encoding='UTF-8')
	sources = f.readlines()
	f.close()

	films = []
	for source in sources:
		if (source[-1] == '\n'):
			source = source[:-1]
		# on regarde si le chemin est valide
		if (verify_source(source)):
			films += scanner_films(source)
	return films

def verify_source(source):
	"""
	vérifie si le chemin est valide
	:param source:
	:return: True si chemin valide, False sinon
	"""
	source_valide = True
	try:
		os.listdir(source)
	except:
		print("____chemin source non valide : " + source)
		source_valide = False
	return source_valide

def scanner_films(path):
	"""
	:param path: chemin du dossier à examiner
	:return: un tableau de 4 colonnes:
	Titre du film [titre, annee, titre_an, serie, langue, qualite, info, path]
	"""

	liste = []
	l = os.listdir(path)
	for e in l :
		pth = path + os.sep + e
		if(os.path.isdir(pth)):
			liste += scan_films_categories(pth)
		else :
			f = traitement_film(e, pth)
			if (not (f == None)):
				liste.append(f)
			else:
				print("Could not process : " + e)

	return liste

def scan_films_categories(path):
	liste = []
	l = os.listdir(path)
	for e in l :
		pth = path + os.sep + e
		if(os.path.isdir(pth)):
			liste += scan_films_serie(pth, e)
		else :
			f = traitement_film(e, pth)
			if(not(f == None)):
				liste.append(f)
			else :
				print("Could not process : " + e)
	return liste

def scan_films_serie(path, serie):
	liste = []
	l = os.listdir(path)
	for e in l :
		pth = path + os.sep + e
		if(not(os.path.isdir(pth))):
			f = traitement_film(e, pth, serie)
			if(not(f == None)):
				liste.append(f)
			else :
				print("Could not process : " + e)
	return liste

def traitement_film(f, path, parent=" ", duration=None):
	"""
	:param f: le nom du fichier
	       s: la série du film (si existe)
	:return: une liste : [titre, annee, titre_an, serie, langue, qualite, info, path]
	ou None si syntaxe non respecté
	"""
	titre = ""
	annee = None
	titre_an = ""
	serie = parent
	langue = ""
	info = ""
	qualite = ""

	try :
		#ex : Chronicle (Chro) - lala - 2012 Director's Cut (Multi VO 1080p)
		#on coupe sur | - |
		l1 = f.split(" - ")
		#ex : l1 = ["Chronicle (Chro)", "lala", "2012 Director's Cut (Multi VO 1080p)"]

		#reecriture du titre :
		for i in range(len(l1)-1):
			titre += l1[i] + " - "
		titre = titre[:-3] #on enleve " - "

			#on enleve le titre anglais
		l2 = titre.split(" (")

		titre = ""
		for a in l2 :
			if len(a.split(")"))>1:
				b = a.split(")")
				titre_an += b[0]
				titre += b[1]
			else :
				titre +=a

		#reste du titre
		l3 = l1[-1].split(" (")
		#l3 = ["2012 Director's Cut", "Multi VO 1080p)"]
			#annee
		l4 = l3[0].split(" ")
		annee = int(l4[0])
			#info
		if(len(l4) > 1):
			for i in range(1, len(l4)):
				info += l4[i] + " "
			info = info[:-1]

			#qualite
		s1 = l3[1].split(")")[0]
		l5 = s1.split(" ")
		qualite = l5[-1]
			#langue
		for i in range(len(l5)-1):
			langue+=l5[i]+" "
		langue = langue[:-1]
	except:
		return None

	return [titre, annee, titre_an, serie, langue, qualite, info, path, duration]