"""
DateCalc.py 網羅的テストスイート
=================================
テストグループ:
  A. parse_year              ─ 年文字列のパース
  B. parse_month_or_day      ─ 月・日文字列のパース
  C. is_valid_date           ─ 日付の存在チェック
  D. historical_to_proleptic ─ 歴史年代 → 天文年代変換
  E. _is_leap                ─ 閏年判定
  F. _proleptic_date         ─ ordinal 計算（紀元前）
  G. _weekday_proleptic      ─ 紀元前日付の曜日
  H. get_weekday             ─ date オブジェクトの曜日
  I. diff_days               ─ 日数差
  J. describe_diff           ─ 差分テキスト生成
  K. format_year_label       ─ 年ラベル整形
  L. calculate               ─ メイン計算ロジック（統合）
  M. 履歴管理                 ─ 重複除去・上限管理
"""

import sys
import unittest
from datetime import date, timedelta

# テスト対象モジュールをインポート
sys.path.insert(0, "/mnt/user-data/outputs")
from DateCalc import (
    parse_year,
    parse_month_or_day,
    is_valid_date,
    historical_to_proleptic,
    _is_leap,
    _proleptic_date,
    _weekday_proleptic,
    _ProlepticDate,
    get_weekday,
    diff_days,
    describe_diff,
    format_year_label,
    calculate,
    MAX_HISTORY,
    WEEKDAYS,
)

# テスト全体で使う固定の「今日」（実行日に依存しないよう固定値を使用）
FIXED_TODAY = date(2026, 5, 21)  # 木曜日


# ══════════════════════════════════════════════════════════════════════════════
# A. parse_year
# ══════════════════════════════════════════════════════════════════════════════
class TestParseYear(unittest.TestCase):

    # ── 正常系 ────────────────────────────────────────────────────────────────
    def test_typical_positive(self):
        self.assertEqual(parse_year("2026"), 2026)

    def test_minimum_positive(self):
        self.assertEqual(parse_year("1"), 1)

    def test_maximum_positive(self):
        self.assertEqual(parse_year("9999"), 9999)

    def test_minimum_negative(self):
        self.assertEqual(parse_year("-1"), -1)

    def test_maximum_negative(self):
        self.assertEqual(parse_year("-999"), -999)

    def test_negative_typical(self):
        self.assertEqual(parse_year("-100"), -100)

    def test_leading_trailing_spaces(self):
        """前後の空白は strip して許容する"""
        self.assertEqual(parse_year("  2026  "), 2026)

    def test_leading_trailing_spaces_negative(self):
        self.assertEqual(parse_year("  -50  "), -50)

    # ── 異常系：0年 ──────────────────────────────────────────────────────────
    def test_zero_returns_none(self):
        self.assertIsNone(parse_year("0"))

    # ── 異常系：範囲外 ───────────────────────────────────────────────────────
    def test_over_max_positive(self):
        self.assertIsNone(parse_year("10000"))

    def test_over_max_negative(self):
        self.assertIsNone(parse_year("-1000"))

    def test_exactly_one_over_max(self):
        self.assertIsNone(parse_year("10000"))

    def test_exactly_one_under_min_negative(self):
        self.assertIsNone(parse_year("-1000"))

    # ── 異常系：書式不正 ─────────────────────────────────────────────────────
    def test_empty_string(self):
        self.assertIsNone(parse_year(""))

    def test_only_spaces(self):
        self.assertIsNone(parse_year("   "))

    def test_float_string(self):
        self.assertIsNone(parse_year("2026.5"))

    def test_alpha_string(self):
        self.assertIsNone(parse_year("abc"))

    def test_leading_zero(self):
        self.assertIsNone(parse_year("0100"))

    def test_leading_zero_two_zeros(self):
        self.assertIsNone(parse_year("00"))

    def test_minus_only(self):
        self.assertIsNone(parse_year("-"))

    def test_double_minus(self):
        self.assertIsNone(parse_year("--1"))

    def test_minus_zero(self):
        self.assertIsNone(parse_year("-0"))

    def test_minus_leading_zero(self):
        self.assertIsNone(parse_year("-01"))

    def test_plus_prefix(self):
        self.assertIsNone(parse_year("+2026"))

    def test_space_in_middle(self):
        self.assertIsNone(parse_year("20 26"))

    def test_special_chars(self):
        self.assertIsNone(parse_year("2026!"))

    def test_japanese_digits(self):
        self.assertIsNone(parse_year("２０２６"))

    def test_none_type_raises(self):
        with self.assertRaises((AttributeError, TypeError)):
            parse_year(None)  # type: ignore


