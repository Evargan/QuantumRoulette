"""
Game Logic and Quantum Mechanics for Quantum Buckshot Roulette

This module contains:
- QuantumBulletSystem: Manages quantum states of bullets using Qiskit
- Player: Represents a player with lives, gates, and actions
- QuantumBuckshotGame: Main game logic controller

"""

from enum import Enum
from dataclasses import dataclass, field
from typing import List, Dict, Tuple, Optional, Callable
import random
import numpy as np
from qiskit import QuantumCircuit, QuantumRegister, ClassicalRegister
from qiskit_aer import AerSimulator
from qiskit.quantum_info import Statevector


class GateType(Enum):
    """Available quantum gates in the game"""
    # Single-qubit gates
    X = "X"
    Y = "Y"
    Z = "Z"
    H = "H"
    RX = "Rx(π/2)"
    RY = "Ry(π/2)"
    RZ = "Rz(π/2)"
    
    # Two-qubit gates
    CNOT = "CNOT"
    
    def is_two_qubit(self) -> bool:
        return self == GateType.CNOT


@dataclass
class Gate:
    """Represents a quantum gate that a player can use"""
    gate_type: GateType
    used: bool = False
    
    def __str__(self):
        status = "✗" if self.used else "✓"
        return f"{self.gate_type.value}[{status}]"
    
    def get_display_name(self) -> str:
        return self.gate_type.value


@dataclass
class Player:
    """Represents a player in the game"""
    name: str
    player_id: int  # 1 or 2
    lives: int = 3
    gates: List[Gate] = field(default_factory=list)
    peek_available: bool = True
    # Track gates applied by this player (for visibility)
    applied_gates_history: List[Tuple[GateType, int, int]] = field(default_factory=list)
    
    def is_alive(self) -> bool:
        return self.lives > 0
    
    def take_damage(self) -> bool:
        self.lives = max(0, self.lives - 1)
        return self.is_alive()
    
    def get_available_gates(self) -> List[Gate]:
        return [g for g in self.gates if not g.used]
    
    def has_gate(self, gate_type: GateType) -> bool:
        return any(g.gate_type == gate_type and not g.used for g in self.gates)
    
    def use_gate(self, gate_type: GateType) -> bool:
        for gate in self.gates:
            if gate.gate_type == gate_type and not gate.used:
                gate.used = True
                return True
        return False
    
    def reset_for_new_round(self):
        self.gates = []
        self.peek_available = True
        self.applied_gates_history = []
    
    def set_gates(self, gate_types: List[GateType]):
        self.gates = [Gate(gt) for gt in gate_types]
    
    def record_gate_application(self, gate_type: GateType, target1: int, target2: int = -1):
        self.applied_gates_history.append((gate_type, target1, target2))


