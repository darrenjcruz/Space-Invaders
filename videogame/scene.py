#!/usr/bin/env python3
# Darren Cruz
# CPSC 386-02
# 2023-04-19
# darrencruz@csu.fullerton.edu
# @darrenjcruz
#
# Lab 05-00
#
# This is the scene module for invaders, it contains the Scene class.
#


"""Scene objects for making games with PyGame."""

from collections import namedtuple
import locale
import os
import pickle
import assets
import random
import pygame
import rgbcolors
from objects import Circle, Player, Enemy, Bullet, Barricade
from animation import Explosion


# NOTES
# Scenes:
# 0 - Menu
# 1 - Game
# 2 - How To Play
# 3 - Leaderboard
# 4 - Win Game
# 5 - Lose Game
# 6 - Enter Initials


# If you're interested in using abstract base classes, feel free to rewrite
# these classes.
# For more information about Python Abstract Base classes, see
# https://docs.python.org/3.8/library/abc.html


#Custom pygame events.
#Player lost
LOSE = pygame.USEREVENT + 1
LOSE_Event = pygame.event.Event(LOSE)

#Player Wins
WIN = pygame.USEREVENT + 2
WIN_Event = pygame.event.Event(WIN)

#Score namedtuple for leaderboard
Score = namedtuple("Score", ["score", "initials"])

#pickle_file
main_dir = os.path.dirname(__file__)
data_dir = os.path.join(main_dir, "data")
pickle_file = os.path.join(data_dir, "leaderboard.pkl")
locale.setlocale(locale.LC_ALL, "en_US.UTF-8")


class SceneManager:
    """A class that manages scenes"""
    
    def __init__(self, score, lives, next_life):
        """Initializer for SceneManager"""
        self._scene_dict = {}
        self._current_scene = None
        self._next_scene = None
        self._reloaded = True
        self._score = score
        self._lives = lives
        self._next_life = next_life
        self._continue_game = False
        self._restart = False

    def set_next_scene(self, key):
        """Sets the next scene in the sequence"""
        self._next_scene = self._scene_dict[key]
        self._reloaded = True

    def add(self, scene_list):
        """Adds a list of scenes"""
        for (index, scene) in enumerate(scene_list):
            self._scene_dict[str(index)] = scene
        self._current_scene = self._scene_dict['0']
    
    def update(self, scene_list):
        """Updates the scene dict"""
        self._scene_dict.update(scene_list)
              
    def __iter__(self):
        """Default Iterator"""
        return self
    
    def __next__(self):
        """Next for Iterator"""
        if self._next_scene and self._reloaded:
            self._reloaded = False
            return self._next_scene
        else:
            raise StopIteration


class Scene:
    """Base class for making PyGame Scenes."""

    def __init__(self, screen, background_color, soundtrack=None):
        """Scene initializer"""
        self._screen = screen
        self._background = pygame.Surface(self._screen.get_size())
        self._background.fill(background_color)
        self._frame_rate = 60
        self._is_valid = True
        self._soundtrack = soundtrack
        self._render_updates = None

    def draw(self):
        """Draw the scene."""
        self._screen.blit(self._background, (0, 0))

    def process_event(self, event):
        """Process a game event by the scene."""
        # This should be commented out or removed since it generates a
        # lot of noise.
        # print(str(event))
        if event.type == pygame.QUIT:
            print("Good Bye!")
            self._is_valid = False

    def is_valid(self):
        """Is the scene valid? A valid scene can be used to play a scene."""
        return self._is_valid

    def render_updates(self):
        """Render all sprite updates."""

    def update_scene(self):
        """Update the scene state."""

    def start_scene(self):
        """Start the scene."""
        if self._soundtrack:
            try:
                pygame.mixer.music.load(self._soundtrack)
                pygame.mixer.music.set_volume(0.2)
            except pygame.error as pygame_error:
                print("Cannot open the mixer?")
                raise SystemExit("broken!!") from pygame_error
            pygame.mixer.music.play(-1)

    def end_scene(self):
        """End the scene."""
        if self._soundtrack and pygame.mixer.music.get_busy():
            # Fade music out so there isn't an audible pop
            pygame.mixer.music.fadeout(500)
            pygame.mixer.music.stop()

    def frame_rate(self):
        """Return the frame rate the scene desires."""
        return self._frame_rate


class PressAnyKeyToExitScene(Scene):
    """Empty scene where it will invalidate when a key is pressed."""

    def process_event(self, event):
        """Process game events."""
        super().process_event(event)
        if event.type == pygame.KEYDOWN:
            self._is_valid = False


class MenuScene(Scene):
    """Scene with a title string and a polygon."""

    def __init__(
        self,
        screen,
        scene_manager,
        title,
        title_color=rgbcolors.ghostwhite,
        title_size=72,
        background_color=rgbcolors.papaya_whip,
        soundtrack=None,
    ):
        """Initialize the scene."""
        super().__init__(screen,
                         background_color,
                         soundtrack)
        self._scene_manager = scene_manager
        self._next_key = '1'
        self._score = 0
        self._lives = 3
        self._next_life = 0
        self._title_font = pygame.font.Font(
            pygame.font.get_default_font(), title_size
            )
        self._title = self._title_font.render(title, True, title_color)
        self._subtitle_font = pygame.font.Font(
            pygame.font.get_default_font(), 24
            )
        self._subtitle = self._subtitle_font.render(
            "Programmed by Darren Cruz", True, rgbcolors.honeydew3
            )
        self._play_font = pygame.font.Font(
            pygame.font.get_default_font(), 24
            )
        self._play = self._play_font.render(
            "[P] Play", True, rgbcolors.black
            )
        self._how_to_play_font = pygame.font.Font(
            pygame.font.get_default_font(), 24
            )
        self._how_to_play = self._how_to_play_font.render(
            "[H] How to Play", True, rgbcolors.black
            )
        self._leaderboard_font = pygame.font.Font(
            pygame.font.get_default_font(), 24
            )
        self._leaderboard = self._leaderboard_font.render(
            "[L] Leaderboard", True, rgbcolors.black
            )
        self._quit_font = pygame.font.Font(
            pygame.font.get_default_font(), 24
            )
        self._quit = self._quit_font.render(
            "[Q] Quit", True, rgbcolors.black
            )

    def draw(self):
        """Draw the scene."""
        super().draw()

        # title
        self._screen.blit(
            self._title,
            (
                400 - self._title.get_width() // 2,
                200 - self._title.get_height() // 2
            ),
        )

        # subtitle
        self._screen.blit(
            self._subtitle,
            (
                400 - self._subtitle.get_width() // 2,
                250 - self._subtitle.get_height() // 2,
            )
        )
        
        # [P] Play
        self._screen.blit(
            self._play,
            (
                400 - self._play.get_width() // 2,
                400 - self._play.get_height() // 2,
            ),
        )

        # [H] How to Play
        self._screen.blit(
            self._how_to_play,
            (
                400 - self._how_to_play.get_width() // 2,
                440 - self._how_to_play.get_height() // 2,
            )
        )

        # [L] Leaderboard
        self._screen.blit(
            self._leaderboard,
            (
                400 - self._leaderboard.get_width() // 2,
                480 - self._leaderboard.get_height() //2,
            ),
        )

        # [Q] Quit
        self._screen.blit(
            self._quit,
            (
                400 - self._quit.get_width() // 2,
                520 - self._quit.get_height() // 2,
            ),
        )

    def end_scene(self):
        """End the scene"""
        super().end_scene()
        self._is_valid = True

    def process_event(self, event):
        """Process Keyboard events."""
        if event.type == pygame.KEYDOWN and event.key == pygame.K_p:
            self._scene_manager._restart = True
            self._scene_manager.set_next_scene('1')
            self._is_valid = False
        elif event.type == pygame.KEYDOWN and event.key == pygame.K_h:
            self._scene_manager.set_next_scene('2')
            self._is_valid = False
        elif event.type == pygame.KEYDOWN and event.key == pygame.K_l:
            self._scene_manager.set_next_scene('3')
            self._is_valid = False
        elif event.type == pygame.KEYDOWN and event.key == pygame.K_q:
            print("Bye bye!")
            self._is_valid = False
        else:
            super().process_event(event)


