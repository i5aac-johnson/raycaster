import pygame
from math import sin, cos, tan, floor, ceil, sqrt, radians, pi

worlds = [ 
        [
        "111114511111111",
        "100000000000001",
        "100000000000001",
        "100000000000001",
        "111112000021111",
        "100000000000001",
        "100000000000001",
        "100000000000001",
        "100000003000001",
        "100000000000001",
        "100000000000001",
        "102100000000001",
        "101200000000001",
        "100000000000001",
        "111111111111111"],
        [
        "111111111111111",
        "100000000000001",
        "100000000000001",
        "100020000000001",
        "100020000000001",
        "100020000000001",
        "111111111000001",
        "100000001000001",
        "100000001000001",
        "100000001222001",
        "100000000000001",
        "100000001222001",
        "100000001002001",
        "100000001002001",
        "111111111111111"]
        ]

# Load default level from worlds array
defaultLevel = 0
world = worlds[defaultLevel]


# Let user select a level
validLevelInput = False
while validLevelInput != True:
    try:
        print("Select a level (1-"+ str(len(worlds)) + ")")
        userInput = int(input())
        if userInput < 1:
            print("Invalid input, try again...")
            print("Select a level (1-"+ str(len(worlds)) + ")")
            userInput = int(input())
        else:
            world = worlds[userInput - 1]
            break
    except IndexError or ValueError:
        print("That level is invalid. Loading level " + str(defaultLevel + 1))
        world = worlds[defaultLevel]
        break

pygame.init()

# GENERAL SETUP:

viewWidth = 128
displayWidthX = int(viewWidth*5)
displayWidthY = int(displayWidthX*0.75)
trueZero = displayWidthY/2
mapWidth = 15*20
screen = pygame.display.set_mode((displayWidthX + mapWidth, displayWidthY))
clock = pygame.time.Clock()
running = True

playerX = 7.0
playerY = 7.0
playerOrient = radians(45)
speed = 0.067
rotationSpeed = 2/60
FOV = radians(60)

# BACKGROUND DRAWING INSTRUCTIONS

skyShade = 0
skyShadeChange = -0.1

def drawBackground():
    global skyShade, skyShadeChange
    
    screen.fill("black")

    if skyShade < -20:
        skyShade = -20
        skyShadeChange = 0.1
    elif skyShade > 20:
        skyShade = 20
        skyShadeChange = -0.1
    else:
        skyShade = skyShade + skyShadeChange

    pygame.draw.rect(screen,(0,(100+skyShade),(200+skyShade)),(0,0,displayWidthX,(displayWidthY/2)))
    pygame.draw.rect(screen,("grey"),(0,displayWidthY/2,displayWidthX,(displayWidthY)))

# MAP DRAWING INSTRUCTIONS

def updateMap():
    global world, playerX, playerY, xHitLocations, yHitLocations
    sizePerCell = mapWidth/len(world[0])

    topLeftY = 0
    drawMapY = 0
    while drawMapY != len(world):
        drawMapX = 0
        topLeftX = displayWidthX + 1
        while drawMapX != len(world[drawMapY]):
            if world[drawMapY][drawMapX] != "0":
                pygame.draw.rect(screen,("red"),(topLeftX, topLeftY, sizePerCell,sizePerCell))  
            topLeftX = topLeftX + sizePerCell
            drawMapX = drawMapX + 1

        topLeftY = topLeftY + sizePerCell
        drawMapY = drawMapY + 1

    drawPlayerX = displayWidthX + (playerX * sizePerCell)
    drawPlayerY = playerY * sizePerCell

    drawMapLine = 0
    while drawMapLine != len(xHitLocations):
        drawLineX = displayWidthX + (xHitLocations[drawMapLine] * sizePerCell)
        drawLineY = yHitLocations[drawMapLine] * sizePerCell
        pygame.draw.aaline(screen, ("grey"), (drawPlayerX, drawPlayerY),(drawLineX, drawLineY))
        drawMapLine = drawMapLine + 1
        
    pygame.draw.circle(screen, ('white'), (drawPlayerX, drawPlayerY), 5)

# IMPORT TEXTURES FROM PNG

textures = []
textures.append(["placeholder"])

def fetchTexture(fileName,textureID):
    try:
        image = pygame.image.load(fileName)
    except:
        print("ERROR:",fileName,"was not found")
        image = pygame.image.load("missing.png")
    textures.append([])
    
    readPixelY = 0
    while not readPixelY == 16:
        textures[textureID].append([])
        readPixelX = 0
        while not readPixelX == 16:
            thisColor = image.get_at((readPixelX, readPixelY))
            
            textures[textureID][readPixelY].append(thisColor)
            
            readPixelX = readPixelX + 1
        readPixelY = readPixelY + 1

