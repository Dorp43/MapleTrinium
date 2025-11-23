
import pygame
import random

class Projectile(pygame.sprite.Sprite):
    def __init__(self, x, y, direction, speed, isRotate, projectile_name, damage, hit_count):
        pygame.sprite.Sprite.__init__(self)
        if direction == 1:
            self.flip = True
        else:
            self.flip = False
        self.projectile_name = projectile_name
        self.original_image = pygame.image.load(f'sprites/projectiles/{self.projectile_name}/0.png').convert_alpha()
        self.image = self.original_image  # This will reference our rotated image.
        self.image = pygame.transform.flip(self.image, self.flip, False)
        self.rect = self.image.get_rect()
        self.rect = self.image.get_rect()
        self.rect.center = (x,y)
        self.angle = 0 # Always initialize angle
        
        self.range = 300 # Default range if not passed
        # self.projectile = projectile # Removed as it was undefined and unused
        self.speed = speed
        self.hit_count = 0
        self.damage = damage
        self.isRotate = isRotate
        self.direction = direction
        self.mobs_hitted = pygame.sprite.Group()
        self.hit_count = hit_count
        
        # Critical hit settings
        self.crit_chance = 0.15  # 15% critical hit chance
        self.crit_multiplier = 1.5  # 1.5x damage on critical hits

        

    def update(self, mobs, player, hit_list=None):
        #move projectile
        self.rect.x += (self.direction * self.speed)
        if self.isRotate:
            self.rotate()
        for mob in mobs:
            if pygame.sprite.spritecollide(mob, player.projectiles_group, False):
                if mob.alive and mob not in self.mobs_hitted and len(self.mobs_hitted) != self.hit_count:
                    self.mobs_hitted.add(mob)
                    
                    # Add damage variance (70% to 100% of base damage)
                    damage_variance = random.uniform(0.7, 1.0)
                    base_damage = int(self.damage * damage_variance)
                    
                    # Calculate critical hit
                    is_critical = random.random() < self.crit_chance
                    damage = int(base_damage * self.crit_multiplier) if is_critical else base_damage
                    
                    # Apply damage with critical flag
                    mob.hit(damage, player, is_critical=is_critical)
                    if hit_list is not None:
                        hit_list.append((mob.id, damage))
                    if self.hit_count == 1:
                        self.kill()
        #check if projectile has gone off range
        if self.rect.x > (player.rect.x + self.range) or self.rect.x < (player.rect.x - self.range):
            # print("DEBUG: Projectile killed due to range")
            self.kill()

    def rotate(self):
        self.image = pygame.transform.rotate(self.original_image, self.angle)
        self.angle += 10 % 360  # Value will reapeat after 359. This prevents angle to overflow.
        x, y = self.rect.center  # Save its current center.
        self.rect = self.image.get_rect()  # Replace old rect with new rect.
        self.rect.center = (x, y)  # Put the new rect's center at old center.

 