"""
main.py — Entry point for Mirror Clone Survival.

Run with:
    python main.py
"""

import sys

import pygame

from config import FPS, WINDOW_HEIGHT, WINDOW_TITLE, WINDOW_WIDTH
from game import Game, STATE_GAME_OVER, STATE_INSTRUCTION


def main() -> None:
    pygame.init()

    screen = pygame.display.set_mode((WINDOW_WIDTH, WINDOW_HEIGHT))
    pygame.display.set_caption(WINDOW_TITLE)
    clock = pygame.time.Clock()

    game = Game(screen)

    running = True
    while running:
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                running = False

            if event.type == pygame.KEYDOWN:
                # Quit only outside instruction/replay
                if event.key == pygame.K_ESCAPE and not game.replay_mode and game.state != STATE_INSTRUCTION:
                    running = False
                # Restart only on game over and not during replay
                if event.key == pygame.K_r and game.state == STATE_GAME_OVER and not game.replay_mode:
                    game.reset()

            # Forward all events to game
            game.handle_event(event)

        game.update()
        game.render()
        pygame.display.flip()
        clock.tick(FPS)

    pygame.quit()
    sys.exit()


if __name__ == "__main__":
    main()
