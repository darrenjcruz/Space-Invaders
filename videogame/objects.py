#!/usr/bin/env python3
# Darren Cruz
# CPSC 386-02
# 2023-04-19
# darrencruz@csu.fullerton.edu
# @darrenjcruz
#
# Lab 05-00
#
# This is the objects module that contains the object classes.
#


"""Using assets to create objects."""


from itertools import cycle
from random import randint
import math
import rgbcolors
import pygame
import assets


def load_sprite_sheet(filename, img_dim_x, img_dim_y, num_images, colorkey=None):
    """Loads a sprite sheet"""
    # Limitation: only considers a 1D strip of images where the images
    # are tiled from left to right
    try:
        sheet = pygame.image.load(filename)
    except pygame.error as pygame_error:
        print("\n".join(pygame_error.args))
        raise SystemExit(
            f'Unable to open "{filename}" {pygame.get_error()}'
        ) from pygame_error
    rects = [
        pygame.Rect(0 + (img_dim_x * n), 0, img_dim_x, img_dim_y)
        for n in range(num_images)
    ]
    images = []
    for r in rects:
        image = pygame.Surface(r.size)
        image.blit(sheet, (0, 0), r)
        if colorkey is not None:
            if colorkey == -1:
                colorkey = image.get_at((0, 0))
            image.set_colorkey(colorkey, pygame.RLEACCEL)
        images.append(tuple((image, image.get_rect())))
    return images


# Taken from the pygame examples
def load_image(filename, colorkey=None, scale=1):
    """Loads an image"""
    image = pygame.image.load(filename)
    image = image.convert()

    size = image.get_size()
    size = (size[0] * scale, size[1] * scale)
    image = pygame.transform.scale(image, size)

    if colorkey is not None:
        if colorkey == -1:
            colorkey = image.get_at((0, 0))
        image.set_colorkey(colorkey, pygame.RLEACCEL)
    return image, image.get_rect()


class Circle:
    """Class representing a ball with a bounding rect."""

    min_speed = 1.0
    max_speed = 5.0

    def __init__(self, position, speed, radius, color, name="None"):
        """Initialize a Circle object"""
        self._position = position
        self._original_position = pygame.math.Vector2(position)
        assert speed <= Circle.max_speed
        assert speed >= Circle.min_speed
        self._speed = speed
        self._radius = radius
        self._color = color
        self._name = name

    @property
    def radius(self):
        """Return the circle's radius"""
        return self._radius

    @property
    def position(self):
        """Return the circle's position."""
        return self._position

    @property
    def original_position(self):
        """Return the circle's original position."""
        return self._original_position

    @position.setter
    def position(self, val):
        """Set the circle's position."""
        self._position = val

    @property
    def speed(self):
        """Return the circle's speed."""
        return self._speed

    @property
    def inverse_speed(self):
        """Return the circle's inverse speed."""
        return Circle.max_speed - self._speed

    def move_ip(self, x, y):
        """ "Move the circle."""
        self._position = self._position + pygame.math.Vector2(x, y)

    @property
    def rect(self):
        """Return bounding rect."""
        left = self._position.x - self._radius
        top = self._position.y - self._radius
        width = 2 * self._radius
        return pygame.Rect(left, top, width, width)

    @property
    def width(self):
        """Return the width of the bounding box the circle is in."""
        return 2 * self._radius

    @property
    def height(self):
        """Return the height of the bounding box the circle is in."""
        return 2 * self._radius

    def contains(self, point, buffer=0):
        """Return true if point is in the circle + buffer"""
        v = point - self._position
        distance = v.length()
        # assume all circles have the same radius
        seperating_distance = 2 * (self._radius + buffer)
        return distance <= seperating_distance

    def draw(self, screen):
        """Draw the circle to screen."""
        pygame.draw.circle(screen, self._color, self.position, self.radius)

    def __repr__(self):
        """Circle stringify."""
        return f'Circle({repr(self._position)}, {self._radius}, {self._color}, "{self._name}")'


class Player(pygame.sprite.Sprite):
    """Class representing the Player's spaceship with a bounding rect."""

    def __init__(self, position):
        """Initialize the Player object"""
        pygame.sprite.Sprite.__init__(self)
        self.image, self.rect = load_image(assets.get("player"), -1)
        self._position = position
        self.rect.center = self._position
        self._velocity = pygame.math.Vector2(0, 0)

    def update(self):
        """Update the player."""
        v = self._position.x + self._velocity.x
        if v > 0 and v < 800:
            self._position = self._position + self._velocity
            self.rect.center = self._position

    @property
    def position(self):
        """Return the Player's position"""
        return self._position

    def stop(self):
        """Stops the player from moving."""
        self._velocity = pygame.math.Vector2(0, 0)

    def move_left(self):
        """Moves the player left."""
        self._velocity = pygame.math.Vector2(-5, 0)

    def move_right(self):
        """Moves the player right."""
        self._velocity = pygame.math.Vector2(5, 0)


