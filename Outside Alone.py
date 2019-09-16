#***
#Outside Alone
#***
#Zombie survival game
#Henri Johann Norden, 4.11.2014
#***


targetFps = 60 #Multiple of 30
dynamicFps = True #Allow the game to lower the fps when performance is low
screenSize = (1280,720)

#Startup
from math import *
from random import *
from pygame import *
import os
init()
font.init()
screen = display.set_mode(screenSize)

#Background related images
background = image.load("Game/background.png")
multiplier = screenSize[0]/background.get_rect()[2] #Pixel multiplier
background = transform.scale(background, screenSize)
newFence = image.load("Game/Fence/0.png")
fence = transform.scale(newFence, (int(newFence.get_rect()[2]*multiplier), int(newFence.get_rect()[3]*multiplier)))
overlayRed = Surface.convert(transform.scale(image.load("Game/redOverlay.png"), screenSize))
overlayBlack = Surface.convert(transform.scale(image.load("Game/blackOverlay.png"), screenSize))
overlayBlack.set_alpha(0)

# Blood
bloodDot = Surface((int(1.5*multiplier),int(1.5*multiplier)))

#Menu: main/game/shop
menu = "none"

#Base health amount
baseHP = 1000
maxBaseHP = baseHP

#Item list for shop
#gunList = ["Pistol","UZI","Shotgun","Crossbow","RPG",]
#gunPrice = [0, 25, 50, 100, 500]
turretPrice = 500
#Prices for turret upgrades [damage, fire rate]
turretUpgrades = []
for i in range(7):
    turretUpgrades.append([150,250])
#Lists of available upgrades
gunUpgrades = ["Damage","Fire rate","Reload spd","Mag size","Penetration","Bullets/shot","Explosions!"]
baseUpgrades = ["Repair","Max HP","Mines","","Cillit Bang!","Better mines","M-Turret 9k"]
#Upgrade descriptions
upgradeDescription = [[[1,"+ Damage"]],[[1,"+ Fire rate"]],[[1,"+ Reload speed"]],[[1,"+3 Magazine size"]],[[1,"+ Bullet penetration"]],[[1,"+1 Bullets per shot"],[0, "+ Bullet spread"],[0, "- Reload speed"],[0, "- Fire rate"],[0, "-3 Magazine size"]],[[1, "Explosive bullets!!!"],[1, "+ Damage"],[0,"- Reload speed"],[0, "- Fire rate"],[0,"-5 Magazine size"]]]
baseUpgradeDescription = [[[1,"+20% of max HP"]],[[1,"+50% Max HP"]],[[1,"+ Random mines!"]],[[0,""]],[[1,"Bang!"],[1,"And the blood is gone!"]],[[1,"Now even explodier!"]],[[1,"At least 10% more"],[1,"death, guaranteed!"],[0,"Upgrades purchased"],[0,"turrets only"]]]
#Cost of upgrades
upgradeCost = [100,100,200,250,500,750,2000] #gun upgrades
baseUpgradeCost = [100, 250, 50, 0, 4.99, 2500, 9999]
#List to check whether upgrades are maxed
upgradeMaxed = [False] * 7
baseUpgradeMaxed = [False] * 7
baseUpgradeMaxed[3] = True


#Gun list: [[gun name, damage, fire rate, bullets per shot, mag size, penetration, muzzle flash, muzzle size multiplier, price, bullet spread]]
guns = [
    ["Pistol", 10, 15, 1, 7, 0, 1, 0.5, 0, 2.5],
    ["UZI", 7, 3, 1, 30, 0, 1, 0.75, 50, 1],
    ["Shotgun", 20, 25, 6, 2, 3, 1, 1.2, 100, 5],
    ["Pump", 30, 15, 8, 8, 2, 1, 1, 250, 3],
    ["Crossbow", 100, 50, 1, 1, 6, 0, 0, 500, 0],
    ["RPG", 100, 50, 1, 1, 0, 2, 1.5, 500, 0.5],
]
#Mine base config: [damage, detection radius, explosion size]
mineValues = [35, 15, 1]

#Variables for tracking cheats
cheats = ""
lastCheat = 0
#Player controls
#[left, right, shoot]
#Note: shooting with key controls is broken - wrong accuracy
controls = [[276, 275, None]]
#Zombie spawning (and stopping) locations
startX = []
endX = []
endY = 0
#Zombie image cache
zombieImages = []
zombieRect = []
#Projectile image cache
projectileImages = []
projectileRect = []
projectileMask = []
#Zombie object list
zombies = []
#Bullet object list
bullets = []
#Game button list
buttons = []
#Shop button list
shop = []
#Player list
players = []
#Text object list
texts = []
#Shop text object list
shopTexts = []
#Temporary list for blood drops that have hit the ground
bloods = []
#Turret list
turrets = []
#List for checking the average fps
averageFps = []
#List of currently happening explosions
explosions = []
#List of dropping meat chunks
meatChunks = []
meatRect = []
#List of music files
music = []
#List of mines
mines = []


#Counters
shopTick = 0 #the tick when the shop was last closed
tick = 0
difficulty = 0 #unused
wave = 1 #default: 1
waveMulti = 1 #default: 1
lastSpawn = 0
zombieSpawn = 10
damaged = 0
playerAmount = 0
endGame = 0
seekPos = 0
seekTrack = -1
shopMusic = 0
sleep = 0

#Sound effects
mixer.set_num_channels(16)
gunFX = mixer.Sound("./Game/Sounds/pistol.ogg")
gunFX.set_volume(0.5)
turretFX = mixer.Sound("./Game/Sounds/turret.ogg")
turretFX.set_volume(0.2)
rpgFX = mixer.Sound("./Game/Sounds/rpg.ogg")
rpgFX.set_volume(0.75)
explosionFX = mixer.Sound("./Game/Sounds/explosion.ogg")
explosionFX.set_volume(0.6)
reloadFX = mixer.Sound("./Game/Sounds/reload.ogg")
reloadFX.set_volume(0.7)
reloadStop = mixer.Sound("./Game/Sounds/reloadStop.ogg")
reloadStop.set_volume(0.5)
#deathFX = mixer.Sound("./Game/Sounds/death.ogg")
#deathFX.set_volume(0.5)

class testSprite: None

class zomBasic:
    def __init__(self):
        zombieSelect = randint(1,len(zombieImages[0]))-1
        self.image = zombieImages[0][zombieSelect]
        self.rect = zombieRect[0][zombieSelect]
        self.blood = []
        self.dead = False
        self.currentImage = 0
        self.mask = mask.from_surface(self.image[0])
        self.startLoc = randint(0,len(startX)-1)
        self.xStart = startX[self.startLoc]-self.rect[0][2]/2
        self.xEnd = endX[self.startLoc]-self.rect[0][2]/2
        self.x = self.xStart
        self.y = -1-self.rect[0][3]
        self.speed = uniform(4.5,5.5)*multiplier*(0.75+waveMulti/4)
        self.health = 20*waveMulti
        #self.anim = [frames:[frame1:image, speedmultiplier, tickPause],[frame2:...]]
        self.anim = [[0, 0, 20], [1, 0.5, 2], [2, 0.75, 2], [3, 0.75, 2]]
        self.animFrame = 0
        self.lastRun = 0
        self.damage = int(50*waveMulti)
        self.attackSpd = 150-wave
        self.money = int((5 + randint(0,3))*(2*(waveMulti-0.5)))


