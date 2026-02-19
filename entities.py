import pygame
import math
import random

SCREEN_WIDTH = 1200
SCREEN_HEIGHT = 700

# Colores
HELICOPTER_BODY = (60, 60, 60)
HELICOPTER_ACCENT = (255, 69, 0)
BULLET_COLOR = (255, 215, 0)
ENEMY_RED = (220, 20, 60)
GROUND_GREEN = (34, 139, 34)
DARK_GREEN = (0, 100, 0)
COIN_GOLD = (255, 215, 0)
STONE_GRAY = (100, 100, 100)
STONE_DARK = (60, 60, 60)
STONE_LIGHT = (150, 150, 150)


class Helicopter:
    def __init__(self, x, y):
        self.x = x
        self.y = y
        self.width = 60
        self.height = 30
        self.velocity_y = 0
        self.velocity_x = 0
        self.health = 100
        self.max_health = 100
        self.rotor_angle = 0
        self.tilt = 0

    def update(self, keys):
        # Movimiento vertical
        if keys[pygame.K_UP] or keys[pygame.K_w]:
            self.velocity_y -= 0.45
            self.tilt = -5
        elif keys[pygame.K_DOWN] or keys[pygame.K_s]:
            self.velocity_y += 0.45
            self.tilt = 5
        else:
            self.velocity_y *= 0.96
            self.tilt *= 0.9

        # Movimiento horizontal
        if keys[pygame.K_RIGHT] or keys[pygame.K_d]:
            self.velocity_x = min(self.velocity_x + 0.25, 5)
        elif keys[pygame.K_LEFT] or keys[pygame.K_a]:
            self.velocity_x = max(self.velocity_x - 0.25, -3)
        else:
            self.velocity_x *= 0.96

        # Gravedad más suave
        self.velocity_y += 0.25
        self.velocity_y = max(-7, min(7, self.velocity_y))

        # Actualiza posición
        self.y += self.velocity_y
        self.x += self.velocity_x

        # Limita dentro de la pantalla
        self.y = max(50, min(SCREEN_HEIGHT - 100, self.y))
        self.x = max(50, min(SCREEN_WIDTH - 100, self.x))

        # Rotor
        self.rotor_angle = (self.rotor_angle + 20) % 360

    def draw(self, screen):
        # Cuerpo
        body_rect = pygame.Rect(self.x - 25, self.y - 10, 50, 20)
        pygame.draw.ellipse(screen, HELICOPTER_BODY, body_rect)
        pygame.draw.ellipse(screen, (40, 40, 40), body_rect, 2)

        # Cabina
        cockpit_rect = pygame.Rect(self.x + 10, self.y - 8, 15, 16)
        pygame.draw.ellipse(screen, (100, 150, 200), cockpit_rect)
        pygame.draw.ellipse(screen, (200, 220, 255),
                            pygame.Rect(self.x + 12, self.y - 6, 8, 8))

        # Cola
        tail_points = [
            (self.x - 25, self.y),
            (self.x - 45, self.y - 5),
            (self.x - 45, self.y + 5)
        ]
        pygame.draw.polygon(screen, HELICOPTER_BODY, tail_points)

        # Rotor trasero
        tail_rotor_x = self.x - 45
        tail_rotor_y = self.y
        pygame.draw.line(screen, HELICOPTER_ACCENT,
                         (tail_rotor_x - 5, tail_rotor_y - 8),
                         (tail_rotor_x - 5, tail_rotor_y + 8), 2)

        # Rotor principal
        rotor_center_x = self.x
        rotor_center_y = self.y - 15
        for i in range(2):
            angle = math.radians(self.rotor_angle + i * 180)
            end_x = rotor_center_x + math.cos(angle) * 40
            end_y = rotor_center_y + math.sin(angle) * 8
            pygame.draw.line(screen, (80, 80, 80),
                             (rotor_center_x, rotor_center_y),
                             (end_x, end_y), 3)

        pygame.draw.circle(screen, HELICOPTER_ACCENT,
                           (int(rotor_center_x), int(rotor_center_y)), 5)

        # Patines
        skid_y = self.y + 12
        pygame.draw.line(screen, (60, 60, 60),
                         (self.x - 20, skid_y), (self.x + 20, skid_y), 3)
        pygame.draw.line(screen, (60, 60, 60),
                         (self.x - 20, self.y + 5), (self.x - 20, skid_y), 2)
        pygame.draw.line(screen, (60, 60, 60),
                         (self.x + 20, self.y + 5), (self.x + 20, skid_y), 2)
        pygame.draw.line(screen, HELICOPTER_ACCENT,
                         (self.x - 20, self.y), (self.x + 20, self.y), 2)

    def draw_health_bar(self, screen):
        bar_width = 60
        bar_height = 6
        bar_x = self.x - bar_width // 2
        bar_y = self.y - 30
        pygame.draw.rect(screen, (100, 100, 100),
                         (bar_x, bar_y, bar_width, bar_height))
        health_width = int((self.health / self.max_health) * bar_width)
        health_color = (0, 255, 0) if self.health > 50 else (255, 255, 0) if self.health > 25 else (255, 0, 0)
        pygame.draw.rect(screen, health_color,
                         (bar_x, bar_y, health_width, bar_height))
        pygame.draw.rect(screen, (255, 255, 255),
                         (bar_x, bar_y, bar_width, bar_height), 1)

    def get_rect(self):
        return pygame.Rect(self.x - 25, self.y - 10, 50, 20)


