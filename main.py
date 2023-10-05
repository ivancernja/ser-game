import pygame
import sys
import random
import requests

# Pygame Init
pygame.init()

clock = pygame.time.Clock()

infoObject = pygame.display.Info()
screen_width = infoObject.current_w
screen_height = infoObject.current_h

screen = pygame.display.set_mode((screen_width, screen_height), pygame.FULLSCREEN)
spawn_area = pygame.Rect(screen_width * 0.2, 0, screen_width * 0.6, screen_height)  

# Colors
black = (0, 0, 0)
white = (255, 255, 255)

# Player
player_size = 50
player_speed = screen_width / 250
player_img = pygame.image.load("player.png")
player_rect = player_img.get_rect()
player_rect.topleft = [screen_width / 2, screen_height - 2 * player_size]

# Bullet
bullet_size = 10
bullet_speed = 20
bullet_active = False
bullet_rect = pygame.Rect(0, 0, bullet_size, bullet_size)

# Enemy
enemy_list = []
enemy_size = 25
enemy_speed = 0.5
font = pygame.font.Font(None, 36)

# Health
heart_img = pygame.image.load("heart.png")
heart_rects = [heart_img.get_rect(topleft=(410 + i * 30, 50)) for i in range(3)]
lives = 3

# Score
score = 0
font_score = pygame.font.Font(None, 36)

# Player's Name
player_name = ''
input_font = pygame.font.Font(None, 32)

# Modify the title_font and menu_font definitions to include glitchy text effects
title_font = pygame.font.Font(None, 70)
menu_font = pygame.font.Font(None, 50)

# social links
social_media_links = [
    {"label": "Twitter", "url": "@shuttle_dev", "image":"./twitter_qr.png"},
    {"label": "GitHub", "url": "github.com/shuttle-hq/shuttle", "image": "./github_qr.png"},
    {"label": "Leaderboard", "url": None, "image": "./leaderboard_qr.png"},
    # Add more social media links as needed
]

# side screen
sidebar_size = screen_width / 5 
side_screen = pygame.Surface((sidebar_size, screen_height))
sidebar_left_x_pos = 0;
sidebar_right_x_pos = screen_width - (sidebar_size);
 
side_screen.fill((25, 25, 25))
# Function to render glitchy text with different colors and offsets
def render_glitchy_text(text, font, x, y, colors):
    for color, offset in colors:
        text_surface = font.render(text, True, color)
        screen.blit(text_surface, (x + offset, y))

screen = pygame.display.set_mode((screen_width, screen_height))

particles = []

# Sound effects
bullet_sound = pygame.mixer.Sound("pew.wav")
gameover_sound = pygame.mixer.Sound("gameover.wav")

def create_particles(position):
    particle_count = 20
    for _ in range(particle_count):
        particles.append([list(position), [random.random() * 4 - 2, -2], random.randint(2, 5)])

def draw_particles():
    for particle in particles:
        pygame.draw.rect(screen, white, (particle[0][0], particle[0][1], particle[2], particle[2]))
        particle[0][0] += particle[1][0]
        particle[0][1] += particle[1][1]
        particle[2] -= 0.1
        if particle[2] <= 0:
            particles.remove(particle)

def drop_enemies(enemy_list):
    delay = random.random()
    rust_items = ["unwrap()", "panic!", "mut", "oddbjorn"]
    spawn_rate = 0.03 - score * 0.000005  # Faster spawn rate as score increases
    if len(enemy_list) < 5 and random.random() < spawn_rate:  # Decrease spawn rate as score increases
        x_pos = random.randint(spawn_area.left, spawn_area.right - enemy_size)
        y_pos = 0
        direction = random.randint(1, 3)
        item = random.choice(rust_items)
        text = font.render(item, 1, white)
        overlap = False
        for enemy in enemy_list:
            if abs(x_pos - enemy[1][0]) < enemy_size:
                overlap = True
                break
        if not overlap:
            enemy_list.append([item, [x_pos, y_pos], direction, text.get_rect()])

def draw_enemies(enemy_list):
    for enemy in enemy_list:
        text = font.render(enemy[0], 1, white)
        screen.blit(text, enemy[1])

def update_enemy_positions(enemy_list, score):
    if score < 50:
        enemy_speed = 0.5
    elif score < 100:
        enemy_speed = 0.7
    elif score < 150:
        enemy_speed = 1
    elif score < 200:
        enemy_speed = 1.25
    elif score < 300:
        enemy_speed = 1.5
    else:
        enemy_speed = 2


    for idx, enemy in enumerate(enemy_list):
        if enemy[1][0] >= sidebar_right_x_pos - enemy[3].width:
            enemy[2] = 2 
        elif enemy[1][0] <= sidebar_size:
            enemy[2] = 1 

        if enemy[1][1] >= 0 and enemy[1][1] < screen_height:
            enemy[1][1] += enemy_speed
            if enemy[2] == 1:
                enemy[1][0] += enemy_speed
            elif enemy[2] == 2:
                enemy[1][0] -= enemy_speed
            if enemy[1][0] >= screen_width - enemy[3].width:
                enemy[1][0] = screen_width - enemy[3].width
                enemy[2] = 2
            elif enemy[1][0] <= 0:
                enemy[1][0] = 0
                enemy[2] = 1
        else:
            enemy_list.pop(idx)
            return True
    return False

