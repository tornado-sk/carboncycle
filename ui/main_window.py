"""碳循环饮食计划生成器主窗口"""

import csv
import sys
from datetime import datetime

from PyQt6.QtCore import QSettings
from PyQt6.QtGui import QColor
from PyQt6.QtWidgets import (
    QApplication, QMainWindow, QWidget, QVBoxLayout, QHBoxLayout,
    QLabel, QLineEdit, QComboBox, QPushButton, QGroupBox, QTableWidget,
    QTableWidgetItem, QHeaderView, QTabWidget, QTextEdit, QMessageBox,
    QSpinBox, QDoubleSpinBox, QFileDialog,
)

from core.calculator import CarbCyclingCalculator
from core.input_model import UserInput
from ui import i18n


class MainWindow(QMainWindow):
    """主窗口"""

    # 周计划行背景色（按碳水类型）
    DAY_TYPE_COLORS = {
        'high': '#ffebee',      # 浅红
        'moderate': '#fff8e1',  # 浅黄
        'low': '#e8f5e9',       # 浅绿
    }

    def __init__(self):
        super().__init__()
        self.calculator = CarbCyclingCalculator()
        self.settings = QSettings('CarbCycle', 'Planner')
        self._last_plan = None
        self._last_user_name = '用户'
        self.init_ui()
        self._restore_inputs()

    def init_ui(self):
        """初始化UI"""
        self.setWindowTitle(i18n.WINDOW_TITLE)
        self.setGeometry(100, 100, 1100, 700)

        # 中央控件
        central_widget = QWidget()
        self.setCentralWidget(central_widget)

        # 主布局
        main_layout = QVBoxLayout()
        central_widget.setLayout(main_layout)

        # 创建标签页
        self.tabs = QTabWidget()
        main_layout.addWidget(self.tabs)

        # 各个页面
        self.create_input_tab()
        self.create_plan_tab()
        self.create_food_tab()

    def create_input_tab(self):
        """创建输入页面"""
        input_widget = QWidget()
        layout = QVBoxLayout()
        input_widget.setLayout(layout)

        # 个人信息组
        personal_group = QGroupBox(i18n.GROUP_PERSONAL)
        personal_layout = QVBoxLayout()

        # 第一行：姓名、性别、年龄
        row1 = QHBoxLayout()

        self.name_input = QLineEdit()
        self.name_input.setPlaceholderText(i18n.PH_NAME)

        self.gender_combo = QComboBox()
        self.gender_combo.addItems(['男', '女'])

        self.age_input = QSpinBox()
        self.age_input.setRange(10, 100)
        self.age_input.setValue(25)
        self.age_input.setSuffix(' 岁')

        row1.addWidget(QLabel(i18n.LABEL_NAME))
        row1.addWidget(self.name_input)
        row1.addWidget(QLabel(i18n.LABEL_GENDER))
        row1.addWidget(self.gender_combo)
        row1.addWidget(QLabel(i18n.LABEL_AGE))
        row1.addWidget(self.age_input)

        # 第二行：身高、体重、体脂率
        row2 = QHBoxLayout()

        self.height_input = QDoubleSpinBox()
        self.height_input.setRange(100, 230)
        self.height_input.setValue(170)
        self.height_input.setDecimals(1)
        self.height_input.setSuffix(' cm')

        self.weight_input = QDoubleSpinBox()
        self.weight_input.setRange(30, 250)
        self.weight_input.setValue(65)
        self.weight_input.setDecimals(1)
        self.weight_input.setSuffix(' kg')

        self.body_fat_input = QDoubleSpinBox()
        self.body_fat_input.setRange(3, 60)
        self.body_fat_input.setValue(20)
        self.body_fat_input.setDecimals(1)
        self.body_fat_input.setSuffix(' %')

        row2.addWidget(QLabel(i18n.LABEL_HEIGHT))
        row2.addWidget(self.height_input)
        row2.addWidget(QLabel(i18n.LABEL_WEIGHT))
        row2.addWidget(self.weight_input)
        row2.addWidget(QLabel(i18n.LABEL_BODY_FAT))
        row2.addWidget(self.body_fat_input)

        personal_layout.addLayout(row1)
        personal_layout.addLayout(row2)
        personal_group.setLayout(personal_layout)
        layout.addWidget(personal_group)

        # 训练信息组
        training_group = QGroupBox(i18n.GROUP_TRAINING)
        training_layout = QVBoxLayout()

        row3 = QHBoxLayout()

        self.training_years_input = QDoubleSpinBox()
        self.training_years_input.setRange(0, 80)
        self.training_years_input.setDecimals(1)
        self.training_years_input.setValue(1)
        self.training_years_input.setSuffix(' 年')

        self.training_intensity_combo = QComboBox()
        self.training_intensity_combo.addItems(['低强度', '中强度', '高强度'])
        self.training_intensity_combo.setToolTip(i18n.TIP_TRAINING_INTENSITY)

        self.training_days_combo = QComboBox()
        self.training_days_combo.addItems(['3天/周', '4天/周', '5天/周', '6天/周'])
        self.training_days_combo.setToolTip(i18n.TIP_TRAINING_DAYS)

        row3.addWidget(QLabel(i18n.LABEL_TRAINING_YEARS))
        row3.addWidget(self.training_years_input)
        row3.addWidget(QLabel(i18n.LABEL_TRAINING_INTENSITY))
        row3.addWidget(self.training_intensity_combo)
        row3.addWidget(QLabel(i18n.LABEL_TRAINING_DAYS))
        row3.addWidget(self.training_days_combo)

        row4 = QHBoxLayout()

        self.activity_combo = QComboBox()
        self.activity_combo.addItems([
            '久坐（很少运动）',
            '轻度活跃（每周1-3次运动）',
            '中度活跃（每周3-5次运动）',
            '高度活跃（每周6-7次运动）',
            '极度活跃（高强度训练）'
        ])
        self.activity_combo.setToolTip(i18n.TIP_ACTIVITY)

        row4.addWidget(QLabel(i18n.LABEL_ACTIVITY))
        row4.addWidget(self.activity_combo)

        training_layout.addLayout(row3)
        training_layout.addLayout(row4)
        training_group.setLayout(training_layout)
        layout.addWidget(training_group)

        # 目标选择
        goal_group = QGroupBox(i18n.GROUP_GOAL)
        goal_layout = QHBoxLayout()

        self.goal_combo = QComboBox()
        self.goal_combo.addItems(['减脂', '维持', '增肌'])

        goal_layout.addWidget(QLabel(i18n.LABEL_GOAL))
        goal_layout.addWidget(self.goal_combo)

        goal_group.setLayout(goal_layout)
        layout.addWidget(goal_group)

        # 生成按钮
        generate_btn = QPushButton(i18n.BTN_GENERATE)
        generate_btn.setStyleSheet("""
            QPushButton {
                background-color: #4CAF50;
                color: white;
                font-size: 16px;
                font-weight: bold;
                padding: 15px;
                border-radius: 5px;
            }
            QPushButton:hover {
                background-color: #45a049;
            }
        """)
        generate_btn.clicked.connect(self.generate_plan)
        layout.addWidget(generate_btn)

        # 结果显示区
        result_group = QGroupBox(i18n.GROUP_RESULT)
        result_layout = QVBoxLayout()

        self.result_text = QTextEdit()
        self.result_text.setReadOnly(True)
        self.result_text.setMaximumHeight(150)

        result_layout.addWidget(self.result_text)
        result_group.setLayout(result_layout)
        layout.addWidget(result_group)

        layout.addStretch()
        self.tabs.addTab(input_widget, i18n.TAB_INPUT)

    def create_plan_tab(self):
        """创建计划页面"""
        plan_widget = QWidget()
        layout = QVBoxLayout()
        plan_widget.setLayout(layout)

        # 周计划表格
        plan_group = QGroupBox('周碳循环计划')
        plan_layout = QVBoxLayout()

        self.plan_table = QTableWidget()
        self.plan_table.setColumnCount(6)
        self.plan_table.setHorizontalHeaderLabels(i18n.TABLE_HEADERS)

        # 设置表头样式
        header = self.plan_table.horizontalHeader()
        header.setSectionResizeMode(QHeaderView.ResizeMode.Stretch)

        plan_layout.addWidget(self.plan_table)

        # 导出按钮
        export_btn = QPushButton(i18n.BTN_EXPORT_CSV)
        export_btn.clicked.connect(self.export_csv)
        plan_layout.addWidget(export_btn)

        plan_group.setLayout(plan_layout)
        layout.addWidget(plan_group)

        # 宏量营养素说明
        note_group = QGroupBox('计划说明')
        note_layout = QVBoxLayout()

        note_text = QTextEdit()
        note_text.setReadOnly(True)
        note_text.setMaximumHeight(200)
        note_text.setPlainText(i18n.PLAN_NOTE_TEXT.strip())

        note_layout.addWidget(note_text)
        note_group.setLayout(note_layout)
        layout.addWidget(note_group)

        self.tabs.addTab(plan_widget, i18n.TAB_PLAN)

    def create_food_tab(self):
        """创建食物推荐页面"""
        food_widget = QWidget()
        layout = QVBoxLayout()
        food_widget.setLayout(layout)

        for title, text in [
            (i18n.FOOD_HIGH_TITLE, i18n.FOOD_HIGH_TEXT),
            (i18n.FOOD_MOD_TITLE, i18n.FOOD_MOD_TEXT),
            (i18n.FOOD_LOW_TITLE, i18n.FOOD_LOW_TEXT),
        ]:
            group = QGroupBox(title)
            group_layout = QVBoxLayout()
            label = QLabel(text)
            label.setWordWrap(True)
            group_layout.addWidget(label)
            group.setLayout(group_layout)
            layout.addWidget(group)

        layout.addStretch()
        self.tabs.addTab(food_widget, i18n.TAB_FOOD)

    def _read_inputs(self) -> UserInput:
        """从 widgets 读取用户输入。SpinBox 已限制范围，无需再 try/float。"""
        return UserInput(
            name=self.name_input.text() or i18n.DEFAULT_NAME,
            gender=self.gender_combo.currentText(),
            age=self.age_input.value(),
            height=self.height_input.value(),
            weight=self.weight_input.value(),
            body_fat=self.body_fat_input.value(),
            training_years=self.training_years_input.value(),
            training_intensity=self.training_intensity_combo.currentText(),
            activity_level=self.activity_combo.currentText(),
            goal=self.goal_combo.currentText(),
            training_days=int(self.training_days_combo.currentText()[0]),
        )

    def generate_plan(self):
        """生成饮食计划"""
        try:
            user_input = self._read_inputs()
            user_input.validate_or_raise()

            # 计算各项指标
            bmr = self.calculator.calculate_bmr(
                user_input.weight, user_input.height, user_input.age, user_input.gender
            )
            tdee = self.calculator.calculate_tdee(
                bmr, user_input.activity_level, user_input.training_years,
                user_input.training_intensity,
            )
            macros = self.calculator.calculate_macros(
                tdee, user_input.goal, user_input.body_fat, user_input.weight, bmr=bmr,
            )
            weekly_plan = self.calculator.create_weekly_plan(
                macros, user_input.training_days
            )
            weekly_avg_calories = sum(day['calories'] for day in weekly_plan) / len(weekly_plan)

            # 保存供 CSV 导出
            self._last_plan = weekly_plan
            self._last_user_name = user_input.name

            name = user_input.name

            # 显示基础结果（HTML 表格，避免中文等宽对齐问题）
            warnings_html = ''
            if macros['warnings']:
                warnings_html = (
                    '<p style="color:#d32f2f;">⚠ '
                    + '<br>⚠ '.join(macros['warnings']) + '</p>'
                )
            result = f"""
<h3 style="margin:4px 0;">{name} 的代谢数据</h3>
<table cellspacing="0" cellpadding="4" style="border-collapse:collapse;">
  <tr><td><b>基础代谢率 (BMR)</b></td><td>{bmr:.0f} 千卡</td>
      <td><b>蛋白质</b></td><td>{macros['protein']} g/天</td></tr>
  <tr><td><b>每日总消耗 (TDEE)</b></td><td>{tdee:.0f} 千卡</td>
      <td><b>脂肪</b></td><td>{macros['fat']} g/天</td></tr>
  <tr><td><b>目标摄入</b></td><td>{macros['calories']:.0f} 千卡</td>
      <td><b>碳水（基础）</b></td><td>{macros['carbs']} g/天</td></tr>
  <tr><td><b>周计划日均</b></td><td>{weekly_avg_calories:.0f} 千卡</td>
      <td></td><td></td></tr>
</table>
{warnings_html}
            """.strip()
            self.result_text.setHtml(result)

            # 更新表格
            self.plan_table.setRowCount(len(weekly_plan))

            for row, day_plan in enumerate(weekly_plan):
                self.plan_table.setItem(row, 0, QTableWidgetItem(day_plan['day']))
                self.plan_table.setItem(row, 1, QTableWidgetItem(day_plan['note']))
                self.plan_table.setItem(row, 2, QTableWidgetItem(f"{day_plan['calories']:.0f}"))
                self.plan_table.setItem(row, 3, QTableWidgetItem(f"{day_plan['protein']}g"))
                self.plan_table.setItem(row, 4, QTableWidgetItem(f"{day_plan['fat']}g"))
                self.plan_table.setItem(row, 5, QTableWidgetItem(f"{day_plan['carbs']}g"))

                # 设置行颜色
                color = self.DAY_TYPE_COLORS.get(day_plan['type'], '#ffffff')
                for col in range(6):
                    self.plan_table.item(row, col).setBackground(QColor(color))

            # 切换到计划页面
            self.tabs.setCurrentIndex(1)

            QMessageBox.information(
                self, i18n.MSG_GENERATE_OK_TITLE, i18n.MSG_GENERATE_OK_FMT.format(name)
            )

        except ValueError as e:
            message = str(e) or i18n.MSG_INPUT_ERROR_DEFAULT
            QMessageBox.warning(
                self, i18n.MSG_INPUT_ERROR_TITLE, message
            )
        except Exception as e:
            QMessageBox.critical(
                self, i18n.MSG_GENERATE_ERROR_TITLE, i18n.MSG_GENERATE_ERROR_FMT.format(str(e))
            )

    def generate_plan_for_user_input(self, user_input: UserInput):
        """供测试和外部脚本使用：直接传入 UserInput 生成结果"""
        user_input.validate_or_raise()
        bmr = self.calculator.calculate_bmr(
            user_input.weight, user_input.height, user_input.age, user_input.gender
        )
        tdee = self.calculator.calculate_tdee(
            bmr, user_input.activity_level, user_input.training_years,
            user_input.training_intensity,
        )
        macros = self.calculator.calculate_macros(
            tdee, user_input.goal, user_input.body_fat, user_input.weight, bmr=bmr,
        )
        plan = self.calculator.create_weekly_plan(macros, user_input.training_days)
        return bmr, tdee, macros, plan

    def export_csv(self) -> None:
        """把最近一次生成的周计划导出为 CSV。"""
        if not self._last_plan:
            QMessageBox.information(self, '提示', i18n.MSG_EXPORT_TIP)
            return

        default_name = f"{self._last_user_name}_{datetime.now():%Y%m%d}.csv"
        path, _ = QFileDialog.getSaveFileName(
            self, '导出周计划', default_name, 'CSV 文件 (*.csv)'
        )
        if not path:
            return

        try:
            with open(path, 'w', newline='', encoding='utf-8-sig') as f:
                writer = csv.writer(f)
                writer.writerow(['日期', '类型', '说明', '卡路里', '蛋白质(g)', '脂肪(g)', '碳水(g)'])
                for day in self._last_plan:
                    writer.writerow([
                        day['day'], day['type'], day['note'],
                        f"{day['calories']:.0f}", day['protein'], day['fat'], day['carbs'],
                    ])
            QMessageBox.information(
                self, i18n.MSG_EXPORT_OK_TITLE, i18n.MSG_EXPORT_OK_FMT.format(path)
            )
        except OSError as e:
            QMessageBox.warning(
                self, i18n.MSG_EXPORT_FAIL_TITLE, i18n.MSG_EXPORT_FAIL_FMT.format(e)
            )

    def _save_inputs(self) -> None:
        """保存当前输入到 QSettings"""
        s = self.settings
        s.setValue('name', self.name_input.text())
        s.setValue('gender', self.gender_combo.currentText())
        s.setValue('age', self.age_input.value())
        s.setValue('height', self.height_input.value())
        s.setValue('weight', self.weight_input.value())
        s.setValue('body_fat', self.body_fat_input.value())
        s.setValue('training_years', self.training_years_input.value())
        s.setValue('training_intensity', self.training_intensity_combo.currentText())
        s.setValue('activity', self.activity_combo.currentText())
        s.setValue('goal', self.goal_combo.currentText())
        s.setValue('training_days', self.training_days_combo.currentText())

    def _restore_inputs(self) -> None:
        """从 QSettings 恢复输入"""
        s = self.settings
        if s.value('name') is not None:
            self.name_input.setText(s.value('name', ''))
        if s.value('gender'):
            idx = self.gender_combo.findText(s.value('gender'))
            if idx >= 0:
                self.gender_combo.setCurrentIndex(idx)
        for value_key, widget in [
            ('age', self.age_input),
            ('height', self.height_input),
            ('weight', self.weight_input),
            ('body_fat', self.body_fat_input),
            ('training_years', self.training_years_input),
        ]:
            value = s.value(value_key)
            if value is not None:
                try:
                    widget.setValue(float(value))
                except (TypeError, ValueError):
                    pass
        for combo, key in [
            (self.training_intensity_combo, 'training_intensity'),
            (self.activity_combo, 'activity'),
            (self.goal_combo, 'goal'),
            (self.training_days_combo, 'training_days'),
        ]:
            value = s.value(key)
            if value:
                idx = combo.findText(str(value))
                if idx >= 0:
                    combo.setCurrentIndex(idx)

    def closeEvent(self, event):
        """关闭时保存输入"""
        self._save_inputs()
        super().closeEvent(event)
