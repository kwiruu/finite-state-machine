import pygame

# Initialize Pygame
pygame.init()

# Game screen dimensions
SCREEN_WIDTH = 800
SCREEN_HEIGHT = 600

# Colors
WHITE = (255, 255, 255)
BLACK = (0, 0, 0)
BLUE = (0, 0, 255)

# Create screen
screen = pygame.display.set_mode((SCREEN_WIDTH, SCREEN_HEIGHT))
pygame.display.set_caption("FSM Character Movement")

# Load background and floor images
bg_image = pygame.image.load("sprites/bg.png")  # Load the background image
bg_image = pygame.transform.scale(bg_image, (SCREEN_WIDTH, SCREEN_HEIGHT))  # Scale to fit screen

floor_image = pygame.image.load("sprites/floor.png")
floor_rect = floor_image.get_rect()

# Frame rate control
clock = pygame.time.Clock()

# Define character properties
CHARACTER_WIDTH = 100
CHARACTER_HEIGHT = 100

character_x = SCREEN_WIDTH // 2
character_y = SCREEN_HEIGHT - CHARACTER_HEIGHT - floor_rect.height
character_speed = 5
jump_height = 15
gravity = 1

# Load the sprite sheets
dino_idle_sheet = pygame.image.load("sprites/dino_idle.png")
dino_walk_sheet = pygame.image.load("sprites/dino_walk.png")
dino_jump_sheet = pygame.image.load("sprites/dino_jump.png")

# Function to extract frames from a sprite sheet
# Function to extract frames from a sprite sheet without scaling
def load_frames(sheet, num_frames, frame_width, frame_height):
    frames = []
    for i in range(num_frames):
        frame = sheet.subsurface(pygame.Rect(i * frame_width, 0, frame_width, frame_height))
        frames.append(frame)
    return frames


# Extract frames with the new 120x120 size
idle_frames = load_frames(dino_idle_sheet, 4, 120, 120)
walk_frames = load_frames(dino_walk_sheet, 5, 120, 120)
jump_frame = dino_jump_sheet.subsurface(pygame.Rect(0, 0, 120, 120))  # No scaling needed

# FSM and animation control
class CharacterFSM:
    def __init__(self):
        self.state = 'Idle'
        self.vel_y = 0  # Vertical velocity for jumping
        self.current_frame = 0
        self.flip = False  # Flip flag to flip the sprite when moving left
        self.animation_counter = 0

    def handle_input(self, input):
        previous_state = self.state

        if self.state == 'Idle':
            if input == 'move_left' or input == 'move_right':
                self.state = 'Walking'
            elif input == 'jump':
                self.state = 'Jumping'
                self.vel_y = -jump_height  # Start jump
        elif self.state == 'Walking':
            if input == 'stop':
                self.state = 'Idle'
            elif input == 'jump':
                self.state = 'Jumping'
                self.vel_y = -jump_height
        elif self.state == 'Jumping':
            if input == 'land':
                self.state = 'Idle'  # Character lands

        # Reset current_frame to 0 if the state has changed
        if previous_state != self.state:
            self.current_frame = 0

    def get_state(self):
        return self.state

    def update(self):
        if self.state == 'Jumping':
            global character_y
            self.vel_y += gravity
            character_y += self.vel_y

            # Ensure the character stays on the floor based on the new sprite size
            if character_y >= SCREEN_HEIGHT - CHARACTER_HEIGHT - floor_rect.height:
                character_y = SCREEN_HEIGHT - CHARACTER_HEIGHT - floor_rect.height
                self.handle_input('land')

        # Handle animation update
        self.animation_counter += 1
        current_frames = self.get_current_frames()

        if self.animation_counter >= 10:  # Change frame every 10 ticks
            if len(current_frames) > 1:  # Only cycle frames if there are multiple
                self.current_frame = (self.current_frame + 1) % len(current_frames)
            else:
                self.current_frame = 0  # For single-frame animations like jumping
            self.animation_counter = 0

    def get_current_frames(self):
        if self.state == 'Idle':
            return idle_frames
        elif self.state == 'Walking':
            return walk_frames
        elif self.state == 'Jumping':
            return [jump_frame]

    def get_current_frame(self):
        frames = self.get_current_frames()
        frame = frames[self.current_frame]  # Safe access to frame by resetting current_frame
        if self.flip:  # Flip the frame if moving left
            return pygame.transform.flip(frame, True, False)
        return frame


# Create the FSM instance
fsm = CharacterFSM()

# Font for displaying text
font = pygame.font.Font(None, 36)  # None uses default font, size 36

# Game loop
running = True
move_left = False
move_right = False

while running:
    screen.fill(WHITE)

    # Draw the background (first element to be drawn)
    screen.blit(bg_image, (0, 0))

    # Draw the floor (inside the game loop before drawing the player)
    for i in range(0, SCREEN_WIDTH, floor_rect.width):
        screen.blit(floor_image, (i, SCREEN_HEIGHT - floor_rect.height))

    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            running = False

        # Key press events
        if event.type == pygame.KEYDOWN:
            if event.key == pygame.K_a:  # A to move left
                move_left = True
                fsm.handle_input('move_left')
                fsm.flip = True  # Set flip to True when moving left
            if event.key == pygame.K_d:  # D to move right
                move_right = True
                fsm.handle_input('move_right')
                fsm.flip = False  # Set flip to False when moving right
            if event.key == pygame.K_w and fsm.get_state() != 'Jumping':  # W to jump
                fsm.handle_input('jump')

        # Key release events
        if event.type == pygame.KEYUP:
            if event.key == pygame.K_a:
                move_left = False
                fsm.handle_input('stop')
            if event.key == pygame.K_d:
                move_right = False
                fsm.handle_input('stop')

    # Update character state and position
    if move_left:
        character_x -= character_speed
    if move_right:
        character_x += character_speed

    # Keep character within screen bounds
    if character_x < 0:
        character_x = 0
    elif character_x > SCREEN_WIDTH - CHARACTER_WIDTH:
        character_x = SCREEN_WIDTH - CHARACTER_WIDTH

    # Update FSM for jumping and gravity
    fsm.update()

    # Draw character (based on animation frames)
    current_frame = fsm.get_current_frame()
    screen.blit(current_frame, (character_x, character_y))

    # Display the current state in the top right corner
    state_text = font.render(f"State: {fsm.get_state()}", True, BLACK)
    screen.blit(state_text, (SCREEN_WIDTH - state_text.get_width() - 10, 10))  # Add padding of 10px

    # Update the display
    pygame.display.flip()

    # Cap the frame rate
    clock.tick(60)

# Quit the game
pygame.quit()
