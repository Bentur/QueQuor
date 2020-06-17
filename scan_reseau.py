"""
scan le réseau à la recherche de clien DLNA (le NAS quoi)


https://www.synology.com/en-global/knowledgebase/DSM/tutorial/Multimedia/How_to_enjoy_multimedia_contents_stored_on_Synology_NAS_with_DLNA_UPnP_compliant_DMAs

bibliothèque testé :
https://github.com/gabrielmagno/nano-dlna
pip install nanodlna

https://pypi.org/project/Cohen3/
pip install Cohen3

Ca a l'air pas trop mal
https://github.com/cherezov/dlnap

explication :
https://github.com/flyte/upnpclient
https://github.com/fboender/pyupnpclient
https://www.electricmonk.nl/log/2016/07/05/exploring-upnp-with-python/
"""
import upnpclient
from bs4 import BeautifulSoup
from scan import traitement_film

path_base_reseau = "data\\path_scan_reseau.txt"


def scan_devices():
    """
    scan le réseau à la recherche des devices upnp
    renvoie l'addresse du fichier pour mettre dans le fichier data/path_scan_reseau
    """
    devices = upnpclient.discover()

    for device in devices:
        print(device)
        print(device.device_name)
        print("\n")

def scan_all_reseau(path = path_base_reseau):
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
        films += scanner_reseau(source)
    return films

def scanner_reseau(path_reseau):
    films = []

    #d = upnpclient.Device("http://192.168.1.79:50001/desc/device.xml")
    d = upnpclient.Device(path_reseau)

    a = d.ContentDirectory.Browse(ObjectID="34$614", BrowseFlag='BrowseDirectChildren', Filter="*", StartingIndex=0, RequestedCount=999999, SortCriteria="")

    fo = a["Result"]

    soup = BeautifulSoup(fo, "html.parser")
    folders = soup.find_all("container")

    for folder in folders:
        """
        <container id="34$644"  parentID="34$614"  restricted="1">
        <dc:title>Zombie</dc:title>
        <upnp:class>object.container.storageFolder</upnp:class>
        <upnp:storageUsed>-1</upnp:storageUsed>
        </container>
        """
        id = folder.get("id")
        films += scan_folder_reseau(d, id)

    return films


def scan_folder_reseau(d, id, parent=" "):
    """
    scan un dossier du réseau avec l'id renseigné
    """
    films = []

    a = d.ContentDirectory.Browse(ObjectID=id, BrowseFlag='BrowseDirectChildren', Filter="*", StartingIndex=0, RequestedCount=999999, SortCriteria="")

    fo = a["Result"]

    soup = BeautifulSoup(fo, "html.parser")
    folders = soup.find_all("container")

    #on regarde si il y a des sous-dossiers
    for folder in folders:
        """
        <container id="34$644"  parentID="34$614"  restricted="1">
        <dc:title>Garfield</dc:title>
        <upnp:class>object.container.storageFolder</upnp:class>
        <upnp:storageUsed>-1</upnp:storageUsed>
        </container>
        """
        id = folder.get("id")
        parent = folder.find('dc:title').text
        #print("new parent : ", parent)
        films += scan_folder_reseau(d, id)

    files = soup.find_all("item")

    for file in files:
        """
        <item id="34$@1711" parentid="34$644" restricted="1">
        <dc:title>Zoo - 2018 (VO 720p)</dc:title>
        <upnp:class>object.item.videoItem</upnp:class>
        <dc:date>2020-04-04T18:19:15</dc:date><res bitrate="56721" duration="1:34:40.000" nraudiochannels="2" protocolinfo="http-get:*:video/x-matroska:*" resolution="1280x544" samplefrequency="48000" size="322198435">http://192.168.1.79:50002/v/NDLNA/1711.mkv</res></item>
        """
        title = file.find("dc:title").text
        res = file.find("res")
        duration = res.get("duration")
        path = res.text

        f = traitement_film(title, path, parent, duration)
        if (not (f == None)):
            films.append(f)
        else :
            print("couldn't process : ", title, duration, path)

    return films

#a = scan_all_reseau()


"""
a = d.ContentDirectory.Browse(ObjectID=33, BrowseFlag='BrowseMetadata', Filter=0, StartingIndex=0, RequestedCount=0, SortCriteria=0)
print(a)
for cont in a :
    print(cont, a[cont])
    print('\n')

#print(d.ContentDirectory.GetSystemUpdateID())
#print(type(d.ContentDirectory.GetSystemUpdateID()))
"""

