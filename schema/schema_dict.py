from pydantic import BaseModel


class SolarIndex(BaseModel):
    """
    太阳数据 solar_index.xls
    """
    longitude: float
    latitude: float
    province: str
    city: str
    filename: str

    @classmethod
    def from_string(cls, data_string: str):
        parts = data_string.split(',')
        if len(parts) != 5:
            raise ValueError("Invalid data string format")
        return cls(
            longitude=float(parts[0]),
            latitude=float(parts[1]),
            province=parts[2],
            city=parts[3],
            filename=parts[4]
        )


# 新增 AshraeBody 类
class AshraeBody(BaseModel):
    """
    ASHRAE 数据模型
    """
    province: str
    city: str
    restaurant_fast_food: str
    office_medium: str
    hotel_small: str
    apartment_high_rise: str

    @classmethod
    def from_string(cls, data_string: str):
        parts = data_string.split(',')
        if len(parts) != 6:
            raise ValueError("Invalid data string format")
        return cls(
            province=parts[0],
            city=parts[1],
            restaurant_fast_food=parts[2],
            office_medium=parts[3],
            hotel_small=parts[4],
            apartment_high_rise=parts[5]
        )