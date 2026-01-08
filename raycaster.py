import pygame
from math import sin, cos, floor, sqrt, radians
pygame.init()

# GENERAL SETUP:

viewWidth = 128
displayWidthX = int(viewWidth*5)
displayWidthY = int(displayWidthX*0.75)
trueZero = displayWidthY/2
screen = pygame.display.set_mode((displayWidthX, displayWidthY))
clock = pygame.time.Clock()
running = True

world = [
        "111111111111111",
        "100000000000001",
        "100000000000001",
        "100000000000001",
        "111111000011111",
        "100000000000001",
        "100000000000001",
        "100000000000001",
        "100000000000001",
        "100000000110001",
        "100000000110001",
        "100000000000001",
        "100000000000001",
        "100000000000001",
        "111111111111111"]

worldTextures = [
        "211111111111112",
        "200000000000002",
        "200000000000002",
        "200000000000002",
        "211113000031112",
        "200000000000002",
        "200000000000002",
        "200000000000002",
        "200000000000002",
        "200000000320002",
        "200000000230002",
        "200000000000002",
        "200000000000002",
        "200000000000002",
        "211111111111112"]

playerX = 7.0
playerY = 7.0
playerOrient = 45
speed = 0.067

FOV = 60

# BACKGROUND DRAWING INSTRUCTIONS

skyShade = 0
skyShadeChange = -0.25

def drawBackground():
    global skyShade, skyShadeChange
    
    screen.fill("grey")

    if skyShade == -20:
        skyShade = -19
        skyShadeChange = 0.25
    elif skyShade == 20:
        skyShade = 19
        skyShadeChange = -0.25
    else:
        skyShade = skyShade + skyShadeChange
    
    pygame.draw.rect(screen,(0,(100+skyShade),(200+skyShade)),(0,0,displayWidthX,(displayWidthY/2)))

# RAYCASTING ALGORITHM:

lineHeights = []
lineColors = []
rayCount = 0

def castRay(crIndex):
    stopCast = 0
        
    rayX = playerX
    rayY = playerY
    rayOrient = playerOrient - FOV/2 + (crIndex / viewWidth) * FOV
        
    dx = cos(radians(rayOrient))
    dy = sin(radians(rayOrient))
        
    while stopCast == 0:
        rayStep = 0.05

        rayX = (rayX+(dx*rayStep))
        rayY = (rayY+(dy*rayStep))

        mapX = floor(rayX)
        mapY = floor(rayY)
            
        if world[mapY][mapX] == "1":
                stopCast = 1
                         
    distance = sqrt(((rayX-playerX)**2)+((rayY-playerY)**2))
    distance = distance*(cos(radians(rayOrient - playerOrient)))
                    
    lineHeights.append(580/distance)
    lineColors.append(worldTextures[mapY][mapX])

# LINE DRAW INSTRUCTIONS

distanceLighting = 1

def drawRay(drIndex):
    lineHeight = (lineHeights[drIndex]/2)

    if distanceLighting == 1:
        rayShade = 55 + lineHeight
        
        if rayShade > 255:
            rayShade = 255
    else:
        rayShade = 155
                
    red = int(0)
    green = int(0)
    blue = int(0)
        
    if lineColors[drIndex] == "1":
        red = rayShade
    if lineColors[drIndex] == "2":
        green = rayShade
    if lineColors[drIndex] == "3":
        blue = rayShade
            
    pygame.draw.line(screen, (red,green,blue), [((drIndex*5))+2,(trueZero-lineHeight)], [((drIndex*5))+2,(trueZero+lineHeight)], width=5)

# CONTROLS AND COLLISION

def doControls():
    global playerX, playerY, playerOrient
    keys = pygame.key.get_pressed()

    oldX = playerX
    oldY = playerY

    if keys[pygame.K_w]:
        playerX = playerX + cos(radians(playerOrient)) * speed
        playerY = playerY + sin(radians(playerOrient)) * speed
        
    if keys[pygame.K_s]:
        playerX = playerX - cos(radians(playerOrient)) * speed
        playerY = playerY - sin(radians(playerOrient)) * speed


    if keys[pygame.K_a]:
        playerX = playerX + cos(radians(playerOrient-90)) * speed
        playerY = playerY + sin(radians(playerOrient-90)) * speed
        
    if keys[pygame.K_d]:
        playerX = playerX - cos(radians(playerOrient-90)) * speed
        playerY = playerY - sin(radians(playerOrient-90)) * speed

    if world[floor(playerY)][floor(playerX)] == "1":
            playerX = oldX
    if world[floor(playerY)][floor(playerX)] == "1":
            playerY = oldY

    if keys[pygame.K_LEFT]:
        if playerOrient == 0:
            playerOrient = 359
        else:
            playerOrient = playerOrient - 2
            
    if keys[pygame.K_RIGHT]:
        if playerOrient == 359:
            playerOrient = 0
        else:
            playerOrient = playerOrient + 2

# MAIN PROGRAM LOOP:

while running:
    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            running = False

    drawBackground()

    lineHeights = []
    lineColors = []
    rayCount = 0
    
    while not rayCount == 128:
        castRay(rayCount)
        drawRay(rayCount)
        rayCount = rayCount + 1

    pygame.display.flip()
    
    doControls()
    
    clock.tick(64)

pygame.quit()
