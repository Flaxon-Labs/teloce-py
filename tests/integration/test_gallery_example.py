from tests.integration.test_browser_e2e import _chrome, _dump_dom
import pytest


@pytest.mark.skipif(_chrome() is None, reason="Chrome is not installed")
def test_live_gallery_mounts_compiled_vel_components():
    result = _dump_dom("http://127.0.0.1:5050/", 5000)
    assert result.returncode == 0, result.stderr
    assert "Collect the useful web." in result.stdout
    assert "Gallery could not start" not in result.stdout
    assert "Loading gallery" not in result.stdout