# RAYCASTING ALGORITHM:

lineHeights = []
rayCount = 0
sideHit = 0
xHitLocations = []
yHitLocations = []
hitTextLocations = []
rayTextures = []

def castRay(crIndex):
    global lineHeights, lineColors, sideHit, hitTextLocations, rayTextures

    rayOrient = playerOrient - FOV/2 + (crIndex / viewWidth) * FOV
    startX = playerX
    startY = playerY

    # SCAN VERTICAL LINES

    # which way are we going?
    if cos(rayOrient) < 0:
        stepX = -1
    elif cos(rayOrient) > 0:
        stepX = 1
    else:
        stepX = 0

    if stepX == 0:
        xDistance = float('inf')
    else:

        # what is our gradient?
        gradient = tan(rayOrient)

        # which line do we intersect next?
        if stepX == -1:
            lineX = floor(startX)
        if stepX == +1:
            lineX = ceil(startX)

        # how far away is this line on the x axis?
        distX = lineX - startX

        # what is y when we intersect this line?
        lineY = startY + (gradient*distX)

        # what is the distance on the hypotenuse to this intersection?
        lineDistX = sqrt((lineX - startX)**2 + (lineY - startY)**2)

        # how far is it between horizontal lines at this gradient?
        nextX = lineX + stepX
        nextDistX = nextX - lineX
        nextY = lineY + (gradient*nextDistX)
        nextDist = sqrt((nextX - lineX)**2 + (lineY - startY)**2)

        # scan loop
        xDistance = lineDistX
        rayX = lineX
        rayY = lineY
        scan = True
        while scan:
            # get coord of next cell
            if stepX == -1:
                nextCellX = rayX -1
            else:
                nextCellX = rayX
            mapY = floor(rayY)

            # check if we are out of bounds
            if nextCellX < 0 or nextCellX > (len(world)-1) or mapY < 0 or mapY > (len(world)-1):
                xDistance = float('inf')
                scan = False
            else:
                if world[mapY][nextCellX] != "0":
                    scan = False
                else:
                    rayX = rayX + stepX
                    rayY = startY + gradient * (rayX - startX)
                    xDistance = sqrt((rayX - startX)**2 + (rayY - startY)**2)
        vRayX = rayX
        vRayY = rayY

    # SCAN HORIZONTAL LINES

    # which way are we going?
    if sin(rayOrient) < 0:
        stepY = -1
    elif sin(rayOrient) > 0:
        stepY = 1
    else:
        stepY = 0

    if stepY == 0:
        yDistance = float('inf')
    else:

        # what is our gradient?
        gradient = 1/tan(rayOrient)

        # which line do we intersect next?
        if stepY == -1:
            lineY = floor(startY)
        if stepY == +1:
            lineY = ceil(startY)

        # how far away is this line on the y axis?
        distY = lineY - startY

        # what is x when we intersect this line?
        lineX = startX + (gradient*distY)

        # what is the distance on the hypotenuse to this intersection?
        lineDistY = sqrt((lineY - startY)**2 + (lineX - startX)**2)

        # how far is it between vertical lines at this gradient?
        nextY = lineY + stepY
        nextDistY = nextY - lineY
        nextX = lineX + (gradient*nextDistY)
        nextDist = sqrt((nextY - lineY)**2 + (lineX - startX)**2)

        # scan loop
        yDistance = lineDistY
        rayY = lineY
        rayX = lineX
        scan = True
        while scan:
            # get coord of next cell
            if stepY == -1:
                nextCellY = rayY -1
            else:
                nextCellY = rayY
            mapX = floor(rayX)

            # check if we are out of bounds
            if nextCellY < 0 or nextCellY > (len(world)-1) or mapX < 0 or mapX > (len(world)-1):
                yDistance = float('inf')
                scan = False
            else:
                if world[nextCellY][mapX] != "0":
                    scan = False
                else:
                    rayY = rayY + stepY
                    rayX = startX + gradient * (rayY - startY)
                    yDistance = sqrt((rayY - startY)**2 + (rayX - startX)**2)
        hRayX = rayX
        hRayY = rayY
        
    # take the distance of the shortest scan  
    
    if xDistance < yDistance:
        distance = xDistance
        bestRayX = vRayX
        bestRayY = vRayY

        textX = int((bestRayY % 1) * 16)
        if (stepX < 0):
            textX = 15 - textX
            mapX = floor(bestRayX)-1
        else:
            mapX = floor(bestRayX)

        mapY = floor(bestRayY)

        sideHit = 0
    else:
        distance = yDistance
        bestRayX = hRayX
        bestRayY = hRayY

        textX = int((bestRayX % 1) * 16)
        if (stepY > 0):
            textX = 15 - textX
            mapY = floor(bestRayY)
        else:
            mapY = floor(bestRayY)-1

        mapX = floor(bestRayX)

        sideHit = 1

    rayTextures.append(int(world[mapY][mapX])-1)
    hitTextLocations.append(textX)

    # fisheye correction
    distance = distance*cos(rayOrient - playerOrient)

    # add to our output
    if distance == 0:
        lineHeights.append(580)
    else:
        lineHeights.append(580/distance)

    xHitLocations.append(bestRayX)
    yHitLocations.append(bestRayY)