class zomFat:
    #Basic zombie class
    def __init__(self):
        zombieSelect = randint(1,len(zombieImages[2]))-1
        self.image = zombieImages[2][zombieSelect]
        self.rect = zombieRect[2][zombieSelect]
        self.blood = []
        self.dead = False
        self.currentImage = 0
        self.mask = mask.from_surface(self.image[0])
        self.startLoc = randint(0,len(startX)-1)
        self.xStart = startX[self.startLoc]-self.rect[0][2]/2
        self.xEnd = endX[self.startLoc]-self.rect[0][2]/2
        self.x = self.xStart
        self.y = -1-self.rect[0][3]
        self.speed = uniform(4,5)*multiplier*(0.75+waveMulti/4)
        self.health = 80*waveMulti
        #self.anim = [frames:[frame1:image, speedmultiplier, tickPause],[frame2:...]]
        self.anim = [[0, 0, 25], [1, 1, 5], [0, 0, 10], [2, 1, 5]]
        self.animFrame = 0
        self.lastRun = 0
        self.damage = int(100*waveMulti)
        self.attackSpd = 200-wave
        self.money = int((9 + randint(0,3))*(2*(waveMulti-0.5)))


class zomFast:
    #Basic zombie class
    def __init__(self):
        zombieSelect = randint(1,len(zombieImages[1]))-1
        self.image = zombieImages[1][zombieSelect]
        self.rect = zombieRect[1][zombieSelect]
        self.blood = []
        self.dead = False
        self.currentImage = 0
        self.mask = mask.from_surface(self.image[0])
        self.startLoc = randint(0,len(startX)-1)
        self.xStart = startX[self.startLoc]-self.rect[0][2]/2
        self.xEnd = endX[self.startLoc]-self.rect[0][2]/2
        self.x = self.xStart
        self.y = -1-self.rect[0][3]
        self.speed = uniform(5.5,6.5)*multiplier*(0.75+waveMulti/4)
        self.health = 10*waveMulti
        #self.anim = [frames:[frame1:image, speedmultiplier, tickPause],[frame2:...]]
        self.anim = [[0, 0, 10], [1, 1, 3], [0, 0.2, 5], [2, 1, 3]]
        self.animFrame = 0
        self.lastRun = 0
        self.damage = int(30*waveMulti)
        self.attackSpd = 100-wave
        self.money = int((7 + randint(0,3))*(2*(waveMulti-0.5)))


class player:
    #Class for players
    def __init__(self, playerNo):
        self.image = []
        self.rect = []
        for i in os.listdir("./Game/Player/"):
            tempImg = image.load("./Game/Player/"+i)
            tempRect = tempImg.get_rect()
            tempImg = transform.scale(tempImg, (int(tempRect[2]*multiplier), int(tempRect[3]*multiplier)))
            self.image.append(tempImg)
            self.rect.append(tempImg.get_rect())
        self.gun = None
        self.guns = []
        self.x = 160*multiplier-self.rect[0][2]
        self.y = 120*multiplier
        self.speed = 20
        #self.anim = [frames:[frame1:image, speedmultiplier, tickPause],[frame2:...]]
        #self.anim[0] = idle; self.anim[1] = move left; self.anim[2] = move right
        self.anim = [[[0, 0, 0]],
                     [[0, 1, 1], [1, 1, 1], [2, 1.5, 1], [1, 1, 1]],
                     [[0, 1, 1], [3, 1, 1], [4, 1.5, 1], [3, 1, 1]]]
        self.animFrame = [0,0]
        self.currentImage = 0
        self.lastRun = 0
        self.money = 1
        self.keys = controls[playerNo]
        self.pressed = []
        self.killed = 0
        for i in range(len(self.keys)+1):
            self.pressed.append(0)


