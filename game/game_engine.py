import pygame
from .bird import Bird
from .pipe import Pipe

# Game Engine

WHITE = (255, 255, 255)
GREEN = (0, 150, 0)
BLACK = (0, 0, 0)


class GameEngine:
    def __init__(self, width, height):
        self.width = width
        self.height = height

        self.bird = Bird(width // 4, height // 2)
        self.pipe_speed = 4
        self.pipe_interval = 90  # frames between pipe spawns
        self._spawn_timer = 0
        self.pipes = [Pipe(width + 100, height, speed=self.pipe_speed)]
        self.score = 0

        self.font = pygame.font.SysFont("Arial", 30)
        self.game_over_font = pygame.font.SysFont("Arial", 56, bold=True)
        self.final_score_font = pygame.font.SysFont("Arial", 36)
        self.instruction_font = pygame.font.SysFont("Arial", 24)

        self.game_over = False

    def handle_event(self, event):
        # Once the game is over, normal gameplay input is disabled.
        if self.game_over:
            return

        # Flap is edge-triggered (KEYDOWN / MOUSEBUTTONDOWN), not held.
        if event.type == pygame.KEYDOWN and event.key == pygame.K_SPACE:
            self.bird.flap()

        if event.type == pygame.MOUSEBUTTONDOWN:
            self.bird.flap()

    def handle_input(self):
        # Reserved for continuously-held-key input; flapping is handled
        # in handle_event instead, so there's nothing to poll here.
        pass

    def _bird_collides_with_rect(self, rect):
        """Check whether the bird's circular hitbox overlaps a rectangle."""
        closest_x = max(rect.left, min(self.bird.x, rect.right))
        closest_y = max(rect.top, min(self.bird.y, rect.bottom))

        dx = self.bird.x - closest_x
        dy = self.bird.y - closest_y

        return dx * dx + dy * dy <= self.bird.radius * self.bird.radius

    def _check_pipe_collision(self, pipe):
        """Check the bird against both the upper and lower pipe."""
        return (
            self._bird_collides_with_rect(pipe.top_rect())
            or self._bird_collides_with_rect(pipe.bottom_rect())
        )

    def update(self):
        # Freeze all normal gameplay after Game Over.
        if self.game_over:
            return

        self.bird.update()

        # Ground and ceiling collision.
        if (
            self.bird.y - self.bird.radius <= 0
            or self.bird.y + self.bird.radius >= self.height
        ):
            self.game_over = True
            return

        self._spawn_timer += 1

        if self._spawn_timer >= self.pipe_interval:
            self._spawn_timer = 0
            self.pipes.append(
                Pipe(self.width, self.height, speed=self.pipe_speed)
            )

        for pipe in self.pipes:
            pipe.move()

            # Task 1 collision detection:
            # check the entire circular bird hitbox instead of
            # checking only the bird's center point.
            if self._check_pipe_collision(pipe):
                self.game_over = True
                return

            # Preserve existing scoring behavior.
            if not pipe.scored and pipe.x + pipe.width < self.bird.x:
                pipe.scored = True
                self.score += 1

        self.pipes = [p for p in self.pipes if not p.off_screen()]

    def render(self, screen):
        # Draw pipes.
        for pipe in self.pipes:
            pygame.draw.rect(screen, GREEN, pipe.top_rect())
            pygame.draw.rect(screen, GREEN, pipe.bottom_rect())

        # Draw bird.
        pygame.draw.circle(
            screen,
            WHITE,
            (int(self.bird.x), int(self.bird.y)),
            self.bird.radius
        )

        # Draw score during gameplay.
        score_text = self.font.render(
            f"Score: {self.score}",
            True,
            WHITE
        )
        screen.blit(score_text, (10, 10))

        # Task 2: Game Over screen.
        if self.game_over:
            overlay = pygame.Surface((self.width, self.height))
            overlay.set_alpha(160)
            overlay.fill(BLACK)
            screen.blit(overlay, (0, 0))

            game_over_text = self.game_over_font.render(
                "GAME OVER",
                True,
                WHITE
            )

            final_score_text = self.final_score_font.render(
                f"Final Score: {self.score}",
                True,
                WHITE
            )

            instruction_text = self.instruction_font.render(
                "Close the window to exit",
                True,
                WHITE
            )

            game_over_rect = game_over_text.get_rect(
                center=(self.width // 2, self.height // 2 - 80)
            )

            final_score_rect = final_score_text.get_rect(
                center=(self.width // 2, self.height // 2)
            )

            instruction_rect = instruction_text.get_rect(
                center=(self.width // 2, self.height // 2 + 60)
            )

            screen.blit(game_over_text, game_over_rect)
            screen.blit(final_score_text, final_score_rect)
            screen.blit(instruction_text, instruction_rect)