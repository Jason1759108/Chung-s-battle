import sys
import pygame
from pygame.locals import QUIT
from random import randint
from math import sin , cos , radians

pygame.init()  # 初始化 Pygame

#設定基本資訊
w, h = 1800, 900
FPS = 120
fpsClock = pygame.time.Clock()
window = pygame.display.set_mode((w, h))
pygame.display.set_caption("彈幕對戰")

#製作三張圖層
bg = pygame.Surface(window.get_size(),pygame.SRCALPHA) #背景
bg = bg.convert()
bg.fill((0, 0, 0))
game_surface = pygame.Surface(window.get_size(),pygame.SRCALPHA) #遊戲區塊
game_surface.fill((0,0,0,0))
information = pygame.Surface(window.get_size(),pygame.SRCALPHA) #資訊區塊
information.fill((0,0,0,0))
menu_surface = pygame.Surface(window.get_size(),pygame.SRCALPHA)
window.blit(bg, (0, 0))
window.blit(game_surface, (0, 0))
window.blit(information, (0, 0))
pygame.display.update()

#匯入需要的全域圖片
heart_image = pygame.image.load("picture/heart.png")
mainMenuBg = pygame.image.load("picture/main_bg.jpg").convert()
mainMenuBg = pygame.transform.scale(mainMenuBg,(w,h))

#載入需要的音效
confirmSound = pygame.mixer.Sound("voice/你要確認欸.wav")
injurySound = pygame.mixer.Sound("Voice/咳嗽.wav")

#所有會顯現的東西
class item(pygame.sprite.Sprite):
    isFlip = 0
    image = None
    rect = None
    surface = None
    def __init__(self,isFlip : bool ,image_path : str ,surface : pygame.Surface , pos : tuple):
        super().__init__()
        self.isFlip = isFlip
        self.image = pygame.image.load(image_path)
        self.image = pygame.transform.flip(self.image , isFlip,0)
        self.rect = self.image.get_rect()
        self.rect.center = pos
        self.surface = surface
        return
    def draw(self):
        self.surface.blit(self.image,self.rect)
        return
class Bullet(item):
    def __init__(self ,isFlip : bool, image_path : str , pos : tuple, dHP : int):
        super().__init__(isFlip,image_path,game_surface,pos)
        self.dHP = dHP
    def detect(self):
        if pygame.sprite.collide_rect(self,P1 if self.isFlip else P2):
            (P1 if self.isFlip else P2).HP -= self.dHP
            self.rect.x = -1 if self.isFlip else w+1
            injurySound.play()

        for s in P1.shields if self.isFlip else P2.shields:
            if pygame.sprite.collide_rect(self,s):
                   self.rect.x = -1 if self.isFlip else w+1
            
#直線子彈
class Bullet1(Bullet):
    waitTime = 60
    def __init__(self, pos , isFlip):
        super().__init__(isFlip,"picture/bullet.png",pos,1)

    def move(self):
        self.rect.x += -20 if self.isFlip else 20
        self.detect()     
#散彈
class Bullet2(Bullet):
    waitTime = 120
    dx , dy = 0 , 0
    x , y = 0 , 0
    def __init__(self, pos , isFlip):
        super().__init__(isFlip,"picture/bullet2.png",pos,1)
        theta = radians(randint(-20,20))
        self.dx , self.dy = 3*(-1 if isFlip else 1)*cos(theta) , 3*sin(theta)
        self.x , self.y = self.rect.x , self.rect.y
    def move(self):
        self.x += self.dx
        self.y += self.dy
        self.rect.x = self.x
        self.rect.y = self.y
        self.detect()     

class Bullet3(Bullet):
    waitTime = 120
    def __init__(self, pos , isFlip):
        super().__init__(isFlip,"picture/bullet3.png",pos,2)

    def move(self):
        self.rect.x += -10 if self.isFlip else 10
        self.detect()     

