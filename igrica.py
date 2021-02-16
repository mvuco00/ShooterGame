import pygame as pg
import sys
import random


LIGHTBLUE = pg.Color('lightskyblue2')
DARKBLUE = (31, 10, 99)
BLUE = (0, 0, 255)
WHITE = (255, 255, 255)
BLACK = (0, 0, 0)
LIGHTRED = (238, 59, 59)
RED = (255, 0, 0)
YELLOW = (255,215,0)
#varijable
DISPLAY_WIDTH = 400
DISPLAY_HEIGHT = 600

FPS = 35

class Game:
    def __init__(self, screen):
        self.screen = screen

        self.clock = pg.time.Clock()
        self.game_over = False
        self.game_exit = False
        self.pause = False
        self.started = False

        self.score = 0
        self.enemy_num = 4
        self.count = 0

        self.all_sprites = pg.sprite.Group()
        self.player_sprite = pg.sprite.GroupSingle()
        self.enemy_sprites = pg.sprite.Group()
        self.bullet_sprites = pg.sprite.Group()
        self.coin_sprites = pg.sprite.Group()
        self.powerful_enemy_sprites = pg.sprite.GroupSingle()


        self.player = Player()
        self.enemy = None
        self.big_enemy = None
        pg.mixer.music.load("music/bgmusic.mp3")
        pg.mixer.music.play()

        self.player_sprite.add(self.player)
        self.all_sprites.add(self.player)

        # stvaramo neprijatelje
        self.create_enemies(self.enemy_num)


    def process_events(self):
        for event in pg.event.get():
            if event.type == pg.QUIT or event.type == pg.KEYDOWN and event.key == pg.K_ESCAPE or event.type == pg.KEYDOWN and event.key == pg.K_q:
                return True
            if event.type == pg.KEYDOWN and event.key == pg.K_SPACE:
                self.create_bullets()
            if event.type == pg.KEYDOWN and event.key == pg.K_p:
                self.pause = True
            if self.game_over and event.type == pg.KEYDOWN and event.key == pg.K_c:
                self.__init__(self.screen)



    def create_bullets(self):
        bullet = self.player.shoot()
        self.bullet_sprites.add(bullet)
        self.all_sprites.add(bullet)


    #stvaranje neprijatelja
    def create_enemies(self, num):
        for i in range(num): #radimo više neprijatelja
            self.enemy = Enemy()
            self.all_sprites.add(self.enemy)
            self.enemy_sprites.add(self.enemy)


    def display_frame(self):
        bg_image = pg.image.load('img/city_new2.png')
        self.all_sprites.update()

        if self.game_over:
            self.game_over_function()

        elif self.pause:
            self.paused()

        elif not self.started:
            self.game_intro()


        elif self.started:
            self.check_collision()

            self.screen.blit(bg_image, (0,0))
            self.all_sprites.draw(self.screen)
            self.text_score(self.score)

            pg.display.update()


    def check_collision(self):
        coin_sound = pg.mixer.Sound('music/coins.wav')
        shot_sound = pg.mixer.Sound('music/boom.wav')
        big_enemy_dies = pg.mixer.Sound('music/enemydie.wav')


        # gledamo je li neprijatelj udario u igrača
        hits = pg.sprite.spritecollide(self.player, self.enemy_sprites, False)

        # gledamo je li metak pogodio neprijatelja
        pogodak = pg.sprite.groupcollide(self.enemy_sprites, self.bullet_sprites, True, True)

        # gledamo je li igrač dohvatio zlatnik
        touch_coin = pg.sprite.spritecollide(self.player, self.coin_sprites, True)

        # gledamo je li igrač pogodio zlatnik
        shot_coin = pg.sprite.groupcollide(self.coin_sprites, self.bullet_sprites, True, True)

        # gledamo je li igrač pogodio velikog neprijatelja
        big_enemy_hit = pg.sprite.groupcollide(self.powerful_enemy_sprites, self.bullet_sprites, False, True)

        #gledamo je li veliki neprijatelj udario u igrača
        big_enemy_player_collide = pg.sprite.spritecollide(self.player,self.powerful_enemy_sprites,False)


        if hits and big_enemy_player_collide:
            self.started = False
            self.game_over = True

        if pogodak:
            # moramo generirat nove neprijatelje nakon sto pogodimo metu jer se iz grupe sprite.group uklanjaju
            pg.mixer.Sound.play(shot_sound)
            for pog in pogodak:
                self.score = self.update_score(self.score, pog.points)
                self.make_coins()
                self.make_big_enemy()
                self.create_enemies(1)

        # zlatnik nosi 5 bodova
        if touch_coin or shot_coin:
            pg.mixer.Sound.play(coin_sound)
            self.score = self.update_score(self.score, 5)
            self.make_coins()

        if big_enemy_hit:
            for x in big_enemy_hit:
                self.count = self.count + 1
                if self.count > 9:
                    self.big_enemy.killsprite()
                    pg.mixer.Sound.play(big_enemy_dies)
                    self.count = 0
                    #neprijatelj nosi 10 bodova
                    self.score = self.update_score(self.score, 10)
                    self.make_coins()

        #ako neprijatelj napusti zaslon dogodi se kraj igre
        for enemy1 in self.enemy_sprites:
            if enemy1.rect.top > DISPLAY_HEIGHT - enemy1.rect.height:
                self.started = False
                self.game_over = True

        #veliki neprijatelj napusti ekran
        for enemy2 in self.powerful_enemy_sprites:
            if enemy2.rect.top > DISPLAY_HEIGHT - enemy2.rect.height:
                self.started = False
                self.game_over = True



    def game_intro(self):
        intro = True

        while intro:
            self.intro_screen_over = pg.time.get_ticks()
            for event in pg.event.get():
                if event.type == pg.QUIT:
                    pg.quit()
                    quit()

                if event.type == pg.KEYDOWN:
                    if event.key == pg.K_c:
                        intro = False
                        self.started = True

                    elif event.key == pg.K_q:
                        pg.quit()
                        quit()

            self.screen.fill(BLACK)
            self.message_to_screen("Welcome", (0,255,0), -130, size="medium")
            self.message_to_screen("to SPACE FIGHT", (0,255,0), -50, size="medium")
            self.message_to_screen("Press C to continue", LIGHTBLUE, 10, size="small")
            self.message_to_screen(" Q to quit", LIGHTBLUE, 50, size="small")
            pg.display.update()




    def game_over_function(self):
        self.all_sprites.remove(self.enemy_sprites, self.bullet_sprites, self.player_sprite)
        clock = pg.time.Clock()

        self.screen.fill(BLACK)
        self.message_to_screen("GAME OVER", RED, -120, size="big")
        self.message_to_screen("Press C to continue", LIGHTBLUE, -50, size="small")
        self.message_to_screen("or Q to quit", LIGHTBLUE, 0, size="small")

        pg.display.update()
        clock.tick(5)


    def update_score(self, score, num):
        score = score + num
        return score

    def text_score(self, score):
        smallfont = pg.font.SysFont("rockwell", 25)
        text = smallfont.render("Score: " + str(score), True, WHITE)
        self.screen.blit(text, [0,0])


    def paused(self):
        paused = True
        clock = pg.time.Clock()

        while paused:
            for event in pg.event.get():
                if event.type == pg.QUIT:
                    pg.quit()
                    quit()

                if event.type == pg.KEYDOWN:
                    if event.key == pg.K_c:
                        paused = False
                        self.pause = False

                    elif event.key == pg.K_q:
                        pg.quit()
                        quit()

            self.screen.fill(DARKBLUE)
            self.message_to_screen("Paused", LIGHTBLUE, -120, size="big")
            self.message_to_screen("Press C to continue", LIGHTBLUE, -50, size="small")
            self.message_to_screen("or Q to quit", LIGHTBLUE, 0, size="small")

            pg.display.update()
            clock.tick(5)


    def message_to_screen(self, msg, color, y_displace=0, size="small"):  # y_displace pomice od centra
        textSurface, textRect = self.text_objects(msg, color, size)
        textRect.center = (DISPLAY_WIDTH / 2), (DISPLAY_HEIGHT / 2) + y_displace
        self.screen.blit(textSurface, textRect)


    def text_objects(self, text, color, size):

        smallfont = pg.font.SysFont("rockwell", 25)  # moramo def font
        mediumfont = pg.font.SysFont("rockwell", 50)
        bigfont = pg.font.SysFont("rockwell", 65)

        if size == "small":
            textSurf = smallfont.render(text, True, color)
        elif size == "medium":
            textSurf = mediumfont.render(text, True, color)
        elif size == "big":
            textSurf = bigfont.render(text, True, color)

        return textSurf, textSurf.get_rect()


    def make_coins(self):
        if self.score % 10 == 0:
            self.coin = Coins()
            self.coin_sprites.add(self.coin)
            self.all_sprites.add(self.coin)


    def make_big_enemy(self):
        #moze se pojaviti samo jedan snažni neprijatelj
        if len(self.powerful_enemy_sprites) == 0 and self.score % 10 == 0:
            self.big_enemy = Powerful_enemy()
            self.powerful_enemy_sprites.add(self.big_enemy)
            self.all_sprites.add(self.big_enemy)





