"""
碳循环饮食计划计算器 - 单元测试
Unit tests for CarbCyclingCalculator
"""

import unittest
from carb_cycling import CarbCyclingCalculator


class TestCalculateBMR(unittest.TestCase):
    """测试基础代谢率（BMR）计算 - Mifflin-St Jeor 公式"""

    def setUp(self):
        self.calc = CarbCyclingCalculator()

    def test_male_bmr(self):
        """男性 BMR = 10×体重 + 6.25×身高 - 5×年龄 + 5"""
        bmr = self.calc.calculate_bmr(weight=70, height=175, age=25, gender='男')
        expected = 10 * 70 + 6.25 * 175 - 5 * 25 + 5
        self.assertAlmostEqual(bmr, expected, places=2)

    def test_female_bmr(self):
        """女性 BMR = 10×体重 + 6.25×身高 - 5×年龄 - 161"""
        bmr = self.calc.calculate_bmr(weight=55, height=165, age=23, gender='女')
        expected = 10 * 55 + 6.25 * 165 - 5 * 23 - 161
        self.assertAlmostEqual(bmr, expected, places=2)

    def test_unknown_gender_defaults_to_male(self):
        """未知性别默认使用男性系数（5）"""
        bmr = self.calc.calculate_bmr(weight=70, height=175, age=25, gender='未知')
        expected = 10 * 70 + 6.25 * 175 - 5 * 25 + 5
        self.assertAlmostEqual(bmr, expected, places=2)

    def test_bmr_positive_for_typical_values(self):
        """典型身体数据应返回正值"""
        bmr = self.calc.calculate_bmr(weight=60, height=170, age=30, gender='女')
        self.assertGreater(bmr, 0)

    def test_bmr_increases_with_weight(self):
        """体重增加 BMR 增加"""
        bmr_light = self.calc.calculate_bmr(weight=60, height=175, age=25, gender='男')
        bmr_heavy = self.calc.calculate_bmr(weight=80, height=175, age=25, gender='男')
        self.assertGreater(bmr_heavy, bmr_light)

    def test_bmr_decreases_with_age(self):
        """年龄增加 BMR 减少"""
        bmr_young = self.calc.calculate_bmr(weight=70, height=175, age=20, gender='男')
        bmr_old = self.calc.calculate_bmr(weight=70, height=175, age=50, gender='男')
        self.assertGreater(bmr_young, bmr_old)

    def test_male_higher_bmr_than_female(self):
        """同条件下男性 BMR 高于女性"""
        bmr_male = self.calc.calculate_bmr(weight=70, height=175, age=25, gender='男')
        bmr_female = self.calc.calculate_bmr(weight=70, height=175, age=25, gender='女')
        self.assertGreater(bmr_male, bmr_female)


class TestCalculateTDEE(unittest.TestCase):
    """测试每日总能量消耗（TDEE）计算"""

    def setUp(self):
        self.calc = CarbCyclingCalculator()
        self.bmr = 1700  # 固定 BMR 用于测试

    def test_sedentary_activity_factor(self):
        """久坐活动系数 1.2"""
        tdee = self.calc.calculate_tdee(self.bmr, '久坐（很少运动）', training_years=0)
        # training_bonus = min(0.1, 0*0.01) = 0
        expected = self.bmr * 1.2 * 1.0
        self.assertAlmostEqual(tdee, expected, places=2)

    def test_extreme_activity_factor(self):
        """极度活跃活动系数 1.9"""
        tdee = self.calc.calculate_tdee(self.bmr, '极度活跃（高强度训练）', training_years=0)
        expected = self.bmr * 1.9 * 1.0
        self.assertAlmostEqual(tdee, expected, places=2)

    def test_default_activity_factor(self):
        """未知活动水平默认系数 1.55"""
        tdee = self.calc.calculate_tdee(self.bmr, '未知活动', training_years=0)
        expected = self.bmr * 1.55 * 1.0
        self.assertAlmostEqual(tdee, expected, places=2)

    def test_training_years_bonus(self):
        """训练年限加成"""
        tdee_0 = self.calc.calculate_tdee(self.bmr, '中度活跃（每周3-5次运动）', training_years=0)
        tdee_5 = self.calc.calculate_tdee(self.bmr, '中度活跃（每周3-5次运动）', training_years=5)
        # training_bonus = min(0.1, 5*0.01) = 0.05
        self.assertGreater(tdee_5, tdee_0)

    def test_training_years_bonus_capped(self):
        """训练年限加成上限 10%"""
        tdee_10 = self.calc.calculate_tdee(self.bmr, '中度活跃（每周3-5次运动）', training_years=10)
        tdee_20 = self.calc.calculate_tdee(self.bmr, '中度活跃（每周3-5次运动）', training_years=20)
        # min(0.1, 10*0.01)=0.1, min(0.1, 20*0.01)=0.1, 应相同
        self.assertAlmostEqual(tdee_10, tdee_20, places=2)

    def test_tdee_greater_than_bmr(self):
        """TDEE 应始终大于 BMR"""
        for level in [
            '久坐（很少运动）',
            '轻度活跃（每周1-3次运动）',
            '中度活跃（每周3-5次运动）',
            '高度活跃（每周6-7次运动）',
            '极度活跃（高强度训练）'
        ]:
            tdee = self.calc.calculate_tdee(self.bmr, level, training_years=0)
            self.assertGreater(tdee, self.bmr, f"TDEE should > BMR for {level}")

    def test_tdee_increases_with_activity(self):
        """活动水平越高 TDEE 越大"""
        levels = [
            '久坐（很少运动）',
            '轻度活跃（每周1-3次运动）',
            '中度活跃（每周3-5次运动）',
            '高度活跃（每周6-7次运动）',
            '极度活跃（高强度训练）'
        ]
        tdees = [self.calc.calculate_tdee(self.bmr, level, training_years=0) for level in levels]
        for i in range(len(tdees) - 1):
            self.assertGreater(tdees[i + 1], tdees[i])


