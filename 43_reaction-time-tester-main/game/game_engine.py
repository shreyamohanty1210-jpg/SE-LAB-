import pygame
import math
from array import array
from .round import Round

WHITE = (255, 255, 255)
BLACK = (0, 0, 0)
GRAY = (90, 90, 90)
GREEN = (40, 180, 90)
BLUE = (50, 90, 170)


class GameEngine:
    def __init__(
        self,
        width,
        height,
        rounds_total=5,
        min_wait_ms=1000,
        max_wait_ms=3000
    ):
        self.width = width
        self.height = height

        self.rounds_total = rounds_total
        self.min_wait_ms = min_wait_ms
        self.max_wait_ms = max_wait_ms

        self.round = Round(
            self.min_wait_ms,
            self.max_wait_ms
        )

        self.reaction_times = []
        self.rounds_completed = 0

        self.result_shown_at = None
        self.result_pause_ms = 800

        self.font = pygame.font.SysFont("Arial", 30)
        self.big_font = pygame.font.SysFont("Arial", 46)
        self.small_font = pygame.font.SysFont("Arial", 24)

        self.game_over = False
        self.results_screen = False
        self.replay_menu = False

        # Initialize sound
        if not pygame.mixer.get_init():
            pygame.mixer.init(
                frequency=44100,
                size=-16,
                channels=1
            )

        self.go_sound = self.create_tone(880, 120)
        self.false_start_sound = self.create_tone(220, 250)
        self.session_end_sound = self.create_end_sound()

        self.previous_round_state = self.round.state

    def create_tone(self, frequency, duration_ms):
        sample_rate = 44100
        sample_count = int(
            sample_rate * duration_ms / 1000
        )

        samples = array("h")

        for i in range(sample_count):
            value = int(
                16000 *
                math.sin(
                    2 * math.pi *
                    frequency *
                    i /
                    sample_rate
                )
            )
            samples.append(value)

        return pygame.mixer.Sound(buffer=samples.tobytes())

    def create_end_sound(self):
        sample_rate = 44100

        frequencies = [
            (660, 150),
            (523, 150),
            (392, 250)
        ]

        samples = array("h")

        for frequency, duration_ms in frequencies:
            sample_count = int(
                sample_rate * duration_ms / 1000
            )

            for i in range(sample_count):
                value = int(
                    16000 *
                    math.sin(
                        2 * math.pi *
                        frequency *
                        i /
                        sample_rate
                    )
                )
                samples.append(value)

        return pygame.mixer.Sound(buffer=samples.tobytes())

    def handle_event(self, event):

        # Replay menu
        if self.replay_menu:
            if event.type == pygame.KEYDOWN:

                if event.key == pygame.K_1:
                    self.start_new_game(
                        rounds_total=3,
                        min_wait_ms=800,
                        max_wait_ms=1800
                    )

                elif event.key == pygame.K_2:
                    self.start_new_game(
                        rounds_total=5,
                        min_wait_ms=1000,
                        max_wait_ms=3000
                    )

                elif event.key == pygame.K_3:
                    self.start_new_game(
                        rounds_total=7,
                        min_wait_ms=1500,
                        max_wait_ms=3500
                    )

                elif event.key == pygame.K_4:
                    pygame.quit()
                    raise SystemExit

            return

        # Results screen
        if self.results_screen:
            if (
                event.type == pygame.KEYDOWN
                or event.type == pygame.MOUSEBUTTONDOWN
            ):
                self.results_screen = False
                self.replay_menu = True

            return

        # Normal gameplay
        is_click = event.type == pygame.MOUSEBUTTONDOWN

        is_space = (
            event.type == pygame.KEYDOWN
            and event.key == pygame.K_SPACE
        )

        if (is_click or is_space):

            # False start
            if self.round.state == "waiting":
                self.false_start_sound.play()

                self.round.register_input()

                self.rounds_completed += 1
                self.result_shown_at = pygame.time.get_ticks()
                return

            # Valid reaction
            if self.round.state == "go":
                reaction_ms = self.round.register_input()

                self.rounds_completed += 1

                if reaction_ms is not None:
                    self.reaction_times.append(reaction_ms)

                self.result_shown_at = pygame.time.get_ticks()

    def handle_input(self):
        pass

    def update(self):

        if self.game_over:
            return

        self.round.update()

        # Screen just changed from waiting to go
        if (
            self.previous_round_state == "waiting"
            and self.round.state == "go"
        ):
            self.go_sound.play()

        self.previous_round_state = self.round.state

        if self.round.state == "result":

            now = pygame.time.get_ticks()

            if now - self.result_shown_at >= self.result_pause_ms:
                self._start_next_round()

    def _start_next_round(self):

        if self.rounds_completed >= self.rounds_total:

            self.game_over = True
            self.results_screen = True

            # Session ending sound
            self.session_end_sound.play()

            return

        self.round = Round(
            self.min_wait_ms,
            self.max_wait_ms
        )

        self.previous_round_state = self.round.state

    def start_new_game(
        self,
        rounds_total,
        min_wait_ms,
        max_wait_ms
    ):

        self.rounds_total = rounds_total
        self.min_wait_ms = min_wait_ms
        self.max_wait_ms = max_wait_ms

        self.round = Round(
            self.min_wait_ms,
            self.max_wait_ms
        )

        self.reaction_times = []
        self.rounds_completed = 0

        self.result_shown_at = None

        self.game_over = False
        self.results_screen = False
        self.replay_menu = False

        self.previous_round_state = self.round.state

    def average_reaction_ms(self):

        if not self.reaction_times:
            return 0

        return round(
            sum(self.reaction_times)
            / len(self.reaction_times)
        )

    def render(self, screen):

        if self.replay_menu:
            self._render_replay_menu(screen)
            return

        if self.results_screen:
            self._render_results(screen)
            return

        if self.round.state == "waiting":

            bg = GRAY
            message = "Wait for green..."

        elif self.round.state == "go":

            bg = GREEN
            message = "Click now!"

        else:

            bg = BLUE

            if self.round.reaction_ms is None:
                message = "False Start!"
            else:
                message = f"{self.round.reaction_ms} ms"

        screen.fill(bg)

        text_surf = self.big_font.render(
            message,
            True,
            WHITE
        )

        text_rect = text_surf.get_rect(
            center=(
                self.width // 2,
                self.height // 2
            )
        )

        screen.blit(
            text_surf,
            text_rect
        )

        round_text = self.font.render(
            f"Round {self.rounds_completed + 1}/{self.rounds_total}",
            True,
            WHITE
        )

        screen.blit(
            round_text,
            (10, 10)
        )

        avg_text = self.font.render(
            f"Avg: {self.average_reaction_ms()} ms",
            True,
            WHITE
        )

        screen.blit(
            avg_text,
            (self.width - 190, 10)
        )

    def _render_results(self, screen):

        screen.fill(BLUE)

        title = self.big_font.render(
            "GAME OVER",
            True,
            WHITE
        )

        title_rect = title.get_rect(
            center=(
                self.width // 2,
                60
            )
        )

        screen.blit(
            title,
            title_rect
        )

        y = 120

        for index, reaction_time in enumerate(
            self.reaction_times,
            start=1
        ):

            result_text = self.small_font.render(
                f"Round {index}: {reaction_time} ms",
                True,
                WHITE
            )

            screen.blit(
                result_text,
                (
                    self.width // 2 - 100,
                    y
                )
            )

            y += 35

        average_text = self.font.render(
            f"Average: {self.average_reaction_ms()} ms",
            True,
            WHITE
        )

        average_rect = average_text.get_rect(
            center=(
                self.width // 2,
                y + 20
            )
        )

        screen.blit(
            average_text,
            average_rect
        )

        instruction = self.small_font.render(
            "Press any key or click to continue",
            True,
            WHITE
        )

        instruction_rect = instruction.get_rect(
            center=(
                self.width // 2,
                self.height - 50
            )
        )

        screen.blit(
            instruction,
            instruction_rect
        )

    def _render_replay_menu(self, screen):

        screen.fill(BLUE)

        title = self.big_font.render(
            "PLAY AGAIN?",
            True,
            WHITE
        )

        title_rect = title.get_rect(
            center=(
                self.width // 2,
                100
            )
        )

        screen.blit(
            title,
            title_rect
        )

        options = [
            "1 - Easy",
            "2 - Medium",
            "3 - Hard",
            "4 - Exit"
        ]

        y = 200

        for option in options:

            option_text = self.font.render(
                option,
                True,
                WHITE
            )

            option_rect = option_text.get_rect(
                center=(
                    self.width // 2,
                    y
                )
            )

            screen.blit(
                option_text,
                option_rect
            )

            y += 55