class Bullets(pg.sprite.Sprite):
    def __init__(self, position, move): # x,y jer se metak ispali uvijek s mjesta na kojem se mi nalazimo
        pg.sprite.Sprite.__init__(self)
        self.image = pg.Surface((4, 10))
        self.image.fill(YELLOW)
        self.rect = self.image.get_rect(center = position)
        self.speedy = move #metak ide od doli prema gori

    def update(self, *args):
        self.rect.y -= self.speedy

        #ako promašimo taj metak se briše, nece nastavit putovat beskonačno
        if self.rect.bottom < 0:
            self.kill()


class Coins(pg.sprite.Sprite):
    def __init__(self):
        pg.sprite.Sprite.__init__(self)
        self.image = pg.image.load('img/coin2.png')
        self.rect = self.image.get_rect()
        self.speed = 10
        self.rect.x = random.randrange(0, DISPLAY_WIDTH - self.rect.width)
        self.rect.y = random.randrange(-300, -10)

    def update(self, *args):
        self.rect.y += self.speed
        # kad zlatnik dode do dna, on tu i ostane
        if self.rect.y >= DISPLAY_HEIGHT-self.rect.height-30 and self.speed >=0:
            self.speed = 0





class Player(pg.sprite.Sprite):
    player_position = (DISPLAY_WIDTH/2, DISPLAY_HEIGHT-50) # početna pozicija igrača
    def __init__(self):
        pg.sprite.Sprite.__init__(self)
        # http://untamed.wild-refuge.net/rmxpresources.php?characters
        self.image = pg.image.load('img/player.png')
        self.rect = self.image.get_rect(center = self.player_position)

        self.move_x = 15
        self.move_bullet = 35
        # granica da igrac ne napusti ekran
        self.bounds = pg.Rect(10, DISPLAY_HEIGHT-60, DISPLAY_WIDTH - 20, 25)

    def update(self, *args):
        keys = pg.key.get_pressed()
        self.move_player(keys)

    def move_player(self,keys):
        if keys[pg.K_LEFT]:

            self.rect.move_ip(-self.move_x, 0)

        elif keys[pg.K_RIGHT]:

            self.rect.move_ip(self.move_x, 0)

        self.rect.clamp_ip(self.bounds)


    def shoot(self):
        return Bullets(self.rect.midtop, self.move_bullet)



