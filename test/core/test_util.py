from core.utils import num_hour_of_year, num_hour_of_year_v1


def test_num_hour_v1():
    num = num_hour_of_year_v1(2025, 7, 7)

    print(num)
    assert num == 4488


def test_num_hour():
    num = num_hour_of_year("2025-07-07")

    print(num)
    assert num == 4488