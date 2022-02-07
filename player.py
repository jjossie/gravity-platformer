import arcade
from dataclasses import dataclass

# Physics
PLAYER_MOVEMENT_SPEED = 12
PLAYER_ACCELERATION = 1
PLAYER_JUMP_SPEED = 25

# Textures
PLAYER_SPRITE_PATH = "sprites/PNG/Players/128x256/Green/alienGreen_stand_crop.png"
CHARACTER_SCALING = 0.546875
TEXTURE_RIGHT_INDEX = 0
TEXTURE_LEFT_INDEX = 1
TEXTURE_RIGHT_INVERTED_INDEX = 2
TEXTURE_LEFT_INVERTED_INDEX = 3


@dataclass
class ControlSet:
    """
    A Data Class representing logical game controls mapped to arcade-enumerated keys.
    """
    jump: int = arcade.key.UP
    left: int = arcade.key.LEFT
    right: int = arcade.key.RIGHT
    toggle_gravity: int = arcade.key.SPACE


class Player(arcade.Sprite):

    def __init__(self, window: arcade.Window, control_set: ControlSet):
        """
        Initializer for the custom player sprite.
        :param window: a reference to the window in which this player exists.
        :param control_set: a DataClass object representing a mapping of keys to game controls.
        """

        super().__init__()

        self.window = window

        # Load textures for each possible orientation of the player sprite
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
        """
        Called on every key press event and used to set which keys are pressed.
        :param key: Arcade enumerated int corresponding to a ControlSet value
        representing a key.
        :return: None
        """
        if key == self.control_set.jump:
            self.jump_pressed = True
        if key == self.control_set.left:
            self.left_pressed = True
        if key == self.control_set.right:
            self.right_pressed = True
        # Gravity inversion control happens here rather than update_speed() because this
        # only gets called once when a key is pressed, rather than once every frame for the
        # duration of the keypress.
        if key == self.control_set.toggle_gravity:
            arcade.play_sound(self.window.gravity_sound, volume=self.window.SFX_VOLUME)
            self.invert_pressed = True
            self.gravity_inverted = not self.gravity_inverted
            self.window.initialize_physics(self.gravity_inverted)

    def on_key_release(self, key: int):
        """
        Called on every key release event and used to set which keys are no longer pressed.
        :param key: Arcade enumerated int representing a key.
        :return: None
        """
        if key == self.control_set.left:
            self.left_pressed = False
        if key == self.control_set.right:
            self.right_pressed = False
        if key == self.control_set.jump:
            self.jump_pressed = False
        if key == self.control_set.toggle_gravity:
            self.invert_pressed = False

    def update_speed(self, physics_engine):
        """
        Calculate new movement speed including jumping every frame based on which keys are
        currently being pressed.
        """

        # Apply acceleration based on left/right keys being pressed
        if self.right_pressed and not self.left_pressed:
            self.apply_acceleration(True)
            self.facing_right = True
        elif self.left_pressed and not self.right_pressed:
            self.apply_acceleration(False)
            self.facing_right = False
        else:
            self.coast()

        # Determine if we can jump up (not inverted) or down (inverted)
        if self.can_jump(physics_engine) and self.jump_pressed:
            arcade.play_sound(self.window.jump_sound, volume=self.window.SFX_VOLUME)
            inv_int = -1 if self.gravity_inverted else 1
            self.change_y = PLAYER_JUMP_SPEED * inv_int

        # Update the texture according to new player sprite orientation
        self.update_texture()

    def can_jump(self, physics_engine):
        """
        Custom function to determine if the player can jump, whether gravity is inverted or not.
        If gravity is inverted, this function checks for a collision above the player sprite
        to determine jump eligibility. Otherwise, it calls the built-in arcade physics engine's
        can_jump() (Which does basically the same thing just for collisions below only).
        :param physics_engine: Reference to the SimplePlatformerPhysicsEngine being used.
        :return: None
        """
        if self.gravity_inverted:
            # Move up to see if we are on a platform
            y_distance = 5
            self.center_y += y_distance

            # Check for wall hit
            hit_list = arcade.check_for_collision_with_lists(
                physics_engine.player_sprite, physics_engine.walls + physics_engine.platforms)
            # Move it back
            self.center_y -= y_distance
            if len(hit_list) > 0:
                physics_engine.jumps_since_ground = 0
                return True
            else:
                return False
        else:
            return physics_engine.can_jump()

    def apply_acceleration(self, is_right):
        """
        Gradually increase the velocity of the player along the x-axis, not
        exceeding the maximum PLAYER_MOVEMENT_SPEED constant.
        """
        if -PLAYER_MOVEMENT_SPEED < self.change_x < PLAYER_MOVEMENT_SPEED:
            if is_right:
                self.change_x += PLAYER_ACCELERATION
            else:
                self.change_x -= PLAYER_ACCELERATION

    def coast(self):
        """
        Gradually decrease velocity until we come to a standstill.
        """
        if -PLAYER_ACCELERATION < self.change_x < PLAYER_ACCELERATION:
            self.change_x = 0
        elif self.change_x > 0:
            self.change_x -= PLAYER_ACCELERATION
        elif self.change_x < 0:
            self.change_x += PLAYER_ACCELERATION

    def update_texture(self):
        """
        Apply the appropriate texture to the player sprite based on orientation.
        :return: None
        """
        if not self.facing_right:
            self.texture = self.textures[
                TEXTURE_LEFT_INVERTED_INDEX if self.gravity_inverted else TEXTURE_LEFT_INDEX
            ]
        else:
            self.texture = self.textures[
                TEXTURE_RIGHT_INVERTED_INDEX if self.gravity_inverted else TEXTURE_RIGHT_INDEX
            ]