class Enemy(pg.sprite.Sprite):
    def __init__(self):
        pg.sprite.Sprite.__init__(self)
        # https://forums.rpgmakerweb.com/index.php?threads/marvel-characters-sets-sv-battlers-avengers-spider-man-x-men-more.101244/
        self.image_names = ['img/big0.png', 'img/big1.png', 'img/big2.png', 'img/big3.png', 'img/big4.png']
        self.random_img = random.choice(self.image_names)
        self.image = pg.image.load(self.random_img)
        self.rect = self.image.get_rect()

        self.rect.x = random.randrange(self.rect.width, DISPLAY_WIDTH - self.rect.width-10)
        self.rect.y = random.randrange(-300, -70)

        self.speed = random.randrange(3, 8) # svi objekti nece padat s istom brzinom
        self.points = self.different_scores(self.random_img)

    def update(self, *args):
        self.rect.y += self.speed

    def different_scores(self, rand_img):
        if rand_img == 'img/big0.png':
            return 5
        elif rand_img == 'img/big1.png' or rand_img == 'img/big2.png':
            return 4
        else:
            return 1



class Powerful_enemy(pg.sprite.Sprite):
    def __init__(self):
        pg.sprite.Sprite.__init__(self)
        self.image = pg.image.load('img/bigenemy.png')
        self.rect = self.image.get_rect()
        self.rect.x = random.randrange(self.rect.width, DISPLAY_WIDTH - self.rect.width)
        self.rect.y = random.randrange(-300, -self.rect.height)
        self.speed = 2

    def update(self, *args):
        self.rect.y += self.speed

    def killsprite(self):
        self.kill()





def main():
    pg.init()
    screen = pg.display.set_mode((DISPLAY_WIDTH,DISPLAY_HEIGHT))
    pg.display.set_caption('Space Fight')
    clock = pg.time.Clock()
    game = Game(screen)

    gameExit = False

    while not gameExit:
        gameExit = game.process_events()
        game.display_frame()
        clock.tick(FPS)

    pg.quit()



if __name__ == '__main__':
    main()