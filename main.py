import os
os.environ["SDL_AUDIODRIVER"] = "pulse"

import pygame
import json
from constants import SCREEN_WIDTH, SCREEN_HEIGHT
from logger import log_state, log_event
from player import Player
from asteroid import Asteroid
from asteroidfield import AsteroidField
from shot import Shot


MENU = "menu"
SETTINGS = "settings"
PLAYING = "playing"
ENTER_HIGH_SCORE = "enter_high_score"
HIGH_SCORES = "high_scores"


def draw_menu(screen, options, selected_index, font):
    for i, option in enumerate(options):
        color = "yellow" if i == selected_index else "white"
        text = font.render(option, True, color)
        rect = text.get_rect(center=(SCREEN_WIDTH / 2, 250 + i * 70))
        screen.blit(text, rect)


def load_high_scores():
    try:
        with open("high_scores.json", "r") as file:
            return json.load(file)
    except FileNotFoundError:
        return []


def save_high_scores(high_scores):
    with open("high_scores.json", "w") as file:
        json.dump(high_scores, file, indent=4)


def add_high_score(name, score):
    high_scores = load_high_scores()

    high_scores.append({
        "name": name,
        "score": score
    })

    high_scores.sort(key=lambda entry: entry["score"], reverse=True)
    high_scores = high_scores[:10]

    save_high_scores(high_scores)


def main():
    pygame.mixer.pre_init(44100, -16, 2, 512)

    pygame.init()
    pygame.mixer.init()

    game_state = MENU
    menu_index = 0
    settings_index = 0
    player_name = ""
    score_saved = False

    background_music_on = True
    game_sounds_on = True

    menu_options = ["Start Game", "Settings", "High Scores", "Quit"]

    clock = pygame.time.Clock()
    dt = 0

    screen = pygame.display.set_mode((SCREEN_WIDTH, SCREEN_HEIGHT))

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

    shoot_sound = pygame.mixer.Sound("shoot.wav")
    explosion_sound = pygame.mixer.Sound("explosion.wav")

    shoot_sound.set_volume(0.3)
    explosion_sound.set_volume(0.5)

    pygame.mixer.music.load("background.wav")
    pygame.mixer.music.set_volume(0.2)
    pygame.mixer.music.play(-1)

    was_shooting = False

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

    while True:
        log_state()

        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                return

            if event.type == pygame.KEYDOWN:

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

                        elif menu_options[menu_index] == "High Scores":
                            game_state = HIGH_SCORES

                        elif menu_options[menu_index] == "Quit":
                            return

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
                                pygame.mixer.music.unpause()
                            else:
                                pygame.mixer.music.pause()

                        elif settings_index == 1:
                            game_sounds_on = not game_sounds_on

                        elif settings_index == 2:
                            game_state = MENU

                elif game_state == PLAYING:
                    if event.key == pygame.K_SPACE and game_over:
                        reset_game()
                        game_state = MENU

                elif game_state == ENTER_HIGH_SCORE:
                    if event.key == pygame.K_BACKSPACE:
                        player_name = player_name[:-1]

                    elif event.key in (pygame.K_RETURN, pygame.K_KP_ENTER):
                        if len(player_name) == 4 and not score_saved:
                            add_high_score(player_name.upper(), score)
                            score_saved = True
                            reset_game()
                            game_state = HIGH_SCORES

                    else:
                        letter = event.unicode.upper()

                        if letter.isalpha() and len(player_name) < 4:
                            player_name += letter

                elif game_state == HIGH_SCORES:
                    if event.key in (pygame.K_RETURN, pygame.K_KP_ENTER, pygame.K_ESCAPE):
                        game_state = MENU

        keys = pygame.key.get_pressed()

        if game_state == MENU:
            screen.blit(menu_background, (0, 0))

        elif game_state == SETTINGS:
            screen.blit(settings_background, (0, 0))

        elif game_state == PLAYING:
            screen.blit(background, (0, 0))

        elif game_state == ENTER_HIGH_SCORE:
            screen.blit(settings_background, (0, 0))

        elif game_state == HIGH_SCORES:
            screen.blit(settings_background, (0, 0))

        if game_state == MENU:
            draw_menu(screen, menu_options, menu_index, font)

        elif game_state == SETTINGS:
            settings_options = [
                f"Background Music: {'ON' if background_music_on else 'OFF'}",
                f"Game Sounds: {'ON' if game_sounds_on else 'OFF'}",
                "Back",
            ]

            draw_menu(screen, settings_options, settings_index, font)

        elif game_state == ENTER_HIGH_SCORE:
            title = font.render("NEW HIGH SCORE!", True, "yellow")
            screen.blit(title, (SCREEN_WIDTH / 2 - 140, 180))

            score_text = font.render(f"Score: {score}", True, "white")
            screen.blit(score_text, (SCREEN_WIDTH / 2 - 70, 230))

            name_text = font.render(f"Enter Name: {player_name}", True, "white")
            screen.blit(name_text, (SCREEN_WIDTH / 2 - 140, 290))

            help_text = font.render("Type 4 letters then ENTER", True, "white")
            screen.blit(help_text, (SCREEN_WIDTH / 2 - 190, 350))

        elif game_state == HIGH_SCORES:
            high_scores = load_high_scores()

            title = font.render("HIGH SCORES", True, "yellow")
            screen.blit(title, (SCREEN_WIDTH / 2 - 120, 120))

            y = 200

            if len(high_scores) == 0:
                empty_text = font.render("No scores yet", True, "white")
                screen.blit(empty_text, (SCREEN_WIDTH / 2 - 90, y))
            else:
                for i, entry in enumerate(high_scores):
                    line = font.render(
                        f"{i + 1}. {entry['name']} - {entry['score']}",
                        True,
                        "white"
                    )
                    screen.blit(line, (SCREEN_WIDTH / 2 - 130, y))
                    y += 40

            back_text = font.render("Press ENTER or ESC to return", True, "white")
            screen.blit(back_text, (SCREEN_WIDTH / 2 - 190, 620))

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
                            player_name = ""
                            score_saved = False
                            game_state = ENTER_HIGH_SCORE

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

        pygame.display.flip()
        dt = clock.tick(60) / 1000


if __name__ == "__main__":
    main()