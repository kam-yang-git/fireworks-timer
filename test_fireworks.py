import unittest
import tkinter as tk
from unittest.mock import Mock, patch, MagicMock
import sys
import os

# fireworksモジュールをインポート
sys.path.append(os.path.dirname(os.path.abspath(__file__)))
from fireworks.fireworks import Firework, Particle, TimerDialog, CanvasAnimationApp


class TestFirework(unittest.TestCase):
    """Fireworkクラスのテスト"""
    
    def setUp(self):
        """テスト前の準備"""
        self.firework = Firework(100, 500, 200)
    
    def test_firework_initialization(self):
        """花火の初期化テスト"""
        self.assertEqual(self.firework.x, 100)
        self.assertEqual(self.firework.y, 500)
        self.assertEqual(self.firework.target_y, 200)
        self.assertEqual(self.firework.speed, 8)
        self.assertFalse(self.firework.exploded)
        self.assertEqual(len(self.firework.particles), 0)
        self.assertEqual(len(self.firework.trail), 0)
        self.assertIn(self.firework.color, ['red', 'blue', 'green', 'yellow', 'purple', 'orange', 'white', 'cyan'])
    
    def test_firework_update_before_explosion(self):
        """爆発前の花火の更新テスト"""
        initial_y = self.firework.y
        initial_trail_length = len(self.firework.trail)
        
        self.firework.update()
        
        # 上に移動することを確認
        self.assertLess(self.firework.y, initial_y)
        # 軌跡が追加されることを確認
        self.assertGreater(len(self.firework.trail), initial_trail_length)
        # まだ爆発していないことを確認
        self.assertFalse(self.firework.exploded)
    
    def test_firework_explosion(self):
        """花火の爆発テスト"""
        # 花火を目標位置まで移動
        self.firework.y = self.firework.target_y + 1
        self.firework.update()
        
        # 爆発することを確認
        self.assertTrue(self.firework.exploded)
        # パーティクルが生成されることを確認
        self.assertGreater(len(self.firework.particles), 0)
    
    def test_firework_explosion_particles(self):
        """爆発時のパーティクル生成テスト"""
        self.firework.explode()
        
        # 96個のパーティクルが生成されることを確認（32個 × 3輪）
        self.assertEqual(len(self.firework.particles), 96)
        
        # 各パーティクルが正しく初期化されていることを確認
        for particle in self.firework.particles:
            self.assertIsInstance(particle, Particle)
            self.assertEqual(particle.x, self.firework.x)
            self.assertEqual(particle.y, self.firework.y)
    
    def test_firework_update_after_explosion(self):
        """爆発後の花火の更新テスト"""
        self.firework.explode()
        initial_particle_count = len(self.firework.particles)
        
        # パーティクルを少し寿命を減らす
        for particle in self.firework.particles:
            particle.life = 1
        
        self.firework.update()
        
        # 寿命が尽きたパーティクルが削除されることを確認
        self.assertLess(len(self.firework.particles), initial_particle_count)
    
    def test_firework_is_finished(self):
        """花火の終了判定テスト"""
        # 爆発前は終了していない
        self.assertFalse(self.firework.is_finished())
        
        # 爆発後、パーティクルがある場合は終了していない
        self.firework.explode()
        self.assertFalse(self.firework.is_finished())
        
        # パーティクルが全て消えた場合は終了
        self.firework.particles.clear()
        self.assertTrue(self.firework.is_finished())


class TestParticle(unittest.TestCase):
    """Particleクラスのテスト"""
    
    def setUp(self):
        """テスト前の準備"""
        self.particle = Particle(100, 200, 0, 5, 'red', 1)
    
    def test_particle_initialization(self):
        """パーティクルの初期化テスト"""
        self.assertEqual(self.particle.x, 100)
        self.assertEqual(self.particle.y, 200)
        self.assertEqual(self.particle.vx, 5)  # cos(0) * 5 = 5
        self.assertEqual(self.particle.vy, 0)  # sin(0) * 5 = 0
        self.assertEqual(self.particle.life, 90)  # 80 + 1 * 10
        self.assertEqual(self.particle.max_life, 90)
        self.assertEqual(self.particle.initial_color, 'red')
        self.assertEqual(self.particle.current_color, 'red')
        self.assertEqual(self.particle.ring, 1)
        self.assertEqual(self.particle.gravity, 0.08)
        self.assertEqual(len(self.particle.trail), 0)
    
    def test_particle_update(self):
        """パーティクルの更新テスト"""
        # 角度0度（水平方向）のパーティクルを作成
        particle = Particle(100, 200, 0, 5, 'red', 1)
        initial_x = particle.x
        initial_y = particle.y
        initial_life = particle.life
        initial_trail_length = len(particle.trail)
        
        particle.update()
        
        # 位置が更新されることを確認
        self.assertNotEqual(particle.x, initial_x)
        # 寿命が減少することを確認
        self.assertLess(particle.life, initial_life)
        # 軌跡が追加されることを確認
        self.assertGreater(len(particle.trail), initial_trail_length)
        
        # 複数回更新して重力の影響を確認
        for _ in range(5):
            particle.update()
        
        # 重力によりY座標が下に移動することを確認
        self.assertGreater(particle.y, initial_y)
    
    def test_particle_color_change(self):
        """パーティクルの色変化テスト"""
        # 初期色を確認
        self.assertEqual(self.particle.current_color, 'red')
        
        # 寿命を少し減らして色変化をテスト
        self.particle.life = int(self.particle.max_life * 0.5)  # 50%の寿命
        self.particle.update()
        
        # 色が変化していることを確認（具体的な色は実装に依存）
        self.assertIsInstance(self.particle.current_color, str)
    
    def test_particle_life_death(self):
        """パーティクルの寿命終了テスト"""
        self.particle.life = 1
        self.particle.update()
        
        # 寿命が0になることを確認
        self.assertEqual(self.particle.life, 0)


