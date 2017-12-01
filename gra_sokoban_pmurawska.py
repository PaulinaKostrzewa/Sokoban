import sys
sys.path.append('/usr/local/lib/python3.6/dist-packages')
import random, sys, copy, os, pygame
from pygame.locals import *

FPS = 30 # frames per second - update ekranu 
WINWIDTH = 800 # szerokosc ekranu w pixelach
WINHEIGHT = 600 # wysokosc ekranu w pixelach
HALF_WINWIDTH = int(WINWIDTH / 2)
HALF_WINHEIGHT = int(WINHEIGHT / 2)

# Rozmiary pojedynczej grafiki tile w pixelach.
TILEWIDTH = 50
TILEHEIGHT = 50
TILEFLOORHEIGHT = 50

BRIGHTBLUE = (  0, 170, 255)
WHITE      = (255, 255, 255)
BGCOLOR = BRIGHTBLUE #tlo jasno niebieskie
TEXTCOLOR = WHITE #kolor tekstu - bialy

UP = 'up'
DOWN = 'down'
LEFT = 'left'
RIGHT = 'right'

##############################FUNKCJE STERUJACE GRA##########################################################

#glowna funkcja ktora tworzy gre:
def main():
    global FPSCLOCK, WINDOW, SLOWNIK_OBRAZKI, TILEMAPPING, BASICFONT, PLAYER_GRAFIKA, PIOSENKI

    # inicjacja gry
    pygame.init()
    FPSCLOCK = pygame.time.Clock()

    #okno gry
    WINDOW = pygame.display.set_mode((WINWIDTH, WINHEIGHT))

    pygame.display.set_caption('Sokoban')
    BASICFONT = pygame.font.Font('freesansbold.ttf', 18)

    # Globalny słownik zawierajacy wszystki grafiki uzte w programie i odpowiednio dostosowana wielkość
    SLOWNIK_OBRAZKI = {'cel_przed': pygame.transform.scale(pygame.image.load('EndPoint_Red.png'),(50,50)),
                  'cel_po': pygame.transform.scale(pygame.image.load('CrateDark_Blue.png'),(50,50)),
                  'skrzynka': pygame.transform.scale(pygame.image.load('Crate_Blue.png'),(50,50)),
                  'mur': pygame.transform.scale(pygame.image.load('Wall_Brown.png'),(50,50)),
                  'podloga': pygame.transform.scale(pygame.image.load('GroundGravel_Sand.png'),(50,50)),
                  'title': pygame.image.load('sokoban_start.png'),
                  'solved': pygame.transform.scale(pygame.image.load('nowa_runda_sokoban.png'),(600,200)),
                  'boy': pygame.transform.scale(pygame.image.load('Character4.png'),(50,50))}

    # Globalny słownik, który czyta mapuje znaki uzyte przy tworzeniu poziomow poziomow
    # w pliku tekstowym
    TILEMAPPING = {'#': SLOWNIK_OBRAZKI['mur'],
                   ' ': SLOWNIK_OBRAZKI['podloga']}


                                             
    # ludzik ktorym poruszamy sie -grafika
    PLAYER_GRAFIKA = SLOWNIK_OBRAZKI['boy']
    
    PIOSENKI = ['Game-Menu_Looping.wav', 'Monkey-Island-Band_Looping.wav', 'applause10.wav']

    #pokazuje ekran startowy az uzytkownik wcisnie jakikolwiek klawisz 
    ekranStartowy()

    # Wczytanie poziomow gry z pliku tesktowego
    poziomy = wczytajPoziomy('levels.txt')
    currentLevelIndex = 0
    czy_boo=False
    

  
    #Kazda petla wczytujaca poziom gry
    while True: 
        # Wczytanie pierwszego poziomy i start gry
        wynikGry = runLevel(poziomy, currentLevelIndex)

        if wynikGry in ('solved', 'next'):
            # wybierz kolejny poziom
            currentLevelIndex += 1
            if currentLevelIndex >= len(poziomy):
                # jesli nie ma juz wiecej poziomow, zacznij znowu od pierwszego
                currentLevelIndex = 0  
            
        elif wynikGry == 'back':
            # wybierz poziom wczesniejszy
            currentLevelIndex -= 1
            if currentLevelIndex < 0:
                # jesli nie ma wczesniejszego poziomu idz do ostatniego
                currentLevelIndex = len(poziomy)-1
        elif wynikGry == 'reset':
            pass # reset petli - obecny poziom wczytany jeszcze raz


