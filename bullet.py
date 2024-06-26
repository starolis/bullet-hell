import pygame
import random

# Initialize Pygame
pygame.init()

# Set up the display
WIDTH, HEIGHT = 800, 600
screen = pygame.display.set_mode((WIDTH, HEIGHT))
pygame.display.set_caption("Enhanced Bullet Hell Game")

# Colors
WHITE = (255, 255, 255)
RED = (255, 0, 0)
BLUE = (0, 0, 255)
GREEN = (0, 255, 0)
YELLOW = (255, 255, 0)

# Player
player_radius = 20
player_x = 50
player_y = HEIGHT // 2
player_speed = 5
player_cooldown = 0
PLAYER_MAX_COOLDOWN = 15

# Gun
class Gun:
    def __init__(self, level):
        self.width = 30
        self.height = 60
        self.respawn(level)
        self.fire_rate = random.randint(30, 90)  # Frames between shots
        self.counter = 0

    def respawn(self, level):
        self.x = WIDTH - self.width
        self.y = random.randint(0, HEIGHT - self.height)
        self.speed = 0 if level < 3 else random.choice([-2, -1, 1, 2])

    def update(self, level):
        self.counter += 1
        if level >= 3:
            self.y += self.speed
            if self.y < 0 or self.y > HEIGHT - self.height:
                self.speed = -self.speed
        if self.counter >= self.fire_rate:
            self.counter = 0
            return Bullet(self.x, self.y + self.height // 2, -1)
        return None

    def draw(self):
        pygame.draw.rect(screen, RED, (self.x, self.y, self.width, self.height))

# Bullet
class Bullet:
    def __init__(self, x, y, direction):
        self.radius = 5
        self.x = x
        self.y = y
        self.speed = random.randint(3, 7) * direction
        self.color = RED if direction < 0 else GREEN

    def update(self):
        self.x += self.speed

    def draw(self):
        pygame.draw.circle(screen, self.color, (int(self.x), int(self.y)), self.radius)

# Game variables
level = 1
guns = [Gun(level) for _ in range(3)]  # Start with 3 guns
enemy_bullets = []
player_bullets = []
score = 0
font = pygame.font.Font(None, 36)
danger_zone_width = 100
points_since_last_gun = 0
score_accumulating = False
guns_eliminated = 0

# Game loop
clock = pygame.time.Clock()
running = True

while running:
    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            running = False
        elif event.type == pygame.KEYDOWN:
            if event.key == pygame.K_SPACE and player_cooldown == 0:
                player_bullets.append(Bullet(player_x + player_radius, player_y, 1))
                player_cooldown = PLAYER_MAX_COOLDOWN

    # Player movement
    keys = pygame.key.get_pressed()
    if keys[pygame.K_UP] and player_y > player_radius:
        player_y -= player_speed
    if keys[pygame.K_DOWN] and player_y < HEIGHT - player_radius:
        player_y += player_speed
    if keys[pygame.K_LEFT] and player_x > player_radius + danger_zone_width:
        player_x -= player_speed
    if keys[pygame.K_RIGHT] and player_x < WIDTH - player_radius:
        player_x += player_speed

    # Update player cooldown
    if player_cooldown > 0:
        player_cooldown -= 1

    # Update guns and create new enemy bullets
    for gun in guns:
        new_bullet = gun.update(level)
        if new_bullet:
            enemy_bullets.append(new_bullet)

    # Update bullet positions and remove off-screen bullets
    enemy_bullets = [bullet for bullet in enemy_bullets if 0 < bullet.x < WIDTH]
    player_bullets = [bullet for bullet in player_bullets if 0 < bullet.x < WIDTH]
    for bullet in enemy_bullets + player_bullets:
        bullet.update()

    # Check for collisions
    player_rect = pygame.Rect(player_x - player_radius, player_y - player_radius, player_radius * 2, player_radius * 2)
    
    # Player collision with enemy bullets
    for bullet in enemy_bullets:
        bullet_rect = pygame.Rect(bullet.x - bullet.radius, bullet.y - bullet.radius, bullet.radius * 2, bullet.radius * 2)
        if player_rect.colliderect(bullet_rect):
            running = False  # End game on collision
        elif abs(bullet.y - player_y) < player_radius * 2 and bullet.x < player_x:
            score += 5  # Near miss bonus

    # Player bullets collision with guns
    bullets_to_remove = []
    for bullet in player_bullets:
        bullet_rect = pygame.Rect(bullet.x - bullet.radius, bullet.y - bullet.radius, bullet.radius * 2, bullet.radius * 2)
        for gun in guns:
            gun_rect = pygame.Rect(gun.x, gun.y, gun.width, gun.height)
            if bullet_rect.colliderect(gun_rect):
                bullets_to_remove.append(bullet)
                gun.respawn(level)
                guns_eliminated += 1
                score += points_since_last_gun
                points_since_last_gun = 0
                score_accumulating = True
                break  # Break here to avoid multiple collisions with the same bullet

    # Remove marked bullets
    for bullet in bullets_to_remove:
        if bullet in player_bullets:
            player_bullets.remove(bullet)

    # Update score
    if score_accumulating:
        points_since_last_gun += 1
        if points_since_last_gun >= 500:
            points_since_last_gun = 500
            score_accumulating = False

    score += points_since_last_gun // 500  # Only add to score when a full 500 points is accumulated

    # Drawing
    screen.fill((0, 0, 0))  # Clear screen
    pygame.draw.rect(screen, YELLOW, (0, 0, danger_zone_width, HEIGHT))  # Danger zone
    for gun in guns:
        gun.draw()
    for bullet in enemy_bullets + player_bullets:
        bullet.draw()
    pygame.draw.circle(screen, BLUE, (int(player_x), int(player_y)), player_radius)

    # Display score, level, and guns eliminated
    score_text = font.render(f"Score: {score}", True, WHITE)
    level_text = font.render(f"Level: {level}", True, WHITE)
    guns_text = font.render(f"Guns Eliminated: {guns_eliminated}", True, WHITE)
    screen.blit(score_text, (10, 10))
    screen.blit(level_text, (10, 50))
    screen.blit(guns_text, (10, 90))

    # Level up
    if guns_eliminated // 5 + 3 > len(guns):
        level += 1
        guns.append(Gun(level))
        # Update existing guns to move if reaching level 3
        if level == 3:
            for gun in guns:
                gun.speed = random.choice([-2, -1, 1, 2])

    pygame.display.flip()
    clock.tick(60)  # 60 FPS

pygame.quit()