# ══════════════════════════════════════════════════════════════════════════════
# B. parse_month_or_day
# ══════════════════════════════════════════════════════════════════════════════
class TestParseMonthOrDay(unittest.TestCase):

    # ── 月：正常系 ────────────────────────────────────────────────────────────
    def test_month_min(self):
        self.assertEqual(parse_month_or_day("1", 1, 99), 1)

    def test_month_max(self):
        self.assertEqual(parse_month_or_day("99", 1, 99), 99)

    def test_month_typical(self):
        self.assertEqual(parse_month_or_day("3", 1, 99), 3)

    def test_day_typical(self):
        self.assertEqual(parse_month_or_day("31", 1, 99), 31)

    def test_spaces_stripped(self):
        self.assertEqual(parse_month_or_day("  5  ", 1, 99), 5)

    # ── 月・日：異常系 ────────────────────────────────────────────────────────
    def test_zero_returns_none(self):
        self.assertIsNone(parse_month_or_day("0", 1, 99))

    def test_over_max(self):
        self.assertIsNone(parse_month_or_day("100", 1, 99))

    def test_empty_string(self):
        self.assertIsNone(parse_month_or_day("", 1, 99))

    def test_negative_returns_none(self):
        self.assertIsNone(parse_month_or_day("-1", 1, 99))

    def test_leading_zero(self):
        self.assertIsNone(parse_month_or_day("01", 1, 99))

    def test_alpha_string(self):
        self.assertIsNone(parse_month_or_day("abc", 1, 99))

    def test_float_string(self):
        self.assertIsNone(parse_month_or_day("3.5", 1, 99))

    def test_japanese_digits(self):
        self.assertIsNone(parse_month_or_day("１２", 1, 99))


# ══════════════════════════════════════════════════════════════════════════════
# C. is_valid_date
# ══════════════════════════════════════════════════════════════════════════════
class TestIsValidDate(unittest.TestCase):

    # ── 正常系 ────────────────────────────────────────────────────────────────
    def test_typical(self):
        self.assertTrue(is_valid_date(2026, 5, 21))

    def test_year_1_valid(self):
        self.assertTrue(is_valid_date(1, 1, 1))

    def test_year_9999_valid(self):
        self.assertTrue(is_valid_date(9999, 12, 31))

    def test_leap_year_feb29(self):
        self.assertTrue(is_valid_date(2024, 2, 29))

    def test_century_non_leap_feb28(self):
        self.assertTrue(is_valid_date(1900, 2, 28))

    def test_400year_leap_feb29(self):
        self.assertTrue(is_valid_date(2000, 2, 29))

    def test_31day_month(self):
        self.assertTrue(is_valid_date(2026, 1, 31))

    def test_30day_month(self):
        self.assertTrue(is_valid_date(2026, 4, 30))

    def test_bc_year_neg1(self):
        """紀元前1年（天文0年）は有効"""
        self.assertTrue(is_valid_date(-1, 1, 1))

    def test_bc_year_neg999(self):
        self.assertTrue(is_valid_date(-999, 6, 15))

    def test_bc_leap_year(self):
        """天文0年（BC1年）は400の倍数なので閏年"""
        self.assertTrue(is_valid_date(-1, 2, 29))

    # ── 異常系：0年 ──────────────────────────────────────────────────────────
    def test_year_zero(self):
        self.assertFalse(is_valid_date(0, 1, 1))

    # ── 異常系：月範囲外 ─────────────────────────────────────────────────────
    def test_month_zero(self):
        self.assertFalse(is_valid_date(2026, 0, 1))

    def test_month_13(self):
        self.assertFalse(is_valid_date(2026, 13, 1))

    def test_month_negative(self):
        self.assertFalse(is_valid_date(2026, -1, 1))

    # ── 異常系：日範囲外 ─────────────────────────────────────────────────────
    def test_day_zero(self):
        self.assertFalse(is_valid_date(2026, 1, 0))

    def test_day_32(self):
        self.assertFalse(is_valid_date(2026, 1, 32))

    def test_feb29_non_leap(self):
        self.assertFalse(is_valid_date(2025, 2, 29))

    def test_feb29_century_non_leap(self):
        self.assertFalse(is_valid_date(1900, 2, 29))

    def test_feb30(self):
        self.assertFalse(is_valid_date(2024, 2, 30))

    def test_apr31(self):
        self.assertFalse(is_valid_date(2026, 4, 31))

    def test_jun31(self):
        self.assertFalse(is_valid_date(2026, 6, 31))

    def test_sep31(self):
        self.assertFalse(is_valid_date(2026, 9, 31))

    def test_nov31(self):
        self.assertFalse(is_valid_date(2026, 11, 31))