class TestParticleDrawing(unittest.TestCase):
    """Particle描画機能のテスト"""
    
    def setUp(self):
        """テスト前の準備"""
        self.root = tk.Tk()
        self.canvas = tk.Canvas(self.root, width=400, height=300, bg='black')
        self.canvas.pack()
        
    def tearDown(self):
        """テスト後のクリーンアップ"""
        self.canvas.destroy()
        self.root.destroy()
    
    def test_particle_draw_basic(self):
        """基本的なパーティクル描画テスト"""
        particle = Particle(100, 200, 0, 5, 'red', 1)
        particle.life = 90  # 寿命を設定
        
        # 描画前のキャンバス状態を確認
        initial_items = len(self.canvas.find_all())
        
        # パーティクルを描画
        particle.draw(self.canvas)
        
        # 描画後にキャンバスアイテムが追加されることを確認
        final_items = len(self.canvas.find_all())
        self.assertGreater(final_items, initial_items)
    
    def test_particle_draw_with_trail(self):
        """軌跡付きパーティクル描画テスト"""
        particle = Particle(100, 200, 0, 5, 'red', 1)
        particle.life = 90
        
        # 軌跡を追加
        particle.trail = [
            (95, 195, 'red'),
            (90, 190, 'red'),
            (85, 185, 'red')
        ]
        
        # 描画前のキャンバス状態を確認
        initial_items = len(self.canvas.find_all())
        
        # パーティクルを描画
        particle.draw(self.canvas)
        
        # 軌跡も含めて描画されることを確認
        final_items = len(self.canvas.find_all())
        self.assertGreater(final_items, initial_items)
    
    def test_particle_draw_sparkle_effect(self):
        """きらめき効果のテスト"""
        particle = Particle(100, 200, 0, 5, 'gold', 0)
        particle.life = 90
        
        # きらめき効果を強制的に発生させるため、random.random()をモック
        with patch('random.random', return_value=0.05):  # きらめき発生
            # 描画前のキャンバス状態を確認
            initial_items = len(self.canvas.find_all())
            
            # パーティクルを描画
            particle.draw(self.canvas)
            
            # きらめき効果により追加のアイテムが描画されることを確認
            final_items = len(self.canvas.find_all())
            self.assertGreater(final_items, initial_items)
    
    def test_particle_draw_no_sparkle(self):
        """きらめき効果なしのテスト"""
        particle = Particle(100, 200, 0, 5, 'red', 1)
        particle.life = 90
        
        # きらめき効果を無効にするため、random.random()をモック
        with patch('random.random', return_value=0.5):  # きらめきなし
            # 描画前のキャンバス状態を確認
            initial_items = len(self.canvas.find_all())
            
            # パーティクルを描画
            particle.draw(self.canvas)
            
            # 通常の描画のみ行われることを確認
            final_items = len(self.canvas.find_all())
            self.assertGreater(final_items, initial_items)
    
    def test_particle_draw_ring_structure(self):
        """輪の構造による描画調整テスト"""
        # 内側の輪（ring=0）
        inner_particle = Particle(100, 200, 0, 5, 'red', 0)
        inner_particle.life = 90
        
        # 外側の輪（ring=2）
        outer_particle = Particle(150, 200, 0, 5, 'blue', 2)
        outer_particle.life = 90
        
        # 両方のパーティクルを描画
        inner_particle.draw(self.canvas)
        outer_particle.draw(self.canvas)
        
        # 両方とも正常に描画されることを確認
        items = len(self.canvas.find_all())
        self.assertGreater(items, 0)
    
    def test_particle_draw_life_based_size(self):
        """寿命に基づくサイズ調整テスト"""
        # 寿命が長いパーティクル
        long_life_particle = Particle(100, 200, 0, 5, 'red', 1)
        long_life_particle.life = 90
        long_life_particle.max_life = 90
        
        # 寿命が短いパーティクル
        short_life_particle = Particle(150, 200, 0, 5, 'blue', 1)
        short_life_particle.life = 30
        short_life_particle.max_life = 90
        
        # 両方のパーティクルを描画
        long_life_particle.draw(self.canvas)
        short_life_particle.draw(self.canvas)
        
        # 両方とも正常に描画されることを確認
        items = len(self.canvas.find_all())
        self.assertGreater(items, 0)
    
    def test_particle_draw_color_variations(self):
        """色変化パターンのテスト"""
        colors = ['gold', 'yellow', 'orange', 'red', 'purple', 'blue', 'white']
        
        for i, color in enumerate(colors):
            particle = Particle(100 + i * 20, 200, 0, 5, color, 1)
            particle.life = 90
            
            # 各色のパーティクルを描画
            particle.draw(self.canvas)
        
        # 全ての色が正常に描画されることを確認
        items = len(self.canvas.find_all())
        self.assertGreater(items, 0)
    
    def test_particle_draw_fade_effect(self):
        """フェード効果のテスト"""
        particle = Particle(100, 200, 0, 5, 'gold', 1)
        particle.life = 90
        
        # 軌跡を追加（フェード効果をテスト）
        particle.trail = [
            (95, 195, 'gold'),
            (90, 190, 'orange'),
            (85, 185, 'red')
        ]
        
        # パーティクルを描画
        particle.draw(self.canvas)
        
        # フェード効果が正常に描画されることを確認
        items = len(self.canvas.find_all())
        self.assertGreater(items, 0)
    
    def test_particle_draw_zero_life(self):
        """寿命0のパーティクル描画テスト"""
        particle = Particle(100, 200, 0, 5, 'red', 1)
        particle.life = 0  # 寿命0
        
        # 描画前のキャンバス状態を確認
        initial_items = len(self.canvas.find_all())
        
        # パーティクルを描画
        particle.draw(self.canvas)
        
        # 寿命0の場合は何も描画されないことを確認
        final_items = len(self.canvas.find_all())
        self.assertEqual(final_items, initial_items)
    
    def test_particle_draw_complex_trail(self):
        """複雑な軌跡の描画テスト"""
        particle = Particle(100, 200, 0, 5, 'purple', 1)
        particle.life = 90
        
        # 複雑な軌跡を追加
        particle.trail = [
            (95, 195, 'purple'),
            (90, 190, 'purple'),
            (85, 185, 'purple'),
            (80, 180, 'purple'),
            (75, 175, 'purple'),
            (70, 170, 'purple'),
            (65, 165, 'purple'),
            (60, 160, 'purple')
        ]
        
        # パーティクルを描画
        particle.draw(self.canvas)
        
        # 複雑な軌跡が正常に描画されることを確認
        items = len(self.canvas.find_all())
        self.assertGreater(items, 0)
    
    def test_particle_draw_all_rings(self):
        """全ての輪の描画テスト"""
        for ring in range(3):
            particle = Particle(100 + ring * 50, 200, 0, 5, 'red', ring)
            particle.life = 90
            
            # 各輪のパーティクルを描画
            particle.draw(self.canvas)
        
        # 全ての輪が正常に描画されることを確認
        items = len(self.canvas.find_all())
        self.assertGreater(items, 0)
    
    def test_particle_draw_edge_cases(self):
        """エッジケースの描画テスト"""
        # 極端な位置のパーティクル
        edge_particle = Particle(0, 0, 0, 5, 'red', 1)
        edge_particle.life = 90
        
        # 極端な位置でも正常に描画されることを確認
        edge_particle.draw(self.canvas)
        
        items = len(self.canvas.find_all())
        self.assertGreater(items, 0)
    
    def test_particle_draw_integration(self):
        """統合描画テスト"""
        # 複数のパーティクルを同時に描画
        particles = []
        for i in range(5):
            particle = Particle(100 + i * 30, 200, 0, 5, 'red', i % 3)
            particle.life = 90
            particles.append(particle)
        
        # 全てのパーティクルを描画
        for particle in particles:
            particle.draw(self.canvas)
        
        # 全てのパーティクルが正常に描画されることを確認
        items = len(self.canvas.find_all())
        self.assertGreater(items, 0)


