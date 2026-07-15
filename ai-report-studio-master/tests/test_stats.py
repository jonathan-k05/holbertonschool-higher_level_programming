from stats import _to_float, compute_basic_stats, compute_summary_stats


def test_compute_basic_stats():
    data = [
        {"sales": 100},
        {"sales": 200},
        {"sales": 150},
        {"sales": 300},
    ]
    result = compute_basic_stats(data, "sales")
    assert result["count"] == 4
    assert result["sum"] == 750
    assert result["mean"] == 187.5
    assert result["min"] == 100
    assert result["max"] == 300


def test_compute_summary_stats():
    data = [
        {"sales": 100, "profit": 20, "region": "North"},
        {"sales": 200, "profit": 50, "region": "South"},
        {"sales": 150, "profit": 30, "region": "North"},
    ]
    result = compute_summary_stats(data)
    assert "sales" in result
    assert "profit" in result
    assert "region" not in result
    assert result["sales"]["sum"] == 450


def test_empty_data():
    assert compute_basic_stats([], "sales") == {
        "count": 0,
        "sum": 0,
        "mean": 0,
        "min": 0,
        "max": 0,
    }
    assert compute_summary_stats([]) == {}


def test_string_values_from_csv():
    data = [
        {"value": "100"},
        {"value": "200"},
        {"value": "x"},
    ]
    result = compute_basic_stats(data, "value")
    assert result["count"] == 2
    assert result["sum"] == 300
    assert result["mean"] == 150.0


def test_summary_stats_union_of_columns():
    data = [{"a": 1}, {"b": 2}]
    result = compute_summary_stats(data)
    assert "a" in result
    assert "b" in result


def test_to_float_rejects_nan_inf():
    assert _to_float("nan") is None
    assert _to_float("inf") is None
    assert _to_float(float("nan")) is None
    assert _to_float(float("inf")) is None