class TestCalculateMacros(unittest.TestCase):
    """测试宏量营养素计算"""

    def setUp(self):
        self.calc = CarbCyclingCalculator()
        self.tdee = 2500
        self.weight = 70
        self.body_fat = 20

    def test_cutting_reduces_calories(self):
        """减脂目标减少 500 千卡"""
        macros = self.calc.calculate_macros(self.tdee, '减脂', self.body_fat, self.weight)
        self.assertAlmostEqual(macros['calories'], self.tdee - 500, places=1)

    def test_maintenance_same_calories(self):
        """维持目标卡路里不变"""
        macros = self.calc.calculate_macros(self.tdee, '维持', self.body_fat, self.weight)
        self.assertAlmostEqual(macros['calories'], self.tdee, places=1)

    def test_bulking_increases_calories(self):
        """增肌目标增加 300 千卡"""
        macros = self.calc.calculate_macros(self.tdee, '增肌', self.body_fat, self.weight)
        self.assertAlmostEqual(macros['calories'], self.tdee + 300, places=1)

    def test_unknown_goal_defaults_to_maintenance(self):
        """未知目标默认维持（+0）"""
        macros = self.calc.calculate_macros(self.tdee, '未知', self.body_fat, self.weight)
        self.assertAlmostEqual(macros['calories'], self.tdee, places=1)

    def test_protein_based_on_weight(self):
        """蛋白质 = 体重 × 2.0"""
        macros = self.calc.calculate_macros(self.tdee, '维持', self.body_fat, self.weight)
        self.assertAlmostEqual(macros['protein'], self.weight * 2.0, places=1)

    def test_fat_is_20_percent_of_calories(self):
        """脂肪占总卡路里 20%（每克 9 千卡）"""
        macros = self.calc.calculate_macros(self.tdee, '维持', self.body_fat, self.weight)
        expected_fat = self.tdee * 0.20 / 9
        self.assertAlmostEqual(macros['fat'], round(expected_fat, 1), places=1)

    def test_carbs_fill_remaining_calories(self):
        """碳水 = (总卡路里 - 蛋白质卡路里 - 脂肪卡路里) / 4"""
        macros = self.calc.calculate_macros(self.tdee, '维持', self.body_fat, self.weight)
        protein_cal = macros['protein'] * 4
        fat_cal = macros['fat'] * 9
        expected_carbs = (self.tdee - protein_cal - fat_cal) / 4
        self.assertAlmostEqual(macros['carbs'], round(expected_carbs, 1), places=0)

    def test_macros_sum_to_total_calories(self):
        """宏量营养素热量之和应接近总卡路里"""
        macros = self.calc.calculate_macros(self.tdee, '维持', self.body_fat, self.weight)
        total_from_macros = macros['protein'] * 4 + macros['fat'] * 9 + macros['carbs'] * 4
        self.assertAlmostEqual(total_from_macros, macros['calories'], delta=5)

    def test_all_macros_positive(self):
        """所有宏量营养素应为正值"""
        for goal in ['减脂', '维持', '增肌']:
            macros = self.calc.calculate_macros(self.tdee, goal, self.body_fat, self.weight)
            self.assertGreater(macros['protein'], 0, f"Protein should > 0 for {goal}")
            self.assertGreater(macros['fat'], 0, f"Fat should > 0 for {goal}")
            self.assertGreater(macros['carbs'], 0, f"Carbs should > 0 for {goal}")

    def test_cutting_has_fewer_carbs_than_bulking(self):
        """减脂碳水少于增肌"""
        macros_cut = self.calc.calculate_macros(self.tdee, '减脂', self.body_fat, self.weight)
        macros_bulk = self.calc.calculate_macros(self.tdee, '增肌', self.body_fat, self.weight)
        self.assertGreater(macros_bulk['carbs'], macros_cut['carbs'])