class Enemy:
    """Class respresenting the Enemy with a bounding rect."""

    def __init__(self, center_x, center_y, color, name="None"):
        """Initialize the Enemy object"""
        self._center_x = center_x
        self._center_y = center_y
        self._color = color
        self._name = name
        self._is_exploding = False
        self._position = pygame.math.Vector2(center_x, center_y)
        self._velocity = pygame.math.Vector2(0, 0)
        self._center_x = self._position.x
        self._center_y = self._position.y
        self._speed = 0.01
        self._top_left_vertice = ((self._center_x - 16), (self._center_y - 16))
        self._top_right_vertice = ((self._center_x + 16), (self._center_y - 16))
        self._bottom_vertice = ((self._center_x), (self._center_y + 16))
        self._directions = ["right", "down", "left", "down"]
        self._directions_iterator = cycle(self._directions)
        self._direction = next(self._directions_iterator)
        self._pixels_counter = 0
        self._move_amount = 1

    def update(self):
        """Update the player."""
        if self._direction == "right":
            self.position.x += self._move_amount
            self._pixels_counter += 1
            self.rect.center = self._position
            self._center_x = self._position.x
            self._center_y = self._position.y
            self._top_left_vertice = ((self._center_x - 16), (self._center_y - 16))
            self._top_right_vertice = ((self._center_x + 16), (self._center_y - 16))
            self._bottom_vertice = ((self._center_x), (self._center_y + 16))
            if self._pixels_counter > 176:
                self._pixels_counter = 0
                self._direction = next(self._directions_iterator)
        elif self._direction == "left":
            self._position.x += self._move_amount * -1
            self._pixels_counter += 1
            self.rect.center = self._position
            self._center_x = self._position.x
            self._center_y = self._position.y
            self._top_left_vertice = ((self._center_x - 16), (self._center_y - 16))
            self._top_right_vertice = ((self._center_x + 16), (self._center_y - 16))
            self._bottom_vertice = ((self._center_x), (self._center_y + 16))
            if self._pixels_counter > 176:
                self._pixels_counter = 0
                self._direction = next(self._directions_iterator)
        else:
            self.position.y += self._move_amount
            self._pixels_counter += 1
            self.rect.center = self._position
            self._center_x = self._position.x
            self._center_y = self._position.y
            self._top_left_vertice = ((self._center_x - 16), (self._center_y - 16))
            self._top_right_vertice = ((self._center_x + 16), (self._center_y - 16))
            self._bottom_vertice = ((self._center_x), (self._center_y + 16))
            if self._pixels_counter > 52:
                self._pixels_counter = 0
                self._direction = next(self._directions_iterator)

    @property
    def position(self):
        """Return the Enemy's position"""
        return self._position

    @property
    def rect(self):
        """Return boudning rect."""
        left = self._position.x - 16
        top = self._position.y - 16
        width = 32
        return pygame.Rect(left, top, width, width)

    def draw(self, screen):
        """Draws the enemy to the screen"""
        pygame.draw.polygon(
            screen,
            rgbcolors.maroon,
            [self._top_left_vertice, self._top_right_vertice, self._bottom_vertice],
        )

    def __repr__(self):
        """Enemy stringify"""
        return f'Enemy({self._position.x}, {self._position.y}, {self._color}, "{self._name}")'


# To fix to use with sprites
# class Bullet(pygame.sprite.Sprite):
#     """Class representing a bullet with a bounding rect."""

#     def __init__(self, position, target_position, speed):
#         """Initialize the bullet"""
#         pygame.sprite.Sprite.__init__(self)
#         # self._elapsed_time = 0
#         # self._pulse_time = randint(50, 140)
#         # self.images = load_sprite_sheet(assets.get("bullets"), 16, 16, 2, -1)
#         # self._image_pool = cycle(self.images)
#         # self.image, self.rect = next(self._image_pool)
#         self.images, self.rect = load_image(assets.get("bullet"), -1)
#         self.rect.center = position
#         self._position = pygame.math.Vector2(position)
#         self._position = pygame.math.Vector2(400,400)
#         self._target_position = pygame.math.Vector2(target_position)
#         self._speed = speed

#     def should_die(self):
#         """Checks if the bullet should die"""
#         squared_distance = (self._position - self._target_position).length_squared()
#         return math.isclose(squared_distance, 0.0, rel_tol=1e-01)

#     def update(self, delta_time):
#         """"Updates the bullet"""
#         # self._elapsed_time += delta_time
#         # if self._elapsed_time > self._pulse_time:
#         #     self.image = next(self._image_pool)
#         #     self._elapsed_time = 0
#         self._position.move_towards_ip(self._target_position, self._speed * delta_time)
#         self.rect.center = self._position


class Bullet:
    """Class representing a Bullet"""

    def __init__(self, position, target_position, speed, color=rgbcolors.light_cyan):
        """Initialize the Bullet"""
        self._position = pygame.math.Vector2(position)
        self._target_position = pygame.math.Vector2(target_position)
        self._speed = speed
        self._color = color
        self._radius = 5

    @property
    def rect(self):
        """Return bounding rect."""
        left = self._position.x - self._radius
        top = self._position.y - self._radius
        width = 2 * self._radius
        return pygame.Rect(left, top, width, width)

    def should_die(self):
        """Check if the bullet should die."""
        squared_distance = (self._position - self._target_position).length_squared()
        return math.isclose(squared_distance, 0.0, rel_tol=1e-01)

    def update(self, delta_time):
        """Update the bullet"""
        self._position.move_towards_ip(self._target_position, self._speed * delta_time)

    def draw(self, screen):
        """Draw the circle to screen."""
        pygame.draw.circle(screen, self._color, self._position, self._radius)


class Barricade:
    """Class representing a Barricade with a bounding rect"""

    def __init__(self, center_x, center_y):
        """Initialize the Barricade"""
        self._center_x = center_x
        self._center_y = center_y
        self._color = rgbcolors.navyblue
        self._position = pygame.math.Vector2(center_x, center_y)
        self._top = center_y - 12.5
        self._left = center_x - 50
        self._width = 100
        self._height = 25
        self._rect = pygame.Rect(self._left, self._top, self._width, self._height)

    @property
    def rect(self):
        """Return bounding rect."""
        return self._rect

    def draw(self, screen):
        """Draws the barricade to the screen"""
        pygame.draw.rect(screen, self._color, self._rect)