def collision_check(enemy_list, player_rect):
    for enemy in enemy_list:
        if player_rect.colliderect(pygame.Rect(enemy[1][0], enemy[1][1], enemy[3].width, enemy[3].height)):
            return True
    return False

def bullet_enemy_collision(bullet_rect, enemy_list):
    for enemy in enemy_list[:]:
        enemy_rect = pygame.Rect(enemy[1][0], enemy[1][1], enemy[3].width, enemy[3].height)
        if bullet_rect.colliderect(enemy_rect):
            return enemy
    return None

def main_menu():
    global player_name, score, lives, enemy_list, bullet_active, bullet_rect, player_rect
    player_name = ''
    score = 0
    lives = 3
    enemy_list = []
    bullet_active = False
    bullet_rect = pygame.Rect(0, 0, bullet_size, bullet_size)
    player_rect.topleft = [screen_width / 2, screen_height - 2 * player_size]

    menu_font = pygame.font.Font(None, 50)
    input_box = pygame.Rect(screen_width // 2 - 100, screen_height // 2 - 50, 200, 50)
    color_inactive = pygame.Color('lightskyblue3')
    color_active = pygame.Color('dodgerblue2')
    color = color_inactive
    active = False

    while True:
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                pygame.quit()
                sys.exit()
            if event.type == pygame.KEYDOWN:
                if event.key == pygame.K_RETURN and player_name != '':
                    return  # Return from the function when the player hits enter
                if event.key == pygame.K_BACKSPACE:
                    player_name = player_name[:-1]
                else:
                    player_name += event.unicode
            if event.type == pygame.MOUSEBUTTONDOWN:
                if input_box.collidepoint(event.pos):
                    active = not active
                else:
                    active = False
                color = color_active if active else color_inactive
	
        y_offset_left = 50  # Adjust the starting Y-coordinate for links	
        font = pygame.font.Font(None, 36)  # You can adjust the font size
        text_color = white  # Black text color

        screen.fill(black)
        screen.blit(side_screen, (0, 0)) 

        for link in social_media_links:
            text = font.render(link["label"], True, text_color)
            screen.blit(text, (10, y_offset_left))
            
            if link["url"] is not None:
                text = font.render(link["url"], True, text_color)
                screen.blit(text, (10, y_offset_left + 30))
                qr = pygame.image.load(link["image"])
                qr = pygame.transform.scale(qr, (225, 225))
                screen.blit(qr, (50, y_offset_left + 60))
                y_offset_left += 330  # Adjust the vertical spacing between links
            else:
                qr = pygame.image.load(link["image"])
                qr = pygame.transform.scale(qr, (225, 225))
                screen.blit(qr, (50, y_offset_left + 30)) 
                y_offset_left += 300  # Adjust the vertical spacing between links
	
        y_offset_right = 50 
        screen.blit(side_screen, (sidebar_right_x_pos, 0))
        for link in social_media_links:
            text = font.render(link["label"], True, text_color)
            screen.blit(text, (sidebar_right_x_pos + 10, y_offset_right))
            
            if link["url"] is not None:
                text = font.render(link["url"], True, text_color)
                screen.blit(text, (sidebar_right_x_pos + 10, y_offset_right + 30))
                qr = pygame.image.load(link["image"])
                qr = pygame.transform.scale(qr, (225, 225))
                screen.blit(qr, (sidebar_right_x_pos + 50, y_offset_right + 60))
                y_offset_right += 330  # Adjust the vertical spacing between links
            else:
                qr = pygame.image.load(link["image"])
                qr = pygame.transform.scale(qr, (225, 225))
                screen.blit(qr, (sidebar_right_x_pos + 50, y_offset_right + 30)) 
                y_offset_right += 300  # Adjust the vertical spacing between links
	
        title_text = title_font.render("Shuttle Invaders", True, white)
        screen.blit(title_text, (screen_width // 2 - title_text.get_width() // 2, 50))
        menu_text = menu_font.render("Enter your name and press Enter to Start Game", True, white)
        screen.blit(menu_text, (screen_width // 2 - menu_text.get_width() // 2, screen_height // 2 - 100))
        pygame.draw.rect(screen, color, input_box, 2)
        txt_surface = input_font.render(player_name, True, color)
        screen.blit(txt_surface, (input_box.x+5, input_box.y+5))
        pygame.display.flip()

def draw_game_over_popup():
    pygame.draw.rect(screen, black, (screen_width // 2 - 250, screen_height // 2 - 150, 500, 300))
    pygame.draw.rect(screen, white, (screen_width // 2 - 250, screen_height // 2 - 150, 500, 300), 5)
    game_over_text = font_score.render("Game Over", True, white)
    screen.blit(game_over_text, (screen_width // 2 - 80, screen_height // 2 - 60))
    score_text = font_score.render(f"Final Score: {score}", True, white)
    screen.blit(score_text, (screen_width // 2 - 80, screen_height // 2))
    pygame.display.update()

while True:
    main_menu()
    # Game Loop
    game_over = False

    while not game_over:
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                pygame.quit()
                sys.exit()

        clock.tick(120)

        keys = pygame.key.get_pressed()
        if keys[pygame.K_LEFT] and player_rect.left > 400:
            player_rect.x -= player_speed
        if keys[pygame.K_RIGHT] and player_rect.right < screen_width:
            player_rect.x += player_speed
        if keys[pygame.K_RIGHT] and player_rect.right > screen_width - 400:
            player_rect.x -= player_speed
        if keys[pygame.K_UP] and player_rect.top > 0:
            player_rect.y -= player_speed
        if keys[pygame.K_DOWN] and player_rect.bottom < screen_height:
            player_rect.y += player_speed
        if keys[pygame.K_SPACE] and not bullet_active:
            bullet_active = True
            bullet_rect.midtop = player_rect.midtop
            bullet_sound.play()
        if player_rect.left > screen_width - 400:
            player_rect.right = 0
        elif player_rect.right < 0:
            player_rect.left = screen_width 

        text_color = white  # Black text color
        screen.fill(black)

        screen.blit(side_screen, (0, 0)) 
        y_offset_left = 50

        for link in social_media_links:
            text = font.render(link["label"], True, text_color)
            screen.blit(text, (10, y_offset_left))
            
            if link["url"] is not None:
                text = font.render(link["url"], True, text_color)
                screen.blit(text, (10, y_offset_left + 30))
                qr = pygame.image.load(link["image"])
                qr = pygame.transform.scale(qr, (225, 225))
                screen.blit(qr, (50, y_offset_left + 60))
                y_offset_left += 330  # Adjust the vertical spacing between links
            else:
                qr = pygame.image.load(link["image"])
                qr = pygame.transform.scale(qr, (225, 225))
                screen.blit(qr, (50, y_offset_left + 30)) 
                y_offset_left += 300  # Adjust the vertical spacing between links
	
        y_offset_right = 50 
        screen.blit(side_screen, (sidebar_right_x_pos, 0))
        for link in social_media_links:
            text = font.render(link["label"], True, text_color)
            screen.blit(text, (sidebar_right_x_pos + 10, y_offset_right))
            
            if link["url"] is not None:
                text = font.render(link["url"], True, text_color)
                screen.blit(text, (sidebar_right_x_pos + 10, y_offset_right + 30))
                qr = pygame.image.load(link["image"])
                qr = pygame.transform.scale(qr, (225, 225))
                screen.blit(qr, (sidebar_right_x_pos + 50, y_offset_right + 60))
                y_offset_right += 330  # Adjust the vertical spacing between links
            else:
                qr = pygame.image.load(link["image"])
                qr = pygame.transform.scale(qr, (225, 225))
                screen.blit(qr, (sidebar_right_x_pos + 50, y_offset_right + 30)) 
                y_offset_right += 300  # Adjust the vertical spacing between links
	
        if bullet_active:
            pygame.draw.rect(screen, white, bullet_rect)
            bullet_rect.y -= bullet_speed
            collided_enemy = bullet_enemy_collision(bullet_rect, enemy_list)
            if collided_enemy is not None:
                create_particles(collided_enemy[1])
                enemy_list.remove(collided_enemy)
                bullet_active = False
                score += 10
            elif bullet_rect.y < 0:
                bullet_active = False
        
        draw_particles()

        drop_enemies(enemy_list)
        if update_enemy_positions(enemy_list, score):
            lives -= 1
            if lives == 0:
                game_over = True
                gameover_sound.play()

        if player_rect.colliderect(spawn_area):
                player_velocity = (0, 0)
        if collision_check(enemy_list, player_rect):
            lives -= 1
            for enemy in enemy_list[:]:
                if (
                    player_rect.colliderect(pygame.Rect(enemy[1][0], enemy[1][1], enemy[3].width, enemy[3].height))
                ):
                    enemy_list.remove(enemy)
                    create_particles(enemy[1])
            if lives <= 0:
                game_over = True
                gameover_sound.play()

        draw_enemies(enemy_list)

        screen.blit(player_img, player_rect)

        for i, heart_rect in enumerate(heart_rects[:lives]):
            screen.blit(heart_img, heart_rect)
        
        score_text = font_score.render(f"Score: {score}", True, white)

        score_x = screen_width // 2 - score_text.get_rect().width // 2

        screen.blit(score_text, (score_x, 50))

        pygame.display.update()

    if game_over:
        draw_game_over_popup()
        pygame.time.delay(3000)

        data = {
            "name": player_name,
            "score": score
        }
        response = requests.post("https://shuttlegame-leaderboard.shuttleapp.rs/submit", json=data)

        if response.status_code == 200:
            print("Score successfully submitted to the leaderboard.")
        else:
            print("There was a problem submitting the score to the leaderboard.")