def runLevel(poziomy, levelNum):
    
    #muzyka
    pygame.mixer.music.load(PIOSENKI[1])
    pygame.mixer.music.play(-1)
 
    levelObj = poziomy[levelNum]
    mapObj = przeksztMapy(levelObj['mapObj'])
    gameStateObj = copy.deepcopy(levelObj['startState'])
    mapNeedsRedraw = True # True - rysuje mape: rysujMape()
    levelSurf = BASICFONT.render('Poziom nr %s z %s' % (levelNum + 1, len(poziomy)), 1, TEXTCOLOR) #wypisanie na ekranie ktory poziom gry obecnie
    levelRect = levelSurf.get_rect()
    levelRect.bottomleft = (20, WINHEIGHT - 35)
    mapWidth = len(mapObj) * TILEWIDTH
    mapHeight = (len(mapObj[0]) - 1) * TILEFLOORHEIGHT + TILEHEIGHT

    levelIsComplete = False


    while True: # PETLA GŁOWNA GRY
        # reset zmiennych:
        ludzikRuchW = None
        keyPressed = False

        for event in pygame.event.get(): 
            if event.type == QUIT:
                # jesli uzytkownik wcisnal 'x' w prawym gornym rogu
                koniecGry()

            elif event.type == KEYDOWN:
                # jesli wcisniety klawisz strzalka
                keyPressed = True
                if event.key == K_LEFT:
                    ludzikRuchW = LEFT
                elif event.key == K_RIGHT:
                    ludzikRuchW = RIGHT
                elif event.key == K_UP:
                    ludzikRuchW = UP
                elif event.key == K_DOWN:
                    ludzikRuchW = DOWN


                # klawisz n - nastepny poziom
                elif event.key == K_n:
                    return 'next'
                # klawisz b - wczesniejszy poziom 
                elif event.key == K_b:
                    return 'back'

                # uzytkownik wcisal ESC - koniec gry
                elif event.key == K_ESCAPE:
                    koniecGry()
                # backspace - reset gry
                elif event.key == K_BACKSPACE:
                    return 'reset' 
                

        if ludzikRuchW != None and not levelIsComplete:
            # Jesli uzytkownik wcisnal klawisz ruchu to ludzik ma sie poruszyc 
            # jesli to możliwe oraz popchnac skrzynke jesli sie da
            moved = czyRuch(mapObj, gameStateObj, ludzikRuchW) #TRUE/FALSE

            if moved:
                # podbij liczbe krokow
                gameStateObj['licznikKrokow'] += 1
                mapNeedsRedraw = True

            if PoziomUkonczony(levelObj, gameStateObj):
                # poziom jest ukonczony - pokaz grafike 'solved'
                levelIsComplete = True
                keyPressed = False

                
        
        WINDOW.fill(BGCOLOR)

        #ponowne malowanie mapy
        if mapNeedsRedraw:
            mapSurf = rysujMape(mapObj, gameStateObj, levelObj['cele'])
            mapNeedsRedraw = False


        # Ustawienie prostokata mapy na centrum planszy gry  
        mapSurfRect = mapSurf.get_rect()
        mapSurfRect.center = (HALF_WINWIDTH, HALF_WINHEIGHT)

        # Dodanie prostokata mapy do okna WINDOW
        WINDOW.blit(mapSurf, mapSurfRect)

        WINDOW.blit(levelSurf, levelRect)
		
		# licznik wykonanych krokow na ekranie
        stepSurf = BASICFONT.render('Liczba wykonanych krokow: %s' % (gameStateObj['licznikKrokow']), 1, TEXTCOLOR) 
        stepRect = stepSurf.get_rect()
        stepRect.bottomleft = (20, WINHEIGHT - 10) #miejsce ustawienie licznika na ekranie
        WINDOW.blit(stepSurf, stepRect) #wywolanie licznika na ekran

        if levelIsComplete:
            # jesli TRUE (poziom ukonczony) to pokaz grafike 'solved' 
            # az uzytkownik wcisniej jakikolwiek przycisk
            solvedRect = SLOWNIK_OBRAZKI['solved'].get_rect()
            solvedRect.center = (HALF_WINWIDTH, HALF_WINHEIGHT)
            WINDOW.blit(SLOWNIK_OBRAZKI['solved'], solvedRect)
            #muzyka
            pygame.mixer.music.load(PIOSENKI[2])
            pygame.mixer.music.play(0)

            if keyPressed:
                return 'solved'

        pygame.display.update() # WINDOW 
        FPSCLOCK.tick()