class button:
    #Class for making shop buttons
    #NB: All arguments must be lists
    def __init__(self, boxSize, color, location, price, text, textSize, textColor, textLocation):
        self.color = color
        self.text = text
        self.size = []
        self.image = Surface((int(boxSize[0][0]*multiplier),int(boxSize[0][1]*multiplier)))
        self.rect = self.image.get_rect()
        for i in range(len(boxSize)):
            self.size.append((boxSize[i][0]*multiplier,boxSize[i][1]*multiplier))
            tempImg = Surface(self.size[i])
            tempImg.fill(self.color[i])
            self.image.blit(tempImg, ((self.rect[2]-tempImg.get_rect()[2])/2,(self.rect[3]-tempImg.get_rect()[3])/2))
            self.image = Surface.convert(self.image)
        self.textColor = textColor
        self.textLocation = textLocation
        self.textSize = textSize
        self.x,self.y = location
        self.location = (location[0]*multiplier,location[1]*multiplier)
        self.rect.move_ip(self.location[0],self.location[1])
        self.price = price
        for i in range(len(textLocation)):
            if textLocation[i][0] == "mid":
                termFont = font.Font(None,int(self.textSize[i]*multiplier))
                if i < len(text):
                    self.textLocation[i] = ((int(self.size[0][0]-termFont.size(text[i])[0])/2),textLocation[i][1])
                else:
                    self.textLocation[i] = ((int(self.size[0][0]-termFont.size("Price: "+str(self.price))[0])/2),textLocation[i][1])
        self.makeImage()
        self.item = 0

    def makeImage(self):
        for i in range(len(self.text)):
            termFont = font.Font(None,int(self.textSize[i]*multiplier))
            text = termFont.render(self.text[i], False, self.textColor[i])
            self.image.blit(text, self.textLocation[i])
            self.image = Surface.convert(self.image)
        if self.price != -1:
            text = termFont.render("Price: "+str(self.price), False, self.textColor[i+1])
            self.image.blit(text, self.textLocation[len(self.textLocation)-1])
            self.image = Surface.convert(self.image)

    def onClick(self):
        print("No function defined for this button!")

    def check(self, item):
        if players[0].money >= item:
            players[0].money -= ceil(item)
            return True
        else:
            return False

    def makeTurret(self):
        global turretPrice
        if self.check(turretPrice):
            turrets.append(turret(self.item))

    def turretUpgrade(self):
        global turretUpgrades
        for i in range(len(turrets)):
            if turrets[i].pos == self.item:
                selected = i
                break
        if self.text[0][0] == "D":
            if self.check(turretUpgrades[self.item][0]):
                turretUpgrades[self.item][0] += int(turretUpgrades[self.item][0]*0.5)
                turrets[selected].damage += 5
        elif self.text[0][0] == "F":
            if self.check(turretUpgrades[self.item][1]):
                turretUpgrades[self.item][1] += int(turretUpgrades[self.item][1]*0.5)
                turrets[selected].fireRate -= 6

    def gunUpgrade(self):
        global gunUpgrades, multiplier, upgradeCost
        up = self.text[0][0]
        up1 = self.text[0][1]
        money = players[0].money
        if self.check(upgradeCost[self.item]):
            if up == "D":
                players[0].gun.damage += 5
            elif up == "F":
                players[0].gun.fireRate -= 2
                if players[0].gun.fireRate <= 8:
                    upgradeMaxed[self.item] = True
            elif up == "R" and up1 == "e":
                players[0].gun.reloadSpeed -= 10
                if players[0].gun.reloadSpeed <= 0:
                    players[0].gun.reloadSpeed = 0
                    upgradeMaxed[self.item] = True
            elif up == "M":
                players[0].gun.mag += 3
            elif up == "P":
                players[0].gun.penetration += 1
                if players[0].gun.penetration > 9:
                    upgradeMaxed[self.item] = True
            elif up == "B":
                if players[0].gun.mag > 3:
                    players[0].gun.bps += 1
                    players[0].gun.spread += 0.3*multiplier
                    players[0].gun.reloadSpeed += 10
                    players[0].gun.fireRate += 6
                    upgradeMaxed[gunUpgrades.index("Reload spd")] = False
                    upgradeMaxed[gunUpgrades.index("Fire rate")] = False
                    players[0].gun.mag -= 3
                    players[0].gun.bullet = players[0].gun.mag
                else:
                    players[0].money += upgradeCost[self.item]
            elif up == "E":
                if players[0].gun.mag > 5:
                    players[0].gun.damage += 25
                    players[0].gun.fireRate += 25
                    players[0].gun.reloadSpeed += 50
                    upgradeMaxed[gunUpgrades.index("Reload spd")] = False
                    upgradeMaxed[gunUpgrades.index("Fire rate")] = False
                    players[0].gun.mag -= 5
                    players[0].gun.bullet = players[0].gun.mag
                    players[0].gun.explosions = True
                    gunUpgrades.pop(self.item)
                    gunUpgrades.append("Radius")
                    upgradeCost.pop(self.item)
                    upgradeCost.append(1000)
                    upgradeDescription.pop(self.item)
                    upgradeDescription.append([[1, "+ Explosion radius"]])
                    upgradeMaxed[gunUpgrades.index("Penetration")]
                    players[0].gun.penetration = 0
                    return
                else:
                    players[0].money += upgradeCost[self.item]
            elif up == "R" and up1 == "a":
                players[0].gun.radius -= 0.5
                players[0].gun.startRadius -= 0.5
                if players[0].gun.radius <= 0.5:
                    upgradeMaxed[self.item] = True
        if money > players[0].money:
            if upgradeCost[self.item] < 10000:
                upgradeCost[self.item] += int(upgradeCost[self.item]*0.5)
            else:
                upgradeCost[self.item] += 10000 + randint(-500,500)

    def baseUpgrade(self):
        global baseUpgrades, baseUpgradeCost, baseHP, maxBaseHP, background, screenSize, mineValues
        up = self.text[0][0]
        up1 = self.text[0][1]
        if self.check(baseUpgradeCost[self.item]):
            if up == "R":
                if baseHP == maxBaseHP:
                    players[0].money += baseUpgradeCost[self.item]
                    return
                baseHP += int(maxBaseHP*0.2)
                if baseHP > maxBaseHP:
                    baseHP = maxBaseHP
                if baseUpgradeCost[self.item] < 500:
                    baseUpgradeCost[self.item] += int(baseUpgradeCost[self.item]*0.25)
                if baseUpgradeCost[self.item] > 500:
                    baseUpgradeCost[self.item] = 500
            elif up == "M":
                if up1 == "a":
                    upgrade = int(maxBaseHP*0.5)
                    maxBaseHP += upgrade
                    baseHP += upgrade
                    if baseUpgradeCost[self.item] < 1000:
                        baseUpgradeCost[self.item] = baseUpgradeCost[self.item]*2
                    else:
                        baseUpgradeCost[self.item] += int(baseUpgradeCost[self.item]*0.5)
                    if maxBaseHP > 25000:
                        baseUpgradeMaxed[self.item] = True
                elif up1 == "-":
                    for i in turrets:
                        if i.radius > 1:
                            i.radius -= 0.5
                            i.startRadius -= 0.5
                        i.explosions = True
                        i.bps += 1
                        i.damage += 5
                    if baseUpgradeCost[self.item] < 90000:
                        baseUpgradeCost[self.item] += 10000
                elif up1 == "i":
                    for i in range(3):
                        mines.append(mine(randint(80*multiplier,250*multiplier),randint(0, 150*multiplier)))
                    baseUpgradeCost[self.item] += 20
            elif up == "C":
                background = transform.scale(image.load("./Game/background.png"),screenSize)
            elif up == "B":
                baseUpgradeMaxed[self.item] = True
                mineValues[0] += 25
                mineValues[1] *= 3
                mineValues[2] -= 0.5
                for i in mines:
                    i.damage = mineValues[0]
                    i.radius = mineValues[1]
                    i.explosionRadius = mineValues[2]


