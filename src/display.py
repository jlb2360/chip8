import pygame

class Display:
    def __init__(self, scale=10):
        self.width = 64
        self.height = 32
        self.scale = scale
        self.screen = pygame.display.set_mode((self.width *self.scale, self.height * self.scale))
        self.pixels = [[0] * self.width for _ in range(self.height)]
        pygame.display.set_caption("Chip-8")

    def clear(self):
        self.pixels = [[0] * self.width for _ in range(self.height)]
        self.update()

    def draw_pixel(self, x, y):
        x %= self.width
        y %= self.height

        
        self.pixels[y][x] ^= 1
        return self.pixels[y][x] == 0
    
    def update(self):
        self.screen.fill((0, 0, 0))
        for y in range(self.height):
            for x in range(self.width):
                if self.pixels[y][x]:
                    pygame.draw.rect(self.screen, (255, 255, 255),
                                     (x * self.scale, y * self.scale, self.scale, self.scale))
                    

        pygame.display.flip()