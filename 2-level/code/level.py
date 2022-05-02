import pygame

from particls import ParticleEffect
from support import import_csv_layout
from support import impor_cut_graphics
from settings import tile_size, screen_height, vertical_tile_number,screen_width
from tiles import Title, StaticTile, Crate, AnimatedTile, Coin, Palm
from enemy import Enemy
from decoration import Sky, Water, Clouds
from player import Player
from particls import ParticleEffect


class Level:
    def __init__(self, level_data, surface):
        # general setup
        self.display_surface = surface
        self.world_shift = 0
        current_x = None

        # Player
        player_layout = import_csv_layout(level_data['player'])
        self.player = pygame.sprite.GroupSingle()
        self.goal = pygame.sprite.GroupSingle()
        self.player_setup(player_layout)

        #dust
        self.dust_sprite = pygame.sprite.GroupSingle()
        self.player_on_ground = False

        # terrain
        terrain_layout = import_csv_layout(level_data['terrain'])
        self.terrani_sprites = self.create_tile_group(terrain_layout, 'terrain')

        # grass setup
        grass_layout = import_csv_layout(level_data['grass'])
        self.grass_sprites = self.create_tile_group(grass_layout, 'grass')

        # crates
        crates_layout = import_csv_layout(level_data['crates'])
        self.crates_sprites = self.create_tile_group(crates_layout, 'crates')

        # coins
        coin_layout = import_csv_layout(level_data['coins'])
        self.coin_sprites = self.create_tile_group(coin_layout, 'coins')

        # foreground palms
        fg_palm_layout = import_csv_layout(level_data['fg plams'])
        self.fg_palm_sprites = self.create_tile_group(fg_palm_layout, 'fg plams')

        # bckground palms
        bg_palm_layout = import_csv_layout(level_data['bg plams'])
        self.bg_palm_sprites = self.create_tile_group(bg_palm_layout, 'bg plams')

        # enemy
        enemy_layout = import_csv_layout(level_data['enemies'])
        self.enemy_sprites = self.create_tile_group(enemy_layout, 'enemies')

        # constraint
        constraint_layout = import_csv_layout(level_data['constraints'])
        self.constraint_sprites = self.create_tile_group(constraint_layout, 'constraints')

        # decoration
        self.sky = Sky(8)
        level_width = len(terrain_layout[0]) * tile_size
        self.Water = Water(screen_height - 10, level_width)

        self.clouds = Clouds(400, level_width, 20)

    def create_tile_group(self, layout, type):
        sprite_group = pygame.sprite.Group()

        for row_index, row in enumerate(layout):
            # print('row number: ')
            # print(row_index)
            for col_index, val in enumerate(row):
                if val != '-1':
                    x = col_index * tile_size
                    y = row_index * tile_size

                    if type == 'terrain':
                        terrain_tile_list = impor_cut_graphics('../graphic/terrain/terrain_tiles.png')
                        tile_surface = terrain_tile_list[int(val)]
                        sprite = StaticTile(tile_size, x, y, tile_surface)
                        sprite_group.add(sprite)
                    if type == 'grass':
                        grass_tile_list = impor_cut_graphics('../graphic/decoration/grass/grass.png')
                        tile_surface = grass_tile_list[int(val)]
                        sprite = StaticTile(tile_size, x, y, tile_surface)
                        sprite_group.add(sprite)
                    if type == 'crates':
                        sprite = Crate(tile_size, x, y)
                        sprite_group.add(sprite)
                    if type == 'coins':
                        if val == '0':
                            sprite = Coin(tile_size, x, y, '../graphic/coins/gold')
                        else:
                            sprite = Coin(tile_size, x, y, '../graphic/coins/silver')
                        # sprite = Coin(tile_size, x, y, '../graphic/coins/gold')
                        sprite_group.add(sprite)
                    if type == 'fg plams':
                        if val == '0': sprite = Palm(tile_size, x, y, '../graphic/terrain/palm_small', 38)
                        if val == '1': sprite = Palm(tile_size, x, y, '../graphic/terrain/palm_large', 64)
                        sprite_group.add(sprite)
                    if type == 'bg plams':
                        sprite = Palm(tile_size, x, y, '../graphic/terrain/palm_bg', 64)
                        sprite_group.add(sprite)
                    if type == 'enemies':
                        sprite = Enemy(tile_size, x, y)
                        sprite_group.add(sprite)
                    if type == 'constraints':
                        sprite = Title(tile_size, x, y)
                        sprite_group.add(sprite)

        return sprite_group

    def player_setup(self, layout):
        for row_index, row in enumerate(layout):
            # print('row number: ')
            # print(row_index)
            for col_index, val in enumerate(row):
                x = col_index * tile_size
                y = row_index * tile_size
                if val == '0':
                    sprite = Player((x, y), self.display_surface, self.create_jump_particles)
                    self.player.add(sprite)
                if val == '1':
                    hat_surface = pygame.image.load('../graphic/character/hat.png').convert_alpha()
                    sprite = StaticTile(tile_size, x, y, hat_surface)
                    self.goal.add(sprite)

    def enemy_collision_reverse(self):
        for enemy in self.enemy_sprites.sprites():
            if pygame.sprite.spritecollide(enemy, self.constraint_sprites, False):
                enemy.reverse()

    def create_jump_particles(self, pos):
        if self.player.sprite.facing_right:
            pos -= pygame.math.Vector2(10, 5)
        else:
            pos += pygame.math.Vector2(10, -5)
        jump_particle_sprite = ParticleEffect(pos, 'jump')
        self.dust_sprite.add(jump_particle_sprite)

    def horizontal_movement_collision(self):
        player = self.player.sprite
        player.rect.x += player.direction.x * player.speed
        collidable_sprites = self.terrani_sprites.sprites() + self.crates_sprites.sprites() + self.fg_palm_sprites.sprites()
        for sprite in collidable_sprites:
            if sprite.rect.colliderect(player.rect):
                if player.direction.x < 0:
                    player.rect.left = sprite.rect.right
                    player.on_left = True
                    self.current_x = player.rect.left
                elif player.direction.x > 0:
                    player.rect.right = sprite.rect.left
                    player.on_right = True
                    self.current_x = player.rect.right

        if player.on_left and (player.rect.left < self.current_x or player.direction.x >= 0):
            player.on_left = False
        if player.on_right and (player.rect.right < self.current_x or player.direction.x <= 0):
            player.on_right = False

    def vertical_movement_collision(self):
        player = self.player.sprite
        player.apply_gravity()
        collidable_sprites = self.terrani_sprites.sprites() + self.crates_sprites.sprites() + self.fg_palm_sprites.sprites()

        for sprite in collidable_sprites:
            if sprite.rect.colliderect(player.rect):
                if player.direction.y > 0:
                    player.rect.bottom = sprite.rect.top
                    player.direction.y = 0
                    player.on_ground = True
                elif player.direction.y < 0:
                    player.rect.top = sprite.rect.bottom
                    player.direction.y = 0
                    self.on_ceilinng = True

        if player.on_ground and player.direction.y < 0 or player.direction.y > 1:
            player.on_ground = False
        if player.on_ceilinng and player.direction.y > 0:
            player.on_ceilinng = False

    def scrool_x(self):
        player = self.player.sprite
        player_x = player.rect.centerx
        direction_x = player.direction.x

        if player_x < screen_width / 4 and direction_x < 0:
            self.world_shift = 8
            player.speed = 0
        elif player_x > screen_width - (screen_width / 4) and direction_x > 0:
            self.world_shift = -8
            player.speed = 0
        else:
            self.world_shift = 0
            player.speed = 8

    def get_palyer_on_ground(self):
        if self.player.sprite.on_ground:
            self.palyer_on_ground = True
        else:
            self.palyer_on_ground = False

    def create_landing_dust(self):
        if not self.palyer_on_ground and self.player.sprite.on_ground and not self.dust_sprite.sprites():
            if not self.player.sprite.facing_right:
                offset = pygame.math.Vector2(10, 15)
            else:
                offset = pygame.math.Vector2(-10, 15)
            fall_dust_particle = ParticleEffect(self.player.sprite.rect.midbottom - offset, 'land')
            self.dust_sprite.add(fall_dust_particle)

    def run(self):
        # run the full level

        # decoration
        self.sky.draw(self.display_surface)
        self.clouds.draw(self.display_surface, self.world_shift)

        # background plam
        self.bg_palm_sprites.update(self.world_shift)
        self.bg_palm_sprites.draw(self.display_surface)
        # terrain
        self.terrani_sprites.update(self.world_shift)
        self.terrani_sprites.draw(self.display_surface)

        # crates
        self.crates_sprites.update(self.world_shift)
        self.crates_sprites.draw(self.display_surface)

        # enemy
        self.enemy_sprites.update(self.world_shift)
        self.constraint_sprites.update(self.world_shift)
        self.enemy_collision_reverse()
        self.enemy_sprites.draw(self.display_surface)

        # grass
        self.grass_sprites.update(self.world_shift)
        self.grass_sprites.draw(self.display_surface)

        # coins
        self.coin_sprites.update(self.world_shift)
        self.coin_sprites.draw(self.display_surface)

        # foreground plam
        self.fg_palm_sprites.update(self.world_shift)
        self.fg_palm_sprites.draw(self.display_surface)

        #dust particles
        self.dust_sprite.update(self.world_shift)
        self.dust_sprite.draw(self.display_surface)

        # player sprite
        self.player.update()
        self.horizontal_movement_collision()

        self.get_palyer_on_ground()
        self.vertical_movement_collision()

        self.create_landing_dust()
        self.scrool_x()
        self.player.draw(self.display_surface)
        self.goal.update(self.world_shift)
        self.goal.draw(self.display_surface)

        # water
        self.Water.draw(self.display_surface, self.world_shift)