class TestGetDayType(unittest.TestCase):
    """测试每日碳水类型判定"""

    def setUp(self):
        self.calc = CarbCyclingCalculator()
        self.days = ['周一', '周二', '周三', '周四', '周五', '周六', '周日']

    def test_4_training_days_default(self):
        """4天训练：周一(0)、周三(2)、周五(4)、周六(5) 为高碳日"""
        high_days = []
        for i in range(7):
            day_type = self.calc.get_day_type(i, training_days=4, days=self.days)
            if day_type == 'high':
                high_days.append(i)
        self.assertEqual(high_days, [0, 2, 4, 5])

    def test_3_training_days(self):
        """3天训练：前3天为高碳日"""
        high_days = []
        for i in range(7):
            day_type = self.calc.get_day_type(i, training_days=3, days=self.days)
            if day_type == 'high':
                high_days.append(i)
        self.assertEqual(high_days, [0, 2, 4])

    def test_each_day_has_valid_type(self):
        """每天类型必须是 high/moderate/low"""
        for training_days in [3, 4, 5, 6]:
            for i in range(7):
                day_type = self.calc.get_day_type(i, training_days, self.days)
                self.assertIn(day_type, ['high', 'moderate', 'low'])

    def test_moderate_day_is_day_after_training(self):
        """中碳日是训练日的次日"""
        for i in range(7):
            day_type = self.calc.get_day_type(i, training_days=4, days=self.days)
            training_indices = [0, 2, 4, 5]
            next_day_indices = [(idx + 1) % 7 for idx in training_indices]
            if i in next_day_indices and i not in training_indices:
                self.assertEqual(day_type, 'moderate')


class TestCreateWeeklyPlan(unittest.TestCase):
    """测试周碳循环计划生成"""

    def setUp(self):
        self.calc = CarbCyclingCalculator()

    def test_plan_has_7_days(self):
        """计划应包含 7 天"""
        base_macros = {'calories': 2000, 'protein': 140, 'fat': 44.4, 'carbs': 244.4}
        plan = self.calc.create_weekly_plan(base_macros, training_days=4)
        self.assertEqual(len(plan), 7)

    def test_plan_contains_all_days(self):
        """计划应包含周一到周日"""
        base_macros = {'calories': 2000, 'protein': 140, 'fat': 44.4, 'carbs': 244.4}
        plan = self.calc.create_weekly_plan(base_macros, training_days=4)
        day_names = [d['day'] for d in plan]
        expected = ['周一', '周二', '周三', '周四', '周五', '周六', '周日']
        self.assertEqual(day_names, expected)

    def test_protein_consistent_across_days(self):
        """蛋白质在所有天数中保持不变"""
        base_macros = {'calories': 2000, 'protein': 140, 'fat': 44.4, 'carbs': 244.4}
        plan = self.calc.create_weekly_plan(base_macros, training_days=4)
        proteins = [d['protein'] for d in plan]
        self.assertTrue(all(p == base_macros['protein'] for p in proteins))

    def test_fat_consistent_across_days(self):
        """脂肪在所有天数中保持不变"""
        base_macros = {'calories': 2000, 'protein': 140, 'fat': 44.4, 'carbs': 244.4}
        plan = self.calc.create_weekly_plan(base_macros, training_days=4)
        fats = [d['fat'] for d in plan]
        self.assertTrue(all(f == base_macros['fat'] for f in fats))

    def test_high_carb_day_has_most_carbs(self):
        """高碳日碳水最高"""
        base_macros = {'calories': 2000, 'protein': 140, 'fat': 44.4, 'carbs': 244.4}
        plan = self.calc.create_weekly_plan(base_macros, training_days=4)
        high_carbs = [d['carbs'] for d in plan if d['type'] == 'high']
        low_carbs = [d['carbs'] for d in plan if d['type'] == 'low']
        self.assertTrue(all(hc > lc for hc in high_carbs for lc in low_carbs))

    def test_low_carb_day_has_least_carbs(self):
        """低碳日碳水最低"""
        base_macros = {'calories': 2000, 'protein': 140, 'fat': 44.4, 'carbs': 244.4}
        plan = self.calc.create_weekly_plan(base_macros, training_days=4)
        low_carbs = [d['carbs'] for d in plan if d['type'] == 'low']
        mod_carbs = [d['carbs'] for d in plan if d['type'] == 'moderate']
        high_carbs = [d['carbs'] for d in plan if d['type'] == 'high']
        self.assertTrue(all(lc < mc for lc in low_carbs for mc in mod_carbs))
        self.assertTrue(all(lc < hc for lc in low_carbs for hc in high_carbs))

    def test_carb_multiplier_values(self):
        """碳循环倍数：高碳2x，中碳1x，低碳0.2x"""
        base_macros = {'calories': 2000, 'protein': 140, 'fat': 44.4, 'carbs': 200}
        plan = self.calc.create_weekly_plan(base_macros, training_days=4)
        for d in plan:
            if d['type'] == 'high':
                self.assertAlmostEqual(d['carbs'], 200 * 2.0, places=1)
            elif d['type'] == 'moderate':
                self.assertAlmostEqual(d['carbs'], 200 * 1.0, places=1)
            elif d['type'] == 'low':
                self.assertAlmostEqual(d['carbs'], 200 * 0.2, places=1)

    def test_calorie_values_positive(self):
        """每天卡路里应为正值"""
        base_macros = {'calories': 2000, 'protein': 140, 'fat': 44.4, 'carbs': 244.4}
        plan = self.calc.create_weekly_plan(base_macros, training_days=4)
        for d in plan:
            self.assertGreater(d['calories'], 0)

    def test_each_day_has_note(self):
        """每天都有说明文字"""
        base_macros = {'calories': 2000, 'protein': 140, 'fat': 44.4, 'carbs': 244.4}
        plan = self.calc.create_weekly_plan(base_macros, training_days=4)
        for d in plan:
            self.assertTrue(len(d['note']) > 0)

    def test_training_days_count_affects_plan(self):
        """不同训练天数产生不同计划"""
        base_macros = {'calories': 2000, 'protein': 140, 'fat': 44.4, 'carbs': 244.4}
        plan_3 = self.calc.create_weekly_plan(base_macros, training_days=3)
        plan_5 = self.calc.create_weekly_plan(base_macros, training_days=5)
        types_3 = [d['type'] for d in plan_3]
        types_5 = [d['type'] for d in plan_5]
        self.assertNotEqual(types_3, types_5)


