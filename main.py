import os
os.environ["SDL_AUDIODRIVER"] = "pulse"

import pygame
from constants import SCREEN_WIDTH, SCREEN_HEIGHT
from logger import log_state, log_event
from player import Player
from asteroid import Asteroid
from asteroidfield import AsteroidField
from shot import Shot


def main():
    pygame.init()
    pygame.mixer.init()

    clock = pygame.time.Clock()
    dt = 0

    screen = pygame.display.set_mode((SCREEN_WIDTH, SCREEN_HEIGHT))

    font = pygame.font.SysFont(None, 36)
    score = 0
    lives = 3
    game_over = False
    invincible_timer = 0

    # 🔊 Load sounds
    shoot_sound = pygame.mixer.Sound("shoot.wav")
    explosion_sound = pygame.mixer.Sound("explosion.wav")

    shoot_sound.set_volume(0.3)
    explosion_sound.set_volume(0.5)
    pygame.mixer.music.load("background.wav")
    pygame.mixer.music.set_volume(0.2)
    pygame.mixer.music.play(-1)

    was_shooting = False

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

    print(f"Starting Asteroids with pygame version: {pygame.version.ver}")

    while True:
        log_state()

        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                return

            if event.type == pygame.KEYDOWN:
                if event.key == pygame.K_SPACE and game_over:
                    reset_game()

        keys = pygame.key.get_pressed()

        # 🔊 Shoot sound
        if keys[pygame.K_SPACE] and not was_shooting and not game_over:
            shoot_sound.play()

        was_shooting = keys[pygame.K_SPACE]

        screen.fill((10, 10, 20))

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
                        print("Game Over")
                        game_over = True

                for shot in shots:
                    if asteroid.collides_with(shot):
                        explosion_sound.play()  # 🔊 Explosion
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
                "GAME OVER - Press SPACE to restart",
                True,
                "white"
            )
            screen.blit(game_over_text, (SCREEN_WIDTH / 2 - 250, SCREEN_HEIGHT / 2))

        pygame.display.flip()

        dt = clock.tick(60) / 1000


if __name__ == "__main__":
    main()