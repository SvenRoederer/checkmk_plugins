#!/usr/env/bin python
# -*- encoding: utf-8; py-indent-offset: 4 -*-

#
# 2021-10-11 c.steinkogler[at]cashpoint.com
#
# Check_MK kemp_loadmaster_services_extended
# an extended SNMP CheckPlugin with parts reused from the included check
#
# This program is free software: you can redistribute it and/or modify
# it under the terms of the GNU General Public License as published by
# the Free Software Foundation, either version 3 of the License, or
# (at your option) any later version.
# This program is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
# GNU General Public License for more details.
# You should have received a copy of the GNU General Public License
# along with this program.  If not, see <http://www.gnu.org/licenses/>.

# As documentation about these parameter-files is scarce I orientated on the code from
# ~/lib/python3/cmk/gui/plugins/wato/check_parameters/netscaler_vserver.py

# for autotranslating stuff it seems
from cmk.gui.i18n import _
# we need Dictionary, Tuple and Integer as we use those later
from cmk.gui.valuespec import (
    Dictionary,
    Tuple,
    Integer,
    TextAscii,
)

from cmk.gui.plugins.wato import (
    CheckParameterRulespecWithItem,
    rulespec_registry,
    RulespecGroupCheckParametersOperatingSystem,
)

def _parameter_valuespec_kemp_loadmaster_services_extended():
    return Dictionary(
        elements=[
            ("active_conns",
             Tuple(
                 title=_("Levels for Active Connections"),
                 help=_("The check detects the active connections"),
                 elements=[
                     Integer(title=_("Warning at"), default_value=1500),
                     Integer(title=_("Critical at"), default_value=2000),
                 ]
             ),
             ),
            ("connspersec",
             Tuple(
                 title=_("Levels for Connections per second"),
                 help=_("The check detects Connections per second"),
                 elements=[
                     Integer(title=_("Warning at"), default_value=1500),
                     Integer(title=_("Critical at"), default_value=2000),
                 ]
             ),
             )
        ]
    )
# enddef

rulespec_registry.register(
    CheckParameterRulespecWithItem(
        check_group_name="ubnt_airos_wireless",
        group=RulespecGroupCheckParametersOperatingSystem,
        item_spec=lambda: TextAscii(title=_("Name of Service")),
        match_type="dict",
        parameter_valuespec=_parameter_valuespec_kemp_loadmaster_services_extended,
        title=lambda: _("Kemp Service Connection Thresholds"),
    )
)