class Bullet4(Bullet):
    waitTime = 120
    def __init__(self, pos , isFlip):
        super().__init__(isFlip,"picture/bullet4.png",pos,1)

    def move(self):
        self.rect.x += -35 if self.isFlip else 35
        self.detect()

class Shield(item):
    waitTime = 480
    def __init__(self,pos,isFlip):
        super().__init__(isFlip,"picture/shield.png",game_surface,pos)

class Button(pygame.sprite.Sprite):
    text_color = (0,0,0)
    bg_color = (255,255,255)
    click_color = (50,50,255)
    font = pygame.font.SysFont("Arial",35)
    def __init__(self,text : str,surface : pygame.Surface , pos):
        super().__init__()
        self.text = self.font.render(text,True,self.text_color)
        self.rect = self.text.get_rect()
        self.rect.center = pos
        self.surface = surface
        self.clicked = False
        return
    def set_text(self,text : str):
        self.text = self.font.render(text,True,self.text_color)
        self.rect = self.text.get_rect()
        return
    def set_font(self,font : str , size : int):
        self.font = pygame.font.SysFont(font,size)
        return
    def draw(self):
        pygame.draw.rect(self.surface,self.click_color if self.clicked else self.bg_color,self.rect)
        self.surface.blit(self.text,self.rect)
        return

class Menu():
    surface = None
    def __init__(self, surface : pygame.Surface):
        self.buttons = []
        self.surface = surface
        surface.fill((0,0,0,0))
        self.other = []
    def add_text(self , text : str , pos , fontSize = 35 , font = "PMingLiU"):
        font = pygame.font.SysFont(font,fontSize)
        text = font.render(text,True,(255,255,255))
        rect = text.get_rect()
        rect.center = pos
        self.other.append((text,rect))
        return
    def add_picture(self):
        return #之後要補    
    def add_button(self,text : str  ,pos):
        self.buttons.append(Button(text,self.surface,pos))
    def add_buttons(self,details : list):
        for detail in details:
            self.buttons.append(Button(detail[0],self.surface,detail[1]))
    def draw(self):
        for button in self.buttons:
            button.draw()
        for i in self.other:
            self.surface.blit(i[0],i[1])
    def update(self):
        self.surface.fill((0,0,0,0))
        ret = -1
        for event in pygame.event.get():
            if event.type == pygame.MOUSEBUTTONDOWN:
                for index in range(len(self.buttons)):
                    if self.buttons[index].rect.collidepoint(event.pos):
                        self.buttons[index].clicked = not self.buttons[index].clicked
                        ret = index
            elif event.type == QUIT:
                pygame.quit()
                sys.exit()
        self.draw()
        return ret
    
class CoolBar(pygame.sprite.Sprite):
    fullSize = 400
    def __init__(self,text : str , player : bool , index : int , fullValue : int):
        super().__init__()
        self.text = text
        font = pygame.font.SysFont("Arial",25)
        self.text = font.render(text,True,(255,255,255))
        self.player = player
        self.index = index
        self.fullValue = fullValue
        return
    def update(self):
        size = (P2 if self.player else P1).wait[self.index]*self.fullSize/self.fullValue
        information.blit(self.text,(350 if self.player else 950,100+self.index*50))
        if self.player:
            pygame.draw.rect(information,(20,20,100+self.index*30),(1050,100+self.index*50,size,20))
        else:
            pygame.draw.rect(information,(100+self.index*30,20,20),(450,100+self.index*50,size,20))
        

