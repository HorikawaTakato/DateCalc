"""
test_datecalc.py
DateCalc.py の各関数に対するユニットテスト
"""

import pytest
from datetime import date
from DateCalc import (
    get_weekday,
    is_valid_date,
    historical_to_proleptic,
    diff_days,
    describe_diff,
    format_year_label,
    parse_year,
    parse_month_or_day,
    calculate,
)


# ── get_weekday ───────────────────────────────────────────────────────────────
class TestGetWeekday:
    def test_monday(self):
        assert get_weekday(date(2025, 1, 6)) == "月"

    def test_friday(self):
        assert get_weekday(date(2025, 1, 10)) == "金"

    def test_sunday(self):
        assert get_weekday(date(2025, 1, 12)) == "日"


# ── is_valid_date ─────────────────────────────────────────────────────────────
class TestIsValidDate:
    def test_valid_date(self):
        assert is_valid_date(2025, 5, 20) is True

    def test_year_zero_is_invalid(self):
        assert is_valid_date(0, 1, 1) is False

    def test_invalid_month(self):
        assert is_valid_date(2025, 13, 1) is False

    def test_invalid_day(self):
        assert is_valid_date(2025, 1, 32) is False

    def test_leap_year_feb29(self):
        assert is_valid_date(2024, 2, 29) is True

    def test_non_leap_year_feb29(self):
        assert is_valid_date(2025, 2, 29) is False

    def test_bc_year(self):
        assert is_valid_date(-1, 1, 1) is True


# ── historical_to_proleptic ───────────────────────────────────────────────────
class TestHistoricalToProleptic:
    def test_ad_year_unchanged(self):
        assert historical_to_proleptic(2025) == 2025

    def test_bc1_to_astro0(self):
        assert historical_to_proleptic(-1) == 0

    def test_bc2_to_astro_minus1(self):
        assert historical_to_proleptic(-2) == -1


# ── diff_days ─────────────────────────────────────────────────────────────────
class TestDiffDays:
    def test_future(self):
        today = date(2025, 1, 1)
        target = date(2025, 1, 11)
        assert diff_days(target, today) == 10

    def test_past(self):
        today = date(2025, 1, 11)
        target = date(2025, 1, 1)
        assert diff_days(target, today) == -10

    def test_same_day(self):
        today = date(2025, 5, 20)
        assert diff_days(today, today) == 0


# ── describe_diff ─────────────────────────────────────────────────────────────
class TestDescribeDiff:
    def test_today(self):
        today = date(2025, 5, 20)
        assert describe_diff(0, today, today) == "今日"

    def test_future_within_365(self):
        today = date(2025, 1, 1)
        target = date(2025, 6, 1)
        result = describe_diff(diff_days(target, today), target, today)
        assert "日後" in result
        assert "年" not in result

    def test_past_within_365(self):
        today = date(2025, 6, 1)
        target = date(2025, 1, 1)
        result = describe_diff(diff_days(target, today), target, today)
        assert "日前" in result
        assert "年" not in result

    def test_future_over_365(self):
        today = date(2025, 1, 1)
        target = date(2027, 1, 1)
        result = describe_diff(diff_days(target, today), target, today)
        assert "年" in result
        assert "日後" in result

    def test_past_over_365(self):
        today = date(2027, 1, 1)
        target = date(2025, 1, 1)
        result = describe_diff(diff_days(target, today), target, today)
        assert "年" in result
        assert "日前" in result


# ── format_year_label ─────────────────────────────────────────────────────────
class TestFormatYearLabel:
    def test_ad_year(self):
        assert format_year_label(2025) == "2025"

    def test_bc_year(self):
        assert format_year_label(-100) == "紀元前100"

    def test_year_1(self):
        assert format_year_label(1) == "1"


# ── parse_year ────────────────────────────────────────────────────────────────
class TestParseYear:
    def test_valid_ad(self):
        assert parse_year("2025") == 2025

    def test_valid_bc(self):
        assert parse_year("-100") == -100

    def test_zero_is_invalid(self):
        assert parse_year("0") is None

    def test_out_of_range_large(self):
        assert parse_year("10000") is None

    def test_out_of_range_small(self):
        assert parse_year("-1000") is None

    def test_non_numeric(self):
        assert parse_year("abc") is None

    def test_empty(self):
        assert parse_year("") is None


# ── parse_month_or_day ────────────────────────────────────────────────────────
class TestParseMonthOrDay:
    def test_valid_month(self):
        assert parse_month_or_day("6", 1, 12) == 6

    def test_invalid_month_zero(self):
        assert parse_month_or_day("0", 1, 12) is None

    def test_invalid_month_over(self):
        assert parse_month_or_day("13", 1, 12) is None

    def test_valid_day(self):
        assert parse_month_or_day("31", 1, 31) == 31

    def test_non_numeric(self):
        assert parse_month_or_day("abc") is None


# ── calculate ─────────────────────────────────────────────────────────────────
class TestCalculate:
    def test_today(self):
        today = date.today()
        result = calculate(today.year, today.month, today.day, today)
        assert result["ok"] is True
        assert result["cls"] == "today"
        assert result["diff"] == 0

    def test_future(self):
        today = date(2025, 1, 1)
        result = calculate(2025, 12, 31, today)
        assert result["ok"] is True
        assert result["cls"] == "future"
        assert result["diff"] > 0

    def test_past(self):
        today = date(2025, 6, 1)
        result = calculate(2025, 1, 1, today)
        assert result["ok"] is True
        assert result["cls"] == "past"
        assert result["diff"] < 0

    def test_invalid_date(self):
        today = date(2025, 1, 1)
        result = calculate(2025, 2, 30, today)
        assert result["ok"] is False
        assert "error" in result

    def test_date_label_format(self):
        today = date(2025, 1, 1)
        result = calculate(2025, 3, 15, today)
        assert "2025" in result["date_label"]
        assert "3" in result["date_label"]
        assert "15" in result["date_label"]

    def test_bc_year(self):
        today = date(2025, 1, 1)
        result = calculate(-100, 1, 1, today)
        assert result["ok"] is True
        assert "紀元前100" in result["date_label"]
