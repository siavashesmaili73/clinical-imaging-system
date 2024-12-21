import pygame
import math
import random

# Initialize Pygame
pygame.init()

# Constants
WINDOW_WIDTH = 800
WINDOW_HEIGHT = 600
MIN_CELL_RADIUS = 10
MAX_BOT_RADIUS = 40
INITIAL_BOTS = 50  # Increased number of bots
PLAYER_SPEED_MULTIPLIER = 3.5  # Increased player speed
BOT_SPEED_MULTIPLIER = 2
GROWTH_RATE = 0.5
BOT_SPEED = 1.5
FEED_MASS = 5
SPLIT_MIN_MASS = 35
PLAYER_NAME = "Siavash"

# Colors
WHITE = (255, 255, 255)
BLACK = (0, 0, 0)
COLORS = [
    (255, 0, 0),    # Red
    (0, 255, 0),    # Green
    (0, 0, 255),    # Blue
    (255, 255, 0),  # Yellow
    (255, 0, 255),  # Magenta
    (0, 255, 255),  # Cyan
    (255, 165, 0),  # Orange
    (128, 0, 128),  # Purple
]

class Cell:
    def __init__(self, x, y, radius, color, is_player=False, name=None):
        self.x = x
        self.y = y
        self.radius = radius
        self.color = color
        self.is_player = is_player
        self.name = name
        self.speed = (PLAYER_SPEED_MULTIPLIER if is_player else BOT_SPEED_MULTIPLIER) / math.sqrt(radius)
        self.target = None
        self.direction = [0, 0]
        self.feed_cooldown = 0
        self.split_cooldown = 0

    def draw(self, screen, camera_offset):
        # Draw cell body
        screen_x = int(self.x - camera_offset[0])
        screen_y = int(self.y - camera_offset[1])
        pygame.draw.circle(screen, self.color, (screen_x, screen_y), int(self.radius))
        pygame.draw.circle(screen, (min(255, self.color[0] + 50), 
                                  min(255, self.color[1] + 50),
                                  min(255, self.color[2] + 50)),
                          (screen_x, screen_y), int(self.radius * 0.8))
        
        # Draw cell membrane
        pygame.draw.circle(screen, BLACK, (screen_x, screen_y), int(self.radius), 2)

        # Draw name and size for player
        if self.is_player or self.name:
            font = pygame.font.Font(None, 24)
            name_text = font.render(self.name or "", True, BLACK)
            size_text = font.render(f"Size: {int(self.radius)}", True, BLACK)
            screen.blit(name_text, (screen_x - name_text.get_width()//2, screen_y - self.radius - 25))
            if self.is_player:
                screen.blit(size_text, (10, 10))

    def move(self, target_x, target_y):
        dx = target_x - self.x
        dy = target_y - self.y
        distance = math.sqrt(dx * dx + dy * dy)
        
        if distance > 0:
            self.x += (dx / distance) * self.speed
            self.y += (dy / distance) * self.speed

    def feed(self, direction_x, direction_y):
        if self.feed_cooldown <= 0 and self.radius > FEED_MASS * 2:
            self.radius -= FEED_MASS
            distance = math.sqrt(direction_x**2 + direction_y**2)
            if distance > 0:
                normalized_x = direction_x / distance
                normalized_y = direction_y / distance
                feed_x = self.x + normalized_x * (self.radius + FEED_MASS)
                feed_y = self.y + normalized_y * (self.radius + FEED_MASS)
                return Cell(feed_x, feed_y, FEED_MASS, self.color)
        return None

    def split(self, direction_x, direction_y):
        if self.split_cooldown <= 0 and self.radius >= SPLIT_MIN_MASS:
            new_radius = self.radius / math.sqrt(2)
            self.radius = new_radius
            distance = math.sqrt(direction_x**2 + direction_y**2)
            if distance > 0:
                normalized_x = direction_x / distance
                normalized_y = direction_y / distance
                split_x = self.x + normalized_x * (new_radius * 2)
                split_y = self.y + normalized_y * (new_radius * 2)
                new_cell = Cell(split_x, split_y, new_radius, self.color, self.is_player, self.name)
                new_cell.speed = self.speed
                return new_cell
        return None

    def update_bot_movement(self, player, cells):
        if self.is_player:
            return

        # Find nearest cell that's smaller
        nearest_dist = float('inf')
        nearest_cell = None
        fleeing = False

        for cell in cells:
            if cell != self:
                dx = cell.x - self.x
                dy = cell.y - self.y
                dist = math.sqrt(dx * dx + dy * dy)

                if cell.radius > self.radius * 1.1:  # Run from bigger cells
                    if dist < nearest_dist:
                        nearest_dist = dist
                        nearest_cell = cell
                        fleeing = True
                elif self.radius > cell.radius * 1.1 and not fleeing:  # Chase smaller cells
                    if dist < nearest_dist:
                        nearest_dist = dist
                        nearest_cell = cell

        if nearest_cell:
            if fleeing:
                # Move away from bigger cell
                self.direction = [
                    self.x - nearest_cell.x,
                    self.y - nearest_cell.y
                ]
            else:
                # Move toward smaller cell
                self.direction = [
                    nearest_cell.x - self.x,
                    nearest_cell.y - self.y
                ]

            # Normalize direction
            length = math.sqrt(self.direction[0]**2 + self.direction[1]**2)
            if length > 0:
                self.direction = [
                    self.direction[0] / length * BOT_SPEED,
                    self.direction[1] / length * BOT_SPEED
                ]

        # Apply movement
        self.x += self.direction[0]
        self.y += self.direction[1]

        # Keep within bounds
        self.x = max(0, min(WINDOW_WIDTH * 2, self.x))
        self.y = max(0, min(WINDOW_HEIGHT * 2, self.y))

    def check_collision(self, other):
        dx = self.x - other.x
        dy = self.y - other.y
        distance = math.sqrt(dx * dx + dy * dy)
        return distance < self.radius + other.radius

class Game:
    def __init__(self):
        self.screen = pygame.display.set_mode((WINDOW_WIDTH, WINDOW_HEIGHT))
        pygame.display.set_caption(f"Cell.io - {PLAYER_NAME}")
        self.clock = pygame.time.Clock()
        self.running = True
        self.cells = []
        self.camera_offset = [0, 0]
        self.world_size = (WINDOW_WIDTH * 2, WINDOW_HEIGHT * 2)
        
        # Create player
        self.player = Cell(
            WINDOW_WIDTH/2,
            WINDOW_HEIGHT/2,
            MIN_CELL_RADIUS * 2,
            random.choice(COLORS),
            True,
            PLAYER_NAME
        )
        self.cells.append(self.player)
        
        # Create bots
        for _ in range(INITIAL_BOTS):
            self.spawn_bot()

    def spawn_bot(self):
        radius = random.uniform(MIN_CELL_RADIUS, MAX_BOT_RADIUS)
        x = random.randint(0, self.world_size[0])
        y = random.randint(0, self.world_size[1])
        color = random.choice(COLORS)
        bot_names = ["Bot", "Cell", "Blob", "Sphere", "Circle", "Dot"]
        name = random.choice(bot_names) + str(random.randint(1, 99))
        self.cells.append(Cell(x, y, radius, color, name=name))

    def update_camera(self):
        # Camera follows player with smooth movement
        target_x = self.player.x - WINDOW_WIDTH/2
        target_y = self.player.y - WINDOW_HEIGHT/2
        
        # Smooth camera movement
        self.camera_offset[0] += (target_x - self.camera_offset[0]) * 0.1
        self.camera_offset[1] += (target_y - self.camera_offset[1]) * 0.1
        
        # Keep camera within world bounds
        self.camera_offset[0] = max(0, min(self.world_size[0] - WINDOW_WIDTH, self.camera_offset[0]))
        self.camera_offset[1] = max(0, min(self.world_size[1] - WINDOW_HEIGHT, self.camera_offset[1]))

    def handle_collisions(self):
        for i, cell1 in enumerate(self.cells):
            for cell2 in self.cells[i+1:]:
                if cell1.check_collision(cell2):
                    # Larger cell eats smaller cell
                    if cell1.radius > cell2.radius * 1.1:
                        cell1.radius += cell2.radius * 0.8  # Absorb 80% of eaten cell's mass
                        self.cells.remove(cell2)
                        if len(self.cells) < INITIAL_BOTS + 1:
                            self.spawn_bot()
                    elif cell2.radius > cell1.radius * 1.1:
                        cell2.radius += cell1.radius * 0.8
                        self.cells.remove(cell1)
                        if len(self.cells) < INITIAL_BOTS + 1:
                            self.spawn_bot()
                        if cell1 == self.player:
                            self.game_over()
                        break

    def game_over(self):
        font = pygame.font.Font(None, 74)
        text = font.render('Game Over!', True, BLACK)
        text_rect = text.get_rect(center=(WINDOW_WIDTH/2, WINDOW_HEIGHT/2))
        
        score_font = pygame.font.Font(None, 48)
        score_text = score_font.render(f'Final Size: {int(self.player.radius)}', True, BLACK)
        score_rect = score_text.get_rect(center=(WINDOW_WIDTH/2, WINDOW_HEIGHT/2 - 50))
        
        restart_font = pygame.font.Font(None, 36)
        restart_text = restart_font.render('Press R to Restart', True, BLACK)
        restart_rect = restart_text.get_rect(center=(WINDOW_WIDTH/2, WINDOW_HEIGHT/2 + 50))
        
        while True:
            for event in pygame.event.get():
                if event.type == pygame.QUIT:
                    pygame.quit()
                    return
                if event.type == pygame.KEYDOWN:
                    if event.key == pygame.K_r:
                        self.__init__()
                        return
            
            self.screen.fill(WHITE)
            self.screen.blit(text, text_rect)
            self.screen.blit(score_text, score_rect)
            self.screen.blit(restart_text, restart_rect)
            pygame.display.flip()
            self.clock.tick(60)

    def draw_grid(self):
        # Draw grid lines
        grid_size = 50
        for x in range(0, self.world_size[0], grid_size):
            screen_x = x - self.camera_offset[0]
            if 0 <= screen_x <= WINDOW_WIDTH:
                pygame.draw.line(self.screen, (200, 200, 200),
                               (screen_x, 0),
                               (screen_x, WINDOW_HEIGHT))
        
        for y in range(0, self.world_size[1], grid_size):
            screen_y = y - self.camera_offset[1]
            if 0 <= screen_y <= WINDOW_HEIGHT:
                pygame.draw.line(self.screen, (200, 200, 200),
                               (0, screen_y),
                               (WINDOW_WIDTH, screen_y))

    def run(self):
        while self.running:
            # Handle events
            for event in pygame.event.get():
                if event.type == pygame.QUIT:
                    self.running = False
                elif event.type == pygame.KEYDOWN:
                    if event.key == pygame.K_w:  # Feed
                        mouse_x, mouse_y = pygame.mouse.get_pos()
                        direction_x = mouse_x + self.camera_offset[0] - self.player.x
                        direction_y = mouse_y + self.camera_offset[1] - self.player.y
                        new_cell = self.player.feed(direction_x, direction_y)
                        if new_cell:
                            self.cells.append(new_cell)
                            self.player.feed_cooldown = 20
                    elif event.key == pygame.K_SPACE:  # Split
                        mouse_x, mouse_y = pygame.mouse.get_pos()
                        direction_x = mouse_x + self.camera_offset[0] - self.player.x
                        direction_y = mouse_y + self.camera_offset[1] - self.player.y
                        new_cell = self.player.split(direction_x, direction_y)
                        if new_cell:
                            self.cells.append(new_cell)
                            self.player.split_cooldown = 30

            # Update cooldowns
            if self.player.feed_cooldown > 0:
                self.player.feed_cooldown -= 1
            if self.player.split_cooldown > 0:
                self.player.split_cooldown -= 1

            # Get mouse position and convert to world coordinates
            mouse_x, mouse_y = pygame.mouse.get_pos()
            target_x = mouse_x + self.camera_offset[0]
            target_y = mouse_y + self.camera_offset[1]
            
            # Update player movement
            self.player.move(target_x, target_y)
            
            # Update bot movements
            for cell in self.cells:
                if not cell.is_player:
                    cell.update_bot_movement(self.player, self.cells)
            
            # Update camera position
            self.update_camera()
            
            # Handle collisions
            self.handle_collisions()
            
            # Draw everything
            self.screen.fill(WHITE)
            self.draw_grid()
            
            # Draw all cells
            for cell in sorted(self.cells, key=lambda x: x.radius):
                cell.draw(self.screen, self.camera_offset)
            
            pygame.display.flip()
            self.clock.tick(60)

        pygame.quit()

if __name__ == "__main__":
    game = Game()
    game.run()
