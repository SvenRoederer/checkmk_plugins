#!/usr/bin/env python3
# -*- coding: utf-8 -*-
# Copyright (C) 2019 tribe29 GmbH - License: GNU General Public License v2
# This file is part of Checkmk (https://checkmk.com). It is subject to the terms and
# conditions defined in the file COPYING, which is part of this source code package.

# .1.3.6.1.4.1.14685.3.1.12.1.0 10 --> DATAPOWER-STATUS-MIB::dpStatusTCPSummaryestablished.0
# .1.3.6.1.4.1.14685.3.1.12.2.0 2 --> DATAPOWER-STATUS-MIB::dpStatusTCPSummarysynsent.0
# .1.3.6.1.4.1.14685.3.1.12.3.0 0 --> DATAPOWER-STATUS-MIB::dpStatusTCPSummarysynreceived.0
# .1.3.6.1.4.1.14685.3.1.12.4.0 0 --> DATAPOWER-STATUS-MIB::dpStatusTCPSummaryfinwait1.0
# .1.3.6.1.4.1.14685.3.1.12.5.0 0 --> DATAPOWER-STATUS-MIB::dpStatusTCPSummaryfinwait2.0
# .1.3.6.1.4.1.14685.3.1.12.6.0 15 --> DATAPOWER-STATUS-MIB::dpStatusTCPSummarytimewait.0
# .1.3.6.1.4.1.14685.3.1.12.7.0 0 --> DATAPOWER-STATUS-MIB::dpStatusTCPSummaryclosed.0
# .1.3.6.1.4.1.14685.3.1.12.8.0 0 --> DATAPOWER-STATUS-MIB::dpStatusTCPSummaryclosewait.0
# .1.3.6.1.4.1.14685.3.1.12.9.0 0 --> DATAPOWER-STATUS-MIB::dpStatusTCPSummarylastack.0
# .1.3.6.1.4.1.14685.3.1.12.10.0 24 --> DATAPOWER-STATUS-MIB::dpStatusTCPSummarylisten.0
# .1.3.6.1.4.1.14685.3.1.12.11.0 0 --> DATAPOWER-STATUS-MIB::dpStatusTCPSummaryclosing.0
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


def discover_linux_usbstick(section):
    print(f"discovery for airos_wifi: {section}")
    txrate = int(section[0][4])/8
    print(f" txrate: {txrate}")
#    print(type(txrate))
    print(render.networkbandwidth(txrate))
    yield Service()

def check_linux_usbstick(section):
    print(f"check for airos_wifi: {section}")
    txrate = 0
    try:
        txrate = int(section[0][4])
        print(f" txrate: {txrate}")
    except ValueError:
        yield Result(state=State.UNKNOWN, summary=f"failed to parse SNMP TXlink-speed {section[0][4]}")
        return
    
    if txrate == 0:
        yield Result(state=State.WARN, summary="TXlink-speed=0")
    else:
        yield Result(state=State.OK, summary=f"TXlink-speed={render.networkbandwidth(txrate/8)}")
    return

def check_airos_as_metric(section):
    print(f"check for airos_wifi: {section}")
#    print(item)
#    print(params)
    txrate = -100000
    rxrate = -100000
    try:
        txrate = int(section[0][4])
        rxrate = int(section[0][5])
        rffreq = int(section[0][8])
        txlevel = int(section[0][10])
        rxlevel = int(section[0][0])
        noise = int(section[0][3])
        ccq = int(section[0][2])
        print(f" txrate: {txrate}; rxrate: {rxrate}; freq {rffreq}")

        sta_tx = int(section[19][-2]) * 1024
        sta_rx = int(section[20][-2]) * 1024
        print(f" Station: txrate: {sta_tx}; rxrate: {sta_rx}")

        rssi = int(section[0][1])
        rssiChains = [int(section[1][-1]), int(section[3][-1]) ]
        rssiAsym = rssiChains[1]-rssiChains[0]
        print(f" RSSI-chain: {rssiChains}")
    except ValueError:
#        yield Result(state=State.CRIT, notice=f"failed to parse SNMP TXlink-speed {section[0][4]}")
        return
    
    yield Metric(name="if_out_bps", value=txrate)
    yield Metric(name="txCapacity", value=sta_tx)
#    yield from check_levels(
#        txrate,                                                 # the value as int to check
#        label = "Data Throughput",                              # Summary Text
#        metric_name = 'traffic',                                # Name from metric which should be used
#        render_func = lambda v: render.networkbandwidth(v / 8)  # Bits/Sec to MBits/Sec
#    )
    yield Metric(name="if_in_bps", value=rxrate)
    yield Metric(name="frequency", value=rffreq * 1000000)
    yield Metric(name="output_signal_power_dbm", value=txlevel)
    yield Metric(name="input_signal_power_dbm", value=rxlevel)
    yield Metric(name="rssi", value=rssi)
    yield Metric(name="noise_level_dbm", value=noise)
    yield Metric(name="txCapacity", value=sta_tx)
    yield Metric(name="rxCapacity", value=sta_rx)
    yield Metric(name="rssi_chain_asymetry", value=rssiAsym)
    yield Metric(name="ccq", value=ccq)
    yield Result(state=State.OK, summary="Link is operational")
    return

register.snmp_section(
    name = "snmp_ubiquiti_airos_wifilink_info",
    detect = startswith(".1.3.6.1.2.1.1.9.1.3.5", "Ubiquiti Networks MIB module"),
#    detect = startswith(".1.3.6.1.2.1.1.1.0", "-Linux 2.6.32.68 #1 Mon Feb 3 13:02:58 EET 2020 mips"),
#iso.3.6.1.2.1.1.2.0 = OID: iso.3.6.1.4.1.10002.1
# .1.3.6.1.4.1.41112.1.4.5.1.10.1
    fetch = SNMPTree(
        base = '.1.3.6.1.4.1.41112.1.4',
        oids = [
            '5.1.5',  # UBNT-AirMAX-MIB::ubntWlStatSignal
            '5.1.6',  # UBNT-AirMAX-MIB::ubntWlStatRssi
            '5.1.7',  # UBNT-AirMAX-MIB::ubntWlStatCcq
            '5.1.8',  # UBNT-AirMAX-MIB::ubntWlStatNoiseFloor
            '5.1.9',  # UBNT-AirMAX-MIB::ubntWlStatTxRate
            '5.1.10', # UBNT-AirMAX-MIB::ubntWlStatRxRate
            '5.1.14', # UBNT-AirMAX-MIB::ubntWlStatChanWidth
            '5.1.15', # UBNT-AirMAX-MIB::ubntWlStatStaCount
            '1.1.4',  # UBNT-MIB::ubntRadioFreq
            '1.1.5',  # UBNT-MIB::ubntRadioDfsEnabled
            '1.1.6',  # UBNT-MIB::ubntRadioTxPower
            '7.1', # 
            '2.1.2', # ubntRadioRssiIndex per Chain
        ],
    ),
)

register.check_plugin(
    name="ubnt_airos_wireless",
    service_name="ubiquiti_airos_wifilink_service",
    sections=["snmp_ubiquiti_airos_wifilink_info"],
    discovery_function=discover_linux_usbstick,
#    check_function=check_linux_usbstick,
    check_function=check_airos_as_metric,
)