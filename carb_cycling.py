"""
碳循环饮食计划计算器
Carb Cycling Diet Planner
"""

import sys
from PyQt6.QtWidgets import (
    QApplication, QMainWindow, QWidget, QVBoxLayout, QHBoxLayout,
    QLabel, QLineEdit, QComboBox, QPushButton, QGroupBox, QTableWidget,
    QTableWidgetItem, QHeaderView, QTabWidget, QTextEdit, QMessageBox,
)


class CarbCyclingCalculator:
    """碳循环饮食计算核心逻辑"""

    def __init__(self):
        self.gender_options = {
            '男': 5,
            '女': -161
        }

    def calculate_bmr(self, weight, height, age, gender):
        """使用 Mifflin-St Jeor 公式计算基础代谢率"""
        gender_factor = self.gender_options.get(gender, 5)
        bmr = (10 * weight) + (6.25 * height) - (5 * age) + gender_factor
        return bmr

    def calculate_tdee(self, bmr, activity_level, training_years, training_intensity='中强度'):
        """计算每日总能量消耗"""
        activity_factors = {
            '久坐（很少运动）': 1.2,
            '轻度活跃（每周1-3次运动）': 1.375,
            '中度活跃（每周3-5次运动）': 1.55,
            '高度活跃（每周6-7次运动）': 1.725,
            '极度活跃（高强度训练）': 1.9
        }
        factor = activity_factors.get(activity_level, 1.55)

        # 训练年限加成（长期训练者代谢更高效）
        training_bonus = min(0.1, training_years * 0.01)

        intensity_adjustments = {
            '低强度': -0.03,
            '中强度': 0,
            '高强度': 0.04
        }
        intensity_adjustment = intensity_adjustments.get(training_intensity, 0)

        tdee = bmr * factor * (1 + training_bonus + intensity_adjustment)
        return tdee

    def calculate_macros(self, tdee, goal, body_fat_pct, weight):
        """计算宏量营养素分配"""
        # 根据目标调整卡路里
        goal_adjustments = {
            '减脂': -500,
            '维持': 0,
            '增肌': 300
        }
        target_calories = tdee + goal_adjustments.get(goal, 0)

        # 蛋白质：优先基于瘦体重计算，让体脂率输入影响结果。
        body_fat_pct = min(max(body_fat_pct, 3), 60)
        lean_mass = weight * (1 - body_fat_pct / 100)
        protein_g = lean_mass * 2.2

        # 脂肪：占总卡路里的20%（每克脂肪9千卡）
        fat_g = target_calories * 0.20 / 9

        # 碳水：剩余卡路里给碳水（每克碳水4千卡）
        protein_cal = protein_g * 4
        fat_cal = fat_g * 9
        carb_cal = target_calories - protein_cal - fat_cal
        carb_g = carb_cal / 4

        return {
            'calories': target_calories,
            'protein': round(protein_g, 1),
            'fat': round(fat_g, 1),
            'carbs': round(carb_g, 1)
        }

    def create_weekly_plan(self, base_macros, training_days=4):
        """创建周碳循环计划"""
        days = ['周一', '周二', '周三', '周四', '周五', '周六', '周日']
        plan = []

        carb_weights = {
            'high': 1.4,
            'moderate': 1.0,
            'low': 0.6
        }
        day_types = [
            self.get_day_type(i, training_days, days)
            for i in range(len(days))
        ]
        total_weight = sum(carb_weights[day_type] for day_type in day_types)
        weekly_base_carbs = base_macros['carbs'] * len(days)

        # 只重新分配碳水，保证一周总碳水和目标热量接近 base_macros。
        for day, day_type in zip(days, day_types):
            carbs = weekly_base_carbs * carb_weights[day_type] / total_weight

            if day_type == 'high':
                note = "高碳日（训练日）- 补充肌糖原"
            elif day_type == 'moderate':
                note = "中碳日（维持）"
            else:
                note = "低碳日（燃脂）- 提高脂肪氧化"

            total_cal = base_macros['protein'] * 4 + base_macros['fat'] * 9 + carbs * 4

            plan.append({
                'day': day,
                'type': day_type,
                'calories': round(total_cal, 0),
                'protein': base_macros['protein'],
                'fat': base_macros['fat'],
                'carbs': round(carbs, 1),
                'note': note
            })

        return plan

    def get_day_type(self, day_index, training_days, days):
        """确定每天的碳水类型"""
        training_patterns = {
            3: [0, 2, 4],
            4: [0, 2, 4, 5],
            5: [0, 1, 2, 4, 5],
            6: [0, 1, 2, 3, 4, 5]
        }
        training_indices = training_patterns.get(training_days, training_patterns[4])

        if day_index in training_indices:
            return 'high'
        elif day_index in [(i + 1) % 7 for i in training_indices]:
            return 'moderate'
        else:
            return 'low'


