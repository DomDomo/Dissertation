import os
import sys
import threading
import pygame

SCALE_FACTOR = 3
MARGIN = 5


class DisplayManager:
    def __init__(self):
        self.running = False
        self.display_thread = None
        self.screen = None
        pygame.init()

    def display_images(self, image1, image2, text, tiny_image):
        image1_surface = self._make_pygame_image(image1)
        image2_surface = self._make_pygame_image(image2)
        tiny_image_surface = self._make_pygame_image(tiny_image)

        # Resize images to fit window
        image1_surface = pygame.transform.scale(
            image1_surface, (image1.width // SCALE_FACTOR, image1.height // SCALE_FACTOR))
        image2_surface = pygame.transform.scale(
            image2_surface, (image2.width // SCALE_FACTOR, image2.height // SCALE_FACTOR))
        blank_image_surface = pygame.Surface(
            (image1.width // SCALE_FACTOR, image1.height // SCALE_FACTOR))
        tiny_width, tiny_height = tiny_image_surface.get_size()
        if tiny_width > 150:
            scale_factor = 150 / tiny_width
            tiny_width = 150
            tiny_height = int(tiny_height * scale_factor)
            tiny_image_surface = pygame.transform.scale(
                tiny_image_surface, (tiny_width, tiny_height))

        # Calculate the window size to fit the images with margin
        window_width = (image1_surface.get_width(
        ) + image2_surface.get_width() + blank_image_surface.get_width()) + MARGIN * 4
        window_height = max(image1_surface.get_height(), image2_surface.get_height(
        ), blank_image_surface.get_height()) + MARGIN * 2

        # Add text to the middle of the blank image surface
        font = pygame.font.Font(None, 36)
        text_surface = font.render(text, True, (255, 255, 255))
        text_rect = text_surface.get_rect(center=(
            blank_image_surface.get_width() // 2, blank_image_surface.get_height() // 4))
        blank_image_surface.blit(text_surface, text_rect)

        # Add the tiny image below the text
        if "Generator" in text:
            tiny_image_rect = tiny_image_surface.get_rect(
                center=(blank_image_surface.get_width() // 2, blank_image_surface.get_height() * 3 // 6))
            blank_image_surface.blit(tiny_image_surface, tiny_image_rect)

        # Start the Pygame display loop in a separate thread
        if not self.running:
            self.running = True
            self.display_thread = threading.Thread(
                target=self._display_loop,
                args=(image1_surface, image2_surface, blank_image_surface, window_width, window_height))
            self.display_thread.start()
        else:
            # Update the display if the Pygame window is already running
            self._update_display(image1_surface, image2_surface,
                                 blank_image_surface, window_width, window_height)

    def _display_loop(self, image1_surface, image2_surface, blank_image_surface, window_width, window_height):
        # Initialize Pygame
        os.environ['PYGAME_HIDE_SUPPORT_PROMPT'] = "hide"
        pygame.init()
        self.screen = pygame.display.set_mode((window_width, window_height))
        pygame.display.set_caption("Pygame Image Display")

        # Display the initial images
        self._update_display(image1_surface, image2_surface,
                             blank_image_surface, window_width, window_height)

        # Main loop
        while self.running:
            for event in pygame.event.get():
                if event.type == pygame.QUIT:
                    self.running = False
                elif event.type == pygame.KEYDOWN:
                    if event.key == pygame.K_ESCAPE:
                        self.running = False

        # Quit Pygame
        pygame.quit()
        sys.exit()

    def _update_display(self, image1_surface, image2_surface, blank_image_surface, window_width, window_height):
        if self.screen is not None:
            self.screen.fill((0, 0, 0))  # Clear the screen with black

            # Blit the images
            self.screen.blit(image1_surface, (MARGIN, MARGIN))
            self.screen.blit(
                image2_surface, (image1_surface.get_width() + MARGIN * 2, MARGIN))
            self.screen.blit(blank_image_surface, (image1_surface.get_width(
            ) + image2_surface.get_width() + MARGIN * 3, MARGIN))

            # # Add text to the top of the blank surface
            # font = pygame.font.Font(None, 36)
            # text = font.render("Top Text", True, (255, 255, 255))
            # text_rect = text.get_rect()
            # text_rect.midtop = (image1_surface.get_width(
            # ) + image2_surface.get_width() + blank_image_surface.get_width() // 2 + MARGIN * 3, MARGIN)
            # self.screen.blit(text, text_rect)

            # # Add text to the middle of the blank surface
            # text = font.render("Middle Text", True, (255, 255, 255))
            # text_rect = text.get_rect()
            # text_rect.midtop = (image1_surface.get_width() + image2_surface.get_width(
            # ) + blank_image_surface.get_width() // 2 + MARGIN * 3, blank_image_surface.get_height() // 2 + MARGIN)
            # self.screen.blit(text, text_rect)

            pygame.display.flip()

    def _make_pygame_image(self, image):
        return pygame.image.frombuffer(image.tobytes(), image.size, image.mode)
