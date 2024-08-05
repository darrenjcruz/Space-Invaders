#!/usr/bin/env python3
# Darren Cruz
# CPSC 386-02
# 2023-04-19
# darrencruz@csu.fullerton.edu
# @darrenjcruz
#
# Lab 05-00
#
# This is the animation module that contains the animation function.
#


"""
Demonstrate how to use sprite sheets to perform some simple
animations in PyGame.
"""

import pygame
import assets


# Adapted aliens.py in pygame/examples
# https://github.com/pygame/pygame/blob/main/examples/aliens.py


class Explosion(pygame.sprite.Sprite):
    """Play an explosion sprite."""

    defaultlife = 12
    animcycle = 3
    images = []

    def __init__(self, actor):
        pygame.sprite.Sprite.__init__(self, self.containers)
        try:
            surface = pygame.image.load(assets.get("explosion2"))
        except pygame.error as pygame_error:
            raise SystemExit(
                f'Could not load image "{assets.get("explosion2")}"'
                + f" {pygame.get_error()}"
            ) from pygame_error
        img = surface.convert()
        if not Explosion.images:
            Explosion.images = [img, pygame.transform.flip(img, 1, 1)]
        self.image = self.images[0]
        self.rect = self.image.get_rect(center=actor.rect.center)
        self.life = Explosion.defaultlife
        self._actor = actor

    def update(self):
        """Update the animation."""
        self.life = self.life - 1
        self.image = self.images[self.life // Explosion.animcycle % 2]
        if self.life <= 0:
            self.kill()
            self._actor.is_exploding = False
