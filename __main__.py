#!/usr/bin/env python3

import sys
from rpg import app

if __name__ == "__main__":
    game = app.Game()
    sys.exit(game.run())