#玩家
class Player(item):
    HP = 3
    x = 0
    y = 0
    shield_exist_time = 0
    isFlip = False
    def __init__(self,isFlip):
        super().__init__(isFlip,"picture/circle face.png",game_surface,(w - 200 , 450) if isFlip else (200 , 450))
        self.wait = [0 for _ in range(5)]
        self.skills = []
        self.bullets = pygame.sprite.Group()
        self.coolBars = pygame.sprite.Group()
        self.shields = pygame.sprite.Group()
        for i in range(self.HP):
            information.blit(heart_image,(120+self.isFlip*(w-380)+i*50,10))        
    def set_skills(self,skill1,skill2,skill3 = 0 ,skill4 = 0 ,skill5 = 0):
        self.skills = [None for _ in range(5)]
        self.skills[0] = skill1
        self.skills[1] = skill2
        self.skills[2] = skill3
        self.skills[3] = skill4
        self.skills[4] = skill5
        return
    def buildCoolBar(self):
        for i in range(3):
            self.coolBars.add(CoolBar("Bullet "+ str(i+1) , self.isFlip , i , self.skills[i].waitTime))
        return
    def shoot(self,index):
        if self.wait[index] == 0:
            if self.skills[index] == Bullet2:
                for _ in range(7):
                    bullet = self.skills[index](self.rect.center,self.isFlip)
                    self.bullets.add(bullet)
            elif self.skills[index] == Shield:
                shield = self.skills[index](self.rect.center,self.isFlip)
                self.shields.add(shield)
                self.shield_exist_time = 60
            else:
                bullet = self.skills[index](self.rect.center,self.isFlip)
                self.bullets.add(bullet)
            self.wait[index] = self.skills[index].waitTime
    def up(self):
        if self.rect.y >= 5:
            self.rect.y -= 5

    def down(self):
        if self.rect.y <= h - 135:
            self.rect.y += 5

    def left(self):
        if self.rect.x >= (w - 300 if self.isFlip else 0) :
            self.rect.x -= 5

    def right(self):
        if self.rect.x <= (w - 130 if self.isFlip else 170):
            self.rect.x += 5
    #更新所有資訊
    def update(self):
        for i in range(5):
            if self.wait[i] > 0:
                self.wait[i] -= 1
        for b in self.bullets:
            b.move()
            if b.rect.x > w or b.rect.x < 0:
                b.kill()
            else:
                b.draw()
        for s in self.shields:
            if self.shield_exist_time == 0:
                s.kill()
            else:
                self.shield_exist_time -= 1
                s.rect.x = self.rect.x -110 if self.isFlip else self.rect.x + 130
                s.rect.y = self.rect.y - 58
                s.draw() 
        if self.HP <= 0:
            self.image = pygame.image.load("picture/circle die.png").convert()
            self.image = pygame.transform.flip(self.image,self.isFlip,0)
        else:
            for i in range(self.HP):
                information.blit(heart_image,((w-380 if self.isFlip else 0)+120+i*50,10))
            

        for coolBar in self.coolBars:
            coolBar.update()

        self.draw()

#宣告全域物件
P1 = Player(False)
P2 = Player(True)
def help():
    bg.fill((0,0,0,0))
    window.blit(bg,(0,0))
    helpMenu = Menu(menu_surface)
    helpMenu.add_text("測試",(w/2,100))
    helpMenu.add_button("Return",(w/2,800))
    while True:
        res = helpMenu.update()
        if res >= 0:
            return 
        window.blit(menu_surface, (0, 0))
        pygame.display.update()
        for event in pygame.event.get():
            if event.type == QUIT:
                pygame.quit()
                sys.exit()
            elif event.type == pygame.MOUSEBUTTONDOWN:
                if helpMenu.buttons[0].rect.collidepoint(event.pos):  
                    return

def menu_phase(): 
    bg.blit(mainMenuBg,(0,0))
    window.blit(bg,(0,0))
    mainMenu = Menu(menu_surface)
    mainMenu.add_buttons([("Start",(w/2,100)),("Help",(w/2,200)),("Quit",(w/2,800))])
    while True:
        mainMenu.draw()
        res = mainMenu.update()
        window.blit(menu_surface, (0, 0))
        pygame.display.update()
        if res == 0:
            return
        if res == 1:
            help()
            mainMenu.buttons[1].clicked = False
            bg.blit(mainMenuBg,(0,0))
            window.blit(bg,(0,0))
        elif res == 2:
            pygame.quit()
            sys.exit()
        #event.get做一次就好

