from datetime import time

import pytest

from talent_id.modules.workforce.domain import Site, WorkSchedule


def test_site_requires_real_timezone() -> None:
    with pytest.raises(ValueError, match="timezone"):
        Site(name="Bogota", timezone="Not/AZone")


def test_schedule_rejects_equal_start_and_end() -> None:
    with pytest.raises(ValueError, match="cannot be equal"):
        WorkSchedule(
            name="Invalid",
            start_time=time(8, 30),
            end_time=time(8, 30),
        )
