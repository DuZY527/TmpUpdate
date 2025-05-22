import csv
import os

import pandas as pd
import xlrd

from core import utils, defined
from core.utils import location_to_province, pinyin
from schema.schema_load import LoadBody
from service.load import consts
from service.load.load_service_v2 import CalcLoadServiceV2


class LoadBaseService:
    """
    公共 基类
    """
    def __init__(self):
        pass

    def fenqu(self, wei, jing):
        load_sort = 5 if jing > 106 and wei < 25 else 2
        if jing < 106:
            load_sort = 4
        if wei > 35:
            load_sort = 3
        if wei >= 40 or (jing < 101 and wei > 28):
            load_sort = 1
        return load_sort

    def gqmonthcorrectload(self, g_demand, q_demand, heat_month, cold_month):
        gn_demand = [0 for i in range(8760)]
        qn_demand = [0 for i in range(8760)]
        z_heat_month = [0 for i in range(8760)]
        z_cold_month = [0 for i in range(8760)]

        if heat_month.start == "0101" and heat_month.end == "1231":  # 全年
            z_heat_month = [1 for i in range(8760)]
            gn_demand[0:8760] = g_demand[0:8760]
        else:
            start_h_m = int(heat_month.start.split('-')[0])
            start_h_d = int(heat_month.start.split('-')[1])

            end_h_m = int(int(heat_month.end.split('-')[0]))
            end_h_d = int(int(heat_month.end.split('-')[1]))

            start_h_index = consts.m_date[start_h_m - 1] + 24 * (start_h_d - 1)
            end_h_index = consts.m_date[end_h_m - 1] + 24 * (end_h_d - 1)

            if end_h_index >= start_h_index:
                gn_demand[start_h_index:end_h_index] = g_demand[start_h_index:end_h_index]
                z_heat_month[start_h_index:end_h_index] = [1 for i in range(end_h_index - start_h_index)]
            else:
                gn_demand[0:end_h_index] = g_demand[0:end_h_index]
                gn_demand[start_h_index:8760] = g_demand[start_h_index:8760]
                z_heat_month[0:end_h_index] = [1 for i in range(end_h_index)]
                z_heat_month[start_h_index:8760] = [1 for i in range(8760 - start_h_index)]
        if cold_month.start == "0101" and cold_month.end == "1231":  # 全年
            z_cold_month = [1 for i in range(8760)]
            qn_demand[0:8760] = q_demand[0:8760]
        else:
            start_c_m = int(cold_month.start.split('-')[0])
            start_c_d = int(cold_month.start.split('-')[1])
            end_c_m = int(cold_month.end.split('-')[0])
            end_c_d = int(cold_month.end.split('-')[1])

            start_c_index = consts.m_date[start_c_m - 1] + 24 * (start_c_d - 1)
            end_c_index = consts.m_date[end_c_m - 1] + 24 * (end_c_d - 1)

            if end_c_index >= start_c_index:
                qn_demand[start_c_index:end_c_index] = q_demand[start_c_index:end_c_index]
                z_cold_month[start_c_index:end_c_index] = [1 for i in range(end_c_index - start_c_index)]
            else:
                qn_demand[0:end_c_index] = q_demand[0:end_c_index]
                qn_demand[start_c_index:8760] = q_demand[start_c_index:8760]
                z_cold_month[0:end_c_index] = [1 for i in range(end_c_index)]
                z_cold_month[start_c_index:8760] = [1 for i in range(8760 - end_c_index)]
        return gn_demand, qn_demand, z_heat_month, z_cold_month


