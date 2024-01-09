import sys
import os
import random
from math import ceil
import pygame
from PIL import Image


GRAVITY = 0.5
JUMPS = 20
FPS = 60
CELLWIDTH = 200
CELLHEIGHT = 130
PUSHEEN = 1
UPDATESTARS = pygame.USEREVENT + 1
UPDATEPUSHEEN = pygame.USEREVENT + 2
RECOVER = pygame.USEREVENT + 3


# salmon, coral, gold, springgreen, cyan, royalblue, mediumpurple, purple, lavender, hotpink, pink, violet
pastel_colors = [(250, 128, 114), (255, 127, 80), (255, 215, 0), (0, 255, 127),
                 (0, 255, 255), (65, 105, 225), (147, 112, 219), (128, 0, 128),
                 (230, 230, 250), (255, 105, 180), (255, 192, 203), (238, 130, 238)]


def is_inside(x, y):
    return 0 <= x < WIDTH and 0 <= y < HEIGHT


def load_image(name):
    fullname = os.path.join('data', name)
    if not os.path.isfile(fullname):
        print(f"Файл с изображением '{fullname}' не найден")
        sys.exit()
    image = pygame.image.load(fullname)
    return image


def load_level(name):
    fullname = os.path.join('data', name)
    if not os.path.isfile(fullname):
        print(f"Файл уровня '{fullname}' не найден")
        sys.exit()
    with open(fullname, 'r') as mapFile:
        level_map = [line.strip() for line in mapFile]
        level_height = len(level_map)
        level_width = len(level_map[0])
    return level_map, level_width, level_height


def crop_pusheen():
    for name in ['pusheen_gray_1.png', 'pusheen_gray_2.png', 'pusheen_pink_1.png',
                 'pusheen_pink_2.png', 'pusheen_green_1.png', 'pusheen_green_2.png']:
        fullname = os.path.join('data', name)
        if not os.path.isfile(fullname):
            print(f"Файл с изображением '{fullname}' не найден")
            sys.exit()
        image = Image.open(fullname)
        image = image.crop((450, 685, 2505, 1900))
        image.save(fullname)


def terminate():
    pygame.quit()
    sys.exit()


class Particle(pygame.sprite.Sprite):
    particles = [load_image("star.png")]
    for scale in (5, 10, 20):
        particles.append(pygame.transform.scale(particles[0], (scale, scale)))

    def __init__(self, pos, dx, dy):
        super().__init__(all_sprites)
        self.image = random.choice(self.particles)
        self.rect = self.image.get_rect()
        self.velocity = [dx, dy]
        self.rect.x, self.rect.y = pos
        self.gravity = GRAVITY

    def update(self):
        self.velocity[1] += self.gravity
        self.rect.x += self.velocity[0]
        self.rect.y += self.velocity[1]
        if not is_inside(self.rect.x, self.rect.y):
            self.kill()


def create_particles(position):
    particle_count = 20
    numbers = range(-5, 6)
    for _ in range(particle_count):
        Particle(position, random.choice(numbers), random.choice(numbers))


def level_result(win):
    image = pygame.transform.scale(load_image(['lose.jpg', 'win.jpg'][win]), (WIDTH, HEIGHT))
    screen.blit(image, (0, 0))
    while True:
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                terminate()
            if event.type == pygame.KEYDOWN:
                main_screen()
        pygame.display.flip()
        clock.tick(FPS)


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
                                       MINIGAMEY + MINIGAMEHEIGHT - self.rect.height)
        while pygame.sprite.spritecollideany(self, math_sprites):
            self.rect = self.image.get_rect()
            self.rect.x = random.randrange(MINIGAMEX + self.rect.width,
                                           MINIGAMEX + MINIGAMEWIDTH - self.rect.width)
            self.rect.y = random.randrange(MINIGAMEY + self.rect.height,
                                           MINIGAMEY + MINIGAMEHEIGHT - self.rect.height)
        font = pygame.font.Font(None, 20)
        text = font.render(str(number), True, (0, 0, 0))
        text_x = (self.rect.width - text.get_width()) // 2
        text_y = (self.rect.height - text.get_height()) // 2
        pygame.draw.circle(self.image, self.color, (self.radius, self.radius), self.radius)
        self.image.blit(text, (text_x, text_y))
        math_sprites.add(self)

    def update(self, event):
        if self.rect.collidepoint(event.pos):
            if self.is_prime:
                self.kill()
                if self.parent.check_win():
                    level_result(1)
            else:
                self.image = self.image_boom
                self.parent.draw_background()
                math_sprites.draw(screen)
                pygame.display.flip()
                pygame.time.delay(1000)
                level_result(0)