def czyMur(mapObj, x, y):
    """Zwraca True jesli (x,y) pozycja na mapie jest murem,
    w.p.p. zwraca False"""
    if x < 0 or x >= len(mapObj) or y < 0 or y >= len(mapObj[x]):
        return False # (x,y) nie sa na mapie
    elif mapObj[x][y] in ('#'):
        return True # mur na drodze
    return False


def przeksztMapy(mapObj):
    """Funkcja tworzy kopie mapy - bez obiektow typu ludzik, skrzynia, cel_przed, cel_po
    Zwraca mape"""

    # Kopia mapy - by nie zmieniac oryginalnej
    mapObjCopy = copy.deepcopy(mapObj)

    # Usuniecie z mapy obiektow ktore nie są murem (zmiana na obiekt typu podloga)
    for x in range(len(mapObjCopy)):
        for y in range(len(mapObjCopy[0])):
            if mapObjCopy[x][y] in ('$', '.', '@', '+', '*'):
                mapObjCopy[x][y] = ' '

    return mapObjCopy


def czyZablokowany(mapObj, gameStateObj, x, y):
    """Funkcja zwraca True jesli pozycja (x,y) na mapie jestReturns
    zablokowana przez mur lub skrzynie, 
    w.p.p zwraca False"""

    if czyMur(mapObj, x, y):
        return True

    elif x < 0 or x >= len(mapObj) or y < 0 or y >= len(mapObj[x]):
        return True # (x,y) sa poza mapa

    elif (x, y) in gameStateObj['skrzynki']:
        return True # skrzynka blokuje

    return False


def czyRuch(mapObj, gameStateObj, ludzikRuchW):
    """Funkcja dla odpowieniej mapy, stanu gry, sprawdza czy jest mozliwosc dla ludzika 
    zrobic dany ruch. Jesli tak - zmienia pozycje ludzika 
    (i ew. pozycje skrzyni). Jesli ruch jest niemozliwy - nic nie robi.

    Zwraca True jesli ludzik wykonal ruch, w p.p. False"""

    # Sprawdzenie czy ludzik moze sie w danym kierunku poruszyc:
    playerx, playery = gameStateObj['ludzik']

	# zmienna pomocnicza 
    skrzynki = gameStateObj['skrzynki']

    # Ruch ludzika
    if ludzikRuchW == UP:
        xOffset = 0
        yOffset = -1
    elif ludzikRuchW == RIGHT:
        xOffset = 1
        yOffset = 0
    elif ludzikRuchW == DOWN:
        xOffset = 0
        yOffset = 1
    elif ludzikRuchW == LEFT:
        xOffset = -1
        yOffset = 0

    # Sprawdzenie czy ruch jest mozliwy
    if czyMur(mapObj, playerx + xOffset, playery + yOffset):
        return False
    else:
        if (playerx + xOffset, playery + yOffset) in skrzynki:
            # Na drodze jest strzynka wiec nastepuje jej przesuniecie
            if not czyZablokowany(mapObj, gameStateObj, playerx + (xOffset*2), playery + (yOffset*2)):
                # Przesun skrzynke
                ind = skrzynki.index((playerx + xOffset, playery + yOffset))
                skrzynki[ind] = (skrzynki[ind][0] + xOffset, skrzynki[ind][1] + yOffset)
            else:
                return False
        # Przesuniecie ludzika
        gameStateObj['ludzik'] = (playerx + xOffset, playery + yOffset)
        return True


