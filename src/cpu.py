import logging
import random

class CPU:
    def __init__(self, memory, display):
        self.memory = memory
        self.display = display
        
        self.V = bytearray(16) # Vx registers

        self.I = 0 # 16-bit register for memory addresses
        
        # 0x200 is the start address for most programs
        self.program_counter = 0x200 # Current executing address

        self.delay_timer = 0
        self.sound_timer = 0

        self.stack = [] # subroutine return address

        self.keyboard = [0] * 16

        self.logger = logging.getLogger("CHIP8")
        self.logger.setLevel(logging.INFO)

    def execution_cycle(self):
        opcode = self._next_opcode()
        self._execute(opcode)

    def _next_opcode(self):
        opcode = (self.memory.ram[self.program_counter] << 8) | self.memory.ram[self.program_counter + 1]
        self.program_counter += 2
        return opcode

    def _execute(self, opcode):
        addr = opcode & 0x0FFF
        nibble = opcode & 0x000F
        x = (opcode & 0x0F00) >> 8
        y = (opcode & 0x00F0) >> 4
        kk = opcode & 0x00FF

        match opcode:
            case 0x00E0:
                self.display.clear()
            case 0x00EE:
                self.program_counter = self.stack.pop()
            case co if (co & 0xF000) == 0x1000:
                self.program_counter = addr
            case co if (co & 0xF000) == 0x2000:
                self.stack.append(self.program_counter)
                self.program_counter = addr
            case co if (co & 0xF000) == 0x3000:
                if self.V[x] == kk:
                    self.program_counter += 2
            case co if (co & 0xF000) == 0x4000:
                if self.V[x] != kk:
                    self.program_counter += 2
            case co if (co & 0xF000) == 0x5000:
                if self.V[x] == self.V[y]:
                    self.program_counter += 2
            case co if (co & 0xF000) == 0x6000:
                self.V[x] = kk
            case co if (co & 0xF000) == 0x7000:
                self.V[x] = (self.V[x] + kk) & 0xFF
            case co if (co & 0xF00F) == 0x8000:
                self.V[x] = self.V[y]
            case co if (co & 0xF00F) == 0x8001:
                self.V[x] |= self.V[y]
                self.V[0xF] = 0 # quirk of chip 8
            case co if (co & 0xF00F) == 0x8002:
                self.V[x] = self.V[x] & self.V[y]
                self.V[0xF] = 0 # quirk of chip 8
            case co if (co & 0xF00F) == 0x8003:
                self.V[x] = self.V[x] ^ self.V[y]
                self.V[0xF] = 0 # quirk of chip 8
            case co if (co & 0xF00F) == 0x8004:
                result = self.V[x] + self.V[y]
                test = 1 if result > 255 else 0
                self.V[x] = result & 0xFF
                self.V[0xF] = test
            case co if (co & 0xF00F) == 0x8005:
                borrow = 1 if self.V[x] >= self.V[y] else 0
                self.V[x] = (self.V[x] - self.V[y]) & 0xFF
                self.V[0xF] = borrow
            case co if (co & 0xF00F) == 0x8006:
                test = self.V[x] & 0x1
                self.V[x] = self.V[y] >> 1
                self.V[0xF] = test
            case co if (co & 0xF00F) == 0x8007:
                test = 1 if self.V[x] <= self.V[y] else 0
                self.V[x] = (self.V[y] - self.V[x]) & 0xFF
                self.V[0xF] = test
            case co if (co & 0xF00F) == 0x800E:
                test = (self.V[x] & 0x80) >> 7
                self.V[x] = (self.V[y] << 1) & 0xFF
                self.V[0xF] = test
            case co if (co & 0xF000) == 0x9000:
                if self.V[x] != self.V[y]:
                    self.program_counter += 2
            case co if (co & 0xF000) == 0xA000:
                self.I = addr
            case co if (co & 0xF000) == 0xB000:
                self.program_counter = addr + self.V[0]
            case co if (co & 0xF000) == 0xC000:
                self.V[x] = random.randint(0, 255) & kk
            case co if (co & 0xF000) == 0xD000:
                self.V[0xF] = 0
                for row in range(nibble):
                    sprite_byte = self.memory.ram[self.I + row]
                    for col in range(8):
                        if (sprite_byte & (0x80 >> col)) != 0:
                            if self.display.draw_pixel(self.V[x] + col, self.V[y] + row):
                                self.V[0xF] = 1
            case co if (co & 0xF0FF) == 0xE09E:
                if self.keyboard[self.V[x]]:
                    self.program_counter += 2
            case co if (co & 0xF0FF) == 0xE0A1:
                if not self.keyboard[self.V[x]]:
                    self.program_counter += 2
            case co if (co & 0xF00F) == 0xF007:
                self.V[x] = self.delay_timer
            case co if (co & 0xF00F) == 0xF00A:
                key_pressed = False
                for i in range(16):
                    if self.keyboard[i]:
                        self.V[x] = i
                        key_pressed = True
                        break
                if not key_pressed:
                    self.program_counter -= 2
            case co if (co & 0xF0FF) == 0xF015:
                self.delay_timer = self.V[x]
            case co if (co & 0xF0FF) == 0xF018:
                self.sound_timer = self.V[x]
            case co if (co & 0xF0FF) == 0xF01E:
                self.I += self.V[x]
            case co if (co & 0xF0FF) == 0xF029:
                self.I = self.V[x] * 5 # 5 is the number of hex stored for sprite
            case co if (co & 0xF0FF) == 0xF033:
                self.memory.ram[self.I] = self.V[x] // 100
                self.memory.ram[self.I+1] = (self.V[x] // 10) % 10
                self.memory.ram[self.I+2] = self.V[x] % 10
            case co if (co & 0xF0FF) == 0xF055:
                for i in range(x + 1):
                    self.memory.ram[self.I + i] = self.V[i]
                self.I += x + 1 # quirk of chip8
            case co if (co & 0xF0FF) == 0xF065:
                for i in range(x+1):
                    self.V[i] = self.memory.ram[self.I + i]
                self.I += x + 1 # quirk of chip8
            case _:
                self.logger.info(f"Unknown command: {opcode:04X}")
            

    def log_state(self):
        self.logger.info(f"PC = {self.program_counter}")
        self.logger.info(f"Vx registers = {self.V}")
        self.logger.info(f"Stack = {self.stack}")

    def update_timers(self):
        """Updates the delay and sound timers."""
        if self.delay_timer > 0:
            self.delay_timer -= 1
        if self.sound_timer > 0:
            self.sound_timer -= 1
            if self.sound_timer == 0:
                # TODO: Implement sound
                print("BEEP!")

    