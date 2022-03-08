#!/usr/bin/env python3
# -*- coding: utf-8 -*-
# Copyright (C) 2019 tribe29 GmbH - License: GNU General Public License v2
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


def discover_ubiquiti_airos_link(section):
    print(f"discovery for airos_wireless_link: {section}")
    yield Service()


def check_ubiquiti_airos_link(section):
    msg = ""
    
    print(f"check for airos_wireless_link: {section}")

    if len(section) == 0:
        yield Result(state=State.UNKNOWN, notice="No AP data could be found")
        return
    ap_data = section.pop(0)

    try:
        ssid = ap_data[0]
        rxlevel = int(ap_data[1])
        rssi = int(ap_data[2])
        ccq = int(ap_data[3])
        noise = int(ap_data[4])
        txrate = int(ap_data[5])
        rxrate = int(ap_data[6])
        bwidth = int(ap_data[7])
        sta_count = int(ap_data[8])
        
        print(f" AP: txrate: {txrate}; rxrate: {rxrate}; rx-level {rxlevel}; noise {noise}")

    except ValueError:
        msg += f"failed to parse SNMP TXlink-speed {ap_data[4]}"
        return

    yield Metric(name="if_out_bps", value=txrate)
    yield Metric(name="if_in_bps", value=rxrate)
    yield Metric(name="input_signal_power_dbm", value=rxlevel)
    yield Metric(name="noise_level_dbm", value=noise)
    yield Metric(name="rssi", value=rssi)
    yield Metric(name="ccq", value=ccq)

    yield Result(state=State.OK, summary=f"AP is up with SSID {ssid}, {sta_count} stations connected {msg}")
    return

register.snmp_section(
    name = "snmp_ubiquiti_airos_wifilink_link_info",
    detect = all_of(
        startswith(".1.3.6.1.2.1.1.9.1.3.5", "Ubiquiti Networks MIB module"),
        any_of(
            equals(".1.3.6.1.4.1.41112.1.4.1.1.2.1", "1"),  # client
            equals(".1.3.6.1.4.1.41112.1.4.1.1.2.1", "4"),  # AP-WDS-bridge
        )
    ),
    fetch = SNMPTree(
        base = '.1.3.6.1.4.1.41112.1.4.5.1',
        oids = [
            '2',  # UBNT-AirMAX-MIB::ubntWlStatSsid
            '5',  # UBNT-AirMAX-MIB::ubntWlStatSignal
            '6',  # UBNT-AirMAX-MIB::ubntWlStatRssi
            '7',  # UBNT-AirMAX-MIB::ubntWlStatCcq
            '8',  # UBNT-AirMAX-MIB::ubntWlStatNoiseFloor
            '9',  # UBNT-AirMAX-MIB::ubntWlStatTxRate
            '10', # UBNT-AirMAX-MIB::ubntWlStatRxRate
            '14', # UBNT-AirMAX-MIB::ubntWlStatChanWidth
            '15', # UBNT-AirMAX-MIB::ubntWlStatStaCount
        ],
    ),
)

register.check_plugin(
    name="ubnt_airos_wireless_link",
    service_name="ubiquiti_airos_wifilink_link_service",
    sections=["snmp_ubiquiti_airos_wifilink_link_info"],
    discovery_function=discover_ubiquiti_airos_link,
    check_function=check_ubiquiti_airos_link,
)