class gun:
    #Class for the players' gun
    #[gun name, damage, fire rate, bullets per shot, mag size, penetration, muzzle flash, muzzle size multiplier, price]
    def __init__(self, gun, player):
        global multiplier
        self.image = image.load("./Game/Guns/"+gun[0]+".png")
        self.muzzle = image.load("./Game/Guns/"+str(gun[6])+".png")
        self.rect = self.image.get_rect()
        self.muzzleRect = self.muzzle.get_rect()
        self.baseImage = transform.scale(self.image, (int(self.rect[2]*(multiplier/2)), int(self.rect[3]*(multiplier/2))))
        self.baseMuzzle = transform.scale(self.muzzle, (int(self.muzzleRect[2]*(multiplier/2)), int(self.muzzleRect[3]*(multiplier/2))))
        self.image = self.baseImage
        self.muzzle = self.baseMuzzle
        self.baseMuzzleDelay = 2
        self.muzzleDelay = self.baseMuzzleDelay
        self.rect = self.baseImage.get_rect()
        self.angle = 0
        self.damage = gun[1]
        self.fireRate = gun[2]
        self.bps = gun[3]
        self.mag = gun[4]
        self.bullet = self.mag
        self.penetration = gun[5]
        self.muzzleSize = gun[7]
        self.price = gun[8]
        self.spread = gun[9]*multiplier
        self.update(player)
        self.lastRun = 0
        self.reloading = 0
        self.reloadSpeed = 60
        self.explosions = False
        self.radius = 1.5
        self.startRadius = 5

    def shoot(self, pos):
        if self.lastRun + self.fireRate < tick:
            if self.bullet != 0:
                if self.angle == -360:
                    self.angle = 0
                self.muzzleDelay = self.baseMuzzleDelay
                self.muzzle = transform.rotate(self.baseMuzzle, -self.angle-180)
                self.muzzleRect = self.muzzle.get_rect()
                if self.angle == 0:
                    angle = 0.0001
                else:
                    angle = self.angle
                self.muzzleRect[0] = self.rect[0] - self.rect[2] / 2 + self.muzzleRect[2] * (angle / 90) * 0.5# - [2]
                self.muzzleRect[1] = self.rect[1] - self.muzzleRect[3] * 0.75 + self.muzzleRect[3] * (abs(angle) / 90) * 0.5
                if pos == None:
                    for i in range(self.bps):
                        bullets.append(bullet(self.damage, self.penetration, (self.rect[0] + self.rect[2]/2, self.rect[1]-self.rect[3]/2), None, self.spread))
                        if self.explosions:
                            bullets[len(bullets)-1].changeImage(1)
                            bullets[len(bullets)-1].radius = self.radius
                            bullets[len(bullets)-1].currentRadius = self.startRadius
                else:
                    for i in range(self.bps):
                        bullets.append(bullet(self.damage, self.penetration, (self.rect[0] + self.rect[2]/2, self.rect[1]-self.rect[3]/2 + (abs(self.angle)/90)*(self.rect[3])), pos, self.spread))
                        if self.explosions:
                            bullets[len(bullets)-1].changeImage(1)
                            bullets[len(bullets)-1].radius = self.radius
                            bullets[len(bullets)-1].currentRadius = self.startRadius
                self.lastRun = tick
                self.bullet -= 1
                if self.explosions:
                    rpgFX.play()
                else:
                    gunFX.play()

    def update(self, player):
        self.rect[0] = player.x + player.rect[0][2] * 0.5
        self.rect[1] = player.y + player.rect[0][3] * 0.1
        if self.angle != -360:
            self.rect[0] += (self.angle/90)*(self.rect[2]/3)
            self.rect[1] += (abs(self.angle)/90)*(self.rect[3]/2)

    def updateAngle(self, target):
        if target == None:
            self.target = None
            self.angle = -360
        else:
            self.diffX = target[0] - self.rect[0]
            self.diffY = self.rect[1] - target[1]
            if self.diffY > 50 and self.diffX != 0:
                self.angle = 90 - degrees(atan(self.diffY/abs(self.diffX)))
            else:
                self.angle = -360
            if self.diffX < 0 and self.angle != -360:
                self.angle = -self.angle
            if self.angle != -360:
                self.image = transform.rotate(self.baseImage, -self.angle)
                self.rect = self.image.get_rect()
            else:
                self.image = self.baseImage
        self.update(players[0])


class blood:
    def __init__(self, startCoords, height):
        self.image = Surface.convert(bloodDot)
        self.image.fill([randint(100,150),0,0])
        self.image.set_alpha(randint(100,200))
        self.X = startCoords[0]
        self.Y = startCoords[1]
        self.speedX = uniform(-1.5*multiplier,1.5*multiplier)
        self.speedY = uniform(-3*multiplier,0)
        self.accelY = 0.2*multiplier
        self.height = 0
        self.maxHeight = height


class gore:
    def __init__(self, startCoords, height):
        self.image = transform.rotate(Surface.convert_alpha(meatChunks[randint(0,(len(meatChunks)-1))]), randint(0,359))
        self.X = startCoords[0]
        self.Y = startCoords[1]
        self.speedX = uniform(-1*multiplier,1*multiplier)
        self.speedY = uniform(-2*multiplier,0)
        self.accelY = 0.2*multiplier
        self.height = 0
        self.maxHeight = height


class bullet:
    #Class for all bullets
    def __init__(self, damage, penetration, startCoords, target, spread):
        self.rect = projectileRect[0]
        self.currentImage = None
        self.damage = damage
        self.penetration = penetration
        self.penetrated = []
        self.radius = 0
        self.endTick = 0
        self.currentRadius = 5
        self.speedY = 15*multiplier
        self.speedX = uniform(-spread, spread)
        self.x,self.y = startCoords[0],startCoords[1]
        if target == None:
            self.x -= self.rect[2]
            self.target = None
            self.angle = -360
        else:
            self.target = []
            self.target.append(target[0] - self.rect[2]/2)
            self.target.append(target[1])
            self.diffX = self.target[0] - self.x
            self.diffY = self.y - self.target[1]
            if self.diffY > 0 and self.diffX != 0:
                self.angle = 90 - degrees(atan(self.diffY/abs(self.diffX)))
            else:
                self.angle = -360
            if self.diffX < 0 and self.angle != -360:
                self.angle = -self.angle
            if self.angle < 10:
                self.x -= self.rect[3]/2
        if self.angle != -360:
            old = [self.speedX,self.speedY]
            multi = [self.angle/90,(90 - abs(self.angle))/90]
            self.speedX = old[1] * multi[0] + old[0] * multi[0]
            self.speedY = old[1] * multi[1] + abs(old[0] * multi[1])
            self.speedX += (uniform(-spread,spread)*(1-multi[0]))/5
        self.changeImage(0)
        
    def changeImage(self, imgNo):
        self.image = projectileImages[imgNo].copy()
        self.image = transform.rotate(self.image, -self.angle)
        self.rect = projectileRect[imgNo]
        self.mask = projectileMask[imgNo]

    def update(self):
        self.rect[0] = self.x
        self.rect[1] = self.y


class turret:
    def __init__(self, pos):
        global startX, endX, endY, multiplier
        self.pos = pos
        img = image.load("./Game/Guns/Turret.png")
        rect = img.get_rect()
        self.angle = degrees(atan(endY/(startX[pos]-endX[pos])))
        if self.angle > 0:
            self.angle = -(90 - self.angle)
        else:
            self.angle = 90 + self.angle
        self.image = transform.scale(img, (int(rect[2]*multiplier),int(rect[3]*multiplier)))
        self.rect = self.image.get_rect()
        muzzle = image.load("./Game/Guns/2.png")
        rect = muzzle.get_rect()
        self.muzzle = transform.rotate(transform.scale(muzzle, (int(rect[2]*(multiplier/2)), int(rect[3]*(multiplier/2)))), self.angle)
        self.muzzleRect = self.muzzle.get_rect()
        self.x = endX[pos]-self.rect[2]/2
        self.y = endY-self.rect[3]
        self.firing = 0
        self.fireRate = 40
        self.damage = 5
        self.lastShot = 0
        self.baseMuzzleDelay = 2
        self.muzzleDelay = 0
        self.bps = 1
        self.explosions = False
        self.radius = 2
        self.startRadius = 5

    def shoot(self):
        global startX, endX
        if self.explosions:
            rpgFX.play()
        else:
            turretFX.play()
        for i in range(self.bps):
            bullets.append(bullet(self.damage, 0, (endX[self.pos],self.y), (startX[self.pos],0), 1))
            if self.explosions:
                bullets[len(bullets)-1].changeImage(1)
                bullets[len(bullets)-1].radius = self.radius
                bullets[len(bullets)-1].currentRadius = self.startRadius
        self.muzzleDelay = self.baseMuzzleDelay


