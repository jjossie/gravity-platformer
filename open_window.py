import arcade

# Constants
SCREEN_WIDTH = 1000
SCREEN_HEIGHT = 650
SCREEN_TITLE = "Platformer"
# Scaling
CHARACTER_SCALING = 0.5
# TILE_SCALING = 0.9142857142857 # using old 70x70px sprites
# COIN_SCALING = 0.9142857142857 # using old 70x70px sprites
TILE_SCALING = 0.5
COIN_SCALING = 0.5
# Physics
PLAYER_MOVEMENT_SPEED = 10
PLAYER_ACCELERATION = 0.9
GRAVITY = 1
PLAYER_JUMP_SPEED = 20
# Game Logic
COIN_VALUE = 5


class MyGame(arcade.Window):
    """
    Main application class.
    """

    def __init__(self) -> None:
        # Create this Arcade Window but do not display it yet
        super().__init__(SCREEN_WIDTH, SCREEN_HEIGHT, SCREEN_TITLE)
        arcade.set_background_color(arcade.csscolor.CORNFLOWER_BLUE)

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

    def setup(self):
        """Set up the game here. Call this function to restart the game."""

        # Set up Arcade Objects
        self.scene = arcade.Scene()
        self.camera = arcade.Camera(self.width, self.height)
        self.gui_camera = arcade.Camera(self.width, self.height)

        # Setup Tile Maps
        map_path = "maps/demo.tmx"
        layer_options = {
            "platforms": {
                "use_spatial_hash": True
            }
        }

        # Load the tilemap
        self.tile_map = arcade.load_tilemap(map_path, TILE_SCALING, layer_options)

        # Initialize Scene with tilemap
        self.scene = arcade.Scene.from_tilemap(self.tile_map)

        # # Create Sprite Lists
        # self.scene.add_sprite_list("Player")
        # self.scene.add_sprite_list("Walls", use_spatial_hash=True)
        # self.scene.add_sprite_list("Coins")

        # Create Sprites
        player_sprite_path = "sprites/PNG/Players/128x256/Green/alienGreen_stand.png"
        self.player_sprite = arcade.Sprite(player_sprite_path, CHARACTER_SCALING)
        self.player_sprite.center_x = 128
        self.player_sprite.center_y = 256
        self.scene.add_sprite("player", self.player_sprite)
        #
        # # Generate Wall Tiles
        # for x in range(0, 2500, 64):
        #     wall = arcade.Sprite("Sprites/Tiles/Ground Tiles/Grass/grassMid.png", TILE_SCALING)
        #     wall.center_x = x
        #     wall.center_y = 32
        #     self.scene.add_sprite("Walls", wall)
        #
        # # Generate Boxes
        # coordinate_list = [[512, 96], [256, 96], [768, 96]]
        # for coordinate in coordinate_list:
        #     crate = arcade.Sprite("Sprites/Tiles/box.png", TILE_SCALING)
        #     crate.position = coordinate
        #     self.scene.add_sprite("Walls", crate)
        #
        # # Generate Coins
        # # Use a loop to place some coins for our character to pick up
        # for x in range(128, 2500, 192):
        #     coin = arcade.Sprite("Sprites/Items/Coins/coinGold.png", COIN_SCALING)
        #     coin.center_x = x
        #     coin.center_y = 96
        #     self.scene.add_sprite("Coins", coin)

        # Initialize Physics Engine
        self.physics_engine = arcade.PhysicsEnginePlatformer(
            self.player_sprite, gravity_constant=GRAVITY, walls=self.scene["platforms"]
        )

        # Game Logic
        self.score = 0

    def on_key_press(self, key: int, modifiers: int):
        """Called whenever a key is pressed."""

        if key in [arcade.key.UP, arcade.key.W]:
            self.up_pressed = True
        elif key in [arcade.key.DOWN, arcade.key.S]:
            self.down_pressed = True
        elif key in [arcade.key.LEFT, arcade.key.A]:
            self.left_pressed = True
        elif key in [arcade.key.RIGHT, arcade.key.D]:
            self.right_pressed = True
        elif key == arcade.key.SPACE:
            self.space_pressed = True

    def on_key_release(self, key: int, modifiers: int):
        """Called whenever a key is released."""

        if key in [arcade.key.LEFT, arcade.key.A]:
            self.left_pressed = False
        elif key in [arcade.key.RIGHT, arcade.key.D]:
            self.right_pressed = False
        elif key in [arcade.key.UP, arcade.key.W]:
            self.up_pressed = False
        elif key in [arcade.key.DOWN, arcade.key.S]:
            self.down_pressed = False
        elif key == arcade.key.SPACE:
            self.space_pressed = False

    def update_player_speed(self):
        """Calculate new movement speed every time a key is pressed/released"""

        if self.right_pressed and not self.left_pressed:
            self.apply_acceleration(True)
        elif self.left_pressed and not self.right_pressed:
            self.apply_acceleration(False)
        else:
            self.coast()

        if self.physics_engine.can_jump() and (self.up_pressed or self.space_pressed):
            self.player_sprite.change_y = PLAYER_JUMP_SPEED

    def apply_acceleration(self, is_right):
        """Gradually increase the velocity of a particular axis."""
        if -PLAYER_MOVEMENT_SPEED < self.player_sprite.change_x < PLAYER_MOVEMENT_SPEED:
            if is_right:
                self.player_sprite.change_x += PLAYER_ACCELERATION
            else:
                self.player_sprite.change_x -= PLAYER_ACCELERATION

    def coast(self):
        if -PLAYER_ACCELERATION < self.player_sprite.change_x < PLAYER_ACCELERATION:
            self.player_sprite.change_x = 0
        elif self.player_sprite.change_x > 0:
            self.player_sprite.change_x -= PLAYER_ACCELERATION
        elif self.player_sprite.change_x < 0:
            self.player_sprite.change_x += PLAYER_ACCELERATION

    def camera_follow(self):
        screen_center_x = self.player_sprite.center_x - (self.camera.viewport_width / 2)
        screen_center_y = self.player_sprite.center_y - (self.camera.viewport_height / 2)

        # Don't let camera travel past 0
        if screen_center_x < 0:
            screen_center_x = 0
        if screen_center_y < 0:
            screen_center_y = 0

        self.camera.move_to((screen_center_x, screen_center_y))

    def on_draw(self):
        """Render the screen."""

        # Clear the screen to the background color
        arcade.start_render()

        # Activate the game camera
        self.camera.use()

        # Draw the Scene
        self.scene.draw()

        # Activate GUI camera before drawing GUI
        self.gui_camera.use()

        # Draw GUI
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
            self.player_sprite, self.scene["items"]
        )

        for coin in coin_hit_list:
            # Remove the coin
            coin.remove_from_sprite_lists()
            self.score += COIN_VALUE


def main():
    window = MyGame()
    window.setup()
    arcade.run()


if __name__ == "__main__":
    main()
