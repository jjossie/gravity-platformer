import arcade


class Coin(arcade.Sprite):

    def __init__(self):
        super().__init__()
        self.value = 15
