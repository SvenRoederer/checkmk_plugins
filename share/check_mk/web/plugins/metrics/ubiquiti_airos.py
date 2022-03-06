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