class TestEndToEnd(unittest.TestCase):
    """端到端集成测试"""

    def setUp(self):
        self.calc = CarbCyclingCalculator()

    def test_full_pipeline_male_cutting(self):
        """男性减脂完整流程"""
        bmr = self.calc.calculate_bmr(weight=80, height=178, age=28, gender='男')
        tdee = self.calc.calculate_tdee(bmr, '中度活跃（每周3-5次运动）', training_years=3)
        macros = self.calc.calculate_macros(tdee, '减脂', 20, 80)
        plan = self.calc.create_weekly_plan(macros, training_days=4)

        self.assertGreater(bmr, 0)
        self.assertGreater(tdee, bmr)
        self.assertEqual(len(plan), 7)
        self.assertAlmostEqual(macros['calories'], tdee - 500, places=1)

    def test_full_pipeline_female_bulking(self):
        """女性增肌完整流程"""
        bmr = self.calc.calculate_bmr(weight=55, height=163, age=24, gender='女')
        tdee = self.calc.calculate_tdee(bmr, '高度活跃（每周6-7次运动）', training_years=2)
        macros = self.calc.calculate_macros(tdee, '增肌', 22, 55)
        plan = self.calc.create_weekly_plan(macros, training_days=5)

        self.assertGreater(bmr, 0)
        self.assertGreater(tdee, bmr)
        self.assertEqual(len(plan), 7)
        self.assertAlmostEqual(macros['calories'], tdee + 300, places=1)

    def test_full_pipeline_maintenance(self):
        """维持目标完整流程"""
        bmr = self.calc.calculate_bmr(weight=70, height=175, age=30, gender='男')
        tdee = self.calc.calculate_tdee(bmr, '轻度活跃（每周1-3次运动）', training_years=1)
        macros = self.calc.calculate_macros(tdee, '维持', 18, 70)
        plan = self.calc.create_weekly_plan(macros, training_days=3)

        self.assertAlmostEqual(macros['calories'], tdee, places=1)
        self.assertEqual(len(plan), 7)
        # 验证宏量营养素热量总和
        for d in plan:
            total_cal = d['protein'] * 4 + d['fat'] * 9 + d['carbs'] * 4
            self.assertAlmostEqual(total_cal, d['calories'], delta=10)


if __name__ == '__main__':
    unittest.main()
