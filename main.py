import os
os.environ["SDL_AUDIODRIVER"] = "pulse"

import pygame
from constants import SCREEN_WIDTH, SCREEN_HEIGHT
from logger import log_state, log_event
from player import Player
from asteroid import Asteroid
from asteroidfield import AsteroidField
from shot import Shot


MENU = "menu"
SETTINGS = "settings"
PLAYING = "playing"


def draw_menu(screen, options, selected_index, font):
    for i, option in enumerate(options):
        color = "yellow" if i == selected_index else "white"
        text = font.render(option, True, color)
        rect = text.get_rect(center=(SCREEN_WIDTH / 2, 250 + i * 70))
        screen.blit(text, rect)


def main():
    pygame.init()
    pygame.mixer.init()

    game_state = MENU
    menu_index = 0
    settings_index = 0

    background_music_on = True
    game_sounds_on = True

    menu_options = ["Start Game", "Settings", "Quit"]

    clock = pygame.time.Clock()
    dt = 0

    screen = pygame.display.set_mode((SCREEN_WIDTH, SCREEN_HEIGHT))

    # -------- BACKGROUNDS --------
    background = pygame.image.load("background.png").convert()
    background = pygame.transform.scale(background, (SCREEN_WIDTH, SCREEN_HEIGHT))

    menu_background = pygame.image.load("menubackground.png").convert()
    menu_background = pygame.transform.scale(menu_background, (SCREEN_WIDTH, SCREEN_HEIGHT))

    settings_background = pygame.image.load("settingsbackground.png").convert()
    settings_background = pygame.transform.scale(settings_background, (SCREEN_WIDTH, SCREEN_HEIGHT))

    font = pygame.font.SysFont(None, 36)

    score = 0
    lives = 3
    game_over = False
    invincible_timer = 0

    # -------- SOUNDS --------
    shoot_sound = pygame.mixer.Sound("shoot.wav")
    explosion_sound = pygame.mixer.Sound("explosion.wav")

    shoot_sound.set_volume(0.3)
    explosion_sound.set_volume(0.5)

    pygame.mixer.music.load("background.wav")
    pygame.mixer.music.set_volume(0.2)
    pygame.mixer.music.play(-1)

    was_shooting = False

    # -------- GROUPS --------
    updatable = pygame.sprite.Group()
    drawable = pygame.sprite.Group()
    asteroids = pygame.sprite.Group()
    shots = pygame.sprite.Group()

    Player.containers = (updatable, drawable)
    Asteroid.containers = (asteroids, updatable, drawable)
    AsteroidField.containers = (updatable,)
    Shot.containers = (shots, updatable, drawable)

    player = Player(SCREEN_WIDTH / 2, SCREEN_HEIGHT / 2)
    AsteroidField()

    def reset_game():
        nonlocal score, lives, game_over, invincible_timer

        score = 0
        lives = 3
        game_over = False
        invincible_timer = 0

        player.position.x = SCREEN_WIDTH / 2
        player.position.y = SCREEN_HEIGHT / 2

        for asteroid in asteroids:
            asteroid.kill()

        for shot in shots:
            shot.kill()

        AsteroidField()

    print(f"Starting Asteroids with pygame version: {pygame.version.ver}")

    # -------- GAME LOOP --------
    while True:
        log_state()

        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                return

            if event.type == pygame.KEYDOWN:

                # -------- MENU --------
                if game_state == MENU:
                    if event.key == pygame.K_UP:
                        menu_index -= 1

                    if event.key == pygame.K_DOWN:
                        menu_index += 1

                    menu_index %= len(menu_options)

                    if event.key in (pygame.K_RETURN, pygame.K_KP_ENTER):
                        if menu_options[menu_index] == "Start Game":
                            game_state = PLAYING

                        elif menu_options[menu_index] == "Settings":
                            game_state = SETTINGS

                        elif menu_options[menu_index] == "Quit":
                            return

                # -------- SETTINGS --------
                elif game_state == SETTINGS:
                    if event.key == pygame.K_UP:
                        settings_index -= 1

                    if event.key == pygame.K_DOWN:
                        settings_index += 1

                    settings_index %= 3

                    if event.key in (pygame.K_RETURN, pygame.K_KP_ENTER):
                        if settings_index == 0:
                            background_music_on = not background_music_on

                            if background_music_on:
                                pygame.mixer.music.play(-1)
                            else:
                                pygame.mixer.music.stop()

                        elif settings_index == 1:
                            game_sounds_on = not game_sounds_on

                        elif settings_index == 2:
                            game_state = MENU

                # -------- RESET --------
                elif game_state == PLAYING:
                    if event.key == pygame.K_SPACE and game_over:
                        reset_game()
                        game_state = MENU

        keys = pygame.key.get_pressed()

        # -------- DRAW BACKGROUND --------
        if game_state == MENU:
            screen.blit(menu_background, (0, 0))

        elif game_state == SETTINGS:
            screen.blit(settings_background, (0, 0))

        elif game_state == PLAYING:
            screen.blit(background, (0, 0))

        # -------- MENU DRAW --------
        if game_state == MENU:
            draw_menu(screen, menu_options, menu_index, font)

        # -------- SETTINGS DRAW --------
        elif game_state == SETTINGS:
            settings_options = [
                f"Background Music: {'ON' if background_music_on else 'OFF'}",
                f"Game Sounds: {'ON' if game_sounds_on else 'OFF'}",
                "Back",
            ]

            draw_menu(screen, settings_options, settings_index, font)

        # -------- GAME --------
        elif game_state == PLAYING:

            if keys[pygame.K_SPACE] and not was_shooting and not game_over:
                if game_sounds_on:
                    shoot_sound.play()

            was_shooting = keys[pygame.K_SPACE]

            if not game_over:
                updatable.update(dt)

            if invincible_timer > 0:
                invincible_timer -= dt

            if not game_over:
                for asteroid in asteroids:
                    if asteroid.collides_with(player) and invincible_timer <= 0:
                        log_event("player_hit")
                        lives -= 1
                        invincible_timer = 2
                        asteroid.kill()

                        if lives <= 0:
                            game_over = True

                    for shot in shots:
                        if asteroid.collides_with(shot):
                            if game_sounds_on:
                                explosion_sound.play()

                            log_event("asteroid_shot")
                            score += 100
                            asteroid.split()
                            shot.kill()

            for thing in drawable:
                thing.draw(screen)

            score_text = font.render(f"Score: {score}", True, "white")
            screen.blit(score_text, (20, 20))

            lives_text = font.render(f"Lives: {lives}", True, "white")
            screen.blit(lives_text, (20, 55))

            if game_over:
                game_over_text = font.render(
                    "GAME OVER - Press SPACE for Menu",
                    True,
                    "white"
                )
                screen.blit(game_over_text, (SCREEN_WIDTH / 2 - 250, SCREEN_HEIGHT / 2))

        pygame.display.flip()
        dt = clock.tick(60) / 1000


if __name__ == "__main__":
    main()