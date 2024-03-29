import os
import sys
import random
import sqlite3
from math import ceil
from datetime import datetime, timedelta

import pygame


pastel_colors = [(233, 173, 216), (227, 207, 255), (164, 235, 251),
                 (239, 179, 191), (246, 174, 9), (0, 255, 255), (187, 255, 205)]


def load_image(name):
    fullname = os.path.join('data', name)
    if not os.path.isfile(fullname):
        print(f"Файл с изображением '{fullname}' не найден")
        terminate()
    image = pygame.image.load(fullname)
    return image


def load_level(name):
    fullname = os.path.join('data', name)
    if not os.path.isfile(fullname):
        print(f"Файл уровня '{fullname}' не найден")
        terminate()
    with open(fullname, 'r') as mapFile:
        level_map = [line.strip() for line in mapFile]
        level_height = len(level_map)
        level_width = len(level_map[0])
    return level_map, level_width, level_height


def generate_level(level):
    pusheen_x, pusheen_y = None, None
    for y in range(len(level)):
        for x in range(len(level[y])):
            if level[y][x] == '#':
                Tile('ground', x, y)
            elif level[y][x] == '_':
                Tile('sofa', x, y)
            elif level[y][x] == '0':
                Tile('donut', x, y)
            elif level[y][x] == ']':
                Tile('door', x, y)
            elif level[y][x] == '@':
                pusheen_x, pusheen_y = x, y
    return pusheen_x, pusheen_y


class Particle(pygame.sprite.Sprite):
    particles = [load_image('star.png')]
    for scale in (5, 10, 20, 40):
        particles.append(pygame.transform.scale(particles[0], (scale, scale)))

    def __init__(self, pos, dx, dy):
        super().__init__(all_sprites)
        self.image = random.choice(self.particles)
        self.rect = self.image.get_rect()
        self.velocity = [dx, dy]
        self.rect.x, self.rect.y = pos
        self.gravity = 0.5

    def update(self):
        self.velocity[1] += self.gravity
        self.rect.x += self.velocity[0]
        self.rect.y += self.velocity[1]
        if not self.rect.colliderect((0, 0, WIDTH, HEIGHT)):
            self.kill()


def create_particles(pos):
    particle_count = 20
    numbers = range(-5, 6)
    for _ in range(particle_count):
        Particle(pos, random.choice(numbers), random.choice(numbers))


class MathNumber(pygame.sprite.Sprite):
    def __init__(self, parent, number, is_prime):
        super().__init__()
        self.parent = parent
        self.is_prime = is_prime
        self.radius = 15
        self.color = random.choice(pastel_colors)
        self.image = pygame.Surface((2 * self.radius, 2 * self.radius), pygame.SRCALPHA, 32)
        self.image_boom = pygame.transform.scale(load_image('boom.png'), (4 * self.radius, 4 * self.radius))
        self.rect = self.image.get_rect()
        self.rect.x = random.randrange(MINIGAMEX + self.rect.width,
                                       MINIGAMEX + MINIGAMEWIDTH - self.rect.width)
        self.rect.y = random.randrange(MINIGAMEY + self.rect.height,
                                       MINIGAMEY + MINIGAMEHEIGHT - self.rect.height - 20)
        while pygame.sprite.spritecollideany(self, math_sprites):
            self.rect = self.image.get_rect()
            self.rect.x = random.randrange(MINIGAMEX + self.rect.width,
                                           MINIGAMEX + MINIGAMEWIDTH - self.rect.width)
            self.rect.y = random.randrange(MINIGAMEY + self.rect.height,
                                           MINIGAMEY + MINIGAMEHEIGHT - self.rect.height)
        font = pygame.font.Font(None, 20)
        text = font.render(str(number), True, (56, 13, 70))
        text_x = (self.rect.width - text.get_width()) // 2
        text_y = (self.rect.height - text.get_height()) // 2
        pygame.draw.circle(self.image, self.color, (self.radius, self.radius), self.radius)
        self.image.blit(text, (text_x, text_y))
        math_sprites.add(self)

    def update(self, event):
        if self.rect.collidepoint(event.pos):
            if self.is_prime:
                self.kill()
            else:
                self.image = self.image_boom
                self.parent.lose = True


