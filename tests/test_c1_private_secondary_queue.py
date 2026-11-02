from __future__ import annotations

from scripts.constituent_weekly.build_c1_private_secondary_queue import (
    REFERENCE_COUNT, SECONDARY_CLASSES,
)


def test_secondary_queue_scope_is_exact_remaining_catalogue_classes():
    assert SECONDARY_CLASSES == {"buyback", "agm_or_other"}


def test_secondary_queue_reference_count_is_49():
    assert REFERENCE_COUNT == 49