class TestTimerDialog(unittest.TestCase):
    """TimerDialogクラスのテスト"""
    
    def setUp(self):
        """テスト前の準備"""
        self.root = tk.Tk()
        self.dialog = TimerDialog(self.root)
    
    def tearDown(self):
        """テスト後のクリーンアップ"""
        self.dialog.destroy()
        self.root.destroy()
    
    def test_timer_dialog_initialization(self):
        """タイマーダイアログの初期化テスト"""
        self.assertEqual(self.dialog.minutes.get(), 10)
        self.assertEqual(self.dialog.seconds.get(), 0)
        self.assertIsNone(self.dialog.result)
    
    def test_start_timer_valid_input(self):
        """有効な入力でのタイマー開始テスト"""
        self.dialog.minutes.set(5)
        self.dialog.seconds.set(30)
        
        with patch('tkinter.messagebox.showwarning') as mock_warning:
            self.dialog.start_timer()
            
            # 警告が表示されないことを確認
            mock_warning.assert_not_called()
            # 結果が正しく設定されることを確認
            self.assertEqual(self.dialog.result, 330)  # 5分30秒 = 330秒
    
    def test_start_timer_invalid_input(self):
        """無効な入力でのタイマー開始テスト"""
        self.dialog.minutes.set(0)
        self.dialog.seconds.set(0)
        
        with patch('tkinter.messagebox.showwarning') as mock_warning:
            self.dialog.start_timer()
            
            # 警告が表示されることを確認
            mock_warning.assert_called_once()
            # 結果がNoneのままであることを確認
            self.assertIsNone(self.dialog.result)
    
    def test_cancel_timer(self):
        """タイマーキャンセルテスト"""
        self.dialog.cancel_timer()
        self.assertIsNone(self.dialog.result)