class LoadExistedCsvService(LoadBaseService):
    """
    加载给定的csv 文件中的负荷
    不用算直接加载结果输出
    """

    def __init__(self):
        pass

    def exec(self, load: LoadBody):

        # add_eqpr()  # 生成电/热 excel文件

        load_area = load.load_area
        province = load.province
        heating_cycle = load.heating_cycle
        cooling_cycle = load.cooling_cycle
        load_sort = self.fenqu(load.location[0], load.location[1])
        df = pd.read_csv(os.path.join(consts.CONST_LOAD_DIR, load.fileaddress))  # 加载指定地区负荷
        ele_load = df['电负荷(kW)'].tolist()
        g_demand = df['热负荷(kW)'].tolist()
        q_demand = df['冷负荷(kW)'].tolist()
        steam120_demand = df['蒸汽120负荷(t)'].tolist()
        steam180_demand = df['蒸汽180负荷(t)'].tolist()
        h_demand = df['氢负荷(kg)'].tolist()
        r_r_solar, r_solar = [0 for i in range(8760)], [0 for i in range(8760)]
        book_r_solar = xlrd.open_workbook(consts.CONST_SOLAR_INDEX_FILENAME)
        data = book_r_solar.sheet_by_index(0)
        sheng = data.col_values(2, start_rowx=0, end_rowx=None)
        suoyin = sheng.index(province)
        r_solar_filename = data.cell_value(suoyin, 4)
        r_solar_dir = os.path.join(consts.CONST_SOLAR_DATA_DIR, r_solar_filename)

        # 读取solar csv 中数据
        with open(r_solar_dir) as tempreture_file:
            reader = csv.reader(tempreture_file)
            column = [row for row in reader]

        for i in range(8760):
            if float(column[i + 4][2]) * 1759.6 / 1321.728 < 1:
                r_solar[i] = float(column[i + 4][2])
            else:
                r_solar[i] = float(column[i + 4][2])
        r_solar = r_solar[-8:] + r_solar[:-8]

        g_demand, q_demand, z_heat_mounth, z_cold_month = self.gqmonthcorrectload(g_demand, q_demand,
                                                                                  heating_cycle, cooling_cycle)

        # return ele_load, g_demand, q_demand, r_solar, z_heat_mounth, z_cold_month, load_sort
        return_load = {'power_load': ele_load,
                       'heating_demand': g_demand,
                       'cooling_demand': q_demand,
                       'h2_demand': h_demand,
                       'steam120_demand': steam120_demand,
                       'steam180_demand': steam180_demand,
                       'r_solar': r_solar,
                       'r_r_solar': r_solar,
                       'load_sort': load_sort,
                       'z_cold_month': z_cold_month,
                       'z_heat_month': z_heat_mounth}
        return return_load