class mine:
    def __init__(self, x, y):
        global mineValues #[damage, detection radius, explosion size]
        self.image = projectileImages[3]
        self.damage = mineValues[0]
        self.rect = self.image.get_rect()
        self.rect[0] = x
        self.rect[1] = y
        self.radius = mineValues[1]
        self.explosionRadius = mineValues[2]
        self.x = x
        self.y = y
        self.currentRadius = 3
        self.endTick = 0


class printText:
    def __init__(self, text, textSize, textColor, textLocation):
        termFont = font.Font(None,int(textSize*multiplier))
        self.image = termFont.render(text, False, textColor)
        self.x,self.y = textLocation[0]*multiplier,textLocation[1]*multiplier


def openShop():
    #Brings up the shop overlay
    global menu, shopMusic, oldMusic, seekTrack, seekPos
    if shopMusic == 0:
        if seekTrack != oldMusic:
            seekTrack = oldMusic
            seekPos = mixer.music.get_pos()
        else:
            seekPos += mixer.music.get_pos()
        mixer.music.fadeout(600)
        shopMusic = 1
    elif shopMusic == 1 and mixer.music.get_busy() == False:
        shopMusic = 2
        mixer.music.load("./Game/Sounds/shop.ogg")
        mixer.music.set_volume(0)
        mixer.music.play(-1)
    elif shopMusic == 2:
        currentVol = mixer.music.get_volume()
        if currentVol < 1:
            mixer.music.set_volume(currentVol + 0.05)
        else:
            shopMusic = 3 
    if overlayBlack.get_alpha() != 200:
        overlayBlack.set_alpha(overlayBlack.get_alpha()+20)
        screen.blit(overlayBlack, (0,0))
    else:
        drawButtons()
        for i in shopTexts:
            screen.blit(i.image, (i.x, i.y))
    menu = "shop"


def closeShop():
    #Closes the shop overlay
    global menu, shopMusic, shopTick
    mixer.music.fadeout(600)
    while overlayBlack.get_alpha() != 0:
        overlayBlack.set_alpha(overlayBlack.get_alpha()-10)
        drawGame()
        screen.blit(overlayBlack, (0,0))
        display.flip()
        time.wait(20)
    averageFps = []
    shopTick = tick
    menu = "none"

    
def makeShop():
    #Generates the shop buttons
    global shop,shopTexts
    shop = []
    shopTexts = []
    shop.append(button([(26,13),(24,11)], [(0,0,0),(153,101,21)], (160-26/2, 180-5-13), -1, ["BACK"], [10], [(255,215,0)],  [("mid", 13)]))
    shop[0].onClick = closeShop
    for i in range(7): #Turret buttons (2 top rows)
        exists = -1
        for j in range(len(turrets)):
            if turrets[j].pos == i:
                exists = j
                break
        if exists == -1:
            shop.append(button([(40,20),(37,17)], [(0,0,0),(139,69,19)], ((5+i*40+i*5), 5), turretPrice, ["Turret "+str(i+1)], [9, 8], [(0,150,0),(255,215,0)],  [("mid",8),("mid",44)]))
            shop[len(shop)-1].item = i
            shop[len(shop)-1].onClick = shop[len(shop)-1].makeTurret
        else:
            if turrets[exists].fireRate > 10:
                shop.append(button([(40,20),(37,17)], [(0,0,0),(139,69,19)], ((5+i*40+i*5), 30), turretUpgrades[i][1], ["Fire rate "+str(i+1)], [9, 8], [(0,150,0),(255,215,0)],  [("mid",8),("mid",44)]))
                shop[len(shop)-1].item = i
                shop[len(shop)-1].onClick = shop[len(shop)-1].turretUpgrade
            shop.append(button([(40,20),(37,17)], [(0,0,0),(139,69,19)], ((5+i*40+i*5), 5), turretUpgrades[i][0], ["Damage "+str(i+1)], [9, 8], [(0,150,0),(255,215,0)],  [("mid",8),("mid",44)]))
            shop[len(shop)-1].item = i
            shop[len(shop)-1].onClick = shop[len(shop)-1].turretUpgrade
    upgradeX = 5
    upgradeY = 55
    for i in range(len(gunUpgrades)): #Gun upgrade buttons (middle row)
        if upgradeMaxed[i]:
            upgradeX += 40 + 5
            continue
        shop.append(button([(40,20),(37,17)], [(0,0,0),(139,69,19)], (upgradeX, upgradeY), upgradeCost[i], [gunUpgrades[i]], [9, 8], [(150,0,0),(255,215,0)],  [("mid",8),("mid",44)]))
        shop[len(shop)-1].item = i
        shop[len(shop)-1].onClick = shop[len(shop)-1].gunUpgrade
        for j in range(len(upgradeDescription[i])):
            if upgradeDescription[i][j][0] == 0:
                color = (255,0,0)
            else:
                color = (20,200,20)
            shopTexts.append(printText(upgradeDescription[i][j][1], 6, color, (upgradeX, upgradeY + 20 + j*3.5)))
        upgradeX += 40 + 5
    upgradeX = 5
    upgradeY = 95
    if len(mines) > 2:
        baseUpgradeMaxed[baseUpgrades.index("Mines")] = True
    else:
        baseUpgradeMaxed[baseUpgrades.index("Mines")] = False
    for i in range(len(baseUpgrades)): #Base upgrade buttons (Bottom row)
        if baseUpgradeMaxed[i]:
            upgradeX += 40 + 5
            continue
        shop.append(button([(40,20),(37,17)], [(0,0,0),(139,69,19)], (upgradeX, upgradeY), baseUpgradeCost[i], [baseUpgrades[i]], [9, 8], [(0,0,150),(255,215,0)],  [("mid",8),("mid",44)]))
        shop[len(shop)-1].item = i
        shop[len(shop)-1].onClick = shop[len(shop)-1].baseUpgrade
        for j in range(len(baseUpgradeDescription[i])):
            if baseUpgradeDescription[i][j][0] == 0:
                color = (255,0,0)
            else:
                color = (20,200,20)
            shopTexts.append(printText(baseUpgradeDescription[i][j][1], 6, color, (upgradeX, upgradeY + 20 + j*3.5)))
        upgradeX += 40 + 5
            
    shopTexts.append(printText("$ "+str(players[0].money), 16, (0,255,0), (265, 163)))
    shopTexts.append(printText("Base HP: ", 12, (0,80,0), (1, 165)))
    shopTexts.append(printText(str(baseHP)+"/"+str(maxBaseHP), 12, (255-255*(baseHP/maxBaseHP),255*(baseHP/maxBaseHP),0), (38, 165)))


