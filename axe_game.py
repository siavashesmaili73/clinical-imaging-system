import pygame
import math
import random

# Initialize Pygame
pygame.init()

# Constants
WINDOW_WIDTH = 800
WINDOW_HEIGHT = 600
GRAVITY = 0.25  # Reduced gravity for better arc
MAX_POWER = 40  # Increased max power
POWER_MULTIPLIER = 0.4  # Increased power multiplier
MAX_RANGE = 600  # Increased maximum shooting range
ARROWS_PER_TURN = 2  # Number of arrows per turn
ARROW_DAMAGE = 35  # Increased damage for more exciting gameplay

# Colors
WHITE = (255, 255, 255)
BLACK = (0, 0, 0)
RED = (255, 0, 0)
GREEN = (0, 255, 0)
BLUE = (0, 0, 255)
BROWN = (139, 69, 19)
SKIN = (255, 218, 185)
SKY_BLUE = (135, 206, 235)
GRASS_GREEN = (34, 139, 34)
MOUNTAIN_BROWN = (101, 67, 33)

# Create a simple nature background
def create_background():
    background = pygame.Surface((WINDOW_WIDTH, WINDOW_HEIGHT))
    
    # Sky gradient
    for y in range(WINDOW_HEIGHT):
        blue = int(200 - (y / WINDOW_HEIGHT * 100))
        color = (135, 206, blue)
        pygame.draw.line(background, color, (0, y), (WINDOW_WIDTH, y))
    
    # Mountains in background
    mountain_points = [(0, WINDOW_HEIGHT - 100)]
    for x in range(0, WINDOW_WIDTH + 50, 50):
        height = random.randint(100, 300)
        mountain_points.append((x, WINDOW_HEIGHT - height))
    mountain_points.append((WINDOW_WIDTH, WINDOW_HEIGHT - 100))
    mountain_points.append((WINDOW_WIDTH, WINDOW_HEIGHT))
    mountain_points.append((0, WINDOW_HEIGHT))
    pygame.draw.polygon(background, MOUNTAIN_BROWN, mountain_points)
    
    # Trees
    for _ in range(20):
        x = random.randint(0, WINDOW_WIDTH)
        y = random.randint(WINDOW_HEIGHT - 200, WINDOW_HEIGHT - 50)
        # Tree trunk
        pygame.draw.rect(background, BROWN, (x, y, 10, 40))
        # Tree top
        pygame.draw.circle(background, GRASS_GREEN, (x + 5, y - 10), 20)
    
    # Sun
    pygame.draw.circle(background, (255, 255, 0), (100, 100), 40)
    for i in range(8):  # Sun rays
        angle = i * math.pi / 4
        start_x = 100 + math.cos(angle) * 45
        start_y = 100 + math.sin(angle) * 45
        end_x = 100 + math.cos(angle) * 60
        end_y = 100 + math.sin(angle) * 60
        pygame.draw.line(background, (255, 255, 0), (start_x, start_y), (end_x, end_y), 3)
    
    # Clouds
    for _ in range(5):
        x = random.randint(0, WINDOW_WIDTH)
        y = random.randint(50, 200)
        for i in range(3):
            pygame.draw.circle(background, WHITE, (x + i * 20, y), 20)
    
    return background

# Create background once
BACKGROUND = create_background()

# Set up the display
screen = pygame.display.set_mode((WINDOW_WIDTH, WINDOW_HEIGHT))
pygame.display.set_caption("Archery Battle")
clock = pygame.time.Clock()

