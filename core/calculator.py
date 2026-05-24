"""碳循环饮食计算核心逻辑"""

from dataclasses import dataclass, asdict, field
from typing import Any, Dict, List, Optional, Sequence, Union


@dataclass
class Macros:
    """每日宏量营养素分配"""
    calories: float
    protein: float
    fat: float
    carbs: float
    warnings: List[str] = field(default_factory=list)

    def __getitem__(self, key: str) -> Any:
        return getattr(self, key)

    def to_dict(self) -> Dict[str, Any]:
        return asdict(self)


@dataclass
class DayPlan:
    """周计划中某一天的方案"""
    day: str
    type: str
    calories: float
    protein: float
    fat: float
    carbs: float
    note: str

    def __getitem__(self, key: str) -> Any:
        return getattr(self, key)

    def to_dict(self) -> Dict[str, Any]:
        return asdict(self)


# 性别系数（Mifflin-St Jeor 公式）
GENDER_FACTORS = {
    '男': 5,
    '女': -161,
}

# 日常活动水平 → TDEE 系数
ACTIVITY_FACTORS = {
    '久坐（很少运动）': 1.2,
    '轻度活跃（每周1-3次运动）': 1.375,
    '中度活跃（每周3-5次运动）': 1.55,
    '高度活跃（每周6-7次运动）': 1.725,
    '极度活跃（高强度训练）': 1.9,
}
DEFAULT_ACTIVITY_FACTOR = 1.55

# 训练强度对 TDEE 的微调
INTENSITY_ADJUSTMENTS = {
    '低强度': -0.03,
    '中强度': 0.0,
    '高强度': 0.04,
}

# 目标 → 卡路里调整（百分比，按 TDEE 百分比缩放）
GOAL_RATIOS = {
    '减脂': -0.15,
    '维持': 0.0,
    '增肌': 0.10,
}

# 安全下限：减脂时摄入不能低于 BMR × 1.0（防止极端节食）
MIN_CALORIES_VS_BMR = 1.0

# 训练年限加成上限
MAX_TRAINING_BONUS = 0.10
TRAINING_BONUS_PER_YEAR = 0.01

# 蛋白质目标（每 kg 瘦体重的克数）
PROTEIN_PER_KG_LEAN = 2.2

# 脂肪占总热量比例（按目标）
FAT_RATIOS = {
    '减脂': 0.25,
    '维持': 0.25,
    '增肌': 0.20,
}
DEFAULT_FAT_RATIO = 0.25

# 宏量营养素的卡路里密度
KCAL_PER_G_PROTEIN = 4
KCAL_PER_G_CARB = 4
KCAL_PER_G_FAT = 9

# 体脂率边界
MIN_BODY_FAT_PCT = 3
MAX_BODY_FAT_PCT = 60

# 碳循环周计划：碳水权重
CARB_WEIGHTS = {
    'high': 1.4,
    'moderate': 1.0,
    'low': 0.6,
}

# 周计划碳水类型说明
DAY_TYPE_NOTES = {
    'high': '高碳日（训练日）- 补充肌糖原',
    'moderate': '中碳日（维持）',
    'low': '低碳日（燃脂）- 提高脂肪氧化',
}

# 周计划模式：直接预设每天的碳水类型，符合常见训练分化与休息节律
# - 3 天：周一/三/五训练，次日中碳，周末深度低碳
# - 4 天：上下分化（一二、四五），周三/六中碳，周日低碳
# - 5 天：一二三训练，周四中碳过渡，五六训练，周日深度休息
# - 6 天：周四单日中碳过渡，其余为高碳（频率过高时本不适合长期低碳）
WEEKLY_PATTERNS = {
    3: ['high', 'moderate', 'high', 'moderate', 'high', 'low', 'low'],
    4: ['high', 'high', 'moderate', 'high', 'high', 'moderate', 'low'],
    5: ['high', 'high', 'high', 'moderate', 'high', 'high', 'low'],
    6: ['high', 'high', 'high', 'moderate', 'high', 'high', 'high'],
}
DEFAULT_TRAINING_DAYS = 4

WEEK_DAYS = ['周一', '周二', '周三', '周四', '周五', '周六', '周日']


