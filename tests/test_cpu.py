
import pytest
from src.cpu import CPU
from src.memory import Memory
from src.display import Display

@pytest.fixture
def cpu():
    """Fixture to create a CPU instance for testing."""
    memory = Memory()
    display = Display()
    return CPU(memory, display)

def test_initial_state(cpu):
    """Test the initial state of the CPU."""
    assert cpu.program_counter == 0x200
    assert all(v == 0 for v in cpu.V)
    assert cpu.I == 0
    assert not cpu.stack
    assert cpu.delay_timer == 0
    assert cpu.sound_timer == 0

def test_6xkk_ld_vx_byte(cpu):
    """Test 6xkk opcode: LD Vx, byte."""
    opcode = 0x61FF  # LD V1, 0xFF
    cpu._execute(opcode)
    assert cpu.V[1] == 0xFF

def test_7xkk_add_vx_byte(cpu):
    """Test 7xkk opcode: ADD Vx, byte."""
    cpu.V[2] = 0x10
    opcode = 0x7205  # ADD V2, 0x05
    cpu._execute(opcode)
    assert cpu.V[2] == 0x15

def test_annn_ld_i_addr(cpu):
    """Test Annn opcode: LD I, addr."""
    opcode = 0xA123 # LD I, 0x123
    cpu._execute(opcode)
    assert cpu.I == 0x123

def test_jump_and_call(cpu):
    """Test jump and call opcodes."""
    # 2nnn: CALL addr
    cpu._execute(0x2ABC)
    assert cpu.program_counter == 0xABC
    assert cpu.stack == [0x200] # Initial PC was 0x200, it executed opcode at 0x200, pc became 0x202, then stack pushed 0x202. Wait, fetch increments pc.
    cpu.program_counter = 0x200 # Reset PC for next test
    cpu.stack = []

    # Test CALL
    initial_pc = cpu.program_counter
    cpu._execute(0x2ABC)
    assert cpu.program_counter == 0xABC
    assert cpu.stack.pop() == initial_pc

    # Test RET
    cpu.stack = [0x200]
    cpu._execute(0x00EE)
    assert cpu.program_counter == initial_pc

    # Test JP
    cpu._execute(0x1DEF)
    assert cpu.program_counter == 0xDEF

def test_8xy1_or_vx_vy(cpu):
    """Test 8xy1 opcode: OR Vx, Vy."""
    cpu.V[1] = 0xAA  # 10101010
    cpu.V[2] = 0x55  # 01010101
    opcode = 0x8121   # OR V1, V2
    cpu._execute(opcode)
    assert cpu.V[1] == 0xFF  # 11111111