class ICTNumber(pygame.sprite.Sprite):
    def __init__(self, parent, i, number):
        super().__init__()
        self.parent = parent
        self.number = number
        self.width = 55
        self.height = 120
        self.color = (0, 255, 0)
        self.image = pygame.Surface((self.width, self.height), pygame.SRCALPHA, 32)
        self.rect = self.image.get_rect()
        self.rect.x = MINIGAMEX + 10 + i * (self.width + 5)
        self.rect.y = MINIGAMEY + (MINIGAMEHEIGHT - self.height) // 2
        self.redraw(self.color)
        ict_sprites.add(self)

    def redraw(self, color):
        font = pygame.font.Font(None, 20)
        text = font.render(str(self.number), True, (0, 0, 0))
        text_x = (self.rect.width - text.get_width()) // 2
        text_y = (self.rect.height - text.get_height()) // 2
        pygame.draw.rect(self.image, color, (0, 0, self.width, self.height))
        self.image.blit(text, (text_x, text_y))

    def update(self, event):
        if self.rect.collidepoint(event.pos):
            self.number ^= 1
            self.redraw((0, 255, 0))


class EnglishWord(pygame.sprite.Sprite):
    def __init__(self, parent, i, j, word, synonym):
        super().__init__()
        self.parent = parent
        self.word = word
        self.synonym = synonym
        self.width = 100
        self.height = 60
        self.color = random.choice(pastel_colors)
        self.image = pygame.Surface((self.width, self.height), pygame.SRCALPHA, 32)
        self.rect = self.image.get_rect()
        self.rect.x = MINIGAMEX + 20 + i * (self.width + 20)
        self.rect.y = MINIGAMEY + (MINIGAMEHEIGHT - self.height * 3) // 2 + j * self.height * 2
        self.redraw(random.choice(pastel_colors))
        english_sprites.add(self)

    def redraw(self, color):
        font = pygame.font.Font(None, 20)
        text = font.render(self.word, True, (56, 13, 70))
        text_x = (self.rect.width - text.get_width()) // 2
        text_y = (self.rect.height - text.get_height()) // 2
        pygame.draw.rect(self.image, color, (0, 0, self.width, self.height))
        self.image.blit(text, (text_x, text_y))

    def update(self, event):
        if self.rect.collidepoint(event.pos):
            if self.parent.prev is not None:
                if self.parent.prev.word == self.synonym:
                    self.redraw((0, 255, 0))
                    self.parent.prev.redraw((0, 255, 0))
                    english_sprites.draw(screen)
                    pygame.display.flip()
                    pygame.time.delay(500)
                    self.parent.prev.kill()
                    self.kill()
                elif self.parent.prev.word != self.word:
                    self.redraw((255, 0, 0))
                    self.parent.prev.redraw((255, 0, 0))
                    self.parent.lose = True
                self.parent.prev = None
            else:
                self.parent.prev = self


