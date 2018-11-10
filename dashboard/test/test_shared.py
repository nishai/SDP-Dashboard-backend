import pytest

from dashboard.shared.errors import VisibleError


def test_visible_error():
    with pytest.raises(VisibleError):
        raise VisibleError("Test Error")
