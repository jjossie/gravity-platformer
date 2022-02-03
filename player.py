import arcade
from dataclasses import dataclass

CHARACTER_SCALING = 0.5
PLAYER_SPRITE_PATH = "sprites/PNG/Players/128x256/Green/alienGreen_stand.png"

# Force applied while on the ground
PLAYER_MOVE_FORCE_ON_GROUND = 8000

# Force applied when moving left/right in the air
PLAYER_MOVE_FORCE_IN_AIR = 4000

# Strength of a jump
PLAYER_JUMP_IMPULSE = 2200

# --- Visuals.

# TEXTURES
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

        # Animation Control
        self.facing_right = True
        self.scale = CHARACTER_SCALING
        self.textures = []
        self.textures.append(arcade.load_texture(PLAYER_SPRITE_PATH))
        self.textures.append(arcade.load_texture(PLAYER_SPRITE_PATH, flipped_horizontally=True))
        self.textures.append(arcade.load_texture(PLAYER_SPRITE_PATH, flipped_vertically=True))
        self.textures.append(arcade.load_texture(PLAYER_SPRITE_PATH,
                                                 flipped_horizontally=True, flipped_vertically=True))
        self.texture = self.textures[0]

        self.hit_box_algorithm = 'Detailed'


        # Key Tracking
        self.left_pressed = False
        self.right_pressed = False
        self.jump_pressed = False
        self.down_pressed = False
        self.invert_pressed = False
        self.control_set = control_set

        # Game Logic
        self.gravity_inverted = False


    def on_key_press(self, key: int):
        if key == self.control_set.jump:
            self.jump_pressed = True
        if key == self.control_set.left:
            self.left_pressed = True
        if key == self.control_set.right:
            self.right_pressed = True
        if key == self.control_set.toggle_gravity:
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

    def update_movement(self, physics_engine):
        """ Update player forces based on keys pressed """
        is_on_ground = physics_engine.is_on_ground(self)

        if self.left_pressed and not self.right_pressed:
            # Create a force to the left. Apply it.
            force = (-PLAYER_MOVE_FORCE_ON_GROUND if is_on_ground else -PLAYER_MOVE_FORCE_IN_AIR, 0)
            physics_engine.apply_force(self, force)
            # Set friction to zero for the player while moving
            physics_engine.set_friction(self, 0)
            self.facing_right = False
        elif self.right_pressed and not self.left_pressed:
            # Create a force to the right. Apply it.
            force = (PLAYER_MOVE_FORCE_ON_GROUND if is_on_ground else PLAYER_MOVE_FORCE_IN_AIR, 0)
            physics_engine.apply_force(self, force)
            # Set friction to zero for the player while moving
            physics_engine.set_friction(self, 0)
            self.facing_right = True
        else:
            # Player's feet are not moving. Therefore, up the friction so we stop.
            physics_engine.set_friction(self, 1.0)
        if self.jump_pressed and is_on_ground:
            impulse = (0, PLAYER_JUMP_IMPULSE)
            physics_engine.apply_impulse(self, impulse)

    def pymunk_moved(self, physics_engine, dx, dy, d_angle):
        if self.facing_right:
            self.texture = self.textures[
                TEXTURE_RIGHT_INVERTED_INDEX if self.gravity_inverted else TEXTURE_RIGHT_INDEX
            ]
        else:
            self.texture = self.textures[
                TEXTURE_LEFT_INVERTED_INDEX if self.gravity_inverted else TEXTURE_LEFT_INDEX
            ]

    # def update_speed(self, physics_engine):
    #     """Calculate new movement speed every frame. And set animations (extraneous cohesion, I know)."""
    #
    #     if self.right_pressed and not self.left_pressed:
    #         self.apply_acceleration(True)
    #         # Apply right animation
    #         self.texture = self.textures[
    #             TEXTURE_RIGHT_INVERTED_INDEX if self.gravity_inverted else TEXTURE_RIGHT_INDEX
    #         ]
    #     elif self.left_pressed and not self.right_pressed:
    #         self.apply_acceleration(False)
    #         # Apply left animation
    #         self.texture = self.textures[
    #             TEXTURE_LEFT_INVERTED_INDEX if self.gravity_inverted else TEXTURE_LEFT_INDEX
    #         ]
    #
    #     else:
    #         self.coast()
    #
    #     if physics_engine.can_jump() and self.jump_pressed:
    #         inv_int = -1 if self.gravity_inverted else 1
    #         self.change_y = PLAYER_JUMP_SPEED * inv_int

    # def apply_acceleration(self, is_right):
    #     """Gradually increase the velocity of the player along the x-axis."""
    #     if -PLAYER_MOVEMENT_SPEED < self.change_x < PLAYER_MOVEMENT_SPEED:
    #         if is_right:
    #             self.change_x += PLAYER_ACCELERATION
    #         else:
    #             self.change_x -= PLAYER_ACCELERATION
    #
    # def coast(self):
    #     """Gradually decrease velocity until we come to a standstill."""
    #     if -PLAYER_ACCELERATION < self.change_x < PLAYER_ACCELERATION:
    #         self.change_x = 0
    #     elif self.change_x > 0:
    #         self.change_x -= PLAYER_ACCELERATION
    #     elif self.change_x < 0:
    #         self.change_x += PLAYER_ACCELERATION
