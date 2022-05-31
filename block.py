from settings import BLOCKSIZE
import pygame

vec = pygame.math.Vector2

class Block(pygame.sprite.Sprite):
    def __init__(self, pos, size):
        super().__init__()
        self.originalPos = pos
        self.image = pygame.Surface((size, size))
        self.image.fill((255, 255, 255))
        self.rect = self.image.get_rect(topleft=pos)

    def isLowest(self):
        return abs(self.originalPos[1]-self.rect.y) < 10

    def update(self, dir, speed):
        # world move
        self.rect.x -= speed*dir

    def updateY(self, speed):
        if self.originalPos[1] > self.rect.y - speed: 
            self.rect.y = self.originalPos[1]
            return
            
        self.rect.y -= speed

# inheritance heisst, dass mer eifach alli funktione vom parent class übernimmt und override chan
class Spike(Block):
    def __init__(self, pos, size):
        super().__init__(pos, size)
        pos = (pos[0], pos[1]+BLOCKSIZE)
        self.image = pygame.Surface((size, 30))
        self.image.fill((0, 255, 255))
        self.rect = self.image.get_rect(bottomleft=pos)

        self.cooldown = 0 # before it will effect the player.health

class Coin(Block):
    def __init__(self, pos, size):
        super().__init__(pos, size)
        self.pos = (pos[0] + int(BLOCKSIZE/4), pos[1] + int(BLOCKSIZE/4))
        self.image = pygame.Surface((int(BLOCKSIZE/2), int(BLOCKSIZE/2)))
        self.image.fill((255, 255, 0))
        self.rect = self.image.get_rect(topleft=self.pos)

class SpecialEffectBlock(Block):
    """Will give a random effect, for eg. jump buff, speed buff, or just points"""
    def __init__(self, pos, size):
        super().__init__(pos, size)

    def randomEffect(self):
        return 3
    