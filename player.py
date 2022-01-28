import arcade

CHARACTER_SCALING = 0.5
PLAYER_SPRITE_PATH = "sprites/PNG/Players/128x256/Green/alienGreen_stand.png"

# PHYSICS
PLAYER_MOVEMENT_SPEED = 10
PLAYER_ACCELERATION = 0.9
PLAYER_JUMP_SPEED = 20

TEXTURE_RIGHT_INDEX = 0
TEXTURE_LEFT_INDEX = 1


class Player(arcade.Sprite):

    def __init__(self):
        super().__init__()

        self.scale = CHARACTER_SCALING
        self.textures = []

        self.textures.append(arcade.load_texture(PLAYER_SPRITE_PATH))
        self.textures.append(arcade.load_texture(PLAYER_SPRITE_PATH, flipped_horizontally=True))
        self.texture = self.textures[0]

        # Key Tracking
        self.left_pressed = False
        self.right_pressed = False
        self.up_pressed = False
        self.down_pressed = False
        self.space_pressed = False

    def on_key_press(self, key: int):
        if key in [arcade.key.UP, arcade.key.W]:
            self.up_pressed = True
        if key in [arcade.key.DOWN, arcade.key.S]:
            self.down_pressed = True
        if key in [arcade.key.LEFT, arcade.key.A]:
            self.left_pressed = True
        if key in [arcade.key.RIGHT, arcade.key.D]:
            self.right_pressed = True
        if key == arcade.key.SPACE:
            self.space_pressed = True

    def on_key_release(self, key: int):
        if key in [arcade.key.LEFT, arcade.key.A]:
            self.left_pressed = False
        if key in [arcade.key.RIGHT, arcade.key.D]:
            self.right_pressed = False
        if key in [arcade.key.UP, arcade.key.W]:
            self.up_pressed = False
        if key in [arcade.key.DOWN, arcade.key.S]:
            self.down_pressed = False
        if key == arcade.key.SPACE:
            self.space_pressed = False

    def update_speed(self, physics_engine):
        """Calculate new movement speed every frame."""

        if self.right_pressed and not self.left_pressed:
            self.apply_acceleration(True)
            # Apply right animation
            self.texture = self.textures[TEXTURE_RIGHT_INDEX]
        elif self.left_pressed and not self.right_pressed:
            self.apply_acceleration(False)
            # Apply left animation
            self.texture = self.textures[TEXTURE_LEFT_INDEX]

        else:
            self.coast()

        if physics_engine.can_jump() and (self.up_pressed or self.space_pressed):
            self.change_y = PLAYER_JUMP_SPEED

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