def getEvents():
    #Finds whether any of the player control keys/buttons have been pressed (or unpressed)
    global menu, lastCheat, tick, cheats
    for i in event.get():
        if i.type == KEYDOWN:
            for player in players:
                for k in range(len(player.keys)):
                    if i.key == player.keys[k]:
                        if player.pressed[k] == 0:
                                player.pressed[k] = 1
            if i.key == 114 or i.key == 273:
                players[0].gun.bullet = 0
                player.gun.reloading = 1
                if reloadFX.get_num_channels() == 0:
                    reloadFX.play()
            if i.key == 27:
                if menu == "none":
                    menu = "shop"
                elif menu == "shop":
                    closeShop()
            if i.key == 109 or i.key == 111 or i.key == 110 or i.key == 101 or i.key == 121:
                if lastCheat < tick - 20:
                    cheats = cheats+i.unicode
                    if cheats.count("moneymoneymoney") != 0:
                        players[0].money += 999999
                        cheats = "moneymoney"
                else:
                    cheats = ""+i.unicode
                    lastCheat = tick
        elif i.type == KEYUP:
            for player in players:
                for k in range(len(player.keys)):
                    if i.key == player.keys[k]:
                        if player.pressed[k] != 0:
                                player.pressed[k] = 0
        elif i.type == MOUSEBUTTONDOWN:
            checkClick(i.pos, i.button)
        elif i.type == MOUSEBUTTONUP:
            uncheckClick(i.pos, i.button)
        elif i.type == MOUSEMOTION:
            if players[0].pressed[2] == 2:
                checkClick(i.pos, 99)
            players[0].gun.updateAngle(i.pos)
        elif i.type == 102 and shopMusic == 0:
            checkMusic()
        elif i.type == QUIT:
            quit()


def uncheckClick(pos, button):
    if button == 1:
        if menu == "none":
            players[0].pressed[2] = 0


def checkClick(pos, button):
    #Checks whether a button has been clicked
    if button == 1:
        if menu == "main":
            None
        elif menu == "shop":
            for i in shop:
                if i.rect.collidepoint(pos):
                    i.onClick()
        elif menu == "none":
            for i in buttons:
                if i.rect.collidepoint(pos):
                    i.onClick()
                else:
                    players[0].pressed[2] = 2
                    players[0].pressed[3] = pos
    elif button == 99:
        players[0].pressed[3] = pos
    """elif button == 2:
        None
        if menu == "shop":
            for i in shop:
                if i.rect.collidepoint(pos):
                    i.info()"""
            


def pathCoords():
    #Multiplies zombie start and end coordinates with the pixel multiplier
    global startX,endX,endY,multiplier
    startx = [100, 122, 143, 163, 177, 193, 213]
    endx = [62, 98, 128, 158, 186, 218, 255]
    endY = 153 * multiplier
    for i in startx:
        startX.append(i * multiplier)
    for i in endx:
        endX.append(i * multiplier)


def fileCache():
    #Loads all zombie images into memory
    global zombieImages, projectileImages, meatChunks
    dirCount = 0
    dir1 = []
    projectile = 0
    meat = 0
    for i in os.listdir("./Game/Music/"):
        music.append(i)
    for i in os.listdir("./Game/Gore/"):
        img = image.load("./Game/Gore/"+i)
        rect = img.get_rect()
        meatChunks.append(transform.scale(img, (int(rect[2]*multiplier),int(rect[3]*multiplier))))
        meat += 1
    for i in os.listdir("./Game/Projectiles/"):
        img = image.load("./Game/Projectiles/"+i)
        rect = img.get_rect()
        projectileImages.append(transform.scale(img, (int(rect[2]*multiplier),int(rect[3]*multiplier))))
        projectileRect.append(projectileImages[projectile].get_rect())
        projectileMask.append(mask.from_surface(projectileImages[projectile]))
        projectile += 1
    for i in os.listdir("./Game/Zombies/"):
        if os.path.isdir("./Game/Zombies/"+i):
            zombieImages.append([])
            zombieRect.append([])
            for j in os.listdir("./Game/Zombies/"+i+"/"):
                if os.path.isdir("./Game/Zombies/"+i+"/"+j):
                    zombieImages[len(zombieImages)-1].append([])
                    zombieRect[len(zombieRect)-1].append([])
                    for k in os.listdir("./Game/Zombies/"+i+"/"+j+"/"):
                        if os.path.isfile("./Game/Zombies/"+i+"/"+j+"/"+k):
                            img = image.load("./Game/Zombies/"+(str(i))+"/"+(str(j)+"/"+(str(k))))
                            rect = img.get_rect()
                            baseLen = len(zombieImages)-1
                            zombieImages[baseLen][len(zombieImages[baseLen])-1].append(transform.scale(img, (int(rect[2]*multiplier),int(rect[3]*multiplier))))
                            zombieRect[baseLen][len(zombieRect[baseLen])-1].append(zombieImages[baseLen] [int(j)][len(zombieImages[baseLen][int(j)])-1].get_rect())


def checkBlood():
    #Check whether the base has been damaged
    global damaged
    if damaged == 2:
        overlayRed.set_alpha(100)
        screen.blit(overlayRed, (0,0))
        damaged = 1
    elif damaged == 1:
        overlayRed.set_alpha(overlayRed.get_alpha()-10)
        screen.blit(overlayRed, (0,0))
    if overlayRed.get_alpha() == 0:
        damaged = 0


def playerMove(i, direction):
    #Moves the player
    i.animFrame[0] = direction
    if i.anim[i.animFrame[0]][i.animFrame[1]][2] + i.lastRun < tick:
        if i.animFrame[1] < len(i.anim[i.animFrame[0]])-1:
            i.animFrame[1] += 1
        else:
            i.animFrame[1] = 0
        i.currentImage = i.anim[i.animFrame[0]][i.animFrame[1]][0]
        if direction == 2:
            i.x += i.speed*i.anim[i.animFrame[0]][i.animFrame[1]][1]
        else:
            i.x -= i.speed*i.anim[i.animFrame[0]][i.animFrame[1]][1]
        i.lastRun = tick


