# /// script
# requires-python = ">=3.10"
# dependencies = [
#     "gymnasium",
#     "numpy",
#     "pygame",
#     "tensorflow-cpu",
#     "matplotlib"
# ]
# ///

import gymnasium as gym
from gymnasium import spaces
import numpy as np
import pygame
import random
import tensorflow as tf
from collections import deque
import matplotlib.pyplot as plt
import sys
import os

# Potlačení TensorFlow logů (aby to nevypisovalo zbytečné info o GPU)
os.environ['TF_CPP_MIN_LOG_LEVEL'] = '2'

try:
    import nastaveni
except ImportError:
    # Fallback pokud chybí soubor nastaveni.py
    class NastaveniDefault:
        PENALE_ZA_KROK = -0.1
        PENALE_ZA_ZED = -10
        PENALE_ZA_OCAS = -10
        PENALE_ZA_HLAD = -5
        MAX_KROKU_BEZ_JIDLA = 100
        ODMENA_ZA_JIDLO = 10
        CILOVY_POCET_JABLEK = 20
        ODMENA_ZA_VYHRU = 50
        RYCHLOST_HRY_NA_KONCI = 15
        UKAZKA_KAZDYCH_N_HER = 50
        CELKOVY_POCET_HER = 200
    nastaveni = NastaveniDefault()
    print("⚠️ UPOZORNĚNÍ: Soubor 'nastaveni.py' nebyl nalezen. Používám výchozí hodnoty.")

# Globální proměnné
REKORD_JABLEK = 0
NAZEV_MODELU = "muj_vytrenovany_had_tf.keras" # Formát Keras

class SnakeEnv(gym.Env):
    def __init__(self):
        super(SnakeEnv, self).__init__()
        self.grid_size = 20
        self.window_size = 600
        self.action_space = spaces.Discrete(4)
        self.observation_space = spaces.Box(low=0, high=1, shape=(8,), dtype=np.float32)
        self.screen = None
        self.clock = None
        self.pocet_jablek = 0 
        self.kroky_bez_jidla = 0
        self.rezim_nekonecna = False 
        
    def reset(self, seed=None, options=None):
        super().reset(seed=seed)
        self.snake = [[self.grid_size // 2, self.grid_size // 2]]
        self.direction = 3 
        self._spawn_food()
        self.pocet_jablek = 0 
        self.kroky_bez_jidla = 0
        return self._get_obs(), {}

    def _spawn_food(self):
        while True:
            self.food = [random.randint(0, self.grid_size-1), random.randint(0, self.grid_size-1)]
            if self.food not in self.snake: break

    def _get_obs(self):
        head = self.snake[0]
        def is_danger(x, y):
            if x < 0 or x >= self.grid_size or y < 0 or y >= self.grid_size: return 1.0
            if [x, y] in self.snake: return 1.0
            return 0.0

        danger_up    = is_danger(head[0], head[1] - 1)
        danger_down  = is_danger(head[0], head[1] + 1)
        danger_left  = is_danger(head[0] - 1, head[1])
        danger_right = is_danger(head[0] + 1, head[1])

        food_up    = 1.0 if self.food[1] < head[1] else 0.0
        food_down  = 1.0 if self.food[1] > head[1] else 0.0
        food_left  = 1.0 if self.food[0] < head[0] else 0.0
        food_right = 1.0 if self.food[0] > head[0] else 0.0

        return np.array([
            danger_up, danger_down, danger_left, danger_right,
            food_up, food_down, food_left, food_right
        ], dtype=np.float32)

    def step(self, action):
        head = list(self.snake[0])
        
        # Ochrana proti otočení o 180 stupňů
        if (action == 0 and self.direction != 1): self.direction = 0
        elif (action == 1 and self.direction != 0): self.direction = 1
        elif (action == 2 and self.direction != 3): self.direction = 2
        elif (action == 3 and self.direction != 2): self.direction = 3

        if self.direction == 0: head[1] -= 1 # Nahoru
        if self.direction == 1: head[1] += 1 # Dolů
        if self.direction == 2: head[0] -= 1 # Doleva
        if self.direction == 3: head[0] += 1 # Doprava
        
        self.kroky_bez_jidla += 1
        game_over = False
        reward = nastaveni.PENALE_ZA_KROK 
        info_dict = {}

        hit_wall = (head[0] < 0 or head[0] >= self.grid_size or head[1] < 0 or head[1] >= self.grid_size)
        hit_self = (head in self.snake)

        if hit_wall or hit_self:
            game_over = True
            info_dict["skore_na_konci"] = self.pocet_jablek
            if hit_wall: reward = nastaveni.PENALE_ZA_ZED
            elif hit_self: reward = nastaveni.PENALE_ZA_OCAS
        
        elif self.kroky_bez_jidla > nastaveni.MAX_KROKU_BEZ_JIDLA:
            game_over = True
            reward = nastaveni.PENALE_ZA_HLAD
            info_dict["skore_na_konci"] = self.pocet_jablek
            
        else:
            self.snake.insert(0, head)
            if head == self.food:
                reward = nastaveni.ODMENA_ZA_JIDLO
                self.pocet_jablek += 1
                self.kroky_bez_jidla = 0 
                global REKORD_JABLEK
                if self.pocet_jablek > REKORD_JABLEK:
                    REKORD_JABLEK = self.pocet_jablek
                
                if not self.rezim_nekonecna and self.pocet_jablek >= nastaveni.CILOVY_POCET_JABLEK:
                    game_over = True
                    reward += nastaveni.ODMENA_ZA_VYHRU
                    info_dict["skore_na_konci"] = self.pocet_jablek
                    info_dict["vyhra"] = True
                else:
                    self._spawn_food()
            else:
                self.snake.pop()

        return self._get_obs(), reward, game_over, False, info_dict

    def render(self):
        if self.screen is None:
            pygame.init()
            self.screen = pygame.display.set_mode((self.window_size, self.window_size))
            self.clock = pygame.time.Clock()
            caption = "Snake AI (TensorFlow) - Divák" if self.rezim_nekonecna else "Snake AI (TensorFlow) - Trénink"
            pygame.display.set_caption(caption)
            
        self.screen.fill((0, 0, 0))
        block_size = self.window_size // self.grid_size
        
        # Kreslení jídla
        pygame.draw.rect(self.screen, (255, 0, 0), (self.food[0]*block_size, self.food[1]*block_size, block_size, block_size))
        
        # Kreslení hada
        for i, segment in enumerate(self.snake):
            color = (0, 255, 0) if i > 0 else (150, 255, 150)
            pygame.draw.rect(self.screen, color, (segment[0]*block_size, segment[1]*block_size, block_size, block_size))
        
        # Texty
        font = pygame.font.SysFont("Arial", 24)
        limit_text = "(Nekonečno)" if self.rezim_nekonecna else f"/{nastaveni.CILOVY_POCET_JABLEK}"
        text_skore = font.render(f'Jablka: {self.pocet_jablek} {limit_text}', True, (255, 255, 255))
        text_rekord = font.render(f'REKORD: {REKORD_JABLEK}', True, (255, 215, 0))
        
        self.screen.blit