"""Tests for per-country lockdown/NPI controller."""

import pytest
import sys
import os

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from src.interventions.lockdown_controller import (
    CountryLockdownController, NPILevel, GlobalNPIManager,
    NPI_ESCALATION_THRESHOLDS
)


class TestCountryLockdownController:
    def test_initial_state_is_none(self):
        ctrl = CountryLockdownController("TestCountry")
        assert ctrl.current_level == NPILevel.NONE

    def test_escalation_to_mild(self):
        ctrl = CountryLockdownController("TestCountry")
        threshold = NPI_ESCALATION_THRESHOLDS[NPILevel.MILD]
        modifier = ctrl.update(0, threshold + 0.001)
        assert ctrl.current_level >= NPILevel.MILD
        assert modifier < 1.0  # R0 should be reduced

    def test_escalation_to_strict(self):
        ctrl = CountryLockdownController("TestCountry")
        threshold = NPI_ESCALATION_THRESHOLDS[NPILevel.STRICT]
        ctrl.update(0, threshold + 0.001)
        assert ctrl.current_level == NPILevel.STRICT

    def test_hysteresis_prevents_immediate_deescalation(self):
        ctrl = CountryLockdownController("TestCountry")
        # Escalate to strict
        ctrl.update(0, 0.03)
        assert ctrl.current_level == NPILevel.STRICT

        # Rate drops below strict threshold but above deescalation threshold
        deesc = NPI_ESCALATION_THRESHOLDS[NPILevel.STRICT] * 0.7
        ctrl.update(1, deesc)
        # Should still be strict (hysteresis)
        assert ctrl.current_level == NPILevel.STRICT

    def test_deescalation_below_threshold(self):
        ctrl = CountryLockdownController("TestCountry")
        # Escalate
        ctrl.update(0, 0.03)
        # Drop well below deescalation threshold
        ctrl.update(1, 0.001)
        assert ctrl.current_level < NPILevel.STRICT

    def test_compliance_decay(self):
        ctrl = CountryLockdownController("TestCountry", compliance_decay_rate=0.01)
        ctrl.update(0, 0.03)  # Enter strict lockdown

        modifier_early = ctrl.update(1, 0.03)
        for day in range(2, 50):
            modifier_late = ctrl.update(day, 0.03)

        # Later modifier should be closer to 1.0 (less effective due to compliance decay)
        assert modifier_late > modifier_early

    def test_no_lockdown_returns_1(self):
        ctrl = CountryLockdownController("TestCountry")
        modifier = ctrl.update(0, 0.0)  # No infections
        assert modifier == 1.0


class TestGlobalNPIManager:
    def test_add_and_update_countries(self):
        mgr = GlobalNPIManager()
        mgr.add_country("A")
        mgr.add_country("B")

        modifiers = mgr.update_all(0, {"A": 0.03, "B": 0.001})
        assert modifiers["A"] < 1.0  # A should have NPI
        assert modifiers["B"] == 1.0  # B should be fine

    def test_statistics(self):
        mgr = GlobalNPIManager()
        mgr.add_country("A")
        mgr.update_all(0, {"A": 0.03})
        stats = mgr.get_all_statistics()
        assert "A" in stats
