import pygame
from .bird import Bird
from .pipe import Pipe
from .sound_manager import SoundManager


# Game Engine

WHITE = (255, 255, 255)
GREEN = (0, 150, 0)
BLACK = (0, 0, 0)


class GameEngine:
    def __init__(self, width, height):
        self.width = width
        self.height = height

        self.font = pygame.font.SysFont("Arial", 30)
        self.game_over_font = pygame.font.SysFont(
            "Arial",
            56,
            bold=True,
        )
        self.final_score_font = pygame.font.SysFont("Arial", 36)
        self.instruction_font = pygame.font.SysFont("Arial", 24)
        self.difficulty_font = pygame.font.SysFont("Arial", 30)

        # Task 3: Difficulty settings
        # Format: (pipe speed, pipe gap)
        self.difficulties = {
            "Easy": (3, 180),
            "Medium": (4, 150),
            "Hard": (6, 120),
        }

        self.difficulty = "Medium"

        self.game_over = False
        self.exit_requested = False

        # Task 4: Initialize sound manager once.
        self.sound_manager = SoundManager()

        self._reset_game()

    def _reset_game(self):
        """Reset all state needed for a completely new game."""

        self.bird = Bird(
            self.width // 4,
            self.height // 2,
        )

        self.pipe_speed, self.pipe_gap = self.difficulties[
            self.difficulty
        ]

        self.pipe_interval = 90
        self._spawn_timer = 0

        self.pipes = [
            Pipe(
                self.width + 100,
                self.height,
                gap=self.pipe_gap,
                speed=self.pipe_speed,
            )
        ]

        self.score = 0
        self.game_over = False
        self.exit_requested = False

    def _start_new_game(self, difficulty):
        """Start a fresh game using the selected difficulty."""

        self.difficulty = difficulty
        self._reset_game()

    def _set_game_over(self):
        """Enter Game Over state and play the death sound once."""

        if not self.game_over:
            self.game_over = True
            self.sound_manager.play_die()

    def handle_event(self, event):
        # -------------------------
        # Game Over input
        # -------------------------
        if self.game_over:
            if event.type == pygame.KEYDOWN:
                if event.key == pygame.K_e:
                    self.exit_requested = True

                elif event.key == pygame.K_1:
                    self._start_new_game("Easy")

                elif event.key == pygame.K_2:
                    self._start_new_game("Medium")

                elif event.key == pygame.K_3:
                    self._start_new_game("Hard")

            return

        # -------------------------
        # Normal gameplay input
        # -------------------------
        if (
            event.type == pygame.KEYDOWN
            and event.key == pygame.K_SPACE
        ):
            self.bird.flap()
            self.sound_manager.play_flap()

        if event.type == pygame.MOUSEBUTTONDOWN:
            self.bird.flap()
            self.sound_manager.play_flap()

    def handle_input(self):
        # Reserved for continuously-held-key input.
        pass

    def _bird_collides_with_rect(self, rect):
        """
        Check whether the bird's circular hitbox overlaps a rectangle.

        This is the Task 1 collision detection.
        """

        closest_x = max(
            rect.left,
            min(self.bird.x, rect.right),
        )

        closest_y = max(
            rect.top,
            min(self.bird.y, rect.bottom),
        )

        dx = self.bird.x - closest_x
        dy = self.bird.y - closest_y

        return (
            dx * dx + dy * dy
            <= self.bird.radius * self.bird.radius
        )

    def _check_pipe_collision(self, pipe):
        """Check the bird against both the upper and lower pipe."""

        return (
            self._bird_collides_with_rect(pipe.top_rect())
            or self._bird_collides_with_rect(pipe.bottom_rect())
        )

    def update(self):
        # Freeze normal gameplay after Game Over.
        if self.game_over:
            return

        self.bird.update()

        # -------------------------
        # Ceiling / ground collision
        # -------------------------
        if (
            self.bird.y - self.bird.radius <= 0
            or self.bird.y + self.bird.radius >= self.height
        ):
            self._set_game_over()
            return

        # -------------------------
        # Pipe spawning
        # -------------------------
        self._spawn_timer += 1

        if self._spawn_timer >= self.pipe_interval:
            self._spawn_timer = 0

            self.pipes.append(
                Pipe(
                    self.width,
                    self.height,
                    gap=self.pipe_gap,
                    speed=self.pipe_speed,
                )
            )

        # -------------------------
        # Pipe movement, collision
        # and scoring
        # -------------------------
        for pipe in self.pipes:
            pipe.move()

            # Preserve Task 1 collision detection.
            if self._check_pipe_collision(pipe):
                self._set_game_over()
                return

            # Preserve existing scoring behavior.
            if (
                not pipe.scored
                and pipe.x + pipe.width < self.bird.x
            ):
                pipe.scored = True
                self.score += 1

                # Task 4: Play point sound exactly once.
                self.sound_manager.play_point()

        # Remove pipes that have moved off screen.
        self.pipes = [
            pipe
            for pipe in self.pipes
            if not pipe.off_screen()
        ]

    def render(self, screen):
        # -------------------------
        # Draw pipes
        # -------------------------
        for pipe in self.pipes:
            pygame.draw.rect(
                screen,
                GREEN,
                pipe.top_rect(),
            )

            pygame.draw.rect(
                screen,
                GREEN,
                pipe.bottom_rect(),
            )

        # -------------------------
        # Draw bird
        # -------------------------
        pygame.draw.circle(
            screen,
            WHITE,
            (
                int(self.bird.x),
                int(self.bird.y),
            ),
            self.bird.radius,
        )

        # -------------------------
        # Draw current score
        # -------------------------
        score_text = self.font.render(
            f"Score: {self.score}",
            True,
            WHITE,
        )

        screen.blit(
            score_text,
            (10, 10),
        )

        # -------------------------
        # Game Over screen
        # -------------------------
        if self.game_over:
            overlay = pygame.Surface(
                (self.width, self.height)
            )

            overlay.set_alpha(170)
            overlay.fill(BLACK)

            screen.blit(
                overlay,
                (0, 0),
            )

            game_over_text = self.game_over_font.render(
                "GAME OVER",
                True,
                WHITE,
            )

            final_score_text = self.final_score_font.render(
                f"Final Score: {self.score}",
                True,
                WHITE,
            )

            difficulty_text = self.difficulty_font.render(
                "Choose Difficulty",
                True,
                WHITE,
            )

            easy_text = self.instruction_font.render(
                "1 - Easy",
                True,
                WHITE,
            )

            medium_text = self.instruction_font.render(
                "2 - Medium",
                True,
                WHITE,
            )

            hard_text = self.instruction_font.render(
                "3 - Hard",
                True,
                WHITE,
            )

            exit_text = self.instruction_font.render(
                "E - Exit",
                True,
                WHITE,
            )

            game_over_rect = game_over_text.get_rect(
                center=(
                    self.width // 2,
                    100,
                )
            )

            final_score_rect = final_score_text.get_rect(
                center=(
                    self.width // 2,
                    170,
                )
            )

            difficulty_rect = difficulty_text.get_rect(
                center=(
                    self.width // 2,
                    250,
                )
            )

            easy_rect = easy_text.get_rect(
                center=(
                    self.width // 2,
                    310,
                )
            )

            medium_rect = medium_text.get_rect(
                center=(
                    self.width // 2,
                    360,
                )
            )

            hard_rect = hard_text.get_rect(
                center=(
                    self.width // 2,
                    410,
                )
            )

            exit_rect = exit_text.get_rect(
                center=(
                    self.width // 2,
                    470,
                )
            )

            screen.blit(
                game_over_text,
                game_over_rect,
            )

            screen.blit(
                final_score_text,
                final_score_rect,
            )

            screen.blit(
                difficulty_text,
                difficulty_rect,
            )

            screen.blit(
                easy_text,
                easy_rect,
            )

            screen.blit(
                medium_text,
                medium_rect,
            )

            screen.blit(
                hard_text,
                hard_rect,
            )

            screen.blit(
                exit_text,
                exit_rect,
            )