"""Sunsynk sensor tests."""
import logging
from typing import Sequence

import pytest

from sunsynk.definitions import ALL_SENSORS, AMPS, CELSIUS, DEPRECATED, VOLT, WATT
from sunsynk.sensor import (
    FaultSensor,
    HSensor,
    InverterStateSensor,
    MathSensor,
    SDStatusSensor,
    Sensor,
    SerialSensor,
    TempSensor,
    TimeRWSensor,
    ensure_tuple,
    group_sensors,
    update_sensors,
)
from sunsynk.sunsynk import register_map

_LOGGER = logging.getLogger(__name__)


# @pytest.fixture
# def sensors():
#     """Fixture to create some sensors."""
#     yield [
#         (402, True, Sensor("6400_00262200", "s_402", "W")),
#         (3514, True, Sensor("6400_00260100", "s_3514", "W", 1000)),
#     ]


def test_sen():
    a = []
    s = Sensor(0, "S 1").append_to(a)
    h = HSensor(0, "H 1").append_to(a)
    assert a[0] is s
    assert a[1] is h
    assert s.id == "s_1"


def test_group() -> None:
    sen = [
        Sensor(10, "10"),
        Sensor(11, "11"),
        Sensor(12, "12"),
        Sensor(20, "20"),
    ]
    g = list(group_sensors(sen))
    assert g == [[10, 11, 12], [20]]


def test_all_groups() -> None:
    s = [ALL_SENSORS[s] for s in ALL_SENSORS]
    for i in range(2, 6):
        _LOGGER.warning("waste with %d gap: %s", i, waste(group_sensors(s, i)))

    grp = group_sensors(s)

    grplen = [len(i) for i in grp]

    assert grplen[:1] == [6]
    assert grplen[-1:] == [1]


def waste(groups) -> Sequence[int]:
    """Calculate amount of unused registers in this grouping."""
    return [sum(b - a for a, b in zip(g[:-1], g[1:])) for g in groups]


def test_ids() -> None:
    for name, sen in ALL_SENSORS.items():
        assert name == sen.id

        if sen.factor and sen.factor < 0 and len(sen.reg_address) > 1:
            assert False, "only single signed supported"

        if sen.id in DEPRECATED:
            continue
        assert sen.unit != AMPS or sen.name.endswith(" current")
        assert sen.unit != WATT or sen.name.endswith(" power")
        assert sen.unit != VOLT or sen.name.endswith(" voltage")
        assert sen.unit != CELSIUS or sen.name.endswith(" temperature")


def test_ensure_tuple() -> None:
    assert ensure_tuple(1) == (1,)
    assert ensure_tuple((1,)) == (1,)
    assert ensure_tuple((1, 5)) == (1, 5)
    assert ensure_tuple("a") == ("a",)


def test_signed() -> None:
    """Signed sensors have a -1 factor"""
    s = Sensor(1, "", "", factor=-1)
    assert s.reg_to_value(1) == 1
    assert s.reg_to_value(0xFFFE) == -1

    s = Sensor(1, "", "", factor=1)
    assert s.reg_to_value(1) == 1
    assert s.reg_to_value(0xFFFE) == 0xFFFE
    assert s.reg_to_value((1, 1)) == 0x10001


def test_other_sensros() -> None:
    s = TempSensor(1, "", "", 0.1)
    assert s.reg_to_value(1000) == 0

    s = SDStatusSensor(1, "", "")
    assert s.reg_to_value(1000) == "fault"
    assert s.reg_to_value(1) == "unknown 1"

    s = InverterStateSensor(1, "", "")
    assert s.reg_to_value(2) == "ok"
    assert s.reg_to_value(1) == "unknown 1"


def test_math() -> None:
    s = MathSensor((1, 2), "", "", factors=(1, -1))
    assert s.reg_to_value((1000, 800)) == 200

    with pytest.raises(AssertionError):
        MathSensor((0, 1), "", "", factors=(1))

    with pytest.raises(AssertionError):
        MathSensor((0, 1), "", "", factors="aaa")

    with pytest.raises(TypeError):
        MathSensor((0, 1), "", "")


def test_update_func() -> None:
    s = SerialSensor(1, "", "")
    regs = (0x4148, 0x3738)
    assert s.reg_to_value(regs) == "AH78"

    # s = Sensor((2, 3, 4), "serial", func=decode_serial)

    # rmap = register_map(2, regs)

    # assert s.value is None
    # update_sensors([s], rmap)
    # assert s.value is None, "no update, not enough registers"

    # rmap = register_map(2, regs + regs)
    # update_sensors([s], rmap)
    # assert s.value == "AH78AH"


def test_update_float() -> None:
    s = TempSensor(60, "two", factor=0.1)
    rmap = register_map(60, [1001])
    update_sensors([s], rmap)
    assert s.value == 0.1


def test_decode_fault() -> None:
    s = FaultSensor(1, "", "")
    regs = (0x01, 0x0, 0x0, 0x0)
    assert s.reg_to_value(regs) == "F01"
    regs = (0x02, 0x0, 0x0, 0x0)
    assert s.reg_to_value(regs) == "F02"
    regs = (0x80, 0x0, 0x0, 0x0)
    assert s.reg_to_value(regs) == "F08"

    regs = (0x0, 0x8000, 0x0, 0x0)
    assert s.reg_to_value(regs) == "F32"
    regs = (0x0, 0x0, 0x1, 0x0)
    assert s.reg_to_value(regs) == "F33"


def test_time_rw() -> None:
    s = TimeRWSensor(60, "two", factor=0.1)
    rmap = register_map(60, [300])
    update_sensors([s], rmap)
    assert s.value == "3:00"


def test_dep() -> None:
    ctl = ALL_SENSORS["grid_ct_load"]
    assert ctl.id in DEPRECATED

    ctl = ALL_SENSORS["grid_ct_power"]
    assert ctl.id not in DEPRECATED