def playerActions():
    #Calculates player actions
    for player in players:
        if player.pressed[0] == 1:
            playerMove(player, 1)
        if player.pressed[1] == 1:
            playerMove(player, 2)
        if player.pressed[0] == 0 and player.pressed[1] == 0:
            player.animFrame = [0,0]
            player.currentImage = 0
        if player.pressed[2] == 2:
            player.gun.updateAngle(player.pressed[3])
            if player.gun.bullet == 0:
                player.gun.reloading = 1
                if reloadFX.get_num_channels() == 0:
                    reloadFX.play()
            player.gun.shoot(player.pressed[3])
        elif player.pressed[2] == 1:
            player.gun.updateAngle((player.gun.rect[0] + player.gun.rect[2]/2, player.gun.rect[1]-100))
            if player.gun.bullet == 0:
                player.gun.reloading = 1
                if reloadFX.get_num_channels() == 0:
                    reloadFX.play()
            player.gun.shoot(None)
        if player.gun.bullet == 0:
            if player.gun.reloading == 0:
                player.gun.lastRun = tick
            else:
                if player.gun.lastRun + player.gun.reloadSpeed < tick:
                    player.gun.bullet = player.gun.mag
                    player.gun.reloading = 0
                    reloadStop.play()
        player.gun.update(player)


def actions():
    #Calculates all zombie (and blood) movement and damage
    global baseHP, damaged, tick
    for i in mines:
        for j in zombies:
            testSprite.rect = j.rect[0]
            if sprite.collide_circle(i,testSprite):
                i.radius = i.explosionRadius
                i.image = Surface.convert_alpha(projectileImages[2])
                i.rect = i.image.get_rect()
                i.currentImage = transform.scale(i.image, (int(i.rect[2]/i.currentRadius),int(i.rect[3]/i.currentRadius)))
                i.newRect = i.currentImage.get_rect()
                explosions.append(i)
                mines.pop(mines.index(i))
                explosionFX.play()
    for i in explosions:
        if i.currentRadius > i.radius:
            i.currentRadius -= 0.5
            i.currentImage = transform.scale(i.image, (int(i.rect[2]/i.currentRadius),int(i.rect[3]/i.currentRadius)))
            rect = i.currentImage.get_rect()
            i.x -= (rect[2]-i.newRect[2])/2
            i.y -= (rect[3]-i.newRect[3])/2
            i.newRect = rect
        else:
            i.currentImage.fill((255,255,255,240), None, BLEND_RGBA_MULT)
            if i.endTick == 0:
                i.endTick = tick
                i.rect = i.currentImage.get_rect()
                i.rect[0] = i.x
                i.rect[1] = i.y
                i.mask = mask.from_surface(i.currentImage)
                for j in zombies:
                    j.rect[0][0] = j.x
                    j.rect[0][1] = j.y
                    testSprite.mask = j.mask
                    testSprite.rect = j.rect[0]
                    if sprite.collide_mask(testSprite, i):
                        point = sprite.collide_mask(testSprite, i)
                        j.health -= i.damage
                        for k in range(randint(40,80)):
                            if len(j.blood) > 100:
                                break
                            j.blood.append(blood((point[0]+j.rect[0][0], point[1]+j.rect[0][1]), j.rect[0][3] - point[1] + randint(int(-10*multiplier),int(10*multiplier))))
            elif i.endTick + 50 < tick:
                explosions.pop(explosions.index(i))
    for i in turrets:
        if i.firing != 0:
            if i.lastShot + i.fireRate <= tick:
                i.firing = 0
    for i in zombies:
        if i.health > 0:
            for j in turrets:
                if j.firing == 0 and j.pos == i.startLoc and i.y > 50:
                    j.shoot()
                    j.firing = 2
                    j.lastShot = tick
            if i.y < endY-i.rect[0][3]:
                if i.anim[i.animFrame][2] + i.lastRun < tick:
                    if i.animFrame < len(i.anim)-1:
                        i.animFrame += 1
                    else:
                        i.animFrame = 0
                    i.currentImage = i.anim[i.animFrame][0]
                    i.y += i.speed*i.anim[i.animFrame][1]
                    if i.y > endY-i.rect[0][3]:
                        i.y = endY-i.rect[0][3]+randint(1,5*multiplier)
                    i.lastRun = tick
                    if i.x < i.xStart + (i.xEnd-i.xStart)*((i.y+i.rect[0][3])/endY):
                        i.x += 5
                    if i.x > i.xStart + (i.xEnd-i.xStart)*((i.y+i.rect[0][3])/endY):
                        i.x -= 5
            else:
                if i.lastRun + i.attackSpd < tick:
                    baseHP = int(baseHP - i.damage)
                    damaged = 2
                    i.lastRun = tick
        elif not i.dead:
            players[0].money += i.money
            i.dead = True
            players[0].killed += 1
            #deathFX.play()
            for _ in range(4,randint(5,10)):
                i.rect[0][0] = i.x
                i.rect[0][1] = i.y
                heightMulti = uniform(0,1)
                i.blood.append(gore((i.rect[0][0]+i.rect[0][2]*uniform(0,1)-15*multiplier,i.rect[0][1]+i.rect[0][3]*heightMulti-15*multiplier), i.rect[0][3]*heightMulti + randint(int(-5*multiplier),int(2*multiplier))))
            for _ in range(randint(50,70)):
                if len(i.blood) > 100:
                    break
                heightMulti = uniform(0,1)
                i.blood.append(blood((i.rect[0][0]+i.rect[0][2]*uniform(0,1),i.rect[0][1]+i.rect[0][3]*heightMulti), i.rect[0][3]*heightMulti + randint(int(-10*multiplier),int(10*multiplier))))
    for i in bullets:
        if int(tick) == tick:
            i.y -= i.speedY
            i.x += i.speedX
        i.update()
        if int(tick) == tick:
            if i.y < -100 or i.x < -100 or i.x > screenSize[1]*multiplier+100:
                bullets.pop(bullets.index(i))
    for j in zombies:
        if j.blood != [] and int(tick) == tick:
            for i in j.blood:
                i.speedY += i.accelY
                i.Y += i.speedY
                i.X += i.speedX
                i.height += i.speedY
                if i.height > i.maxHeight:
                    bloods.append(i)
                    j.blood.pop(j.blood.index(i))
        if j.dead and j.blood == []:
            zombies.pop(zombies.index(j))
            continue
        if not j.dead:
            j.rect[0][0] = j.x
            j.rect[0][1] = j.y
            testSprite.mask = j.mask
            testSprite.rect = j.rect[0]
            for i in bullets: #Bullet collision detection
                if i.penetrated.count(j) == 0:
                    if sprite.collide_mask(testSprite, i):
                        point = sprite.collide_mask(testSprite, i)
                        if point[1] < j.rect[0][3]*0.8:
                            if i.radius != 0:
                                i.image = Surface.convert_alpha(projectileImages[2])
                                i.rect = i.image.get_rect()
                                i.currentImage = transform.scale(i.image, (int(i.rect[2]/i.currentRadius),int(i.rect[3]/i.currentRadius)))
                                i.newRect = i.currentImage.get_rect()
                                explosions.append(i)
                                bullets.pop(bullets.index(i))
                                explosionFX.play()
                                continue
                            j.health -= i.damage
                            i.penetration -= 1
                            i.penetrated.append(j)
                            i.speedY = i.speedY * 0.65
                            if i.penetration < 0:
                                bullets.pop(bullets.index(i))
                                if len(j.blood) < 100:
                                    for k in range(randint(5,15)):
                                        j.blood.append(blood((point[0]+j.rect[0][0], point[1]+j.rect[0][1]), j.rect[0][3] - point[1] + randint(int(-10*multiplier),int(10*multiplier))))