class QuantumBulletSystem:
    """
    Manages the quantum state of bullets using Qiskit.
    """
    
    def __init__(self, num_bullets: int):
        self.num_bullets = num_bullets
        self.qr = QuantumRegister(num_bullets, 'bullet')
        self.cr = ClassicalRegister(num_bullets, 'measure')
        self.circuit = QuantumCircuit(self.qr, self.cr)
        self.simulator = AerSimulator()
        
        # Track entanglements: maps qubit -> its entangled partner
        self.entanglements: Dict[int, int] = {}
        
        # Track which bullets have been measured (fired)
        self.measured: List[bool] = [False] * num_bullets
        self.measurement_results: List[Optional[int]] = [None] * num_bullets
        
        # Store initial configuration for display
        self.initial_live_positions: List[int] = []
        
        # Current bullet index (queue position)
        self.current_bullet_index: int = 0
    
    def initialize_bullets(self, live_positions: List[int]):
        self.circuit = QuantumCircuit(self.qr, self.cr)
        self.entanglements = {}
        self.measured = [False] * self.num_bullets
        self.measurement_results = [None] * self.num_bullets
        self.initial_live_positions = sorted(live_positions)
        self.current_bullet_index = 0
        self._collapsed_states = {} 
        
        for pos in live_positions:
            if 0 <= pos < self.num_bullets:
                self.circuit.x(self.qr[pos])
    
    def _break_entanglement(self, qubit: int):
        if qubit in self.entanglements:
            partner = self.entanglements[qubit]
            del self.entanglements[qubit]
            if partner in self.entanglements:
                del self.entanglements[partner]
    
    def apply_gate(self, gate_type: GateType, target1: int, target2: int = -1) -> bool:
        if target1 < 0 or target1 >= self.num_bullets:
            return False
        if self.measured[target1]:
            return False
        
        if gate_type.is_two_qubit():
            if target2 < 0 or target2 >= self.num_bullets:
                return False
            if self.measured[target2]:
                return False
            if target1 == target2:
                return False
        
        try:
            if gate_type == GateType.X:
                self.circuit.x(self.qr[target1])
            elif gate_type == GateType.Y:
                self.circuit.y(self.qr[target1])
            elif gate_type == GateType.Z:
                self.circuit.z(self.qr[target1])
            elif gate_type == GateType.H:
                self.circuit.h(self.qr[target1])
            elif gate_type == GateType.RX:
                self.circuit.rx(np.pi/2, self.qr[target1])
            elif gate_type == GateType.RY:
                self.circuit.ry(np.pi/2, self.qr[target1])
            elif gate_type == GateType.RZ:
                self.circuit.rz(np.pi/2, self.qr[target1])
            elif gate_type == GateType.CNOT:
                self._break_entanglement(target2)
                self.circuit.cx(self.qr[target1], self.qr[target2])
                self.entanglements[target1] = target2
                self.entanglements[target2] = target1
            else:
                return False
            return True
        except Exception as e:
            print(f"Error applying gate: {e}")
            return False
    
    def get_current_bullet(self) -> int:
        return self.current_bullet_index
    
    def measure_bullet(self, qubit: int) -> int:
        if self.measured[qubit]:
            return self.measurement_results[qubit]
        
        if hasattr(self, '_collapsed_states') and qubit in self._collapsed_states:
            result_value = self._collapsed_states[qubit]
            self.measured[qubit] = True
            self.measurement_results[qubit] = result_value
            del self._collapsed_states[qubit]
            
            # Move to next bullet
            self.current_bullet_index += 1
            while self.current_bullet_index < self.num_bullets and self.measured[self.current_bullet_index]:
                self.current_bullet_index += 1
            return result_value
        
        had_entanglement = qubit in self.entanglements
        partner = self.entanglements.get(qubit, -1)
        
        measure_circuit = self.circuit.copy()
        measure_circuit.measure(self.qr[qubit], self.cr[qubit])
        
        job = self.simulator.run(measure_circuit, shots=1)
        result = job.result()
        counts = result.get_counts()
        
        measured_string = list(counts.keys())[0]
        result_value = int(measured_string[-(qubit+1)])
        
        self.measured[qubit] = True
        self.measurement_results[qubit] = result_value
        self.circuit.measure(self.qr[qubit], self.cr[qubit])
        
        # Handle entanglement collapse - partner collapses to correlated state
        if had_entanglement and partner >= 0 and not self.measured[partner]:
            if not hasattr(self, '_collapsed_states'):
                self._collapsed_states = {}

            self._collapsed_states[partner] = result_value
            
            # Remove entanglement tracking
            self._break_entanglement(qubit)
        
        self.current_bullet_index += 1
        while self.current_bullet_index < self.num_bullets and self.measured[self.current_bullet_index]:
            self.current_bullet_index += 1
        
        return result_value
    
    def fire_next_bullet(self) -> Tuple[int, int]:
        bullet_idx = self.current_bullet_index
        if bullet_idx >= self.num_bullets:
            return -1, -1
        result = self.measure_bullet(bullet_idx)
        return bullet_idx, result
    
    def get_probabilities(self) -> List[Tuple[float, float]]:
        probabilities = []
        try:
            sv_circuit = self.circuit.copy()
            sv_circuit.remove_final_measurements()
            sv_circuit.save_statevector()
            
            job = self.simulator.run(sv_circuit)
            result = job.result()
            statevector = result.get_statevector()
            
            for qubit in range(self.num_bullets):
                if self.measured[qubit]:
                    if self.measurement_results[qubit] == 0:
                        probabilities.append((1.0, 0.0))
                    else:
                        probabilities.append((0.0, 1.0))
                elif hasattr(self, '_collapsed_states') and qubit in self._collapsed_states:
                    if self._collapsed_states[qubit] == 0:
                        probabilities.append((1.0, 0.0))
                    else:
                        probabilities.append((0.0, 1.0))
                else:
                    p_zero = 0.0
                    p_one = 0.0
                    for i, amplitude in enumerate(statevector):
                        bit_value = (i >> qubit) & 1
                        prob = abs(amplitude) ** 2
                        if bit_value == 0:
                            p_zero += prob
                        else:
                            p_one += prob
                    probabilities.append((p_zero, p_one))
        except Exception as e:
            print(f"Error getting probabilities: {e}")
            for qubit in range(self.num_bullets):
                if self.measured[qubit]:
                    if self.measurement_results[qubit] == 0:
                        probabilities.append((1.0, 0.0))
                    else:
                        probabilities.append((0.0, 1.0))
                elif hasattr(self, '_collapsed_states') and qubit in self._collapsed_states:
                    if self._collapsed_states[qubit] == 0:
                        probabilities.append((1.0, 0.0))
                    else:
                        probabilities.append((0.0, 1.0))
                else:
                    probabilities.append((0.5, 0.5))
        return probabilities
    
    def get_bullet_state_category(self, qubit: int) -> str:
        if self.measured[qubit]:
            if self.measurement_results[qubit] == 1:
                return 'fired_live'
            else:
                return 'fired_blank'
        
        if hasattr(self, '_collapsed_states') and qubit in self._collapsed_states:
            if self._collapsed_states[qubit] == 1:
                return 'live'
            else:
                return 'blank'
        
        probs = self.get_probabilities()
        p_blank, p_live = probs[qubit]
        is_entangled = qubit in self.entanglements
        
        if p_live > 0.99:
            return 'entangled' if is_entangled else 'live'
        elif p_live < 0.01:
            return 'entangled' if is_entangled else 'blank'
        else:
            return 'entangled' if is_entangled else 'superposition'
    
    def get_unmeasured_bullets(self) -> List[int]:
        return [i for i in range(self.num_bullets) if not self.measured[i]]
    
    def all_measured(self) -> bool:
        return all(self.measured)