# ══════════════════════════════════════════════════════════════════════════════
# D. historical_to_proleptic
# ══════════════════════════════════════════════════════════════════════════════
class TestHistoricalToProleptic(unittest.TestCase):

    def test_positive_unchanged(self):
        self.assertEqual(historical_to_proleptic(2026), 2026)

    def test_year1_unchanged(self):
        self.assertEqual(historical_to_proleptic(1), 1)

    def test_bc1_to_astro0(self):
        self.assertEqual(historical_to_proleptic(-1), 0)

    def test_bc2_to_astro_minus1(self):
        self.assertEqual(historical_to_proleptic(-2), -1)

    def test_bc999_to_astro_minus998(self):
        self.assertEqual(historical_to_proleptic(-999), -998)


# ══════════════════════════════════════════════════════════════════════════════
# E. _is_leap
# ══════════════════════════════════════════════════════════════════════════════
class TestIsLeap(unittest.TestCase):

    def test_typical_leap(self):
        self.assertTrue(_is_leap(2024))

    def test_typical_non_leap(self):
        self.assertFalse(_is_leap(2023))

    def test_century_non_leap(self):
        self.assertFalse(_is_leap(1900))

    def test_400_year_leap(self):
        self.assertTrue(_is_leap(2000))

    def test_year_4_leap(self):
        self.assertTrue(_is_leap(4))

    def test_year_1_non_leap(self):
        self.assertFalse(_is_leap(1))

    def test_astro_year_0_leap(self):
        """天文0年（BC1）は400の倍数なので閏年"""
        self.assertTrue(_is_leap(0))

    def test_astro_year_minus4_leap(self):
        """天文-4年は4の倍数だが100の倍数でない→閏年"""
        self.assertTrue(_is_leap(-4))

    def test_astro_year_minus100_non_leap(self):
        self.assertFalse(_is_leap(-100))

    def test_astro_year_minus400_leap(self):
        self.assertTrue(_is_leap(-400))


# ══════════════════════════════════════════════════════════════════════════════
# F. _proleptic_date（ordinal 計算の正確性）
# ══════════════════════════════════════════════════════════════════════════════
class TestProlepticDate(unittest.TestCase):

    def test_year1_jan1_ordinal(self):
        """date(1,1,1).toordinal() == 1 との整合性確認"""
        result = _proleptic_date(1, 1, 1)
        self.assertEqual(result, date(1, 1, 1))

    def test_positive_year_returns_date(self):
        result = _proleptic_date(2026, 5, 21)
        self.assertEqual(result, date(2026, 5, 21))

    def test_astro_year0_jan1_ordinal(self):
        """天文0年1/1は date(1,1,1) の366日前（0年は閏年）"""
        result = _proleptic_date(0, 1, 1)
        self.assertIsInstance(result, _ProlepticDate)
        expected_ordinal = date(1, 1, 1).toordinal() - 366
        self.assertEqual(result.ordinal, expected_ordinal)

    def test_astro_year0_dec31_ordinal(self):
        """天文0年12/31は date(1,1,1) の1日前"""
        result = _proleptic_date(0, 12, 31)
        expected_ordinal = date(1, 1, 1).toordinal() - 1
        self.assertEqual(result.ordinal, expected_ordinal)

    def test_astro_year0_feb29_exists(self):
        """天文0年は閏年なので2/29が存在する"""
        result = _proleptic_date(0, 2, 29)
        self.assertIsInstance(result, _ProlepticDate)

    def test_astro_year_minus1_jan1(self):
        """天文-1年（BC2）1/1の ordinal が天文0年1/1より365日前"""
        pd0 = _proleptic_date(0, 1, 1)
        pdm1 = _proleptic_date(-1, 1, 1)
        # 天文-1年は365日（非閏年）
        self.assertFalse(_is_leap(-1))
        self.assertEqual(pd0.ordinal - pdm1.ordinal, 365)

    def test_diff_with_today_type(self):
        """_ProlepticDate と date の引き算が timedelta を返す"""
        pd = _proleptic_date(0, 1, 1)
        today = date(1, 1, 1)
        diff = today - pd
        self.assertIsInstance(diff, timedelta)
        self.assertEqual(diff.days, 366)


