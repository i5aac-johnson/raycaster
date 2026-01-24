import pygame
from math import sin, cos, tan, floor, ceil, sqrt, radians, pi

collision = []
ceilings = []
walls = []
floors = []

worldIndex = 0
world = []

# GENERAL SETUP:

pygame.init()

viewWidth = 128
displayWidthX = int(viewWidth*5)
displayWidthY = int(displayWidthX*0.75)
trueZero = displayWidthY/2
mapWidth = 15*20
screen = pygame.display.set_mode((displayWidthX + mapWidth, displayWidthY))
clock = pygame.time.Clock()
FOV = radians(60)
planeDistance = displayWidthX / ((2*tan(FOV/2)))

running = True

# PLAYER VALUES:

playerX = 7.0
playerY = 7.0

playerMapX = 7
playerMapY = 7

playerOrient = radians(45)
speed = 0.067
rotationSpeed = 2/60

# IMPORT LEVEL INSTRUCTIONS

def importWorld(filename):
    with open(filename) as file:
        lines = [line.rstrip() for line in file]

    print("importing level data from",filename)

    fileLine = 0

    fileLineOld = fileLine
    if lines[fileLine] == "collision(":
        fileLine = 1
        importCollision = []

        while not lines[fileLine] == ")":
            importCollision.append(lines[fileLine])
            fileLine = fileLine + 1
        collision.append(importCollision)
        
        print("imported collision data from",filename,"line",fileLineOld,"to",fileLine)

    else:
        print("collision data not found")

    fileLine += 1
    fileLineOld = fileLine
    
    if lines[fileLine] == "ceilings(":
        fileLine += 1
        importCeilings = []
        
        while not lines[fileLine] == ")":
            ceilingLine = [int(x) for x in (lines[fileLine].split(','))]
            
            importCeilings.append(ceilingLine)
            fileLine += 1
        ceilings.append(importCeilings)
        
        print("imported ceiling texture data from",filename,"line",fileLineOld,"to",fileLine)

    else:
        print("ceiling texture data not found")

    fileLine = fileLine + 1
    fileLineOld = fileLine
    
    if lines[fileLine] == "walls(":
        fileLine += 1
        importWalls = []
        
        while not lines[fileLine] == ")":
            wallLine = [int(x) for x in (lines[fileLine].split(','))]
            
            importWalls.append(wallLine)
            fileLine += 1
        walls.append(importWalls)
        
        print("imported wall texture data from",filename,"line",fileLineOld,"to",fileLine)

    else:
        print("wall texture data not found")

    fileLine += 1
    fileLineOld = fileLine
    
    if lines[fileLine] == "floors(":
        fileLine += 1
        importFloors = []
        
        while not lines[fileLine] == ")":
            floorLine = [int(x) for x in (lines[fileLine].split(','))]
            
            importFloors.append(floorLine)
            fileLine += 1
        floors.append(importFloors)
        
        print("imported floor texture data from",filename,"line",fileLineOld,"to",fileLine)

    else:
        print("floor texture data not found")

# SET WARPS:

warpX = [1,16,11,2]
warpY = [2,18,13,4]
warpWorld = [0,0,0,1]

warpDestX = [16,1,2,11]
warpDestY = [18,2,4,13]
warpDestWorld = [0,0,1,0]
warpDestOrientation = [0,0,270,270]

# TELEPORT FUNCTION

lockWarp = 0
oldWarpX = 0
oldWarpY = 0

