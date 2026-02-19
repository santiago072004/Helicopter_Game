import pygame
import random
from entities import Helicopter, Bullet, Obstacle, Turret, EnemyBullet, Coin, Medikit
from effects import ParticleSystem, SoundManager
from records import save_record

SCREEN_WIDTH = 1200
SCREEN_HEIGHT = 700
FPS = 60

SKY_BLUE = (135, 206, 250)
DARK_BLUE = (25, 25, 112)
GROUND_GREEN = (34, 139, 34)
DARK_GREEN = (0, 100, 0)
CLOUD_WHITE = (255, 255, 255, 200)


class Game:
    def __init__(self, player_name="Jugador"):
        self.player_name = player_name
        self.screen = pygame.display.set_mode((SCREEN_WIDTH, SCREEN_HEIGHT))
        pygame.display.set_caption("Helicopter Shooter")
        self.clock = pygame.time.Clock()
        self.font = pygame.font.Font(None, 36)
        self.small_font = pygame.font.Font(None, 24)

        self.running = True
        self.game_over = False
        self.won = False
        self.paused = False

        # Score y distancia
        self.distance = 0
        self.score = 0
        self.target_distance = 4000  # después puedes hacer infinito

        # Jugador y objetos
        self.helicopter = Helicopter(200, SCREEN_HEIGHT // 2)
        self.bullets = []
        self.obstacles = []
        self.turrets = []
        self.enemy_bullets = []
        self.coins = []
        self.medikits = []

        self.particle_system = ParticleSystem()

        # sonidos
        try:
            self.shoot_sound = SoundManager.generate_shoot_sound()
            self.explosion_sound = SoundManager.generate_explosion_sound()
            self.coin_sound = SoundManager.generate_coin_sound()
        except Exception:
            self.shoot_sound = None
            self.explosion_sound = None
            self.coin_sound = None

        self.shoot_cooldown = 0
        self.spawn_timer = 0
        self.background_offset = 0

        # Nubes
        self.clouds = [
            [random.randint(0, SCREEN_WIDTH), random.randint(50, 200),
             random.randint(100, 180), random.randint(50, 80),
             random.uniform(0.3, 1.0)]
            for _ in range(6)
        ]

    # ---------------------------------------
    # BACKGROUND
    # ---------------------------------------
    def draw_background(self):
        for y in range(SCREEN_HEIGHT - 50):
            ratio = y / (SCREEN_HEIGHT - 50)
            color = (
                int(SKY_BLUE[0] + (DARK_BLUE[0] - SKY_BLUE[0]) * ratio),
                int(SKY_BLUE[1] + (DARK_BLUE[1] - SKY_BLUE[1]) * ratio),
                int(SKY_BLUE[2] + (DARK_BLUE[2] - SKY_BLUE[2]) * ratio)
            )
            pygame.draw.line(self.screen, color, (0, y), (SCREEN_WIDTH, y))

        for cloud in self.clouds:
            x, y, w, h, speed = cloud
            surf = pygame.Surface((w, h), pygame.SRCALPHA)
            pygame.draw.ellipse(surf, CLOUD_WHITE, (0, 0, w, h))
            self.screen.blit(surf, (x, y))
            cloud[0] -= speed
            if cloud[0] < -w:
                cloud[0] = SCREEN_WIDTH + random.randint(0, 200)
                cloud[1] = random.randint(40, 220)

        # Suelo
        pygame.draw.rect(self.screen, GROUND_GREEN, (0, SCREEN_HEIGHT - 50, SCREEN_WIDTH, 50))
        for i in range(0, SCREEN_WIDTH, 100):
            pygame.draw.rect(self.screen, DARK_GREEN,
                             ((i - int(self.background_offset * 2)) % SCREEN_WIDTH,
                              SCREEN_HEIGHT - 50, 50, 50))

    # ---------------------------------------
    # SPAWN OBJECTS
    # ---------------------------------------
    def spawn_objects(self):
        self.spawn_timer += 1
        if self.spawn_timer > 70:
            self.spawn_timer = 0
            if random.random() < 0.35:
                self.obstacles.append(Obstacle(SCREEN_WIDTH, random.randint(70, 180)))
            if random.random() < 0.15:
                self.turrets.append(Turret(SCREEN_WIDTH, random.randint(150, SCREEN_HEIGHT - 180)))
            if random.random() < 0.45:
                self.coins.append(Coin(SCREEN_WIDTH, random.randint(100, SCREEN_HEIGHT - 200)))
            if random.random() < 0.05:
                self.medikits.append(Medikit(SCREEN_WIDTH, random.randint(100, SCREEN_HEIGHT - 150)))

    # ---------------------------------------
    # INPUT
    # ---------------------------------------
    def handle_input(self):
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                if self.game_over or self.won:
                    save_record(self.player_name, self.score, self.distance)
                self.running = False

            if event.type == pygame.KEYDOWN:
                if event.key == pygame.K_p:
                    self.paused = not self.paused

                if not self.paused:
                    if event.key == pygame.K_SPACE and self.shoot_cooldown == 0 and not (self.game_over or self.won):
                        self.bullets.append(Bullet(self.helicopter.x + 30, self.helicopter.y))
                        if self.shoot_sound:
                            try:
                                self.shoot_sound.play()
                            except Exception:
                                pass
                        self.shoot_cooldown = 15

                    if event.key == pygame.K_r and (self.game_over or self.won):
                        save_record(self.player_name, self.score, self.distance)
                        pname = self.player_name
                        self.__init__(pname)

                else:
                    if event.key == pygame.K_r:
                        save_record(self.player_name, self.score, self.distance)
                        pname = self.player_name
                        self.__init__(pname)

    # ---------------------------------------
    # UPDATE
    # ---------------------------------------
    def update(self):
        if self.game_over or self.won or self.paused:
            return

        keys = pygame.key.get_pressed()
        self.helicopter.update(keys)

        # DISTANCIA + SCORE
        self.distance += 1
        self.score = self.distance // 5  # cada 5 píxeles = 1 punto

        if self.distance >= self.target_distance:
            self.won = True

        if self.shoot_cooldown > 0:
            self.shoot_cooldown -= 1

        # Update bullets
        for bullet in self.bullets[:]:
            bullet.update()
            if bullet.x > SCREEN_WIDTH + 50:
                self.bullets.remove(bullet)

        # Update obstáculos
        for obstacle in self.obstacles[:]:
            obstacle.update()
            if obstacle.x < -obstacle.width:
                self.obstacles.remove(obstacle)
            elif self.helicopter.get_rect().colliderect(obstacle.get_rect()):
                self.helicopter.health -= 20
                self.particle_system.add_explosion(self.helicopter.x, self.helicopter.y, 15)
                self.obstacles.remove(obstacle)

        # Update turrets
        for turret in self.turrets[:]:
            turret.update(self.helicopter.x, self.helicopter.y)
            if turret.x < -50:
                self.turrets.remove(turret)
                continue
            if turret.can_shoot() and turret.x < SCREEN_WIDTH - 100:
                self.enemy_bullets.append(turret.shoot())
            for bullet in self.bullets[:]:
                if bullet.get_rect().colliderect(turret.get_rect()):
                    turret.health -= 1
                    self.bullets.remove(bullet)
                    self.particle_system.add_explosion(turret.x, turret.y, 10)
                    if turret.health <= 0:
                        self.turrets.remove(turret)
                        self.score += 50
                        self.particle_system.add_explosion(turret.x, turret.y, 20)

        # Update enemy bullets
        for enemy_bullet in self.enemy_bullets[:]:
            enemy_bullet.update()
            if (enemy_bullet.x < 0 or enemy_bullet.x > SCREEN_WIDTH or
                enemy_bullet.y < 0 or enemy_bullet.y > SCREEN_HEIGHT):
                self.enemy_bullets.remove(enemy_bullet)
            elif self.helicopter.get_rect().colliderect(enemy_bullet.get_rect()):
                self.helicopter.health -= 10
                self.enemy_bullets.remove(enemy_bullet)
                self.particle_system.add_explosion(enemy_bullet.x, enemy_bullet.y, 8)

        # Update coins
        for coin in self.coins[:]:
            coin.update()
            if coin.x < -coin.radius:
                self.coins.remove(coin)
            elif self.helicopter.get_rect().colliderect(coin.get_rect()):
                self.score += 10
                self.coins.remove(coin)
                self.particle_system.add_explosion(coin.x, coin.y, 10)

        # Update medikits
        for medikit in self.medikits[:]:
            medikit.update()
            if medikit.x < -medikit.radius:
                self.medikits.remove(medikit)
            elif self.helicopter.get_rect().colliderect(medikit.get_rect()):
                self.helicopter.health += medikit.heal_amount
                if self.helicopter.health > self.helicopter.max_health:
                    self.helicopter.health = self.helicopter.max_health
                self.medikits.remove(medikit)

        self.particle_system.update()
        self.spawn_objects()

        if self.helicopter.health <= 0:
            self.game_over = True
            self.particle_system.add_explosion(self.helicopter.x, self.helicopter.y, 30)

        self.background_offset = (self.background_offset + 0.5) % SCREEN_WIDTH

    # ---------------------------------------
    # DRAW
    # ---------------------------------------
    def draw(self):
        # Dibujar todo
        self.draw_background()

        for obstacle in self.obstacles:
            obstacle.draw(self.screen)
        for coin in self.coins:
            coin.draw(self.screen)
        for turret in self.turrets:
            turret.draw(self.screen)
        for bullet in self.bullets:
            bullet.draw(self.screen)
        for enemy_bullet in self.enemy_bullets:
            enemy_bullet.draw(self.screen)
        for medikit in self.medikits:
            medikit.draw(self.screen)

        self.particle_system.draw(self.screen)

        if not self.game_over:
            self.helicopter.draw(self.screen)
            self.helicopter.draw_health_bar(self.screen)

        self.draw_ui()

        # Pausa
        if self.paused:
            overlay = pygame.Surface((SCREEN_WIDTH, SCREEN_HEIGHT), pygame.SRCALPHA)
            overlay.fill((0, 0, 0, 160))
            self.screen.blit(overlay, (0, 0))
            t = self.font.render("PAUSA", True, (255, 255, 255))
            t2 = self.small_font.render("Presiona P para continuar — R para reiniciar", True, (200, 200, 200))
            self.screen.blit(t, (SCREEN_WIDTH // 2 - t.get_width() // 2, 280))
            self.screen.blit(t2, (SCREEN_WIDTH // 2 - t2.get_width() // 2, 340))

        # Game Over
        if self.game_over:
            save_record(self.player_name, self.score, self.distance)
            overlay = pygame.Surface((SCREEN_WIDTH, SCREEN_HEIGHT), pygame.SRCALPHA)
            overlay.fill((0, 0, 0, 180))
            self.screen.blit(overlay, (0, 0))
            self.show_message("GAME OVER", "Presiona R para reiniciar")

        # Ganaste
        if self.won:
            save_record(self.player_name, self.score, self.distance)
            overlay = pygame.Surface((SCREEN_WIDTH, SCREEN_HEIGHT), pygame.SRCALPHA)
            overlay.fill((0, 0, 0, 180))
            self.screen.blit(overlay, (0, 0))
            self.show_message("¡GANASTE!", "Presiona R para volver a jugar")

        pygame.display.flip()

    # ---------------------------------------
    # UI
    # ---------------------------------------
    def draw_ui(self):
        score_text = self.font.render(f"{self.player_name} — Score: {self.score}", True, (255, 255, 255))
        self.screen.blit(score_text, (20, 20))
        distance_text = self.small_font.render(f"Distancia: {self.distance}/{self.target_distance}", True, (255, 255, 255))
        self.screen.blit(distance_text, (20, 55))
        pause_hint = self.small_font.render("P = Pausa  |  R = Reiniciar cuando pierdas", True, (200, 200, 200))
        self.screen.blit(pause_hint, (20, SCREEN_HEIGHT - 40))

    def show_message(self, line1, line2):
        t1 = self.font.render(line1, True, (255, 255, 255))
        t2 = self.small_font.render(line2, True, (255, 255, 255))
        self.screen.blit(t1, (SCREEN_WIDTH // 2 - t1.get_width() // 2, 300))
        self.screen.blit(t2, (SCREEN_WIDTH // 2 - t2.get_width() // 2, 360))

    # ---------------------------------------
    # RUN
    # ---------------------------------------
    def run(self):
        while self.running:
            self.handle_input()
            self.update()
            self.draw()
            self.clock.tick(FPS)
