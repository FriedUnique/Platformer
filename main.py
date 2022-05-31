import pygame
from settings import ORIGINAL_SPEED, WIDTH, HEIGHT, BLOCKSIZE, maps
from block import Block, Coin, Spike, SpecialEffectBlock


#TODO: Make a easy splashscreen class (for level navigation after level finish) (auuuughghu9auhsusd[fo das])
#TODO: Double Jump (done)
#TODO: Score, Highscore, Timer (done, more or less)

pygame.init()

screen = pygame.display.set_mode((WIDTH, HEIGHT))
clock = pygame.time.Clock()
vec = pygame.math.Vector2

#region classes
class Player(pygame.sprite.Sprite):
    def __init__(self, pos):
        self.image = pygame.Surface((32, 64))
        self.image.fill((25, 20, 230))
        self.rect = self.image.get_rect(topleft=(pos))

        self.speed = 10 # controlls the world and plazer speed

        self.velocity = vec(0, 0)
        self.gForce = 0.59
        self.jmpForce = -14

        self.isGrounded = True
        self.maxJumps = 2
        self.jumps = self.maxJumps
        self.health = 3

        self.score = 0


    def move(self, dir):
        # horizotal movement
        self.velocity.x = dir
        self.rect.x += self.velocity.x * self.speed

        
    def gravity(self):
        #constant gravity
        if self.isGrounded: return

        self.velocity.y += self.gForce
        self.rect.y += self.velocity.y

        #check if grounded
    def jump(self):
        if not self.isGrounded and self.jumps == 0: return 0
        self.velocity.y = self.jmpForce
        self.jumps -= 1
        return self.jmpForce

    def draw(self, surface):
        surface.blit(self.image, self.rect)