class QuantumBuckshotGame:
    
    def __init__(self, num_bullets: int = 6, num_gates: int = 3, num_lives: int = 3):
        self.num_bullets = num_bullets
        self.num_gates = num_gates
        self.initial_lives = num_lives
        
        self.player1 = Player("Player 1", 1, num_lives)
        self.player2 = Player("Player 2", 2, num_lives)
        self.current_player = self.player1
        
        self.bullet_system: Optional[QuantumBulletSystem] = None
        self.round_number = 0
        self.game_over = False
        self.winner: Optional[Player] = None
        
        self.phase = "gate_selection"
        self.gate_selection_player = 1
        self.gate_applied_this_turn = False
        
        self.all_gate_types = [
            GateType.X, GateType.Y, GateType.Z, GateType.H,
            GateType.RX, GateType.RY, GateType.RZ, GateType.CNOT
        ]
        
        self.on_state_change: Optional[Callable] = None
        self.on_shot_result: Optional[Callable] = None
        self.on_round_end: Optional[Callable] = None
        self.on_game_end: Optional[Callable] = None
    
    def get_opponent(self, player: Player) -> Player:
        return self.player2 if player == self.player1 else self.player1
    
    def start_new_round(self):
        self.round_number += 1
        self.phase = "gate_selection"
        self.gate_selection_player = 1
        self.gate_applied_this_turn = False
        
        self.player1.reset_for_new_round()
        self.player2.reset_for_new_round()
        
        min_live = max(1, int(self.num_bullets * 0.3))
        max_live = self.num_bullets - 1
        num_live = random.randint(min_live, max_live)
        
        all_positions = list(range(self.num_bullets))
        live_positions = random.sample(all_positions, num_live)
        
        self.bullet_system = QuantumBulletSystem(self.num_bullets)
        self.bullet_system.initialize_bullets(live_positions)
        
        if self.on_state_change:
            self.on_state_change()
    
    def get_available_gate_types(self) -> List[GateType]:
        return self.all_gate_types.copy()
    
    def submit_gate_selection(self, player_id: int, selected_gates: List[GateType]) -> bool:
        if len(selected_gates) != self.num_gates:
            return False
        
        player = self.player1 if player_id == 1 else self.player2
        player.set_gates(selected_gates)
        
        if player_id == 1:
            self.gate_selection_player = 2
        else:
            self.phase = "show_bullets"
        
        if self.on_state_change:
            self.on_state_change()
        return True
    
    def start_playing_phase(self):
        self.phase = "playing"
        self.gate_applied_this_turn = False
        self.current_player = self.player1
        if self.on_state_change:
            self.on_state_change()
    
    def apply_gate(self, gate_type: GateType, target1: int, target2: int = -1) -> Tuple[bool, str]:
        if self.phase != "playing":
            return False, "Cannot apply gates outside playing phase"
        if self.game_over:
            return False, "Game is over"
        if self.gate_applied_this_turn:
            return False, "You can only apply one gate per turn"
        
        player = self.current_player
        if not player.has_gate(gate_type):
            return False, f"You don't have {gate_type.value} available"
        
        if self.bullet_system.apply_gate(gate_type, target1, target2):
            player.use_gate(gate_type)
            player.record_gate_application(gate_type, target1, target2)
            self.gate_applied_this_turn = True
            
            if gate_type.is_two_qubit():
                msg = f"Applied {gate_type.value} to bullets {target1} and {target2}"
            else:
                msg = f"Applied {gate_type.value} to bullet {target1}"
            
            if self.on_state_change:
                self.on_state_change()
            return True, msg
        else:
            return False, "Failed to apply gate (invalid target?)"
    
    def shoot(self, shoot_self: bool) -> Dict:
        if self.phase != "playing":
            return {"success": False, "message": "Cannot shoot outside playing phase"}
        if self.game_over:
            return {"success": False, "message": "Game is over"}
        
        shooter = self.current_player
        target = shooter if shoot_self else self.get_opponent(shooter)
        
        bullet_idx, result = self.bullet_system.fire_next_bullet()
        if bullet_idx < 0:
            return {"success": False, "message": "No more bullets to fire"}
        
        is_live = result == 1
        
        result_info = {
            "success": True,
            "shooter": shooter.name,
            "shooter_id": shooter.player_id,
            "target": target.name,
            "target_id": target.player_id,
            "bullet_index": bullet_idx,
            "is_live": is_live,
            "shot_self": shoot_self,
            "extra_turn": False,
            "damage_dealt": False,
            "target_lives_remaining": target.lives,
            "round_over": False,
            "game_over": False,
            "winner": None
        }
        
        if is_live:
            still_alive = target.take_damage()
            result_info["damage_dealt"] = True
            result_info["target_lives_remaining"] = target.lives
            
            if not still_alive:
                self.game_over = True
                self.winner = self.get_opponent(target)
                result_info["game_over"] = True
                result_info["winner"] = self.winner.name
                if self.on_game_end:
                    self.on_game_end(self.winner)
            else:
                self.current_player = self.get_opponent(shooter)
                self.gate_applied_this_turn = False
        else:
            if shoot_self:
                result_info["extra_turn"] = True
                self.gate_applied_this_turn = False
            else:
                self.current_player = self.get_opponent(shooter)
                self.gate_applied_this_turn = False
        
        if self.bullet_system.all_measured() and not self.game_over:
            result_info["round_over"] = True
            if self.on_round_end:
                self.on_round_end()
        
        if self.on_shot_result:
            self.on_shot_result(result_info)
        if self.on_state_change:
            self.on_state_change()
        
        return result_info
    
    def use_peek(self) -> Tuple[bool, List[Gate]]:
        if self.phase != "playing":
            return False, []
        
        player = self.current_player
        opponent = self.get_opponent(player)
        
        if not player.peek_available:
            return False, []
        
        player.peek_available = False
        available_gates = opponent.get_available_gates()
        
        if self.on_state_change:
            self.on_state_change()
        return True, available_gates
    
    def get_visible_bullet_states(self, for_player_id: int) -> List[str]:
        if not self.bullet_system:
            return []
        
        player = self.player1 if for_player_id == 1 else self.player2
        states = []
        
        for i in range(self.num_bullets):
            if self.bullet_system.measured[i]:
                if self.bullet_system.measurement_results[i] == 1:
                    states.append('fired_live')
                else:
                    states.append('fired_blank')
            else:
                player_modified = any(
                    t1 == i or t2 == i 
                    for _, t1, t2 in player.applied_gates_history
                )
                
                if player_modified:
                    states.append(self.bullet_system.get_bullet_state_category(i))
                else:
                    if i in self.bullet_system.initial_live_positions:
                        states.append('live')
                    else:
                        states.append('blank')
        return states
    
    def get_game_state(self) -> Dict:
        probabilities = []
        if self.bullet_system:
            probabilities = self.bullet_system.get_probabilities()
        
        return {
            "phase": self.phase,
            "round": self.round_number,
            "gate_selection_player": self.gate_selection_player,
            "current_player": self.current_player.player_id if self.current_player else None,
            "gate_applied_this_turn": self.gate_applied_this_turn,
            "player1": {
                "name": self.player1.name,
                "lives": self.player1.lives,
                "gates": [{"type": g.gate_type.value, "used": g.used} for g in self.player1.gates],
                "peek_available": self.player1.peek_available
            },
            "player2": {
                "name": self.player2.name,
                "lives": self.player2.lives,
                "gates": [{"type": g.gate_type.value, "used": g.used} for g in self.player2.gates],
                "peek_available": self.player2.peek_available
            },
            "bullets": {
                "total": self.num_bullets,
                "initial_live": self.bullet_system.initial_live_positions if self.bullet_system else [],
                "measured": self.bullet_system.measured if self.bullet_system else [],
                "results": self.bullet_system.measurement_results if self.bullet_system else [],
                "probabilities": probabilities,
                "entanglements": dict(self.bullet_system.entanglements) if self.bullet_system else {},
                "current_bullet": self.bullet_system.current_bullet_index if self.bullet_system else 0
            },
            "game_over": self.game_over,
            "winner": self.winner.name if self.winner else None
        }
    
    def get_initial_bullet_config(self) -> Tuple[int, List[int]]:
        if self.bullet_system:
            return self.num_bullets, self.bullet_system.initial_live_positions
        return self.num_bullets, []