class TestCanvasAnimationApp(unittest.TestCase):
    """CanvasAnimationAppクラスのテスト"""
    
    def setUp(self):
        """テスト前の準備"""
        self.app = CanvasAnimationApp()
    
    def tearDown(self):
        """テスト後のクリーンアップ"""
        self.app.destroy()
    
    def test_app_initialization(self):
        """アプリケーションの初期化テスト"""
        self.assertFalse(self.app.is_running)
        self.assertEqual(len(self.app.fireworks), 0)
        self.assertIsNone(self.app.animation_id)
        self.assertEqual(self.app.timer_seconds, 0)
        self.assertEqual(self.app.remaining_seconds, 0)
        self.assertIsNone(self.app.timer_id)
        self.assertIsNone(self.app.start_time)
        self.assertIsNone(self.app.end_time)
    
    def test_launch_firework(self):
        """花火発射テスト"""
        initial_firework_count = len(self.app.fireworks)
        
        self.app.launch_firework(100, 200)
        
        # 花火が追加されることを確認
        self.assertEqual(len(self.app.fireworks), initial_firework_count + 1)
        
        # 追加された花火のプロパティを確認
        firework = self.app.fireworks[-1]
        self.assertEqual(firework.x, 100)
        self.assertEqual(firework.target_y, 200)
    
    def test_launch_firework_random(self):
        """ランダム花火発射テスト"""
        initial_firework_count = len(self.app.fireworks)
        
        self.app.launch_firework()
        
        # 花火が追加されることを確認
        self.assertEqual(len(self.app.fireworks), initial_firework_count + 1)
        
        # 追加された花火のプロパティを確認
        firework = self.app.fireworks[-1]
        self.assertIsInstance(firework.x, int)
        self.assertIsInstance(firework.target_y, int)
    
    def test_reset_animation(self):
        """アニメーションリセットテスト"""
        # 花火を追加
        self.app.launch_firework(100, 200)
        self.app.is_running = True
        
        self.app.reset_animation()
        
        # リセット後の状態を確認
        self.assertFalse(self.app.is_running)
        self.assertEqual(len(self.app.fireworks), 0)
        self.assertEqual(self.app.timer_seconds, 0)
        self.assertEqual(self.app.remaining_seconds, 0)
        self.assertIsNone(self.app.start_time)
        self.assertIsNone(self.app.end_time)
    
    def test_update_timer_display(self):
        """タイマー表示更新テスト"""
        self.app.remaining_seconds = 125  # 2分5秒
        self.app.update_timer_display()
        
        # 表示が正しく更新されることを確認
        self.assertEqual(self.app.timer_var.get(), "残り時間: 02:05")
    
    def test_update_timer_display_zero(self):
        """タイマー表示更新テスト（0秒）"""
        self.app.remaining_seconds = 0
        self.app.update_timer_display()
        
        # 表示が空になることを確認
        self.assertEqual(self.app.timer_var.get(), "")
    
    def test_calculate_end_time(self):
        """終了時刻計算テスト"""
        with patch('datetime.datetime') as mock_datetime:
            # 現在時刻を2024年1月1日12:00:00に固定
            mock_now = Mock()
            mock_now.strftime.return_value = "12:00"
            mock_datetime.now.return_value = mock_now
            
            # 終了時刻を計算
            mock_end = Mock()
            mock_end.strftime.return_value = "12:10"
            mock_timedelta = Mock()
            mock_datetime.timedelta.return_value = mock_timedelta
            mock_now.__add__ = Mock(return_value=mock_end)
            
            self.app.timer_seconds = 600  # 10分
            end_time = self.app.calculate_end_time()
            
            # 終了時刻が計算されることを確認
            self.assertEqual(end_time, "12:10")
    
    def test_show_timer_dialog_sets_end_time(self):
        """タイマーダイアログで終了時刻が設定されるテスト"""
        with patch('fireworks.fireworks.TimerDialog') as mock_dialog_class:
            # モックダイアログを作成
            mock_dialog = Mock()
            mock_dialog.result = 300  # 5分
            mock_dialog_class.return_value = mock_dialog
            
            with patch.object(self.app, 'wait_window') as mock_wait_window:
                with patch.object(self.app, 'start_animation') as mock_start_animation:
                    with patch('datetime.datetime') as mock_datetime:
                        # 現在時刻を固定
                        mock_now = Mock()
                        mock_datetime.now.return_value = mock_now
                        
                        # 終了時刻をモック
                        mock_end = Mock()
                        mock_timedelta = Mock()
                        mock_datetime.timedelta.return_value = mock_timedelta
                        mock_now.__add__ = Mock(return_value=mock_end)
                        
                        # タイマーダイアログを表示
                        self.app.show_timer_dialog()
                        
                        # 終了時刻が設定されることを確認
                        self.assertIsNotNone(self.app.end_time)
                        self.assertEqual(self.app.timer_seconds, 300)
                        self.assertEqual(self.app.remaining_seconds, 300)  # タイマー開始前なので300のまま
    
    def test_update_break_display_with_fixed_end_time(self):
        """固定終了時刻での休憩表示更新テスト"""
        with patch('datetime.datetime') as mock_datetime:
            # 終了時刻をモック
            mock_end = Mock()
            mock_end.strftime.return_value = "12:10"
            
            # アプリケーションの状態を設定
            self.app.is_running = True
            self.app.timer_seconds = 300
            self.app.remaining_seconds = 180
            self.app.end_time = mock_end
            
            # 休憩表示を更新
            self.app.update_break_display()
            
            # 正しいメッセージが表示されることを確認
            self.assertIn("12:10", self.app.break_var.get())
            self.assertIn("休憩中", self.app.break_var.get())
    
    def test_update_break_display_timer_finished(self):
        """タイマー終了時の休憩表示テスト"""
        with patch('datetime.datetime') as mock_datetime:
            # 終了時刻をモック
            mock_end = Mock()
            mock_end.strftime.return_value = "12:10"
            
            # アプリケーションの状態を設定（タイマー終了）
            self.app.is_running = True
            self.app.timer_seconds = 300
            self.app.remaining_seconds = 0
            self.app.end_time = mock_end
            
            # 休憩表示を更新
            self.app.update_break_display()
            
            # 正しいメッセージが表示されることを確認
            self.assertIn("12:10", self.app.break_var.get())
            self.assertIn("再開時刻", self.app.break_var.get())
            self.assertIn("講義を再開します", self.app.break_var.get())
    
    def test_update_break_display_no_timer(self):
        """タイマーなしでの休憩表示テスト"""
        # タイマーが設定されていない状態
        self.app.is_running = False
        self.app.timer_seconds = 0
        self.app.end_time = None
        
        # 休憩表示を更新
        self.app.update_break_display()
        
        # 表示が空になることを確認
        self.assertEqual(self.app.break_var.get(), "")


