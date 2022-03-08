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


def discover_ubiquiti_airos_ap(section):
    print(f"discovery for airos_wireless_ap: {section}")
    yield Service()


def check_ubiquiti_airos_ap(section):
    print(f"check for airos_wireless_ap: {section}")

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
        
        print(f" txrate: {txrate}; rxrate: {rxrate}; rx-level {rxlevel}; noise {noise}")

    except ValueError:
#        yield Result(state=State.CRIT, notice=f"failed to parse SNMP TXlink-speed {ap_data[4]}")
        return

    yield Metric(name="if_out_bps", value=txrate)
    yield Metric(name="if_in_bps", value=rxrate)
    yield Metric(name="input_signal_power_dbm", value=rxlevel)
    yield Metric(name="noise_level_dbm", value=noise)
    yield Metric(name="rssi", value=rssi)
    yield Metric(name="ccq", value=ccq)


    if sta_count != len(section):
        yield Result(state=State.CRIT, notice="Error!! Station-count of AP don not match site of dataset.")
        return
    if len(section) == 0:
        yield Result(state=State.WARN, notice="no station connected.")
        return
    if len(section) > 1:
        yield Result(state=State.WARN, notice="more than 1 station connected --> needs to be implemented ....")
        return

    sta_data = section[0]
    sta_data = sta_data[9:]
    try:
        sta_mac = sta_data[0]
        sta_name = sta_data[1]
        sta_rxlevel = int(sta_data[2])
        sta_noise = int(sta_data[3])
        sta_ccq = int(sta_data[4])
        sta_txrate = int(sta_data[5])
        sta_rxrate = int(sta_data[6])
        sta_cinr = int(sta_data[7])
        sta_tx = int(sta_data[8]) * 1024
        sta_rx = int(sta_data[9]) * 1024
        sta_air_tx = float(sta_data[10]) / 10
        sta_air_rx = float(sta_data[11]) / 10
        sta_lat = int(sta_data[12])
        

        print(f" Station: txrate: {sta_txrate}; rxrate: {sta_rxrate}") #; freq {rffreq}")
        print(f" Station: txrate: {sta_tx}; rxrate: {sta_rx}")

#        rssi = int(sta_data[1])
#        rssiChains = [int(section[1][-1]), int(section[3][-1]) ]
#        rssiAsym = rssiChains[1]-rssiChains[0]
#        print(f" RSSI-chain: {rssiChains}")
    except ValueError:
#        yield Result(state=State.CRIT, notice=f"failed to parse SNMP TXlink-speed {sta_data[4]}")
        return
    
    yield Metric(name="txCapacity", value=sta_tx)
    yield Metric(name="rxCapacity", value=sta_rx)
    yield Metric(name="if_out_bps", value=sta_txrate)
    yield Metric(name="if_in_bps", value=sta_rxrate)
#    yield Metric(name="frequency", value=rffreq * 1000000)
#    yield Metric(name="output_signal_power_dbm", value=txlevel)
    yield Metric(name="input_signal_power_dbm", value=sta_rxlevel)
    yield Metric(name="noise_level_dbm", value=sta_noise)
#    yield Metric(name="rssi_chain_asymetry", value=rssiAsym)
    yield Metric(name="ccq", value=sta_ccq)
    yield Metric(name="cinr_db", value=sta_cinr)

    yield Result(state=State.OK, summary=f"AP is up with SSID {ssid}, {sta_count} stations connected")
    return

register.snmp_section(
    name = "snmp_ubiquiti_airos_wifilink_ap_info",
    detect = all_of(
        startswith(".1.3.6.1.2.1.1.9.1.3.5", "Ubiquiti Networks MIB module"),
        equals(".1.3.6.1.4.1.41112.1.4.1.1.2.1", "4"),
    ),
    fetch = SNMPTree(
        base = '.1.3.6.1.4.1.41112.1.4',
        oids = [
            '5.1.2',  # UBNT-AirMAX-MIB::ubntWlStatSsid
            '5.1.5',  # UBNT-AirMAX-MIB::ubntWlStatSignal
            '5.1.6',  # UBNT-AirMAX-MIB::ubntWlStatRssi
            '5.1.7',  # UBNT-AirMAX-MIB::ubntWlStatCcq
            '5.1.8',  # UBNT-AirMAX-MIB::ubntWlStatNoiseFloor
            '5.1.9',  # UBNT-AirMAX-MIB::ubntWlStatTxRate
            '5.1.10', # UBNT-AirMAX-MIB::ubntWlStatRxRate
            '5.1.14', # UBNT-AirMAX-MIB::ubntWlStatChanWidth
            '5.1.15', # UBNT-AirMAX-MIB::ubntWlStatStaCount
            '7.1.1',  # Station data: ubntStaMac
            '7.1.2',  # Station data: ubntStaName
            '7.1.3',  # Station data: ubntStaSignal
            '7.1.4',  # Station data: ubntStaNoiseFloor
            '7.1.6',  # Station data: ubntStaCcq
            '7.1.11', # Station data: ubntStaTxRate
            '7.1.12', # Station data: ubntStaRxRate
            '7.1.16', # Station data: ubntStaLocalCINR
            '7.1.17', # Station data: ubntStaTxCapacity
            '7.1.18', # Station data: ubntStaRxCapacity
            '7.1.19', # Station data: ubntStaTxAirtime
            '7.1.20', # Station data: ubntStaRxAirtime
            '7.1.21', # Station data: ubntStaTxLatency
        ],
    ),
)

register.check_plugin(
    name="ubnt_airos_wireless_ap",
    service_name="ubiquiti_airos_wifilink_ap_service",
    sections=["snmp_ubiquiti_airos_wifilink_ap_info"],
    discovery_function=discover_ubiquiti_airos_ap,
    check_function=check_ubiquiti_airos_ap,
)