def doWarps():
    global worldIndex, playerX, playerY, world, oldWarpX, oldWarpY, lockWarp, playerOrient
    for teleportIndex in range(len(warpWorld)):
        if (warpWorld[teleportIndex] == worldIndex and
            warpX[teleportIndex] == playerMapX and
            warpY[teleportIndex] == playerMapY):

                teleportWorld = warpDestWorld[teleportIndex]
                teleportX = warpDestX[teleportIndex]
                teleportY = warpDestY[teleportIndex]

                if lockWarp == 0:
                    print("teleported the player from (",playerMapX,playerMapY,") in level",worldIndex+1,"to (",teleportX,teleportY,") in level",teleportWorld+1)

                    oldWarpX = teleportX
                    oldWarpY = teleportY
                    
                    playerX = teleportX + 0.5
                    playerY = teleportY + 0.5
                    worldIndex = teleportWorld
                    world = collision[worldIndex]
                    playerOrient = radians(warpDestOrientation[teleportIndex])

                    lockWarp = 1
                    print("locked teleportation!")
                    # we want warps disabled after teleport, until player moves to a different tile.

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
    global world, playerX, playerY, xHitLocation, yHitLocation
    sizePerCell = mapWidth/len(world[0])

    topLeftY = 0
    for drawMapY in range(0,len(world)):
        drawMapX = 0
        topLeftX = displayWidthX + 1
        for drawMapX in range(0,len(world[drawMapY])):
            if world[drawMapY][drawMapX] != "0":
                pygame.draw.rect(screen,("red"),(topLeftX, topLeftY, sizePerCell,sizePerCell))  
            topLeftX += sizePerCell

        topLeftY += sizePerCell

    drawPlayerX = displayWidthX + (playerX * sizePerCell)
    drawPlayerY = playerY * sizePerCell

    drawMapLine = 0
    for drawMapLine in range(0,len(xHitLocations)):
        drawLineX = displayWidthX + (xHitLocations[drawMapLine] * sizePerCell)
        drawLineY = yHitLocations[drawMapLine] * sizePerCell
        pygame.draw.aaline(screen, ("grey"), (drawPlayerX, drawPlayerY),(drawLineX, drawLineY))
        
    pygame.draw.circle(screen, ('white'), (drawPlayerX, drawPlayerY), 5)

# IMPORT TEXTURES FROM PNG

textures = []
textureSize = 16
textures.append(["placeholder"])

def fetchTexture(fileName,textureID):
    try:
        image = pygame.image.load(fileName)
    except:
        print("ERROR:",fileName,"was not found")
        image = pygame.image.load("missing.png")
    else:
        print("imported texture data from",fileName)
    textures.append([])
    
    for readPixelY in range(0, textureSize):
        textures[textureID].append([])
        readPixelX = 0
        for readPixelX in range(0, textureSize):
            thisColor = image.get_at((readPixelX, readPixelY))
            textures[textureID][readPixelY].append(thisColor)

# RAYCASTING ALGORITHM:

xHitLocations = []
yHitLocations = []
rayCount = 0