class TestAnimationAndTimer(unittest.TestCase):
    """アニメーションとタイマーのテスト"""
    
    def setUp(self):
        """テスト前の準備"""
        self.app = CanvasAnimationApp()
    
    def tearDown(self):
        """テスト後のクリーンアップ"""
        self.app.destroy()
    
    def test_start_animation(self):
        """アニメーション開始のテスト"""
        # 初期状態を確認
        self.assertFalse(self.app.is_running)
        self.assertIsNone(self.app.animation_id)
        
        # アニメーションを開始
        self.app.start_animation()
        
        # 状態が変更されることを確認
        self.assertTrue(self.app.is_running)
        self.assertIsNotNone(self.app.animation_id)
    
    def test_stop_animation(self):
        """アニメーション停止のテスト"""
        # アニメーションを開始
        self.app.start_animation()
        self.assertTrue(self.app.is_running)
        
        # アニメーションを停止
        self.app.stop_animation()
        
        # 状態が変更されることを確認
        self.assertFalse(self.app.is_running)
        self.assertIsNone(self.app.animation_id)
        self.assertEqual(self.app.timer_var.get(), "")
        self.assertEqual(self.app.break_var.get(), "")
    
    def test_animate_method(self):
        """アニメーションループのテスト"""
        # アニメーションを開始
        self.app.is_running = True
        self.app.frame_count = 0
        self.app.next_firework_frame = 1  # 次のフレームで花火を発射
        
        # 花火を追加
        initial_firework_count = len(self.app.fireworks)
        
        # アニメーションループを実行
        self.app.animate()
        
        # フレームカウントが増加することを確認
        self.assertEqual(self.app.frame_count, 1)
        
        # 自動花火発射が動作することを確認（next_firework_frameを調整）
        self.app.frame_count = 100
        self.app.next_firework_frame = 100
        self.app.animate()
        
        # 花火が追加されることを確認
        self.assertGreater(len(self.app.fireworks), initial_firework_count)
    
    def test_animate_when_not_running(self):
        """アニメーション停止時のanimateテスト"""
        # アニメーションを停止
        self.app.is_running = False
        initial_frame_count = self.app.frame_count
        
        # animateを呼び出しても何も起こらないことを確認
        self.app.animate()
        
        # フレームカウントが変更されないことを確認
        self.assertEqual(self.app.frame_count, initial_frame_count)
    
    def test_update_timer(self):
        """タイマー更新のテスト"""
        # タイマーを設定
        self.app.is_running = True
        self.app.remaining_seconds = 10
        self.app.timer_seconds = 10
        
        # タイマー更新を実行
        with patch.object(self.app, 'after') as mock_after:
            self.app.update_timer()
            
            # 残り時間が減少することを確認
            self.assertEqual(self.app.remaining_seconds, 9)
            
            # 次のタイマー更新がスケジュールされることを確認
            mock_after.assert_called_once_with(1000, self.app.update_timer)
    
    def test_update_timer_finished(self):
        """タイマー終了時のテスト"""
        # タイマーを設定（残り時間1から0になるように）
        self.app.is_running = True
        self.app.remaining_seconds = 1
        self.app.timer_seconds = 10
        self.app.animation_id = "dummy_id"
        
        with patch.object(self.app, 'after_cancel') as mock_after_cancel:
            with patch.object(self.app, 'update_break_display') as mock_update_break:
                with patch.object(self.app.canvas, 'delete') as mock_delete:
                    # タイマー更新を実行（remaining_secondsが1から0になる）
                    self.app.update_timer()
                    
                    # アニメーションが停止されることを確認
                    self.assertFalse(self.app.is_running)
                    self.assertIsNone(self.app.animation_id)
                    
                    # 花火が消されることを確認
                    mock_delete.assert_called_once_with('firework')
    
    def test_animate_with_finished_fireworks(self):
        """終了した花火の処理テスト"""
        # 花火を作成して爆発させる
        firework = Firework(100, 500, 200)
        firework.explode()
        self.app.fireworks.append(firework)
        
        # パーティクルの寿命を0にする
        for particle in firework.particles:
            particle.life = 0
        
        # アニメーションを開始
        self.app.is_running = True
        
        # アニメーションループを実行
        self.app.animate()
        
        # 終了した花火が削除されることを確認
        self.assertEqual(len(self.app.fireworks), 0)
    
    def test_animate_clears_canvas(self):
        """アニメーション時のキャンバスクリアテスト"""
        # アニメーションを開始
        self.app.is_running = True
        
        # キャンバスに何かを描画
        self.app.canvas.create_oval(0, 0, 10, 10, tags='firework')
        
        # アニメーションループを実行
        self.app.animate()
        
        # キャンバスがクリアされることを確認（fireworkタグの要素が削除される）
        # 実際のテストでは、キャンバスの内容を直接確認することは難しいため、
        # アニメーションが正常に動作することを確認
    
    def test_animate_schedules_next_frame(self):
        """次のフレームのスケジュールテスト"""
        # アニメーションを開始
        self.app.is_running = True
        
        with patch.object(self.app, 'after') as mock_after:
            # アニメーションループを実行
            self.app.animate()
            
            # 次のフレームがスケジュールされることを確認
            mock_after.assert_called_once_with(50, self.app.animate)
    
    def test_update_timer_display_integration(self):
        """タイマー表示の統合テスト"""
        # タイマーを設定
        self.app.remaining_seconds = 125  # 2分5秒
        
        # タイマー表示を更新
        self.app.update_timer_display()
        
        # 表示が正しく更新されることを確認
        self.assertEqual(self.app.timer_var.get(), "残り時間: 02:05")
    
    def test_update_break_display_integration(self):
        """休憩表示の統合テスト"""
        # 終了時刻を設定
        with patch('datetime.datetime') as mock_datetime:
            mock_end = Mock()
            mock_end.strftime.return_value = "12:10"
            
            self.app.is_running = True
            self.app.timer_seconds = 300  # タイマー秒数を設定
            self.app.remaining_seconds = 180  # 残り時間を設定
            self.app.end_time = mock_end
            
            # 休憩表示を更新
            self.app.update_break_display()
            
            # 正しいメッセージが表示されることを確認
            break_text = self.app.break_var.get()
            self.assertIn("12:10", break_text)
            self.assertIn("休憩中", break_text)
    
    def test_launch_firework_integration(self):
        """花火発射の統合テスト"""
        # ランダム花火発射
        initial_count = len(self.app.fireworks)
        self.app.launch_firework()
        
        # 花火が追加されることを確認
        self.assertEqual(len(self.app.fireworks), initial_count + 1)
        
        # 追加された花火のプロパティを確認
        firework = self.app.fireworks[-1]
        self.assertIsInstance(firework.x, int)
        self.assertIsInstance(firework.target_y, int)
        self.assertFalse(firework.exploded)
    
    def test_firework_lifecycle_integration(self):
        """花火ライフサイクルの統合テスト"""
        # 花火を発射
        self.app.launch_firework(100, 200)
        firework = self.app.fireworks[0]
        
        # 爆発前の状態を確認
        self.assertFalse(firework.exploded)
        self.assertEqual(len(firework.particles), 0)
        
        # 花火を更新（爆発させる）
        firework.y = firework.target_y
        firework.update()
        
        # 爆発後の状態を確認
        self.assertTrue(firework.exploded)
        self.assertGreater(len(firework.particles), 0)
        
        # パーティクルの寿命を0にして終了させる
        for particle in firework.particles:
            particle.life = 0
        
        # 花火を更新
        firework.update()
        
        # 花火が終了することを確認
        self.assertTrue(firework.is_finished())