class LevelHandler:
    def __init__(self, surface):
        self.level = 0
        self.targetSurface = surface

        self.dir = 0
        self.moveThreshold = [400, WIDTH-432]

        self.player = None
        self.loadLevel(self.level)

        self.jumpPressed = False
        self.levelTime = 0

        self.v = 0

    def loadLevel(self, level):
        level = min(level, len(maps))
        
        self.blocks = pygame.sprite.Group()
        self.spikes = pygame.sprite.Group()
        self.finish = pygame.sprite.GroupSingle()
        self.coins = pygame.sprite.Group()
        self.player = None

        for y, row in enumerate(maps[level]):
            for x, blockData in enumerate(row):

                # block
                if blockData == 1:
                    b = Block((x*BLOCKSIZE,y*BLOCKSIZE), BLOCKSIZE)
                    self.blocks.add(b)

                # player
                elif blockData == 2:
                    self.player = Player((x*BLOCKSIZE, y*BLOCKSIZE))

                # spike
                elif blockData == 3:
                    s = Spike((x*BLOCKSIZE, y*BLOCKSIZE), BLOCKSIZE)
                    self.spikes.add(s)

                #finish block
                elif blockData == 4:
                    b = Block((x*BLOCKSIZE,y*BLOCKSIZE), BLOCKSIZE)
                    b.image.fill((0, 255, 0))
                    self.finish.add(b)

                # coin
                elif blockData == 5:
                    c = Coin((x*BLOCKSIZE,y*BLOCKSIZE), 0)
                    self.coins.add(c)

        # reset all buffs
        self.player.speed = ORIGINAL_SPEED

    def reset(self):
        self.loadLevel(self.level)
    
    def nextLevel(self):
        if self.level + 1 > len(maps)-1:
            print("scheiss sweat es git keis nögschts level.")
            return
        
        self.level += 1
        self.levelTime = 0
        self.loadLevel(self.level)

    def ui(self):
        """Draw misc. ui elements"""
        w = self.targetSurface.get_width()
        # time
        timeText = pygame.font.Font(None, 35).render("%07d" % (int(round(self.levelTime/1000, 0)), ), True, (255, 255, 255))
        # score
        scoreText = pygame.font.Font(None, 35).render("%05d" % (self.player.score, ), True, (255, 255, 255))
        # level
        levelText = pygame.font.Font(None, 35).render(f"Level: {self.level+1}", True, (255, 255, 255))


        self.targetSurface.blit(timeText, (10, 10))
        self.targetSurface.blit(scoreText, (w-90, 10))
        self.targetSurface.blit(levelText, (int(w/2)-int(levelText.get_width()/2), 10))

    #region physics (han so kei bock meh uf das)

    def movement(self):
        self.dir = 0

        keys = pygame.key.get_pressed()

        if keys[pygame.K_RIGHT]:
            self.dir = 1
            if self.player.rect.x <= self.moveThreshold[1]:
                self.player.move(self.dir)
                return

        elif keys[pygame.K_LEFT]:
            self.dir = -1
            if self.player.rect.x >= self.moveThreshold[0]:
                self.player.move(self.dir)
                return

        # world movement
        self.blocks.update(self.dir, self.player.speed)
        self.spikes.update(self.dir, self.player.speed)
        self.finish.update(self.dir, self.player.speed)
        self.coins.update(self.dir, self.player.speed)


    def gravityMovement(self):
        keys = pygame.key.get_pressed()
        if keys[pygame.K_UP] and not self.jumpPressed:
            self.v += self.player.jump()
            self.jumpPressed = True

        if not keys[pygame.K_UP]:
            self.jumpPressed = False
            
        # normal
        if self.player.rect.y > 100:
            self.player.gravity()
            self.v = self.player.velocity.y

        # world movement
        elif self.player.rect.y <= 100 and not self.player.isGrounded:
            self.player.rect.y = 100

            self.v += self.player.gForce
            self.verticalCollisions()

            for b in self.blocks:
                b.updateY(self.v)

            if list(self.blocks)[0].isLowest():
                self.player.velocity.y = self.v
                self.player.gravity()
        

        # fall of the map
        if self.player.rect.y > WIDTH:
            self.reset()


    # split the collisions so the gravity wont affect the performance of the collision handeling
    def horizotalCollisions(self):
        for block in self.blocks.sprites():
            if block.rect.colliderect(self.player.rect):
                if self.dir == 1: # right
                    self.player.rect.right = block.rect.left
                elif self.dir == -1: # left
                    self.player.rect.left = block.rect.right

    def verticalCollisions(self):
        self.player.isGrounded = False

        for block in self.blocks.sprites():
            if block.rect.colliderect(self.player.rect):
                if self.player.velocity.y > 0 or self.v > 0: # down    
                    self.player.rect.bottom = block.rect.top

                    self.player.velocity.y = 0
                    self.v = 0
                    self.player.isGrounded = True
                    self.player.jumps = self.player.maxJumps
                    
                # results in problem when jumping at the right moment, it will think you hit the block from below, because your velocity is pointing up
                elif (self.player.velocity.y < 0 or self.v < 0) and block.rect.bottom > self.player.rect.top: # up
                    self.player.isGrounded = True
                    self.player.rect.top = block.rect.bottom
                    self.player.velocity.y = 0
                    
                    if type(block) == SpecialEffectBlock:
                        self.player.speed += block.randomEffect()

    def normalCollision(self):
        """general collision with Spikes, Finish, etc. By default they will be 'ghost' blocks."""
        # if collided then jump back
        spikes = pygame.sprite.spritecollide(self.player, self.spikes, False)
        if spikes:
            for spike in spikes:
                if spike.cooldown < pygame.time.get_ticks():
                    spike.cooldown = pygame.time.get_ticks() + 1000
                    self.player.health -= 1
                    print("player hurt: spikes")

        if pygame.sprite.spritecollide(self.player, self.finish, False):
            #! instead of directly loading next level, show promt
            self.nextLevel()

        coins = pygame.sprite.spritecollide(self.player, self.coins, False)
        if coins:
            for coin in coins:
                coin.kill()
                self.player.score += 10


    # calls all the physics related fuctions
    def physics(self):
        self.movement()
        self.horizotalCollisions()
        self.gravityMovement()
        self.verticalCollisions()

        self.normalCollision()
    
    #endregion

    def update(self):
        self.physics()

        # draw level
        self.blocks.draw(self.targetSurface)
        self.spikes.draw(self.targetSurface)
        self.finish.draw(self.targetSurface)
        self.coins.draw(self.targetSurface)

        self.player.draw(self.targetSurface)

        self.ui()

        self.levelTime += clock.get_time()

#endregion

levelHandler = LevelHandler(screen)

isRunning = True
while isRunning:
    clock.tick(60)

    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            isRunning = False

    screen.fill((0, 0, 0))
    levelHandler.update()

    pygame.display.update()