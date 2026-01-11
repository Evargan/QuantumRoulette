# Quantum Buckshot Roulette

A strategic two-player quantum game that combines classic Buckshot Roulette mechanics with quantum computing concepts.

## 🎮 Game Overview

Two players sit opposite each other at a table with a shotgun loaded with a mix of live and blank rounds. The bullets are **quantum bits (qubits)** that can exist in superposition until measured (fired)!

Players can manipulate the quantum states of bullets using **quantum gates** before shooting, adding strategic depth to the classic game.

## 🔧 Requirements

- Python 3.8 or higher
- tkinter (usually comes with Python)
- qiskit >= 1.0
- qiskit-aer
- numpy

## 📦 Installation

```bash
pip install qiskit qiskit-aer numpy
```

## 🚀 Running the Game

```bash
cd quantum_buckshot_roulette
python main.py
```

Or in VS Code: Open `main.py` and press `F5`.

## 📖 Game Rules

### Setup
- Each player starts with configurable lives (1-5)
- The game loads 4-10 bullets (configurable)
- At least 30% of bullets are live (random)

### Round Flow
1. **Gate Selection**: Each player selects their quantum gates (can pick same gate multiple times)
2. **Bullet Reveal**: Initial configuration shown for 3 seconds
3. **Playing Phase**: Players take turns
4. **New Round**: When all bullets are fired

### Turn Actions
1. **Apply Gate** (optional): Apply ONE gate per turn
2. **Shoot** (required): Always shoots the next bullet in queue
   - **Shoot Self**: If blank → extra turn! If live → lose 1 life
   - **Shoot Opponent**: If blank → turn ends. If live → opponent loses 1 life
3. **Peek** (once per round): See opponent's remaining unused gates

### Visibility Rules
- Each player only sees changes they made to bullets
- Fired bullets are visible to everyone
- Initial configuration must be memorized!

### Winning
Eliminate your opponent by reducing their lives to 0!

## ⚛️ Quantum Gates

### Single-Qubit Gates
| Gate | Effect |
|------|--------|
| **X** | Flips state: \|0⟩↔\|1⟩ |
| **Y** | Flips with phase rotation |
| **Z** | Phase flip (affects superposition) |
| **H** | Creates 50/50 superposition |
| **Rx(π/2)** | Partial X rotation |
| **Ry(π/2)** | Partial Y rotation |
| **Rz(π/2)** | Phase rotation |

### Two-Qubit Gates
| Gate | Effect |
|------|--------|
| **CNOT** | Flips target if control is \|1⟩, creates entanglement |

## 🎨 Bullet Colors

| Color | Meaning |
|-------|---------|
| 🔴 Red | Live round |
| ⚪ Green | Blank round |
| 🟡 Yellow | Superposition (uncertain) |
| 🟣 Purple | Entangled |
| Gray | Fired |

## 🎯 Strategy Tips

1. **The Flip**: Use X gate to flip a known bullet state
2. **The Uncertainty**: Apply H to create 50/50 uncertainty
3. **Safe Self-Shot**: If you know the next bullet is blank, shoot yourself for an extra turn
4. **Entanglement Trap**: Use CNOT to link two bullets' fates

## 📁 File Structure

```
quantum_buckshot_roulette/
├── main.py           # Entry point, main menu
├── game_logic.py     # Quantum mechanics and game rules
├── ui_components.py  # tkinter UI elements
├── animations.py     # Visual animations
└── requirements.txt  # Python dependencies
```

## 📝 License

Educational project for quantum computing concepts in game format.

---

*"In quantum mechanics, observation changes reality. In Quantum Buckshot Roulette, your choice of gate changes your fate!"*
