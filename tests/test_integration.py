import pytest
from src.cpu import CPU
from src.memory import Memory
from src.display import Display

def test_bcd_conversion():
    """Test BCD conversion and memory storage."""
    memory = Memory()
    display = Display()
    cpu = CPU(memory, display)

    # Load a value into V0
    cpu.V[0] = 123 # 123 in decimal
    # Set I register to a memory location
    cpu.I = 0x300
    # Execute BCD conversion opcode
    # Fx33: LD B, Vx
    cpu._execute(0xF033)

    # Check memory
    assert memory.ram[0x300] == 1
    assert memory.ram[0x301] == 2
    assert memory.ram[0x302] == 3

def test_store_and_load_registers():
    """Test storing and loading registers to/from memory."""
    memory = Memory()
    display = Display()
    cpu = CPU(memory, display)

    # Load values into registers V0-V3
    for i in range(4):
        cpu.V[i] = i * 10

    # Set I register
    cpu.I = 0x400

    # Store V0-V3 into memory
    # Fx55: LD [I], Vx
    cpu._execute(0xF355)

    # Verify memory contents
    for i in range(4):
        assert memory.ram[0x400 + i] == i * 10

    # Clear registers
    for i in range(16):
        cpu.V[i] = 0

    # Load V0-V3 from memory
    # Fx65: LD Vx, [I]
    cpu._execute(0xF365)

    # Verify register contents
    for i in range(4):
        assert cpu.V[i] == i * 10
