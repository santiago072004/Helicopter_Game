import pygame
from game import Game
from records import get_top_records, save_record  # Cambiado desde load_record

pygame.init()
SCREEN = pygame.display.set_mode((800, 600))
pygame.display.set_caption("Helicopter Shooter - Menú Principal")
FONT = pygame.font.Font(None, 48)
SMALL = pygame.font.Font(None, 28)
clock = pygame.time.Clock()


def draw_text_center(surface, text, y, font, color=(255, 255, 255)):
    surf = font.render(text, True, color)
    surface.blit(surf, (surface.get_width() // 2 - surf.get_width() // 2, y))


def input_name_screen():
    """Pantalla para que el jugador escriba su nombre antes de jugar."""
    name = ""
    active = True
    while active:
        SCREEN.fill((18, 24, 40))
        draw_text_center(SCREEN, "Ingresa tu nombre (ENTER para aceptar)", 140, FONT, (180, 220, 255))

        # cuadro de texto
        box = pygame.Rect(200, 260, 400, 60)
        pygame.draw.rect(SCREEN, (255, 255, 255), box, 2)
        name_surf = FONT.render(name or "Jugador", True, (255, 255, 255))
        SCREEN.blit(name_surf, (box.x + 10, box.y + 8))

        draw_text_center(SCREEN, "ESC para volver al menú", 360, SMALL, (200, 200, 200))

        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                return None
            if event.type == pygame.KEYDOWN:
                if event.key == pygame.K_RETURN:
                    return name.strip() or "Jugador"
                elif event.key == pygame.K_ESCAPE:
                    return None
                elif event.key == pygame.K_BACKSPACE:
                    name = name[:-1]
                else:
                    if len(event.unicode) == 1 and len(name) < 16:
                        name += event.unicode

        pygame.display.flip()
        clock.tick(30)


def show_record_screen():
    """Mostrar los últimos 5 récords de jugadores"""
    SCREEN.fill((12, 18, 30))
    all_records = get_top_records(1000)  # traer todos los registros
    draw_text_center(SCREEN, "Últimos Récords", 80, FONT, (255, 215, 120))

    if not all_records:
        draw_text_center(SCREEN, "Aún no hay récords", 200, FONT)
    else:
        # Tomamos los últimos 5 registros
        last_records = all_records[-5:]
        start_y = 180
        for i, rec in enumerate(last_records):
            y = start_y + i * 40
            draw_text_center(SCREEN, f"{rec['name']} — {rec['score']}", y, SMALL, (255, 255, 255))

    draw_text_center(SCREEN, "Presiona ESC para volver al menú", 500, SMALL, (180, 180, 180))

    waiting = True
    while waiting:
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                waiting = False
            if event.type == pygame.KEYDOWN and event.key == pygame.K_ESCAPE:
                waiting = False
        pygame.display.flip()
        clock.tick(30)


def main_menu():
    options = ["Iniciar juego", "Ver récords", "Salir"]
    selected = 0
    running = True
    while running:
        SCREEN.fill((8, 14, 30))
        draw_text_center(SCREEN, "🚁 Helicopter Shooter 🚁", 80, FONT, (120, 200, 255))

        for i, opt in enumerate(options):
            color = (255, 215, 0) if i == selected else (255, 255, 255)
            draw_text_center(SCREEN, opt, 200 + i * 80, FONT, color)

        draw_text_center(SCREEN, "Usa ARRIBA/ABAJO y ENTER para elegir", 500, SMALL, (180, 180, 180))

        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                running = False
            if event.type == pygame.KEYDOWN:
                if event.key == pygame.K_UP:
                    selected = (selected - 1) % len(options)
                elif event.key == pygame.K_DOWN:
                    selected = (selected + 1) % len(options)
                elif event.key == pygame.K_RETURN:
                    if selected == 0:
                        player_name = input_name_screen()
                        if player_name is not None:
                            Game(player_name).run()
                    elif selected == 1:
                        show_record_screen()
                    elif selected == 2:
                        running = False

        pygame.display.flip()
        clock.tick(30)

    pygame.quit()


if __name__ == "__main__":
    main_menu()
