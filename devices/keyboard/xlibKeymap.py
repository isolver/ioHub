# -*- coding: utf-8 -*-
"""
Created on Mon Apr  8 12:09:19 2013

@author: root
"""

VirtualKeys=dict(
    NoSymbol = 0,
    XK_0 = 48,
    XK_1 = 49,
    XK_2 = 50,
    XK_3 = 51,
    XK_4 = 52,
    XK_5 = 53,
    XK_6 = 54,
    XK_7 = 55,
    XK_8 = 56,
    XK_9 = 57,
    XK_A = 65,
    XK_AE = 198,
    XK_Aacute = 193,
    XK_Acircumflex = 194,
    XK_Adiaeresis = 196,
    XK_Agrave = 192,
    XK_ALT_LEFT = 65513,
    XK_ALT_RIGHT = 65514,
    XK_Aring = 197,
    XK_Atilde = 195,
    XK_B = 66,
    XK_BACK = 65288,
    XK_BEGIN = 65368,
    XK_BREAK = 65387,
    XK_C = 67,
    XK_CANCEL = 65385,
    XK_CAPLOCKS = 65509,
    XK_Ccedilla = 199,
    XK_CLEAR = 65291,
    XK_CONTROL_LEFT = 65507,
    XK_CONTROL_RIGHT = 65508,
    XK_D = 68,
    XK_DELETE = 65535,
    XK_DOWN = 65364,
    XK_E = 69,
    XK_ETH = 208,
    XK_Eacute = 20,
    XK_Ecircumflex = 202,
    XK_Ediaeresis = 203,
    XK_Egrave = 200,
    XK_Eisu_Shift = 65327,
    XK_Eisu_toggle = 65328,
    XK_END = 65367,
    XK_ESCAPE = 65307)

if 203 not in VirtualKeys:
    for k,v in VirtualKeys.items():
        VirtualKeys[v]=k