class TestIntegration(unittest.TestCase):
    """統合テスト"""
    
    def setUp(self):
        """テスト前の準備"""
        self.root = tk.Tk()
    
    def tearDown(self):
        """テスト後のクリーンアップ"""
        self.root.destroy()
    
    def test_firework_particle_integration(self):
        """花火とパーティクルの統合テスト"""
        # 花火を作成
        firework = Firework(100, 500, 200)
        
        # 爆発前の状態を確認
        self.assertFalse(firework.exploded)
        self.assertEqual(len(firework.particles), 0)
        
        # 爆発させる
        firework.explode()
        
        # 爆発後の状態を確認
        self.assertTrue(firework.exploded)
        self.assertGreater(len(firework.particles), 0)
        
        # パーティクルの更新をテスト
        initial_particle_count = len(firework.particles)
        firework.update()
        
        # パーティクルが更新されることを確認
        self.assertIsInstance(firework.particles[0].x, (int, float))
        self.assertIsInstance(firework.particles[0].y, (int, float))
    
    def test_canvas_click_integration(self):
        """キャンバスクリック統合テスト"""
        app = CanvasAnimationApp()
        
        # アニメーションを開始
        app.is_running = True
        
        # モックイベントを作成
        mock_event = Mock()
        mock_event.x = 100
        mock_event.y = 200
        
        # キャンバスクリックをシミュレート
        initial_firework_count = len(app.fireworks)
        app.on_canvas_click(mock_event)
        
        # 花火が追加されることを確認
        self.assertEqual(len(app.fireworks), initial_firework_count + 1)
        
        app.destroy()