class EnglishWord(pygame.sprite.Sprite):
    def __init__(self, parent, i, j, word, synonym):
        super().__init__()
        self.parent = parent
        self.width = 100
        self.word = word
        self.synonym = synonym
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
        text = font.render(self.word, True, (0, 0, 0))
        text_x = (self.rect.width - text.get_width()) // 2
        text_y = (self.rect.height - text.get_height()) // 2
        pygame.draw.rect(self.image, color, (0, 0, self.width, self.height))
        self.image.blit(text, (text_x, text_y))

    def update(self, event):
        global prev
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
                    if not english_sprites:
                        level_result(1)
                elif self.parent.prev.word != self.word:
                    self.redraw((255, 0, 0))
                    self.parent.prev.redraw((255, 0, 0))
                    english_sprites.draw(screen)
                    pygame.display.flip()
                    pygame.time.delay(1000)
                    level_result(0)
                self.parent.prev = None
            else:
                self.parent.prev = self


class ICTNumber(pygame.sprite.Sprite):
    def __init__(self, parent, i, number):
        super().__init__()
        self.width = 55
        self.height = 120
        self.number = number
        self.parent = parent
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
        global prev
        if self.rect.collidepoint(event.pos):
            self.number ^= 1
            self.redraw((0, 255, 0))
            if self.parent.check_win():
                ict_sprites.draw(screen)
                pygame.display.flip()
                pygame.time.delay(1000)
                level_result(1)


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

    def is_prime(self, n):
        for i in range(2, int(n ** 0.5) + 1):
            if n % i == 0:
                return False
        return True

    def check_win(self):
        for sprite in math_sprites:
            if sprite.is_prime:
                return False
        return True

    def draw_background(self):
        pygame.draw.rect(screen, pygame.Color(75, 20, 130),
                         (MINIGAMEX, MINIGAMEY, MINIGAMEWIDTH, MINIGAMEHEIGHT))