class Bullet:
    def __init__(self, x, y):
        self.x = x
        self.y = y
        self.speed = 12
        self.radius = 12

    def update(self):
        self.x += self.speed

    def draw(self, screen):
        pygame.draw.circle(screen, BULLET_COLOR,
                           (int(self.x), int(self.y)), self.radius)

    def get_rect(self):
        return pygame.Rect(self.x - self.radius, self.y - self.radius,
                           self.radius * 2, self.radius * 2)


class Obstacle:
    """Pilares desde el suelo (ya no flotan)"""
    def __init__(self, x, height):
        self.x = x
        self.height = height
        self.width = 60
        self.speed = 2.5  # más lento

    def update(self):
        self.x -= self.speed

    def draw(self, screen):
        # Posición desde el suelo
        y_base = SCREEN_HEIGHT - 50
        y_top = y_base - self.height

        # Bloque principal
        pygame.draw.rect(screen, STONE_GRAY,
                         (self.x, y_top, self.width, self.height))

        # Sombra lateral derecha
        pygame.draw.rect(screen, STONE_DARK,
                         (self.x + self.width - 5, y_top, 5, self.height))

        # Luz lateral izquierda
        pygame.draw.rect(screen, STONE_LIGHT,
                         (self.x, y_top, 5, self.height))

        # Borde superior
        pygame.draw.rect(screen, (180, 180, 180),
                         (self.x, y_top, self.width, 4))

    def get_rect(self):
        y_base = SCREEN_HEIGHT - 50
        y_top = y_base - self.height
        return pygame.Rect(self.x, y_top, self.width, self.height)


class Turret:
    def __init__(self, x, y):
        self.x = x
        self.y = y
        self.width = 40
        self.height = 40
        self.speed = 2.5
        self.health = 3
        self.shoot_cooldown = 0
        self.angle = 0

    def update(self, helicopter_x, helicopter_y):
        self.x -= self.speed
        dx = helicopter_x - self.x
        dy = helicopter_y - self.y
        self.angle = math.atan2(dy, dx)
        if self.shoot_cooldown > 0:
            self.shoot_cooldown -= 1

    def can_shoot(self):
        return self.shoot_cooldown == 0

    def shoot(self):
        self.shoot_cooldown = 70
        spawn_x = self.x + math.cos(self.angle) * 20
        spawn_y = self.y + math.sin(self.angle) * 20
        return EnemyBullet(spawn_x, spawn_y, self.angle)

    def draw(self, screen):
        pygame.draw.circle(screen, ENEMY_RED, (int(self.x), int(self.y)), 15)
        barrel_length = 25
        barrel_end_x = self.x + math.cos(self.angle) * barrel_length
        barrel_end_y = self.y + math.sin(self.angle) * barrel_length
        pygame.draw.line(screen, (150, 150, 150),
                         (self.x, self.y), (barrel_end_x, barrel_end_y), 4)
        for i in range(self.health):
            pygame.draw.circle(screen, (0, 255, 0),
                               (int(self.x - 10 + i * 10), int(self.y - 25)), 3)

    def get_rect(self):
        return pygame.Rect(self.x - 20, self.y - 15, 40, 35)


class EnemyBullet:
    def __init__(self, x, y, angle):
        self.x = x
        self.y = y
        self.angle = angle
        self.speed = 6.5  # más lento para mayor equilibrio
        self.radius = 5

    def update(self):
        self.x += math.cos(self.angle) * self.speed
        self.y += math.sin(self.angle) * self.speed

    def draw(self, screen):
        pygame.draw.circle(screen, ENEMY_RED, (int(self.x), int(self.y)), self.radius)

    def get_rect(self):
        return pygame.Rect(self.x - self.radius, self.y - self.radius,
                           self.radius * 2, self.radius * 2)


class Coin:
    def __init__(self, x, y):
        self.x = x
        self.y = y
        self.radius = 12
        self.speed = 2.5
        self.angle = 0
        self.bob_offset = 0

    def update(self):
        self.x -= self.speed
        self.angle += 5
        self.bob_offset = math.sin(self.angle * 0.1) * 5

    def draw(self, screen):
        y = self.y + self.bob_offset
        pygame.draw.circle(screen, COIN_GOLD, (int(self.x), int(y)), self.radius)
        pygame.draw.circle(screen, (255, 235, 100),
                           (int(self.x), int(y)), self.radius - 3)
        pygame.draw.circle(screen, (200, 170, 0),
                           (int(self.x), int(y)), self.radius, 2)

    def get_rect(self):
        y = self.y + self.bob_offset
        return pygame.Rect(self.x - self.radius, y - self.radius,
                           self.radius * 2, self.radius * 2)

class Medikit:
    def __init__(self, x, y, heal_amount=20):
        self.x = x
        self.y = y
        self.radius = 20
        self.heal_amount = heal_amount

    def update(self):
        self.x -= 3  # se mueve hacia la izquierda

    def draw(self, screen):
        # Círculo rojo con cruz blanca
        pygame.draw.circle(screen, (255, 0, 0), (int(self.x), int(self.y)), self.radius)
        pygame.draw.line(screen, (255, 255, 255), (self.x - 8, self.y), (self.x + 8, self.y), 3)
        pygame.draw.line(screen, (255, 255, 255), (self.x, self.y - 8), (self.x, self.y + 8), 3)

    def get_rect(self):
        return pygame.Rect(self.x - self.radius, self.y - self.radius, self.radius*2, self.radius*2)
