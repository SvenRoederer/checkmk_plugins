#!/usr/bin/env python3
# -*- coding: utf-8 -*-
# Copyright (C) 2022 Sven Roederer - License: GNU General Public License v2
# This file is part of Checkmk (https://checkmk.com). It is subject to the terms and
# conditions defined in the file COPYING, which is part of this source code package.

from typing import TypedDict, Mapping, List, Iterable, Tuple

#from .agent_based_api.v1.type_defs import StringTable
#from .agent_based_api.v1 import register, OIDEnd, SNMPTree, startswith
from .agent_based_api.v1 import *

map_states = {
    1: (0, 'in service'),
    2: (2, 'out of service'),
    3: (2, 'failed'),
    4: (0, 'disabled'),
    5: (1, 'sorry'),
    6: (0, 'redirect'),
    7: (2, 'error message'),
}

map_summary_states = {
    0: "(.)",
    1: "(!)",
    2: "(!!)",
    3: "(?)",
}

class KempService(TypedDict, total=False):
    service_name: str
    device_state: int
    conns: int
    active_conns: int


Section = Mapping[str, KempService]


def discover_ubiquiti_airos_sta(section):
    print(f"discovery for airos_wireless_sta: {section}")
#    txrate = int(section[0][4])/8
#    print(f" txrate: {txrate}")
#    print(type(txrate))
#    print(render.networkbandwidth(txrate))
    yield Service()

def check_ubiquiti_airos_sta(section):
    print(f"check for airos_wireless_sta: {section}")
#    print(item)
#    print(params)
    txrate = -100000
    rxrate = -100000
    if len(section) > 1:
        yield Result(state=State.CRIT, notice="more than one link to APs reported")
        return
    if len(section) == 0:
        yield Result(state=State.WARN, notice="not connected to an AP.")
        return
    result = section[0]
    try:
        rxlevel = int(result[2])
        noise = int(result[3])
        ccq = int(result[4])
        txrate = int(result[5])
        rxrate = int(result[6])
        cinr = int(result[7])
        sta_tx = int(result[8]) * 1024
        sta_rx = int(result[9]) * 1024
        airtime_tx = float(result[8]) / 10
        airtime_rx = float(result[9]) /10
        print(f" Station: txrate: {sta_tx}; rxrate: {sta_rx}")
        print(f" rxlevel: {rxlevel}; noise: {noise}; CINR {cinr}")

    except ValueError:
#        yield Result(state=State.CRIT, notice=f"failed to parse SNMP TXlink-speed {section[0][4]}")
        return
    
    yield Metric(name="txCapacity", value=sta_tx)
    yield Metric(name="rxCapacity", value=sta_rx)
    yield Metric(name="input_signal_power_dbm", value=rxlevel)
    yield Metric(name="noise_level_dbm", value=noise)
    yield Metric(name="ccq", value=ccq)
    yield Metric(name="cinr_db", value=cinr)
    yield Result(state=State.OK, summary=f"connected to AP: {result[1]}")
    return

register.snmp_section(
    name = "snmp_ubiquiti_airos_wifilink_sta_info",
    detect = all_of(
        startswith(".1.3.6.1.2.1.1.9.1.3.5", "Ubiquiti Networks MIB module"),
        equals(".1.3.6.1.4.1.41112.1.4.1.1.2.1", "1"),
    ),
    fetch = SNMPTree(
        base = '.1.3.6.1.4.1.41112.1.4.7.1',
        oids = [
            '1',  # ubntStaMac
            '2',  # ubntStaName
            '3',  # ubntStaSignal
            '4',  # ubntStaNoiseFloor
            '6',  # ubntStaCcq
            '11', # ubntStaTxRate
            '12', # ubntStaRxRate
            '16', # ubntStaLocalCINR
            '17', # ubntStaTxCapacity
            '18', # ubntStaRxCapacity
            '19', # ubntStaTxAirtime
            '20', # ubntStaRxAirtime
            '21', # ubntStaTxLatency
        ],
    ),
)

register.check_plugin(
    name="ubnt_airos_wireless_sta",
    service_name="ubiquiti_airos_wifilink_sta_service",
    sections=["snmp_ubiquiti_airos_wifilink_sta_info"],
    discovery_function=discover_ubiquiti_airos_sta,
    check_function=check_ubiquiti_airos_sta,
)