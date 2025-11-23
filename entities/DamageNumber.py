import pygame
import os


class DamageNumber:
    """
    Represents a floating damage number that appears above entities when they take damage.
    The number floats upward and fades out over time, just like in MapleStory.
    """
    
    def __init__(self, damage, x, y, damage_type='mob'):
        """
        Initialize a damage number.
        
        Args:
            damage (int): The damage value to display
            x (int): World x position (center of entity)
            y (int): World y position (top of entity)
            damage_type (str): 'mob' for damage to mobs, 'player' for damage to players
        """
        self.damage = int(damage)
        self.x = x
        self.y = y
        self.damage_type = damage_type
        
        # Animation properties
        self.lifetime = 0  # Time alive in milliseconds
        self.max_lifetime = 1200  # Total duration in milliseconds (1.2 seconds)
        self.float_speed = 1.5  # Pixels per frame to move upward
        self.alive = True
        
        # Load digit sprites
        self.digit_sprites = {}
        sprite_path = f'sprites/entities/damage/{damage_type}'
        
        for i in range(10):
            digit_file = os.path.join(sprite_path, f'{i}.png')
            if os.path.exists(digit_file):
                self.digit_sprites[str(i)] = pygame.image.load(digit_file).convert_alpha()
        
        # Load critical effect sprite if this is a critical hit
        self.effect_sprite = None
        if damage_type == 'critical':
            effect_file = os.path.join(sprite_path, 'effect.png')
            if os.path.exists(effect_file):
                self.effect_sprite = pygame.image.load(effect_file).convert_alpha()
        
        # Create the composed damage number image
        self.create_damage_image()
        
        # Center the damage number horizontally
        self.x -= self.image.get_width() // 2
        
    def create_damage_image(self):
        """Create a single image from individual digit sprites."""
        damage_str = str(self.damage)
        
        # Spacing adjustment between digits (negative = closer together)
        # Critical sprites have extra padding, so we need more overlap
        digit_spacing = -35 if self.damage_type == 'critical' else -5
        
        # Base scale multiplier for different damage types
        # Normal damage is bigger (1.3x), critical stays at normal size (1.0x)
        base_scale = 1.0 if self.damage_type == 'critical' else 1.2
        
        # Scale factors for each digit position (first digit is largest)
        # First digit: 1.0x, second: 0.9x, third: 0.8x, etc.
        def get_scale_factor(index, total_digits):
            # First digit is 100%, each subsequent digit is 10% smaller
            return max(0.5, 1.0 - (index * 0.1)) * base_scale
        
        # Calculate total width and max height for digits (with scaling)
        total_width = 0
        max_height = 0
        digit_images = []
        scaled_digit_images = []
        
        num_digits = len(damage_str)
        for i, digit in enumerate(damage_str):
            if digit in self.digit_sprites:
                sprite = self.digit_sprites[digit]
                digit_images.append(sprite)
                
                # Scale the digit based on position
                scale_factor = get_scale_factor(i, num_digits)
                scaled_width = int(sprite.get_width() * scale_factor)
                scaled_height = int(sprite.get_height() * scale_factor)
                scaled_sprite = pygame.transform.scale(sprite, (scaled_width, scaled_height))
                scaled_digit_images.append(scaled_sprite)
                
                total_width += scaled_width + digit_spacing
                max_height = max(max_height, scaled_height)
        
        # Remove the extra spacing from the last digit
        if scaled_digit_images:
            total_width -= digit_spacing
        
        # Create a surface to hold all digits
        self.base_image = pygame.Surface((total_width, max_height), pygame.SRCALPHA)
        
        # Draw the critical effect FIRST (behind/z-index below the first digit)
        first_digit_x = 0
        if self.effect_sprite and scaled_digit_images:
            # Center the effect at the same position as the first digit
            first_digit_width = scaled_digit_images[0].get_width()
            first_digit_height = scaled_digit_images[0].get_height()
            effect_x = first_digit_x + (first_digit_width - self.effect_sprite.get_width() - 25) // 2
            effect_y = max_height - first_digit_height + (first_digit_height - self.effect_sprite.get_height()+25) // 2
            self.base_image.blit(self.effect_sprite, (effect_x, effect_y))
        
        # Blit each digit onto the surface, aligned at the bottom (AFTER effect, so digits are on top)
        current_x = 0
        for i, digit_img in enumerate(scaled_digit_images):
            # Align all digits at the bottom to prevent staggered heights
            y_offset = max_height - digit_img.get_height()
            self.base_image.blit(digit_img, (current_x, y_offset))
            current_x += digit_img.get_width() + digit_spacing
        
        # Start with the base image
        self.image = self.base_image.copy()
    
    def update(self, dt):
        """
        Update the damage number animation.
        
        Args:
            dt (int): Delta time in milliseconds
        """
        self.lifetime += dt
        
        # Float upward
        self.y -= self.float_speed
        
        # Calculate alpha based on lifetime (fade out in the last 60% of lifetime)
        fade_start = self.max_lifetime * 0.4  # Start fading at 40% of lifetime
        if self.lifetime > fade_start:
            # Fade from 255 to 0
            fade_progress = (self.lifetime - fade_start) / (self.max_lifetime - fade_start)
            alpha = int(255 * (1 - fade_progress))
            alpha = max(0, min(255, alpha))  # Clamp between 0 and 255
            
            # Apply alpha to the image
            self.image = self.base_image.copy()
            self.image.fill((255, 255, 255, alpha), special_flags=pygame.BLEND_RGBA_MULT)
        
        # Check if lifetime expired
        if self.lifetime >= self.max_lifetime:
            self.alive = False
    
    def draw(self, screen, camera_x=0, camera_y=0):
        """
        Draw the damage number on screen.
        
        Args:
            screen: Pygame surface to draw on
            camera_x (int): Camera x offset
            camera_y (int): Camera y offset
        """
        if self.alive:
            screen_x = self.x - camera_x
            screen_y = self.y - camera_y
            screen.blit(self.image, (screen_x, screen_y))