# ══════════════════════════════════════════════════════════════════════════════
# G. _weekday_proleptic
# ══════════════════════════════════════════════════════════════════════════════
class TestWeekdayProleptic(unittest.TestCase):

    def test_known_weekday_consistency(self):
        """
        date(1,1,1) は月曜（weekday=0, ordinal=1）。
        _ProlepticDate(ordinal=1) も同じ曜日になるべき。
        """
        pd = _ProlepticDate(1)
        self.assertEqual(_weekday_proleptic(pd), "月")

    def test_ordinal_cycle(self):
        """ordinal が 7 増えると同じ曜日"""
        pd1 = _ProlepticDate(1)
        pd2 = _ProlepticDate(8)
        self.assertEqual(_weekday_proleptic(pd1), _weekday_proleptic(pd2))

    def test_all_weekdays_covered(self):
        """ordinal 1〜7 で月〜日の全曜日が網羅されること"""
        weekdays = {_weekday_proleptic(_ProlepticDate(i)) for i in range(1, 8)}
        self.assertEqual(weekdays, set(WEEKDAYS))

    def test_negative_ordinal(self):
        """負の ordinal でもクラッシュせず有効な曜日を返す"""
        result = _weekday_proleptic(_ProlepticDate(-6))
        self.assertIn(result, WEEKDAYS)


# ══════════════════════════════════════════════════════════════════════════════
# H. get_weekday
# ══════════════════════════════════════════════════════════════════════════════
class TestGetWeekday(unittest.TestCase):

    def test_monday(self):
        self.assertEqual(get_weekday(date(2026, 5, 18)), "月")

    def test_tuesday(self):
        self.assertEqual(get_weekday(date(2026, 5, 19)), "火")

    def test_wednesday(self):
        self.assertEqual(get_weekday(date(2026, 5, 20)), "水")

    def test_thursday(self):
        self.assertEqual(get_weekday(date(2026, 5, 21)), "木")

    def test_friday(self):
        self.assertEqual(get_weekday(date(2026, 5, 22)), "金")

    def test_saturday(self):
        self.assertEqual(get_weekday(date(2026, 5, 23)), "土")

    def test_sunday(self):
        self.assertEqual(get_weekday(date(2026, 5, 24)), "日")


# ══════════════════════════════════════════════════════════════════════════════
# I. diff_days
# ══════════════════════════════════════════════════════════════════════════════
class TestDiffDays(unittest.TestCase):

    def test_same_day_zero(self):
        self.assertEqual(diff_days(FIXED_TODAY, FIXED_TODAY), 0)

    def test_future_positive(self):
        self.assertEqual(diff_days(FIXED_TODAY + timedelta(days=30), FIXED_TODAY), 30)

    def test_past_negative(self):
        self.assertEqual(diff_days(FIXED_TODAY - timedelta(days=10), FIXED_TODAY), -10)

    def test_one_day_future(self):
        self.assertEqual(diff_days(FIXED_TODAY + timedelta(1), FIXED_TODAY), 1)

    def test_one_day_past(self):
        self.assertEqual(diff_days(FIXED_TODAY - timedelta(1), FIXED_TODAY), -1)

    def test_large_future(self):
        self.assertEqual(diff_days(date(9999, 12, 31), date(1, 1, 1)),
                         date(9999, 12, 31).toordinal() - 1)


