"""用户输入模型与校验"""

from dataclasses import dataclass
from typing import List


@dataclass
class UserInput:
    """碳循环计算的全部用户输入"""
    name: str
    gender: str
    age: float
    height: float
    weight: float
    body_fat: float
    training_years: float
    training_intensity: str
    activity_level: str
    goal: str
    training_days: int

    def validate(self) -> List[str]:
        """返回所有错误信息列表；空列表表示有效"""
        errors: List[str] = []
        checks = [
            (10 <= self.age <= 100, '年龄应在 10-100 岁之间。'),
            (100 <= self.height <= 230, '身高应在 100-230 cm 之间。'),
            (30 <= self.weight <= 250, '体重应在 30-250 kg 之间。'),
            (3 <= self.body_fat <= 60, '体脂率应在 3%-60% 之间。'),
            (0 <= self.training_years <= 80, '训练年限应在 0-80 年之间。'),
            (3 <= self.training_days <= 6, '训练天数应在 3-6 天之间。'),
        ]
        for valid, message in checks:
            if not valid:
                errors.append(message)
        return errors

    def validate_or_raise(self) -> None:
        """若有错误，抛出 ValueError（合并所有错误信息）"""
        errors = self.validate()
        if errors:
            raise ValueError('\n'.join(errors))
