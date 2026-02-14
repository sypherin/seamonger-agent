from src.db import FishermanMemory
from src.models import Fisherman


def test_fisherman_memory_upsert_and_get(tmp_path):
    db_path = tmp_path / "test.db"
    memory = FishermanMemory(str(db_path))

    memory.upsert_fisherman(Fisherman("+6591234567", "bawal", 0.6))
    row = memory.get_fisherman("+6591234567")

    assert row is not None
    assert row.fisherman_id == "+6591234567"
    assert row.specialty == "bawal"
    assert row.reliability_score == 0.6