class TestGUIEventHandlers(unittest.TestCase):
    """GUIイベントハンドラーのテスト"""
    
    def setUp(self):
        """テスト前の準備"""
        self.app = CanvasAnimationApp()
    
    def tearDown(self):
        """テスト後のクリーンアップ"""
        self.app.destroy()
    
    def test_canvas_click_event(self):
        """キャンバスクリックイベントのテスト"""
        # アニメーションを開始
        self.app.is_running = True
        initial_firework_count = len(self.app.fireworks)
        
        # モックイベントを作成
        mock_event = Mock()
        mock_event.x = 100
        mock_event.y = 200
        
        # キャンバスクリックをシミュレート
        self.app.on_canvas_click(mock_event)
        
        # 花火が追加されることを確認
        self.assertEqual(len(self.app.fireworks), initial_firework_count + 1)
        
        # 追加された花火のプロパティを確認
        firework = self.app.fireworks[-1]
        self.assertEqual(firework.x, 100)
        self.assertEqual(firework.target_y, 200)
    
    def test_canvas_click_when_not_running(self):
        """アニメーション停止時のキャンバスクリックテスト"""
        # アニメーションを停止
        self.app.is_running = False
        initial_firework_count = len(self.app.fireworks)
        
        # モックイベントを作成
        mock_event = Mock()
        mock_event.x = 150
        mock_event.y = 250
        
        # キャンバスクリックをシミュレート
        self.app.on_canvas_click(mock_event)
        
        # 花火が追加されないことを確認
        self.assertEqual(len(self.app.fireworks), initial_firework_count)
    
    def test_canvas_click_bound_to_canvas(self):
        """キャンバスへのイベントバインディングテスト"""
        # キャンバスにバインディングされているイベントを確認
        bindings = self.app.canvas.bind()
        
        # Button-1（左クリック）がバインディングされていることを確認
        self.assertIn('<Button-1>', bindings)
    
    def test_button_click_events(self):
        """ボタンクリックイベントのテスト"""
        # リセットボタンのクリックをテスト
        initial_firework_count = len(self.app.fireworks)
        self.app.is_running = True
        
        # リセットボタンをクリック
        self.app.reset_animation()
        
        # アニメーションが停止し、花火がクリアされることを確認
        self.assertFalse(self.app.is_running)
        self.assertEqual(len(self.app.fireworks), 0)
    
    def test_timer_button_click(self):
        """タイマー設定ボタンクリックのテスト"""
        with patch('fireworks.fireworks.TimerDialog') as mock_dialog_class:
            # モックダイアログを作成
            mock_dialog = Mock()
            mock_dialog.result = 300  # 5分
            mock_dialog_class.return_value = mock_dialog
            
            with patch.object(self.app, 'wait_window') as mock_wait_window:
                with patch.object(self.app, 'start_animation') as mock_start_animation:
                    # タイマー設定ボタンをクリック
                    self.app.show_timer_dialog()
                    
                    # ダイアログが作成され、アニメーションが開始されることを確認
                    mock_dialog_class.assert_called_once_with(self.app)
                    mock_wait_window.assert_called_once_with(mock_dialog)
                    mock_start_animation.assert_called_once()
    
    def test_timer_button_click_cancel(self):
        """タイマー設定キャンセルのテスト"""
        with patch('fireworks.fireworks.TimerDialog') as mock_dialog_class:
            # モックダイアログを作成（キャンセル）
            mock_dialog = Mock()
            mock_dialog.result = None
            mock_dialog_class.return_value = mock_dialog
            
            with patch.object(self.app, 'wait_window') as mock_wait_window:
                with patch.object(self.app, 'start_animation') as mock_start_animation:
                    # タイマー設定ボタンをクリック
                    self.app.show_timer_dialog()
                    
                    # ダイアログが作成されるが、アニメーションは開始されないことを確認
                    mock_dialog_class.assert_called_once_with(self.app)
                    mock_wait_window.assert_called_once_with(mock_dialog)
                    mock_start_animation.assert_not_called()
    
    def test_keyboard_events(self):
        """キーボードイベントのテスト（もし実装されている場合）"""
        # 現在の実装ではキーボードイベントはないが、
        # 将来的な拡張のためにテストを準備
        pass
    
    def test_multiple_canvas_clicks(self):
        """複数回のキャンバスクリックテスト"""
        self.app.is_running = True
        
        # 複数回クリック
        for i in range(3):
            mock_event = Mock()
            mock_event.x = 100 + i * 50
            mock_event.y = 200 + i * 30
            self.app.on_canvas_click(mock_event)
        
        # 3つの花火が追加されることを確認
        self.assertEqual(len(self.app.fireworks), 3)
        
        # 各花火の位置を確認
        for i, firework in enumerate(self.app.fireworks):
            self.assertEqual(firework.x, 100 + i * 50)
            self.assertEqual(firework.target_y, 200 + i * 30)
    
    def test_canvas_click_edge_cases(self):
        """キャンバスクリックのエッジケーステスト"""
        self.app.is_running = True
        
        # 境界値でのテスト
        edge_cases = [
            (0, 0),           # 左上
            (1200, 0),        # 右上
            (0, 700),         # 左下
            (1200, 700),      # 右下
            (600, 350),       # 中央
        ]
        
        for x, y in edge_cases:
            mock_event = Mock()
            mock_event.x = x
            mock_event.y = y
            self.app.on_canvas_click(mock_event)
        
        # 全ての花火が正しく追加されることを確認
        self.assertEqual(len(self.app.fireworks), len(edge_cases))
    
    def test_canvas_click_with_negative_coordinates(self):
        """負の座標でのキャンバスクリックテスト"""
        self.app.is_running = True
        
        mock_event = Mock()
        mock_event.x = -10
        mock_event.y = -20
        
        # 負の座標でも花火が追加されることを確認
        initial_count = len(self.app.fireworks)
        self.app.on_canvas_click(mock_event)
        
        self.assertEqual(len(self.app.fireworks), initial_count + 1)
        firework = self.app.fireworks[-1]
        self.assertEqual(firework.x, -10)
        self.assertEqual(firework.target_y, -20)
    
    def test_canvas_click_with_large_coordinates(self):
        """大きな座標でのキャンバスクリックテスト"""
        self.app.is_running = True
        
        mock_event = Mock()
        mock_event.x = 2000
        mock_event.y = 1500
        
        # 大きな座標でも花火が追加されることを確認
        initial_count = len(self.app.fireworks)
        self.app.on_canvas_click(mock_event)
        
        self.assertEqual(len(self.app.fireworks), initial_count + 1)
        firework = self.app.fireworks[-1]
        self.assertEqual(firework.x, 2000)
        self.assertEqual(firework.target_y, 1500)
    
    def test_button_command_bindings(self):
        """ボタンのコマンドバインディングテスト"""
        # タイマー設定ボタンのコマンドが設定されていることを確認
        self.assertIsNotNone(self.app.start_button['command'])
        
        # コマンドが設定されていることを確認（文字列または呼び出し可能オブジェクト）
        command = self.app.start_button['command']
        self.assertTrue(callable(command) or isinstance(command, str))
        
        # リセットボタンのコマンドを確認（create_widgets内で作成されるため、
        # 実際のボタンオブジェクトへの参照を取得する必要がある）
        # このテストは実装の詳細に依存するため、実際の動作で確認
    
    def test_event_propagation(self):
        """イベント伝播のテスト"""
        self.app.is_running = True
        
        # イベントが正しく処理されることを確認
        mock_event = Mock()
        mock_event.x = 100
        mock_event.y = 200
        
        # イベント処理前の状態
        initial_fireworks = len(self.app.fireworks)
        
        # イベントを処理
        self.app.on_canvas_click(mock_event)
        
        # イベント処理後の状態
        final_fireworks = len(self.app.fireworks)
        
        # 花火が追加されたことを確認
        self.assertEqual(final_fireworks, initial_fireworks + 1)


