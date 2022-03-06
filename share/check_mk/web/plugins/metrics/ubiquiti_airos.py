# taken from https://forum.checkmk.com/t/check-plugin-with-metrics/24324/3

from cmk.gui.i18n import _
from cmk.gui.plugins.metrics import (
    metric_info,
    graph_info,
    perfometer_info,
)

metric_info["traffic"] = {
    "title": _("Traffic"),
    "unit": "bits/s",
    "color": "13/a",
}

metric_info["rxCapacity"] = {
    "title": _("rxCapacity"),
    "unit": "bits/s",
    "color": "33/a",
}
 
metric_info["txCapacity"] = {
    "title": _("txCapacity"),
#    "unit": "bytes/s",
    "unit": "bits/s",
    "color": "16/a",
}

metric_info["noise_level_dbm"] = {
    "title": _("Noise"),
    "unit": "dbm",
    "color": "33/a",
}

metric_info["rssi"] = {
    "title": _("RSSI"),
    "unit": "",
    "color": "33/a",
}

metric_info["rssi_chain_asymetry"] = {
    "title": _("RSSI asymetricy"),
    "unit": "",
    "color": "33/a",
}

metric_info["cinr_db"] = {
    "title": _("Carrier to Interference+Noise Ratio"),
    "unit": "",
    "color": "16/b",
}

metric_info["ccq"] = {
    "title": _("Client Connection Quality"),
    "unit": "%",
    "color": "16/b",
}


# https://forum.checkmk.com/t/custom-check-and-graph-template/21067/2 about "graph_info[]" vs. "graph_info.append()"
graph_info["trafficCombined"] = {
    "title": _("Traffic"),
    "metrics": [
        ("rxCapacity", "area"),
        ("txCapacity", "-area"),
        ("if_in_bps", "line"),
        ("if_out_bps", "-line"),
    ],
    "conflicting_metrics": ["bandwidth", "bandwidth_translated",],
}

graph_info.append({
    "title": _("RF-status"),
    "metrics": [
        ("noise_level_dbm", "line"),
        ("input_signal_power_dbm", "line"),
        ("output_signal_power_dbm", "line"),
# we can't combine different units (RSSI is vendor specific)
#        ("rssi", "line"),  
    ],
})

graph_info.append({
    "title": _("RSSI state"),
    "metrics": [
        ("rssi", "line"),
        ("rssi_chain_asymetry", "line"),
        ("cinr_db", "line"),
    ],
})
