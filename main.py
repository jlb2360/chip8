import pygame
import sys
from src.cpu import CPU
from src.memory import Memory
from src.display import Display

# Key mapping from Pygame keys to Chip-8 keypad
KEY_MAP = {
    pygame.K_1: 0x1, pygame.K_2: 0x2, pygame.K_3: 0x3, pygame.K_4: 0xC,
    pygame.K_q: 0x4, pygame.K_w: 0x5, pygame.K_e: 0x6, pygame.K_r: 0xD,
    pygame.K_a: 0x7, pygame.K_s: 0x8, pygame.K_d: 0x9, pygame.K_f: 0xE,
    pygame.K_z: 0xA, pygame.K_x: 0x0, pygame.K_c: 0xB, pygame.K_v: 0xF,
}

def main():
    """Main function to run the emulator."""
    if len(sys.argv) < 2:
        print("Usage: poetry run python main.py <path_to_rom>")
        sys.exit(1)

    rom_path = sys.argv[1]

    pygame.init()

    memory = Memory()
    display = Display()
    cpu = CPU(memory, display)

    try:
        memory.load_rom(rom_path)
    except FileNotFoundError:
        print(f"Error: ROM file not found at '{rom_path}'")
        sys.exit(1)

    clock = pygame.time.Clock()
    running = True

    while running:
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                running = False
            # Handle key presses
            if event.type == pygame.KEYDOWN:
                if event.key in KEY_MAP:
                    cpu.keyboard[KEY_MAP[event.key]] = 1
            if event.type == pygame.KEYUP:
                if event.key in KEY_MAP:
                    cpu.keyboard[KEY_MAP[event.key]] = 0

        # Execute multiple CPU cycles per frame for speed
        for _ in range(10):
            cpu.execution_cycle()

        cpu.update_timers()
        display.update()

        # 60 Hz timer update rate
        clock.tick(60)

    pygame.quit()

if __name__ == "__main__":
    main()