import pygame
import random
from enum import Enum
from collections import namedtuple
import numpy as np

#ustawia czcionke
pygame.init()
font = pygame.font.SysFont("Comic Sans MS", 24)



#ustala kierunki
class Kierunek(Enum):
    PRAWO = 1
    LEWO = 2
    GÓRA = 3
    DÓŁ = 4


Punkt = namedtuple('Punkt', 'x, y')

#kolory
WHITE = (255, 255, 255)
RED = (200, 0, 0)
GREEN = (0, 255, 0)
BLACK = (0, 0, 0)
#nasze stałe wartości
Wielkość_kwadratu = 20
szybkość = 200

class wazGra:
    #definiowanie planszy
    def __init__(self, w=500):
        self.w = w
        self.display = pygame.display.set_mode((self.w,self.w))
        pygame.display.set_caption('Waz_rzeczny')
        self.clock = pygame.time.Clock()
        self.reset()

    def reset(self):
        #definiowanie startu, kierunku startowego weża i długości startowej
        self.kierunek = Kierunek.PRAWO
        self.głowa = Punkt(self.w / 2+10, self.w / 2 + 10)
        self.waz = [self.głowa,
                      Punkt(self.głowa.x - Wielkość_kwadratu, self.głowa.y),
                      Punkt(self.głowa.x - (2 * Wielkość_kwadratu), self.głowa.y)]

        self.wynik = 0
        self.jedzenie = None
        self.położenie_jedzenia()
        self.iteracja_klatki = 0

    #funkcja która losowo kładzie jabuszko
    def położenie_jedzenia(self):
        x = random.randint(0, (self.w - Wielkość_kwadratu) // Wielkość_kwadratu) * Wielkość_kwadratu
        y = random.randint(0, (self.w - Wielkość_kwadratu) // Wielkość_kwadratu) * Wielkość_kwadratu
        self.jedzenie = Punkt(x, y)
        if self.jedzenie in self.waz:
            self.położenie_jedzenia()

    def krok_gry(self, action):
        self.iteracja_klatki += 1

        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                pygame.quit()
                quit()


        self.ruch(action)
        self.waz.insert(0, self.głowa)

        #definicja kiedy bot jest nagradzany a kiedy karany
        nagroda = 0
        game_over = False
        if self.kolizja() or self.iteracja_klatki > 100 * len(self.waz):
            game_over = True
            nagroda = -10
            return nagroda, game_over, self.wynik

        #definicja powiększenia się weża i zjedzenia jabłka
        if self.głowa == self.jedzenie:
            self.wynik += 1
            nagroda += 10
            self.położenie_jedzenia()
        else:
            self.waz.pop()


        self.aktualizajcaja_ui()
        self.clock.tick(szybkość)

        return nagroda, game_over, self.wynik
    #definicja przegranej
    def kolizja(self, pt=None):
        if pt is None:
            pt = self.głowa

        if pt.x > self.w - Wielkość_kwadratu or pt.x < 0 or pt.y > self.w - Wielkość_kwadratu or pt.y < 0:
            return True

        if pt in self.waz[1:]:
            return True

        return False
    #funkcja ta pozwala nam na zobaczenie węża
    def aktualizajcaja_ui(self):
        self.display.fill(BLACK)
        pygame.draw.rect(self.display, RED, pygame.Rect(self.jedzenie.x, self.jedzenie.y, Wielkość_kwadratu, Wielkość_kwadratu))

        for pt in self.waz:
            pygame.draw.rect(self.display, GREEN, pygame.Rect(pt.x, pt.y, Wielkość_kwadratu, Wielkość_kwadratu))



        text = font.render("Wynik: " + str(self.wynik), True, WHITE)
        self.display.blit(text, [0,0])
        pygame.display.flip()

    def ruch(self, action, ):

        #definicja zmiany kierunku
        clock_wise = [Kierunek.PRAWO, Kierunek.DÓŁ, Kierunek.LEWO, Kierunek.GÓRA]
        idx = clock_wise.index(self.kierunek)
        #ruch bezzmian
        if np.array_equal(action, [1, 0, 0]):
            nowy_kier = clock_wise[idx]
        #ruch w lewo
        elif np.array_equal(action, [0, 1, 0]):
            next_idx = (idx + 1) % 4
            nowy_kier = clock_wise[next_idx]
        else:
            next_idx = (idx - 1) % 4
            nowy_kier = clock_wise[next_idx]

        self.kierunek = nowy_kier
        #defincia przemieszczania sie
        x = self.głowa.x
        y = self.głowa.y
        if self.kierunek == Kierunek.PRAWO:
            x += Wielkość_kwadratu
        elif self.kierunek == Kierunek.LEWO:
            x -= Wielkość_kwadratu
        elif self.kierunek == Kierunek.DÓŁ:
            y += Wielkość_kwadratu
        elif self.kierunek == Kierunek.GÓRA:
            y -= Wielkość_kwadratu

        self.głowa = Punkt(x, y)