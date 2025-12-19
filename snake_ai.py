# /// script
# requires-python = ">=3.10"
# dependencies = [
#     "gymnasium",
#     "numpy",
#     "pygame",
#     "shimmy",
#     "stable-baselines3",
#     "torch",
#     "matplotlib"
# ]
# [tool.uv.sources]
# torch = { index = "pytorch-cpu" }
# [[tool.uv.index]]
# name = "pytorch-cpu"
# url = "https://download.pytorch.org/whl/cpu"
# ///

import gymnasium as gym
from gymnasium import spaces
import numpy as np
import pygame
import random
from stable_baselines3 import PPO
from stable_baselines3.common.callbacks import BaseCallback
import matplotlib.pyplot as plt
import sys
import os

try:
    import nastaveni
except ImportError:
    print("CHYBA: Chybí soubor 'nastaveni.py'!")
    sys.exit()

# Globální proměnná pro rekord
REKORD_JABLEK = 0
NAZEV_MODELU = "muj_vytrenovany_had.zip"

class SledovacHer(BaseCallback):
    def __init__(self, limit_her_pro_kolo, verbose=0):
        super(SledovacHer, self).__init__(verbose)
        self.historie_jablek = []
        self.limit_her = limit_her_pro_kolo
        self.hry_v_tomto_kole = 0

    def _on_step(self) -> bool:
        if "dones" in self.locals and self.locals["dones"][0]:
            self.hry_v_tomto_kole += 1
            info = self.locals["infos"][0]
            if "skore_na_konci" in info:
                self.historie_jablek.append(info["skore_na_konci"])
            
            if self.hry_v_tomto_kole >= self.limit_her:
                return False 
        return True

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
        if (action == 0 and self.direction != 1): self.direction = 0
        elif (action == 1 and self.direction != 0): self.direction = 1
        elif (action == 2 and self.direction != 3): self.direction = 2
        elif (action == 3 and self.direction != 2): self.direction = 3

        if self.direction == 0: head[1] -= 1
        if self.direction == 1: head[1] += 1
        if self.direction == 2: head[0] -= 1
        if self.direction == 3: head[0] += 1
        
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
            
            if self.rezim_nekonecna:
                pygame.display.set_caption("Snake AI - Režim diváka (Bez limitu)")
            else:
                pygame.display.set_caption("Snake AI - Trénink")
            
        self.screen.fill((0, 0, 0))
        block_size = self.window_size // self.grid_size
        pygame.draw.rect(self.screen, (255, 0, 0), (self.food[0]*block_size, self.food[1]*block_size, block_size, block_size))
        for i, segment in enumerate(self.snake):
            color = (0, 255, 0) if i > 0 else (150, 255, 150)
            pygame.draw.rect(self.screen, color, (segment[0]*block_size, segment[1]*block_size, block_size, block_size))
        
        font = pygame.font.SysFont("Arial", 24)
        
        if self.rezim_nekonecna:
            text_skore = font.render(f'Jablka: {self.pocet_jablek} (Nekonečno)', True, (255, 255, 255))
        else:
            text_skore = font.render(f'Jablka: {self.pocet_jablek}/{nastaveni.CILOVY_POCET_JABLEK}', True, (255, 255, 255))
            
        text_rekord = font.render(f'REKORD: {REKORD_JABLEK}', True, (255, 215, 0))
        color_hlad = (100, 100, 255) if self.kroky_bez_jidla < nastaveni.MAX_KROKU_BEZ_JIDLA * 0.8 else (255, 50, 50)
        text_hlad = font.render(f'Hlad: {self.kroky_bez_jidla}/{nastaveni.MAX_KROKU_BEZ_JIDLA}', True, color_hlad)

        self.screen.blit(text_skore, (10, 10))
        self.screen.blit(text_rekord, (10, 40))
        self.screen.blit(text_hlad, (10, 70))
        pygame.display.flip()
        self.clock.tick(nastaveni.RYCHLOST_HRY_NA_KONCI)

    def close(self):
        if self.screen is not None:
            pygame.quit()
            self.screen = None

def vykreslit_graf(data):
    try:
        if not data: return
        print("\n📊 Generuji graf...")
        plt.figure(figsize=(10, 6))
        plt.plot(data, label='Skóre', color='green', alpha=0.4)
        window_size = 10
        if len(data) > window_size:
            avg_data = np.convolve(data, np.ones(window_size)/window_size, mode='valid')
            plt.plot(range(window_size-1, len(data)), avg_data, label=f'Průměr', color='red', linewidth=2)
        plt.axhline(y=nastaveni.CILOVY_POCET_JABLEK, color='blue', linestyle='--', label='Cíl')
        plt.title('Vývoj inteligence hada')
        plt.xlabel('Počet her')
        plt.ylabel('Jablka')
        plt.legend()
        plt.grid(True)
        plt.show()
    except Exception as e:
        print(f"Chyba grafu: {e}")