class GameScene(Scene):
    """Main gameplay scene"""
    spriteson = True
    def __init__(
            self,
            screen,
            scene_manager,
            score=0,
            lives=3,
            next_life=0,
            background_color=rgbcolors.plum,
            soundtrack=None,
            continue_game=False,
            restart=False
        ):
        """"Initialize the scene"""
        super().__init__(screen,
                         background_color,
                         soundtrack)
        self._scene_manager = scene_manager
        self._next_key = '2'
        self._barricades = []
        self._enemies = []
        self._explsion_sound = pygame.mixer.Sound(assets.get("explosionsfx"))
        self._delta_time = 0
        self._continue_game = continue_game
        self._restart = restart

        self._player_bullets = []
        self._last_enemy_shot = pygame.time.get_ticks()
        self._enemy_cooldown = 1000
        self._enemy_bullets = []
        self.width = self._screen.get_size()[0]
        self.height = self._screen.get_size()[1]
        self._is_game_over = False

        self._score = score
        self._lives = lives
        self._next_life = next_life

        self._score_text_text = str(score)
        self._score_font = pygame.font.Font(
            pygame.font.get_default_font(), 18
        )
        self._score_text = self._score_font.render(self._score_text_text, True, rgbcolors.ghostwhite)        
        
        self._lives = lives
        self._lives_text_text = str(self._lives)
        self._lives_font = pygame.font.Font(
            pygame.font.get_default_font(), 18
        )
        self._lives_text = self._lives_font.render(self._lives_text_text, True, rgbcolors.ghostwhite)  
        
        self._press_m_for_menu_font = pygame.font.Font(
            pygame.font.get_default_font(), 18
        )
        self._press_m_for_menu = self._press_m_for_menu_font.render(
            "[M] Main Menu", True, rgbcolors.black
        )
        
        self._player = Player(pygame.math.Vector2(self.width//2, self.height-50))
        self.make_barricades()
        self.make_enemies()
        
        if GameScene.spriteson:
            self._render_updates = pygame.sprite.RenderUpdates(self._player)
            Explosion.containers = self._render_updates
        else:
            self._render_updates = None

    def make_enemies(self):
        """Makes all enemies."""
        gutter_width = 20
        enemy_width = 32
        x_step = gutter_width + enemy_width
        y_step = gutter_width + enemy_width
        enemies_per_row = 11
        num_rows = 5
        self._enemies = [
            Enemy(
                x_step + (j * x_step),
                y_step + (i * y_step),
                rgbcolors.maroon,
                f"{i+1}, {j+1}",
            )
            for i in range(num_rows)
            for j in range(enemies_per_row)
        ]

    def make_barricades(self):
        """Makes all barricades."""
        gutter_width = 80
        barricade_width = 100
        x_step = gutter_width + barricade_width
        barricades = 4
        self._barricades = [
            Barricade(
                (gutter_width + barricade_width // 2) + (j * x_step),
                700,
            )
            for j in range(barricades)
        ]
    
    @property
    def delta_time(self):
        """delta_time getter"""
        return self._delta_time
    
    @delta_time.setter
    def delta_time(self, val):
        """delta_time setter"""
        self._delta_time = val

    def end_scene(self):
        """End the scene"""
        super().end_scene()
        self._is_valid = True

    def process_event(self, event):
        """Process game events."""
        if event.type == pygame.KEYDOWN and event.key == pygame.K_RIGHT:
            self._player.move_right()
        elif event.type == pygame.KEYUP and event.key == pygame.K_RIGHT:
            self._player.stop()
        elif event.type == pygame.KEYDOWN and event.key == pygame.K_LEFT:
            self._player.move_left()
        elif event.type == pygame.KEYUP and event.key == pygame.K_LEFT:
            self._player.stop()
        elif event.type == pygame.KEYDOWN and event.key == pygame.K_SPACE:
            bullet_target = self._player.position - pygame.math.Vector2(0, self.height)
            velocity = 0.25
            self._player_bullets.append(Bullet(self._player.position, bullet_target, velocity))
        elif event.type == pygame.KEYDOWN and event.key == pygame.K_m:
            self._scene_manager.set_next_scene('0')
            self._is_valid = False
        elif event.type == LOSE:
            self._scene_manager._score = self._score
            self._scene_manager._lives = self._lives
            self._scene_manager._next_life = self._next_life
            self._scene_manager.set_next_scene('5')
            self._is_valid = False
        elif event.type == WIN:
            self._scene_manager._score = self._score
            self._scene_manager._lives = self._lives
            self._scene_manager._next_life = self._next_life
            self._scene_manager.set_next_scene('4')
            self._is_valid = False
        else:
            super().process_event(event)
    
    def update_scene(self):
        """Update the scene"""
        super().update_scene()
        self._player.update()
        self._restart = self._scene_manager._restart

        if (self._continue_game == True):
            print("continued")
            self._player_bullets = []
            self._enemy_bullets = []
            self.make_enemies()
            self._lives_text_text = str(self._lives)
            self._lives_text = self._lives_font.render(self._lives_text_text, True, rgbcolors.ghostwhite)
            self._score_text_text = str(self._score)
            self._score_text = self._score_font.render(self._score_text_text, True, rgbcolors.ghostwhite)
            self._continue_game = False

        if (self._restart == True):
            print("restarted")
            self._player_bullets = []
            self._enemy_bullets = []
            self.make_enemies()
            self._score = 0
            self._lives = 3
            self._next_life = 0
            self._lives_text_text = str(self._lives)
            self._lives_text = self._lives_font.render(self._lives_text_text, True, rgbcolors.ghostwhite)
            self._score_text_text = str(self._score)
            self._score_text = self._score_font.render(self._score_text_text, True, rgbcolors.ghostwhite)
            self._restart = False
            self._scene_manager._restart = False

        for enemy in self._enemies:
            enemy.update()
            index_player = enemy.rect.collidelist([self._player.rect])
            if index_player > -1:
                self._enemies.remove(enemy)
                Explosion(self._player)
                self._explsion_sound.play()
                self._lives -= 1
                self._lives_text_text = str(self._lives)
                self._lives_text = self._lives_font.render(self._lives_text_text, True, rgbcolors.ghostwhite)
            if enemy.position.y > 760:
                self._enemies.remove(enemy)
                self._is_game_over = True
                self._lives = 0
                self._lives_text_text = str(self._lives)
                self._lives_text = self._lives_font.render(self._lives_text_text, True, rgbcolors.ghostwhite)
                pygame.event.post(LOSE_Event)

        time_now = pygame.time.get_ticks()
        if time_now - self._last_enemy_shot > self._enemy_cooldown and len(self._enemy_bullets) < 5 and len(self._enemies) > 0:
            chosen_enemy = random.choice(self._enemies)
            bullet_target = chosen_enemy.position + pygame.math.Vector2(0, 760 - chosen_enemy.position.y)
            velocity = 0.25
            self._enemy_bullets.append(Bullet(chosen_enemy.position, bullet_target, velocity, rgbcolors.coral))
            self._last_enemy_shot = time_now
    
        for bullet in self._player_bullets:
            bullet.update(self.delta_time)
            if bullet.should_die():
                self._player_bullets.remove(bullet)
            else:
                index_barricade = bullet.rect.collidelist([b.rect for b in self._barricades])
                if index_barricade > -1:
                    self._player_bullets.remove(bullet)
                index_enemy = bullet.rect.collidelist([e.rect for e in self._enemies])
                if index_enemy > -1:
                    Explosion(self._enemies[index_enemy])
                    self._explsion_sound.play()
                    self._enemies[index_enemy].is_exploding = True
                    # remove an enemy
                    self._enemies.remove(self._enemies[index_enemy])
                    # self._explosion_sound.play()
                    # remove a bullet
                    self._player_bullets.remove(bullet)
                    self._score += 10
                    self._next_life += 10
                    # add an extra life after every 500 points
                    if self._next_life == 500:
                        self._lives += 1
                        self._next_life = 0
                        self._lives_text_text = str(self._lives)
                        self._lives_text = self._lives_font.render(self._lives_text_text, True, rgbcolors.ghostwhite)
                    self._score_text_text = str(self._score)
                    self._score_text = self._score_font.render(self._score_text_text, True, rgbcolors.ghostwhite)
        
        for bullet in self._enemy_bullets:
            bullet.update(self._delta_time)
            if bullet.should_die():
                self._enemy_bullets.remove(bullet)
            else:
                index_barricade = bullet.rect.collidelist([b.rect for b in self._barricades])
                if index_barricade > -1:
                    self._enemy_bullets.remove(bullet)
                index_player = bullet.rect.collidelist([self._player.rect])
                if index_player > -1:
                    self._enemy_bullets.remove(bullet)
                    Explosion(self._player)
                    self._explsion_sound.play()
                    # self._player.is_exploding = True
                    self._lives -= 1
                    self._lives_text_text = str(self._lives)
                    self._lives_text = self._lives_font.render(self._lives_text_text, True, rgbcolors.ghostwhite)
        
        if self._lives == 0:
            self._is_game_over = True
            pygame.event.post(LOSE_Event)

        if len(self._enemies) == 0:
            self._is_game_over = True
            pygame.event.post(WIN_Event)
    
    def draw(self):
        """Draw the scene."""
        super().draw()
        # if not self._render_updates:

        #draw enemies
        for enemy in self._enemies:
            if not enemy._is_exploding:
                enemy.draw(self._screen)

        #draw barricades
        for barricade in self._barricades:
            barricade.draw(self._screen)

        #draw player bullets
        for bullet in self._player_bullets:
            bullet.draw(self._screen)

        #draw enemy bullets
        for bullet in self._enemy_bullets:
            bullet.draw(self._screen)

        #blit the score
        self._screen.blit(
            self._score_text,
            (
                715,
                775
            ),
        )

        #blit "[M] for Menu"
        self._screen.blit(
            self._press_m_for_menu,
            (
                400 - self._press_m_for_menu.get_width() // 2,
                775,
            ),
        )

        #blit lives
        self._screen.blit(
            self._lives_text,
            (
                15,
                775
            )
        )
        pygame.draw.polygon(self._screen, rgbcolors.maroon4, [(38,792),(30,784),(30,779),(33,776),(35,776),(38,779),(41,776),(43,776),(46,779),(46,784)])


    def render_updates(self):
        """Render updates"""
        if self._render_updates:
            super().render_updates()
            # if self._render_updates:
            self._render_updates.clear(self._screen, self._background)
            self._render_updates.update()
            dirty = self._render_updates.draw(self._screen)


class HowToPlayScene(Scene):
    """Scene for instructions."""

    def __init__(
        self,
        screen,
        scene_manager,
        title,
        title_color=rgbcolors.ghostwhite,
        title_size=72,
        background_color=rgbcolors.papaya_whip,
        soundtrack=None,
    ):
        """Initalize the scene."""
        super().__init__(screen,
                         background_color,
                         soundtrack)
        self._scene_manager = scene_manager
        self._next_key = '0'
        
        self._title_font = pygame.font.Font(
            pygame.font.get_default_font(), title_size
            )
        self._title = self._title_font.render(title, True, title_color)
        self._legend_font = pygame.font.Font(
            pygame.font.get_default_font(), 36
            )
        self._legend = self._legend_font.render(
            "Legend: ", True, rgbcolors.maroon
            )
        self._player = Player(pygame.math.Vector2(84, 359))
        self._render_updates = pygame.sprite.RenderUpdates(self._player)

        self._you_font = pygame.font.Font(
            pygame.font.get_default_font(), 24
            )
        self._you = self._you_font.render(
            "--- YOU", True, rgbcolors.black
        )
        self._enemy = Enemy(84, 409, rgbcolors.maroon)

        self._enemy_text_font = pygame.font.Font(
            pygame.font.get_default_font(), 24
        )
        self._enemy_text = self._enemy_text_font.render(
            "--- ENEMY", True, rgbcolors.black
        )

        self._barricade = Barricade(84, 459)
        self._barricade_text_font = pygame.font.Font(
            pygame.font.get_default_font(), 24
        )
        self._barricade_text = self._barricade_text_font.render(
            "--- BARRICADE", True, rgbcolors.black
        )

        self._your_bullet_font = pygame.font.Font(
            pygame.font.get_default_font(), 24
        )
        self._your_bullet = self._your_bullet_font.render(
            "--- YOUR BULLET", True, rgbcolors.black
        )

        self._enemy_bullet_font = pygame.font.Font(
            pygame.font.get_default_font(), 24
        )
        self._enemy_bullet = self._your_bullet_font.render(
            "--- ENEMY BULLET", True, rgbcolors.black
        )

        self._goal_font = pygame.font.Font(
            pygame.font.get_default_font(), 36
            )
        self._goal = self._goal_font.render(
            "Goal: ", True, rgbcolors.maroon
            )
        
        self._goal_1_font = pygame.font.Font(
            pygame.font.get_default_font(), 24
            )
        self._goal_1 = self._goal_1_font.render(
            "Kill all enemies on the screen", True, rgbcolors.black
            )
        
        self._goal_2_font = pygame.font.Font(
            pygame.font.get_default_font(), 24
            )
        self._goal_2 = self._goal_2_font.render(
            "You lose if all your lives are", True, rgbcolors.black
            )
        
        self._goal_3_font = pygame.font.Font(
            pygame.font.get_default_font(), 24
            )
        self._goal_3 = self._goal_3_font.render(
            "are gone or if an enemy reaches", True, rgbcolors.black
            )

        self._goal_4_font = pygame.font.Font(
            pygame.font.get_default_font(), 24
            )
        self._goal_4 = self._goal_4_font.render(
            "the bottom.", True, rgbcolors.black
            )
        
        self._goal_5_font = pygame.font.Font(
            pygame.font.get_default_font(), 24
            )
        self._goal_5 = self._goal_5_font.render(
            "The barricade stops bullets", True, rgbcolors.black
            )
        
        self._goal_6_font = pygame.font.Font(
            pygame.font.get_default_font(), 24
            )
        self._goal_6 = self._goal_6_font.render(
            "from passing.", True, rgbcolors.black
            )
        
        self._goal_7_font = pygame.font.Font(
            pygame.font.get_default_font(), 24
            )
        self._goal_7 = self._goal_7_font.render(
            "You get an extra life every", True, rgbcolors.black
            )
        
        self._goal_8_font = pygame.font.Font(
            pygame.font.get_default_font(), 24
            )
        self._goal_8 = self._goal_8_font.render(
            "500 points.", True, rgbcolors.black
            )
        
        self._controls_font = pygame.font.Font(
            pygame.font.get_default_font(), 36
            )
        self._controls = self._controls_font.render(
            "Controls:", True, rgbcolors.maroon
            )
        
        self._left_font = pygame.font.Font(
            pygame.font.get_default_font(), 24
            )
        self._left = self._left_font.render(
            "[<-] --- Move Left", True, rgbcolors.black
            )
        
        self._right_font = pygame.font.Font(
            pygame.font.get_default_font(), 24
            )
        self._right = self._right_font.render(
            "[->] --- Move Right", True, rgbcolors.black
            )
        
        self._shoot_font = pygame.font.Font(
            pygame.font.get_default_font(), 24
            )
        self._shoot = self._shoot_font.render(
            "[SPACE] --- Shoot", True, rgbcolors.black
            )
        
        self._press_m_for_menu_font = pygame.font.Font(
            pygame.font.get_default_font(), 18
        )
        self._press_m_for_menu = self._press_m_for_menu_font.render(
            "[ESC] or [M] Main Menu", True, rgbcolors.black
        )
    
    def draw(self):
        """Draw the scene."""
        super().draw()

        # title
        self._screen.blit(
            self._title,
            (
                400 - self._title.get_width() // 2,
                150 - self._title.get_height() // 2
            ),
        )

        # Legend
        self._screen.blit(
            self._legend,
            (
                200 - self._legend.get_width() // 2,
                300 - self._legend.get_height() // 2,
            ),
        )

        # --- YOU
        self._screen.blit(
            self._you,
            (
                150,
                359 - self._you.get_height() // 2,
            ),
        )
    
        self._enemy.draw(self._screen)
        
        # --- ENEMY
        self._screen.blit(
            self._enemy_text,
            (
                150,
                409 - self._enemy_text.get_height() // 2,
            ),
        )

        self._barricade.draw(self._screen)

        # --- BARRICADE
        self._screen.blit(
            self._barricade_text,
            (
                150,
                459 - self._barricade_text.get_height() // 2,
            ),
        )

        pygame.draw.circle(self._screen, rgbcolors.light_cyan, (84, 509), 5)

        # --- YOUR BULLET
        self._screen.blit(
            self._your_bullet,
            (
                150,
                509 - self._your_bullet.get_height() // 2,
            )
        )

        pygame.draw.circle(self._screen, rgbcolors.coral, (84, 559), 5)

        # --- YOUR BULLET
        self._screen.blit(
            self._enemy_bullet,
            (
                150,
                559 - self._enemy_bullet.get_height() // 2,
            )
        )

        # Goal
        self._screen.blit(
            self._goal,
            (
                600 - self._goal.get_width() // 2,
                300 - self._goal.get_height() // 2,
            ),
        )

        # Goal 1
        self._screen.blit(
            self._goal_1,
            (
                600 - self._goal_1.get_width() // 2,
                359 - self._goal_1.get_height() // 2,
            ),
        )

        # Goal 2
        self._screen.blit(
            self._goal_2,
            (
                600 - self._goal_2.get_width() // 2,
                384 - self._goal_2.get_height() // 2,
            ),
        )

        # Goal 3
        self._screen.blit(
            self._goal_3,
            (
                600 - self._goal_3.get_width() // 2,
                409 - self._goal_3.get_height() // 2,
            ),
        )

        # Goal 4
        self._screen.blit(
            self._goal_4,
            (
                600 - self._goal_4.get_width() // 2,
                434 - self._goal_4.get_height() // 2,
            ),
        )

        # Goal 5
        self._screen.blit(
            self._goal_5,
            (
                600 - self._goal_5.get_width() // 2,
                459 - self._goal_5.get_height() // 2,
            ),
        )

        # Goal 6
        self._screen.blit(
            self._goal_6,
            (
                600 - self._goal_6.get_width() // 2,
                484 - self._goal_6.get_height() // 2,
            ),
        )

        # Goal 7
        self._screen.blit(
            self._goal_7,
            (
                600 - self._goal_7.get_width() // 2,
                509 - self._goal_7.get_height() // 2,
            ),
        )

        # Goal 5
        self._screen.blit(
            self._goal_5,
            (
                600 - self._goal_5.get_width() // 2,
                534 - self._goal_5.get_height() // 2,
            ),
        )

        # Controls
        self._screen.blit(
            self._controls,
            (
                400 - self._controls.get_width() // 2,
                600 - self._controls.get_height() // 2,
            )
        )

        # Left
        self._screen.blit(
            self._left,
            (
                400 - self._left.get_width() // 2,
                649 - self._left.get_height() // 2,
            )
        )

        # Right
        self._screen.blit(
            self._right,
            (
                400 - self._right.get_width() // 2,
                679 - self._right.get_height() // 2,
            )
        )

        # Shoot
        self._screen.blit(
            self._shoot,
            (
                400 - self._shoot.get_width() // 2,
                709 - self._shoot.get_height() // 2,
            )
        )

        #[M] for Menu
        self._screen.blit(
            self._press_m_for_menu,
            (
                400 - self._press_m_for_menu.get_width() // 2,
                775,
            ),
        )

    def end_scene(self):
        """End the scene"""
        super().end_scene()
        self._is_valid = True

    def process_event(self, event):
        """Process Keyboard events."""
        if event.type == pygame.KEYDOWN and event.key == pygame.K_m:
            self._scene_manager.set_next_scene(self._next_key)
            self._is_valid = False
        if event.type == pygame.KEYDOWN and event.key == pygame.K_ESCAPE:
            self._scene_manager.set_next_scene(self._next_key)
            self._is_valid = False
        else:
            super().process_event(event)

    def render_updates(self):
        """Render updates"""
        if self._render_updates:
            super().render_updates()
            # if self._render_updates:
            self._render_updates.clear(self._screen, self._background)
            self._render_updates.update()
            dirty = self._render_updates.draw(self._screen)


class LeaderboardScene(Scene):
    """Scene for the leaderboard """

    def __init__(
        self,
        screen,
        scene_manager,
        title,
        title_color=rgbcolors.ghostwhite,
        title_size=72,
        background_color=rgbcolors.papaya_whip,
        soundtrack=None,
    ):
        """Initialize the scene."""
        super().__init__(screen,
                         background_color,
                         soundtrack)
        self._scene_manager = scene_manager
        self._next_key = '0'
        
        self._title_font = pygame.font.Font(
            pygame.font.get_default_font(), title_size
            )
        self._title = self._title_font.render(title, True, title_color)

        self._press_m_for_menu_font = pygame.font.Font(
            pygame.font.get_default_font(), 18
        )
        self._press_m_for_menu = self._press_m_for_menu_font.render(
            "[ESC] or [M] Main Menu", True, rgbcolors.black
        )

    def draw(self):
        """Draw the scene."""
        super().draw()

        self._leaderboard = []
        
        if os.path.exists(pickle_file):
            with open(pickle_file, "rb") as opened:
                leaderboard = pickle.load(opened)
            for player in leaderboard:
                self._leaderboard.append(player)

        self._leaderboard = sorted(self._leaderboard, key=lambda x: x.score, reverse=True)

        # title
        self._screen.blit(
            self._title,
            (
                400 - self._title.get_width() // 2,
                150 - self._title.get_height() // 2
            ),
        )

        if len(self._leaderboard) > 0:
            self._leaderboard_1_font = pygame.font.Font(
                pygame.font.get_default_font(), 36
                )
            self._leaderboard_1 = self._leaderboard_1_font.render(
                f"1. {self._leaderboard[0].initials} ----- {self._leaderboard[0].score}", True, rgbcolors.black
            )

        if len(self._leaderboard) > 1:
            self._leaderboard_2_font = pygame.font.Font(
                pygame.font.get_default_font(), 36
                )
            self._leaderboard_2 = self._leaderboard_2_font.render(
                f"2. {self._leaderboard[1].initials} ----- {self._leaderboard[1].score}", True, rgbcolors.black
            )

        if len(self._leaderboard) > 2:
            self._leaderboard_3_font = pygame.font.Font(
                pygame.font.get_default_font(), 36
                )
            self._leaderboard_3 = self._leaderboard_3_font.render(
                f"3. {self._leaderboard[2].initials} ----- {self._leaderboard[2].score}", True, rgbcolors.black
            )

        if len(self._leaderboard) > 3:
            self._leaderboard_4_font = pygame.font.Font(
                pygame.font.get_default_font(), 36
                )
            self._leaderboard_4 = self._leaderboard_4_font.render(
                f"4. {self._leaderboard[3].initials} ----- {self._leaderboard[3].score}", True, rgbcolors.black
            )

        if len(self._leaderboard) > 4:
            self._leaderboard_5_font = pygame.font.Font(
                pygame.font.get_default_font(), 36
                )
            self._leaderboard_5 = self._leaderboard_5_font.render(
                f"5. {self._leaderboard[4].initials} ----- {self._leaderboard[4].score}", True, rgbcolors.black
            )

        if len(self._leaderboard) > 5:
            self._leaderboard_6_font = pygame.font.Font(
                pygame.font.get_default_font(), 36
                )
            self._leaderboard_6 = self._leaderboard_6_font.render(
                f"6. {self._leaderboard[5].initials} ----- {self._leaderboard[5].score}", True, rgbcolors.black
            )

        if len(self._leaderboard) > 6:
            self._leaderboard_7_font = pygame.font.Font(
                pygame.font.get_default_font(), 36
                )
            self._leaderboard_7 = self._leaderboard_7_font.render(
                f"7. {self._leaderboard[6].initials} ----- {self._leaderboard[6].score}", True, rgbcolors.black
            )

        if len(self._leaderboard) > 7:
            self._leaderboard_8_font = pygame.font.Font(
                pygame.font.get_default_font(), 36
                )
            self._leaderboard_8 = self._leaderboard_8_font.render(
                f"8. {self._leaderboard[7].initials} ----- {self._leaderboard[7].score}", True, rgbcolors.black
            )

        if len(self._leaderboard) > 8:
            self._leaderboard_9_font = pygame.font.Font(
                pygame.font.get_default_font(), 36
                )
            self._leaderboard_9 = self._leaderboard_9_font.render(
                f"9. {self._leaderboard[8].initials} ----- {self._leaderboard[8].score}", True, rgbcolors.black
            )

        if len(self._leaderboard) > 9:
            self._leaderboard_10_font = pygame.font.Font(
                pygame.font.get_default_font(), 36
                )
            self._leaderboard_10 = self._leaderboard_10_font.render(
                f"10. {self._leaderboard[9].initials} ----- {self._leaderboard[9].score}", True, rgbcolors.black
            )

        if len(self._leaderboard) > 0:
            # Leaderboard 1
            self._screen.blit(
                self._leaderboard_1,
                (
                    400 - self._leaderboard_1.get_width() // 2,
                    225 - self._leaderboard_1.get_height() // 2,
                )
            )

        if len(self._leaderboard) > 1:
            # Leaderboard 2
            self._screen.blit(
                self._leaderboard_2,
                (
                    400 - self._leaderboard_2.get_width() // 2,
                    275 - self._leaderboard_2.get_height() // 2,
                )
            )

        if len(self._leaderboard) > 2:
            # Leaderboard 3
            self._screen.blit(
                self._leaderboard_3,
                (
                    400 - self._leaderboard_3.get_width() // 2,
                    325 - self._leaderboard_3.get_height() // 2,
                )
            )

        if len(self._leaderboard) > 3:
            # Leaderboard 4
            self._screen.blit(
                self._leaderboard_4,
                (
                    400 - self._leaderboard_4.get_width() // 2,
                    375 - self._leaderboard_4.get_height() // 2,
                )
            )

        if len(self._leaderboard) > 4:
            # Leaderboard 5
            self._screen.blit(
                self._leaderboard_5,
                (
                    400 - self._leaderboard_5.get_width() // 2,
                    425 - self._leaderboard_5.get_height() // 2,
                )
            )

        if len(self._leaderboard) > 5:
            # Leaderboard 6
            self._screen.blit(
                self._leaderboard_6,
                (
                    400 - self._leaderboard_6.get_width() // 2,
                    475 - self._leaderboard_6.get_height() // 2,
                )
            )

        if len(self._leaderboard) > 6:
            # Leaderboard 7
            self._screen.blit(
                self._leaderboard_7,
                (
                    400 - self._leaderboard_7.get_width() // 2,
                    525 - self._leaderboard_7.get_height() // 2,
                )
            )

        if len(self._leaderboard) > 7:
            # Leaderboard 8
            self._screen.blit(
                self._leaderboard_8,
                (
                    400 - self._leaderboard_8.get_width() // 2,
                    575 - self._leaderboard_8.get_height() // 2,
                )
            )

        if len(self._leaderboard) > 8:
            # Leaderboard 9
            self._screen.blit(
                self._leaderboard_9,
                (
                    400 - self._leaderboard_9.get_width() // 2,
                    625 - self._leaderboard_9.get_height() // 2,
                )
            )

        if len(self._leaderboard) > 9:
            # Leaderboard 10
            self._screen.blit(
                self._leaderboard_10,
                (
                    400 - self._leaderboard_10.get_width() // 2,
                    675 - self._leaderboard_10.get_height() // 2,
                )
            )

        #[M] for Menu
        self._screen.blit(
            self._press_m_for_menu,
            (
                400 - self._press_m_for_menu.get_width() // 2,
                775,
            ),
        )

    def end_scene(self):
        """End the scene"""
        super().end_scene()
        self._is_valid = True

    def process_event(self, event):
        """Process Keyboard events."""
        if event.type == pygame.KEYDOWN and event.key == pygame.K_m:
            self._scene_manager.set_next_scene(self._next_key)
            self._is_valid = False
        if event.type == pygame.KEYDOWN and event.key == pygame.K_ESCAPE:
            self._scene_manager.set_next_scene(self._next_key)
            self._is_valid = False
        else:
            super().process_event(event)


class WinScene(Scene):
    """Scene for when the player wins."""

    def __init__(
        self,
        screen,
        scene_manager,
        title,
        score,
        lives,
        next_life,
        title_color=rgbcolors.ghostwhite,
        title_size=72,
        background_color=rgbcolors.papaya_whip,
        soundtrack=None,
    ):
        """Initialize the scene."""
        super().__init__(screen,
                         background_color,
                         soundtrack)
        self._scene_manager = scene_manager
        self._next_key = '1'
        self._score = score
        self._lives = lives
        self._next_life = next_life
        self._title_font = pygame.font.Font(
            pygame.font.get_default_font(), title_size
            )
        self._title = self._title_font.render(title, True, title_color)

        self._continue_font = pygame.font.Font(
            pygame.font.get_default_font(), 24
            )
        self._continue = self._continue_font.render(
            "[C] Continue", True, rgbcolors.black
            )
        self._end_game_font = pygame.font.Font(
            pygame.font.get_default_font(), 24
            )
        self._end_game = self._end_game_font.render(
            "[E] End the game", True, rgbcolors.black
        )

    def draw(self):
        """Draw the scene."""
        super().draw()

        # title
        self._screen.blit(
            self._title,
            (
                400 - self._title.get_width() // 2,
                360 - self._title.get_height() // 2
            ),
        )

        # [C] Continue
        self._screen.blit(
            self._continue,
            (
                400 - self._continue.get_width() // 2,
                440 - self._continue.get_height() // 2,
            ),
        )

        # [E] End the game
        self._screen.blit(
            self._end_game,
            (
                400 - self._end_game.get_width() // 2,
                480 - self._end_game.get_height() // 2,
            ),
        )

    def end_scene(self):
        """End the scene"""
        super().end_scene()
        self._is_valid = True

    def process_event(self, event):
        """Process Keyboard events."""
        if event.type == pygame.KEYDOWN and event.key == pygame.K_c:
            self._scene_manager._continue_game = True
            self._scene_manager.set_next_scene(self._next_key)
            self._is_valid = False
        elif event.type == pygame.KEYDOWN and event.key == pygame.K_e:
            self._scene_manager.set_next_scene('6')
            self._is_valid = False
        else:
            super().process_event(event)


class LoseScene(Scene):
    """Scene for when the player loses."""

    def __init__(
        self,
        screen,
        scene_manager,
        title,
        score,
        title_color=rgbcolors.ghostwhite,
        title_size=72,
        background_color=rgbcolors.papaya_whip,
        soundtrack=None,
    ):
        """Initialize the scene."""
        super().__init__(screen,
                         background_color,
                         soundtrack)
        self._scene_manager = scene_manager
        self._next_key = '6'
        self._score = score
        self._title_font = pygame.font.Font(
            pygame.font.get_default_font(), title_size
            )
        self._title = self._title_font.render(title, True, title_color)

        self._press_enter_to_continue_font = pygame.font.Font(
            pygame.font.get_default_font(), 24
            )
        self._press_enter_to_continue = self._press_enter_to_continue_font.render(
            "Press Enter to Continue", True, rgbcolors.black
            )

    def draw(self):
        """Draw the scene."""
        super().draw()

        # title
        self._screen.blit(
            self._title,
            (
                400 - self._title.get_width() // 2,
                360 - self._title.get_height() // 2
            ),
        )

        # Press Enter to Continue
        self._screen.blit(
            self._press_enter_to_continue,
            (
                400 - self._press_enter_to_continue.get_width() // 2,
                440 - self._press_enter_to_continue.get_height() // 2,
            ),
        )

    def end_scene(self):
        """End the scene"""
        super().end_scene()
        self._is_valid = True

    def process_event(self, event):
        """Process Keyboard events."""
        if event.type == pygame.KEYDOWN and event.key == pygame.K_RETURN:
            self._scene_manager.set_next_scene(self._next_key)
            self._is_valid = False
        else:
            super().process_event(event)

    def render_updates(self):
        """Render updates"""
        if self._render_updates:
            super().render_updates()
            # if self._render_updates:
            self._render_updates.clear(self._screen, self._background)
            self._render_updates.update()
            dirty = self._render_updates.draw(self._screen)


class EnterInitialsScene(Scene):
    """Scene for when the player loses."""

    def __init__(
        self,
        screen,
        scene_manager,
        title,
        score,
        title_color=rgbcolors.ghostwhite,
        title_size=72,
        background_color=rgbcolors.papaya_whip,
        soundtrack=None,
    ):
        """Initialize the scene."""
        super().__init__(screen,
                         background_color,
                         soundtrack)
        self._scene_manager = scene_manager
        self._next_key = '0'

        self._leaderboard = []
        
        if os.path.exists(pickle_file):
            with open(pickle_file, "rb") as opened:
                leaderboard = pickle.load(opened)
            for player in leaderboard:
                self._leaderboard.append(player)

        self._leaderboard = sorted(self._leaderboard, key=lambda x: x.score, reverse = True)
        
        self._title_font = pygame.font.Font(
            pygame.font.get_default_font(), title_size
            )
        self._title = self._title_font.render(title, True, title_color)

        self._score = score
        self._score_text_font = pygame.font.Font(
            pygame.font.get_default_font(), 60
            )

        self._initials_text =""
        self._initials_text_font = pygame.font.Font(
            pygame.font.get_default_font(), 60
            )
        self._initials = self._initials_text_font.render(
            self._initials_text, True, rgbcolors.black
            )
        self._press_enter_to_submit_score_font = pygame.font.Font(
            pygame.font.get_default_font(), 24
            )
        self._press_enter_to_submit_score = self._press_enter_to_submit_score_font.render(
            "Press Enter to Submit Score", True, rgbcolors.black
            )
        
        self._skip_font = pygame.font.Font(
            pygame.font.get_default_font(), 24
        )
        self._skip = self._skip_font.render(
            "[/] to skip", True, rgbcolors.black
        )
        
        self._leaderboard_text_font = pygame.font.Font(
            pygame.font.get_default_font(), 48
        )
        self._leaderboard_text = self._leaderboard_text_font.render(
            "Leaderboard:", True, rgbcolors.maroon
        )

    def draw(self):
        """Draw the scene."""
        super().draw()
        self._leaderboard = sorted(self._leaderboard, key=lambda x: x.score, reverse = True)

        # title
        self._screen.blit(
            self._title,
            (
                400 - self._title.get_width() // 2,
                200 - self._title.get_height() // 2
            ),
        )

        # Score: _______
        self._score_text = self._score_text_font.render(
            f"Score: {self._score}", True, rgbcolors.maroon
            )
        self._screen.blit(
            self._score_text,
            (
                400 - self._score_text.get_width() // 2,
                275 - self._score_text.get_height() // 2,
            ),
        )

        # Initials "__ __ __"
        self._initials = self._initials_text_font.render(
            self._initials_text, True, rgbcolors.black
            )
        self._screen.blit(
            self._initials,
            (
                600 - self._initials.get_width() // 2,
                440 - self._initials.get_height() // 2,
            ),
        )

        # Press Enter to Submit
        self._screen.blit(
            self._press_enter_to_submit_score,
            (
                600 - self._press_enter_to_submit_score.get_width() // 2,
                540 - self._press_enter_to_submit_score.get_height() //2,
            ),
        )

        # skip
        self._screen.blit(
            self._skip,
            (
                600 - self._skip.get_width() // 2,
                570 - self._skip.get_height() // 2,
            )
        )

        # Leaderboard:
        self._screen.blit(
            self._leaderboard_text,
            (
                200 - self._leaderboard_text.get_width() // 2,
                350 - self._leaderboard_text.get_height() // 2,
            )
        )

        if len(self._leaderboard) > 0:
            self._leaderboard_1_font = pygame.font.Font(
                pygame.font.get_default_font(), 24
                )
            self._leaderboard_1 = self._leaderboard_1_font.render(
                f"{self._leaderboard[0].initials} ----- {self._leaderboard[0].score}", True, rgbcolors.black
            )

        if len(self._leaderboard) > 1:
            self._leaderboard_2_font = pygame.font.Font(
                pygame.font.get_default_font(), 24
                )
            self._leaderboard_2 = self._leaderboard_2_font.render(
                f"{self._leaderboard[1].initials} ----- {self._leaderboard[1].score}", True, rgbcolors.black
            )

        if len(self._leaderboard) > 2:
            self._leaderboard_3_font = pygame.font.Font(
                pygame.font.get_default_font(), 24
                )
            self._leaderboard_3 = self._leaderboard_3_font.render(
                f"{self._leaderboard[2].initials} ----- {self._leaderboard[2].score}", True, rgbcolors.black
            )

        if len(self._leaderboard) > 3:
            self._leaderboard_4_font = pygame.font.Font(
                pygame.font.get_default_font(), 24
                )
            self._leaderboard_4 = self._leaderboard_4_font.render(
                f"{self._leaderboard[3].initials} ----- {self._leaderboard[3].score}", True, rgbcolors.black
            )

        if len(self._leaderboard) > 4:
            self._leaderboard_5_font = pygame.font.Font(
                pygame.font.get_default_font(), 24
                )
            self._leaderboard_5 = self._leaderboard_5_font.render(
                f"{self._leaderboard[4].initials} ----- {self._leaderboard[4].score}", True, rgbcolors.black
            )

        if len(self._leaderboard) > 5:
            self._leaderboard_6_font = pygame.font.Font(
                pygame.font.get_default_font(), 24
                )
            self._leaderboard_6 = self._leaderboard_6_font.render(
                f"{self._leaderboard[5].initials} ----- {self._leaderboard[5].score}", True, rgbcolors.black
            )

        if len(self._leaderboard) > 6:
            self._leaderboard_7_font = pygame.font.Font(
                pygame.font.get_default_font(), 24
                )
            self._leaderboard_7 = self._leaderboard_7_font.render(
                f"{self._leaderboard[6].initials} ----- {self._leaderboard[6].score}", True, rgbcolors.black
            )

        if len(self._leaderboard) > 7:
            self._leaderboard_8_font = pygame.font.Font(
                pygame.font.get_default_font(), 24
                )
            self._leaderboard_8 = self._leaderboard_8_font.render(
                f"{self._leaderboard[7].initials} ----- {self._leaderboard[7].score}", True, rgbcolors.black
            )

        if len(self._leaderboard) > 8:
            self._leaderboard_9_font = pygame.font.Font(
                pygame.font.get_default_font(), 24
                )
            self._leaderboard_9 = self._leaderboard_9_font.render(
                f"{self._leaderboard[8].initials} ----- {self._leaderboard[8].score}", True, rgbcolors.black
            )

        if len(self._leaderboard) > 9:
            self._leaderboard_10_font = pygame.font.Font(
                pygame.font.get_default_font(), 24
                )
            self._leaderboard_10 = self._leaderboard_10_font.render(
                f"{self._leaderboard[9].initials} ----- {self._leaderboard[9].score}", True, rgbcolors.black
            )

        if len(self._leaderboard) > 0:
            # Leaderboard 1
            self._screen.blit(
                self._leaderboard_1,
                (
                    200 - self._leaderboard_1.get_width() // 2,
                    390 - self._leaderboard_1.get_height() // 2,
                )
            )

        if len(self._leaderboard) > 1:
            # Leaderboard 2
            self._screen.blit(
                self._leaderboard_2,
                (
                    200 - self._leaderboard_2.get_width() // 2,
                    420 - self._leaderboard_2.get_height() // 2,
                )
            )

        if len(self._leaderboard) > 2:
            # Leaderboard 3
            self._screen.blit(
                self._leaderboard_3,
                (
                    200 - self._leaderboard_3.get_width() // 2,
                    450 - self._leaderboard_3.get_height() // 2,
                )
            )

        if len(self._leaderboard) > 3:
            # Leaderboard 4
            self._screen.blit(
                self._leaderboard_4,
                (
                    200 - self._leaderboard_4.get_width() // 2,
                    480 - self._leaderboard_4.get_height() // 2,
                )
            )

        if len(self._leaderboard) > 4:
            # Leaderboard 5
            self._screen.blit(
                self._leaderboard_5,
                (
                    200 - self._leaderboard_5.get_width() // 2,
                    510 - self._leaderboard_5.get_height() // 2,
                )
            )

        if len(self._leaderboard) > 5:
            # Leaderboard 6
            self._screen.blit(
                self._leaderboard_6,
                (
                    200 - self._leaderboard_6.get_width() // 2,
                    540 - self._leaderboard_6.get_height() // 2,
                )
            )

        if len(self._leaderboard) > 6:
            # Leaderboard 7
            self._screen.blit(
                self._leaderboard_7,
                (
                    200 - self._leaderboard_7.get_width() // 2,
                    570 - self._leaderboard_7.get_height() // 2,
                )
            )

        if len(self._leaderboard) > 7:
            # Leaderboard 8
            self._screen.blit(
                self._leaderboard_8,
                (
                    200 - self._leaderboard_8.get_width() // 2,
                    600 - self._leaderboard_8.get_height() // 2,
                )
            )

        if len(self._leaderboard) > 8:
            # Leaderboard 9
            self._screen.blit(
                self._leaderboard_9,
                (
                    200 - self._leaderboard_9.get_width() // 2,
                    630 - self._leaderboard_9.get_height() // 2,
                )
            )

        if len(self._leaderboard) > 9:
            # Leaderboard 10
            self._screen.blit(
                self._leaderboard_10,
                (
                    200 - self._leaderboard_10.get_width() // 2,
                    660 - self._leaderboard_10.get_height() // 2,
                )
            )

    def end_scene(self):
        """End the scene"""
        super().end_scene()
        self._is_valid = True

    def process_event(self, event):
        """Process Keyboard events."""

        with open(pickle_file, "wb") as opened:
            pickle.dump(self._leaderboard, opened, pickle.HIGHEST_PROTOCOL)
        
        if event.type == pygame.KEYDOWN and event.key == pygame.K_SLASH:
            self._scene_manager.set_next_scene(self._next_key)
            self._is_valid = False
        elif event.type == pygame.KEYDOWN and event.key == pygame.K_RETURN and len(self._initials_text) == 1:
            self._initials_text += "__"
            new_score = Score(self._score, self._initials_text)
            self._leaderboard.append(new_score)
            with open(pickle_file, "wb") as opened:
                pickle.dump(self._leaderboard, opened, pickle.HIGHEST_PROTOCOL)
            self._scene_manager.set_next_scene(self._next_key)
            self._is_valid = False
        elif event.type == pygame.KEYDOWN and event.key == pygame.K_RETURN and len(self._initials_text) == 2:
            self._initials_text += "_"
            new_score = Score(self._score, self._initials_text)
            self._leaderboard.append(new_score)
            with open(pickle_file, "wb") as opened:
                pickle.dump(self._leaderboard, opened, pickle.HIGHEST_PROTOCOL)
            self._scene_manager.set_next_scene(self._next_key)
            self._is_valid = False
        elif event.type == pygame.KEYDOWN and event.key == pygame.K_RETURN and len(self._initials_text) == 3:
            new_score = Score(self._score, self._initials_text)
            self._leaderboard.append(new_score)
            with open(pickle_file, "wb") as opened:
                pickle.dump(self._leaderboard, opened, pickle.HIGHEST_PROTOCOL)
            self._scene_manager.set_next_scene(self._next_key)
            self._is_valid = False
        elif event.type == pygame.KEYDOWN and event.key == pygame.K_BACKSPACE and len(self._initials_text) <= 3 and len(self._initials_text) >= 1:
            self._initials_text = self._initials_text.rstrip(self._initials_text[-1])
        elif event.type == pygame.KEYDOWN and event.key == pygame.K_a and len(self._initials_text) <=2 and len(self._initials_text) >= 0:
            self._initials_text += "A"
        elif event.type == pygame.KEYDOWN and event.key == pygame.K_b and len(self._initials_text) <=2 and len(self._initials_text) >= 0:
            self._initials_text += "B"
        elif event.type == pygame.KEYDOWN and event.key == pygame.K_c and len(self._initials_text) <=2 and len(self._initials_text) >= 0:
            self._initials_text += "C"
        elif event.type == pygame.KEYDOWN and event.key == pygame.K_d and len(self._initials_text) <=2 and len(self._initials_text) >= 0:
            self._initials_text += "D"
        elif event.type == pygame.KEYDOWN and event.key == pygame.K_e and len(self._initials_text) <=2 and len(self._initials_text) >= 0:
            self._initials_text += "E"
        elif event.type == pygame.KEYDOWN and event.key == pygame.K_f and len(self._initials_text) <=2 and len(self._initials_text) >= 0:
            self._initials_text += "F"
        elif event.type == pygame.KEYDOWN and event.key == pygame.K_g and len(self._initials_text) <=2 and len(self._initials_text) >= 0:
            self._initials_text += "G"
        elif event.type == pygame.KEYDOWN and event.key == pygame.K_h and len(self._initials_text) <=2 and len(self._initials_text) >= 0:
            self._initials_text += "H"
        elif event.type == pygame.KEYDOWN and event.key == pygame.K_i and len(self._initials_text) <=2 and len(self._initials_text) >= 0:
            self._initials_text += "I"
        elif event.type == pygame.KEYDOWN and event.key == pygame.K_j and len(self._initials_text) <=2 and len(self._initials_text) >= 0:
            self._initials_text += "J"
        elif event.type == pygame.KEYDOWN and event.key == pygame.K_k and len(self._initials_text) <=2 and len(self._initials_text) >= 0:
            self._initials_text += "K"
        elif event.type == pygame.KEYDOWN and event.key == pygame.K_l and len(self._initials_text) <=2 and len(self._initials_text) >= 0:
            self._initials_text += "L"
        elif event.type == pygame.KEYDOWN and event.key == pygame.K_m and len(self._initials_text) <=2 and len(self._initials_text) >= 0:
            self._initials_text += "M"
        elif event.type == pygame.KEYDOWN and event.key == pygame.K_n and len(self._initials_text) <=2 and len(self._initials_text) >= 0:
            self._initials_text += "N"
        elif event.type == pygame.KEYDOWN and event.key == pygame.K_o and len(self._initials_text) <=2 and len(self._initials_text) >= 0:
            self._initials_text += "O"
        elif event.type == pygame.KEYDOWN and event.key == pygame.K_p and len(self._initials_text) <=2 and len(self._initials_text) >= 0:
            self._initials_text += "P"
        elif event.type == pygame.KEYDOWN and event.key == pygame.K_q and len(self._initials_text) <=2 and len(self._initials_text) >= 0:
            self._initials_text += "Q"
        elif event.type == pygame.KEYDOWN and event.key == pygame.K_r and len(self._initials_text) <=2 and len(self._initials_text) >= 0:
            self._initials_text += "R"
        elif event.type == pygame.KEYDOWN and event.key == pygame.K_s and len(self._initials_text) <=2 and len(self._initials_text) >= 0:
            self._initials_text += "S"
        elif event.type == pygame.KEYDOWN and event.key == pygame.K_t and len(self._initials_text) <=2 and len(self._initials_text) >= 0:
            self._initials_text += "T"
        elif event.type == pygame.KEYDOWN and event.key == pygame.K_u and len(self._initials_text) <=2 and len(self._initials_text) >= 0:
            self._initials_text += "U"
        elif event.type == pygame.KEYDOWN and event.key == pygame.K_v and len(self._initials_text) <=2 and len(self._initials_text) >= 0:
            self._initials_text += "V"
        elif event.type == pygame.KEYDOWN and event.key == pygame.K_w and len(self._initials_text) <=2 and len(self._initials_text) >= 0:
            self._initials_text += "W"
        elif event.type == pygame.KEYDOWN and event.key == pygame.K_x and len(self._initials_text) <=2 and len(self._initials_text) >= 0:
            self._initials_text += "X"
        elif event.type == pygame.KEYDOWN and event.key == pygame.K_y and len(self._initials_text) <=2 and len(self._initials_text) >= 0:
            self._initials_text += "Y"
        elif event.type == pygame.KEYDOWN and event.key == pygame.K_z and len(self._initials_text) <=2 and len(self._initials_text) >= 0:
            self._initials_text += "Z"
        else:
            super().process_event(event)

    def render_updates(self):
        """Render updates"""
        if self._render_updates:
            super().render_updates()
            # if self._render_updates:
            self._render_updates.clear(self._screen, self._background)
            self._render_updates.update()
            dirty = self._render_updates.draw(self._screen)