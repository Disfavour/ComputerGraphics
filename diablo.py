import math
import os
import pygame
import random
import pathlib
import sys


# number of rooms per level
NUMBER_OF_ROOMS_MIN = 20
NUMBER_OF_ROOMS_MAX = 23

# number of enemies per room
ENEMY_COUNT_MIN = 3
ENEMY_COUNT_MAX = 5

# number of levels
MAX_LEVEL = 2

PROGRAM_PATH = pathlib.Path(__file__).parent.absolute()
TXT_MAP_SIZE = 15
GLOBAL_MAP_SIZE = 7

# colors
WHITE = (255, 255, 255)
BLACK = (0, 0, 0)
GRAY = (125, 125, 125)
LIGHT_BLUE = (64, 128, 255)
GREEN = (0, 200, 64)
YELLOW = (225, 225, 0)
PINK = (230, 50, 230)
RED = (255, 0, 0)


def load_image(name, colorkey=None):
    fullname = os.path.join(PROGRAM_PATH, "data", "images", name)
    image = pygame.image.load(fullname)
    if colorkey is None:
        image = image.convert()
    # True - удаляем фон
    elif colorkey:
        image = image.convert()
        colorkey = image.get_at((0, 0))
        image.set_colorkey(colorkey)
    # пустые пиксели False
    else:
        image.convert_alpha()
    return image


def load_level(level):
    with open(os.path.join(PROGRAM_PATH, "data", "levels", level), 'r') as file:
        level_map = [list(line.strip()) for line in file]
    return level_map


