from __future__ import division
# -*- coding: utf-8 -*-

# >>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>> IMPORTS

from Autodesk.Revit.DB import *
from Autodesk.Revit.DB import Transaction, Element, ElementId, FilteredElementCollector
from Autodesk.Revit.DB.Structure import StructuralType
from Autodesk.Revit.UI.Selection import ObjectType

import clr

clr.AddReference("System")

from _create import _auto as a
from _create import _test as tt
from _create import _parts as p
from _create import _coordinate as c
from _create import _openings as o
from _create import _errorhandler as e
from _create import _checks as cc

from pyrevit import forms
from pyrevit.forms import WPFWindow
from pyrevit import script

# >>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>> VARIABLES

app = __revit__.Application  # represents the Revit Autodesk Application
doc = __revit__.ActiveUIDocument.Document  # obj used to create new instances of elements within the active project
uidoc = __revit__.ActiveUIDocument  # obj that represent the current active project


# ________________________________________________________________________________________________TESTS


def command_option():
    from pyrevit import forms
    ops = ['option1', 'option2', 'option3', 'option4']
    selected = forms.CommandSwitchWindow.show(ops, message='Select Option')
    print (selected)


def combined_option():
    ops = ['External parts', 'Internal Parts', 'External and Internal parts']
    cfgs = {'option1': {'background': '#783F04'}}
    rops, rswitches = forms.CommandSwitchWindow.show(
        ops,
        message='Select Option for Takeoff',
        config=cfgs,
        recognize_access_key=False)

    print (rops)


def get_value():
    sele = forms.ask_for_number_slider(default=2, min=1, max=3, interval=0.5, prompt='Select minimum panel size:',
                                       title='Minimum panel ')
    print (sele)


def sample_form():
    from pyrevit import forms
    layout = '<Window ' \
             'xmlns="http://schemas.microsoft.com/winfx/2006/xaml/presentation" ' \
             'xmlns:x="http://schemas.microsoft.com/winfx/2006/xaml" ' \
             'ShowInTaskbar="False" ResizeMode="NoResize" ' \
             'WindowStartupLocation="CenterScreen" ' \
             'HorizontalContentAlignment="Center">' \
             '</Window>'
    w = forms.WPFWindow(layout, literal_string=True)
    w.show()


def display_form(data):
    output = script.get_output()
    output.center()
    output.add_style('body { color: blue; }')
    output.make_bar_chart(version=None)
    data1 = [['row1', 'data', 'data', 80], ['row2', 'data', 'data', 45]]
    tt = output.print_table(table_data=data1, title="Example Table",
                            columns=["Row Name", "Column 1", "Column 2", "Percentage"],
                            formats=['', '', '', '{}%'], last_line_style='color:red;')


def display_table():
    output = script.get_output()
    output.add_style('body { color: blue; }')


def single_value():
    while True:
        cost_per_sf = forms.ask_for_string(default='0', prompt='Enter Cost per SF:', title='Panel Material take off')
        count = 0
        for ltr in cost_per_sf:
            if ltr.isdigit():
                count += 1
        if count == len(cost_per_sf):
            break
    return cost_per_sf

