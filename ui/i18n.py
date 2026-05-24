"""UI 文案集中。

集中管理所有显示给用户的字符串，便于后续添加英文等其它语言版本。
"""

# 窗口和标签页
WINDOW_TITLE = '碳循环饮食计划生成器 v1.1'
TAB_INPUT = '📝 信息输入'
TAB_PLAN = '📊 饮食计划'
TAB_FOOD = '🍎 食物推荐'

# 输入页分组
GROUP_PERSONAL = '个人信息'
GROUP_TRAINING = '训练信息'
GROUP_GOAL = '目标选择'
GROUP_RESULT = '计算结果'

# 输入页字段标签
LABEL_NAME = '姓名：'
LABEL_GENDER = '性别：'
LABEL_AGE = '年龄：'
LABEL_HEIGHT = '身高：'
LABEL_WEIGHT = '体重：'
LABEL_BODY_FAT = '体脂率：'
LABEL_TRAINING_YEARS = '训练年限：'
LABEL_TRAINING_INTENSITY = '训练强度：'
LABEL_TRAINING_DAYS = '训练频率：'
LABEL_ACTIVITY = '日常活动水平：'
LABEL_GOAL = '主要目标：'

# 按钮
BTN_GENERATE = '生成饮食计划'
BTN_EXPORT_CSV = '📥 导出为 CSV'

# tooltip
TIP_TRAINING_INTENSITY = (
    '指你训练时的"努力程度"。\n'
    '低强度：以适应/恢复为主，组间充分休息。\n'
    '中强度：标准抗阻或有氧训练（默认）。\n'
    '高强度：力竭组、HIIT、运动员级训练。'
)
TIP_TRAINING_DAYS = '每周到健身房或正式训练的次数'
TIP_ACTIVITY = (
    '指日常生活+训练的总活动量（用于计算 TDEE）。\n'
    '与"训练强度"不同：训练强度只描述单次训练的吃力程度；\n'
    '此处则反映你一整周的能量消耗水平，包括步行、家务、通勤等。'
)

# 占位符 / 默认值
PH_NAME = '输入姓名'

# 计划页表头
TABLE_HEADERS = ['日期', '类型', '卡路里', '蛋白质', '脂肪', '碳水']

# 计划说明
PLAN_NOTE_TEXT = """
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
"""

# 食物推荐
FOOD_HIGH_TITLE = '🔴 高碳日推荐食物'
FOOD_HIGH_TEXT = """优质碳水：燕麦、红薯、糙米、全麦面包、藜麦
  训练前后：香蕉、蜂蜜、葡萄汁
  蛋白质：鸡胸肉、鱼肉、蛋白粉
  脂肪：少量坚果、橄榄油（控制摄入）"""

FOOD_MOD_TITLE = '🟡 中碳日推荐食物'
FOOD_MOD_TEXT = """碳水：少量燕麦、红薯、玉米
  蛋白质：牛肉、鸡蛋、乳清蛋白
  蔬菜：西兰花、菠菜、芦笋（大量）
  脂肪：适量牛油果、坚果"""

FOOD_LOW_TITLE = '🟢 低碳日推荐食物'
FOOD_LOW_TEXT = """碳水：尽量减少，仅从蔬菜获取
  蛋白质：高蛋白饮食，维持饱腹感
  蔬菜：绿叶蔬菜（无限量）、黄瓜、番茄
  脂肪：橄榄油、椰子油、三文鱼（可适当增加）
  避免：面包、米饭、面条、糖果、甜点"""

# 弹窗
MSG_INPUT_ERROR_TITLE = '输入错误'
MSG_INPUT_ERROR_DEFAULT = '请确保所有数字字段输入正确！'
MSG_GENERATE_ERROR_TITLE = '错误'
MSG_GENERATE_ERROR_FMT = '生成计划时出错：{}'
MSG_GENERATE_OK_TITLE = '生成成功'
MSG_GENERATE_OK_FMT = '已为 {} 生成碳循环饮食计划！'
MSG_EXPORT_TIP = '请先生成饮食计划。'
MSG_EXPORT_OK_TITLE = '导出成功'
MSG_EXPORT_OK_FMT = '已保存到：\n{}'
MSG_EXPORT_FAIL_TITLE = '导出失败'
MSG_EXPORT_FAIL_FMT = '无法写入文件：{}'

# 默认姓名
DEFAULT_NAME = '用户'