def ekranStartowy():
    """Funkcja wyswietla ekran startowy z tytulem gry i instrukcja gry
    dopuki uzytkownik nie wcisnie jakiegokolwiek klawisza. Zwraca None."""

    #muzyka
    pygame.mixer.music.load(PIOSENKI[0])
    pygame.mixer.music.play(-1)
    
    # Pozycja grafiki 'title'
    titleRect = SLOWNIK_OBRAZKI['title'].get_rect()
    topCoord = 50 # topCoord tracks where to position the top of the text
    titleRect.top = topCoord
    titleRect.centerx = HALF_WINWIDTH
    topCoord += titleRect.height

    # Poniewaz w Pygame tekt moze byc pokazywany tylko w jednej linijce (brak opcji 'newline')
    # dlatego uzyta lista tekstow ktore beda wyswietlane linijka po linijce
    INSTRUKCJA = ['INSTRUKCJA',
                       'Popychając ustaw skrzynki na czerwone kolka.',
                       'Poruszaj sie przy uzyciu strzalek.',
                       'Wcisnik Backspace by zresetowac poziom.',
                       'Wcisnij ESC by zakonczyc gre.',
                       'Wcisnij N by przejsc do kolejnego poziomu.',
                       'Wcisnij B by przejsc do poprzedniego poziomu.',
                       'POWODZENIA!']

    # Napiejw pomaluj tlo:
    WINDOW.fill(BGCOLOR)

    # Obraz tytulowy 'title':
    WINDOW.blit(SLOWNIK_OBRAZKI['title'], titleRect)

    #instrukcja
    for i in range(len(INSTRUKCJA)):
        instSurf = BASICFONT.render(INSTRUKCJA[i], 1, TEXTCOLOR)
        instRect = instSurf.get_rect()
        topCoord += 10 # 10 pixeli pomiedzy linijkami
        instRect.top = topCoord
        instRect.centerx = HALF_WINWIDTH
        topCoord += instRect.height # dodac szerokosc liniki
        WINDOW.blit(instSurf, instRect)

    while True: #Petla glowna dla ekranu startowego
        for event in pygame.event.get():
            if event.type == QUIT:
                koniecGry()
                return
            elif event.type == KEYDOWN:
                if event.key == K_ESCAPE:
                    koniecGry()
                    return
                pygame.mixer.music.stop()
                return # uzytkownik wcisnal klawisz wiec return

        pygame.display.update()
        FPSCLOCK.tick()      

        


def wczytajPoziomy(filename):
    assert os.path.exists(filename), 'Cannot find the level file: %s' % (filename)
    mapFile = open(filename, 'r')
    # Kazdy poziom musi zakonczyc sie linia pusta
    content = mapFile.readlines() + ['\r\n']
    mapFile.close()

    poziomy = [] # zawierajaca poziomy
    levelNum = 0
    mapTextLines = [] # zwiera linijki pojedynczej mapy poziomu
    mapObj = [] # mapa stworzona z linijki kodu z mapTextLines
    for lineNum in range(len(content)):
        # Przeksztalcanie kazdej linijki z pliku z poziomami
        line = content[lineNum].rstrip('\r\n')

        if ';' in line:
            # ; - linijki rozpoczynajace sie znakiem ; sa ignorowane (kometarze)
            line = line[:line.find(';')]

        if line != '':
            # linijka mapy
            mapTextLines.append(line)
        elif line == '' and len(mapTextLines) > 0:
            # pusta linia oznacza koniec mapy w pliku tekstowym

            # Znajdz najdluzsza linijke w mapie
            maxWidth = -1
            for i in range(len(mapTextLines)):
                if len(mapTextLines[i]) > maxWidth:
                    maxWidth = len(mapTextLines[i])
					
            # Dodaj spacje na koncu w linijkach krotszych niz maksymalna
            # otrzymamy prostokatna mape
            for i in range(len(mapTextLines)):
                mapTextLines[i] += ' ' * (maxWidth - len(mapTextLines[i]))

            # Przekonwertowanie linijek mapTextLines to obiektu mapy
            for x in range(len(mapTextLines[0])):
                mapObj.append([])
            for y in range(len(mapTextLines)):
                for x in range(maxWidth):
                    mapObj[x].append(mapTextLines[y][x])

            # Petla wyszukujaca znaki: @, ., $
            startx = None # wspolrzedne polozenia ludzika
            starty = None
            cele = [] # lista wspolrzednych (x, y) gdzie znajduja sie cele
            skrzynki = [] # lista wspolrzednych (x, y) gdzie znajduja sie skrzynki
            for x in range(maxWidth):
                for y in range(len(mapObj[x])):
                    if mapObj[x][y] in ('@', '+'):
                        # '@' ludzik, '+' ludzik i cel w tym samym miejscu
                        startx = x
                        starty = y
                    if mapObj[x][y] in ('.', '+', '*'):
                        # '.' cel, '*' skrzynka i cel w tym samym miejscu
                        cele.append((x, y))
                    if mapObj[x][y] in ('$', '*'):
                        # '$' skrzynka
                        skrzynki.append((x, y))

            # Podstawowe checki:
            assert startx != None and starty != None, 'Level %s (around line %s) in %s is missing a "@" or "+" to mark the start point.' % (levelNum+1, lineNum, filename)
            assert len(cele) > 0, 'Level %s (around line %s) in %s must have at least one goal.' % (levelNum+1, lineNum, filename)
            assert len(skrzynki) >= len(cele), 'Level %s (around line %s) in %s is impossible to solve. It has %s cele but only %s stars.' % (levelNum+1, lineNum, filename, len(cele), len(skrzynki))

            # Obekty poziomu i poczatkowych stanow w grze 
            gameStateObj = {'ludzik': (startx, starty),
                            'licznikKrokow': 0,
                            'skrzynki': skrzynki}
            levelObj = {'width': maxWidth,
                        'height': len(mapObj),
                        'mapObj': mapObj,
                        'cele': cele,
                        'startState': gameStateObj}

            poziomy.append(levelObj)

            # Reset zmiennych/list by wczytac mape z nowym poziomem
            mapTextLines = []
            mapObj = []
            gameStateObj = {}
            levelNum += 1
    return poziomy