class Character:
    def __init__(self, x, y, color, is_player=True):
        self.x = x
        self.y = y
        self.width = 30
        self.height = 60
        self.color = color
        self.health = 100
        self.is_player = is_player
        self.is_hit = False
        self.hit_timer = 0
        self.arrows_left = ARROWS_PER_TURN
        self.bow_angle = 0  # Angle of the bow

    def draw(self, screen):
        # Draw legs
        leg_width = 8
        leg_height = 20
        pygame.draw.rect(screen, BROWN, (self.x + 5, self.y + 40, leg_width, leg_height))
        pygame.draw.rect(screen, BROWN, (self.x + 17, self.y + 40, leg_width, leg_height))
        
        # Draw body
        pygame.draw.rect(screen, self.color, (self.x + 5, self.y + 15, 20, 25))
        
        # Draw head
        pygame.draw.circle(screen, SKIN, (self.x + 15, self.y + 10), 10)
        
        # Draw arms and bow
        if self.is_player:
            # Right arm holding bow
            pygame.draw.line(screen, SKIN, 
                           (self.x + 25, self.y + 20),
                           (self.x + 35, self.y + 25), 5)
            
            # Draw bow
            bow_start = (self.x + 35, self.y + 25)
            bow_angle_rad = math.radians(self.bow_angle)
            bow_length = 20
            bow_end = (bow_start[0] + math.cos(bow_angle_rad) * bow_length,
                      bow_start[1] + math.sin(bow_angle_rad) * bow_length)
            pygame.draw.arc(screen, BROWN, 
                          (bow_start[0]-5, bow_start[1]-10, 10, 20),
                          -math.pi/2, math.pi/2, 2)
            
            # Left arm drawing bowstring
            pygame.draw.line(screen, SKIN,
                           (self.x + 5, self.y + 20),
                           (self.x + 35, self.y + 25), 5)
        else:
            # Mirror image for bot
            pygame.draw.line(screen, SKIN,
                           (self.x + 5, self.y + 20),
                           (self.x - 5, self.y + 25), 5)
            pygame.draw.arc(screen, BROWN,
                          (self.x - 15, self.y + 15, 10, 20),
                          math.pi/2, 3*math.pi/2, 2)
            pygame.draw.line(screen, SKIN,
                           (self.x + 25, self.y + 20),
                           (self.x - 5, self.y + 25), 5)
        
        # Draw health bar
        health_width = 50
        health_height = 5
        health_x = self.x - (health_width - self.width) // 2
        pygame.draw.rect(screen, RED, (health_x, self.y - 15, health_width, health_height))
        pygame.draw.rect(screen, GREEN, (health_x, self.y - 15, 
                        health_width * (self.health / 100), health_height))
        
        # Draw arrows left indicator
        arrows_text = f"Arrows: {self.arrows_left}"
        font = pygame.font.Font(None, 24)
        text = font.render(arrows_text, True, BLACK)
        screen.blit(text, (self.x, self.y - 30))

        # Flash effect when hit
        if self.is_hit and self.hit_timer > 0:
            pygame.draw.rect(screen, WHITE, (self.x, self.y, self.width, self.height), 2)
            self.hit_timer -= 1
            if self.hit_timer == 0:
                self.is_hit = False

    def take_damage(self, damage):
        self.health -= damage
        self.is_hit = True
        self.hit_timer = 10
        if self.health < 0:
            self.health = 0

    def update_bow_angle(self, mouse_pos):
        if self.is_player:
            dx = mouse_pos[0] - (self.x + 35)
            dy = mouse_pos[1] - (self.y + 25)
            self.bow_angle = math.degrees(math.atan2(dy, dx))

class Arrow:
    def __init__(self, x, y, vx, vy):
        self.x = x
        self.y = y
        self.vx = vx
        self.vy = vy
        self.angle = math.atan2(vy, vx)
        self.active = True

    def update(self):
        if self.active:
            self.x += self.vx
            self.y += self.vy
            self.vy += GRAVITY
            self.angle = math.atan2(self.vy, self.vx)
            
            # Check if arrow is off screen or hits ground
            if (self.x < 0 or self.x > WINDOW_WIDTH or 
                self.y < 0 or self.y > WINDOW_HEIGHT - 20):
                self.active = False

    def draw(self, screen):
        if self.active:
            # Draw arrow as a line with a triangle head
            arrow_length = 20
            dx = math.cos(self.angle) * arrow_length
            dy = math.sin(self.angle) * arrow_length
            
            # Arrow shaft
            end_x = self.x + dx
            end_y = self.y + dy
            pygame.draw.line(screen, BROWN, (self.x, self.y), (end_x, end_y), 2)
            
            # Arrow head
            head_size = 5
            head_angle = math.pi/6  # 30 degrees
            angle1 = self.angle + head_angle
            angle2 = self.angle - head_angle
            head1_x = end_x - head_size * math.cos(angle1)
            head1_y = end_y - head_size * math.sin(angle1)
            head2_x = end_x - head_size * math.cos(angle2)
            head2_y = end_y - head_size * math.sin(angle2)
            
            pygame.draw.polygon(screen, BROWN, [
                (end_x, end_y),
                (head1_x, head1_y),
                (head2_x, head2_y)
            ])

    def check_collision(self, character):
        if self.active:
            if (self.x > character.x and self.x < character.x + character.width and
                self.y > character.y and self.y < character.y + character.height):
                character.take_damage(ARROW_DAMAGE)  # Use the new ARROW_DAMAGE constant
                self.active = False
                return True
        return False

