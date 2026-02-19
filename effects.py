import pygame
import numpy as np
import math
import random
from dataclasses import dataclass
from typing import Tuple, List

pygame.mixer.init()


@dataclass
class Particle:
    x: float
    y: float
    vx: float
    vy: float
    life: int
    color: Tuple[int, int, int]
    size: float


class ParticleSystem:
    def __init__(self):
        self.particles: List[Particle] = []

    def add_explosion(self, x, y, intensity=20):
        for _ in range(intensity):
            angle = random.uniform(0, 2 * math.pi)
            speed = random.uniform(2, 8)
            self.particles.append(Particle(
                x, y,
                math.cos(angle) * speed,
                math.sin(angle) * speed,
                random.randint(30, 60),
                random.choice([(255, 69, 0), (255, 215, 0), (255, 255, 0)]),
                random.uniform(3, 8)
            ))

    def update(self):
        for p in self.particles[:]:
            p.x += p.vx
            p.y += p.vy
            p.vy += 0.1
            p.life -= 1
            p.size *= 0.97
            if p.life <= 0 or p.size < 0.5:
                self.particles.remove(p)

    def draw(self, screen):
        for p in self.particles:
            surf = pygame.Surface((p.size * 2, p.size * 2), pygame.SRCALPHA)
            pygame.draw.circle(surf, (*p.color, 200), (int(p.size), int(p.size)), int(p.size))
            screen.blit(surf, (p.x - p.size, p.y - p.size))


class SoundManager:
    @staticmethod
    def _make_sound(arr):
        try:
            return pygame.sndarray.make_sound(arr)
        except:
            return None

    @staticmethod
    def generate_shoot_sound():
        sample_rate = 22050
        n = int(0.1 * sample_rate)
        arr = np.zeros((n, 2), dtype=np.int16)
        for i in range(n):
            t = i / sample_rate
            freq = 800 - i / n * 200
            value = int(32767 * 0.25 * math.sin(2 * math.pi * freq * t))
            arr[i] = [value, value]
        return SoundManager._make_sound(arr)

    @staticmethod
    def generate_explosion_sound():
        sample_rate = 22050
        n = int(0.3 * sample_rate)
        arr = np.zeros((n, 2), dtype=np.int16)
        for i in range(n):
            decay = 1 - i / n
            value = int(32767 * 0.4 * decay * (random.random() * 2 - 1))
            arr[i] = [value, value]
        return SoundManager._make_sound(arr)

    @staticmethod
    def generate_coin_sound():
        sample_rate = 22050
        n = int(0.15 * sample_rate)
        arr = np.zeros((n, 2), dtype=np.int16)
        for i in range(n):
            t = i / sample_rate
            freq = 500 + i / n * 300
            value = int(32767 * 0.2 * math.sin(2 * math.pi * freq * t))
            arr[i] = [value, value]
        return SoundManager._make_sound(arr)
