#!/usr/bin/env python3
# -*- coding: utf-8 -*-
# Copyright (C) 2019 tribe29 GmbH - License: GNU General Public License v2
# This file is part of Checkmk (https://checkmk.com). It is subject to the terms and
# conditions defined in the file COPYING, which is part of this source code package.

from typing import TypedDict, Mapping, List, Iterable, Tuple, Dict, NamedTuple

#from .agent_based_api.v1.type_defs import StringTable
#from .agent_based_api.v1 import register, OIDEnd, SNMPTree, startswith
from .agent_based_api.v1 import *
from .agent_based_api.v1.type_defs import (
#    CheckResult,
#    DiscoveryResult,
    HostLabelGenerator,
    InventoryResult,
            )
#from .agent_based_api.v1 import HostLabel

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

class SNMPInfo(NamedTuple):
    description: str
    contact: str
    name: str
    location: str

ubntRadioMode = {
    "1" : "Station",
    "4" : "AP-WDS",
}

def host_labels(section) -> HostLabelGenerator:
#    print(f"host_labels: {section}")
    if section:
#        print(" yielding Hostlabel cmk/wireless --> ubiquiti")
        yield HostLabel("cmk/device_type", 'wireless')
        yield HostLabel('cmk/wireless_type', 'ubiquiti')

def discover_ubiquiti_airos_wireless_radio(section):
    print(f"discovery for airos_wireless_radio: {section}")
    yield Service()


def check_ubiquiti_airos_wireless_radio(section):
    print(f"check for airos_wireless_radio: {section}")
    try:
        rffreq = int(section[0][0]) * 1000000
        txlevel = int(section[0][2])
        rssiChains = [int(section[1][-1]), int(section[2][-1]) ]
        rssiAsym = rssiChains[1]-rssiChains[0]
        radioMode = section[0][3]
        print(f" radio: freq {rffreq}; TX-power {txlevel}")

    except ValueError:
#        yield Result(state=State.CRIT, notice=f"failed to parse SNMP TXlink-speed {section[0][4]}")
        return
    
    yield Metric(name="frequency", value=rffreq)
    yield Metric(name="output_signal_power_dbm", value=txlevel)
    yield Metric(name="rssi_chain_asymetry", value=rssiAsym)
    yield Result(state=State.OK, summary=f"Radio is operational in {ubntRadioMode[radioMode]} mode", details=f"Frequency: {render.frequency(rffreq)}; tx-power: {txlevel} dbm")
    return

register.snmp_section(
    name = "snmp_ubiquiti_airos_wireless_radio_info",
    detect = startswith(".1.3.6.1.2.1.1.9.1.3.5", "Ubiquiti Networks MIB module"),
    # host_label stuff taken from lib/python3/cmk/base/plugins/agent_based/snmp_info.py
    host_label_function=host_labels,
    fetch = SNMPTree(
        base = '.1.3.6.1.4.1.41112.1.4',
        oids = [
            '1.1.4',  # UBNT-MIB::ubntRadioFreq
            '1.1.5',  # UBNT-MIB::ubntRadioDfsEnabled
            '1.1.6',  # UBNT-MIB::ubntRadioTxPower
            '1.1.2',  # UBNT-MIB::ubntRadioMode
            '2.1.2',  # ubntRadioRssiIndex per Chain
        ],
    ),
)

register.check_plugin(
    name="ubnt_airos_wireless_radio",
    service_name="ubiquiti_airos_wireless_radio_service",
    sections=["snmp_ubiquiti_airos_wireless_radio_info"],
    discovery_function=discover_ubiquiti_airos_wireless_radio,
    check_function=check_ubiquiti_airos_wireless_radio,
)

def inventory_snmp_wireless_info(section: SNMPInfo) -> InventoryResult:
    print(f"inventory_wireless_snmp_info: {section}")
    yield Attributes(path=["hardware", "system"],
                     inventory_attributes={
                         "product": section.description,
                     })

    yield Attributes(path=["software", "configuration", "snmp_info"],
                     inventory_attributes={
                         "contact": section.contact,
                         "name": section.name,
                         "location": section.location,
                     })


register.inventory_plugin(
    name="snmp_wireless_info",
    inventory_function=inventory_snmp_wireless_info,
)

