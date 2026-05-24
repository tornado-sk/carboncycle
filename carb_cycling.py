"""向后兼容入口：保留 `from carb_cycling import CarbCyclingCalculator` 导入路径。

实际实现已拆分到 core/calculator.py 与 ui/main_window.py。

⚠ 此模块不直接导入 PyQt6，确保纯计算逻辑可在无 GUI 环境（如 CI）测试。
"""

from core.calculator import CarbCyclingCalculator

__all__ = ['CarbCyclingCalculator']


if __name__ == '__main__':
    # 仅在直接运行时才加载 GUI 入口
    from main import main
    main()