# ══════════════════════════════════════════════════════════════════════════════
# J. describe_diff
# ══════════════════════════════════════════════════════════════════════════════
class TestDescribeDiff(unittest.TestCase):

    # ── 今日 ─────────────────────────────────────────────────────────────────
    def test_today(self):
        self.assertEqual(describe_diff(0, FIXED_TODAY, FIXED_TODAY), "今日")

    # ── 365日未満：未来 ──────────────────────────────────────────────────────
    def test_1day_future(self):
        self.assertEqual(describe_diff(1, FIXED_TODAY + timedelta(1), FIXED_TODAY), "1日後")

    def test_364days_future(self):
        t = FIXED_TODAY + timedelta(364)
        self.assertEqual(describe_diff(364, t, FIXED_TODAY), "364日後")

    # ── 365日未満：過去 ──────────────────────────────────────────────────────
    def test_1day_past(self):
        self.assertEqual(describe_diff(-1, FIXED_TODAY - timedelta(1), FIXED_TODAY), "1日前")

    def test_364days_past(self):
        t = FIXED_TODAY - timedelta(364)
        self.assertEqual(describe_diff(-364, t, FIXED_TODAY), "364日前")

    # ── ちょうど365日後（1年後と端数なし） ──────────────────────────────────
    def test_exactly_365days_future(self):
        target = date(2027, 5, 21)  # 1年後（2026は閏年でない）
        diff = (target - FIXED_TODAY).days
        result = describe_diff(diff, target, FIXED_TODAY)
        self.assertIn("年", result)
        self.assertIn("後", result)

    # ── 1年ちょうど後（端数0日） ─────────────────────────────────────────────
    def test_1year_exact_future(self):
        target = date(FIXED_TODAY.year + 1, FIXED_TODAY.month, FIXED_TODAY.day)
        diff = (target - FIXED_TODAY).days
        result = describe_diff(diff, target, FIXED_TODAY)
        self.assertIn("1年", result)
        # 端数0日のとき「0日」は含まれないこと
        self.assertNotIn("0日", result)

    # ── 1年ちょうど前 ────────────────────────────────────────────────────────
    def test_1year_exact_past(self):
        target = date(FIXED_TODAY.year - 1, FIXED_TODAY.month, FIXED_TODAY.day)
        diff = (target - FIXED_TODAY).days
        result = describe_diff(diff, target, FIXED_TODAY)
        self.assertIn("1年", result)
        self.assertIn("前", result)
        self.assertNotIn("0日", result)

    # ── 複数年 + 端数日 ──────────────────────────────────────────────────────
    def test_multi_year_with_remainder(self):
        target = date(2030, 6, 15)
        diff = (target - FIXED_TODAY).days
        result = describe_diff(diff, target, FIXED_TODAY)
        self.assertIn("年", result)
        self.assertIn("日後", result)

    # ── 閏年2/29を跨ぐ1年計算 ────────────────────────────────────────────────
    def test_leap_year_feb29_future(self):
        """2028/2/29（閏日）までの差分が正しく計算される"""
        target = date(2028, 2, 29)
        diff = (target - FIXED_TODAY).days
        result = describe_diff(diff, target, FIXED_TODAY)
        self.assertIn("後", result)
        self.assertNotIn("今日", result)

    def test_from_leap_day_to_non_leap(self):
        """閏日(2/29)の翌年の同日を「1年後」として計算すると端数が生じる"""
        today_leap = date(2024, 2, 29)
        target = date(2025, 3, 1)
        diff = (target - today_leap).days  # 366日後
        result = describe_diff(diff, target, today_leap)
        self.assertIn("年", result)

    # ── 過去の複数年 ─────────────────────────────────────────────────────────
    def test_26years_past(self):
        target = date(2000, 1, 1)
        diff = (target - FIXED_TODAY).days
        result = describe_diff(diff, target, FIXED_TODAY)
        self.assertIn("年", result)
        self.assertIn("前", result)

    # ── 境界：diff=365 ───────────────────────────────────────────────────────
    def test_boundary_365_contains_nen(self):
        """365日以上は必ず「年」表記を含む"""
        target = FIXED_TODAY + timedelta(365)
        diff = 365
        result = describe_diff(diff, target, FIXED_TODAY)
        self.assertIn("年", result)

    def test_boundary_364_no_nen(self):
        """364日以下は「年」表記を含まない"""
        target = FIXED_TODAY + timedelta(364)
        diff = 364
        result = describe_diff(diff, target, FIXED_TODAY)
        self.assertNotIn("年", result)