def castRay(crIndex):

    rayOrient = playerOrient - FOV/2 + (crIndex / viewWidth) * FOV
    startX = playerX
    startY = playerY

    # which way are we going?
    # vertical
    skipVScan = False
    if cos(rayOrient) < 0:
        stepX = -1
    elif cos(rayOrient) > 0:
        stepX = 1
    else:
        stepX = 0
    if stepX == 0:
        xDistance = float('inf')
        skipVScan = True

    # horizontal
    skipHScan = False
    if sin(rayOrient) < 0:
        stepY = -1
    elif sin(rayOrient) > 0:
        stepY = 1
    else:
        stepY = 0
    if stepY == 0:
        yDistance = float('inf')
        skipHScan = True

    if skipVScan == False or skipHScan == False:

        # what is our gradient?
        vGradient = tan(rayOrient)
        hGradient = 1/tan(rayOrient)

        # which lines do we intersect next?
        # vertical
        if stepX == -1:
            nextVLineX = floor(startX)
        if stepX == +1:
            nextVLineX = ceil(startX)
            
        distX = nextVLineX - startX # how far away is the next vertical line on the x axis?

        nextVLineY = startY + (vGradient*distX) # what is y when we intersect this line?

        # what is the distance on the hypotenuse to this intersection?
        lineDistX = sqrt((nextVLineX - startX)**2 + (nextVLineY - startY)**2)
        
        # horizontal
        if stepY == -1:
            nextHLineY = floor(startY)
        if stepY == +1:
            nextHLineY = ceil(startY)

        distY = nextHLineY - startY # how far away is the next horizontal line on the y axis?
        
        nextHLineX = startX + (hGradient*distY) # what is x when we intersect this line?

        # what is the distance on the hypotenuse to this intersection?
        lineDistY = sqrt((nextHLineY - startY)**2 + (nextHLineX - startX)**2)

        # scan loop
        xDistance = lineDistX
        vRayX = nextVLineX
        vRayY = nextVLineY
        
        yDistance = lineDistY
        hRayY = nextHLineY
        hRayX = nextHLineX
        
        scan = True
        while scan:
            # vertical
            if skipVScan == False and xDistance <= yDistance: # we want to try to loop for the shorter ray
                if stepX == -1:
                    nextCellX = vRayX -1
                else:
                    nextCellX = vRayX
                mapY = floor(vRayY)  # get coord of next cell

                if nextCellX < 0 or nextCellX > (len(world)-1) or mapY < 0 or mapY > (len(world)-1):
                    xDistance = float('inf')
                    scan = False # check if we are out of bounds
                else:
                    if world[mapY][nextCellX] != "0":
                        scan = False # check for hits
                    else:
                        vRayX = vRayX + stepX # step
                        vRayY = startY + vGradient * (vRayX - startX)
                        xDistance = sqrt((vRayX - startX)**2 + (vRayY - startY)**2)

            # horizontal
            elif skipHScan == False and xDistance > yDistance:
                if stepY == -1:
                    nextCellY = hRayY -1
                else:
                    nextCellY = hRayY
                mapX = floor(hRayX) # get coord of next cell

                if nextCellY < 0 or nextCellY > (len(world)-1) or mapX < 0 or mapX > (len(world)-1):
                    yDistance = float('inf')
                    scan = False # check if we are out of bounds
                else:
                    if world[nextCellY][mapX] != "0":
                        scan = False # check for hits
                    else:
                        hRayY += stepY # step
                        hRayX = startX + hGradient * (hRayY - startY)
                        yDistance = sqrt((hRayY - startY)**2 + (hRayX - startX)**2)

            else:
                scan = False # break if we don't want to scan at all
        
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

    xHitLocations.append(bestRayX)
    yHitLocations.append(bestRayY)

    rayTexture = (int(walls[worldIndex][mapY][mapX])-1)

    # fisheye correction
    distance = distance*cos(rayOrient - playerOrient)

    # add to our output
    if distance == 0:
        lineHeight = 580
    else:
        lineHeight = 580/distance

    return (sideHit, rayTexture, textX, lineHeight, bestRayX, bestRayY)

# LINE DRAW INSTRUCTIONS

def drawRay(drIndex, sideHit, rayTexture, textX, lineHeight, bestRayX, bestRayY):
    global blue
    
    lineHeight = (lineHeight/2)

    lineSegment = int(0)
    segmentStartY = trueZero - lineHeight
    segmentHeight = ((lineHeight*2)/16)

    for lineSegment in range(0,textureSize):
        red = textures[rayTexture][lineSegment][textX][0]
        green = textures[rayTexture][lineSegment][textX][1] 
        blue = textures[rayTexture][lineSegment][textX][2]

        if sideHit == 1:
            red = red - 30
            if red < 0:
                    red = 0
            green = green - 30
            if green < 0:
                green = 0
            blue = blue - 30
            if blue < 0:
                blue = 0
    
        pygame.draw.line(screen, (red,green,blue), [((drIndex*5))+2,(segmentStartY)], [((drIndex*5))+2,(segmentStartY+segmentHeight)], width=5)

        segmentStartY += segmentHeight

# CONTROLS AND COLLISION

