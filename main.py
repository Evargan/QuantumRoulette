"""
Quantum Buckshot Roulette
A strategic two-player quantum game

Requirements:
    pip install qiskit qiskit-aer

To run:
    python main.py
"""

import tkinter as tk
from game_logic import QuantumBuckshotGame
from ui_components import GameUI


class MainMenu:
    """Main menu window for game settings and start"""
    
    def __init__(self):
        self.root = tk.Tk()
        self.root.title("Quantum Buckshot Roulette")
        self.root.geometry("700x700")
        self.root.configure(bg='#1a1a2e')
        self.root.resizable(False, False)
        
        self.center_window()
        
        self.num_bullets = tk.IntVar(value=6)
        self.num_gates = tk.IntVar(value=3)
        self.num_lives = tk.IntVar(value=3)
        
        self.create_widgets()
        
    def center_window(self):
        self.root.update_idletasks()
        width, height = 700, 700
        x = (self.root.winfo_screenwidth() // 2) - (width // 2)
        y = (self.root.winfo_screenheight() // 2) - (height // 2)
        self.root.geometry(f'{width}x{height}+{x}+{y}')
    
    def create_widgets(self):
        title_frame = tk.Frame(self.root, bg='#1a1a2e')
        title_frame.pack(pady=30)
        
        title_label = tk.Label(title_frame,
            text="🎯 QUANTUM BUCKSHOT ROULETTE 🎯",
            font=('Arial', 24, 'bold'), fg='#e94560', bg='#1a1a2e')
        title_label.pack()
        
        subtitle_label = tk.Label(title_frame,
            text="A Strategic Quantum Game",
            font=('Arial', 12, 'italic'), fg='#0f3460', bg='#1a1a2e')
        subtitle_label.pack(pady=5)
        
        settings_frame = tk.Frame(self.root, bg='#16213e', padx=40, pady=30)
        settings_frame.pack(pady=20, padx=50, fill='x')
        
        settings_title = tk.Label(settings_frame, text="⚙️ SETTINGS",
            font=('Arial', 16, 'bold'), fg='#e94560', bg='#16213e')
        settings_title.pack(pady=(0, 20))
        
        # Bullets
        bullets_frame = tk.Frame(settings_frame, bg='#16213e')
        bullets_frame.pack(fill='x', pady=10)
        
        tk.Label(bullets_frame, text="Number of Bullets:", font=('Arial', 12),
            fg='white', bg='#16213e', width=20, anchor='w').pack(side='left')
        
        tk.Scale(bullets_frame, from_=4, to=10, orient='horizontal',
            variable=self.num_bullets, bg='#16213e', fg='white',
            highlightthickness=0, troughcolor='#0f3460',
            activebackground='#e94560', length=200).pack(side='right')
        
        # Gates
        gates_frame = tk.Frame(settings_frame, bg='#16213e')
        gates_frame.pack(fill='x', pady=10)
        
        tk.Label(gates_frame, text="Gates per Player:", font=('Arial', 12),
            fg='white', bg='#16213e', width=20, anchor='w').pack(side='left')
        
        tk.Scale(gates_frame, from_=1, to=6, orient='horizontal',
            variable=self.num_gates, bg='#16213e', fg='white',
            highlightthickness=0, troughcolor='#0f3460',
            activebackground='#e94560', length=200).pack(side='right')
        
        # Lives
        lives_frame = tk.Frame(settings_frame, bg='#16213e')
        lives_frame.pack(fill='x', pady=10)
        
        tk.Label(lives_frame, text="Lives per Player:", font=('Arial', 12),
            fg='white', bg='#16213e', width=20, anchor='w').pack(side='left')
        
        tk.Scale(lives_frame, from_=1, to=5, orient='horizontal',
            variable=self.num_lives, bg='#16213e', fg='white',
            highlightthickness=0, troughcolor='#0f3460',
            activebackground='#e94560', length=200).pack(side='right')
        
        # Buttons
        buttons_frame = tk.Frame(self.root, bg='#1a1a2e')
        buttons_frame.pack(pady=30)
        
        tk.Button(buttons_frame, text="▶ START GAME",
            font=('Arial', 16, 'bold'), fg='white', bg='#e94560',
            activebackground='#ff6b6b', activeforeground='white',
            width=20, height=2, cursor='hand2', relief='flat',
            command=self.start_game).pack(pady=10)
        
        tk.Button(buttons_frame, text="✕ EXIT",
            font=('Arial', 12), fg='white', bg='#0f3460',
            activebackground='#16213e', activeforeground='white',
            width=20, height=1, cursor='hand2', relief='flat',
            command=self.root.quit).pack(pady=10)
        
        credits_label = tk.Label(self.root,
            text="Quantum Game Theory Research Project",
            font=('Arial', 9), fg='#0f3460', bg='#1a1a2e')
        credits_label.pack(side='bottom', pady=10)
    
    def start_game(self):
        self.root.withdraw()
        
        game = QuantumBuckshotGame(
            num_bullets=self.num_bullets.get(),
            num_gates=self.num_gates.get(),
            num_lives=self.num_lives.get()
        )
        
        game_window = tk.Toplevel(self.root)
        game_ui = GameUI(game_window, game, self.on_game_end)
        game_ui.start()
        
    def on_game_end(self):
        self.root.deiconify()
    
    def run(self):
        self.root.mainloop()


if __name__ == "__main__":
    menu = MainMenu()
    menu.run()
