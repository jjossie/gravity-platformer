from typing import Optional

import arcade
from player import Player, ControlSet

# --- --- Constants

# Window Options
LAYER_NAME_DEPTH = "depth"
SCREEN_WIDTH = 1280
SCREEN_HEIGHT = 768
SCREEN_TITLE = "Platformer"

# Scaling
TILE_SCALING = 0.5
COIN_SCALING = 0.5

# --- Physics forces. Higher number, faster accelerating.

# Gravity
GRAVITY = 2600

# Damping - Amount of speed lost per second
DEFAULT_DAMPING = 1.0
PLAYER_DAMPING = 0.4

# Friction between objects
PLAYER_FRICTION = 1.0
WALL_FRICTION = 0.7
DYNAMIC_ITEM_FRICTION = 0.6

# Keep player from going too fast
PLAYER_MAX_HORIZONTAL_SPEED = 650
PLAYER_MAX_VERTICAL_SPEED = 1600

# Mass (defaults to 1)
PLAYER_MASS = 2.0

# --- Visuals.

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

        # Arcade Objects
        self.scene = None
        self.player_one = None
        self.player_two = None
        self.player_list = []
        self.physics_engine: Optional[arcade.PymunkPhysicsEngine] = None
        self.camera = None
        self.gui_camera = None
        self.tile_map = None

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

        # Create Players
        self.player_one = Player(self, ControlSet())
        self.player_one.center_x = 192
        self.player_one.center_y = 768
        self.scene.add_sprite(LAYER_NAME_PLAYER, self.player_one)
        # player_two_control_set = ControlSet(
        #     jump=arcade.key.W,
        #     toggle_gravity=arcade.key.CAPSLOCK,
        #     left=arcade.key.A,
        #     right=arcade.key.D
        # )
        # self.player_two = Player(self, player_two_control_set)
        # self.player_two.center_x = 296
        # self.player_two.center_y = 512
        # self.scene.add_sprite(LAYER_NAME_PLAYER, self.player_two)
        self.player_list.append(self.player_one)

        # Initialize Physics Engine
        self.physics_engine = arcade.PymunkPhysicsEngine(
            damping=DEFAULT_DAMPING,
            gravity=(0, -GRAVITY)
        )
        # Add Player to physics
        self.physics_engine.add_sprite(
            self.player_one,
            friction=PLAYER_FRICTION,
            mass=PLAYER_MASS,
            moment_of_intertia=arcade.PymunkPhysicsEngine.MOMENT_INF,
            collision_type="player",
            max_vertical_velocity=PLAYER_MAX_VERTICAL_SPEED,
            max_horizontal_velocity=PLAYER_MAX_HORIZONTAL_SPEED
        )
        # Add Other Layers to physics engine
        self.physics_engine.add_sprite_list(
            self.scene.get_sprite_list(LAYER_NAME_PLATFORMS),
            friction=WALL_FRICTION,
            collision_type="wall",
            body_type=arcade.PymunkPhysicsEngine.STATIC
        )
        self.physics_engine.add_sprite_list(
            self.scene.get_sprite_list(LAYER_NAME_BOXES),
            friction=WALL_FRICTION,
            collision_type="wall",
            body_type=arcade.PymunkPhysicsEngine.STATIC
        )

        # Game Logic
        self.score = 0
        self.max_score = COIN_VALUE * len(self.scene.get_sprite_list(LAYER_NAME_ITEMS))

    def on_key_press(self, key: int, modifiers: int):
        """Called whenever a key is pressed."""
        self.player_one.on_key_press(key)

    def on_key_release(self, key: int, modifiers: int):
        """Called whenever a key is released."""
        self.player_one.on_key_release(key)

    def camera_follow(self, players):
        self.camera.move_to(self.get_camera_position(), 0.1)

    def get_camera_position(self, parallax=1):
        screen_center_x = self.player_one.center_x - (self.camera.viewport_width / 2)
        screen_center_y = self.player_one.center_y - (self.camera.viewport_height / 2)

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
        self.player_one.update_movement(self.physics_engine)
        self.physics_engine.step()

        # Center the camera on the player.
        self.camera_follow([self.player_one])

        # Check for coin collisions
        coin_hit_list = arcade.check_for_collision_with_list(
            self.player_one, self.scene[LAYER_NAME_ITEMS]
        )
        for coin in coin_hit_list:
            # Remove the coin
            coin.remove_from_sprite_lists()
            self.score += COIN_VALUE
            if self.has_won():
                self.win()

        # Check for death
        death_hit_list = arcade.check_for_collision_with_list(
            self.player_one, self.scene[LAYER_NAME_DEATH]
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
