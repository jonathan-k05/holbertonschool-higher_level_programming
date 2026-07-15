import os

PROJECT_ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))


def test_index_html_exists():
    assert os.path.exists(os.path.join(PROJECT_ROOT, "index.html"))


def test_app_js_exists():
    assert os.path.exists(os.path.join(PROJECT_ROOT, "app.js"))


def test_style_css_exists():
    assert os.path.exists(os.path.join(PROJECT_ROOT, "style.css"))
