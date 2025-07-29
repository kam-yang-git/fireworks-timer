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
        TestTimerDialog,
        TestCanvasAnimationApp,
        TestIntegration
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