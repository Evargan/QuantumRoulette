"""
Animation Manager for Quantum Roulette
"""

import tkinter as tk
from typing import Callable, Dict
import math


class AnimationManager:
    """Manages all game animations"""
    
    def __init__(self, root: tk.Tk, colors: Dict[str, str]):
        self.root = root
        self.colors = colors
        self.animation_running = False
    
    def draw_table_scene(self, canvas: tk.Canvas, current_player: int):
        """Draw the game table with two players"""
        canvas.delete("all")
        
        # Get actual canvas size
        canvas.update_idletasks()
        width = canvas.winfo_width()
        height = canvas.winfo_height()
        
        # Fallback if canvas not yet sized
        if width < 100:
            width = 700
        if height < 100:
            height = 350
        
        canvas.create_rectangle(0, 0, width, height, fill=self.colors['bg_dark'], outline='')
        
        # Table - centered and proportional
        table_width = int(width * 0.45)
        table_height = int(height * 0.35)
        table_x = (width - table_width) // 2
        table_y = (height - table_height) // 2
        
        # Table shadow
        canvas.create_rectangle(
            table_x + 5, table_y + 5,
            table_x + table_width + 5, table_y + table_height + 5,
            fill='#0a0a15', outline='')
        
        # Table surface
        canvas.create_rectangle(
            table_x, table_y,
            table_x + table_width, table_y + table_height,
            fill='#2d1f1f', outline='#4a3030', width=3)
        
        # Table pattern
        for i in range(0, table_width, 20):
            canvas.create_line(
                table_x + i, table_y,
                table_x + i, table_y + table_height,
                fill='#3d2f2f', width=1)
        
        # Gun in center
        gun_x = width // 2
        gun_y = height // 2
        self.draw_gun(canvas, gun_x, gun_y)
        
        # Player 1 (left side) - with proper spacing
        p1_x = table_x - 70
        p1_y = height // 2
        p1_active = current_player == 1
        self.draw_player(canvas, p1_x, p1_y, 1, p1_active, facing_right=True)
        
        # Player 2 (right side)
        p2_x = table_x + table_width + 70
        p2_y = height // 2
        p2_active = current_player == 2
        self.draw_player(canvas, p2_x, p2_y, 2, p2_active, facing_right=False)
        
        # Turn indicator
        if current_player == 1:
            self.draw_turn_indicator(canvas, p1_x, p1_y - 70, self.colors['player1'])
        else:
            self.draw_turn_indicator(canvas, p2_x, p2_y - 70, self.colors['player2'])
    
    def draw_player(self, canvas: tk.Canvas, x: int, y: int, player_num: int, 
                    active: bool, facing_right: bool):
        color = self.colors['player1'] if player_num == 1 else self.colors['player2']
        
        if active:
            for i in range(3, 0, -1):
                alpha_color = self.blend_colors(color, self.colors['bg_dark'], 0.3 * i)
                canvas.create_oval(
                    x - 25 - i*5, y - 35 - i*5,
                    x + 25 + i*5, y + 35 + i*5,
                    fill=alpha_color, outline='')
        
        canvas.create_oval(x - 20, y - 10, x + 20, y + 30,
            fill=color, outline=self.darken_color(color), width=2)
        
        canvas.create_oval(x - 15, y - 35, x + 15, y - 5,
            fill=color, outline=self.darken_color(color), width=2)
        
        eye_offset = 5 if facing_right else -5
        canvas.create_oval(x + eye_offset - 3, y - 25, x + eye_offset + 3, y - 19, fill='white')
        canvas.create_oval(x + eye_offset - 1, y - 24, x + eye_offset + 1, y - 20, fill='black')
        
        arm_dir = 1 if facing_right else -1
        canvas.create_line(
            x + arm_dir * 15, y,
            x + arm_dir * 40, y - 10,
            fill=self.darken_color(color), width=6, capstyle='round')
        
        label = f"P{player_num}"
        canvas.create_text(x, y + 50, text=label, fill=color, font=('Arial', 12, 'bold'))
    
    def draw_gun(self, canvas: tk.Canvas, x: int, y: int):
        canvas.create_rectangle(x - 60, y - 8, x + 60, y + 8,
            fill='#3d3d3d', outline='#2a2a2a', width=2)
        
        canvas.create_rectangle(x + 20, y - 5, x + 70, y + 5,
            fill='#4a4a4a', outline='#333333', width=1)
        
        canvas.create_polygon(
            x - 30, y + 8, x - 20, y + 8,
            x - 15, y + 25, x - 35, y + 25,
            fill='#5a3a2a', outline='#3a2a1a', width=2)
        
        canvas.create_arc(x - 25, y + 5, x - 5, y + 20,
            start=180, extent=180, style='arc', outline='#333333', width=2)
    
    def draw_turn_indicator(self, canvas: tk.Canvas, x: int, y: int, color: str):
        canvas.create_polygon(
            x, y + 15, x - 10, y, x - 5, y,
            x - 5, y - 15, x + 5, y - 15,
            x + 5, y, x + 10, y,
            fill=color, outline=self.darken_color(color), width=2)
        
        canvas.create_text(x, y - 30, text="YOUR TURN", fill=color, font=('Arial', 10, 'bold'))
    
    def animate_shot(self, canvas: tk.Canvas, shooter: int, shoot_self: bool, callback: Callable):
        self.animation_running = True
        
        width = canvas.winfo_width() or 600
        height = canvas.winfo_height() or 300
        
        gun_x = width // 2
        gun_y = height // 2
        
        if shooter == 1:
            target_x = width // 2 - 150 - 80 if shoot_self else width // 2 + 150 + 80
        else:
            target_x = width // 2 + 150 + 80 if shoot_self else width // 2 - 150 - 80
        target_y = height // 2
        
        frames = 10
        current_frame = [0]
        
        def animate_frame():
            if current_frame[0] < frames:
                progress = current_frame[0] / frames
                current_gun_x = gun_x + (target_x - gun_x) * progress * 0.3
                
                canvas.delete("all")
                self.draw_shooting_scene(canvas, shooter, shoot_self, current_gun_x, gun_y, progress)
                
                current_frame[0] += 1
                self.root.after(50, animate_frame)
            else:
                self.show_muzzle_flash(canvas, target_x, target_y, callback)
        
        animate_frame()
    
    def draw_shooting_scene(self, canvas: tk.Canvas, shooter: int, shoot_self: bool,
                           gun_x: float, gun_y: float, progress: float):
        width = canvas.winfo_width() or 600
        height = canvas.winfo_height() or 300
        
        canvas.create_rectangle(0, 0, width, height, fill=self.colors['bg_dark'], outline='')
        
        table_width = 300
        table_height = 120
        table_x = (width - table_width) // 2
        table_y = (height - table_height) // 2
        
        canvas.create_rectangle(table_x, table_y, table_x + table_width, table_y + table_height,
            fill='#2d1f1f', outline='#4a3030', width=3)
        
        p1_x = table_x - 80
        p2_x = table_x + table_width + 80
        p_y = height // 2
        
        self.draw_player(canvas, p1_x, p_y, 1, shooter == 1, facing_right=True)
        self.draw_player(canvas, p2_x, p_y, 2, shooter == 2, facing_right=False)
        
        gun_rotation = progress * 30
        self.draw_animated_gun(canvas, gun_x, gun_y, gun_rotation, shooter)
        
        if shoot_self:
            action_text = f"Player {shooter} aims at themselves..."
        else:
            target = 2 if shooter == 1 else 1
            action_text = f"Player {shooter} aims at Player {target}..."
        
        canvas.create_text(width // 2, 30, text=action_text,
            fill=self.colors['accent'], font=('Arial', 14, 'bold'))
    
    def draw_animated_gun(self, canvas: tk.Canvas, x: float, y: float, 
                         rotation: float, holder: int):
        rad = math.radians(rotation)
        length = 60
        direction = 1 if holder == 1 else -1
        
        x1 = x - length * math.cos(rad) * direction
        y1 = y - length * math.sin(rad)
        x2 = x + length * math.cos(rad) * direction
        y2 = y + length * math.sin(rad)
        
        canvas.create_line(x1, y1, x2, y2, fill='#4a4a4a', width=12, capstyle='round')
        canvas.create_oval(x2 - 5, y2 - 5, x2 + 5, y2 + 5, fill='#333333', outline='')
    
    def show_muzzle_flash(self, canvas: tk.Canvas, x: int, y: int, callback: Callable):
        width = canvas.winfo_width() or 600
        height = canvas.winfo_height() or 300
        
        flash_frames = 5
        current = [0]
        
        def flash():
            if current[0] < flash_frames:
                canvas.delete("flash")
                
                size = 30 + current[0] * 10
                colors = ['#ffff00', '#ff8800', '#ff4400', '#ff0000', '#880000']
                
                for i, color in enumerate(colors[:flash_frames - current[0]]):
                    s = size - i * 5
                    canvas.create_oval(x - s, y - s, x + s, y + s,
                        fill=color, outline='', tags="flash")
                
                if current[0] < 3:
                    canvas.create_text(width // 2, height // 2, text="BANG!",
                        fill='#ff4400', font=('Arial', 48, 'bold'), tags="flash")
                
                current[0] += 1
                self.root.after(80, flash)
            else:
                canvas.delete("flash")
                self.animation_running = False
                callback()
        
        flash()
    
    def blend_colors(self, color1: str, color2: str, ratio: float) -> str:
        r1, g1, b1 = int(color1[1:3], 16), int(color1[3:5], 16), int(color1[5:7], 16)
        r2, g2, b2 = int(color2[1:3], 16), int(color2[3:5], 16), int(color2[5:7], 16)
        
        r = int(r1 * (1 - ratio) + r2 * ratio)
        g = int(g1 * (1 - ratio) + g2 * ratio)
        b = int(b1 * (1 - ratio) + b2 * ratio)
        
        return f'#{r:02x}{g:02x}{b:02x}'
    
    def darken_color(self, color: str, factor: float = 0.7) -> str:
        r = int(int(color[1:3], 16) * factor)
        g = int(int(color[3:5], 16) * factor)
        b = int(int(color[5:7], 16) * factor)
        return f'#{r:02x}{g:02x}{b:02x}'