class CarbCyclingCalculator:
    """碳循环饮食计算核心逻辑"""

    def calculate_bmr(self, weight: float, height: float, age: float, gender: str) -> float:
        """使用 Mifflin-St Jeor 公式计算基础代谢率"""
        gender_factor = GENDER_FACTORS.get(gender, GENDER_FACTORS['男'])
        return (10 * weight) + (6.25 * height) - (5 * age) + gender_factor

    def calculate_tdee(
        self,
        bmr: float,
        activity_level: str,
        training_years: float,
        training_intensity: str = '中强度',
    ) -> float:
        """计算每日总能量消耗"""
        factor = ACTIVITY_FACTORS.get(activity_level, DEFAULT_ACTIVITY_FACTOR)
        training_bonus = min(MAX_TRAINING_BONUS, training_years * TRAINING_BONUS_PER_YEAR)
        intensity_adjustment = INTENSITY_ADJUSTMENTS.get(training_intensity, 0.0)
        return bmr * factor * (1 + training_bonus + intensity_adjustment)

    def calculate_macros(
        self,
        tdee: float,
        goal: str,
        body_fat_pct: float,
        weight: float,
        bmr: Optional[float] = None,
    ) -> Macros:
        """计算宏量营养素分配。

        bmr 可选；若提供则用于减脂下限保护（摄入不低于 BMR）。
        """
        ratio = GOAL_RATIOS.get(goal, 0.0)
        target_calories = tdee * (1 + ratio)

        # 减脂下限保护：摄入不应低于 BMR
        if bmr is not None:
            target_calories = max(target_calories, bmr * MIN_CALORIES_VS_BMR)

        # 蛋白质：基于瘦体重计算
        body_fat_pct = min(max(body_fat_pct, MIN_BODY_FAT_PCT), MAX_BODY_FAT_PCT)
        lean_mass = weight * (1 - body_fat_pct / 100)
        protein_g = lean_mass * PROTEIN_PER_KG_LEAN

        # 脂肪：占总卡路里固定比例（按目标调整）
        fat_ratio = FAT_RATIOS.get(goal, DEFAULT_FAT_RATIO)
        fat_g = target_calories * fat_ratio / KCAL_PER_G_FAT

        # 碳水：剩余卡路里给碳水
        protein_cal = protein_g * KCAL_PER_G_PROTEIN
        fat_cal = fat_g * KCAL_PER_G_FAT
        carb_g: float = (target_calories - protein_cal - fat_cal) / KCAL_PER_G_CARB

        warnings: List[str] = []
        if carb_g < 0:
            warnings.append(
                '蛋白与脂肪已超出目标热量；碳水钳制为 0。建议复核体脂率或目标摄入量。'
            )
            carb_g = 0.0
            target_calories = protein_cal + fat_cal

        return Macros(
            calories=target_calories,
            protein=round(protein_g, 1),
            fat=round(fat_g, 1),
            carbs=round(carb_g, 1),
            warnings=warnings,
        )

    def create_weekly_plan(
        self,
        base_macros: Union[Macros, Dict[str, Any]],
        training_days: int = DEFAULT_TRAINING_DAYS,
    ) -> List[DayPlan]:
        """创建周碳循环计划"""
        days = WEEK_DAYS
        day_types = [self.get_day_type(i, training_days, days) for i in range(len(days))]
        total_weight = sum(CARB_WEIGHTS[t] for t in day_types)
        weekly_base_carbs = max(base_macros['carbs'], 0) * len(days)

        plan: List[DayPlan] = []
        for day, day_type in zip(days, day_types):
            carbs = (
                weekly_base_carbs * CARB_WEIGHTS[day_type] / total_weight
                if total_weight else 0.0
            )
            carbs = max(carbs, 0.0)
            total_cal = (
                base_macros['protein'] * KCAL_PER_G_PROTEIN
                + base_macros['fat'] * KCAL_PER_G_FAT
                + carbs * KCAL_PER_G_CARB
            )
            plan.append(DayPlan(
                day=day,
                type=day_type,
                calories=round(total_cal, 0),
                protein=base_macros['protein'],
                fat=base_macros['fat'],
                carbs=round(carbs, 1),
                note=DAY_TYPE_NOTES[day_type],
            ))

        return plan

    def get_day_type(
        self,
        day_index: int,
        training_days: int,
        days: Optional[Sequence[str]] = None,
    ) -> str:
        """确定每天的碳水类型"""
        pattern = WEEKLY_PATTERNS.get(training_days, WEEKLY_PATTERNS[DEFAULT_TRAINING_DAYS])
        return pattern[day_index]
