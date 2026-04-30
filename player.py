import pygame

from circleshape import CircleShape
from constants import (
    PLAYER_RADIUS,
    LINE_WIDTH,
    PLAYER_TURN_SPEED,
    PLAYER_SPEED,
    PLAYER_SHOOT_SPEED,
    PLAYER_SHOOT_COOLDOWN_SECONDS,
    SCREEN_WIDTH,
    SCREEN_HEIGHT
)
from shot import Shot


class Player(CircleShape):
    def __init__(self, x, y):
        super().__init__(x, y, PLAYER_RADIUS)

        self.rotation = 0
        self.shoot_timer = 0

        # 🚀 Load spaceship image from assets folder
        self.image = pygame.image.load("assets/images/ship.png").convert_alpha()

        # 🔧 Scale ship bigger
        scale = 3.0
        size = int(50 * scale)
        self.image = pygame.transform.scale(self.image, (size, size))

    def shoot(self):
        if self.shoot_timer > 0:
            return

        # 🔫 Forward direction
        direction = pygame.Vector2(0, -1).rotate(self.rotation)

        # spawn at front of ship
        spawn_pos = self.position + direction * (self.radius + 60)

        shot = Shot(spawn_pos.x, spawn_pos.y)
        shot.velocity = direction * PLAYER_SHOOT_SPEED

        self.shoot_timer = PLAYER_SHOOT_COOLDOWN_SECONDS

    def update(self, dt):
        keys = pygame.key.get_pressed()

        if keys[pygame.K_a]:
            self.rotation -= PLAYER_TURN_SPEED * dt
        if keys[pygame.K_d]:
            self.rotation += PLAYER_TURN_SPEED * dt

        # 🔄 swapped controls (W forward, S backward)
        if keys[pygame.K_w]:
            direction = pygame.Vector2(0, 1).rotate(self.rotation)
            self.position -= direction * PLAYER_SPEED * dt

        if keys[pygame.K_s]:
            direction = pygame.Vector2(0, 1).rotate(self.rotation)
            self.position += direction * PLAYER_SPEED * dt

        if keys[pygame.K_SPACE]:
            self.shoot()

        if self.shoot_timer > 0:
            self.shoot_timer -= dt

        # 🌍 Screen wrapping
        if self.position.x < 0:
            self.position.x = SCREEN_WIDTH
        elif self.position.x > SCREEN_WIDTH:
            self.position.x = 0

        if self.position.y < 0:
            self.position.y = SCREEN_HEIGHT
        elif self.position.y > SCREEN_HEIGHT:
            self.position.y = 0

    def draw(self, screen):
        rotated_image = pygame.transform.rotate(self.image, -self.rotation)
        rect = rotated_image.get_rect(center=self.position)
        screen.blit(rotated_image, rect)