# ══════════════════════════════════════════════════════════════════════════════
# K. format_year_label
# ══════════════════════════════════════════════════════════════════════════════
class TestFormatYearLabel(unittest.TestCase):

    def test_positive_year(self):
        self.assertEqual(format_year_label(2026), "2026")

    def test_year_1(self):
        self.assertEqual(format_year_label(1), "1")

    def test_year_9999(self):
        self.assertEqual(format_year_label(9999), "9999")

    def test_bc_year_neg1(self):
        self.assertEqual(format_year_label(-1), "紀元前1")

    def test_bc_year_neg100(self):
        self.assertEqual(format_year_label(-100), "紀元前100")

    def test_bc_year_neg999(self):
        self.assertEqual(format_year_label(-999), "紀元前999")


# ══════════════════════════════════════════════════════════════════════════════
# L. calculate（統合テスト）
# ══════════════════════════════════════════════════════════════════════════════
class TestCalculate(unittest.TestCase):

    # ── 今日 ─────────────────────────────────────────────────────────────────
    def test_today_cls_and_diff(self):
        r = calculate(2026, 5, 21, FIXED_TODAY)
        self.assertTrue(r["ok"])
        self.assertEqual(r["cls"], "today")
        self.assertEqual(r["diff"], 0)
        self.assertEqual(r["diff_label"], "今日")

    def test_today_date_label(self):
        r = calculate(2026, 5, 21, FIXED_TODAY)
        self.assertIn("2026年5月21日", r["date_label"])
        self.assertIn("木", r["date_label"])

    # ── 未来 ─────────────────────────────────────────────────────────────────
    def test_future_cls(self):
        r = calculate(2026, 6, 1, FIXED_TODAY)
        self.assertTrue(r["ok"])
        self.assertEqual(r["cls"], "future")
        self.assertGreater(r["diff"], 0)

    def test_future_1day(self):
        r = calculate(2026, 5, 22, FIXED_TODAY)
        self.assertTrue(r["ok"])
        self.assertEqual(r["diff"], 1)
        self.assertEqual(r["diff_label"], "1日後")

    def test_far_future(self):
        r = calculate(9999, 12, 31, FIXED_TODAY)
        self.assertTrue(r["ok"])
        self.assertEqual(r["cls"], "future")

    # ── 過去 ─────────────────────────────────────────────────────────────────
    def test_past_cls(self):
        r = calculate(2026, 5, 20, FIXED_TODAY)
        self.assertTrue(r["ok"])
        self.assertEqual(r["cls"], "past")
        self.assertLess(r["diff"], 0)

    def test_past_1day(self):
        r = calculate(2026, 5, 20, FIXED_TODAY)
        self.assertEqual(r["diff"], -1)
        self.assertEqual(r["diff_label"], "1日前")

    def test_far_past(self):
        r = calculate(1, 1, 1, FIXED_TODAY)
        self.assertTrue(r["ok"])
        self.assertEqual(r["cls"], "past")

    # ── 閏年 ─────────────────────────────────────────────────────────────────
    def test_leap_feb29_valid(self):
        r = calculate(2024, 2, 29, FIXED_TODAY)
        self.assertTrue(r["ok"])
        self.assertIn("2024年2月29日", r["date_label"])

    def test_non_leap_feb29_invalid(self):
        r = calculate(2025, 2, 29, FIXED_TODAY)
        self.assertFalse(r["ok"])
        self.assertIn("存在しません", r["error"])

    def test_400year_leap_feb29_valid(self):
        r = calculate(2000, 2, 29, FIXED_TODAY)
        self.assertTrue(r["ok"])

    def test_100year_non_leap_feb29_invalid(self):
        r = calculate(1900, 2, 29, FIXED_TODAY)
        self.assertFalse(r["ok"])

    # ── 月末境界 ─────────────────────────────────────────────────────────────
    def test_jan31_valid(self):
        self.assertTrue(calculate(2026, 1, 31, FIXED_TODAY)["ok"])

    def test_jan32_invalid(self):
        self.assertFalse(calculate(2026, 1, 32, FIXED_TODAY)["ok"])

    def test_apr30_valid(self):
        self.assertTrue(calculate(2026, 4, 30, FIXED_TODAY)["ok"])

    def test_apr31_invalid(self):
        self.assertFalse(calculate(2026, 4, 31, FIXED_TODAY)["ok"])

    def test_feb28_non_leap_valid(self):
        self.assertTrue(calculate(2025, 2, 28, FIXED_TODAY)["ok"])

    def test_feb30_invalid(self):
        self.assertFalse(calculate(2026, 2, 30, FIXED_TODAY)["ok"])

    # ── 月・日の範囲外 ───────────────────────────────────────────────────────
    def test_month0_invalid(self):
        self.assertFalse(calculate(2026, 0, 1, FIXED_TODAY)["ok"])

    def test_month13_invalid(self):
        self.assertFalse(calculate(2026, 13, 1, FIXED_TODAY)["ok"])

    def test_day0_invalid(self):
        self.assertFalse(calculate(2026, 1, 0, FIXED_TODAY)["ok"])

    # ── 年の境界 ─────────────────────────────────────────────────────────────
    def test_year0_invalid(self):
        r = calculate(0, 1, 1, FIXED_TODAY)
        self.assertFalse(r["ok"])

    def test_year1_valid(self):
        self.assertTrue(calculate(1, 1, 1, FIXED_TODAY)["ok"])

    def test_year9999_valid(self):
        self.assertTrue(calculate(9999, 12, 31, FIXED_TODAY)["ok"])

    # ── 紀元前 ───────────────────────────────────────────────────────────────
    def test_bc1_valid(self):
        r = calculate(-1, 1, 1, FIXED_TODAY)
        self.assertTrue(r["ok"])
        self.assertIn("紀元前1年", r["date_label"])
        self.assertEqual(r["cls"], "past")

    def test_bc1_label_contains_bc(self):
        r = calculate(-1, 6, 15, FIXED_TODAY)
        self.assertTrue(r["ok"])
        self.assertIn("紀元前1", r["date_label"])

    def test_bc999_valid(self):
        r = calculate(-999, 1, 1, FIXED_TODAY)
        self.assertTrue(r["ok"])
        self.assertIn("紀元前999年", r["date_label"])

    def test_bc1_leap_feb29(self):
        """BC1（天文0年）は閏年なので2/29が有効"""
        r = calculate(-1, 2, 29, FIXED_TODAY)
        self.assertTrue(r["ok"])

    def test_bc2_non_leap_feb29(self):
        """BC2（天文-1年）は非閏年なので2/29が無効"""
        r = calculate(-2, 2, 29, FIXED_TODAY)
        self.assertFalse(r["ok"])

    # ── 曜日の正確性 ─────────────────────────────────────────────────────────
    def test_weekday_monday(self):
        r = calculate(2026, 5, 18, FIXED_TODAY)
        self.assertIn("月", r["date_label"])

    def test_weekday_sunday(self):
        r = calculate(2026, 5, 24, FIXED_TODAY)
        self.assertIn("日", r["date_label"])

    def test_weekday_saturday(self):
        r = calculate(2026, 5, 23, FIXED_TODAY)
        self.assertIn("土", r["date_label"])

    # ── diff_label の内容検証 ────────────────────────────────────────────────
    def test_large_future_diff_label_has_nen(self):
        r = calculate(2030, 1, 1, FIXED_TODAY)
        self.assertIn("年", r["diff_label"])
        self.assertIn("後", r["diff_label"])

    def test_large_past_diff_label_has_nen(self):
        r = calculate(2000, 1, 1, FIXED_TODAY)
        self.assertIn("年", r["diff_label"])
        self.assertIn("前", r["diff_label"])

    def test_small_future_diff_label_no_nen(self):
        r = calculate(2026, 6, 1, FIXED_TODAY)
        self.assertNotIn("年", r["diff_label"])
        self.assertIn("後", r["diff_label"])

    # ── ok=False 時に必須キーが存在する ──────────────────────────────────────
    def test_error_result_has_ok_false(self):
        r = calculate(2026, 2, 30, FIXED_TODAY)
        self.assertIn("ok", r)
        self.assertFalse(r["ok"])

    def test_error_result_has_error_key(self):
        r = calculate(2026, 2, 30, FIXED_TODAY)
        self.assertIn("error", r)
        self.assertIsNotNone(r["error"])

    # ── ok=True 時に必須キーが揃っている ────────────────────────────────────
    def test_ok_result_has_all_keys(self):
        r = calculate(2026, 5, 21, FIXED_TODAY)
        for key in ("ok", "date_label", "diff", "diff_label", "cls"):
            self.assertIn(key, r)

    def test_cls_values_are_valid(self):
        for (y, m, d), expected_cls in [
            ((2026, 5, 21), "today"),
            ((2026, 5, 22), "future"),
            ((2026, 5, 20), "past"),
        ]:
            with self.subTest(date=(y, m, d)):
                r = calculate(y, m, d, FIXED_TODAY)
                self.assertEqual(r["cls"], expected_cls)


