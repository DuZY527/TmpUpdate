from service.load.load_service import CalcLoadService


def test_diff_days():
    days = CalcLoadService().diff_day("2021-01-01", "2021-01-15")
    assert days == 14

