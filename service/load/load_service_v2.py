"""
这个版本是基于energyplus 来计算负荷叫V2版本
"""

import math
import os
import re
import tempfile
import uuid
from datetime import datetime

import pandas as pd
from eppy.modeleditor import IDF

from schema.schema_load import LoadBody, CoolingHeatingPowerV2
from service.load import consts


class CalcLoadServiceV2:
    def __init__(self, cchp: CoolingHeatingPowerV2):
        self.cchp = cchp
        self.output_directory = os.path.join(os.sep, tempfile.gettempprefix(), f"load_{uuid.uuid4()}")
        os.makedirs(self.output_directory, exist_ok=True)
        self.output_file_idf = os.path.join(self.output_directory, "modified.idf")
        self.output_file_eplusout_csv = os.path.join(self.output_directory, "eplusout.csv")
        # 结果文件
        self.result_hourly_kwh_csv = os.path.join(self.output_directory, "result_hourly_kwh_csv.csv")
        pass

    def modify_wwr_and_save(self, idf):
        surfaces = idf.idfobjects["BUILDINGSURFACE:DETAILED"]
        windows = idf.idfobjects["FENESTRATIONSURFACE:DETAILED"]

        for direction, ranges in consts.ORIENTATION_RANGES.items():
            walls = {}
            wall_area = 0.0
            win_area = 0.0
            direction_windows = []

            for s in surfaces:
                if s.Surface_Type.lower() != "wall" or s.Outside_Boundary_Condition.lower() != "outdoors":
                    continue
                azi = s.azimuth
                if any(start <= azi < end or (start > end and (azi >= start or azi < end)) for start, end in ranges):
                    walls[s.Name] = s
                    wall_area += s.area

            for w in windows:
                if w.Building_Surface_Name in walls:
                    direction_windows.append(w)
                    win_area += w.area

            if wall_area == 0 or win_area == 0:
                print(f"⚠️ {direction} 方向无有效窗墙组合，跳过")
                continue

            target_area = wall_area * getattr(self.cchp.wwrs, direction)
            scale = math.sqrt(target_area / win_area)
            print(f"{direction}：原窗墙比={win_area / wall_area:.3f}，目标={getattr(self.cchp.wwrs, direction)}，缩放={scale:.3f}")

            for w in direction_windows:
                try:
                    verts = [[float(w[f"Vertex_{i}_Xcoordinate"]), float(w[f"Vertex_{i}_Ycoordinate"]),
                              float(w[f"Vertex_{i}_Zcoordinate"])] for i in range(1, 5)]
                    center = [sum(v) / 4 for v in zip(*verts)]
                    new_verts = [[center[0] + (vx - center[0]) * scale, center[1] + (vy - center[1]) * scale,
                                  center[2] + (vz - center[2]) * scale] for vx, vy, vz in verts]
                    for i, (x, y, z) in enumerate(new_verts, start=1):
                        w[f"Vertex_{i}_Xcoordinate"] = round(x, 6)
                        w[f"Vertex_{i}_Ycoordinate"] = round(y, 6)
                        w[f"Vertex_{i}_Zcoordinate"] = round(z, 6)
                except Exception as e:
                    print(f"❌ {w.Name} 缩放失败: {e}")
        # save
        idf.savecopy(self.output_file_idf)
        return idf

    def modify_material(self, input_idf_path):
        with open(input_idf_path, 'r', encoding='utf-8') as f:
            lines = f.readlines()

        version = 9.4
        for line in lines:
            if line.strip().startswith("Version,"):
                try:
                    version = float(line.split(',')[1].strip().rstrip(';'))
                except:
                    pass
                break

        is_v24 = version >= 24.0
        thickness_idx = 3 if is_v24 else 2
        conductivity_idx = 4 if is_v24 else 3
        field_indent = "    " if is_v24 else "   "
        name_in_next_line = is_v24
        # {name:Material}
        material_dict = {m.material_name: m for m in self.cchp.materials}
        current, field_idx = None, 0
        in_block, mod_lines = False, []

        i = 0
        while i < len(lines):
            line = lines[i]
            s = line.strip()

            if s == "Material,":
                if name_in_next_line and i + 1 < len(lines):
                    name = lines[i + 1].strip().split(',')[0].strip()
                    if name in material_dict:
                        in_block, current = True, name
                        field_idx = 1
                    mod_lines.extend([line, lines[i + 1]])
                    i += 2
                    continue
                elif not name_in_next_line:
                    name = s.split(',')[1].strip()
                    if name in material_dict:
                        in_block, current = True, name
                        field_idx = 0

            if in_block:
                field_idx += 1
                if field_idx == thickness_idx:
                    val = material_dict[current].new_thickness
                    mod_lines.append(f"{field_indent}{val},{' ' * (15 - len(str(val)))}!- Thickness [m]\n")
                    i += 1
                    continue
                elif field_idx == conductivity_idx:
                    val = material_dict[current].new_conductivity
                    mod_lines.append(f"{field_indent}{val},{' ' * (15 - len(str(val)))}!- Conductivity [W/m·K]\n")
                    i += 1
                    continue
                elif s.endswith(';'):
                    in_block, current, field_idx = False, None, 0

            mod_lines.append(line)
            i += 1

        with open(self.output_file_idf, 'w', encoding='utf-8') as f:
            f.writelines(mod_lines)

    def modify_glazing(self):
        """
        修正 output_file_idf文件
        :return:
        """
        with open(self.output_file_idf, 'r', encoding='utf-8') as f:
            lines = f.readlines()

        in_block, found, field_idx = False, False, 0
        new_lines = []

        for line in lines:
            s = line.strip()
            if "WindowMaterial:SimpleGlazingSystem" in s:
                in_block = True
            elif in_block and self.cchp.glazing.glazing_name in s:
                found = True
                new_lines.append(line)
                field_idx = 0
                continue
            elif in_block and found:
                field_idx += 1
                val = [self.cchp.glazing.u, self.cchp.glazing.shgc, self.cchp.glazing.vt][field_idx - 1]
                term = ";" if field_idx == 3 else ","
                new_lines.append(f"    {val}{term}{' ' * (15 - len(str(val)))}!- field\n")
                if field_idx == 3:
                    in_block = False
                continue
            new_lines.append(line)

        with open(self.output_file_idf, 'w', encoding='utf-8') as f:
            f.writelines(new_lines)

    def setup_idf(self, epw):
        IDF.setiddname(consts.CONST_IDD_FILE)
        idf = IDF(self.output_file_idf, epw)

        timestep_objs = idf.idfobjects['Timestep']
        if not timestep_objs:
            idf.newidfobject('Timestep').Number_of_Timesteps_per_Hour = 6
        else:
            timestep_objs[0].Number_of_Timesteps_per_Hour = 6

        for name in [
            'DistrictCooling:Facility',
            'DistrictHeatingWater:Facility',
            'Electricity:Facility'
        ]:
            outvar = idf.newidfobject('Output:Variable')
            outvar.Key_Value = '*'
            outvar.Variable_Name = name
            outvar.Reporting_Frequency = 'Hourly'

        idf.newidfobject('OutputControl:Files').Output_CSV = 'Yes'
        idf.savecopy(self.output_file_idf)
        return idf

    def run_simulation(self, idf):
        idf.run(output_directory=self.output_directory)

    def extract_total_building_area(self, html_path):
        """
        从 HTML 报告中提取 Total Building Area（单位 m²）
        """
        if not os.path.exists(html_path):
            print(f"❌ 文件不存在: {html_path}")
            return None

        with open(html_path, "r", encoding="utf-8") as f:
            content = f.read()

        match = re.search(r"Total Building Area\s*</td>\s*<td[^>]*>\s*([0-9.]+)", content, re.IGNORECASE)
        if match:
            area = float(match.group(1))
            print(f"✅ 提取的 Total Building Area 为: {area:.2f} m²")
            return area
        else:
            print("❌ 未能在 HTML 中找到 Total Building Area")
            return None

    def process_eplusout_output(self):
        if not os.path.exists(self.output_file_eplusout_csv):
            print("❌ 未找到模拟输出文件")
            return

        df = pd.read_csv(self.output_file_eplusout_csv)
        df = df[['Date/Time',
                 'DistrictCooling:Facility [J](Hourly)',
                 'DistrictHeatingWater:Facility [J](Hourly)',
                 'Electricity:Facility [J](Hourly)']]

        def parse_mmdd(row):
            try:
                return datetime.strptime(row.split()[0], "%m/%d").replace(year=1900)
            except:
                return None

        df['parsed_date'] = df['Date/Time'].apply(parse_mmdd)

        c_start = datetime.strptime(self.cchp.cooling_cycle.start, "%m-%d").replace(year=1900)
        c_end = datetime.strptime(self.cchp.cooling_cycle.end, "%m-%d").replace(year=1900)
        h_start = datetime.strptime(self.cchp.heating_cycle.start, "%m-%d").replace(year=1900)
        h_end = datetime.strptime(self.cchp.heating_cycle.end, "%m-%d").replace(year=1900)

        def in_cooling(d):
            return d and c_start <= d <= c_end

        def in_heating(d):
            return d and (d <= h_end or d >= h_start)

        df['Cooling_kWh'] = df.apply(
            lambda x: x['DistrictCooling:Facility [J](Hourly)'] / 3.6e6 if in_cooling(x['parsed_date']) else 0, axis=1)
        df['Heating_kWh'] = df.apply(
            lambda x: x['DistrictHeatingWater:Facility [J](Hourly)'] / 3.6e6 if in_heating(x['parsed_date']) else 0,
            axis=1)
        df['Electricity_kWh'] = df['Electricity:Facility [J](Hourly)'] / 3.6e6

        # === 按面积比例缩放 ===
        html_path = os.path.join(self.output_directory, "eplustbl.htm")
        actual_area = self.extract_total_building_area(html_path)
        target_area = actual_area if self.cchp.target_area is None else self.cchp.target_area

        if actual_area and target_area:
            scale_factor = target_area / actual_area
            df['Cooling_kWh'] *= scale_factor
            df['Heating_kWh'] *= scale_factor
            df['Electricity_kWh'] *= scale_factor
            print(f"📐 模拟面积为 {actual_area:.2f} m²，按 {target_area:.2f} m² 缩放，比例因子为 {scale_factor:.3f}")

        df[['Date/Time', 'Cooling_kWh', 'Heating_kWh', 'Electricity_kWh']].to_csv(self.result_hourly_kwh_csv,
                                                                                  index=False)

        print(f"✅ 最终结果保存至: {self.result_hourly_kwh_csv}")

        return df[['Date/Time', 'Cooling_kWh', 'Heating_kWh', 'Electricity_kWh']].to_json()

    def exec(self):
        """
        执行入口
        :return:
        """
        _input_idf_file = os.path.join(consts.CONST_IDF_DIR, self.cchp.idf_file)
        _epw_file = os.path.join(consts.CONST_EPW_DIR, self.cchp.epw_file)
        print("exec modify_material")
        self.modify_material(_input_idf_file)
        print("exec modify_glazing")
        self.modify_glazing()
        print("exec setup_idf")
        idf = self.setup_idf(_epw_file)
        print("exec modify_wwr_and_save")
        idf = self.modify_wwr_and_save(idf)
        print("exec run_simulation")
        self.run_simulation(idf)
        print("exec process_eplusout_output")
        result = self.process_eplusout_output()
        return result


def loop_calc_load_v2(load: LoadBody):
    """
    TODO 需要集成到V1 计算负荷代码里边去，这里仅做测试
    :param load:
    :return:
    """
    results = []
    print("loop_calc_load_v2 start")
    for cchp in load.cooling_heating_power_v2:
        calc = CalcLoadServiceV2(cchp)
        result = calc.exec()
        results.append(result)

    # TODO 加和之后返回
    return results[0]