class Menu:
    def __init__(self):
        self.in_menu = True
        self.run_menu()

    def draw_menu(self):
        pygame.mouse.set_visible(True)
        screen.fill(BLACK)

        screen.blit(menu_background, (0, 0))

        font = pygame.font.Font(None, 250)
        label = font.render("Diablo pre Alpha 0.1", True, WHITE)
        label_rect = label.get_rect(center=(width // 2, 200))

        font = pygame.font.Font(None, 200)
        button_start = font.render("Play", True, BLACK, WHITE)
        self.button_start_rect = button_start.get_rect(center=(width // 2, 500))

        button_quit = font.render("Quit", True, BLACK, WHITE)
        self.button_quit_rect = button_quit.get_rect(center=(width // 2, 900))

        screen.blit(label, label_rect)

        pygame.draw.rect(screen, RED, self.button_start_rect, 20)
        screen.blit(button_start, self.button_start_rect)

        pygame.draw.rect(screen, RED, self.button_quit_rect, 20)
        screen.blit(button_quit, self.button_quit_rect)

        pygame.display.update()

    def run_menu(self):
        global in_game
        self.draw_menu()
        while self.in_menu:
            for event in pygame.event.get():
                if event.type == pygame.QUIT:
                    self.in_menu = False

            pressed = pygame.mouse.get_pressed()
            pos = pygame.mouse.get_pos()
            if pressed[0]:
                if self.button_start_rect.collidepoint(pos):
                    self.in_menu = False
                    in_game = True
                elif self.button_quit_rect.collidepoint(pos):
                    self.in_menu = False

            clock.tick(fps)


def death_anim():
    global dead, player
    alpha = 255
    screen_sprite_group = pygame.sprite.Group()
    screen_sprite = pygame.sprite.Sprite(screen_sprite_group)

    image = load_image('screen.png')
    font = pygame.font.Font(None, 400)
    label = font.render("Dead", True, RED)
    label_rect = label.get_rect(center=(width // 2, height // 2))
    image.blit(label, label_rect)

    screen_sprite.image = image
    screen_sprite.rect = screen_sprite.image.get_rect()

    while dead:
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                sys.exit()
        screen.fill(WHITE)
        screen_sprite.image.set_alpha(alpha)
        screen_sprite_group.draw(screen)
        pygame.display.update()

        clock.tick(fps)

        if alpha <= 0:
            player.gun.kill()
            player.kill()
            dead = False
            menu.in_menu = True
        alpha -= 1.5


def next_level_anim():
    next_level = True
    alpha = 255
    screen_sprite_group = pygame.sprite.Group()
    screen_sprite = pygame.sprite.Sprite(screen_sprite_group)

    image = load_image('screen.png')
    font = pygame.font.Font(None, 400)
    label = font.render("Next level", True, RED)
    label_rect = label.get_rect(center=(width // 2, height // 2))
    image.blit(label, label_rect)

    screen_sprite.image = image
    screen_sprite.rect = screen_sprite.image.get_rect()

    while next_level:
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                sys.exit()
        screen.fill(WHITE)
        screen_sprite.image.set_alpha(alpha)
        screen_sprite_group.draw(screen)
        pygame.display.update()

        clock.tick(fps)

        if alpha <= 0:
            next_level = False
        alpha -= 3


def run_finish():
    global in_game
    finish = True
    alpha = 255
    screen_sprite_group = pygame.sprite.Group()
    screen_sprite = pygame.sprite.Sprite(screen_sprite_group)

    image = load_image('screen.png')

    font = pygame.font.Font(None, 400)
    label = font.render("Finish", True, RED)
    label_rect = label.get_rect(center=(width // 2, height // 2))
    image.blit(label, label_rect)

    screen_sprite.image = image
    screen_sprite.rect = screen_sprite.image.get_rect()
    while finish:
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                sys.exit()
        screen.fill(WHITE)
        screen_sprite.image.set_alpha(alpha)
        screen_sprite_group.draw(screen)
        pygame.display.update()

        clock.tick(fps)

        if alpha <= 0:
            player.gun.kill()
            player.kill()
            in_game = False
            menu.in_menu = True
            finish = False
        alpha -= 1.5

        clock.tick(fps)


def run_game():
    global screen, in_game, dead, floor
    floor = 0
    mouse_pos = (0, 0)
    camera = Camera()
    generate_map()
    pygame.mouse.set_visible(False)
    damage_timer = 0

    # pygame.key.set_repeat(10, 1)
    shoot_timer = 0
    shooting = False
    while in_game:
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                in_game = False

            # mouse
            elif event.type == pygame.MOUSEBUTTONDOWN and event.button == 1:
                shooting = True
            elif event.type == pygame.MOUSEBUTTONUP and event.button == 1:
                shooting = False
            elif event.type == pygame.MOUSEMOTION:
                mouse_pos = event.pos
                player.gun.rotate()

        # keyboard
        keys = pygame.key.get_pressed()

        # right
        if keys[pygame.K_RIGHT] or keys[pygame.K_d]:
            player.move(0, 1)
            if pygame.sprite.spritecollideany(player.hitbox, walls_group):
                player.move(0, -1)
            if player.walk_cycle < 10:
                player.image = load_image('player.png', True)
            else:
                player.image = load_image('player_2.png', True)

            player.walk_cycle = (player.walk_cycle + 1) % 20
            player.direction = 'right'

        # left
        elif keys[pygame.K_LEFT] or keys[pygame.K_a]:
            player.move(0, -1)
            if pygame.sprite.spritecollideany(player.hitbox, walls_group):
                player.move(0, 1)
            if player.walk_cycle < 10:
                player.image = load_image('player_left.png', True)
            else:
                player.image = load_image('player_left_2.png', True)

            player.walk_cycle = (player.walk_cycle + 1) % 20
            player.direction = 'left'

        # up
        elif keys[pygame.K_UP] or keys[pygame.K_w]:
            player.move(1, -1)
            if pygame.sprite.spritecollideany(player.hitbox, walls_group):
                player.move(1, 1)
            if player.walk_cycle < 10:
                player.image = load_image('player_back.png', True)
            else:
                player.image = load_image('player_back_2.png', True)

            player.walk_cycle = (player.walk_cycle + 1) % 20
            player.direction = 'up'

        # down
        elif keys[pygame.K_DOWN] or keys[pygame.K_s]:
            player.move(1, 1)
            if pygame.sprite.spritecollideany(player.hitbox, walls_group):
                player.move(1, -1)
            if player.walk_cycle < 10:
                player.image = load_image('player_front.png', True)
            else:
                player.image = load_image('player_front_2.png', True)

            player.walk_cycle = (player.walk_cycle + 1) % 20
            player.direction = 'down'

        # ESC
        elif keys[pygame.K_ESCAPE]:
            pygame.image.save(screen, os.path.join(PROGRAM_PATH, "data", "images", "screen.png"))
            run_escape()

        # Inventory
        elif keys[pygame.K_i]:
            pygame.image.save(screen, os.path.join(PROGRAM_PATH, "data", "images", "screen.png"))
            run_inventory()

        # New level
        if pygame.sprite.spritecollideany(player.hitbox, hole_group):
            if floor == MAX_LEVEL:
                pygame.image.save(screen, os.path.join(PROGRAM_PATH, "data", "images", "screen.png"))
                run_finish()

            else:
                pygame.image.save(screen, os.path.join(PROGRAM_PATH, "data", "images", "screen.png"))
                next_level_anim()

            hp = player.hp
            gun = player.gun
            generate_map()

            player.hp = hp
            player.gun = gun

        rx, ry = player.room[0], player.room[1]
        if level_map[ry][rx] != '' and not player.in_corridor:
            if level_map[ry][rx][2] == 'full':
                level_map[ry][rx][2] = 'running'
                for sprite in level_map[ry][rx][3]:
                    sprite.update()
            elif level_map[ry][rx][2] == 'running' and level_map[ry][rx][1] == 0:
                level_map[ry][rx][2] = 'cleared'
                for sprite in level_map[ry][rx][3]:
                    sprite.update()

        if shooting and shoot_timer == 0:
            player.gun.shoot(mouse_pos)
            shoot_timer = player.gun.gap

        camera.update(player)
        for sprite in all_sprites:
            camera.apply(sprite)
        font = pygame.font.Font(None, 100)

        clock.tick(fps)

        screen.fill(BLACK)
        tiles_group.draw(screen)
        temp_walls_group.draw(screen)
        dead_group.update()
        enemy_group.update()
        bullet_group.update()

        # Projectile
        collide = pygame.sprite.groupcollide(bullet_group, enemy_group, True, False)
        for i in range(len(collide)):
            keys = list(collide.keys())
            damage = keys[i].damage
            for j in collide[keys[i]]:
                if not player.in_corridor:
                    GoldText(j.rect.left, j.rect.top, min(damage, j.hp))
                    j.hp -= damage
                if j.hp <= 0 and not j.killed:
                    level_map[ry][rx][1] -= 1
                    j.killed = True

        enemy_group.draw(screen)
        dead_group.draw(screen)
        if player.direction == 'up':
            gun_group.draw(screen)
            player_group.draw(screen)
        else:
            player_group.draw(screen)
            gun_group.draw(screen)
        pygame.sprite.groupcollide(bullet_group, walls_group, True, False)
        pygame.sprite.groupcollide(bullet_group, bullet_stopper_group, True, False)
        bullet_group.draw(screen)

        level_label = font.render("level " + str(floor), True, RED)
        level_label_rect = level_label.get_rect(bottomright=(width - 20, level_label.get_height() + 20))
        screen.blit(level_label, level_label_rect) #(1730, 20))

        # enemy damage
        if pygame.sprite.spritecollideany(player.hitbox, enemy_group) and damage_timer == 0:
            player.hp -= 1
            damage_timer = fps

        # gold text
        gold_text_group.update()
        gold_text_group.draw(screen)

        n = 20
        for i in range(player.hp):
            screen.blit(heart, (n, 20))
            n += heart_rect.width + 20

        # HP < 0
        if player.hp <= 0:
            pygame.image.save(screen, os.path.join(PROGRAM_PATH, "data", "images", "screen.png"))
            in_game = False
            dead = True
        screen.blit(arrow, mouse_pos)
        pygame.display.update()

        if damage_timer > 0:
            damage_timer -= 1
        if shoot_timer > 0:
            shoot_timer -= 1


class Camera:
    def __init__(self):
        self.dx = 0
        self.dy = 0

    def apply(self, obj):
        obj.rect.x = obj.rect.x + self.dx
        obj.rect.y = obj.rect.y + self.dy
        if type(obj) in [Enemy, Bullet]:
            obj.sx += self.dx
            obj.sy += self.dy

    def update(self, target):
        self.dx = -(target.rect.x + target.rect.w // 2 - width // 2)
        self.dy = -(target.rect.y + target.rect.h // 2 - height // 2)


def generate_map():
    global floor
    reset_groups()
    draw_level()
    floor += 1


def reset_groups():
    tiles_group.empty()
    player_group.empty()
    walls_group.empty()
    all_sprites.empty()
    hole_group.empty()
    bullet_group.empty()
    enemy_group.empty()
    dead_group.empty()
    bullet_stopper_group.empty()
    temp_walls_group.empty()
    gold_text_group.empty()


def draw_room(level, i, j, t):
    global player, sig
    if t == 'room':
        ax = 0
        ay = 0
    elif t == 'hor':
        ax = 15
        ay = 5
    else:
        ax = 5
        ay = 15
    # range(TXT_MAP_SIZE)
    for y in range(len(level)):
        for x in range(len(level[0])):
            if level[x][y] == '.':
                Tile('empty', x + j * 20 + ax, y + i * 20 + ay)
            elif level[x][y] == '#':
                Wall('wall', x + j * 20 + ax, y + i * 20 + ay)
            elif level[x][y] == '@':
                Tile('empty', x + j * 20, y + i * 20)
                player = Player(x + j * 20, y + i * 20)
            elif level[x][y] == '$':
                Hole('hole', x + j * 20, y + i * 20)
            elif level[x][y] == '%':
                Tile('empty', x + j * 20, y + i * 20)
                Enemy(x + j * 20, y + i * 20)
            elif level[x][y] == ':':
                level_map[i][j][3].append(TempWall(x + j * 20, y + i * 20))


def draw_level():
    global level_map
    k = random.randint(NUMBER_OF_ROOMS_MIN, NUMBER_OF_ROOMS_MAX)
    names = random.choices(level_names, k=k)
    level_map = [["" for i in range(GLOBAL_MAP_SIZE)] for j in range(GLOBAL_MAP_SIZE)]

    level_map[(GLOBAL_MAP_SIZE - 1) // 2][(GLOBAL_MAP_SIZE - 1) // 2] = 'start'
    names.append('end')

    # real rooms + end = k + 1
    n = 0
    while n <= k:
        x = random.randint(1, GLOBAL_MAP_SIZE - 2)
        y = random.randint(1, GLOBAL_MAP_SIZE - 2)
        if any([level_map[y + 1][x] != '', level_map[y - 1][x] != '', level_map[y][x + 1] != '',
                level_map[y][x - 1] != '']) and level_map[y][x] == '':
            level_map[y][x] = names[n]
            n += 1

    hor = load_level('hor_corridor.txt')
    vert = load_level('vert_corridor.txt')

    for i in range(GLOBAL_MAP_SIZE):
        for j in range(GLOBAL_MAP_SIZE):
            if level_map[i][j] != '':
                with_enemy = level_map[i][j] not in ['start', 'end']
                level = load_level(level_map[i][j] + '.txt')

                # random position and number of enemy
                if with_enemy:
                    enemy_count = random.randint(ENEMY_COUNT_MIN, ENEMY_COUNT_MAX)
                    level_map[i][j] = [level_map[i][j], enemy_count, 'full', []]
                    while enemy_count > 0:
                        x = random.randint(1, TXT_MAP_SIZE - 1)
                        y = random.randint(1, TXT_MAP_SIZE - 1)
                        if level[x][y] == '.' and enemies_allowed[x][y]:
                            level[x][y] = '%'
                            enemy_count -= 1
                else:
                    level_map[i][j] = [level_map[i][j], 0, 'main', []]

                # tempwall
                symb = ':' if with_enemy else '.'

                # bot
                if level_map[i + 1][j] != "":
                    level[(TXT_MAP_SIZE - 1) // 2 - 1][TXT_MAP_SIZE - 1] = symb
                    level[(TXT_MAP_SIZE - 1) // 2][TXT_MAP_SIZE - 1] = symb
                    level[(TXT_MAP_SIZE - 1) // 2 + 1][TXT_MAP_SIZE - 1] = symb
                    draw_room(hor, i, j, "vert")
                # top
                if level_map[i - 1][j] != "":
                    level[(TXT_MAP_SIZE - 1) // 2 - 1][0] = symb
                    level[(TXT_MAP_SIZE - 1) // 2][0] = symb
                    level[(TXT_MAP_SIZE - 1) // 2 + 1][0] = symb
                # right
                if level_map[i][j + 1] != "":
                    level[TXT_MAP_SIZE - 1][(TXT_MAP_SIZE - 1) // 2 - 1] = symb
                    level[TXT_MAP_SIZE - 1][(TXT_MAP_SIZE - 1) // 2] = symb
                    level[TXT_MAP_SIZE - 1][(TXT_MAP_SIZE - 1) // 2 + 1] = symb
                    draw_room(vert, i, j, "hor")
                # left
                if level_map[i][j - 1] != "":
                    level[0][(TXT_MAP_SIZE - 1) // 2 - 1] = symb
                    level[0][(TXT_MAP_SIZE - 1) // 2] = symb
                    level[0][(TXT_MAP_SIZE - 1) // 2 + 1] = symb
                draw_room(level, i, j, "room")


def run_escape():
    global in_game
    in_pause = True
    image = load_image('screen.png')

    pygame.mouse.set_visible(True)
    screen.fill(BLACK)
    screen.blit(image, (0, 0))

    font = pygame.font.Font(None, 250)
    label = font.render("Pause", True, WHITE)
    label_rect = label.get_rect(center=(width // 2, 200))

    font = pygame.font.Font(None, 200)
    button_continue = font.render("Continue", True, BLACK, WHITE)
    button_continue_rect = button_continue.get_rect(center=(width // 2, 500))

    button_quit = font.render("Quit to menu", True, BLACK, WHITE)
    button_quit_rect = button_quit.get_rect(center=(width // 2, 700))

    screen.blit(label, label_rect)

    pygame.draw.rect(screen, RED, button_continue_rect, 20)
    screen.blit(button_continue, button_continue_rect)

    pygame.draw.rect(screen, RED, button_quit_rect, 20)
    screen.blit(button_quit, button_quit_rect)

    pygame.display.update()

    while in_pause:
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                in_pause = False
                in_game = False

        pressed = pygame.mouse.get_pressed()
        pos = pygame.mouse.get_pos()

        if pressed[0]:
            if button_continue_rect.collidepoint(pos):
                pygame.mouse.set_visible(False)
                in_pause = False

            elif button_quit_rect.collidepoint(pos):
                player.gun.kill()
                player.kill()
                in_pause = False
                in_game = False
                menu.in_menu = True

        clock.tick(fps)


def run_inventory():
    global in_game
    in_inventory = True
    image = load_image('screen.png')

    pistol = load_image("pistol.png")
    pistol_rect = pistol.get_rect(center=(5 * width // 12, 5 * height // 12))

    uzi = load_image("uzi.png")
    uzi_rect = uzi.get_rect(center=(7 * width // 12, 5 * height // 12))

    minigun = load_image("minigun.png")
    minigun_rect = minigun.get_rect(center=(5 * width // 12, 7 * height // 12))

    shotgun = load_image("shotgun.png")
    shotgun_rect = shotgun.get_rect(center=(7 * width // 12, 7 * height // 12))

    pygame.mouse.set_visible(True)
    screen.fill(BLACK)
    screen.blit(image, (0, 0))

    font = pygame.font.Font(None, 250)
    label = font.render("Inventory", True, WHITE)
    label_rect = label.get_rect(center=(width // 2, 200))

    font = pygame.font.Font(None, 200)
    button_continue = font.render("Continue", True, BLACK, WHITE)
    button_continue_rect = button_continue.get_rect(center=(width // 2, 900))

    screen.blit(label, label_rect)

    pygame.draw.rect(screen, WHITE, (width // 3, height // 3, width // 3, height // 3))

    pygame.draw.rect(screen, RED, button_continue_rect, 20)
    screen.blit(button_continue, button_continue_rect)

    pygame.draw.rect(screen, RED, pistol_rect, 20)
    screen.blit(pistol, pistol_rect)

    pygame.draw.rect(screen, RED, uzi_rect, 20)
    screen.blit(uzi, uzi_rect)

    pygame.draw.rect(screen, RED, minigun_rect, 20)
    screen.blit(minigun, minigun_rect)

    pygame.draw.rect(screen, RED, shotgun_rect, 20)
    screen.blit(shotgun, shotgun_rect)

    pygame.display.update()

    while in_inventory:
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                sys.exit()

        pressed = pygame.mouse.get_pressed()
        pos = pygame.mouse.get_pos()

        if pressed[0]:
            if button_continue_rect.collidepoint(pos):
                pygame.mouse.set_visible(False)
                in_inventory = False
            elif pistol_rect.collidepoint(pos):
                player.gun.kill()
                player.gun = Pistol(player.rect.left, player.rect.top)
                pygame.mouse.set_visible(False)
                in_inventory = False
            elif uzi_rect.collidepoint(pos):
                player.gun.kill()
                player.gun = Uzi(player.rect.left, player.rect.top)
                pygame.mouse.set_visible(False)
                in_inventory = False
            elif minigun_rect.collidepoint(pos):
                player.gun.kill()
                player.gun = Minigun(player.rect.left, player.rect.top)
                pygame.mouse.set_visible(False)
                in_inventory = False
            elif shotgun_rect.collidepoint(pos):
                player.gun.kill()
                player.gun = Shotgun(player.rect.left, player.rect.top)
                pygame.mouse.set_visible(False)
                in_inventory = False

        clock.tick(fps)


class Enemy(pygame.sprite.Sprite):
    def __init__(self, pos_x, pos_y):
        super().__init__(enemy_group, all_sprites)
        self.image = load_image('slime.png', True)
        self.rect = self.image.get_rect().move(tile_width * pos_x, tile_height * pos_y)
        self.direction = 'right'
        self.walk_cycle = 0
        self.v = 1.5
        self.sx, self.sy = self.rect.center
        self.hp = 20 + floor * 10
        self.room = [pos_x // 20, pos_y // 20]
        self.a = 256
        self.killed = False

    def update(self):
        if self.hp > 0:
            if self.room == player.room and not player.in_corridor:
                x, y = player.rect.center
                g = ((x - self.sx) ** 2 + (self.sy - y) ** 2) ** 0.5
                if g != 0:
                    vx = (x - self.sx) / g * self.v
                    vy = (y - self.sy) / g * self.v
                else:
                    vx, vy = 0, 0
                self.sx, self.sy = self.sx + vx, self.sy + vy
                self.rect.center = (self.sx, self.sy)
                if pygame.sprite.spritecollideany(self, walls_group):
                    fvx = self.v if vx >= 0 else -self.v
                    fvy = self.v if vy >= 0 else -self.v
                    self.sx = self.sx - vx
                    self.sy = self.sy - vy + fvy
                    self.rect.center = (self.sx, self.sy)
                    if pygame.sprite.spritecollideany(self, walls_group):
                        self.sx, self.sy = self.sx + fvx, self.sy - fvy
                        self.rect.center = (self.sx, self.sy)
                        if pygame.sprite.spritecollideany(self, walls_group):
                            self.sx = self.sx - fvx
                            self.rect.center = (self.sx, self.sy)
        else:
            if self.a == 256:
                enemy_group.remove(self)
                dead_group.add(self)

            if self.a > 0:
                self.a -= 5
                self.image.set_alpha(self.a)
            else:
                self.kill()


class GoldText(pygame.sprite.Sprite):
    def __init__(self, x, y, damage):
        super().__init__(gold_text_group, all_sprites)
        self.image = pygame.font.Font(None, 40).render(str(damage), True, YELLOW)
        self.rect = self.image.get_rect().move(x + 7, y - 30)
        self.x = 0

    def update(self):
        self.rect.top -= 1
        self.x += 1
        if self.x > 70:
            self.kill()


class Bullet(pygame.sprite.Sprite):
    def __init__(self, x, y, v, damage, uni):
        super().__init__(bullet_group, all_sprites)
        self.x = player.rect.left + 55
        self.y = player.rect.top + 40
        rx = x - self.x
        ry = y - self.y
        angle = (180 / math.pi) * math.atan2(rx, ry)
        angle = random.uniform(angle - 180 / uni, angle + 180 / uni)
        self.vx = math.sin(angle / 180 * math.pi) * v
        self.vy = math.cos(angle / 180 * math.pi) * v
        self.damage = damage
        self.image = load_image('pistol_bullet.png', True)
        self.rect = self.image.get_rect().move(self.x, self.y)
        self.sx, self.sy = self.rect.center

        self.image = pygame.transform.flip(self.image, False, True)
        self.image = pygame.transform.rotate(self.image, int(angle))

    def update(self):
        self.sx = self.sx + self.vx
        self.sy = self.sy + self.vy
        self.rect.left = self.sx
        self.rect.top = self.sy


class Tile(pygame.sprite.Sprite):
    def __init__(self, tile_type, pos_x, pos_y):
        super().__init__(tiles_group, all_sprites)
        self.image = tile_images[tile_type]
        self.rect = self.image.get_rect().move(tile_width * pos_x, tile_height * pos_y)


class Wall(pygame.sprite.Sprite):
    def __init__(self, tile_type, pos_x, pos_y):
        super().__init__(tiles_group, all_sprites, walls_group)
        self.image = tile_images[tile_type]
        self.rect = self.image.get_rect().move(tile_width * pos_x, tile_height * pos_y)


class TempWall(pygame.sprite.Sprite):
    def __init__(self, pos_x, pos_y):
        super().__init__(tiles_group, all_sprites, bullet_stopper_group)
        self.image = tile_images['empty']
        self.rect = self.image.get_rect().move(tile_width * pos_x, tile_height * pos_y)
        self.cond = 0

    def update(self):
        self.cond += 1
        if self.cond == 1:
            self.image = tile_images['wall']
            bullet_stopper_group.remove(self)
            walls_group.add(self)
        elif self.cond == 2:
            self.image = tile_images['empty']
            walls_group.remove(self)


class Hole(pygame.sprite.Sprite):
    def __init__(self, tile_type, pos_x, pos_y):
        super().__init__(tiles_group, all_sprites, hole_group)
        self.image = tile_images[tile_type]
        self.rect = self.image.get_rect().move(tile_width * pos_x, tile_height * pos_y)


class Hitbox(pygame.sprite.Sprite):
    def __init__(self, x, y):
        super().__init__(all_sprites)
        self.rect = pygame.Rect(x + 23, y + 6, 57, 75)
        self.left = x + 23
        self.top = y + 6
        self.right = self.left + 57
        self.bottom = self.top + 75


class Player(pygame.sprite.Sprite):
    def __init__(self, pos_x, pos_y):
        super().__init__(player_group, all_sprites)
        self.speed = 5
        self.image = load_image('player.png', True)
        self.x = tile_width * pos_x
        self.y = tile_height * pos_y
        self.direction = 'right'
        self.room = [self.x // 1280, self.y // 1280]
        self.in_corridor = False
        self.walk_cycle = 0
        self.hp = 3
        self.hitbox = Hitbox(self.x, self.y)
        self.rect = self.image.get_rect().move(self.x, self.y)
        self.gun = Pistol(self.rect.left, self.rect.top)

    def move(self, dir, n):
        self.rect[dir] += self.speed * n
        self.hitbox.rect[dir] += self.speed * n
        if dir == 0:
            self.x += self.speed * n
            self.hitbox.left += self.speed * n
            self.hitbox.right += self.speed * n
        else:
            self.y += self.speed * n
            self.hitbox.top += self.speed * n
            self.hitbox.bottom += self.speed * n

        self.room = [self.x // 1280, self.y // 1280]

        self.in_corridor = any([self.hitbox.left % 1280 > 895, self.hitbox.top % 1280 > 895, \
                                self.hitbox.right % 1280 < 64, self.hitbox.top % 1280 < 64, \
                                self.hitbox.left % 1280 < 64, self.hitbox.top % 1280 < 64, \
                                self.hitbox.right % 1280 > 896, self.hitbox.bottom % 1280 > 896])


class Gun(pygame.sprite.Sprite):
    def __init__(self, pos_x, pos_y):
        super().__init__(gun_group)
        self.normal_image = load_image('pistol.png', True)
        self.image = load_image('pistol.png', True)
        self.x = tile_width * pos_x + 75
        self.y = tile_height * pos_y + 40
        self.rect = self.image.get_rect().move(self.x, self.y)
        self.damage = 5
        self.bv = 10

    def rotate(self):
        mouse_x, mouse_y = pygame.mouse.get_pos()
        rel_x, rel_y = mouse_x - self.rect.left, mouse_y - self.rect.top
        angle = (180 / math.pi) * -math.atan2(rel_y, rel_x)
        if angle < -90 or angle > 90:
            self.image = pygame.transform.flip(self.normal_image, True, False)
            self.image = pygame.transform.rotate(self.image, int(angle) - 180)
        else:
            self.image = pygame.transform.rotate(self.normal_image, int(angle))
        self.rect = self.image.get_rect(center=(983, 560))


class Pistol(Gun):
    def __init__(self, pos_x, pos_y):
        super().__init__(pos_x, pos_y)
        self.normal_image = load_image('pistol.png', True)
        self.image = load_image('pistol.png', True)
        self.bv = 10
        self.damage = 5
        self.gap = 20

    def shoot(self, pos):
        Bullet(pos[0], pos[1], self.bv, self.damage, 30)


class Uzi(Gun):
    def __init__(self, pos_x, pos_y):
        super().__init__(pos_x, pos_y)
        self.normal_image = load_image('uzi.png', True)
        self.image = load_image('uzi.png', True)
        self.bv = 20
        self.damage = 2
        self.gap = 7

    def shoot(self, pos):
        Bullet(pos[0], pos[1], self.bv, self.damage, 20)


class Minigun(Gun):
    def __init__(self, pos_x, pos_y):
        super().__init__(pos_x, pos_y)
        self.normal_image = load_image('minigun.png', True)
        self.image = load_image('minigun.png', True)
        self.bv = 20
        self.damage = 2
        self.gap = 2

    def shoot(self, pos):
        Bullet(pos[0], pos[1], self.bv, self.damage, 15)


class Shotgun(Gun):
    def __init__(self, pos_x, pos_y):
        super().__init__(pos_x, pos_y)
        self.normal_image = load_image('shotgun.png', True)
        self.image = load_image('shotgun.png', True)
        self.bv = 15
        self.damage = 5
        self.gap = 60

    def shoot(self, pos):
        for i in range(10):
            Bullet(pos[0], pos[1], self.bv, self.damage, 10)


class Bullet(pygame.sprite.Sprite):
    def __init__(self, x, y, v, damage, uni):
        super().__init__(bullet_group, all_sprites)
        self.x = player.rect.left + 55
        self.y = player.rect.top + 40
        rx = x - self.x
        ry = y - self.y
        angle = (180 / math.pi) * math.atan2(rx, ry)
        angle = random.uniform(angle - 180 / uni, angle + 180 / uni)
        self.vx = math.sin(angle / 180 * math.pi) * v
        self.vy = math.cos(angle / 180 * math.pi) * v
        self.damage = damage
        self.image = load_image('pistol_bullet.png', True)
        self.rect = self.image.get_rect().move(self.x, self.y)
        self.sx, self.sy = self.rect.center

        self.image = pygame.transform.flip(self.image, False, True)
        self.image = pygame.transform.rotate(self.image, int(angle))

    def update(self):
        self.sx = self.sx + self.vx
        self.sy = self.sy + self.vy
        self.rect.left = self.sx
        self.rect.top = self.sy


# globals and main part
pygame.init()
width = 1920
height = 1080
screen = pygame.display.set_mode((width, height))
pygame.display.set_caption("Diablo pre Alpha 0.1")
clock = pygame.time.Clock()
fps = 60
level_names = ['room1', 'room2', 'room3', 'room4', 'room5', 'room6', 'room7', 'room8', 'room9', 'room10']
player = None
dead = False
in_game = False
floor = 0

tile_images = {'wall': load_image('wall.png'), 'empty': load_image('floor.png'), 'hole': load_image('hole.png')}
tile_width = 64
tile_height = 64

arrow = load_image('aim.png', False)
menu_background = load_image('menu_background.jpg')
heart = load_image('heart.png', False)
heart_rect = heart.get_rect()

enemies_allowed = []
for i in range(15):
    enemies_allowed.append([])
    for j in range(15):
        enemies_allowed[i].append(True)
for i in range(5, 10):
    enemies_allowed[0][i] = False
    enemies_allowed[1][i] = False
    enemies_allowed[2][i] = False
    enemies_allowed[12][i] = False
    enemies_allowed[13][i] = False
    enemies_allowed[14][i] = False
    enemies_allowed[i][0] = False
    enemies_allowed[i][1] = False
    enemies_allowed[i][2] = False
    enemies_allowed[i][12] = False
    enemies_allowed[i][13] = False
    enemies_allowed[i][14] = False

tiles_group = pygame.sprite.Group()
player_group = pygame.sprite.Group()
walls_group = pygame.sprite.Group()
all_sprites = pygame.sprite.Group()
hole_group = pygame.sprite.Group()
gun_group = pygame.sprite.Group()
bullet_group = pygame.sprite.Group()
enemy_group = pygame.sprite.Group()
dead_group = pygame.sprite.Group()
bullet_stopper_group = pygame.sprite.Group()
temp_walls_group = pygame.sprite.Group()
gold_text_group = pygame.sprite.Group()

menu = Menu()
while in_game or menu.in_menu or dead:
    if in_game:
        run_game()
    if menu.in_menu:
        menu.run_menu()
    if dead:
        death_anim()