class Game:
    def __init__(self):
        self.player = Character(100, WINDOW_HEIGHT - 100, BLUE)
        self.bot = Character(WINDOW_WIDTH - 140, WINDOW_HEIGHT - 100, RED, False)
        self.arrows = []
        self.player_turn = True
        self.game_over = False
        self.winner = None
        self.dragging = False
        self.drag_start = None
        self.font = pygame.font.Font(None, 36)

    def handle_input(self):
        mouse_pos = pygame.mouse.get_pos()
        
        # Update bow angle while mouse moves
        if self.player_turn and not self.game_over:
            self.player.update_bow_angle(mouse_pos)
        
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                return False
            
            if event.type == pygame.MOUSEBUTTONDOWN and event.button == 1:
                if self.player_turn and not self.game_over and self.player.arrows_left > 0:
                    # Check if within range
                    dx = mouse_pos[0] - (self.player.x + self.player.width)
                    dy = mouse_pos[1] - (self.player.y + self.player.height/2)
                    distance = math.sqrt(dx*dx + dy*dy)
                    
                    if distance <= MAX_RANGE:
                        self.dragging = True
                        self.drag_start = mouse_pos
            
            if event.type == pygame.MOUSEBUTTONUP and event.button == 1:
                if self.dragging:
                    end_pos = mouse_pos
                    dx = self.drag_start[0] - end_pos[0]
                    dy = self.drag_start[1] - end_pos[1]
                    power = min(math.sqrt(dx*dx + dy*dy), MAX_POWER)
                    angle = math.atan2(dy, dx)
                    
                    vx = math.cos(angle) * power * POWER_MULTIPLIER
                    vy = math.sin(angle) * power * POWER_MULTIPLIER
                    
                    self.arrows.append(Arrow(
                        self.player.x + 35,
                        self.player.y + 25,
                        vx, vy
                    ))
                    self.dragging = False
                    self.player.arrows_left -= 1
                    
                    # Switch turns if out of arrows
                    if self.player.arrows_left <= 0:
                        self.player_turn = False
                        self.bot.arrows_left = ARROWS_PER_TURN
            
            if event.type == pygame.KEYDOWN and event.key == pygame.K_r and self.game_over:
                self.__init__()
        
        return True

    def update(self):
        # Update arrows
        for arrow in self.arrows[:]:
            arrow.update()
            if arrow.check_collision(self.bot if self.player_turn else self.player):
                self.arrows.remove(arrow)
            elif not arrow.active:
                self.arrows.remove(arrow)

        # Bot's turn
        if not self.player_turn and not self.arrows and self.bot.arrows_left > 0:
            # Calculate trajectory to hit player
            start_x = self.bot.x
            start_y = self.bot.y + 25
            target_x = self.player.x + self.player.width//2
            target_y = self.player.y + self.player.height//2
            
            # Add some randomness to targeting
            target_x += random.randint(-20, 20)
            target_y += random.randint(-20, 20)
            
            # Calculate angle and power
            dx = target_x - start_x
            dy = target_y - start_y
            power = min(math.sqrt(dx*dx + dy*dy) * 0.3, MAX_POWER)  # Increased bot power
            angle = math.atan2(dy, dx)
            
            vx = math.cos(angle) * power * POWER_MULTIPLIER
            vy = math.sin(angle) * power * POWER_MULTIPLIER
            
            self.arrows.append(Arrow(start_x, start_y, vx, vy))
            self.bot.arrows_left -= 1
            
            # Switch turns if out of arrows
            if self.bot.arrows_left <= 0:
                self.player_turn = True
                self.player.arrows_left = ARROWS_PER_TURN

        # Check for game over
        if self.player.health <= 0:
            self.game_over = True
            self.winner = "Bot"
        elif self.bot.health <= 0:
            self.game_over = True
            self.winner = "Player"

    def draw(self):
        # Draw ground
        pygame.draw.rect(screen, GRASS_GREEN, (0, WINDOW_HEIGHT - 20, WINDOW_WIDTH, 20))
        
        # Draw range indicator for player
        if self.player_turn and not self.game_over:
            pygame.draw.circle(screen, (200, 200, 200), 
                             (self.player.x + self.player.width, 
                              self.player.y + self.player.height//2),
                             MAX_RANGE, 1)
        
        # Draw turn indicator
        turn_text = self.font.render("Player's Turn" if self.player_turn else "Bot's Turn", 
                                   True, BLACK)
        screen.blit(turn_text, (10, 10))
        
        # Draw characters
        self.player.draw(screen)
        self.bot.draw(screen)
        
        # Draw arrows
        for arrow in self.arrows:
            arrow.draw(screen)
        
        # Draw game over screen
        if self.game_over:
            game_over_text = self.font.render(f"Game Over! {self.winner} Wins!", True, BLACK)
            restart_text = self.font.render("Press R to Restart", True, BLACK)
            screen.blit(game_over_text, 
                       (WINDOW_WIDTH//2 - game_over_text.get_width()//2, 
                        WINDOW_HEIGHT//2 - 50))
            screen.blit(restart_text,
                       (WINDOW_WIDTH//2 - restart_text.get_width()//2,
                        WINDOW_HEIGHT//2 + 50))

def main():
    game = Game()
    running = True
    
    while running:
        running = game.handle_input()
        game.update()
        
        # Draw background first
        screen.blit(BACKGROUND, (0, 0))
        
        # Draw game elements
        game.draw()
        
        pygame.display.flip()
        clock.tick(60)

    pygame.quit()

if __name__ == "__main__":
    main()