class MainWindow(QMainWindow):
    """主窗口"""

    def __init__(self):
        super().__init__()
        self.calculator = CarbCyclingCalculator()
        self.init_ui()

    def init_ui(self):
        """初始化UI"""
        self.setWindowTitle('碳循环饮食计划生成器 v1.0')
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
        personal_group = QGroupBox('个人信息')
        personal_layout = QVBoxLayout()

        # 第一行：姓名、性别、年龄
        row1 = QHBoxLayout()

        self.name_input = QLineEdit()
        self.name_input.setPlaceholderText('输入姓名')

        self.gender_combo = QComboBox()
        self.gender_combo.addItems(['男', '女'])

        self.age_input = QLineEdit()
        self.age_input.setPlaceholderText('年龄（岁）')

        row1.addWidget(QLabel('姓名：'))
        row1.addWidget(self.name_input)
        row1.addWidget(QLabel('性别：'))
        row1.addWidget(self.gender_combo)
        row1.addWidget(QLabel('年龄：'))
        row1.addWidget(self.age_input)

        # 第二行：身高、体重、体脂率
        row2 = QHBoxLayout()

        self.height_input = QLineEdit()
        self.height_input.setPlaceholderText('身高（cm）')

        self.weight_input = QLineEdit()
        self.weight_input.setPlaceholderText('体重（kg）')

        self.body_fat_input = QLineEdit()
        self.body_fat_input.setPlaceholderText('体脂率（%）')
        self.body_fat_input.setText('20')

        row2.addWidget(QLabel('身高：'))
        row2.addWidget(self.height_input)
        row2.addWidget(QLabel('体重：'))
        row2.addWidget(self.weight_input)
        row2.addWidget(QLabel('体脂率：'))
        row2.addWidget(self.body_fat_input)

        personal_layout.addLayout(row1)
        personal_layout.addLayout(row2)
        personal_group.setLayout(personal_layout)
        layout.addWidget(personal_group)

        # 训练信息组
        training_group = QGroupBox('训练信息')
        training_layout = QVBoxLayout()

        row3 = QHBoxLayout()

        self.training_years_input = QLineEdit()
        self.training_years_input.setPlaceholderText('训练年限（年）')

        self.training_intensity_combo = QComboBox()
        self.training_intensity_combo.addItems(['低强度', '中强度', '高强度'])

        self.training_days_combo = QComboBox()
        self.training_days_combo.addItems(['3天/周', '4天/周', '5天/周', '6天/周'])

        row3.addWidget(QLabel('训练年限：'))
        row3.addWidget(self.training_years_input)
        row3.addWidget(QLabel('训练强度：'))
        row3.addWidget(self.training_intensity_combo)
        row3.addWidget(QLabel('训练频率：'))
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

        row4.addWidget(QLabel('日常活动水平：'))
        row4.addWidget(self.activity_combo)

        training_layout.addLayout(row3)
        training_layout.addLayout(row4)
        training_group.setLayout(training_layout)
        layout.addWidget(training_group)

        # 目标选择
        goal_group = QGroupBox('目标选择')
        goal_layout = QHBoxLayout()

        self.goal_combo = QComboBox()
        self.goal_combo.addItems(['减脂', '维持', '增肌'])

        goal_layout.addWidget(QLabel('主要目标：'))
        goal_layout.addWidget(self.goal_combo)

        goal_group.setLayout(goal_layout)
        layout.addWidget(goal_group)

        # 生成按钮
        generate_btn = QPushButton('生成饮食计划')
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
        result_group = QGroupBox('计算结果')
        result_layout = QVBoxLayout()

        self.result_text = QTextEdit()
        self.result_text.setReadOnly(True)
        self.result_text.setMaximumHeight(150)

        result_layout.addWidget(self.result_text)
        result_group.setLayout(result_layout)
        layout.addWidget(result_group)

        layout.addStretch()
        self.tabs.addTab(input_widget, '📝 信息输入')

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
        self.plan_table.setHorizontalHeaderLabels(
            ['日期', '类型', '卡路里', '蛋白质', '脂肪', '碳水']
        )

        # 设置表头样式
        header = self.plan_table.horizontalHeader()
        header.setSectionResizeMode(QHeaderView.ResizeMode.Stretch)

        plan_layout.addWidget(self.plan_table)
        plan_group.setLayout(plan_layout)
        layout.addWidget(plan_group)

        # 宏量营养素说明
        note_group = QGroupBox('计划说明')
        note_layout = QVBoxLayout()

        note_text = QTextEdit()
        note_text.setReadOnly(True)
        note_text.setMaximumHeight(200)
        note_text.setPlainText("""
碳循环饮食说明：

🔴 高碳日（High Carb）：
  - 适合训练日，特别是高强度训练
  - 碳水占每日摄入的 45-50%
  - 有助于补充肌糖原，提升训练表现
  - 建议在训练前后摄入复合碳水

🟡 中碳日（Moderate Carb）：
  - 适合中低强度训练日
  - 碳水占每日摄入的 30-35%
  - 维持能量平衡

🟢 低碳日（Low Carb）：
  - 适合休息日或轻度活动日
  - 碳水占每日摄入的 10-15%
  - 促进脂肪氧化，提高胰岛素敏感性
  - 多摄入蔬菜和优质脂肪
        """)

        note_layout.addWidget(note_text)
        note_group.setLayout(note_layout)
        layout.addWidget(note_group)

        self.tabs.addTab(plan_widget, '📊 饮食计划')

    def create_food_tab(self):
        """创建食物推荐页面"""
        food_widget = QWidget()
        layout = QVBoxLayout()
        food_widget.setLayout(layout)

        # 高碳日食物
        high_group = QGroupBox('🔴 高碳日推荐食物')
        high_layout = QVBoxLayout()

        high_foods = """优质碳水：燕麦、红薯、糙米、全麦面包、藜麦
  训练前后：香蕉、蜂蜜、葡萄汁
  蛋白质：鸡胸肉、鱼肉、蛋白粉
  脂肪：少量坚果、橄榄油（控制摄入）"""

        high_label = QLabel(high_foods)
        high_label.setWordWrap(True)
        high_layout.addWidget(high_label)
        high_group.setLayout(high_layout)
        layout.addWidget(high_group)

        # 中碳日食物
        mod_group = QGroupBox('🟡 中碳日推荐食物')
        mod_layout = QVBoxLayout()

        mod_foods = """碳水：少量燕麦、红薯、玉米
  蛋白质：牛肉、鸡蛋、乳清蛋白
  蔬菜：西兰花、菠菜、芦笋（大量）
  脂肪：适量牛油果、坚果"""

        mod_label = QLabel(mod_foods)
        mod_label.setWordWrap(True)
        mod_layout.addWidget(mod_label)
        mod_group.setLayout(mod_layout)
        layout.addWidget(mod_group)

        # 低碳日食物
        low_group = QGroupBox('🟢 低碳日推荐食物')
        low_layout = QVBoxLayout()

        low_foods = """碳水：尽量减少，仅从蔬菜获取
  蛋白质：高蛋白饮食，维持饱腹感
  蔬菜：绿叶蔬菜（无限量）、黄瓜、番茄
  脂肪：橄榄油、椰子油、三文鱼（可适当增加）
  避免：面包、米饭、面条、糖果、甜点"""

        low_label = QLabel(low_foods)
        low_label.setWordWrap(True)
        low_layout.addWidget(low_label)
        low_group.setLayout(low_layout)
        layout.addWidget(low_group)

        layout.addStretch()
        self.tabs.addTab(food_widget, '🍎 食物推荐')

    def generate_plan(self):
        """生成饮食计划"""
        try:
            # 获取输入数据
            name = self.name_input.text() or '用户'
            gender = self.gender_combo.currentText()
            age = float(self.age_input.text())
            height = float(self.height_input.text())
            weight = float(self.weight_input.text())
            body_fat = float(self.body_fat_input.text())
            training_years = float(self.training_years_input.text())
            training_intensity = self.training_intensity_combo.currentText()
            activity_level = self.activity_combo.currentText()
            goal = self.goal_combo.currentText()
            training_days = int(self.training_days_combo.currentText()[0])

            self._validate_inputs(age, height, weight, body_fat, training_years)

            # 计算各项指标
            bmr = self.calculator.calculate_bmr(weight, height, age, gender)
            tdee = self.calculator.calculate_tdee(
                bmr, activity_level, training_years, training_intensity
            )
            macros = self.calculator.calculate_macros(tdee, goal, body_fat, weight)
            weekly_plan = self.calculator.create_weekly_plan(macros, training_days)
            weekly_avg_calories = sum(day['calories'] for day in weekly_plan) / len(weekly_plan)

            # 显示基础结果
            result = f"""
┌─────────────────────────────────────┐
│  {name} 的代谢数据                    │
├─────────────────────────────────────┤
│  基础代谢率 (BMR): {bmr:.0f} 千卡      │
│  每日总消耗 (TDEE): {tdee:.0f} 千卡   │
│  目标摄入: {macros['calories']:.0f} 千卡 │
│  周计划日均: {weekly_avg_calories:.0f} 千卡 │
├─────────────────────────────────────┤
│  蛋白质: {macros['protein']}g/天      │
│  脂肪: {macros['fat']}g/天            │
│  碳水: {macros['carbs']}g/天          │
└─────────────────────────────────────┘
            """.strip()
            self.result_text.setText(result)

            # 更新表格
            self.plan_table.setRowCount(len(weekly_plan))
            type_colors = {
                'high': '#ffebee',      # 浅红
                'moderate': '#fff8e1',  # 浅黄
                'low': '#e8f5e9'        # 浅绿
            }

            for row, day_plan in enumerate(weekly_plan):
                self.plan_table.setItem(row, 0, QTableWidgetItem(day_plan['day']))
                self.plan_table.setItem(row, 1, QTableWidgetItem(day_plan['note']))
                self.plan_table.setItem(row, 2, QTableWidgetItem(f"{day_plan['calories']:.0f}"))
                self.plan_table.setItem(row, 3, QTableWidgetItem(f"{day_plan['protein']}g"))
                self.plan_table.setItem(row, 4, QTableWidgetItem(f"{day_plan['fat']}g"))
                self.plan_table.setItem(row, 5, QTableWidgetItem(f"{day_plan['carbs']}g"))

                # 设置行颜色
                color = type_colors.get(day_plan['type'], '#ffffff')
                for col in range(6):
                    self.plan_table.item(row, col).setBackground(
                        self._hex_to_qcolor(color)
                    )

            # 切换到计划页面
            self.tabs.setCurrentIndex(1)

            QMessageBox.information(
                self, '生成成功', f'已为 {name} 生成碳循环饮食计划！'
            )

        except ValueError as e:
            message = str(e) or '请确保所有数字字段输入正确！'
            QMessageBox.warning(
                self, '输入错误', message
            )
        except Exception as e:
            QMessageBox.critical(
                self, '错误', f'生成计划时出错：{str(e)}'
            )

    def _hex_to_qcolor(self, hex_color):
        """将十六进制颜色转换为QColor"""
        from PyQt6.QtGui import QColor
        return QColor(hex_color)

    def _validate_inputs(self, age, height, weight, body_fat, training_years):
        """校验输入范围，防止明显不合理的数据进入计算。"""
        checks = [
            (10 <= age <= 100, '年龄应在 10-100 岁之间。'),
            (100 <= height <= 230, '身高应在 100-230 cm 之间。'),
            (30 <= weight <= 250, '体重应在 30-250 kg 之间。'),
            (3 <= body_fat <= 60, '体脂率应在 3%-60% 之间。'),
            (0 <= training_years <= 80, '训练年限应在 0-80 年之间。')
        ]
        for valid, message in checks:
            if not valid:
                raise ValueError(message)


def main():
    app = QApplication(sys.argv)

    # 设置应用样式
    app.setStyle('Fusion')

    # 创建并显示主窗口
    window = MainWindow()
    window.show()

    sys.exit(app.exec())


if __name__ == '__main__':
    main()