# ══════════════════════════════════════════════════════════════════════════════
# M. 履歴管理（main() のロジックを単体で再現してテスト）
# ══════════════════════════════════════════════════════════════════════════════
class TestHistoryManagement(unittest.TestCase):
    """
    main() 内の履歴操作を直接テスト。
    ロジック: history = [new] + [h for h in history if h["date_label"] != new["date_label"]]
              history = history[:MAX_HISTORY]
    """

    @staticmethod
    def _add_to_history(history: list, result: dict) -> list:
        """main() 内の履歴追加ロジックを再現"""
        history = [result] + [h for h in history if h["date_label"] != result["date_label"]]
        return history[:MAX_HISTORY]

    def _make_result(self, label: str) -> dict:
        return {
            "ok": True,
            "date_label": label,
            "diff": 1,
            "diff_label": "1日後",
            "cls": "future",
        }

    def test_first_entry_added(self):
        h = []
        h = self._add_to_history(h, self._make_result("A"))
        self.assertEqual(len(h), 1)
        self.assertEqual(h[0]["date_label"], "A")

    def test_newest_at_head(self):
        h = []
        h = self._add_to_history(h, self._make_result("A"))
        h = self._add_to_history(h, self._make_result("B"))
        self.assertEqual(h[0]["date_label"], "B")

    def test_duplicate_removed_and_moved_to_head(self):
        h = []
        h = self._add_to_history(h, self._make_result("A"))
        h = self._add_to_history(h, self._make_result("B"))
        h = self._add_to_history(h, self._make_result("A"))  # 再登録
        self.assertEqual(h[0]["date_label"], "A")
        self.assertEqual(len(h), 2)  # 重複は除去されて2件

    def test_max_history_limit(self):
        h = []
        for i in range(MAX_HISTORY + 3):
            h = self._add_to_history(h, self._make_result(f"entry_{i}"))
        self.assertEqual(len(h), MAX_HISTORY)

    def test_oldest_dropped_when_over_limit(self):
        h = []
        for i in range(MAX_HISTORY + 1):
            h = self._add_to_history(h, self._make_result(f"entry_{i}"))
        labels = [e["date_label"] for e in h]
        self.assertNotIn("entry_0", labels)

    def test_clear_history(self):
        h = []
        h = self._add_to_history(h, self._make_result("A"))
        h.clear()
        self.assertEqual(len(h), 0)

    def test_error_result_not_added(self):
        """ok=False の結果は履歴に追加されないこと（main()側の if result["ok"] チェック）"""
        h = []
        error_result = {"ok": False, "error": "この日付は存在しません"}
        if error_result["ok"]:
            h = self._add_to_history(h, error_result)
        self.assertEqual(len(h), 0)

    def test_exact_max_history_no_drop(self):
        h = []
        for i in range(MAX_HISTORY):
            h = self._add_to_history(h, self._make_result(f"entry_{i}"))
        self.assertEqual(len(h), MAX_HISTORY)


# ══════════════════════════════════════════════════════════════════════════════
# エントリポイント
# ══════════════════════════════════════════════════════════════════════════════
if __name__ == "__main__":
    loader = unittest.TestLoader()
    loader.sortTestMethodsUsing = None  # 定義順を維持
    suite = unittest.TestSuite()
    for cls in [
        TestParseYear,
        TestParseMonthOrDay,
        TestIsValidDate,
        TestHistoricalToProleptic,
        TestIsLeap,
        TestProlepticDate,
        TestWeekdayProleptic,
        TestGetWeekday,
        TestDiffDays,
        TestDescribeDiff,
        TestFormatYearLabel,
        TestCalculate,
        TestHistoryManagement,
    ]:
        suite.addTests(loader.loadTestsFromTestCase(cls))

    runner = unittest.TextTestRunner(verbosity=2, stream=sys.stdout)
    result = runner.run(suite)
    sys.exit(0 if result.wasSuccessful() else 1)
