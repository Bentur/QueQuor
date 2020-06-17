"""
fonctions qui servent dans tous les programmes du dossier
"""

#fonction de string
def reecriture(string):
    '''
    enleve les caracteres speciaux
    :param string:
    :return: le string sans les caracteres speciaux
    '''
    s = ""
    for e in string:
        if (e in ['é', 'è', 'ê', 'ë', 'É', 'E']):
            s += 'e'
        elif (e in ['’']):
            s+=" "
        elif (e in ['-', ',', '.', ' ', "'", '[', ']', ":", "."]):
            pass
        elif (e in ['ô', 'ö']):
            s += 'o'
        elif (e in ['ç', 'Ç']):
            s += 'c'
        elif (e in ['à', 'â', 'À', 'Â']):
            s += 'a'
        elif (e in ['ù']):
            s += 'u'
        elif (e in ['î']):
            s += 'i'
        else:
            s += e
    return s

def traduire_pays(pays):
    if(pays == "New Zealand"):
        return "Nouvelle-Zélande"
    elif(pays == "United States of America"):
        return "USA"
    elif(pays == "United Kingdom"):
        return "Angleterre"
    elif(pays == "Sweden"):
        return "Suède"
    elif(pays == "Germany"):
        return "Allemagne"
    elif(pays == "Netherlands"):
        return "Pays-Bas"
    elif(pays == "Spain"):
        return "Espagne"
    elif(pays == "Japan"):
        return "Japon"
    elif(pays == "China"):
        return "Chine"
    elif(pays == "Korea"):
        return "Corée"
    return pays


def colormap(h):
    """
    :param h: une valeur entre 0 et 1
    :return: valeur r, g, b correspondant pour la colormap
    """
    r, g, b = 0, 0, 0
    #red, red|orange_orange_green_lime
    color = [(255, 255, 255), (0, 0, 0), (255, 0, 0), (255, 26, 0)]
    color+= [(255, 54, 0), (255, 80, 0), (255, 107, 0), (255, 134, 0)]
    color+= [(255, 161, 0), (255, 188, 0), (255, 215, 0), (255, 242, 0)]
    color+= [(242, 255, 0), (215, 255, 0), (188, 255, 0), (161, 255, 0)]

    if(h ==0):
        return color[0]
    elif(h == 1):
        return color[-1]

    n = len(color)

    m = int(n*h)

    r = color[m][0] + (color[m+1][0]-color[m][0])*(h*16-m)
    g = color[m][1] + (color[m+1][1]-color[m][1])*(h*16-m)
    b = color[m][2] + (color[m+1][2]-color[m][2])*(h*16-m)

    return (int(r), int(g), int(b))
