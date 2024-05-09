import os
import sys
import threading
import pygame
from PIL import Image

SCALE_FACTOR = 3
MARGIN = 5


class DisplayManager:
    def __init__(self):
        self.running = False
        self.display_thread = None
        self.screen = None

    def display_images(self, folder, screenshot, annotated):
        image1 = Image.open(os.path.join(folder, screenshot))
        image2 = Image.fromarray(annotated)

        # Convert images to Pygame surfaces
        image1_surface = self._make_pygame_image(image1)
        image2_surface = self._make_pygame_image(image2)

        # Resize images to fit window
        image1_surface = pygame.transform.scale(
            image1_surface, (image1.width // SCALE_FACTOR, image1.height // SCALE_FACTOR))
        image2_surface = pygame.transform.scale(
            image2_surface, (image2.width // SCALE_FACTOR, image2.height // SCALE_FACTOR))

        # Calculate the window size to fit the images with margin
        window_width = (image1_surface.get_width() +
                        image2_surface.get_width()) + MARGIN * 3
        window_height = max(image1_surface.get_height(),
                            image2_surface.get_height()) + MARGIN * 2

        # Start the Pygame display loop in a separate thread
        if not self.running:
            self.running = True
            self.display_thread = threading.Thread(
                target=self._display_loop, args=(image1_surface, image2_surface, window_width, window_height))
            self.display_thread.start()
        else:
            # Update the display if the Pygame window is already running
            self._update_display(
                image1_surface, image2_surface, window_width, window_height)

    def _display_loop(self, image1_surface, image2_surface, window_width, window_height):
        # Initialize Pygame
        os.environ['PYGAME_HIDE_SUPPORT_PROMPT'] = "hide"
        pygame.init()
        self.screen = pygame.display.set_mode((window_width, window_height))

        # Set Pygame application name
        pygame.display.set_caption("Pygame Image Display")

        # Display the initial images
        self._update_display(image1_surface, image2_surface,
                             window_width, window_height)

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

    def _update_display(self, image1_surface, image2_surface, window_width, window_height):
        if self.screen is not None:
            self.screen.fill((0, 0, 0))  # Clear the screen with black
            self.screen.blit(image1_surface, (MARGIN, MARGIN))
            self.screen.blit(
                image2_surface, (image1_surface.get_width() + MARGIN * 2, MARGIN))
            pygame.display.flip()

    def _make_pygame_image(self, image):
        return pygame.image.frombuffer(image.tobytes(), image.size, image.mode)