def drawButtons():
    #Draws the correct buttons onto the screen
    if menu == "shop":
        screen.blit(overlayBlack, (0,0))
        for i in shop:
            screen.blit(i.image, i.location)
    elif menu == "main":
        None
    elif menu == "none":
        for i in buttons:
            screen.blit(i.image, i.location)


def drawGame():
    #Draws all zombies, bullets and players onto the screen
    screen.blit(background, (0,0))
    for i in mines:
        screen.blit(i.image, (int(i.x), int(i.y)))
    for bullet in bullets:
        screen.blit(bullet.image, (int(bullet.x), int(bullet.y)))
    zombies.sort(key=lambda x: (x.y+x.rect[0][3]))
    for i in zombies:
        if not i.dead:
            screen.blit(i.image[i.currentImage], (int(i.x), int(i.y)))
        if i.blood != []:
            for drop in i.blood:
                screen.blit(drop.image, (int(drop.X),int(drop.Y)))
    for i in explosions:
        screen.blit(i.currentImage, (int(i.x),int(i.y)))
    for turret in turrets:
        screen.blit(turret.image, (turret.x,turret.y))
        if turret.muzzleDelay > 0:
            screen.blit(turret.muzzle, (int(turret.x+turret.rect[2]/2-turret.muzzleRect[2]/2-((turret.angle/90)*turret.muzzleRect[2])),int(turret.y-turret.muzzleRect[3])))
            turret.muzzleDelay -= 1
    screen.blit(fence, (38*multiplier,123*multiplier))
    for player in players:
        screen.blit(player.gun.image, (int(player.gun.rect[0]), int(player.gun.rect[1])))
        if player.gun.muzzleDelay > 0:
            screen.blit(player.gun.muzzle, (int(player.gun.muzzleRect[0]), int(player.gun.muzzleRect[1])))
            player.gun.muzzleDelay -= 1
        screen.blit(player.image[player.currentImage], (int(player.x), int(player.y)))
    for i in texts:
        screen.blit(i.image, (i.x, i.y))


def spawn():
    #Spawns new zombies according to current wave
    global wave,waveMulti,zombieSpawn,lastSpawn
    delay = 100/(2*waveMulti-1)
    if lastSpawn + delay < tick:
        if zombieSpawn > 0:
            lastSpawn = tick + randint(-5,5)
            randomZombie = randint(1,100)
            if randomZombie > 91-waveMulti and wave >= 5:
                zombies.append(zomFast())
            elif randomZombie > 84-2*waveMulti and wave >= 10:
                zombies.append(zomFat())
            else:
                zombies.append(zomBasic())
            zombieSpawn -= 1
        elif len(zombies) == 0:
            wave += 1
            waveMulti += 0.125
            zombieSpawn = 10 * (0.5+waveMulti/2)


def bloodSplat():
    global background
    for i in bloods:
        background.blit(i.image, (i.X,i.Y))
        bloods.pop(bloods.index(i))
    background = Surface.convert(background)
        

def makeText():
    global texts, baseHP,maxBaseHP
    texts = []
    texts.append(printText("Wave "+str(wave), 12, (0,0,0), (285, 1)))
    texts.append(printText("$ "+str(players[0].money), 10, (0,255,0), (285, 10)))
    texts.append(printText(str(players[0].gun.bullet)+"/"+str(players[0].gun.mag), 12, (100,20,0), (280, 165)))
    texts.append(printText("Base HP: ", 12, (0,80,0), (1, 165)))
    if baseHP <= 0:
        baseHP = 0
        texts.append(printText("GAME OVER", 20, (255,0,0), (120, 80)))
        texts.append(printText("Zombies killed: "+str(players[0].killed), 18, (255,0,0), (100, 100)))
        print("Game over")
    texts.append(printText(str(baseHP)+"/"+str(maxBaseHP), 12, (255-255*(baseHP/maxBaseHP),255*(baseHP/maxBaseHP),0), (38, 165)))


def checkMusic():
    global music, oldMusic
    newMusic = randint(0,len(music)-1)
    while newMusic == oldMusic:
        newMusic = randint(0,len(music)-1)
    mixer.music.load("./Game/Music/"+music[newMusic])
    mixer.music.play()
    mixer.music.set_endevent(102)
    oldMusic = newMusic


def checkShopMusic():
    global shopMusic, seekPos, sleep
    if shopMusic != 0 and shopMusic != 4:
        if mixer.music.get_busy() == False and sleep > 20:
            mixer.music.stop()
            mixer.music.load("./Game/Music/"+music[oldMusic])
            mixer.music.set_volume(0)
            mixer.music.play(start=(seekPos/1000))
            mixer.music.set_endevent(102)
            shopMusic = 4
        else:
            sleep += 1
    elif shopMusic == 4:
        currentVol = mixer.music.get_volume()
        if currentVol < 1:
            mixer.music.set_volume(currentVol + 0.05)
        else:
            shopMusic = 0



buttons.append(button([(34,13),(32,11)], [(0,0,0),(153,101,21)], (1, 1), -1, ["SHOP"], [14], [(255,215,0)],  [("mid",8)]))
buttons[0].onClick = openShop
pathCoords()
fileCache()
players.append(player(playerAmount))
playerAmount += 1
players[0].gun = gun(guns[0], players[0])
oldMusic = randint(0,len(music)-1)
mixer.music.load("./Game/Music/"+music[oldMusic])
mixer.music.play()
mixer.music.set_endevent(102)
mainClock = time.Clock()
tickRate = 30/targetFps


#Main loop
while 1:
    if menu == "main":
        None
    elif menu == "shop":
        drawGame()
        makeShop()
        openShop()
    elif menu == "none":
        checkShopMusic()
        makeText()
        spawn()
        actions()
        playerActions()
        bloodSplat()
        drawGame()
        drawButtons()
        checkBlood()
        tick += 1*tickRate
        #Lowers FPS if performance is bad
        if tick % 5 == 0 and shopTick + 50 < tick:
            averageFps.append(mainClock.get_fps())
        if len(averageFps) == 10:
            avg = sum(averageFps)/len(averageFps)
            print("Average FPS:",avg)
            if avg < 50 and dynamicFps == True and targetFps > 30:
                print("Average FPS is low, locking to 30FPS!")
                targetFps = 30
                tickRate = 30/targetFps
            averageFps = []
    display.flip()
    mainClock.tick(targetFps)
    getEvents()
    if baseHP <= 0 and endGame >= 2:
        break
    elif baseHP <= 0:
        endGame += 1

while 1:
    getEvents()
    time.wait(100)
