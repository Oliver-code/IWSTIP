import pygame
import settings

class Player(pygame.sprite.Sprite):
    def __init__(self, pos):
        super().__init__()
        self.frame = 0

        self.original_image = pygame.image.load(settings.image_dict["PlayerIdle"]).convert_alpha()

        self.image = self.original_image

        self.mask = pygame.mask.from_surface(pygame.image.load(settings.image_dict["PlayerMask"]).convert_alpha())
        mask_rect = (self.mask.get_bounding_rects())[0]
        self.offset = pygame.math.Vector2(mask_rect[0], mask_rect[1])

        self.speed = 3
        self.jump_vel = 8.5
        self.djump_vel = 7
        self.jumps = 2
        self.gravity = 0.4
        self.jump_cooldown = True
        self.max_fall = 9

        self.dead = False
        self.jumps_counter = 1
        self.grounded = False
        self.velocity = pygame.math.Vector2(0, 0)
        self.direction = 1

        self.hitbox = mask_rect
        self.hitbox.topleft = pos
        self.rect = self.image.get_rect()  # pygame.Rect(pos, (size[0], size[1]))
        self.update_sprite()

    def input(self):
        keys = pygame.key.get_pressed()
        if keys[pygame.K_RIGHT]:
            self.velocity.x = 1 * self.speed
            self.image = self.original_image
            self.direction = 1
        elif keys[pygame.K_LEFT]:
            self.velocity.x = -1 * self.speed
            self.image = pygame.transform.flip(self.original_image, True, False)
            self.direction = -1
        else:
            self.velocity.x = 0

        if (keys[pygame.K_LSHIFT] or keys[pygame.K_RSHIFT]) and self.jump_cooldown == False:
            self.jump_cooldown = True
            if self.jumps_counter == 0 and self.grounded:
                self.velocity.y = self.jump_vel - self.gravity
                self.grounded = False
                self.jumps_counter += 1
            elif self.jumps_counter < self.jumps:
                self.velocity.y = self.djump_vel - self.gravity
                self.grounded = False
                self.jumps_counter += 1
        elif (not keys[pygame.K_LSHIFT] and not keys[pygame.K_RSHIFT]) and self.jump_cooldown == True:
            if self.velocity.y > 0:
                self.velocity.y *= 0.45
            self.jump_cooldown = False

    def check_grounded(self, tiles):
        for tile in tiles:
            temp_rect = pygame.Rect((self.hitbox.topleft), (self.hitbox.size[0], self.hitbox.size[1] + 1))
            if temp_rect.colliderect(tile.rect):
                self.grounded = True
                self.jumps_counter = 0
                return
            else:
                self.grounded = False
                if self.jumps_counter < 1:
                    self.jumps_counter = 1

    def block_collision(self, tiles):
        self.horizontal(tiles)
        self.vertical(tiles)

    def horizontal(self, tiles):
        self.hitbox.x += self.velocity.x
        for tile in tiles:
            if self.hitbox.colliderect(tile.rect):
                if self.velocity.x < 0:
                    self.hitbox.left = tile.rect.right
                    self.velocity.x = 0
                elif self.velocity.x > 0:
                    self.hitbox.right = tile.rect.left
                    self.velocity.x = 0

    def vertical(self, tiles):

        if not self.grounded:
            self.apply_gravity()

        self.hitbox.y -= self.velocity.y
        for tile in tiles:
            if self.hitbox.colliderect(tile.rect):
                if self.velocity.y < 0:
                    self.hitbox.bottom = tile.rect.top
                    self.velocity.y = 0
                    self.grounded = True
                    self.jumps_counter = 0
                elif self.velocity.y > 0:
                    self.hitbox.top = tile.rect.bottom
                    self.velocity.y = 0

    def kill_collision(self, killers):
        for sprite in killers:
            if pygame.sprite.collide_rect(self, sprite):
                if pygame.sprite.collide_mask(self, sprite):
                    return True

    def apply_gravity(self):
        self.velocity.y -= self.gravity
        if self.velocity.y < self.max_fall * -1:
            self.velocity.y = self.max_fall * -1

    def update_sprite(self):
        self.rect.topleft = self.hitbox.topleft - self.offset
        if self.direction == -1:
            self.rect.topleft = (self.rect.topleft[0] + 3, self.rect.topleft[1])

    def update(self, tiles, killers):
        self.frame += 1
        self.input()
        self.check_grounded(tiles)
        self.block_collision(tiles)
        self.update_sprite()
        if self.kill_collision(killers):
            self.dead = True

    def draw(self):
        # pygame.draw.rect(screen, "Black", self.hitbox)
        pass