skillList = [Bullet1,Bullet2,Bullet3,Bullet4,Shield]
def choose_skills(player : bool):
    skillMenu = Menu(menu_surface)
    bg.fill((0,0,0,0))
    skillMenu.add_text("Player " + str(player+1),(300,30))
    skillMenu.add_buttons([("Normal Bullet",(w/3,100)),("Shot",(2*w/3,100)),("Large Bullet",(w/3,200)),("Fast Bullet",(2*w/3,200)),("Shield",(w/3,300)),("Confirm",(w/2,500)),("Quit",(w/2,800)),])
    window.blit(menu_surface,(0,0))
    pygame.display.update()
    cnt = 3
    window.blit(bg,(0,0))
    while True:
        res = skillMenu.update()
        window.blit(menu_surface, (0, 0))
        pygame.display.update()
        skillMenu.add_text("Player " + str(player+1),(300,30))
        if res == 5:
            confirmSound.play()
            if cnt == 0:
                break
            skillMenu.buttons[5].clicked = False
            #要能顯現錯誤訊息
            continue
        if res == -1:continue
        if skillMenu.buttons[res].clicked:
            cnt -= 1
        else:cnt += 1
        if res == 6:
            pygame.quit()
            sys.exit()
        for event in pygame.event.get():
            if event.type == QUIT:
                pygame.quit()
                sys.exit()
    for i in range(len(skillList)):
        if skillMenu.buttons[i].clicked:
            (P2 if player else P1).skills.append(skillList[i])
    return
        
        
menu_phase()
choose_skills(False)
choose_skills(True)
P1.buildCoolBar()
P2.buildCoolBar()

bg.fill((0,0,0))
pygame.draw.line(bg, (255, 255, 255), (300, 0), (300, 900), 4)
pygame.draw.line(bg, (255, 255, 255), (w-300, 0), (w-300, 900), 4)
pygame.draw.line(bg, (100, 100, 100), (w/2, 0), (w/2, 900), 4)

while P1.HP > 0 and P2.HP > 0:
    for event in pygame.event.get():
        if event.type == QUIT:
            pygame.quit()
            sys.exit()

    keys = pygame.key.get_pressed()
    if keys[pygame.K_w]:
        P1.up()
    if keys[pygame.K_s]:
        P1.down()
    if keys[pygame.K_a]:
        P1.left()
    if keys[pygame.K_d]:
        P1.right()
    if keys[pygame.K_j]:
        P1.shoot(0)
    if keys[pygame.K_k]:
        P1.shoot(1)
    if keys[pygame.K_l]:
        P1.shoot(2)
    
    if keys[pygame.K_UP]:
        P2.up()
    if keys[pygame.K_DOWN]:
        P2.down()
    if keys[pygame.K_LEFT]:
        P2.left()
    if keys[pygame.K_RIGHT]:
        P2.right()
    if keys[pygame.K_KP1]:
        P2.shoot(0)
    if keys[pygame.K_KP2]:
        P2.shoot(1)
    if keys[pygame.K_KP3]:
        P2.shoot(2)

    window.blit(bg, (0, 0))
    game_surface.fill((0,0,0,0))
    information.fill((0,0,0,0))
    P1.update()
    P2.update()
    window.blit(game_surface,(0,0))
    window.blit(information,(0,0))
    pygame.display.update()
    fpsClock.tick(FPS)  # 控制幀率

#最後一次更新
information.fill((0,0,0,0))
game_surface.fill((0,0,0,0))
P1.update()
P2.update()   
window.blit(bg,(0,0))
window.blit(game_surface,(0,0))
window.blit(information,(0,0))

pygame.display.update()
while True:
    for event in pygame.event.get():
        if event.type == QUIT:
            pygame.quit()
            sys.exit()
