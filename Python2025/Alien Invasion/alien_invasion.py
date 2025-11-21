import sys
import pygame
from ship import Ship
from settings import Settings
from bullet import Bullet

class AlienInvasion:
    def __init__(self):
        pygame.init()
        self.settings=Settings()

        self.screen=pygame.display.set_mode((self.settings.screen_width, self.settings.screen_bridth))
        pygame.display.set_caption("Alien Invasion")
        self.bg_color=(self.settings.bg_color)
        self.ship=Ship(self)#This 'self' represents the current class instance, we assign 'Ship' instance to self.ship so that it's accessible here
        self.bullets=pygame.sprite.Group()

    def run_game(self):
        while True:
            self._check_events()
            self._update_screen()
            self._update_bullet()
            self.ship.update()

    def _check_events(self):
        for event in pygame.event.get():
                if event.type==pygame.QUIT:
                    sys.exit()
                elif event.type==pygame.KEYDOWN:
                    self._check_keydown_events(event)
                elif event.type==pygame.KEYUP:
                    self._check_keyup_events(event)
                    
                
    def _check_keydown_events(self, event):
        if event.key==pygame.K_RIGHT:
            self.ship.moving_right=True
        elif event.key==pygame.K_LEFT:
            self.ship.moving_left=True
        elif event.key==pygame.K_q:
            sys.exit()
        elif event.key==pygame.K_SPACE:
            self._fire_bullet()

    def _check_keyup_events(self, event):
        if event.key==pygame.K_RIGHT:
            self.ship.moving_right=False
        elif event.key==pygame.K_LEFT:
            self.ship.moving_left=False

    def _fire_bullet(self): #I don't understand this code
        if len(self.bullets) < self.settings.bullet_allowed:
            new_bullet=Bullet(self)
            self.bullets.add(new_bullet)

    def _update_screen(self):
        self.screen.fill(self.settings.bg_color)
        self.ship.blitme()
        for bullet in self.bullets.sprites():
            bullet.draw_bullet()
        pygame.display.flip()

    def _update_bullet(self):
        self.bullets.update()
        #Get rid of the bullets that have disappeared
        for bullet in self.bullets.copy():
            if bullet.rect.bottom <= 0:
                self.bullets.remove(bullet)
        print(len(self.bullets))


if __name__=="__main__":
    ai=AlienInvasion()
    ai.run_game()