class MathMiniGame:
    def __init__(self):
        self.primes = [x for x in range(2, 101) if self.is_prime(x)]
        self.numbers = sorted(set(range(2, 101)) - set(self.primes))
        self.selected_primes = random.sample(self.primes, 10)
        self.selected_numbers = random.sample(self.numbers, 10)
        for prime in self.selected_primes:
            ball = MathNumber(self, prime, True)
        for number in self.selected_numbers:
            ball = MathNumber(self, number, False)
        self.lose = False

    def is_prime(self, n):
        for i in range(2, int(n ** 0.5) + 1):
            if n % i == 0:
                return False
        return True

    def draw_background(self, screen):
        pygame.draw.rect(screen, pygame.Color(148, 122, 162),
                         (MINIGAMEX - 5, MINIGAMEY - 5, MINIGAMEWIDTH + 10, MINIGAMEHEIGHT + 10))
        pygame.draw.rect(screen, pygame.Color(197, 167, 232),
                         (MINIGAMEX, MINIGAMEY, MINIGAMEWIDTH, MINIGAMEHEIGHT))
        font = pygame.font.Font(None, 30)
        text = font.render(f'Нажмите на все простые числа', True, (255, 255, 255))
        screen.blit(text, (MINIGAMEX + (MINIGAMEWIDTH - text.get_width()) // 2, MINIGAMEY + 10))        

    def check_win(self):
        for sprite in math_sprites:
            if sprite.is_prime:
                return False
        return True

    def check_lose(self):
        return self.lose


class ICTMiniGame:
    def __init__(self):
        self.number = random.randint(0, 256)
        for i in range(8):
            ict_number = ICTNumber(self, i, 0)

    def draw_background(self, screen):
        pygame.draw.rect(screen, pygame.Color(148, 122, 162),
                         (MINIGAMEX - 5, MINIGAMEY - 5, MINIGAMEWIDTH + 10, MINIGAMEHEIGHT + 10))
        pygame.draw.rect(screen, pygame.Color(197, 167, 232),
                         (MINIGAMEX, MINIGAMEY, MINIGAMEWIDTH, MINIGAMEHEIGHT))
        font = pygame.font.Font(None, 25)
        text = font.render(f'Переведите число {self.number} в двоичную систему счисления', True, (255, 255, 255))
        screen.blit(text, (MINIGAMEX + (MINIGAMEWIDTH - text.get_width()) // 2, MINIGAMEY + 10))

    def check_win(self):
        res = ''.join(str(sprite.number) for sprite in ict_sprites)
        return int(res, 2) == self.number

    def check_lose(self):
        return False


class EnglishMiniGame:
    def __init__(self):
        self.words = {'good': 'nice', 'big': 'gigantic', 'sad': 'unhappy', 'surprised': 'amazed',
                      'happy': 'joyful', 'interesting': 'fascinating', 'beautiful': 'pretty'}
        self.selected_words = random.sample(sorted(self.words), 4)
        self.selected_synonyms = [self.words[key] for key in self.selected_words]
        indices = list(range(4))
        random.shuffle(indices)
        for i in range(4):
            word = self.selected_words[i]
            synonym = self.selected_synonyms[i]
            word_sprite = EnglishWord(self, i, 0, word, synonym)
            word_sprite = EnglishWord(self, indices[i], 1, synonym, word)
        self.prev = None
        self.lose = False

    def draw_background(self, screen):
        pygame.draw.rect(screen, pygame.Color(148, 122, 162),
                         (MINIGAMEX - 5, MINIGAMEY - 5, MINIGAMEWIDTH + 10, MINIGAMEHEIGHT + 10))
        pygame.draw.rect(screen, pygame.Color(197, 167, 232),
                         (MINIGAMEX, MINIGAMEY, MINIGAMEWIDTH, MINIGAMEHEIGHT))
        font = pygame.font.Font(None, 30)
        text = font.render(f'Соедините слова с их синонимами', True, (255, 255, 255))
        screen.blit(text, (MINIGAMEX + (MINIGAMEWIDTH - text.get_width()) // 2, MINIGAMEY + 10))        

    def check_win(self):
        return not english_sprites

    def check_lose(self):
        return self.lose


def mini_game(subject):
    if subject == 'maths':
        sprites = math_sprites
        game = MathMiniGame()
    elif subject == 'english':
        sprites = english_sprites
        game = EnglishMiniGame()
    elif subject == 'ict':
        sprites = ict_sprites
        game = ICTMiniGame()
    else:
        return True
    timer.start()
    while True:
        if timer.end() < 0:
            return False
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                terminate()
            if event.type == pygame.MOUSEBUTTONDOWN:
                sprites.update(event)
        game.draw_background(screen)
        sprites.draw(screen)
        timer.draw(screen)
        pygame.display.flip()
        if game.check_win():
            return True
        if game.check_lose():
            return False
        clock.tick(FPS)


class Pusheen(pygame.sprite.Sprite):
    JUMPS = 20

    def __init__(self, pos_x, pos_y, image):
        super().__init__(all_sprites)
        name, extension = image.split('.')
        image_1 = pygame.transform.scale(load_image(f'{name}_1.{extension}'), (CELLWIDTH, CELLHEIGHT))
        image_2 = pygame.transform.scale(load_image(f'{name}_2.{extension}'), (CELLWIDTH, CELLHEIGHT))
        self.images = [image_1, image_2]
        self.cur_image = 0
        self.redraw()
        self.rect = self.image.get_rect()
        self.rect.x, self.rect.y = CELLWIDTH * pos_x, CELLHEIGHT * pos_y
        self.speed = 7
        self.direction = 1
        self.visited_sofas = list()
        self.jump_flag = False
        self.jump_count = 0
        self.can_move = True

    def move(self):
        if not self.can_move:
            return False
        pressed = pygame.key.get_pressed()
        if pressed[pygame.K_RIGHT] or pressed[pygame.K_d]:
            if not self.collision('midright', tile_sprites):
                if self.direction != 1:
                    self.images = [pygame.transform.flip(im, True, False) for im in self.images]
                    self.direction = 1
                self.rect.x += self.speed
        if pressed[pygame.K_LEFT] or pressed[pygame.K_a]:
            if not self.collision('midleft', tile_sprites):
                if self.direction != -1:
                    self.images = [pygame.transform.flip(im, True, False) for im in self.images]
                    self.direction = -1
                self.rect.x -= self.speed
        if (pressed[pygame.K_UP] or pressed[pygame.K_w] or pressed[pygame.K_SPACE]) and not self.jump_flag:
            self.jump_flag = True
            self.jump_count = self.JUMPS
        if self.jump_flag:
            if self.jump_count > 0 and self.collision('midtop', tile_sprites):
                self.jump_count = 0
            elif (self.jump_count > 0 and not self.collision('midtop', tile_sprites) or
                  self.jump_count <= 0 and not self.collision('midbottom', tile_sprites)):
                self.rect.y -= self.jump_count
                self.jump_count -= 1
            else:
                self.jump_flag = False
        if not self.jump_flag and not self.collision('midbottom', tile_sprites):
            self.rect.y -= self.jump_count
            self.jump_count -= 1
        if self.collision('midleft', tile_sprites):
            self.rect.x += self.speed
        if self.collision('midright', tile_sprites):
            self.rect.x -= self.speed
        while self.floor_collision(tile_sprites):
            self.rect.y -= 1
        sofa = pygame.sprite.spritecollideany(self, sofa_sprites)
        if self.collision('midbottom', sofa_sprites) and sofa not in self.visited_sofas:
            self.visited_sofas.append(sofa)
            self.images = [pygame.transform.flip(im, False, True) for im in self.images]
            self.can_move = False
            pygame.time.set_timer(RECOVERFROMSOFA, 2500, True)
        donut = pygame.sprite.spritecollideany(self, donut_sprites)
        if donut:
            timer.donuts += 1
            donut.kill()
        if pygame.sprite.spritecollideany(self, door_sprites):
            return timer.end() >= 0

    def redraw(self):
        self.cur_image ^= 1
        self.image = self.images[self.cur_image]

    def recover_from_sofa(self):
        self.can_move = True
        self.images = [pygame.transform.flip(im, False, True) for im in self.images]

    def collision(self, point, group):
        return any(tile.rect.collidepoint(getattr(self.rect, point)) for tile in group)

    def floor_collision(self, group):
        x, y = self.rect.midbottom
        return any(tile.rect.collidepoint(x, y - 1) for tile in group)

    def check_fall(self):
        return self.rect.y > HEIGHT * 0.9


class Button(pygame.sprite.Sprite):
    def __init__(self, x, y, width, height, image, clicked_image, group=None):
        super().__init__(all_sprites, button_sprites)
        self.name = image
        self.main_image = pygame.transform.scale(load_image(image), (width, height))
        self.clicked_image = pygame.transform.scale(load_image(clicked_image), (width, height))
        self.image = self.main_image
        self.rect = self.image.get_rect()
        self.rect.x, self.rect.y = x, y
        self.group = group
        self.clicked = False

    def update(self, event):
        if self.rect.collidepoint(event.pos):
            for button in button_sprites:
                if button.group == self.group:
                    button.image = button.main_image
                    button.clicked = False
            self.image = self.clicked_image
            self.clicked = True

    def connect(self, function):
        if self.clicked:
            function()

    def is_clicked(self):
        return self.clicked

    def get_name(self):
        return self.name


class Tile(pygame.sprite.Sprite):
    def __init__(self, tile_type, pos_x, pos_y):
        super().__init__(all_sprites, *tile_groups[tile_type])
        self.image = pygame.transform.scale(tile_images[tile_type], (CELLWIDTH, CELLHEIGHT))
        self.rect = self.image.get_rect().move(CELLWIDTH * pos_x, CELLHEIGHT * pos_y)


class InputField:
    def __init__(self, color, text_color, x, y, width, height):
        self.text = list()
        self.color = color
        self.text_color = text_color
        self.x = x
        self.y = y
        self.width = width
        self.height = height

    def draw(self, screen):
        pygame.draw.rect(screen, self.color, (self.x, self.y, self.width, self.height))
        font = pygame.font.Font(None, 50)
        text = font.render(''.join(self.text), True, self.text_color)
        screen.blit(text, (self.x, self.y))

    def update(self, event):
        if event.key == pygame.K_BACKSPACE and self.text:
            self.text.pop()
        else:
            code = event.unicode
            if code and ord(' ') <= ord(code) <= ord('~'):
                self.text.append(code)

    def get_text(self):
        return ''.join(self.text)


class Camera:
    def __init__(self):
        self.dx = 0
        self.dy = 0

    def apply(self, obj):
        obj.rect.x += self.dx
        obj.rect.y += self.dy

    def update(self, target):
        self.dx = -(target.rect.x + target.rect.w // 2 - WIDTH // 2)
        self.dy = -(target.rect.y + target.rect.h // 2 - HEIGHT // 2)


class MusicPlayer:
    def __init__(self):
        pygame.mixer.music.load('data/pusheen_music.mp3')
        self.paused = False

    def play(self):
        pygame.mixer.music.play(-1)

    def pause(self):
        if self.paused:
            pygame.mixer.music.unpause()
        else:
            pygame.mixer.music.pause()
        self.paused = not self.paused

    def stop(self):
        pygame.mixer.music.stop()


class Database:
    def __init__(self):
        self.con = self.load_db('users.sqlite')
        self.cur = self.con.cursor()

    def get_current_level(self, user_name):
        user_id = self.cur.execute('SELECT id FROM users WHERE name=?', [user_name]).fetchone()
        if user_id is None:
            self.cur.execute('INSERT INTO users(name) VALUES (?)', [user_name])
            self.cur.execute('INSERT INTO levels(level) VALUES (?)', [0])
            self.con.commit()
        user_id = self.cur.execute('SELECT id FROM users WHERE name=?', [user_name]).fetchone()[0]
        return self.cur.execute('SELECT level FROM levels WHERE id=?', [user_id]).fetchone()[0]

    def write(self, name, level):
        self.cur.execute('UPDATE levels SET level = ? WHERE id=(SELECT id FROM users WHERE name=?)', [level, name])
        self.con.commit()

    def load_db(self, name):
        fullname = os.path.join('data', name)
        if not os.path.isfile(fullname):
            print(f"База данных '{fullname}' не найден")
            terminate()
        return sqlite3.connect(fullname)


class Timer:
    def __init__(self):
        self.begin_time = None
        self.end_time = None
        self.donuts = 0

    def draw(self, screen):
        pygame.draw.rect(screen, (229, 204, 255), (0, 0, 80, 35))
        time = f'{timer.end() // 60}:{timer.end() % 60}'
        font = pygame.font.Font(None, 50)
        text = font.render(time, True, (157, 135, 183))
        screen.blit(text, (5, 5))

    def start(self):
        self.begin_time = datetime.now()
        self.donuts = 0

    def end(self):
        if self.begin_time is not None:
            return TIME - (datetime.now() - self.begin_time).seconds + self.donuts * DONUT


def terminate():
    pygame.quit()
    sys.exit()


def get_pusheen_name():
    pusheen_name = 'pusheen_gray.png'
    for button in button_sprites:
        if button.clicked and button.group == PUSHEENRADIOGROUP:
            pusheen_name = button.get_name()[:-6] + button.get_name()[-4:]
    return pusheen_name


def level_result(win):
    image = pygame.transform.scale(load_image(['lose.png', 'win.png'][win]), (WIDTH, HEIGHT))
    screen.blit(image, (0, 0))
    while True:
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                terminate()
            if event.type == pygame.KEYDOWN:
                return
        pygame.display.flip()
        clock.tick(FPS)


def start_screen():
    start_image = pygame.transform.scale(load_image('start_screen.png'), (WIDTH, HEIGHT))
    while True:
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                terminate()
            if event.type == pygame.KEYDOWN:
                return
        screen.blit(start_image, (0, 0))
        pygame.display.flip()
        clock.tick(FPS)


def login_screen():
    login_image = pygame.transform.scale(load_image('login_screen.png'), (WIDTH, HEIGHT))
    offset, dx = (WIDTH - (CELLWIDTH + 100) * 3) // 2, 100
    gray_pusheen = Button(offset, 370, CELLWIDTH, CELLHEIGHT,
                          'pusheen_gray_1.png', 'pusheen_gray_2.png', group=PUSHEENRADIOGROUP)
    pink_pusheen = Button(offset + CELLWIDTH + dx, 370, CELLWIDTH, CELLHEIGHT,
                          'pusheen_pink_1.png', 'pusheen_pink_2.png', group=PUSHEENRADIOGROUP)
    green_pusheen = Button(offset + (CELLWIDTH + dx) * 2, 370, CELLWIDTH, CELLHEIGHT,
                           'pusheen_green_1.png', 'pusheen_green_2.png', group=PUSHEENRADIOGROUP)
    ok_button = Button((WIDTH - 100) // 2, 520, 100, 100, 'ok.png', 'ok.png')
    input_field = InputField((227, 207, 255), (157, 135, 183), (WIDTH - 30) // 2, 220, 550, 30)
    while True:
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                terminate()
            if event.type == pygame.MOUSEBUTTONDOWN:
                button_sprites.update(event)
                if ok_button.is_clicked():
                    return input_field.get_text()
            if event.type == pygame.KEYDOWN:
                input_field.update(event)
        screen.blit(login_image, (0, 0))
        all_sprites.draw(screen)
        input_field.draw(screen)
        pygame.display.flip()
        clock.tick(FPS)


def main_screen(cur_level):
    all_sprites.empty()
    bg_image = pygame.transform.scale(load_image(cur_level + '.png'), (WIDTH, HEIGHT))
    level_map, level_width, level_height = load_level(cur_level + '.txt')
    pusheen_x, pusheen_y = generate_level(level_map)
    pusheen = Pusheen(pusheen_x, pusheen_y, get_pusheen_name())
    pygame.time.set_timer(UPDATEPUSHEEN, 200)
    timer.start()
    while True:
        if timer.end() < 0 or pusheen.check_fall():
            return False
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                terminate()
            if event.type == pygame.KEYDOWN:
                if event.key == pygame.K_p:
                    player.pause()
                if event.key == pygame.K_r:
                    main_screen(cur_level)
            if event.type == UPDATEPUSHEEN:
                pusheen.redraw()
            if event.type == RECOVERFROMSOFA:
                pusheen.recover_from_sofa()
        camera.update(pusheen)
        for sprite in all_sprites:
            camera.apply(sprite)
        if pusheen.move():
            minigame_result = mini_game(cur_level)
            pygame.time.delay(1000)
            level_result(minigame_result)
            return minigame_result
        screen.blit(bg_image, (0, 0))
        all_sprites.draw(screen)
        timer.draw(screen)
        pygame.display.flip()
        clock.tick(FPS)


def final_screen():
    player.stop()
    all_sprites.empty()
    final_image = pygame.transform.scale(load_image(f'final_screen_{get_pusheen_name()}'), (WIDTH, HEIGHT))
    pygame.time.set_timer(UPDATESTARS, 100)
    while True:
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                terminate()
            if event.type == pygame.KEYDOWN:
                return
            if event.type == UPDATESTARS:
                create_particles((random.randint(0, WIDTH), random.randint(0, 3 * HEIGHT // 4)))
        all_sprites.update()
        screen.blit(final_image, (0, 0))
        all_sprites.draw(screen)
        pygame.display.flip()
        clock.tick(FPS)


pygame.init()
pygame.display.set_caption('Pusheen game')
image = load_image('icon.png')
pygame.display.set_icon(image)

PUSHEENRADIOGROUP = 1

UPDATESTARS = pygame.USEREVENT + 1
UPDATEPUSHEEN = pygame.USEREVENT + 2
RECOVERFROMSOFA = pygame.USEREVENT + 3

CELLWIDTH = 200
CELLHEIGHT = 130
info = pygame.display.Info()
SIZE = WIDTH, HEIGHT = info.current_w - 200, CELLHEIGHT * 5
MINIGAMEWIDTH, MINIGAMEHEIGHT = 500, 500
MINIGAMEX = (WIDTH - MINIGAMEWIDTH) // 2
MINIGAMEY = (HEIGHT - MINIGAMEHEIGHT) // 2
screen = pygame.display.set_mode(SIZE)

clock = pygame.time.Clock()
FPS = 60
timer = Timer()
TIME = 30
DONUT = 5
player = MusicPlayer()
db = Database()
camera = Camera()

all_sprites = pygame.sprite.Group()
button_sprites = pygame.sprite.Group()
tile_images = {
    'sofa': load_image('sofa.png'),
    'ground': load_image('ground.png'),
    'donut': load_image('donut.png'),
    'door': load_image('door.png')
}

LEVELCOUNT = 5
LEVELS = ['english', 'corridor0', 'maths', 'corridor1', 'ict']

start_screen()
login = login_screen()
level = db.get_current_level(login) % 5
player.play()
while level < LEVELCOUNT:
    tile_sprites = pygame.sprite.Group()
    sofa_sprites = pygame.sprite.Group()
    donut_sprites = pygame.sprite.Group()
    door_sprites = pygame.sprite.Group()
    english_sprites = pygame.sprite.Group()
    math_sprites = pygame.sprite.Group()
    ict_sprites = pygame.sprite.Group()    
    tile_groups = {
        'sofa': [sofa_sprites, tile_sprites],
        'ground': [tile_sprites],
        'donut': [donut_sprites],
        'door': [door_sprites]
    }
    if main_screen(LEVELS[level]):
        level += 1
        db.write(login, level)
    else:
        level_result(False)
final_screen()
terminate()