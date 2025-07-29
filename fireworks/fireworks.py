import tkinter as tk
from tkinter import messagebox
import random
import math

class Firework:
    def __init__(self, x, y, target_y):
        self.x = x
        self.y = y
        self.target_y = target_y
        self.speed = 8
        self.exploded = False
        self.particles = []
        self.trail = []
        self.color = random.choice(['red', 'blue', 'green', 'yellow', 'purple', 'orange', 'white', 'cyan'])
        
    def update(self):
        if not self.exploded:
            # 打ち上げ段階
            self.trail.append((self.x, self.y))
            if len(self.trail) > 10:
                self.trail.pop(0)
            
            self.y -= self.speed
            if self.y <= self.target_y:
                self.explode()
        else:
            # 爆発後のパーティクル更新
            for particle in self.particles:
                particle.update()
            # 消えたパーティクルを削除
            self.particles = [p for p in self.particles if p.life > 0]
    
    def explode(self):
        self.exploded = True
        # 変化菊パターンで放射状にパーティクルを作成
        num_particles = 32  # 菊のような放射状パターンのため固定数
        base_colors = ['gold', 'orange', 'red', 'crimson', 'purple']
        
        for i in range(num_particles):
            # 均等に放射状に配置
            angle = (2 * math.pi * i) / num_particles
            # 複数の輪を作る（菊のような重層構造）
            for ring in range(3):
                speed = 3 + ring * 2  # 輪ごとに速度を変える
                color_index = (ring + i // 4) % len(base_colors)
                color = base_colors[color_index]
                self.particles.append(Particle(self.x, self.y, angle, speed, color, ring))
    
    def draw(self, canvas):
        if not self.exploded:
            # 打ち上げ中の軌跡を描画
            for i, (x, y) in enumerate(self.trail):
                alpha = i / len(self.trail)
                size = max(1, int(4 * alpha))
                canvas.create_oval(x-size, y-size, x+size, y+size, 
                                 fill=self.color, outline='', tags='firework')
        else:
            # パーティクルを描画
            for particle in self.particles:
                particle.draw(canvas)
    
    def is_finished(self):
        return self.exploded and len(self.particles) == 0

class Particle:
    def __init__(self, x, y, angle, speed, color, ring=0):
        self.x = x
        self.y = y
        self.vx = math.cos(angle) * speed
        self.vy = math.sin(angle) * speed
        self.life = 80 + ring * 10  # 輪によって寿命を変える
        self.max_life = self.life
        self.initial_color = color
        self.current_color = color
        self.ring = ring
        self.gravity = 0.08
        self.fade_phase = 0  # 色変化のフェーズ
        
        # 尾を引く効果のための軌跡記録
        self.trail = []
        self.max_trail_length = 8  # 軌跡の最大長さ
        
        # 変化菊用の色変化パターン
        self.color_sequence = [
            'gold', 'yellow', 'orange', 'red', 'crimson', 'purple', 'blue', 'white'
        ]
        self.color_index = 0
        
    def update(self):
        # 現在位置を軌跡に追加
        self.trail.append((self.x, self.y, self.current_color))
        if len(self.trail) > self.max_trail_length:
            self.trail.pop(0)
            
        self.x += self.vx
        self.y += self.vy
        self.vy += self.gravity  # 重力効果
        self.vx *= 0.985  # 空気抵抗を少し弱める
        self.life -= 1
        
        # 色の変化（変化菊効果）
        life_ratio = 1 - (self.life / self.max_life)
        
        # 3段階で色が変化
        if life_ratio < 0.3:
            # 第1段階: 初期色 → 黄色
            self.current_color = self.initial_color
        elif life_ratio < 0.6:
            # 第2段階: 黄色 → オレンジ → 赤
            colors = ['yellow', 'orange', 'red']
            phase = int((life_ratio - 0.3) * 10) % len(colors)
            self.current_color = colors[phase]
        else:
            # 第3段階: 赤 → 紫 → 青 → 白（フェードアウト）
            colors = ['red', 'purple', 'blue', 'white']
            phase = int((life_ratio - 0.6) * 10) % len(colors)
            self.current_color = colors[phase]
        
    def draw(self, canvas):
        if self.life > 0:
            # 軌跡を描画（尾を引く効果）
            for i, (trail_x, trail_y, trail_color) in enumerate(self.trail):
                # 軌跡の透明度と大きさを後ろほど小さく
                trail_alpha = (i + 1) / len(self.trail)
                trail_size = max(1, int(2 * trail_alpha))
                
                # 軌跡の色を少し暗めに
                if trail_color == 'gold':
                    fade_color = 'orange'
                elif trail_color == 'yellow':
                    fade_color = 'gold'
                elif trail_color == 'orange':
                    fade_color = 'red'
                elif trail_color == 'red':
                    fade_color = 'darkred'
                elif trail_color == 'purple':
                    fade_color = 'darkviolet'
                elif trail_color == 'blue':
                    fade_color = 'darkblue'
                else:
                    fade_color = trail_color
                
                # 軌跡の透明度効果
                if i < len(self.trail) - 3:  # 古い軌跡ほど暗く
                    canvas.create_oval(trail_x-trail_size, trail_y-trail_size, 
                                     trail_x+trail_size, trail_y+trail_size,
                                     fill=fade_color, outline='', tags='firework')
            
            # メインのパーティクルを描画
            life_ratio = self.life / self.max_life
            size = max(2, int(4 * life_ratio))
            
            # 輪の構造により少し大きさを調整
            if self.ring == 0:  # 内側の輪
                size = max(2, int(size * 1.2))
            elif self.ring == 2:  # 外側の輪
                size = max(1, int(size * 0.8))
            
            # きらめき効果（ランダムで少し大きく描画）
            if random.random() < 0.1:
                size += 1
                # きらめきの外周を描画
                canvas.create_oval(self.x-size-1, self.y-size-1, self.x+size+1, self.y+size+1,
                                 fill='white', outline='', tags='firework')
                canvas.create_oval(self.x-size, self.y-size, self.x+size, self.y+size,
                                 fill=self.current_color, outline='', tags='firework')
            else:
                canvas.create_oval(self.x-size, self.y-size, self.x+size, self.y+size,
                                 fill=self.current_color, outline='', tags='firework')

class TimerDialog(tk.Toplevel):
    def __init__(self, parent):
        super().__init__(parent)
        self.parent = parent
        self.result = None
        
        self.title("タイマー設定")
        self.geometry("300x200")
        self.resizable(False, False)
        self.transient(parent)
        self.grab_set()
        
        # デフォルト値
        self.minutes = tk.IntVar(value=10)
        self.seconds = tk.IntVar(value=0)
        
        self.create_widgets()
        self.center_window()
    
    def center_window(self):
        """ウィンドウを中央に配置"""
        self.update_idletasks()
        x = (self.winfo_screenwidth() // 2) - (300 // 2)
        y = (self.winfo_screenheight() // 2) - (200 // 2)
        self.geometry(f"300x200+{x}+{y}")
    
    def create_widgets(self):
        # タイトル
        title_label = tk.Label(self, text="タイマー設定", font=("Arial", 14, "bold"))
        title_label.pack(pady=10)
        
        # 時間設定フレーム
        time_frame = tk.Frame(self)
        time_frame.pack(pady=20)
        
        # 分の設定
        tk.Label(time_frame, text="分:", font=("Arial", 12)).grid(row=0, column=0, padx=5)
        minutes_spinbox = tk.Spinbox(time_frame, from_=0, to=60, width=5, textvariable=self.minutes, font=("Arial", 12))
        minutes_spinbox.grid(row=0, column=1, padx=5)
        
        # 秒の設定
        tk.Label(time_frame, text="秒:", font=("Arial", 12)).grid(row=0, column=2, padx=5)
        seconds_spinbox = tk.Spinbox(time_frame, from_=0, to=59, width=5, textvariable=self.seconds, font=("Arial", 12))
        seconds_spinbox.grid(row=0, column=3, padx=5)
        
        # ボタンフレーム
        button_frame = tk.Frame(self)
        button_frame.pack(pady=20)
        
        tk.Button(button_frame, text="開始", command=self.start_timer, 
                 bg="green", fg="white", font=("Arial", 12, "bold"), width=8).pack(side=tk.LEFT, padx=10)
        tk.Button(button_frame, text="キャンセル", command=self.cancel_timer, 
                 bg="gray", fg="white", font=("Arial", 12, "bold"), width=8).pack(side=tk.LEFT, padx=10)
    
    def start_timer(self):
        """タイマー開始"""
        total_seconds = self.minutes.get() * 60 + self.seconds.get()
        if total_seconds > 0:
            self.result = total_seconds
            self.destroy()
        else:
            tk.messagebox.showwarning("警告", "時間を設定してください。")
    
    def cancel_timer(self):
        """キャンセル"""
        self.result = None
        self.destroy()

class CanvasAnimationApp(tk.Tk):
    def __init__(self):
        super().__init__()
        
        self.title("Fireworks Timer Application")
        self.geometry("1280x720")
        
        # アニメーション制御
        self.is_running = False
        self.fireworks = []
        self.animation_id = None
        
        # タイマー制御
        self.timer_seconds = 0
        self.remaining_seconds = 0
        self.timer_id = None
        self.start_time = None  # 開始時刻を記録
        self.end_time = None  # 終了時刻を記録
        
        self.create_widgets()
        self.setup_animations()
    
    def create_widgets(self):
        # コントロールパネル
        control_frame = tk.Frame(self)
        control_frame.pack(fill=tk.X, padx=10, pady=5)
        
        self.start_button = tk.Button(
            control_frame,
            text="タイマー設定",
            command=self.show_timer_dialog,
            bg="green",
            fg="white",
            font=("Arial", 12, "bold"),
            width=10
        )
        self.start_button.pack(side=tk.LEFT, padx=5)
        
        tk.Button(
            control_frame,
            text="リセット",
            command=self.reset_animation,
            bg="orange",
            fg="white",
            font=("Arial", 12, "bold"),
            width=8
        ).pack(side=tk.LEFT, padx=5)
        

        
        # 中央表示用のフレーム
        center_frame = tk.Frame(control_frame)
        center_frame.pack(expand=True, fill=tk.X)
        
        # 左寄せ配置用のフレーム
        center_labels_frame = tk.Frame(center_frame)
        center_labels_frame.pack(side=tk.LEFT, padx=(150, 0))
        
        # 休憩中表示
        self.break_var = tk.StringVar()
        self.break_var.set("")
        break_label = tk.Label(center_labels_frame, textvariable=self.break_var, font=("Arial", 16, "bold"), fg="red")
        break_label.pack(side=tk.LEFT, padx=20, pady=5)
        
        # タイマー表示
        self.timer_var = tk.StringVar()
        self.timer_var.set("")
        timer_label = tk.Label(center_labels_frame, textvariable=self.timer_var, font=("Arial", 16, "bold"), fg="blue")
        timer_label.pack(side=tk.LEFT, padx=20, pady=5)
        
        # キャンバス
        self.canvas = tk.Canvas(
            self,
            width=1200,
            height=700,
            bg='black',
            relief=tk.SUNKEN,
            borderwidth=2
        )
        self.canvas.pack(padx=10, pady=10)
        
        # キャンバスクリックで花火発射
        self.canvas.bind("<Button-1>", self.on_canvas_click)
    
    def setup_animations(self):
        """アニメーションの初期設定"""
        self.frame_count = 0
        self.next_firework_frame = random.randint(60, 120)  # 次の花火発射フレーム
    
    def show_timer_dialog(self):
        """タイマー設定ダイアログを表示"""
        dialog = TimerDialog(self)
        self.wait_window(dialog)
        
        if dialog.result is not None:
            self.timer_seconds = dialog.result
            self.remaining_seconds = self.timer_seconds
            # 開始時刻と終了時刻を記録
            import datetime
            now = datetime.datetime.now()
            self.start_time = now
            self.end_time = now + datetime.timedelta(seconds=self.timer_seconds)
            self.start_animation()
    
    def get_current_time(self):
        """現在時刻を取得（hh:mm形式）"""
        import datetime
        now = datetime.datetime.now()
        return now.strftime("%H:%M")
    
    def calculate_end_time(self):
        """終了時刻を計算（hh:mm形式）"""
        import datetime
        now = datetime.datetime.now()
        end_time = now + datetime.timedelta(seconds=self.timer_seconds)
        return end_time.strftime("%H:%M")
    
    def update_timer_display(self):
        """タイマー表示を更新"""
        if self.remaining_seconds > 0:
            minutes = self.remaining_seconds // 60
            seconds = self.remaining_seconds % 60
            self.timer_var.set(f"残り時間: {minutes:02d}:{seconds:02d}")
        else:
            self.timer_var.set("")
    
    def update_break_display(self):
        """休憩中表示を更新"""
        if self.is_running and self.timer_seconds > 0 and self.end_time:
            if self.remaining_seconds > 0:
                end_time_str = self.end_time.strftime("%H:%M")
                self.break_var.set(f"休憩中　再開時刻は {end_time_str} です。")
            else:
                end_time_str = self.end_time.strftime("%H:%M")
                self.break_var.set(f"再開時刻 {end_time_str} になりました。講義を再開します。")
        else:
            self.break_var.set("")
    
    def update_timer(self):
        """タイマー更新"""
        if self.is_running and self.remaining_seconds > 0:
            self.remaining_seconds -= 1
            self.update_timer_display()
            self.update_break_display()  # 休憩中表示も更新
            
            if self.remaining_seconds <= 0:
                # タイマー終了時の表示を更新
                self.update_break_display()
                # 花火を停止
                self.is_running = False
                if self.animation_id:
                    self.after_cancel(self.animation_id)
                    self.animation_id = None
                # 花火を消す
                self.canvas.delete('firework')
                return
            
            # 次のタイマー更新をスケジュール
            self.timer_id = self.after(1000, self.update_timer)
        
    def on_canvas_click(self, event):
        """キャンバスクリックで花火を発射"""
        if self.is_running:
            self.launch_firework(event.x, event.y)
    
    def launch_firework(self, x=None, y=None):
        """花火を発射"""
        if x is None:
            x = random.randint(50, 1150)  # キャンバス幅に合わせて調整
        if y is None:
            target_y = random.randint(100, 300)  # 高さも拡大
        else:
            target_y = y
            
        # 下から打ち上げ
        start_y = 680  # キャンバス高さに合わせて調整
        firework = Firework(x, start_y, target_y)
        self.fireworks.append(firework)
    
    def start_animation(self):
        """アニメーション開始"""
        if not self.is_running:
            self.is_running = True
            self.update_timer_display()
            self.update_break_display()  # 休憩中表示を更新
            self.update_timer()  # タイマー開始
            self.animate()
    
    def stop_animation(self):
        """アニメーション停止"""
        self.is_running = False
        self.timer_var.set("")
        self.break_var.set("")
        if self.animation_id:
            self.after_cancel(self.animation_id)
            self.animation_id = None
        if self.timer_id:
            self.after_cancel(self.timer_id)
            self.timer_id = None
    
    def reset_animation(self):
        """アニメーションリセット"""
        self.stop_animation()
        self.fireworks.clear()
        self.canvas.delete('firework')
        self.frame_count = 0
        self.next_firework_frame = random.randint(60, 120)  # リセット時も次の発射タイミングを設定
        self.timer_seconds = 0
        self.remaining_seconds = 0
        self.start_time = None
        self.end_time = None
        self.timer_var.set("")
        self.break_var.set("")
    
    def animate(self):
        """メインアニメーションループ"""
        if not self.is_running:
            return
            
        # キャンバスをクリア
        self.canvas.delete('firework')
        
        # 自動で花火を発射（決められたタイミングで）
        if self.frame_count >= self.next_firework_frame:
            self.launch_firework()
            # 次の発射タイミングを設定
            self.next_firework_frame = self.frame_count + random.randint(60, 120)
        
        # 花火を更新・描画
        for firework in self.fireworks[:]:
            firework.update()
            firework.draw(self.canvas)
            
            # 終了した花火を削除
            if firework.is_finished():
                self.fireworks.remove(firework)
        
        self.frame_count += 1
        
        # 次のフレームをスケジュール
        self.animation_id = self.after(50, self.animate)  # 約20FPS

if __name__ == "__main__":
    app = CanvasAnimationApp()
    app.mainloop()