def spustit_ukazku(env, model, cislo_hry):
    print(f"\n🎥 UKÁZKA (po {cislo_hry} hrách)")
    obs, _ = env.reset()
    while True:
        action, _ = model.predict(obs)
        obs, reward, done, truncated, info = env.step(action)
        env.render()
        
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                env.close(); return False 
        
        if done:
            if info.get("vyhra", False):
                print(f"\n🏆 VÍTĚZSTVÍ! Cíl splněn!")
                print("---------------------------------------------")
                volba = input("Co dál? (ENTER = Pokračovat v učení, S = Stop a Uložit): ").strip().lower()
                print("---------------------------------------------")
                if volba == 's':
                    return True 
            break
    env.close()
    return False

if __name__ == "__main__":
    env = SnakeEnv()
    
    print("\n" + "="*50)
    print("🐍 SNAKE AI TRENER - STUDENT EDITION 🐍")
    print("="*50)
    print("1. Začít trénovat nového hada (od nuly)")
    print("2. Nahrát uloženého hada")
    volba_start = input("\nVyberte možnost (1 nebo 2): ").strip()
    
    model = None
    rezim_jen_koukat = False 
    
    if volba_start == "2":
        if os.path.exists(NAZEV_MODELU):
            print(f"✅ Načítám mozek ze souboru: {NAZEV_MODELU}")
            model = PPO.load(NAZEV_MODELU, env=env)
            
            print("\nCo chcete s načteným hadem dělat?")
            print("   1 = Pokračovat v tréninku (zlepšovat ho)")
            print("   2 = Jen se dívat (režim divák - nekonečná hra)")
            podvolba = input("Vyberte (1/2): ").strip()
            
            if podvolba == '2':
                rezim_jen_koukat = True
                print("👀 Zapínám režim divák (Resetuji rekord, vypínám limity).")
                # ZDE SE PŘEPÍNÁ REŽIM DIVÁKA
                env.rezim_nekonecna = True
                REKORD_JABLEK = 0 # Resetujeme rekord pro diváka
            else:
                print("💪 Jdeme dál trénovat!")
                env.rezim_nekonecna = False
        else:
            print(f"❌ Soubor {NAZEV_MODELU} neexistuje! Začínám nový trénink.")
            model = PPO("MlpPolicy", env, verbose=0)
    
    else:
        print("👶 Vytvářím nového hada.")
        model = PPO("MlpPolicy", env, verbose=0)
        env.rezim_nekonecna = False

    if not rezim_jen_koukat:
        limit_her_kolo = getattr(nastaveni, 'UKAZKA_KAZDYCH_N_HER', 10)
        cilove_hry = getattr(nastaveni, 'CELKOVY_POCET_HER', 100)
        sledovac = SledovacHer(limit_her_pro_kolo=limit_her_kolo)
        
        odehrano_celkem = 0
        ukoncit_trenink = False

        print("\n🚀 START TRÉNINKU!")
        
        while odehrano_celkem < cilove_hry:
            print(f"⚙️  Trénuji dalších {limit_her_kolo} her...")
            sledovac.hry_v_tomto_kole = 0
            model.learn(total_timesteps=1_000_000, callback=sledovac)
            odehrano_celkem += sledovac.hry_v_tomto_kole
            
            print(f"   --> Celkem odehráno: {odehrano_celkem}")
            
            if spustit_ukazku(env, model, odehrano_celkem):
                ukoncit_trenink = True
                break

        print("\n💾 Ukládám mozek hada...")
        model.save(NAZEV_MODELU.replace(".zip", "")) 
        print(f"✅ Uloženo do: {NAZEV_MODELU}")
        
        vykreslit_graf(sledovac.historie_jablek)
        
        print("\n🎬 Přepínám do nekonečného režimu pro ukázku...")
        env.rezim_nekonecna = True

    if rezim_jen_koukat:
         print("\n🎬 Spouštím nekonečnou ukázku (žádný trénink)...")
    
    print("   (Zavřete okno křížkem pro úplný konec)")
    
    while True:
        obs, _ = env.reset()
        done = False
        while not done:
            action, _ = model.predict(obs)
            obs, reward, done, truncated, info = env.step(action)
            env.render()
            
            for event in pygame.event.get():
                if event.type == pygame.QUIT:
                    env.close()
                    sys.exit()
