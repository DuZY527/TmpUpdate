# 太阳 数据 索引
import os.path

# 太阳辐射?
CONST_SOLAR_INDEX_FILENAME = os.path.join('resource', 'solar_index.xls')
CONST_SOLAR_DATA_DIR = os.path.join('resource', 'solar')

# 美国冷热电标准 https://baike.baidu.com/item/ASHRAE%E6%A0%87%E5%87%86/9878437
CONST_ASHRAE_INDEX_FILENAME = os.path.join('resource', 'ashrae_index.xls')
CONST_ASHRAE_DATA_DIR = os.path.join('resource', 'ashrae')

# 算好的负荷
CONST_LOAD_DIR = os.path.join('resource', 'load')

# 工业负荷计算目录
CONST_INDUSTRIAL_DIR = os.path.join('resource', 'industrial')

# 负荷V2版本依赖文件路径
CONST_IDF_DIR = os.path.join('resource', 'idf')
CONST_EPW_DIR = os.path.join('resource', 'epw')
CONST_IDD_DIR = os.path.join('resource', 'idd')

CONST_IDD_FILE = os.path.join(CONST_IDD_DIR, 'Energy+.idd')

# ???
m_date = [31, 28, 31, 30, 31, 30, 31, 31, 30, 31, 30, 31]
m_date = [sum(m_date[:i]) * 24 for i in range(12)]
m_date.append(8760)  # 每个月第一个小时的索引
base_apartment = [40, 30.48, 60.96]  # W/m2
base_hotel = [55, 33.3, 66.7]  # W/m2
base_office = [50, 38.1, 76.2]  # W/m2
base_restaurant = [60, 33.3, 66.7]  # W/m2

# 范围
ORIENTATION_RANGES = {
    "North": [(315, 360), (0, 45)],
    "East": [(45, 135)],
    "South": [(135, 225)],
    "West": [(225, 315)]
}
