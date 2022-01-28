import arcade

# Constants

# Window Options
LAYER_NAME_DEPTH = "depth"
SCREEN_WIDTH = 1280
SCREEN_HEIGHT = 768
SCREEN_TITLE = "Platformer"

# Scaling
CHARACTER_SCALING = 0.5
TILE_SCALING = 0.5
COIN_SCALING = 0.5

# Physics
PLAYER_MOVEMENT_SPEED = 10
PLAYER_ACCELERATION = 0.9
GRAVITY = 1
PLAYER_JUMP_SPEED = 20

# Layer Names
LAYER_NAME_PLAYER = "player"
LAYER_NAME_ITEMS = "items"
LAYER_NAME_BOXES = "boxes"
LAYER_NAME_PLATFORMS = "platforms"
LAYER_NAME_DEATH = "death"
LAYER_NAME_BACKGROUND = "background"

# Game Logic
COIN_VALUE = 5


class MyGame(arcade.Window):
    """
    Main application class.
    """

    def __init__(self) -> None:
        # Create this Arcade Window but do not display it yet
        super().__init__(SCREEN_WIDTH, SCREEN_HEIGHT, SCREEN_TITLE)
        # arcade.set_background_color(arcade.csscolor.CORNFLOWER_BLUE)

        # Arcade Objects
        self.scene = None
        self.player_sprite = None
        self.physics_engine = None
        self.camera = None
        self.gui_camera = None
        self.tile_map = None

        # Key Tracking
        self.left_pressed = False
        self.right_pressed = False
        self.up_pressed = False
        self.down_pressed = False
        self.space_pressed = False

        # Game Logic
        self.score = 0
        self.max_score = 0

    def setup(self):
        """Set up the game here. Call this function to restart the game."""

        # Set up Arcade Objects
        self.scene = arcade.Scene()
        self.camera = arcade.Camera(self.width, self.height)
        self.gui_camera = arcade.Camera(self.width, self.height)

        # Setup Tile Maps
        map_path = "maps/demo.tmx"
        layer_options = {
            LAYER_NAME_PLATFORMS: {
                "use_spatial_hash": True
            },
            LAYER_NAME_ITEMS: {
                "use_spatial_hash": True
            },
            LAYER_NAME_DEPTH: {
                "use_spatial_hash": True
            },
            LAYER_NAME_BOXES: {
                "use_spatial_hash": True
            }
        }

        # Load the tilemap
        self.tile_map = arcade.load_tilemap(map_path, TILE_SCALING, layer_options)

        # Initialize Scene with tilemap
        self.scene = arcade.Scene.from_tilemap(self.tile_map)

        # Create Sprites
        player_sprite_path = "sprites/PNG/Players/128x256/Green/alienGreen_stand.png"
        self.player_sprite = arcade.Sprite(player_sprite_path, CHARACTER_SCALING)
        self.player_sprite.center_x = 128
        self.player_sprite.center_y = 256
        self.scene.add_sprite(LAYER_NAME_PLAYER, self.player_sprite)

        # Initialize Physics Engine
        self.physics_engine = arcade.PhysicsEnginePlatformer(
            self.player_sprite, gravity_constant=GRAVITY, walls=[
                self.scene[LAYER_NAME_PLATFORMS],
                self.scene[LAYER_NAME_BOXES]
            ]
        )

        # Game Logic
        self.score = 0
        self.max_score = COIN_VALUE * len(self.scene.get_sprite_list(LAYER_NAME_ITEMS))

    def on_key_press(self, key: int, modifiers: int):
        """Called whenever a key is pressed."""

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

    def on_key_release(self, key: int, modifiers: int):
        """Called whenever a key is released."""

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

    def update_player_speed(self):
        """Calculate new movement speed every frame."""

        if self.right_pressed and not self.left_pressed:
            self.apply_acceleration(True)
            # Apply right animation

        elif self.left_pressed and not self.right_pressed:
            self.apply_acceleration(False)
            # Apply left animation

        else:
            self.coast()

        if self.physics_engine.can_jump() and (self.up_pressed or self.space_pressed):
            self.player_sprite.change_y = PLAYER_JUMP_SPEED

    def apply_acceleration(self, is_right):
        """Gradually increase the velocity of the player along the x-axis."""
        if -PLAYER_MOVEMENT_SPEED < self.player_sprite.change_x < PLAYER_MOVEMENT_SPEED:
            if is_right:
                self.player_sprite.change_x += PLAYER_ACCELERATION
            else:
                self.player_sprite.change_x -= PLAYER_ACCELERATION

    def coast(self):
        """Gradually decrease velocity until we come to a standstill."""
        if -PLAYER_ACCELERATION < self.player_sprite.change_x < PLAYER_ACCELERATION:
            self.player_sprite.change_x = 0
        elif self.player_sprite.change_x > 0:
            self.player_sprite.change_x -= PLAYER_ACCELERATION
        elif self.player_sprite.change_x < 0:
            self.player_sprite.change_x += PLAYER_ACCELERATION

    def camera_follow(self, parallax=1):
        self.camera.move_to(self.get_camera_position(1))

    def get_camera_position(self, parallax=1):
        screen_center_x = self.player_sprite.center_x - (self.camera.viewport_width / 2)
        screen_center_y = self.player_sprite.center_y - (self.camera.viewport_height / 2)

        # Don't let camera travel past 0
        if screen_center_x < 0:
            screen_center_x = 0
        if screen_center_y < 0:
            screen_center_y = 0

        return screen_center_x * parallax, screen_center_y * parallax

    def on_draw(self):
        """Render the screen."""

        # Clear the screen to the background color
        arcade.start_render()

        # Activate the game cameras
        self.camera.use()

        # Draw the Scene
        self.scene.draw()

        # Activate GUI camera before drawing GUI
        self.gui_camera.use()

        # Draw GUI
        self.draw_gui()

    def draw_gui(self):
        """Display to the screen any text we need to."""
        score_text = f"Score: {self.score}"
        arcade.draw_text(
            score_text,
            10,
            10,
            arcade.csscolor.WHITE,
            18
        )

    def on_update(self, delta_time):
        """Movement and game logic."""

        # Move the player with the physics engine.
        self.update_player_speed()
        self.physics_engine.update()

        # Center the camera on the player.
        self.camera_follow()

        # Check for coin collisions
        coin_hit_list = arcade.check_for_collision_with_list(
            self.player_sprite, self.scene[LAYER_NAME_ITEMS]
        )
        for coin in coin_hit_list:
            # Remove the coin
            coin.remove_from_sprite_lists()
            self.score += COIN_VALUE
            if self.has_won():
                self.win()

        # Check for death
        death_hit_list = arcade.check_for_collision_with_list(
            self.player_sprite, self.scene[LAYER_NAME_DEATH]
        )
        if len(death_hit_list) > 0:
            self.die()

    def die(self):
        self.setup()

    def has_won(self) -> bool:
        return self.score >= self.max_score

    def win(self):
        print("you win")
        pass


def main():
    window = MyGame()
    window.setup()
    arcade.run()


if __name__ == "__main__":
    main()