def doControls():
    global playerX, playerY, playerOrient
    keys = pygame.key.get_pressed()

    oldX = playerX
    oldY = playerY

    if keys[pygame.K_w]:
        playerX += cos(playerOrient) * speed
        if world[floor(playerY)][floor(playerX)] != "0":
            playerX = oldX
        playerY += sin(playerOrient) * speed
        if world[floor(playerY)][floor(playerX)] != "0":
            playerY = oldY
        
    if keys[pygame.K_s]:
        playerX -= cos(playerOrient) * speed
        if world[floor(playerY)][floor(playerX)] != "0":
            playerX = oldX
        playerY -= sin(playerOrient) * speed
        if world[floor(playerY)][floor(playerX)] != "0":
            playerY = oldY

    if keys[pygame.K_a]:
        playerX += cos(playerOrient-radians(90)) * speed
        if world[floor(playerY)][floor(playerX)] != "0":
            playerX = oldX
        playerY += sin(playerOrient-radians(90)) * speed
        if world[floor(playerY)][floor(playerX)] != "0":
            playerY = oldY
        
    if keys[pygame.K_d]:
        playerX -= cos(playerOrient-radians(90)) * speed
        if world[floor(playerY)][floor(playerX)] != "0":
            playerX = oldX
        playerY -= sin(playerOrient-radians(90)) * speed
        if world[floor(playerY)][floor(playerX)] != "0":
            playerY = oldY

    if keys[pygame.K_LEFT]:
        playerOrient = (playerOrient - rotationSpeed) % (2*pi)
            
    if keys[pygame.K_RIGHT]:
        playerOrient = (playerOrient + rotationSpeed) % (2*pi)

# MAIN PROGRAM LOOP:

worldFiles = ["myWorld.txt","newWorld.txt"]
for item in worldFiles:
    importWorld(item)

world = collision[worldIndex]


textures = []
fetchTexture("cobble.png",0)
fetchTexture("wood.png",1)
fetchTexture("tnt.png",2)
fetchTexture("weird1.png",3)
fetchTexture("weird2.png",4)
fetchTexture("portal.png",5)
fetchTexture("frame.png",6)
print("imported textures!")

# Load default level from worlds array
defaultLevel = 0

world = collision[defaultLevel]
worldIndex = defaultLevel


# Let user select a level
skipLevelSelect = True

while skipLevelSelect != True:
    try:
        print("Select a level (1-"+ str(len(collision)) + ")")
        userInput = int(input())
        if userInput < 1:
            print("Invalid input, try again...")
            print("Select a level (1-"+ str(len(collision)) + ")")
            userInput = int(input())
        else:
            world = collision[userInput - 1]
            worldIndex = userInput - 1
            break
    except IndexError or ValueError:
        print("That level is invalid. Loading level " + str(defaultLevel + 1))
        world = collision[defaultLevel]
        worldIndex = userInput - 1
        break

firstLoop = 1
    
while running:
    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            running = False

    drawBackground()
    
    if firstLoop == 1:
        print("can draw background!")

    xHitLocations = []
    yHitLocations = []
    
    for rayCount in range(0,viewWidth):
        sideHit, rayTexture, textX, lineHeight, bestRayX, bestRayY = castRay(rayCount)
        drawRay(rayCount, sideHit, rayTexture, textX, lineHeight, bestRayX, bestRayY)

    if firstLoop == 1:
        print("can render world!")

    updateMap()

    if firstLoop == 1:
        print("can draw map!")

    pygame.display.flip()
    
    doControls()

    playerMapX = floor(playerX)
    playerMapY = floor(playerY)

    if lockWarp == 1:
        if playerMapX != oldWarpX or playerMapY != oldWarpY:
            lockWarp = 0
            print("unlocked teleportation!")
        

    doWarps()
    
    clock.tick(64)

    firstLoop = 0

pygame.quit()
print("game window was closed")