# LINE DRAW INSTRUCTIONS

def drawRay(drIndex):
    global blue
    
    lineHeight = (lineHeights[drIndex]/2)

    lineSegment = int(0)
    segmentStartY = trueZero - lineHeight
    segmentHeight = ((lineHeight*2)/16)
    
    while lineSegment != 16:
        
        red = textures[rayTextures[drIndex]][lineSegment][hitTextLocations[drIndex]][0]
        green = textures[rayTextures[drIndex]][lineSegment][hitTextLocations[drIndex]][1] 
        blue = textures[rayTextures[drIndex]][lineSegment][hitTextLocations[drIndex]][2]

        if sideHit == 1:
            red = red - 50
            if red < 0:
                    red = 0
            green = green - 50
            if green < 0:
                green = 0
            blue = blue - 50
            if blue < 0:
                blue = 0
    
        pygame.draw.line(screen, (red,green,blue), [((drIndex*5))+2,(segmentStartY)], [((drIndex*5))+2,(segmentStartY+segmentHeight)], width=5)

        segmentStartY = segmentStartY + segmentHeight
        lineSegment = lineSegment + 1

# CONTROLS AND COLLISION

def doControls():
    global playerX, playerY, playerOrient
    keys = pygame.key.get_pressed()

    oldX = playerX
    oldY = playerY

    if keys[pygame.K_w]:
        playerX = playerX + cos(playerOrient) * speed
        if world[floor(playerY)][floor(playerX)] != "0":
            playerX = oldX
        playerY = playerY + sin(playerOrient) * speed
        if world[floor(playerY)][floor(playerX)] != "0":
            playerY = oldY
        
    if keys[pygame.K_s]:
        playerX = playerX - cos(playerOrient) * speed
        if world[floor(playerY)][floor(playerX)] != "0":
            playerX = oldX
        playerY = playerY - sin(playerOrient) * speed
        if world[floor(playerY)][floor(playerX)] != "0":
            playerY = oldY

    if keys[pygame.K_a]:
        playerX = playerX + cos(playerOrient-radians(90)) * speed
        if world[floor(playerY)][floor(playerX)] != "0":
            playerX = oldX
        playerY = playerY + sin(playerOrient-radians(90)) * speed
        if world[floor(playerY)][floor(playerX)] != "0":
            playerY = oldY
        
    if keys[pygame.K_d]:
        playerX = playerX - cos(playerOrient-radians(90)) * speed
        if world[floor(playerY)][floor(playerX)] != "0":
            playerX = oldX
        playerY = playerY - sin(playerOrient-radians(90)) * speed
        if world[floor(playerY)][floor(playerX)] != "0":
            playerY = oldY

    if keys[pygame.K_LEFT]:
        playerOrient = (playerOrient - rotationSpeed) % (2*pi)
            
    if keys[pygame.K_RIGHT]:
        playerOrient = (playerOrient + rotationSpeed) % (2*pi)

# MAIN PROGRAM LOOP:

textures = []
fetchTexture("cobble.png",0)
fetchTexture("wood.png",1)
fetchTexture("tnt.png",2)
fetchTexture("weird1.png",3)
fetchTexture("weird2.png",4)
print("imported textures!")

firstLoop = 1
    
while running:
    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            running = False

    drawBackground()
    
    if firstLoop == 1:
        print("can draw background!")

    hitTextLocations = []
    rayTextures = []
    
    xHitLocations = []
    yHitLocations = []
    
    lineHeights = []
    lineColors = []
    rayCount = 0
    
    while not rayCount == 128:
        castRay(rayCount)
        drawRay(rayCount)
        rayCount = rayCount + 1

    if firstLoop == 1:
        print("can render world!")

    updateMap()

    if firstLoop == 1:
        print("can draw map!")

    pygame.display.flip()
    
    doControls()
    
    clock.tick(64)

    firstLoop = 0

pygame.quit()