class CalcLoadService(LoadBaseService):
    """
    实际计算负荷需求
    """
    def __init__(self):
        pass

    def get_load_area(self, load: LoadBody):
        # fenqu()
        if load.province != "":
            province, city = load.province, load.city
        # 如果只有经纬度
        else:
            location = load.location
            province, city = location_to_province(location[0], location[1])
            print(province, city)
            i = 0
            while city == '0' and i < 20:
                province, city = location_to_province(location[0], location[1])
                i = i + 1
            if city == '0' and i > 19:
                raise Exception("网络异常，请修改配置文件增加city")

        pinprovince = pinyin(province)[0:-5]
        pincity = pinyin(city)[0:-3]
        pinprovince = pinprovince.capitalize()
        pincity = pincity.capitalize()
        if province == "陕西省":
            pinprovince = "Shaanxi"
        elif province == "北京市":
            pinprovince = "Beijing"
        elif province == "重庆市":
            pinprovince = "Chongqing"
        elif province == "天津市":
            pinprovince = "Tianjin"
        elif province == "西藏自治区":
            pinprovince = "Tibet"
        elif province == "广西壮族自治区":
            pinprovince = "Guangxi"
        elif province == "新疆维吾尔自治区":
            pinprovince = "Xinjiang"
        elif province == "宁夏回族自治区":
            pinprovince = "Ningxia"
        elif province == "内蒙古自治区":
            pinprovince = "Nei.Mongol"
        elif province == "新疆维吾尔自治区":
            pinprovince = "Xinjiang"
        elif province == "上海市":
            pinprovince = "Shanghai"

        return province, city, pinprovince, pincity

    def find_province_name(self, pinprovince, pincity):
        book = xlrd.open_workbook('egqr.xls')
        data = book.sheet_by_index(0)
        sheng = data.col_values(0, start_rowx=0, end_rowx=None)
        shi = data.col_values(1, start_rowx=0, end_rowx=None)
        suoyin = sheng.index(pinprovince)
        restaurantfilename = data.cell_value(suoyin, 2)
        officefilename = data.cell_value(suoyin, 3)
        hotelfilename = data.cell_value(suoyin, 4)
        apartmentfilename = data.cell_value(suoyin, 5)
        return restaurantfilename, officefilename, hotelfilename, apartmentfilename

    def calc_other_load(self, load: LoadBody):
        power = [0] * 8760
        heating = [0] * 8760
        cooling = [0] * 8760
        h2 = [0] * 8760
        steam120 = [0] * 8760
        steam180 = [0] * 8760
        for other in load.other_load:
            if not other.flag:
                print(f"No used other load name: {other.name}")
                continue
            else:
                diff_days = utils.diff_day(other.start_time, other.end_time)
                # 工业电负荷周期循环:在规定的时间内循环，代码意思是：每年有工业用电的时间段的电负荷 = 用户提供的电负荷*用电时间段内循环次数 + 非整除部分的电负荷
                demand8760 = [0] * 8760
                c_l = other.circle_load
                start = utils.num_hour_of_year(other.start_time)
                end = utils.num_hour_of_year(other.end_time)
                demand8760[start:end] = (c_l * (diff_days * 24 // len(c_l)) + c_l[:int(diff_days * 24 % len(c_l))])
            if other.type == defined.OtherLoadType.Power:
                power = [x + y for x, y in zip(power, demand8760)]
            elif other.type == defined.OtherLoadType.Cooling:
                cooling = [x + y for x, y in zip(cooling, demand8760)]
            elif other.type == defined.OtherLoadType.Heating:
                heating = [x + y for x, y in zip(heating, demand8760)]
            elif other.type == defined.OtherLoadType.H2:
                h2 = [x + y for x, y in zip(h2, demand8760)]
            elif other.type == defined.OtherLoadType.Steam120:
                steam120 = [x + y for x, y in zip(steam120, demand8760)]
            elif other.type == defined.OtherLoadType.Steam180:
                steam180 = [x + y for x, y in zip(steam180, demand8760)]
            else:
                raise Exception(f"No used other load type: {other.type}")

        return power, heating, cooling, h2, steam120, steam180

    def baseautoload(self, province, pinprovince, pincity, building_area, load_area, ele_load_area, g_load_area,
                     q_load_area):
        ele_load = [0 for i in range(8760)]
        g_demand = [0 for i in range(8760)]
        q_demand = [0 for i in range(8760)]
        r_ele_load, o_ele_load, h_ele_load, a_ele_load = [0 for i in range(8760)], [0 for i in range(8760)], [0 for i in
                                                                                                              range(
                                                                                                                  8760)], [
            0 for i in range(8760)]
        r_g_demand, o_g_demand, h_g_demand, a_g_demand = [0 for i in range(8760)], [0 for i in range(8760)], [0 for i in
                                                                                                              range(
                                                                                                                  8760)], [
            0 for i in range(8760)]
        r_q_demand, o_q_demand, h_q_demand, a_q_demand = [0 for i in range(8760)], [0 for i in range(8760)], [0 for i in
                                                                                                              range(
                                                                                                                  8760)], [
            0 for i in range(8760)]
        r_r_solar, r_solar = [0 for i in range(8760)], [0 for i in range(8760)]
        # r_r_solar,o_r_solar,h_r_solar,a_r_solar= [0 for i in range(8760)],[0 for i in range(8760)],[0 for i in range(8760)],[0 for i in range(8760)]
        s_all = float(building_area['apartment']) + float(building_area['hotel']) + float(
            building_area['office']) + float(building_area['restaurant'])
        s_apartment = float(building_area['apartment']) / s_all
        s_hotel = float(building_area['hotel']) / s_all
        s_office = float(building_area['office']) / s_all
        s_restaurant = float(building_area['restaurant']) / s_all
        restaurantfilename, officefilename, hotelfilename, apartmentfilename = self.find_province_name(pinprovince,
                                                                                                       pincity)
        with open(os.path.join(consts.CONST_ASHRAE_DATA_DIR, restaurantfilename)) as restaurantcsv:
            restaurant = csv.DictReader(restaurantcsv)
            i = 0
            for row in restaurant:
                r_ele_load[i] = float(row["Electricity Load [kwh]"])
                r_g_demand[i] = float(row["Heating Load [kwh]"])
                r_q_demand[i] = float(row["Cooling Load [kwh]"])
                r_r_solar[i] = float(row["Environment:Site Direct Solar Radiation Rate per Area [W/m2](Hourly)"])
                i += 1
        with open(os.path.join(consts.CONST_ASHRAE_DATA_DIR, officefilename)) as officecsv:
            office = csv.DictReader(officecsv)
            i = 0
            for row1 in office:
                o_ele_load[i] = float(row1["Electricity Load [kwh]"])
                o_g_demand[i] = float(row1["Heating Load [kwh]"])
                o_q_demand[i] = float(row1["Cooling Load [kwh]"])
                # o_r_solar[i] = float(row1["Environment:Site Direct Solar Radiation Rate per Area [W/m2](Hourly)"])
                i += 1
        with open(os.path.join(consts.CONST_ASHRAE_DATA_DIR, hotelfilename)) as hotelcsv:
            hotel = csv.DictReader(hotelcsv)
            i = 0
            for row2 in hotel:
                h_ele_load[i] = float(row2["Electricity Load [kwh]"])
                h_g_demand[i] = float(row2["Heating Load [kwh]"])
                h_q_demand[i] = float(row2["Cooling Load [kwh]"])
                # h_r_solar[i] = float(row2["Environment:Site Direct Solar Radiation Rate per Area [W/m2](Hourly)"])
                i += 1
        with open(os.path.join(consts.CONST_ASHRAE_DATA_DIR, apartmentfilename)) as apartmentcsv:
            apartment = csv.DictReader(apartmentcsv)
            i = 0
            for row3 in apartment:
                a_ele_load[i] = float(row3["Electricity Load [kwh]"])
                a_g_demand[i] = float(row3["Heating Load [kwh]"])
                a_q_demand[i] = float(row3["Cooling Load [kwh]"])
                # a_r_solar[i] = float(row3["Environment:Site Direct Solar Radiation Rate per Area [W/m2](Hourly)"])
                i += 1
        for i in range(0, 8760):
            ele_load[i] = (a_ele_load[i] * s_apartment + h_ele_load[i] * s_hotel + o_ele_load[i] * s_office +
                           r_ele_load[i] * s_restaurant) * ele_load_area
            g_demand[i] = (a_g_demand[i] * s_apartment + h_g_demand[i] * s_hotel + o_g_demand[i] * s_office +
                           r_g_demand[i] * s_restaurant) * g_load_area
            q_demand[i] = (a_q_demand[i] * s_apartment + h_q_demand[i] * s_hotel + o_q_demand[i] * s_office +
                           r_q_demand[i] * s_restaurant) * q_load_area
            # r_solar[i] = a_r_solar[i] * s_apartment + h_r_solar[i] * s_hotel + o_r_solar[i] * s_office + r_r_solar[i] * s_restaurant

        book_r_solar = xlrd.open_workbook('r_solar.xls')
        data = book_r_solar.sheet_by_index(0)
        sheng = data.col_values(2, start_rowx=0, end_rowx=None)
        shi = data.col_values(3, start_rowx=0, end_rowx=None)
        suoyin = sheng.index(province)
        r_solar_filename = data.cell_value(suoyin, 4)
        r_solar_filepath = os.path.join(consts.CONST_SOLAR_INDEX_FILENAME, r_solar_filename)
        with open(r_solar_filepath) as tempreture_file:
            reader = csv.reader(tempreture_file)
            column = [row for row in reader]
        for i in range(8760):
            if float(column[i + 4][2]) * 1759.6 / 1321.728 < 1:
                r_solar[i] = float(column[i + 4][2])
            else:
                r_solar[i] = float(column[i + 4][2])
        r_solar = r_solar[-8:] + r_solar[:-8]
        # print(r_solar)
        return ele_load, g_demand, q_demand, r_solar, r_r_solar

    def peakbasecorrectload(self, pinprovince, base_ele_load, base_g_demand, base_q_demand, building_area, load_area,
                            ele_load_area, g_load_area, q_load_area):
        """
        TODO 没看懂，暂时注释
        :param pinprovince:
        :param base_ele_load:
        :param base_g_demand:
        :param base_q_demand:
        :param building_area:
        :param load_area:
        :param ele_load_area:
        :param g_load_area:
        :param q_load_area:
        :return:
        """
        pass
        # s_all = float(building_area['apartment']) + float(building_area['hotel']) + float(
        #     building_area['office']) + float(
        #     building_area['restaurant'])
        # s_apartment = float(building_area['apartment']) / s_all
        # s_hotel = float(building_area['hotel']) / s_all
        # s_office = float(building_area['office']) / s_all
        # s_restaurant = float(building_area['restaurant']) / s_all
        # base_e = base_apartment[0] * s_apartment + base_hotel[0] * s_hotel + base_office[0] * s_office + \
        #          base_restaurant[0] * s_restaurant
        # base_g = base_apartment[1] * s_apartment + base_hotel[1] * s_hotel + base_office[1] * s_office + \
        #          base_restaurant[1] * s_restaurant
        # base_q = base_apartment[2] * s_apartment + base_hotel[2] * s_hotel + base_office[2] * s_office + \
        #          base_restaurant[2] * s_restaurant
        # sum_e_cankao = base_e * ele_load_area / 1000
        # sum_g_cankao = base_g * g_load_area / 1000 * theta[pinprovince][0]
        # sum_q_cankao = base_q * q_load_area / 1000 * theta[pinprovince][1]
        # print("热峰值" + str(sum_g_cankao) + "冷峰值" + str(sum_q_cankao))
        # base_ele_load, base_g_demand, base_q_demand = peakcorrectload(base_ele_load, base_g_demand, base_q_demand,
        #                                                               sum_e_cankao, sum_g_cankao, sum_q_cankao)
        # return base_ele_load, base_g_demand, base_q_demand

    def peakcorrectload(self, base_ele_load, base_g_demand, base_q_demand, peak_ele, peak_g, peak_q):
        """
        峰值矫正
        :param base_g_demand:
        :param base_q_demand:
        :param peak_ele:
        :param peak_g:
        :param peak_q:
        :return:
        """
        # ele_max , max_g , max_q = max(base_ele_load) , max(base_g_demand), max(base_q_demand)
        print("peak correct", peak_g)

        ordered_base_ele_load = sorted(base_ele_load)
        ordered_base_g_demand = sorted(base_g_demand)
        ordered_base_q_demand = sorted(base_q_demand)
        ele_max = ordered_base_ele_load[8740]
        max_g = ordered_base_g_demand[8740]
        max_q = ordered_base_q_demand[8740]
        ele_load = [0 for i in range(8760)]
        g_demand = [0 for i in range(8760)]
        q_demand = [0 for i in range(8760)]
        for i in range(0, 8760):
            ele_load[i] = base_ele_load[i] * peak_ele / ele_max
            if max_g == 0:
                g_demand[i] = 0
            else:
                # g_demand[i] = np.sqrt(base_g_demand[i] * peak_g / max_g)* np.sqrt(peak_g)
                g_demand[i] = base_g_demand[i] * peak_g / max_g
                if g_demand[i] > peak_g:
                    g_demand[i] = peak_g
                # if g_demand[i] < peak_g*0.7:
                #     g_demand[i] = g_demand[i] * 1.42
            if max_q == 0:
                q_demand[i] = 0
            else:
                # q_demand[i] = np.sqrt(base_q_demand[i] * peak_q / max_q)* np.sqrt(peak_q)
                q_demand[i] = base_q_demand[i] * peak_q / max_q
                if q_demand[i] > peak_q:
                    q_demand[i] = peak_q
                # if q_demand[i] < peak_q*0.5:
                #     q_demand[i] = q_demand[i] * 1.2
        return ele_load, g_demand, q_demand

    def _industrial(self, filename, model, ele_load_industrial):
        book = xlrd.open_workbook(os.path.join(consts.CONST_INDUSTRIAL_DIR, filename))
        data = book.sheet_by_index(0)
        for l in range(1, data.nrows):
            ele_load_industrial.append(data.cell(l, 0).value)
        ele_load_industrial = ele_load_industrial * 8
        ele_load_industrial = ele_load_industrial[0: 8760]
        if model[0] == 1:
            ordered_ele_load_industrial = sorted(ele_load_industrial)
            ele_max = ordered_ele_load_industrial[8000]
            for i in range(8760):
                ele_load_industrial[i] = ele_load_industrial[i] * model[1] / ele_max
        elif model[0] == 2:
            all_ele = sum(ele_load_industrial)
            for i in range(8760):
                ele_load_industrial[i] = ele_load_industrial[i] * model[1] / all_ele

    def industrial(self, industrial_mode):
        ele_load_industrial = []

        self._industrial("单峰.xlsx", industrial_mode.single_peak, ele_load_industrial)
        self._industrial("双峰.xlsx", industrial_mode.double_peak, ele_load_industrial)
        self._industrial("午间低谷.xlsx", industrial_mode.midday_trough, ele_load_industrial)
        self._industrial("相对均匀.xlsx", industrial_mode.relatively_uniform, ele_load_industrial)
        self._industrial("夜间用能.xlsx", industrial_mode.nighttime_energy_usage, ele_load_industrial)
        # TODO 验证下是否return的是正确的。
        return ele_load_industrial

    def sumcorrectload(self, base_ele_load, base_g_demand, base_q_demand, sum_ele, sum_g, sum_q):
        all_ele, all_g, all_q = sum(base_ele_load), sum(base_g_demand), sum(base_q_demand)
        ele_load = [0 for i in range(8760)]
        g_demand = [0 for i in range(8760)]
        q_demand = [0 for i in range(8760)]
        for i in range(0, 8760):
            if all_ele == 0:
                ele_load[i] = 0
            else:
                ele_load[i] = base_ele_load[i] * sum_ele / all_ele
            if all_g == 0:
                g_demand[i] = 0
            else:
                g_demand[i] = base_g_demand[i] * sum_g / all_g
            if all_q == 0:
                q_demand[i] = 0
            else:
                q_demand[i] = base_q_demand[i] * sum_q / all_q
        print(sum(ele_load), sum(g_demand), sum(q_demand))
        return ele_load, g_demand, q_demand

    def exec(self, load: LoadBody):
        global total_power_demand, total_heating_demand, total_cooling_demand, industrial_power_demand

        province, city, pinyin_province, pinyin_city = self.get_load_area(load)

        load_sort = self.fenqu(load.location[0], load.location[1])
        # 1. base_load 基础 冷热电计算
        base_power_demand = [0] * 8760
        base_heating_demand = [0] * 8760
        base_cooling_demand = [0] * 8760
        r_solar = [0] * 8760
        r_r_solar = [0] * 8760
        z_heat_month = [0] * 8760
        z_cold_month = [0] * 8760
        for one in load.cooling_heating_power:
            # TODO 基础负荷
            # v2 = CalcLoadServiceV2(one)
            # result = v2.exec()
            # _base_cooling_demand = result['cooling_heating_power']
            #
            # for index in range(8760):
            #     base_power_demand[index] = _base_power_demand[index] + base_power_demand[index]
            #     base_heating_demand[index] = _base_heating_demand[index] + base_heating_demand[index]
            #     base_cooling_demand[index] = _base_cooling_demand + base_cooling_demand[index]
            #     r_solar[index] = _r_solar[index] + r_solar[index]
            #     r_r_solar[index] = _r_r_solar[index] + r_r_solar[index]
            #     z_heat_month[index] = _z_heat_month[index] + z_heat_month[index]
            #     z_cold_month[index] = _z_cold_month[index] + z_cold_month[index]
           pass

        # 2.industrial load 如果工业有用能且不输入详细的周期性负荷，则自动生成工业的电负荷，没有对应的热负荷和冷负荷
        if load.industrial_load.flag:
            industrial_power_demand = self.industrial(load.industrial_load.industrial_mode)

        # 3. other load 如果工业有用能且输入详细的周期性负荷，则自动生成工业的电负荷，热负荷和冷负荷
        other_power_demand, other_heating_demand, other_cooling_demand, h_demand, steam120_demand, steam180_demand = self.calc_other_load(
            load)

        # 4. total = base_load + industrial_load + other_load
        for index in range(8760):
            _industrial_power_load = 0 if not load.industrial_load.flag else industrial_power_demand[index]
            total_power_demand = base_power_demand[index] + other_power_demand[index] + _industrial_power_load
            total_heating_demand = base_heating_demand[index] + other_heating_demand[index]
            total_cooling_demand = base_cooling_demand[index] + other_cooling_demand[index]

        total_load = {'power_load': total_power_demand,
                      'heating_demand': total_heating_demand,
                      'cooling_demand': total_cooling_demand,
                      'h2_demand': h_demand,
                      'steam120_demand': steam120_demand,
                      'steam180_demand': steam180_demand,
                      'r_solar': r_solar,
                      'r_r_solar': r_r_solar,
                      'load_sort': load_sort,
                      'z_cold_month': z_cold_month,
                      'z_heat_month': z_heat_month
                      }

        return total_load


class LoadService:
    """
    主要入口处理
    """
    def __init__(self):
        self.load_existed_csv_service = LoadExistedCsvService()
        pass

    def load_existed_csv(self, load: LoadBody):
        result = self.load_existed_csv_service.exec(load)
        return result

    def calc_based_config(self, load: LoadBody):

        """
        根据json输入计算负荷
        :param load:
        :return:
        """
        calc = CalcLoadService()
        result = calc.exec(load)
        return result

    def exec(self, load: LoadBody):
        if load.autoload:
            result = self.load_existed_csv(load)
        else:
            result = self.calc_based_config(load=load)

        return result
        ## TODO save the result to file or return
