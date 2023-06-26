import torch
import random
import numpy as np
from collections import deque
from main import wazGra, Kierunek, Punkt
from model import Liniowe_Qnet, Nauczyciel
from pomocnik import plot

PAMIĘĆ_MAX = 100_000
BATCH_SIZE = 1000
LR = 0.001


class Agent:

    def __init__(self):
        self.n_games = 0
        self.epsilon = 0
        self.gamma = 0.8 #stopa dyskontowa
        self.memory = deque(maxlen=PAMIĘĆ_MAX)
        self.model = Liniowe_Qnet(11, 300, 3)
        self.trainer = Nauczyciel(self.model, lr=LR, gamma=self.gamma)
    #strefa zagrożenia
    def get_state(self, main):
        głowa = main.waz[0]
        point_l = Punkt(głowa.x - 20, głowa.y)
        point_r = Punkt(głowa.x + 20, głowa.y)
        point_u = Punkt(głowa.x, głowa.y - 20)
        point_d = Punkt(głowa.x, głowa.y + 20)

        dir_l = main.kierunek == Kierunek.LEWO
        dir_r = main.kierunek == Kierunek.PRAWO
        dir_u = main.kierunek == Kierunek.GÓRA
        dir_d = main.kierunek == Kierunek.DÓŁ

        state = [

            (dir_r and main.kolizja(point_r)) or
            (dir_l and main.kolizja(point_l)) or
            (dir_u and main.kolizja(point_u)) or
            (dir_d and main.kolizja(point_d)),

            (dir_u and main.kolizja(point_r)) or
            (dir_d and main.kolizja(point_l)) or
            (dir_l and main.kolizja(point_u)) or
            (dir_r and main.kolizja(point_d)),

            (dir_d and main.kolizja(point_r)) or
            (dir_u and main.kolizja(point_l)) or
            (dir_r and main.kolizja(point_u)) or
            (dir_l and main.kolizja(point_d)),

            dir_l,
            dir_r,
            dir_u,
            dir_d,

            main.jedzenie.x < main.głowa.x,
            main.jedzenie.x > main.głowa.x,
            main.jedzenie.y < main.głowa.y,
            main.jedzenie.y > main.głowa.y
        ]

        return np.array(state, dtype=int)

    def remember(self, state, action, nagroda, next_state, done): #z lewej usuwa
        self.memory.append((state, action, nagroda, next_state, done))

    def train_long_memory(self):
        if len(self.memory) > BATCH_SIZE:
            mini_sample = random.sample(self.memory, BATCH_SIZE)
        else:
            mini_sample = self.memory

        states, actions, rewards, next_states, dones = zip(*mini_sample)
        self.trainer.train_step(states, actions, rewards, next_states, dones)

    def train_short_memory(self, state, action, nagroda, next_state, done):
        self.trainer.train_step(state, action, nagroda, next_state, done)

    def get_action(self, state):
        self.epsilon = 80 - self.n_games #ilośc gier na eksploraacje
        Finałoy_ruch = [0, 0, 0]
        if random.randint(0, 200) < self.epsilon:
            ruch = random.randint(0, 2)
            Finałoy_ruch[ruch] = 1
        else:
            state0 = torch.tensor(state, dtype=torch.float)
            prediction = self.model(state0)
            ruch = torch.argmax(prediction).item()
            Finałoy_ruch[ruch] = 1

        return Finałoy_ruch


def nauczanie():
    plot_scores = []
    plot_mean_scores = []
    total_score = 0
    rekord = 0
    agent = Agent()
    main = wazGra()
    while True:

        state_old = agent.get_state(main)

        Finałoy_ruch = agent.get_action(state_old)

        nagroda, done, wynik = main.krok_gry(Finałoy_ruch)
        state_new = agent.get_state(main)

        agent.train_short_memory(state_old, Finałoy_ruch, nagroda, state_new, done)

        agent.remember(state_old, Finałoy_ruch, nagroda, state_new, done)

        if done:

            main.reset()
            agent.n_games += 1
            agent.train_long_memory()

            if wynik > rekord:
                rekord = wynik
                agent.model.save()

            print('Gra', agent.n_games, 'Wynik:', wynik, 'Record:', rekord)

            plot_scores.append(wynik)
            total_score += wynik
            mean_score = total_score / agent.n_games
            plot_mean_scores.append(mean_score)
            plot(plot_scores, plot_mean_scores)


if __name__ == '__main__':
    nauczanie()