import sys
import pygame
from constants import SCREEN_WIDTH, SCREEN_HEIGHT
from logger import log_state, log_event
from player import Player
from asteroid import Asteroid
from asteroidfield import AsteroidField
from shot import Shot




def main():
    pygame.init()


    clock = pygame.time.Clock()
    dt = 0

    screen = pygame.display.set_mode((SCREEN_WIDTH, SCREEN_HEIGHT))

    font = pygame.font.SysFont(None, 36)
    score = 0
    lives = 3
    game_over = False
    invincible_timer = 0

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
    Asteroid_field = AsteroidField()
    
    
    print(f"Starting Asteroids with pygame version: {pygame.version.ver}")
    print(f"Screen width: {SCREEN_WIDTH}, Screen height: {SCREEN_HEIGHT}")


    while True:
        log_state()

        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                return
            
            if event.type == pygame.KEYDOWN:
                if event.key == pygame.K_SPACE and game_over:
                    reset_game()
            

        screen.fill("black")
        
        if not game_over:
            updatable.update(dt)
        if invincible_timer > 0:
            invincible_timer -= dt


        for asteroid in asteroids:
            if asteroid.collides_with(player) and invincible_timer <=0:
                log_event("player_hit")
                lives -= 1
                invincible_timer = 2
                asteroid.kill()

                if lives <= 0:
                    print("Game Over")
                    game_over = True


            for shot in shots:
                if asteroid.collides_with(shot):
                    log_event("asteroid_shot")
                    score += 100
                    asteroid.split()
                    shot.kill()
        
        for thing in drawable:
            thing.draw(screen)
        
        score_text = font.render(f"Score: {score}", True, "white")
        screen.blit(score_text,(20, 20))

        lives_text = font.render(f"Lives: {lives}", True, "white")
        screen.blit(lives_text, (20, 55))

        if game_over:
            game_over_text = font.render("GAME OVER - Press SPACE to restart", True, "white")
            screen.blit(game_over_text,(SCREEN_WIDTH / 2 - 250, SCREEN_HEIGHT / 2)) 
        
        
        
        
        pygame.display.flip()


        dt = clock.tick(60) / 1000
        
      
    
     
    
    
    
if __name__ == "__main__":
    main()