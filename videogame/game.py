#!/usr/bin/env python3
# Darren Cruz
# CPSC 386-02
# 2023-04-19
# darrencruz@csu.fullerton.edu
# @darrenjcruz
#
# Lab 05-00
#
# This is the game module that contains the necessary classes.
#


"""Game objects to create PyGame based games."""


import os
import warnings

import pygame

import rgbcolors
from scene import SceneManager, MenuScene, GameScene, HowToPlayScene, LeaderboardScene, LoseScene, WinScene, EnterInitialsScene
import assets


def display_info():
    """Print out information about the display driver and video information."""
    print(f'The display is using the "{pygame.display.get_driver()}" driver.')
    print("Video Info:")
    print(pygame.display.Info())


# If you're interested in using abstract base classes, feel free to rewrite
# these classes.
# For more information about Python Abstract Base classes, see
# https://docs.python.org/3.8/library/abc.html


class VideoGame:
    """Base class for creating PyGame games."""

    def __init__(
        self,
        window_width=800,
        window_height=800,
        window_title="My Awesome Game",
    ):
        """
        Initializes a new game with the given window size and
        window title.
        """
        pygame.init()
        self._window_size = (window_width, window_height)
        self._clock = pygame.time.Clock()
        self._screen = pygame.display.set_mode(self._window_size)
        self._title = window_title
        pygame.display.set_caption(self._title)
        self._game_is_over = False
        if not pygame.font:
            warnings.warn("Fonts disabled.", RuntimeWarning)
        if not pygame.mixer:
            warnings.warn("Sound disabled.", RuntimeWarning)
        self._scene_graph = None

    @property
    def scene_graph(self):
        """Return the scene graph representing all the scenes in the game."""
        return self._scene_graph

    def build_scene_graph(self):
        """Build the scene graph for the game."""
        # raise NotImplementedError

    def run(self):
        """Run the game; the main game loop."""
        raise NotImplementedError


class MyVideoGame(VideoGame):
    """Show a colored window with a colored message and a polygon."""

    def __init__(self):
        """Init the Pygame demo."""
        super().__init__(800, 800, "Space Invaders")
        self._main_dir = os.path.dirname(__file__)
        self._data_dir = os.path.join(self._main_dir, "data")
        self._soundtrack = assets.get("soundtrack2")
        self._score = 0
        self._lives = 3
        self._next_life = 0
        self._continue_game = False
        self._restart = False
        self._scene_graph = SceneManager(self._score, self._lives, self._next_life)
        self.build_scene_graph()

    def build_scene_graph(self):
        """Build scene graph for the game demo."""
        Menu = MenuScene(
            screen=self._screen,
            scene_manager=self._scene_graph,
            title=self._title,
            title_color=rgbcolors.maroon,
            background_color=rgbcolors.lavender,
        )
        Game = GameScene(
            screen=self._screen,
            scene_manager=self._scene_graph,
            soundtrack=self._soundtrack,
            score=0, lives=3, next_life=0,
        )
        HowToPlay = HowToPlayScene(
            screen=self._screen,
            scene_manager=self._scene_graph,
            title="How To Play",
            title_color=rgbcolors.maroon,
            background_color=rgbcolors.plum,
        )
        Leaderboard = LeaderboardScene(
            screen=self._screen,
            scene_manager=self._scene_graph,
            title="Leaderboard",
            title_color=rgbcolors.maroon,
            background_color=rgbcolors.lavender,
        )
        Lose = LoseScene(
            screen=self._screen,
            scene_manager=self._scene_graph,
            title="You Lose!",
            title_color=rgbcolors.maroon,
            score=0,
            background_color=rgbcolors.lavender,
        )
        Win = WinScene(
            screen=self._screen,
            scene_manager=self._scene_graph,
            title="Cleared the Stage!",
            title_color=rgbcolors.maroon,
            score=0,
            lives=0,
            next_life=0,
            background_color=rgbcolors.lavender,
        )
        EnterInitials = EnterInitialsScene(
            screen=self._screen,
            scene_manager=self._scene_graph,
            title="Enter Your Initials!",
            title_color=rgbcolors.maroon,
            score=0,
            background_color=rgbcolors.lavender,
        )
        self._scene_graph.add([Menu, Game, HowToPlay, Leaderboard, Win, Lose, EnterInitials])
        self._scene_graph.set_next_scene('0')        # raise NotImplementedError

    def run(self):
        """Run the game; the main game loop."""
        scene_iterator = iter(self.scene_graph)
        current_scene = next(scene_iterator)
        while not self._game_is_over:
            current_scene.start_scene()
            current_scene._score = self._score
            current_scene._lives = self._lives
            current_scene._next_life = self._next_life
            current_scene._continue_game = self._continue_game
            current_scene._restart = self._restart
            while current_scene.is_valid():
                current_scene.delta_time = self._clock.tick(current_scene.frame_rate())
                for event in pygame.event.get():
                    current_scene.process_event(event)
                current_scene.update_scene()
                current_scene.draw()
                current_scene.render_updates()
                self._score = current_scene._scene_manager._score
                self._lives = current_scene._scene_manager._lives
                self._next_life = current_scene._scene_manager._next_life
                self._continue_game = current_scene._scene_manager._continue_game
                self._restart = current_scene._scene_manager._restart
                pygame.display.update()
            current_scene.end_scene()
            try:
                current_scene = next(scene_iterator)
            except StopIteration:
                self._game_is_over = True
        pygame.quit()
        return 0