import arcade
from player import Player, ControlSet

# These were used to control waiting before switching to the next level, but
# it was causing unpredictable behavior in update() and setup().
# import threading
# from time import sleep

# Constants

# Window Options
SCREEN_WIDTH = 1280
SCREEN_HEIGHT = 768
SCREEN_TITLE = "Platformer"
GLOBAL_SFX_VOLUME = 0.3
GLOBAL_MUSIC_VOLUME = 0.8

# Resources
MAIN_MUSIC_PATH = "sounds/loom_loop.mp3"
LEVELS = [
    "maps/level_1.tmx",
    "maps/level_2.tmx"
]

# Scaling
TILE_SCALING = 1
COIN_SCALING = 1
GRID_PIXEL_SIZE = 70

# Physics
GRAVITY = 1

# Layer Names
LAYER_NAME_PLAYER = "player"
LAYER_NAME_COINS = "coins"
LAYER_NAME_DECORATION = "decoration"
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
        """
        Initialize this game window.
        """
        # Create this Arcade Window but do not display it yet
        super().__init__(SCREEN_WIDTH, SCREEN_HEIGHT, SCREEN_TITLE)

        # Arcade Objects
        self.scene = None
        self.player_one = None
        self.player_two = None
        self.physics_engine = None
        self.camera = None
        self.gui_camera = None
        self.tile_map = None
        self.map_width = 0
        self.map_height = 0

        # Game Logic
        self.score = 0
        self.max_score = 0
        self.level = 0
        self.won_world = False

        # Load sounds
        self.music = arcade.load_sound(MAIN_MUSIC_PATH, True)
        self.coin_sound = arcade.load_sound(":resources:sounds/coin5.wav")
        self.jump_sound = arcade.load_sound(":resources:sounds/jump4.wav")
        self.gravity_sound = arcade.load_sound(":resources:sounds/upgrade4.wav")
        self.death_sound = arcade.load_sound(":resources:sounds/error4.wav")
        self.SFX_VOLUME = GLOBAL_SFX_VOLUME

        # Play Music
        arcade.play_sound(self.music, volume=GLOBAL_MUSIC_VOLUME, looping=True)

    def setup(self):
        """
        Set up the game here. Call this function to restart the game.
        """

        # Get Level Map
        try:
            map_path = LEVELS[self.level]
        except IndexError:
            # If next map is nowhere to be found, assume we are done with all levels.
            self.win_world()
            return

        # Set up Arcade Objects
        self.scene = arcade.Scene()
        self.camera = arcade.Camera(self.width, self.height)
        self.gui_camera = arcade.Camera(self.width, self.height)

        # Setup Tile Map Options
        # Only layers that frequently check for collisions use the spatial hash.
        layer_options = {
            LAYER_NAME_PLATFORMS: {
                "use_spatial_hash": True
            },
            LAYER_NAME_COINS: {
                "use_spatial_hash": True
            },
            LAYER_NAME_DEATH: {
                "use_spatial_hash": True
            }
        }

        # Load the tilemap
        self.tile_map = arcade.load_tilemap(map_path, TILE_SCALING, layer_options)
        self.map_width = self.tile_map.width * GRID_PIXEL_SIZE
        self.map_height = self.tile_map.height * GRID_PIXEL_SIZE

        # Initialize Scene with tilemap
        self.scene = arcade.Scene.from_tilemap(self.tile_map)

        # Create Sprites
        self.player_one = Player(self, ControlSet())
        self.player_one.center_x = 256
        self.player_one.center_y = 512
        self.scene.add_sprite(LAYER_NAME_PLAYER, self.player_one)

        # Initialize Physics Engine
        self.initialize_physics()

        # Game Logic
        self.score = 0
        self.max_score = COIN_VALUE * len(self.scene.get_sprite_list(LAYER_NAME_COINS))

    def initialize_physics(self, inverted=False):
        """
        Initialize Physics Engine, allowing for inversion of gravity.
        :param inverted: True if player is inverting gravity to fall up rather than down.
        """
        inv_int = -1 if inverted else 1
        self.physics_engine = arcade.PhysicsEnginePlatformer(
            self.player_one, gravity_constant=GRAVITY * inv_int, walls=[
                self.scene[LAYER_NAME_PLATFORMS]
            ]
        )

    def on_key_press(self, key: int, modifiers: int):
        """
        Called whenever a key is pressed.
        """
        self.player_one.on_key_press(key)

    def on_key_release(self, key: int, modifiers: int):
        """
        Called whenever a key is released.
        """
        self.player_one.on_key_release(key)

    def camera_follow(self):
        """
        Called each frame to move the camera towards the player.
        :return: None
        """
        self.camera.move_to(self.get_camera_position(), 0.1)

    def get_camera_position(self, parallax=1):
        """
        Determine the new target position of the camera. It will essentially
        be the player's position plus some constraints. Said constraints are
        currently only working for the bottom/left of the map, not the top/right.
        :param parallax: Feature I never got working. Don't worry about it lol
        :return: A tuple representing the camera's new target coordinates.
        """
        screen_center_x = self.player_one.center_x - (self.camera.viewport_width / 2)
        screen_center_y = self.player_one.center_y - (self.camera.viewport_height / 2)
        right_edge = self.map_width - (self.camera.viewport_width / 2) - 250
        top_edge = self.map_height - (self.camera.viewport_height / 2) - 250
        # Don't let camera travel past boundaries
        if screen_center_x < 0:
            screen_center_x = 0
        if screen_center_y < 0:
            screen_center_y = 0
        if screen_center_x > right_edge:
            screen_center_x = right_edge
        if screen_center_y > top_edge:
            screen_center_y = top_edge

        return screen_center_x * parallax, screen_center_y * parallax

    def on_draw(self):
        """
        Render the screen.
        """

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
        """
        Display to the screen any text we need to.
        """
        score_text = f"Score: {self.score}/{self.max_score}"
        arcade.draw_text(
            score_text,
            20,
            20,
            font_size=24,
            font_name="calibri",
            bold=True
        )
        if self.has_won():
            if self.won_world:
                success_text = "World Complete!"
            else:
                success_text = "Stage Complete"
            arcade.draw_text(
                success_text,
                SCREEN_WIDTH / 2,
                SCREEN_HEIGHT / 2 + 240,
                font_size=48,
                width=480,
                align="center",
                font_name="calibri",
                bold=True,
                anchor_x="center",
                anchor_y="center",
                multiline=False
            )

    def on_update(self, delta_time):
        """
        Movement and game logic.
        """

        # Move the player with the physics engine.
        self.player_one.update_speed(self.physics_engine)
        self.physics_engine.update()

        # Center the camera on the player.
        self.camera_follow()

        # Check for coin collisions
        coin_hit_list = arcade.check_for_collision_with_list(
            self.player_one, self.scene[LAYER_NAME_COINS]
        )
        for coin in coin_hit_list:
            # Remove the coin
            coin.kill()
            arcade.play_sound(self.coin_sound, volume=self.SFX_VOLUME)
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
        """
        Play a death sound and restart the level.
        :return: None
        """
        arcade.play_sound(self.death_sound, volume=self.SFX_VOLUME)
        self.setup()

    def has_won(self) -> bool:
        """
        Return true if the player's score has reached the max score for the level.
        i.e. if the player has collected all the coins/items
        :return: True if player has finished collecting, false if not.
        """
        return self.score >= self.max_score

    def win(self):
        """
        Increment the level and set up the game again. Tried introducing a wait call
        to keep the friendly success message on the screen for longer but was unsuccessful.
        :return: None
        """
        print("stage complete")
        self.level += 1
        # timer = threading.Timer(3.0, lambda: self.setup())
        # timer.start()
        self.setup()

    def win_world(self):
        """
        Declare that the player has finished all maps/levels available.
        :return: None
        """
        self.won_world = True


def main():
    """
    Start the window and run arcade.
    :return: None
    """
    window = MyGame()
    window.setup()
    arcade.run()


if __name__ == "__main__":
    main()