class ICTMiniGame:
    def __init__(self):
        self.number = random.randint(0, 256)
        for i in range(8):
            ict_number = ICTNumber(self, i, 0)

    def check_win(self):
        res = ''.join(str(sprite.number) for sprite in ict_sprites)
        return int(res, 2) == self.number

    def draw_background(self):
        pygame.draw.rect(screen, pygame.Color(75, 20, 130), (MINIGAMEX, MINIGAMEY, MINIGAMEWIDTH, MINIGAMEHEIGHT))
        font = pygame.font.Font(None, 50)
        text = font.render(str(self.number), True, (255, 255, 255))
        screen.blit(text, (MINIGAMEX + (MINIGAMEWIDTH - text.get_width()) // 2, MINIGAMEY + 10))


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

    def draw_background(self):
        pygame.draw.rect(screen, pygame.Color(75, 20, 130),
                         (MINIGAMEX, MINIGAMEY, MINIGAMEWIDTH, MINIGAMEHEIGHT))


def mini_game(subject):
    if subject == 'maths':
        global math_sprites
        math_sprites = sprites = pygame.sprite.Group()
        game = MathMiniGame()
    elif subject == 'english':
        global english_sprites
        sprites = english_sprites = pygame.sprite.Group()
        prev = None
        game = EnglishMiniGame()
    elif subject == 'ict':
        global ict_sprites
        sprites = ict_sprites = pygame.sprite.Group()
        game = ICTMiniGame()
    while True:
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                terminate()
            if event.type == pygame.MOUSEBUTTONDOWN:
                sprites.update(event)
        game.draw_background()
        sprites.draw(screen)
        pygame.display.flip()
        clock.tick(FPS)


class Pusheen(pygame.sprite.Sprite):
    def __init__(self, pos_x, pos_y, image):
        super().__init__(all_sprites)
        name, extension = image.split('.')
        image_1 = pygame.transform.scale(load_image(f'{name}_1.{extension}'), (CELLWIDTH, CELLHEIGHT))
        image_2 = pygame.transform.scale(load_image(f'{name}_2.{extension}'), (CELLWIDTH, CELLHEIGHT))
        self.images = [image_1, image_2]
        self.cur = 0
        self.redraw()
        self.rect = self.image.get_rect()
        self.rect.x, self.rect.y = CELLWIDTH * pos_x, CELLHEIGHT * pos_y
        self.direction = 1
        self.visited_sofas = list()
        self.jump_flag = False
        self.can_move = True
        self.jump_count = 0
        self.speed = 7

    def move(self):
        pressed = pygame.key.get_pressed()
        if pressed[pygame.K_RIGHT]:
            if not self.collision('midright', tile_sprites):
                if self.direction != 1:
                    self.images = [pygame.transform.flip(im, True, False) for im in self.images]
                    self.direction = 1
                self.rect.x += self.speed
        if pressed[pygame.K_LEFT]:
            if not self.collision('midleft', tile_sprites):
                if self.direction != -1:
                    self.images = [pygame.transform.flip(im, True, False) for im in self.images]
                    self.direction = -1
                self.rect.x -= self.speed
        if (pressed[pygame.K_UP] or pressed[pygame.K_SPACE]) and not self.jump_flag:
            self.jump_flag = True
            self.jump_count = JUMPS
        if self.jump_flag:
            if self.jump_count >= 0 or self.jump_count < 0 and not self.collision('midbottom', tile_sprites):
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
        sofa = pygame.sprite.spritecollideany(self, sofa_sprites)
        if self.collision('midbottom', sofa_sprites) and sofa not in self.visited_sofas:
            self.visited_sofas.append(sofa)
            self.images = [pygame.transform.flip(im, False, True) for im in self.images]
            self.can_move = False
            pygame.time.set_timer(RECOVER, 3000, True)
        donut = pygame.sprite.spritecollideany(self, donut_sprites)
        door = pygame.sprite.spritecollideany(self, door_sprites)
        if donut:
            donut.kill()
        if door:
            mini_game(cur_level)
            
    def recover_from_sofa(self):
        self.can_move = True
        self.images = [pygame.transform.flip(im, False, True) for im in self.images]

    def collision(self, point, group):
        return any(tile.rect.collidepoint(getattr(self.rect, point)) for tile in group)

    def redraw(self):
        self.cur ^= 1
        self.image = self.images[self.cur]


class Button(pygame.sprite.Sprite):
    def __init__(self, pos, width, height, image, clicked_image, group=None):
        super().__init__(button_sprites)
        self.name = image
        self.main_image = pygame.transform.scale(load_image(image), (width, height))
        self.clicked_image = pygame.transform.scale(load_image(clicked_image), (width, height))
        self.image = self.main_image
        self.rect = self.image.get_rect()
        self.rect.x, self.rect.y = pos
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


class Tile(pygame.sprite.Sprite):
    def __init__(self, tile_type, pos_x, pos_y):
        super().__init__(all_sprites, *tile_groups[tile_type])
        self.image = pygame.transform.scale(tile_images[tile_type], (CELLWIDTH, CELLHEIGHT))
        self.rect = self.image.get_rect().move(CELLWIDTH * pos_x, CELLHEIGHT * pos_y)


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


def start_screen():
    start_image = pygame.transform.scale(load_image('start_screen.jpg'), (WIDTH, HEIGHT))
    button1 = Button((170, 300), 200, 130, 'pusheen_gray_1.png', 'pusheen_gray_2.png', group=PUSHEEN)
    button2 = Button((470, 300), 200, 130, 'pusheen_pink_1.png', 'pusheen_pink_2.png', group=PUSHEEN)
    button3 = Button((770, 300), 200, 130, 'pusheen_green_1.png', 'pusheen_green_2.png', group=PUSHEEN)
    ok_button = Button(((WIDTH - 100) // 2, 500), 100, 50, 'ok.png', 'ok.png')
    while True:
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                terminate()
            elif event.type == pygame.MOUSEBUTTONDOWN:
                button_sprites.update(event)
                if ok_button.clicked:
                    return 0
        screen.blit(start_image, (0, 0))
        button_sprites.draw(screen)
        pygame.display.flip()
        clock.tick(FPS)


def main_screen():
    # pygame.mixer.music.play(-1)
    pusheen_name = 'pusheen_gray.png'
    for button in button_sprites:
        if button.clicked and button.group == PUSHEEN:
            pusheen_name = button.name[:-6] + button.name[-4:]
    level_map, level_width, level_height = load_level('map.txt')
    pusheen_x, pusheen_y = generate_level(level_map)
    pusheen = Pusheen(pusheen_x, pusheen_y, pusheen_name)
    pygame.time.set_timer(UPDATEPUSHEEN, 200)
    pygame.display.flip()
    while True:
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                terminate()
            if event.type == UPDATEPUSHEEN:
                pusheen.redraw()
            if event.type == RECOVER:
                pusheen.recover_from_sofa()
        camera.update(pusheen)
        for sprite in all_sprites:
            camera.apply(sprite)
        screen.fill((0, 0, 0))
        if pusheen.can_move:
            pusheen.move()
        all_sprites.draw(screen)
        pygame.display.flip()
        clock.tick(FPS)


def final_screen():
    pygame.mixer.music.stop()
    pygame.time.set_timer(UPDATESTARS, 100)
    while True:
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                terminate()
            if event.type == UPDATESTARS:
                create_particles((random.randint(0, WIDTH), random.randint(0, 3 * HEIGHT // 4)))
        all_sprites.update()
        screen.fill((0, 0, 0))
        all_sprites.draw(screen)
        pygame.display.flip()
        clock.tick(FPS)


pygame.init()
info = pygame.display.Info()
SIZE = WIDTH, HEIGHT = info.current_w - 200, 5 * CELLHEIGHT
MINIGAMEWIDTH = 500
MINIGAMEHEIGHT = 500
MINIGAMEX = (WIDTH - MINIGAMEWIDTH) // 2
MINIGAMEY = (HEIGHT - MINIGAMEHEIGHT) // 2
screen = pygame.display.set_mode(SIZE)
clock = pygame.time.Clock()
pygame.mixer.music.load('data/pusheen_music.mp3')
cur_level = 'english'
all_sprites = pygame.sprite.Group()
tile_sprites = pygame.sprite.Group()
sofa_sprites = pygame.sprite.Group()
donut_sprites = pygame.sprite.Group()
door_sprites = pygame.sprite.Group()
button_sprites = pygame.sprite.Group()
tile_images = {
    'sofa': load_image('sofa.png'),
    'ground': load_image('ground.png'),
    'donut': load_image('donut.png'),
    'door': load_image('door.png')
}
tile_groups = {
    'sofa': [tile_sprites, sofa_sprites],
    'ground': [tile_sprites],
    'donut': [donut_sprites],
    'door': [door_sprites]
}
camera = Camera()
start_screen()
main_screen()
