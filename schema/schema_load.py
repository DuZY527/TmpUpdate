import json
from datetime import datetime
from typing import List, Optional

from pydantic import BaseModel, Field, field_validator


class Cycle(BaseModel):
    """
    供暖/供热周期 格式为MM-dd
    """
    start: str  # 周期开始时间
    end: str  # 周期结束时间


class Material(BaseModel):
    """
    需要修改的材料名称及其新的厚度（m）和导热系数（W/m·K）
    """
    material_name: str  # 材料名称
    new_thickness: float  # 新厚度
    new_conductivity: float  # 新导热系数


class Glazing(BaseModel):
    """
    窗户简化模型的名称及其整体热工性能参数（U值、SHGC、VT）
    """
    glazing_name: str  # 玻璃名称
    u: float  # U 值
    shgc: float  # SHGC 值
    vt: float  # VT 值


class WWRS(BaseModel):
    """
    各朝向对应的目标窗墙比（Window-to-Wall Ratio）
    """
    North: float  # 北向窗墙比
    East: float  # 东向窗墙比
    South: float  # 南向窗墙比
    West: float  # 西向窗墙比


class CoolingHeatingPowerV2(BaseModel):
    """
    EnergyPlus的版本
    路径设置：EnergyPlus 所需的 IDD、IDF、输出文件夹和气象文件
    """
    name: str  # 建筑名称
    type: str  # 建筑类型
    target_area: float  # 目标建筑面积（m²）
    idf_file: str  # IDF 文件
    epw_file: str  # EPW 文件
    heating_cycle: Optional[Cycle] = None  # 加热周期配置
    cooling_cycle: Optional[Cycle] = None  # 制冷周期配置
    materials: List[Material]  # 需要修改的材料名称及其新的厚度（m）和导热系数（W/m·K）
    glazing: Glazing  # 窗户简化模型的名称及其整体热工性能参数（U值、SHGC、VT）
    wwrs: WWRS  # 各朝向对应的目标窗墙比（Window-to-Wall Ratio）


class IndustrialMode(BaseModel):
    """
    工业用电模式
    """
    single_peak: List[float] = Field(default_factory=lambda: [0, 0])  # 单一峰谷模式
    double_peak: List[float] = Field(default_factory=lambda: [0, 0])  # 双峰谷模式
    midday_trough: List[float] = Field(default_factory=lambda: [0, 0])  # 中午低谷模式
    relatively_uniform: List[float] = Field(default_factory=lambda: [0, 0])  # 相对均匀模式
    nighttime_energy_usage: List[float] = Field(default_factory=lambda: [0, 0])  # 夜间用电模式


class IndustrialLoad(BaseModel):
    """
    工业用电负载
    """
    flag: bool = False  # 是否启用工业用电
    industrial_mode: IndustrialMode = Field(default_factory=IndustrialMode)  # 工业用电模式配置


class PowerPeak(BaseModel):
    """
    用电峰值配置
    """
    flag: bool = False  # 是否启用峰值配置
    power: float = 0.0  # 峰值功率
    heating: float = 0.0  # 加热功率
    cooling: float = 0.0  # 制冷功率


class PowerSum(BaseModel):
    """
    总用电量配置
    """
    flag: bool = False  # 是否启用总用电量配置
    power: float = 0.0  # 总功率
    heating: float = 0.0  # 总加热功率
    cooling: float = 0.0  # 总制冷功率


class CoolingHeatingPower(BaseModel):
    """
    冷热负荷配置
    """
    name: str  # 配置名称
    building_type: str  # 建筑类型
    building_area: float  # 建筑面积
    flag: bool = False  # 是否启用冷热负荷配置
    power_load_area: float = 0.0  # 功率负荷面积
    heating_load_area: float = 0.0  # 加热负荷面积
    cooling_load_area: float = 0.0  # 制冷负荷面积
    heating_cycle: Optional[Cycle] = None  # 加热周期配置
    cooling_cycle: Optional[Cycle] = None  # 制冷周期配置
    power_peak: PowerPeak = Field(default_factory=PowerPeak)  # 峰值功率配置
    power_sum: PowerSum = Field(default_factory=PowerSum)  # 总功率配置


class OtherLoad(BaseModel):
    """
    其他负载配置
    """
    id: str  # 负载ID
    name: str  # 负载名称
    flag: bool = False  # 是否启用其他负载
    start_time: str = ""  # 负载开始时间
    end_time: str = ""  # 负载结束时间
    type: str = ""  # 负载类型
    circle_load: List[float] = Field(default_factory=list)  # 圆形负载分布


class LoadBody(BaseModel):
    """
    负载配置总表
    """
    autoload: bool = False  # 是否自动加载
    fileaddress: str = ""  # 文件地址
    province: str = ""  # 省份
    city: str = ""  # 城市
    heating_cycle: Optional[Cycle] = None  # 加热周期配置
    cooling_cycle: Optional[Cycle] = None  # 制冷周期配置
    location: List[float] = Field(default_factory=lambda: [0, 0])  # 地理位置坐标
    load_area: float = 0.0  # 负载面积
    industrial_load: IndustrialLoad = Field(default_factory=IndustrialLoad)  # 工业用电负载配置
    cooling_heating_power: List[CoolingHeatingPower] = Field(default_factory=list)  # 冷热负荷配置列表
    cooling_heating_power_v2: List[CoolingHeatingPowerV2] = Field(default_factory=list)
    other_load: List[OtherLoad] = Field(default_factory=list)  # 其他负载配置列表


class LoadResponseBody(BaseModel):
    """
    响应体
    """
    # 根据TLoadRecord生成字段
    id: Optional[str] = None  # 事务ID
    status: Optional[str] = None  # 状态
    msg: Optional[str] = None  # 信息
    create_time: Optional[datetime] = None  # 创建时间，类型修改为 datetime
    refresh_time: Optional[datetime] = None  # 刷新时间，类型修改为 datetime

    request_json: Optional[dict] = None  # 请求JSON
    result_json: Optional[dict] = None  # 结果JSON
    memo: Optional[str] = None  # 备注

    @field_validator('request_json', 'result_json', mode='before')
    @classmethod
    def convert_str_to_dict(cls, value):
        if isinstance(value, str):
            try:
                return json.loads(value)
            except json.JSONDecodeError:
                pass
        return value

    @field_validator('create_time', 'refresh_time', mode='before')
    @classmethod
    def convert_datetime(cls, value):
        if isinstance(value, datetime):
            return value.strftime("%Y-%m-%d %H:%M:%S")
        return value
