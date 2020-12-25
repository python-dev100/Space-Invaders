import pygame
from random import randint
from math import sqrt
import sqlite3

# Initialise
pygame.init()


# Sound
pygame.mixer.music.load("background.wav")
pygame.mixer.music.play(-1)

def setup():
    # Screen
    global screen
    screen = pygame.display.set_mode((800, 600))

    # Title
    global icon
    pygame.display.set_caption("Game")
    icon = pygame.image.load("icon.png")
    pygame.display.set_icon(icon)

    # Background
    global background
    background = pygame.image.load("background.jpg")


    # Player
    global playerImg
    playerImg = pygame.image.load("player.png")
    global playerX
    playerX = 370
    global playerY
    playerY = 480
    global playerX_change
    playerX_change = 0

    # Bullet
    global bullet
    bullet = pygame.image.load("bullet.png")
    global bulletX
    bulletX = playerX
    global bulletY
    bulletY = playerY
    global bulletY_change
    bulletY_change = 1
    global bullet_state
    bullet_state = "READY"

    # Enemy
    global enemyImg
    enemyImg = []
    global enemyX
    enemyX = []
    global enemyY
    enemyY = []
    global enemyX_change
    enemyX_change = []
    global enemyY_change
    enemyY_change = []

    global enemies
    enemies = 5

    for i in range(enemies):
        enemyImg.append(pygame.image.load("enemy.png"))
        enemyX.append(randint(0, 736))
        enemyY.append(randint(50, 150))
        enemyX_change.append(1)
        enemyY_change.append(40)
    global score
    score = 0

font = pygame.font.Font("bauhaus.ttf", 60)
game_over_font = pygame.font.Font("bauhaus.ttf", 120)
textX = 10
textY = 10

def game_over_text():
    text = game_over_font.render("GAME OVER", True, (200, 200, 200))
    screen.blit(text, (150, 200))
    small_font = pygame.font.Font("bauhaus.ttf", 30)
    text = small_font.render("Press any key to start over", True, (200, 200, 200))
    screen.blit(text, (10, 450))

def display_score(x, y):
    text = font.render("Score: " + str(score), True, (60, 60, 255))
    screen.blit(text, (x, y))

def player(x, y):
    screen.blit(playerImg, (x, y))

def enemy(enemyImg, x, y):
    screen.blit(enemyImg, (x, y))

def fire(x, y):
    global bullet_state
    bullet_state = "FIRE"
    screen.blit(bullet, (x + 16, y + 10))

def is_collision(enemyX, enemyY, bulletX, bulletY):
    distance = sqrt((pow(enemyX - bulletX, 2)) + (pow(enemyY - bulletY, 2)))
    return distance <= 27 and distance >= -27

def new_highscore(new):
    conn = sqlite3.connect("highscore.db")
    cur = conn.cursor()
    if new > get_highscore():
        cur.execute("UPDATE highscore SET value=?", (new,))
        conn.commit()
    conn.close()

def get_highscore():
    conn = sqlite3.connect("highscore.db")
    cur = conn.cursor()
    cur.execute("SELECT * FROM highscore")
    data = cur.fetchall()
    return data[0][0]

def display_highscore():
    text = font.render("High Score: " + str(get_highscore()), True, (60, 60, 255))
    screen.blit(text, (400, textY))

# Game Loop
running = True
gameover = False

setup()

while running:
    if not gameover:
        conn = sqlite3.connect("highscore.db")
        cur = conn.cursor()
        cur.execute("CREATE TABLE IF NOT EXISTS highscore (value)")
        cur.execute("SELECT * FROM highscore")
        data = cur.fetchall()
        if len(data) == 0:
            cur.execute("INSERT INTO highscore VALUES (0)")
            data = 0
        else:
            data = data[0][0]
        conn.commit()
        conn.close()
        # Background Image
        screen.blit(background, (0, 0))
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                new_highscore(score)
                running = False
            if event.type == pygame.KEYDOWN:
                if event.key == pygame.K_RIGHT:
                    playerX_change = 2
                if event.key == pygame.K_LEFT:
                    playerX_change = -2
                if event.key == pygame.K_SPACE and bullet_state == "READY":
                    bulletX = playerX
                    fire(bulletX, bulletY)
                    bullet_sound = pygame.mixer.Sound("laser.wav")
                    bullet_sound.play()
            if event.type == pygame.KEYUP:
                if event.key == pygame.K_RIGHT or event.key == pygame.K_LEFT:
                    playerX_change = 0
        playerX += playerX_change
        if playerX <= 0:
            playerX = 0
        elif playerX >= 736:
            playerX = 736
        for i in range(enemies):
            enemyX[i] += enemyX_change[i]
            if enemyY[i] > 440:
                for j in range(enemies):
                    enemyY[j] = 20000
                new_highscore(score)
                game_over_text()
                gameover = True
                break
            if enemyX[i] <= 0 or enemyX[i] >= 736:
                enemyX_change[i] = -enemyX_change[i]
                enemyY[i] += enemyY_change[i]
            collision = is_collision(enemyX[i], enemyY[i], bulletX, bulletY)
            if collision:
                explosion_sound = pygame.mixer.Sound("explosion.wav")
                explosion_sound.play()
                bulletY = playerY
                bullet_state = "READY"
                enemyX[i] = randint(0, 736)
                enemyY[i] = randint(50, 150)
                score += 1
            
        # Bullet Movement
        if bullet_state == "FIRE":
            fire(bulletX, bulletY)
            bulletY -= bulletY_change
        if bulletY <= 0:
            bulletY = playerY
            bullet_state = "READY"


        player(playerX, playerY)
        for Img, i, j in zip(enemyImg, enemyX, enemyY):
            enemy(Img, i, j)
        new_highscore(score)
        display_score(textX, textY)
        display_highscore()
        pygame.display.update()
    else:
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                running = False 
            if event.type == pygame.KEYDOWN:
                setup()
                gameover = False
