"""
UI Components for Quantum Buckshot Roulette
"""

import tkinter as tk
from tkinter import ttk, messagebox
from typing import List, Dict, Optional, Callable
from game_logic import QuantumBuckshotGame, GateType, Player, Gate
from animations import AnimationManager


class GameUI:
    """Main game UI controller"""
    
    COLORS = {
        'bg_dark': '#1a1a2e',
        'bg_medium': '#16213e',
        'bg_light': '#0f3460',
        'accent': '#e94560',
        'accent_light': '#ff6b6b',
        'text_light': '#ffffff',
        'text_dim': '#a0a0a0',
        'player1': '#4fc3f7',
        'player2': '#f06292',
        'live': '#ff5252',
        'blank': '#4caf50',
        'superposition': '#ffc107',
        'entangled': '#9c27b0',
        'fired': '#757575',
        'fired_live': '#b71c1c',
        'fired_blank': '#424242',
        'current_bullet': '#00e5ff'
    }
    
    def __init__(self, root: tk.Toplevel, game: QuantumBuckshotGame, on_exit: Callable):
        self.root = root
        self.game = game
        self.on_exit = on_exit
        
        self.root.title("Quantum Buckshot Roulette")
        self.root.geometry("1200x800")
        self.root.configure(bg=self.COLORS['bg_dark'])
        self.root.protocol("WM_DELETE_WINDOW", self.exit_game)
        
        self.center_window()
        self.animation = AnimationManager(self.root, self.COLORS)
        
        self.selected_gates: List[GateType] = []
        self.selected_gate_for_apply: Optional[GateType] = None
        self.gate_target1: Optional[int] = None
        self.gate_target2: Optional[int] = None
        
        self.game.on_state_change = self.on_game_state_change
        self.game.on_shot_result = self.on_shot_result
        self.game.on_round_end = self.on_round_end
        self.game.on_game_end = self.on_game_end
        
        self.main_frame = tk.Frame(self.root, bg=self.COLORS['bg_dark'])
        self.main_frame.pack(fill='both', expand=True)
        self.current_phase_frame: Optional[tk.Frame] = None
    
    def center_window(self):
        self.root.update_idletasks()
        width, height = 1200, 800
        x = (self.root.winfo_screenwidth() // 2) - (width // 2)
        y = (self.root.winfo_screenheight() // 2) - (height // 2)
        self.root.geometry(f'{width}x{height}+{x}+{y}')
    
    def start(self):
        self.game.start_new_round()
    
    def clear_main_frame(self):
        if self.current_phase_frame:
            self.current_phase_frame.destroy()
        for widget in self.main_frame.winfo_children():
            widget.destroy()
    
    def on_game_state_change(self):
        state = self.game.get_game_state()
        if state['phase'] == 'gate_selection':
            self.show_gate_selection_ui()
        elif state['phase'] == 'show_bullets':
            self.show_bullet_reveal_ui()
        elif state['phase'] == 'playing':
            self.show_playing_ui()
    
    def on_shot_result(self, result: Dict):
        pass
    
    def on_round_end(self):
        self.show_round_end_ui()
    
    def on_game_end(self, winner: Player):
        self.show_game_end_ui(winner)
    
    def show_gate_selection_ui(self):
        self.clear_main_frame()
        
        state = self.game.get_game_state()
        player_num = state['gate_selection_player']
        
        self.current_phase_frame = tk.Frame(self.main_frame, bg=self.COLORS['bg_dark'])
        self.current_phase_frame.pack(fill='both', expand=True, padx=50, pady=30)
        
        title_color = self.COLORS['player1'] if player_num == 1 else self.COLORS['player2']
        title = tk.Label(self.current_phase_frame,
            text=f"🎮 PLAYER {player_num} - SELECT YOUR GATES 🎮",
            font=('Arial', 24, 'bold'), fg=title_color, bg=self.COLORS['bg_dark'])
        title.pack(pady=20)
        
        instructions = tk.Label(self.current_phase_frame,
            text=f"Select {self.game.num_gates} gates. You can select the same gate multiple times.",
            font=('Arial', 12), fg=self.COLORS['text_dim'], bg=self.COLORS['bg_dark'])
        instructions.pack(pady=10)
        
        round_info = tk.Label(self.current_phase_frame, text=f"Round {state['round']}",
            font=('Arial', 14, 'bold'), fg=self.COLORS['accent'], bg=self.COLORS['bg_dark'])
        round_info.pack(pady=5)
        
        gates_frame = tk.Frame(self.current_phase_frame, bg=self.COLORS['bg_medium'], padx=20, pady=20)
        gates_frame.pack(pady=20, fill='x')
        
        single_label = tk.Label(gates_frame, text="Single-Qubit Gates:",
            font=('Arial', 12, 'bold'), fg=self.COLORS['text_light'], bg=self.COLORS['bg_medium'])
        single_label.pack(anchor='w', pady=(0, 10))
        
        single_frame = tk.Frame(gates_frame, bg=self.COLORS['bg_medium'])
        single_frame.pack(fill='x', pady=5)
        
        self.selected_gates = []
        
        single_gates = [gt for gt in GateType if not gt.is_two_qubit()]
        for gate_type in single_gates:
            btn = tk.Button(single_frame, text=gate_type.value,
                font=('Arial', 12, 'bold'), width=10, height=2,
                bg=self.COLORS['bg_light'], fg=self.COLORS['text_light'],
                activebackground=self.COLORS['accent'], relief='flat', cursor='hand2',
                command=lambda gt=gate_type: self.add_gate_to_selection(gt))
            btn.pack(side='left', padx=5, pady=5)
        
        two_label = tk.Label(gates_frame, text="Two-Qubit Gates:",
            font=('Arial', 12, 'bold'), fg=self.COLORS['text_light'], bg=self.COLORS['bg_medium'])
        two_label.pack(anchor='w', pady=(20, 10))
        
        two_frame = tk.Frame(gates_frame, bg=self.COLORS['bg_medium'])
        two_frame.pack(fill='x', pady=5)
        
        two_gates = [gt for gt in GateType if gt.is_two_qubit()]
        for gate_type in two_gates:
            btn = tk.Button(two_frame, text=gate_type.value,
                font=('Arial', 12, 'bold'), width=10, height=2,
                bg=self.COLORS['bg_light'], fg=self.COLORS['text_light'],
                activebackground=self.COLORS['accent'], relief='flat', cursor='hand2',
                command=lambda gt=gate_type: self.add_gate_to_selection(gt))
            btn.pack(side='left', padx=5, pady=5)
        
        selected_frame = tk.Frame(self.current_phase_frame, bg=self.COLORS['bg_dark'])
        selected_frame.pack(pady=15)
        
        tk.Label(selected_frame, text="Selected Gates:", font=('Arial', 12),
            fg=self.COLORS['text_light'], bg=self.COLORS['bg_dark']).pack(side='left', padx=5)
        
        self.selected_display = tk.Label(selected_frame, text="(none)",
            font=('Arial', 12, 'bold'), fg=self.COLORS['accent'], bg=self.COLORS['bg_dark'])
        self.selected_display.pack(side='left', padx=5)
        
        self.selection_label = tk.Label(self.current_phase_frame,
            text=f"Selected: 0 / {self.game.num_gates}",
            font=('Arial', 14), fg=self.COLORS['text_light'], bg=self.COLORS['bg_dark'])
        self.selection_label.pack(pady=5)
        
        btn_frame = tk.Frame(self.current_phase_frame, bg=self.COLORS['bg_dark'])
        btn_frame.pack(pady=10)
        
        self.clear_btn = tk.Button(btn_frame, text="✗ Clear Selection",
            font=('Arial', 12), bg=self.COLORS['bg_light'], fg=self.COLORS['text_light'],
            width=15, relief='flat', cursor='hand2', command=self.clear_gate_selection)
        self.clear_btn.pack(side='left', padx=10)
        
        self.confirm_btn = tk.Button(btn_frame, text="✓ CONFIRM",
            font=('Arial', 14, 'bold'), bg=self.COLORS['accent'], fg=self.COLORS['text_light'],
            width=15, height=2, relief='flat', cursor='hand2', state='disabled',
            command=self.confirm_gate_selection)
        self.confirm_btn.pack(side='left', padx=10)
    
    def add_gate_to_selection(self, gate_type: GateType):
        if len(self.selected_gates) < self.game.num_gates:
            self.selected_gates.append(gate_type)
            self.update_selection_display()
    
    def clear_gate_selection(self):
        self.selected_gates = []
        self.update_selection_display()
    
    def update_selection_display(self):
        if self.selected_gates:
            display_text = ", ".join([g.value for g in self.selected_gates])
        else:
            display_text = "(none)"
        
        self.selected_display.configure(text=display_text)
        self.selection_label.configure(text=f"Selected: {len(self.selected_gates)} / {self.game.num_gates}")
        
        if len(self.selected_gates) == self.game.num_gates:
            self.confirm_btn.configure(state='normal')
        else:
            self.confirm_btn.configure(state='disabled')
    
    def confirm_gate_selection(self):
        state = self.game.get_game_state()
        player_num = state['gate_selection_player']
        self.game.submit_gate_selection(player_num, self.selected_gates.copy())
        
        if player_num == 1:
            self.show_player_switch_screen(2, "select gates")
    
    def show_player_switch_screen(self, next_player: int, action: str):
        self.clear_main_frame()
        
        self.current_phase_frame = tk.Frame(self.main_frame, bg=self.COLORS['bg_dark'])
        self.current_phase_frame.pack(fill='both', expand=True)
        
        color = self.COLORS['player1'] if next_player == 1 else self.COLORS['player2']
        
        msg = tk.Label(self.current_phase_frame, text=f"🔄 SWITCH TO PLAYER {next_player} 🔄",
            font=('Arial', 32, 'bold'), fg=color, bg=self.COLORS['bg_dark'])
        msg.pack(expand=True)
        
        action_label = tk.Label(self.current_phase_frame, text=f"Get ready to {action}!",
            font=('Arial', 18), fg=self.COLORS['text_light'], bg=self.COLORS['bg_dark'])
        action_label.pack()
        
        self.countdown_label = tk.Label(self.current_phase_frame, text="5",
            font=('Arial', 72, 'bold'), fg=self.COLORS['accent'], bg=self.COLORS['bg_dark'])
        self.countdown_label.pack(pady=30)
        
        self.do_countdown(5, lambda: self.on_game_state_change())
    
    def do_countdown(self, seconds: int, callback: Callable):
        if seconds > 0:
            self.countdown_label.configure(text=str(seconds))
            self.root.after(1000, lambda: self.do_countdown(seconds - 1, callback))
        else:
            callback()
    
    def show_bullet_reveal_ui(self):
        self.clear_main_frame()
        
        state = self.game.get_game_state()
        total, live_positions = self.game.get_initial_bullet_config()
        
        self.current_phase_frame = tk.Frame(self.main_frame, bg=self.COLORS['bg_dark'])
        self.current_phase_frame.pack(fill='both', expand=True)
        
        title = tk.Label(self.current_phase_frame, text=f"🔫 ROUND {state['round']} - CHAMBER LOADED 🔫",
            font=('Arial', 28, 'bold'), fg=self.COLORS['accent'], bg=self.COLORS['bg_dark'])
        title.pack(pady=30)
        
        info = tk.Label(self.current_phase_frame,
            text=f"Total: {total} bullets | Live: {len(live_positions)} | Blank: {total - len(live_positions)}",
            font=('Arial', 16), fg=self.COLORS['text_light'], bg=self.COLORS['bg_dark'])
        info.pack(pady=10)
        
        bullets_frame = tk.Frame(self.current_phase_frame, bg=self.COLORS['bg_dark'])
        bullets_frame.pack(pady=30)
        
        for i in range(total):
            is_live = i in live_positions
            color = self.COLORS['live'] if is_live else self.COLORS['blank']
            symbol = "💥" if is_live else "💨"
            
            bullet_frame = tk.Frame(bullets_frame, bg=color, padx=15, pady=15)
            bullet_frame.pack(side='left', padx=8)
            
            tk.Label(bullet_frame, text=symbol, font=('Arial', 24), bg=color).pack()
            tk.Label(bullet_frame, text=f"#{i}", font=('Arial', 14, 'bold'),
                fg='white', bg=color).pack()
        
        message = tk.Label(self.current_phase_frame,
            text="🎯 These bullets are loaded in the chamber. Memorize them!",
            font=('Arial', 14), fg=self.COLORS['text_light'], bg=self.COLORS['bg_dark'])
        message.pack(pady=20)
        
        self.countdown_label = tk.Label(self.current_phase_frame, text="3",
            font=('Arial', 64, 'bold'), fg=self.COLORS['accent'], bg=self.COLORS['bg_dark'])
        self.countdown_label.pack(pady=10)
        
        gates_info_frame = tk.Frame(self.current_phase_frame, bg=self.COLORS['bg_medium'], padx=30, pady=15)
        gates_info_frame.pack(pady=20, fill='x', padx=100)
        
        p1_gates = [g['type'] for g in state['player1']['gates']]
        tk.Label(gates_info_frame, text=f"Player 1 Gates: {', '.join(p1_gates)}",
            font=('Arial', 12), fg=self.COLORS['player1'], bg=self.COLORS['bg_medium']).pack(anchor='w')
        
        p2_gates = [g['type'] for g in state['player2']['gates']]
        tk.Label(gates_info_frame, text=f"Player 2 Gates: {', '.join(p2_gates)}",
            font=('Arial', 12), fg=self.COLORS['player2'], bg=self.COLORS['bg_medium']).pack(anchor='w')
        
        self.do_countdown(3, self.game.start_playing_phase)
    
    def show_playing_ui(self):
        self.clear_main_frame()
        
        state = self.game.get_game_state()
        current_player = state['current_player']
        
        self.current_phase_frame = tk.Frame(self.main_frame, bg=self.COLORS['bg_dark'])
        self.current_phase_frame.pack(fill='both', expand=True)
        
        self.selected_gate_for_apply = None
        self.gate_target1 = None
        self.gate_target2 = None
        
        self.create_top_bar(state)
        
        game_area = tk.Frame(self.current_phase_frame, bg=self.COLORS['bg_dark'])
        game_area.pack(fill='both', expand=True, padx=20, pady=10)
        
        self.create_player_panel(game_area, state['player1'], 1, 'left')
        self.create_game_table(game_area, state)
        self.create_player_panel(game_area, state['player2'], 2, 'right')
        self.create_action_panel(state)
    
    def create_top_bar(self, state: Dict):
        top_bar = tk.Frame(self.current_phase_frame, bg=self.COLORS['bg_medium'], height=60)
        top_bar.pack(fill='x', padx=10, pady=10)
        top_bar.pack_propagate(False)
        
        tk.Label(top_bar, text=f"Round {state['round']}", font=('Arial', 16, 'bold'),
            fg=self.COLORS['accent'], bg=self.COLORS['bg_medium']).pack(side='left', padx=20, pady=15)
        
        current = state['current_player']
        color = self.COLORS['player1'] if current == 1 else self.COLORS['player2']
        tk.Label(top_bar, text=f"🎮 PLAYER {current}'s TURN 🎮", font=('Arial', 18, 'bold'),
            fg=color, bg=self.COLORS['bg_medium']).pack(side='left', expand=True, pady=15)
        
        remaining = len([m for m in state['bullets']['measured'] if not m])
        tk.Label(top_bar, text=f"Bullets: {remaining}/{state['bullets']['total']}",
            font=('Arial', 14), fg=self.COLORS['text_light'],
            bg=self.COLORS['bg_medium']).pack(side='right', padx=20, pady=15)
    
    def create_player_panel(self, parent: tk.Frame, player_data: Dict, player_num: int, side: str):
        color = self.COLORS['player1'] if player_num == 1 else self.COLORS['player2']
        
        panel = tk.Frame(parent, bg=self.COLORS['bg_medium'], width=250)
        panel.pack(side=side, fill='y', padx=10, pady=10)
        panel.pack_propagate(False)
        
        tk.Label(panel, text=f"👤 {player_data['name']}", font=('Arial', 16, 'bold'),
            fg=color, bg=self.COLORS['bg_medium']).pack(pady=15)
        
        lives_frame = tk.Frame(panel, bg=self.COLORS['bg_medium'])
        lives_frame.pack(pady=10)
        
        tk.Label(lives_frame, text="Lives: ", font=('Arial', 14),
            fg=self.COLORS['text_light'], bg=self.COLORS['bg_medium']).pack(side='left')
        
        tk.Label(lives_frame, text=str(player_data['lives']), font=('Arial', 24, 'bold'),
            fg=self.COLORS['live'], bg=self.COLORS['bg_medium']).pack(side='left')
        
        # Get current player to determine what to show
        state = self.game.get_game_state()
        current_player_id = state['current_player']
        is_current_player = (player_num == current_player_id)
        
        tk.Label(panel, text="Gates:", font=('Arial', 12, 'bold'),
            fg=self.COLORS['text_light'], bg=self.COLORS['bg_medium']).pack(pady=(20, 5), anchor='w', padx=15)
        
        if is_current_player:
            # Show full gate status for current player
            for gate in player_data['gates']:
                status = "✗" if gate['used'] else "✓"
                gate_color = self.COLORS['text_dim'] if gate['used'] else self.COLORS['text_light']
                tk.Label(panel, text=f"  {status} {gate['type']}", font=('Arial', 11),
                    fg=gate_color, bg=self.COLORS['bg_medium']).pack(anchor='w', padx=15)
        else:
            # For opponent, only show gate types without used/unused status
            # Count gates by type
            gate_counts = {}
            for gate in player_data['gates']:
                gt = gate['type']
                gate_counts[gt] = gate_counts.get(gt, 0) + 1
            
            for gate_type, count in gate_counts.items():
                if count > 1:
                    tk.Label(panel, text=f"  • {gate_type} ×{count}", font=('Arial', 11),
                        fg=self.COLORS['text_dim'], bg=self.COLORS['bg_medium']).pack(anchor='w', padx=15)
                else:
                    tk.Label(panel, text=f"  • {gate_type}", font=('Arial', 11),
                        fg=self.COLORS['text_dim'], bg=self.COLORS['bg_medium']).pack(anchor='w', padx=15)
        
        # Peek status - only show for current player
        if is_current_player:
            peek_status = "Available" if player_data['peek_available'] else "Used"
            peek_color = self.COLORS['blank'] if player_data['peek_available'] else self.COLORS['text_dim']
            tk.Label(panel, text=f"👁 Peek: {peek_status}", font=('Arial', 11),
                fg=peek_color, bg=self.COLORS['bg_medium']).pack(pady=15, anchor='w', padx=15)
    
    def create_game_table(self, parent: tk.Frame, state: Dict):
        center = tk.Frame(parent, bg=self.COLORS['bg_dark'])
        center.pack(side='left', fill='both', expand=True, padx=20)
        
        self.game_canvas = tk.Canvas(center, width=700, height=350,
            bg=self.COLORS['bg_dark'], highlightthickness=0)
        self.game_canvas.pack(pady=5)
        # Force canvas to update size before drawing
        self.game_canvas.update()
        self.animation.draw_table_scene(self.game_canvas, state['current_player'])
        
        tk.Label(center, text="🔫 CHAMBER 🔫", font=('Arial', 14, 'bold'),
            fg=self.COLORS['accent'], bg=self.COLORS['bg_dark']).pack(pady=10)
        
        bullets_frame = tk.Frame(center, bg=self.COLORS['bg_dark'])
        bullets_frame.pack(pady=10)
        
        self.bullet_buttons = []
        bullets = state['bullets']
        current_bullet = bullets['current_bullet']
        
        visible_states = self.game.get_visible_bullet_states(state['current_player'])
        
        for i in range(bullets['total']):
            btn_frame = tk.Frame(bullets_frame, bg=self.COLORS['bg_dark'])
            btn_frame.pack(side='left', padx=5)
            
            bullet_state = visible_states[i] if i < len(visible_states) else 'blank'
            
            color_map = {
                'fired_live': self.COLORS['fired_live'],
                'fired_blank': self.COLORS['fired_blank'],
                'live': self.COLORS['live'],
                'blank': self.COLORS['blank'],
                'superposition': self.COLORS['superposition'],
                'entangled': self.COLORS['entangled']
            }
            color = color_map.get(bullet_state, self.COLORS['blank'])
            
            if bullet_state == 'fired_live':
                symbol = "💥"
            elif bullet_state == 'fired_blank':
                symbol = "💨"
            elif bullet_state == 'live':
                symbol = "🔴"
            elif bullet_state == 'blank':
                symbol = "⚪"
            elif bullet_state == 'superposition':
                symbol = "🟡"
            elif bullet_state == 'entangled':
                symbol = "🟣"
            else:
                symbol = "⚪"
            
            is_fired = bullets['measured'][i]
            is_current = (i == current_bullet) and not is_fired
            
            # Only show entanglement link if current player created it
            entangle_text = ""
            if i in bullets['entanglements'] and not is_fired:
                # Check if current player applied a two-qubit gate involving this bullet
                current_player_obj = self.game.player1 if state['current_player'] == 1 else self.game.player2
                player_created_entanglement = any(
                    gt.is_two_qubit() and (t1 == i or t2 == i)
                    for gt, t1, t2 in current_player_obj.applied_gates_history
                )
                if player_created_entanglement:
                    partner = bullets['entanglements'][i]
                    entangle_text = f"\n🔗{partner}"
            
            current_indicator = "➤ " if is_current else ""
            
            border_color = self.COLORS['current_bullet'] if is_current else self.COLORS['bg_dark']
            
            btn = tk.Button(btn_frame,
                text=f"{current_indicator}{symbol}\n#{i}{entangle_text}",
                font=('Arial', 10), width=8, height=4,
                bg=color, fg='white', activebackground=color,
                relief='raised' if not is_fired else 'sunken',
                state='normal' if not is_fired else 'disabled',
                cursor='hand2' if not is_fired else 'arrow',
                highlightbackground=border_color, highlightthickness=3,
                command=lambda idx=i: self.select_bullet_for_gate(idx))
            btn.pack()
            self.bullet_buttons.append(btn)
    
    def select_bullet_for_gate(self, index: int):
        state = self.game.get_game_state()
        if state['bullets']['measured'][index]:
            return
        
        if self.selected_gate_for_apply:
            if self.selected_gate_for_apply.is_two_qubit():
                if self.gate_target1 is None:
                    self.gate_target1 = index
                    self.update_action_status(f"Control: #{index}. Select target bullet...")
                    self.bullet_buttons[index].configure(relief='solid')
                else:
                    self.gate_target2 = index
                    self.update_action_status(f"Control: #{self.gate_target1}, Target: #{index}. Click Apply!")
                    self.bullet_buttons[index].configure(relief='solid')
            else:
                self.gate_target1 = index
                self.update_action_status(f"Target: #{index}. Click Apply!")
                self.bullet_buttons[index].configure(relief='solid')
    
    def create_action_panel(self, state: Dict):
        action_frame = tk.Frame(self.current_phase_frame, bg=self.COLORS['bg_medium'], height=180)
        action_frame.pack(fill='x', padx=10, pady=10)
        action_frame.pack_propagate(False)
        
        current_player = state['current_player']
        player_data = state['player1'] if current_player == 1 else state['player2']
        color = self.COLORS['player1'] if current_player == 1 else self.COLORS['player2']
        gate_already_applied = state['gate_applied_this_turn']
        
        tk.Label(action_frame, text=f"🎯 {player_data['name']}'s Actions",
            font=('Arial', 14, 'bold'), fg=color, bg=self.COLORS['bg_medium']).pack(pady=10)
        
        buttons_frame = tk.Frame(action_frame, bg=self.COLORS['bg_medium'])
        buttons_frame.pack(pady=5)
        
        gate_frame = tk.Frame(buttons_frame, bg=self.COLORS['bg_medium'])
        gate_frame.pack(side='left', padx=20)
        
        gate_label_text = "Apply Gate:" if not gate_already_applied else "Gate Applied ✓"
        tk.Label(gate_frame, text=gate_label_text, font=('Arial', 11),
            fg=self.COLORS['text_light'], bg=self.COLORS['bg_medium']).pack()
        
        available_gates = [(g['type'], g['used']) for g in player_data['gates']]
        gate_options = ["None"] + [g[0] for g in available_gates if not g[1]]
        
        self.gate_var = tk.StringVar(value="None")
        dropdown_state = 'readonly' if not gate_already_applied else 'disabled'
        gate_dropdown = ttk.Combobox(gate_frame, textvariable=self.gate_var,
            values=gate_options, state=dropdown_state, width=12)
        gate_dropdown.pack(pady=5)
        gate_dropdown.bind('<<ComboboxSelected>>', self.on_gate_selected)
        
        btn_state = 'disabled'
        self.apply_gate_btn = tk.Button(gate_frame, text="⚡ Apply", font=('Arial', 10),
            bg=self.COLORS['bg_light'], fg=self.COLORS['text_light'],
            width=10, state=btn_state, command=self.apply_selected_gate)
        self.apply_gate_btn.pack(pady=5)
        
        shoot_frame = tk.Frame(buttons_frame, bg=self.COLORS['bg_medium'])
        shoot_frame.pack(side='left', padx=20)
        
        current_bullet = state['bullets']['current_bullet']
        tk.Label(shoot_frame, text=f"Shoot Bullet #{current_bullet}:",
            font=('Arial', 11), fg=self.COLORS['text_light'], bg=self.COLORS['bg_medium']).pack()
        
        shoot_btns = tk.Frame(shoot_frame, bg=self.COLORS['bg_medium'])
        shoot_btns.pack(pady=5)
        
        self.shoot_self_btn = tk.Button(shoot_btns, text="🎯 Shoot Self",
            font=('Arial', 11), bg='#ff9800', fg='white', width=12, cursor='hand2',
            command=lambda: self.shoot(True))
        self.shoot_self_btn.pack(side='left', padx=5)
        
        self.shoot_opponent_btn = tk.Button(shoot_btns, text="💀 Shoot Opponent",
            font=('Arial', 11), bg=self.COLORS['live'], fg='white', width=14, cursor='hand2',
            command=lambda: self.shoot(False))
        self.shoot_opponent_btn.pack(side='left', padx=5)
        
        peek_frame = tk.Frame(buttons_frame, bg=self.COLORS['bg_medium'])
        peek_frame.pack(side='left', padx=20)
        
        peek_available = player_data['peek_available']
        self.peek_btn = tk.Button(peek_frame, text="👁 Peek Gates", font=('Arial', 11),
            bg=self.COLORS['bg_light'] if peek_available else self.COLORS['fired'],
            fg=self.COLORS['text_light'], width=15,
            state='normal' if peek_available else 'disabled',
            cursor='hand2' if peek_available else 'arrow', command=self.use_peek)
        self.peek_btn.pack(pady=15)
        
        self.status_label = tk.Label(action_frame, text="Select a gate or shoot!",
            font=('Arial', 11, 'italic'), fg=self.COLORS['text_dim'], bg=self.COLORS['bg_medium'])
        self.status_label.pack(pady=5)
    
    def update_action_status(self, text: str):
        if hasattr(self, 'status_label'):
            self.status_label.configure(text=text)
    
    def on_gate_selected(self, event):
        gate_name = self.gate_var.get()
        
        if gate_name == "None":
            self.selected_gate_for_apply = None
            self.gate_target1 = None
            self.gate_target2 = None
            self.apply_gate_btn.configure(state='disabled')
            self.update_action_status("Select a gate or shoot!")
        else:
            for gt in GateType:
                if gt.value == gate_name:
                    self.selected_gate_for_apply = gt
                    self.gate_target1 = None
                    self.gate_target2 = None
                    
                    if gt.is_two_qubit():
                        self.update_action_status(f"Select control bullet, then target bullet for {gate_name}")
                    else:
                        self.update_action_status(f"Select target bullet for {gate_name}")
                    
                    self.apply_gate_btn.configure(state='normal')
                    break
    
    def apply_selected_gate(self):
        if not self.selected_gate_for_apply:
            return
        
        if self.gate_target1 is None:
            messagebox.showwarning("Warning", "Please select a target bullet first!")
            return
        
        if self.selected_gate_for_apply.is_two_qubit() and self.gate_target2 is None:
            messagebox.showwarning("Warning", "Please select a second target bullet!")
            return
        
        target2 = self.gate_target2 if self.gate_target2 is not None else -1
        success, msg = self.game.apply_gate(self.selected_gate_for_apply, self.gate_target1, target2)
        
        if success:
            self.update_action_status(msg)
            self.gate_var.set("None")
            self.selected_gate_for_apply = None
            self.gate_target1 = None
            self.gate_target2 = None
            self.apply_gate_btn.configure(state='disabled')
        else:
            messagebox.showerror("Error", msg)
    
    def shoot(self, shoot_self: bool):
        state = self.game.get_game_state()
        current_player = state['current_player']
        
        self.animation.animate_shot(self.game_canvas, current_player, shoot_self,
            callback=lambda: self.execute_shot(shoot_self))
    
    def execute_shot(self, shoot_self: bool):
        result = self.game.shoot(shoot_self)
        
        if not result['success']:
            messagebox.showerror("Error", result.get('message', 'Unknown error'))
            return
        
        if result['is_live']:
            if result['game_over']:
                return
        
        self.show_shot_result_screen(result)
    
    def show_shot_result_screen(self, result: Dict):
        self.clear_main_frame()
        
        self.current_phase_frame = tk.Frame(self.main_frame, bg=self.COLORS['bg_dark'])
        self.current_phase_frame.pack(fill='both', expand=True)
        
        if result['is_live']:
            symbol = "💥"
            color = self.COLORS['live']
            if result['shot_self']:
                main_text = f"{result['shooter']} SHOT THEMSELVES!"
            else:
                main_text = f"{result['shooter']} HIT {result['target']}!"
            sub_text = f"{result['target']} has {result['target_lives_remaining']} lives remaining"
        else:
            symbol = "💨"
            color = self.COLORS['blank']
            main_text = "BLANK ROUND!"
            if result['extra_turn']:
                sub_text = f"{result['shooter']} gets another turn!"
            else:
                sub_text = "Turn passes to opponent"
        
        tk.Label(self.current_phase_frame, text=symbol,
            font=('Arial', 100), bg=self.COLORS['bg_dark']).pack(pady=30)
        
        tk.Label(self.current_phase_frame, text=main_text,
            font=('Arial', 32, 'bold'), fg=color, bg=self.COLORS['bg_dark']).pack(pady=10)
        
        tk.Label(self.current_phase_frame, text=sub_text,
            font=('Arial', 18), fg=self.COLORS['text_light'], bg=self.COLORS['bg_dark']).pack(pady=10)
        
        if result['round_over']:
            next_text = "Starting new round..."
            callback = self.game.start_new_round
        elif result['extra_turn']:
            next_text = f"{result['shooter']}, continue your turn!"
            callback = self.on_game_state_change
        else:
            next_player = 1 if result['shooter_id'] == 2 else 2
            next_text = f"Switching to Player {next_player}..."
            callback = lambda: self.show_player_switch_screen(next_player, "take your turn")
        
        tk.Label(self.current_phase_frame, text=next_text,
            font=('Arial', 14, 'italic'), fg=self.COLORS['text_dim'],
            bg=self.COLORS['bg_dark']).pack(pady=30)
        
        self.countdown_label = tk.Label(self.current_phase_frame, text="3",
            font=('Arial', 48, 'bold'), fg=self.COLORS['accent'], bg=self.COLORS['bg_dark'])
        self.countdown_label.pack(pady=10)
        
        self.do_countdown(3, callback)
    
    def use_peek(self):
        success, gates = self.game.use_peek()
        
        if not success:
            messagebox.showinfo("Peek", "Peek has already been used this round!")
            return
        
        if gates:
            gate_list = ", ".join([g.gate_type.value for g in gates])
            messagebox.showinfo("👁 Peek Result", f"Opponent's available gates:\n\n{gate_list}")
        else:
            messagebox.showinfo("👁 Peek Result", "Opponent has no gates remaining!")
        
        self.on_game_state_change()
    
    def show_round_end_ui(self):
        self.clear_main_frame()
        
        self.current_phase_frame = tk.Frame(self.main_frame, bg=self.COLORS['bg_dark'])
        self.current_phase_frame.pack(fill='both', expand=True)
        
        tk.Label(self.current_phase_frame, text="🔄 ROUND COMPLETE! 🔄",
            font=('Arial', 32, 'bold'), fg=self.COLORS['accent'],
            bg=self.COLORS['bg_dark']).pack(pady=50)
        
        state = self.game.get_game_state()
        
        for pdata, color in [(state['player1'], self.COLORS['player1']), 
                             (state['player2'], self.COLORS['player2'])]:
            tk.Label(self.current_phase_frame, text=f"{pdata['name']}: {pdata['lives']} lives",
                font=('Arial', 20), fg=color, bg=self.COLORS['bg_dark']).pack(pady=10)
        
        tk.Label(self.current_phase_frame, text="New round starting...",
            font=('Arial', 14, 'italic'), fg=self.COLORS['text_dim'],
            bg=self.COLORS['bg_dark']).pack(pady=30)
        
        self.countdown_label = tk.Label(self.current_phase_frame, text="3",
            font=('Arial', 48, 'bold'), fg=self.COLORS['accent'], bg=self.COLORS['bg_dark'])
        self.countdown_label.pack()
        
        self.do_countdown(3, self.game.start_new_round)
    
    def show_game_end_ui(self, winner: Player):
        self.clear_main_frame()
        
        self.current_phase_frame = tk.Frame(self.main_frame, bg=self.COLORS['bg_dark'])
        self.current_phase_frame.pack(fill='both', expand=True)
        
        color = self.COLORS['player1'] if winner.player_id == 1 else self.COLORS['player2']
        
        tk.Label(self.current_phase_frame, text="🏆 GAME OVER 🏆",
            font=('Arial', 40, 'bold'), fg=self.COLORS['accent'],
            bg=self.COLORS['bg_dark']).pack(pady=50)
        
        tk.Label(self.current_phase_frame, text=f"{winner.name} WINS!",
            font=('Arial', 36, 'bold'), fg=color, bg=self.COLORS['bg_dark']).pack(pady=20)
        
        tk.Label(self.current_phase_frame, text="🎉 Congratulations! 🎉",
            font=('Arial', 24), fg=self.COLORS['text_light'],
            bg=self.COLORS['bg_dark']).pack(pady=20)
        
        btn_frame = tk.Frame(self.current_phase_frame, bg=self.COLORS['bg_dark'])
        btn_frame.pack(pady=40)
        
        tk.Button(btn_frame, text="🔄 Play Again", font=('Arial', 14),
            bg=self.COLORS['accent'], fg='white', width=15, height=2, cursor='hand2',
            command=self.restart_game).pack(side='left', padx=20)
        
        tk.Button(btn_frame, text="🚪 Main Menu", font=('Arial', 14),
            bg=self.COLORS['bg_light'], fg='white', width=15, height=2, cursor='hand2',
            command=self.exit_game).pack(side='left', padx=20)
    
    def restart_game(self):
        self.game = QuantumBuckshotGame(
            num_bullets=self.game.num_bullets,
            num_gates=self.game.num_gates,
            num_lives=self.game.initial_lives
        )
        self.game.on_state_change = self.on_game_state_change
        self.game.on_shot_result = self.on_shot_result
        self.game.on_round_end = self.on_round_end
        self.game.on_game_end = self.on_game_end
        self.start()
    
    def exit_game(self):
        self.root.destroy()
        self.on_exit()
