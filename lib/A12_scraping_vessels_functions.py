


def separateSlash(string) :
    '''
    Fonction qui permet de séparer la direction et la vitesse qui sont sous la forme : "direction / vitesse"
    '''
    # On utilise la méthode split de python
    stringlist = string.split('/')
    word1 = stringlist[0]
    word2 = stringlist[1]
    return word1[:-1], word2[1:]

# On crée un dictionnaire pour remplacer les mois par leur numéro (par exemple Aug par 08)
months = ['Jan', 'Feb', 'Mar', 'Apr', 'May', 'Jun', 'Jul', 'Aug', 'Sep', 'Oct', 'Nov', 'Dec']
month_numbers = ["%.2d" % i for i in range(1, len(months)+1)]
dict_month = {months[i]: month_numbers[i] for i in range(len(months))}


def convertDateYear(string, year = True) :
    '''
    Convertit la date scrapée en format :
    YYYY-MM-DD-hh:mm
    '''
    # Si le string commence par '-' alors il n'y a pas d'info donc on ne fait rien
    if string[0] == '-':
        return '-' # on retourne juste '-' pour supprimer les éventuels \n
    # On extrait le jour et on le convertit en numéro à l'aide du dictionnaire dict_month
    convmonth = dict_month[string[:3]]
    # On extrait le jour
    i = 0
    ind = 0
    for car in string :
        if car == ',':
            ind = i
        i+=1
    convday = string[4:ind]
    # On ajoute éventuellement un 0 devant le jour pour avoir un format de date cohérent
    if len(convday)==1:
        convday = '0'+ convday
    # La fin du script diffère selon si l'année est écrite ou pas dans la donnée scrapée
    if year :
        convyear = string[ind+2:ind+6]
        convhour = string[ind+7:ind+12]
        return f'{convyear}-{convmonth}-{convday}-{convhour}'
    else :
        convhour = string[ind+2:ind+7]
        return f'2021-{convmonth}-{convday}-{convhour}'

# def extractdestination2(string):
#     if string[0] in ['-', '.', 'A', 'B', 'C', 'D', 'E', 'F', 'G', 'H', 'I', 'J', 'K', 'L', 'M', 'N', 'O', 'P', 'Q', 'R', 'S', 'T', 'U', 'V', 'W', 'X', 'Y', 'Z'] :
#         return string
#     else :
#         string = string[2:]
#         dest2 = ''
#         for car in string :
#             if car != ' ' :
#                 dest2 += car
#         return dest2

def extractDestinationETA(string) :
    i = 0
    for i in range(len(string)) :
        if string[i:i+4] == "ETA:" or string[i:i+4] == "ATA:" :
            ind = i
        i+=1
    destination = string[1:ind-2]
    eta = string[ind+5:-1]
    return destination, eta

def extractOriginATD(string) :
    i = 0
    for i in range(len(string)) :
        if string[i:i+4] == "ATD:" or string[i:i+4] == "ATA:" :
            ind = i
        i+=1
    origin = string[1:ind-1]
    atd = string[ind+5:-2]
    return origin, atd