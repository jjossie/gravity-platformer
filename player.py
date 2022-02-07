import arcade
from dataclasses import dataclass

CHARACTER_SCALING = 0.546875
PLAYER_SPRITE_PATH = "sprites/PNG/Players/128x256/Green/alienGreen_stand_crop.png"

# PHYSICS
PLAYER_MOVEMENT_SPEED = 12
PLAYER_ACCELERATION = 1
PLAYER_JUMP_SPEED = 25

TEXTURE_RIGHT_INDEX = 0
TEXTURE_LEFT_INDEX = 1
TEXTURE_RIGHT_INVERTED_INDEX = 2
TEXTURE_LEFT_INVERTED_INDEX = 3


@dataclass
class ControlSet:
    jump: int = arcade.key.UP
    left: int = arcade.key.LEFT
    right: int = arcade.key.RIGHT
    toggle_gravity: int = arcade.key.SPACE


class Player(arcade.Sprite):

    def __init__(self, window: arcade.Window, control_set: ControlSet):
        super().__init__()

        self.window = window

        self.scale = CHARACTER_SCALING
        self.textures = []

        self.textures.append(arcade.load_texture(PLAYER_SPRITE_PATH))
        self.textures.append(arcade.load_texture(PLAYER_SPRITE_PATH, flipped_horizontally=True))
        self.textures.append(arcade.load_texture(PLAYER_SPRITE_PATH, flipped_vertically=True))
        self.textures.append(arcade.load_texture(PLAYER_SPRITE_PATH,
                                                 flipped_horizontally=True, flipped_vertically=True))
        self.texture = self.textures[0]

        # Key Tracking
        self.left_pressed = False
        self.right_pressed = False
        self.jump_pressed = False
        self.down_pressed = False
        self.invert_pressed = False
        self.control_set = control_set

        # Game Logic
        self.gravity_inverted = False
        self.facing_right = True

    def on_key_press(self, key: int):
        if key == self.control_set.jump:
            self.jump_pressed = True
        if key == self.control_set.left:
            self.left_pressed = True
        if key == self.control_set.right:
            self.right_pressed = True
        if key == self.control_set.toggle_gravity:
            arcade.play_sound(self.window.gravity_sound, volume=self.window.SFX_VOLUME)
            self.invert_pressed = True
            self.gravity_inverted = not self.gravity_inverted
            self.window.initialize_physics(self.gravity_inverted)

    def on_key_release(self, key: int):
        if key == self.control_set.left:
            self.left_pressed = False
        if key == self.control_set.right:
            self.right_pressed = False
        if key == self.control_set.jump:
            self.jump_pressed = False
        if key == self.control_set.toggle_gravity:
            self.invert_pressed = False

    def update_speed(self, physics_engine):
        """Calculate new movement speed every frame. And set animations (extraneous cohesion, I know)."""

        if self.right_pressed and not self.left_pressed:
            self.apply_acceleration(True)
            self.facing_right = True
            # Apply right animation
            # self.texture = self.textures[
            #     TEXTURE_RIGHT_INVERTED_INDEX if self.gravity_inverted else TEXTURE_RIGHT_INDEX
            # ]
        elif self.left_pressed and not self.right_pressed:
            self.apply_acceleration(False)
            self.facing_right = False
            # Apply left animation
            # self.texture = self.textures[
            #     TEXTURE_LEFT_INVERTED_INDEX if self.gravity_inverted else TEXTURE_LEFT_INDEX
            # ]

        else:
            self.coast()

        if physics_engine.can_jump() and self.jump_pressed:
            arcade.play_sound(self.window.jump_sound, volume=self.window.SFX_VOLUME)
            inv_int = -1 if self.gravity_inverted else 1
            self.change_y = PLAYER_JUMP_SPEED * inv_int

        self.update_texture()

    def apply_acceleration(self, is_right):
        """Gradually increase the velocity of the player along the x-axis."""
        if -PLAYER_MOVEMENT_SPEED < self.change_x < PLAYER_MOVEMENT_SPEED:
            if is_right:
                self.change_x += PLAYER_ACCELERATION
            else:
                self.change_x -= PLAYER_ACCELERATION

    def coast(self):
        """Gradually decrease velocity until we come to a standstill."""
        if -PLAYER_ACCELERATION < self.change_x < PLAYER_ACCELERATION:
            self.change_x = 0
        elif self.change_x > 0:
            self.change_x -= PLAYER_ACCELERATION
        elif self.change_x < 0:
            self.change_x += PLAYER_ACCELERATION

    def update_texture(self):
        if not self.facing_right:
            self.texture = self.textures[
                TEXTURE_LEFT_INVERTED_INDEX if self.gravity_inverted else TEXTURE_LEFT_INDEX
            ]
        else:
            self.texture = self.textures[
                TEXTURE_RIGHT_INVERTED_INDEX if self.gravity_inverted else TEXTURE_RIGHT_INDEX
            ]