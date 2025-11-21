import pygame

class Ship:
    def __init__(self, ai_game):
        self.screen=ai_game.screen
        self.settings=ai_game.settings
        self.screen_rect=ai_game.screen.get_rect()
        self.image=pygame.image.load('images/gokuu.bmp')
        self.image=pygame.transform.scale(self.image,(100,100))
        self.image=pygame.transform.rotate(self.image,90)
        self.rect=self.image.get_rect()
        self.rect.midbottom=self.screen_rect.midbottom

        #Stores the decimal value for the ship's horizontal position
        self.x=float(self.rect.x)

        #Movement flag
        self.moving_right=False
        self.moving_left=False

    def update(self):
        if self.moving_right and self.rect.right<self.screen_rect.right:
            self.x+=self.settings.ship_speed
        elif self.moving_left and self.rect.left>0:
            self.x-=self.settings.ship_speed

        #Update rect object from self
        self.rect.x=self.x

    def blitme(self):
        self.screen.blit(self.image, self.rect)