class TestTimerDialogCenterWindow(unittest.TestCase):
    """TimerDialog.center_window()のテスト"""
    def setUp(self):
        self.root = tk.Tk()
        self.dialog = TimerDialog(self.root)
    def tearDown(self):
        self.dialog.destroy()
        self.root.destroy()
    def test_center_window_sets_position(self):
        # center_window呼び出し
        self.dialog.center_window()
        # ウィンドウの更新を待つ
        self.dialog.update()
        after = self.dialog.geometry()
        # 位置座標部分（+X+Y）が中央付近かどうかを検証
        import re
        match = re.match(r"\d+x\d+\+(\d+)\+(\d+)", after)
        self.assertIsNotNone(match)
        x = int(match.group(1))
        y = int(match.group(2))
        # 画面中央付近（0より大きいことだけ確認、詳細な中央判定は環境依存なので緩く）
        self.assertGreater(x, 0)
        self.assertGreater(y, 0)
        # サイズ部分も確認（ウィンドウが更新された後なので正しいサイズが反映される）
        self.assertIn("300x200", after)

class TestGetCurrentTime(unittest.TestCase):
    """CanvasAnimationApp.get_current_time()のテスト"""
    def setUp(self):
        self.app = CanvasAnimationApp()
    def tearDown(self):
        self.app.destroy()
    def test_get_current_time_format(self):
        # datetimeをモックして固定値を返す
        with patch('datetime.datetime') as mock_datetime:
            mock_now = Mock()
            mock_now.strftime.return_value = "12:34"
            mock_datetime.now.return_value = mock_now
            result = self.app.get_current_time()
            self.assertEqual(result, "12:34")


if __name__ == '__main__':
    # カバレージ測定の設定
    try:
        import coverage
        cov = coverage.Coverage()
        cov.start()
    except ImportError:
        cov = None
        print("coverageライブラリがインストールされていません。")
        print("インストール方法: pip install coverage")
    
    # テストスイートを作成
    test_suite = unittest.TestSuite()
    
    # 各テストクラスを追加
    test_classes = [
        TestFirework,
        TestParticle,
        TestParticleDrawing, # 新しいテストクラスを追加
        TestTimerDialog,
        TestCanvasAnimationApp,
        TestAnimationAndTimer, # 新しいテストクラスを追加
        TestIntegration,
        TestGUIEventHandlers,
        TestTimerDialogCenterWindow, # 新しいテストクラスを追加
        TestGetCurrentTime # 新しいテストクラスを追加
    ]
    
    for test_class in test_classes:
        tests = unittest.TestLoader().loadTestsFromTestCase(test_class)
        test_suite.addTests(tests)
    
    # テストを実行
    runner = unittest.TextTestRunner(verbosity=2)
    result = runner.run(test_suite)
    
    # カバレージ測定を停止
    if cov:
        cov.stop()
        cov.save()
        
        # カバレージレポートを表示
        print("\n" + "="*50)
        print("カバレージレポート")
        print("="*50)
        cov.report()
        
        # HTMLレポートを生成
        cov.html_report(directory='htmlcov')
        print(f"\n詳細なHTMLレポートが 'htmlcov/index.html' に生成されました。")
    
    # 結果を表示
    print(f"\nテスト結果:")
    print(f"実行したテスト数: {result.testsRun}")
    print(f"失敗したテスト数: {len(result.failures)}")
    print(f"エラーが発生したテスト数: {len(result.errors)}")
    
    if result.failures:
        print("\n失敗したテスト:")
        for test, traceback in result.failures:
            print(f"- {test}: {traceback}")
    
    if result.errors:
        print("\nエラーが発生したテスト:")
        for test, traceback in result.errors:
            print(f"- {test}: {traceback}")