def rysujMape(mapObj, gameStateObj, cele):
    """ Rysuje mape na ekranie oraz ludzika i skrzynki. 
	Ta funkcja nie wywoluje pygame.display.update(),
    ani nie wypisuje numerow poziomow i liczby krokow na ekranie."""

    # mapSurf - naniesione sa tiles (grafika mapy) 
	
	#Najepierw obliczenie dlugosci i szerokosci mapy
    mapSurfWidth = len(mapObj) * TILEWIDTH
    mapSurfHeight = (len(mapObj[0]) - 1) * TILEFLOORHEIGHT + TILEHEIGHT
    mapSurf = pygame.Surface((mapSurfWidth, mapSurfHeight))
    mapSurf.fill(BGCOLOR) # kolor tla

    # umieszczenie grafik tiles w odpowiednich miejscach
    for x in range(len(mapObj)):
        for y in range(len(mapObj[x])):
            spaceRect = pygame.Rect((x * TILEWIDTH, y * TILEFLOORHEIGHT, TILEWIDTH, TILEHEIGHT))
            if mapObj[x][y] in TILEMAPPING:
                baseTile = TILEMAPPING[mapObj[x][y]]
            else: 
                baseTile = TILEMAPPING[' ']

            # dodaj na ekran obiekty: mur i podloga
            mapSurf.blit(baseTile, spaceRect)

            
            if (x, y) in gameStateObj['skrzynki']:
                # ustaw skrzynke
                mapSurf.blit(SLOWNIK_OBRAZKI['skrzynka'], spaceRect)
                if (x, y) in cele:
                    # nastepnie jesli w tym miejscu tez jest cel to ustaw grafike 'cel_po' (ciemniejsza skrzynka)
                    mapSurf.blit(SLOWNIK_OBRAZKI['cel_po'], spaceRect)
            elif (x, y) in cele:
                # jesli tylko cel to ustaw grafike celu cel_przed (czerwona kropka) 
                mapSurf.blit(SLOWNIK_OBRAZKI['cel_przed'], spaceRect)

            # Na koncu ustaw ludzika 
            if (x, y) == gameStateObj['ludzik']:
                mapSurf.blit(PLAYER_GRAFIKA, spaceRect)

    return mapSurf



def PoziomUkonczony(levelObj, gameStateObj):
    """Zwraca True jesli wszystkie skrzynki sa ustawione na celach (skrzynki sa ciemne)."""
    for cel in levelObj['cele']:

        if cel not in gameStateObj['skrzynki']:
            # Znaleziono niepokryty cel
            return False

    return True


def koniecGry():
    pygame.quit()
    sys.exit()

#################################### WYWOLANIE GRY ############################################################## 
if __name__ == '__main__':
    main() 