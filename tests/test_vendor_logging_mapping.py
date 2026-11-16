import importlib.util
from pathlib import Path


def test_vendored_logging_log_record_supports_python310_mapping():
    init_path = (
        Path(__file__).resolve().parents[1]
        / "src"
        / "review_heatmap"
        / "libaddon"
        / "_vendor"
        / "logging"
        / "__init__.py"
    )
    spec = importlib.util.spec_from_file_location("rh_vendor_logging", init_path)
    assert spec is not None and spec.loader is not None
    mod = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(mod)

    rec = mod.LogRecord("test", mod.DEBUG, "x.py", 1, "Scheduler version %s", ("v3",), None)
    assert rec.getMessage() == "Scheduler version v3"

    dict_rec = mod.LogRecord("test", mod.DEBUG, "x.py", 1, "Val %(a)s", ({"a": 42},), None)
    assert dict_rec.getMessage() == "Val 42"
