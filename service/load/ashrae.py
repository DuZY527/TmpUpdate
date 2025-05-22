import os

import xlwt

from service.load import consts


class AshraeService:
    """
    egqr.xls 文件处理
    """
    def __init__(self):
        pass

    def data_remode(self):
        province = []
        city = []
        apartmentfilenamelist = [''] * 500
        hotelfilenamelist = [''] * 500
        officefilenamelist = [''] * 500
        restaurantfilenamelist = [''] * 500
        for parent, dirnames, filenames in os.walk(consts.CONST_ASHRAE_DATA_DIR):
            for filename in filenames:
                data = filename.split('_')
                # ASHRAE9012016_RestaurantFastFood_Denver_CHN_Henan.Xinyang.572970_CSWD
                type = data[1]
                location = data[4]
                data1 = location.split('.')
                if data1[0] == 'Nei':
                    province0 = data1[0] + '.' + data1[1]
                    city0 = data1[2]
                else:
                    province0 = data1[0]
                    city0 = data1[1]
                if city.count(city0) == 0:
                    province.append(province0)
                    city.append(city0)
                suoyin = city.index(city0)
                if type == "RestaurantFastFood":
                    restaurantfilenamelist[suoyin] = filename
                elif type == "OfficeMedium":
                    officefilenamelist[suoyin] = filename
                elif type == "HotelSmall":
                    hotelfilenamelist[suoyin] = filename
                elif type == "ApartmentHighRise":
                    apartmentfilenamelist[suoyin] = filename
        return province, city, restaurantfilenamelist, officefilenamelist, hotelfilenamelist, apartmentfilenamelist

    def reindex_ashrae(self):
        """
        8760 个 热、电 等数据 by 地区
        Returns:
        """
        province, city, restaurantfilenamelist, officefilenamelist, hotelfilenamelist, apartmentfilenamelist = self.data_remode()
        wb = xlwt.Workbook()
        total = wb.add_sheet('egqr')
        for i in range(len(province)):
            total.write(i, 0, province[i])
            total.write(i, 1, city[i])
            total.write(i, 2, restaurantfilenamelist[i])
            total.write(i, 3, officefilenamelist[i])
            total.write(i, 4, hotelfilenamelist[i])
            total.write(i, 5, apartmentfilenamelist[i])
        wb.save(consts.CONST_ASHRAE_INDEX_FILENAME)
        return 0

    def exec(self):
        self.reindex_ashrae()
