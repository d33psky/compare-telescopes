#!/usr/bin/env python3
"""
Compare the imaging performance of 2 telescopes for astrophotography.
Performance indicators are: pixel scale (res), FOV, extended object irradiance (eoi), point object irradiance (poi), etendue (e), pixel etendue (pe), pixel signal (ps) and object signal (os).

Version 1.4 add a known list of telescopes and cameras, -s and -c
Version 1.3 add ObjectSignal as os, rename et->e pet->pe, psi->ps
Version 1.2 add defaults for aperture diameter, focal length, focal ratio
Version 1.1 pixelEtendue renamed to pet, added Etendue (of the whole system), added camera binning
Version 1.0
Source code at https://github.com/d33psky/compare-telescopes/
"""
import argparse
import math
import textwrap
import json
import os.path
import sys

default_json_data = """
{
    "scopes": {
        "ED80": { "d": 80, "l": 600 },
        "ESPRIT100": { "d": 100, "f": 5.5 },
        "ESPRIT150": { "d": 150, "f": 7 },
        "APO130": { "d": 130, "l": 650 },
        "TS-photoline-130": { "d": 130, "l": 910 },
        "SV102ED": { "d": 102, "l": 710 },
        "TOA150B": { "d": 150, "l": 1100 },
        "APMLZOS152": { "d": 152, "l": 1200 },
        "TEC140": { "d": 140, "l": 980 },
        "epsilon-180ED": { "d": 180, "f": 2.8 },
        "BS10ED": { "di": 10, "l": 711, "o": 0.35 },
        "BS12ED": { "di": 12, "l": 854, "o": 0.34 },
        "AGOiDK10": { "d": 254, "l": 1674, "o": 0.56 },
        "AGOiDK12.5": { "d": 318, "l": 2128, "o": 0.54 },
        "AGOiDK14.5": { "d": 368, "l": 2464, "o": 0.52 },
        "AGOiDK17": { "d": 432, "l": 2884, "o": 0.49 },
        "AGOiDK20": { "d": 508, "l": 3403, "o": 0.48 },
        "dream16_3.75": { "di": 16, "f": 3.75, "o": 0.375 },
        "MN-152": { "manufacturer": "Explore Scientific", "alias1": "MN6", "type": "Maksutov-Newton", "d": 152, "f": 5, "o": 0.32 },
        "CDK12.5": { "d": 318, "l": 2541, "o": 0.37 },
        "CDK14": { "d": 356, "l": 2563, "o": 0.24 },
        "CDK17": { "d": 432, "l": 2939, "o": 0.24 },
        "CDK20f7.77": { "d": 508, "l": 3951, "o": 0.15 },
        "CDK20f6.8": { "d": 508, "l": 3454, "o": 0.15 },
        "CDK24": { "d": 610, "l": 3974, "o": 0.22 },
        "C8": { "di": 8, "f": 10, "o": 0.39 },
        "C8-H3": { "di": 8, "l": 425, "o": 0.39 },
        "C8-H4": { "di": 8, "l": 390, "o": 0.39 },
        "C9.25": { "di": 9.25, "f": 10, "o": 0.36 },
        "C11": { "di": 11, "f": 10, "o": 0.34 },
        "C14": { "di": 14, "f": 10, "o": 0.32 },
        "C14-H4": { "di": 14, "l": 715, "o": 0.32 },
        "AT6RC": { "di": 6, "l": 1370, "o": 0.50 },
        "AT10RC": { "di": 10, "l": 2000, "o": 0.43 },
        "TSRC8": { "d": 203, "l": 1624, "o": 0.42 },
        "GSRC10": { "d": 254, "l": 2000, "o": 0.44 },
        "GSRC12": { "d": 304, "l": 2432, "o": 0.49 },
        "GSRC14": { "di": 14, "l": 2854, "o": 0.5 },
        "LX200-8f10": { "di": 8, "f": 10, "o": 0.38 },
        "LX200-10f10": { "di": 10, "f": 10, "o": 0.37 },
        "LX200-14f10": { "di": 14, "f": 10, "o": 0.32 },
        "ACF10f8": { "di": 10, "f": 8, "o": 0.47 },
        "ACF12f8": { "di": 12, "f": 8, "o": 0.41 },
        "ACF14f8": { "di": 14, "f": 8, "o": 0.36 },
        "SWE250PDS": { "d": 250, "l": 1200, "o": 0.25 },
        "MEWLON180": { "d": 180, "l": 2160, "o": 0.3 },
        "ONTC808": { "d": 203, "l": 800, "o": 0.36 },
        "ONTC1010": { "d": 254, "l": 1000, "o": 0.31 },
        "ONTC1212": { "d": 303, "l": 1200, "o": 0.29 },
        "RH200": { "d": 200, "l": 600, "o": 0.55 },
        "RH305": { "d": 305, "l": 1159, "o": 0.24 },
        "RASA8": { "di": 8, "l": 400, "o": 0.46 },
        "RASA11": { "di": 11, "l": 620, "o": 0.50 },
        "HUBBLE": { "d": 2400, "l": 57600, "o": 0.127, "t": 0.85 },
        "EUCLID": { "d": 1200, "l": 24500, "o": 0.0, "t": 0.0 },
        "ELT": { "d": 39300, "l": 743400, "o": 0.104 },
        "VLT": { "d": 8200,  "l": 120000, "o": 0.136 },
        "GTC": { "d": 10400,  "l": 169900, "o": 0.115 },
        "KECK_p": { "d": 10000,  "l": 17500 },
        "KECK_sf15": { "d": 10000,  "l": 149600, "o": 0.145 },
        "KECK_sf25": { "d": 10000,  "l": 249700, "o": 0.050 },
        "KECK_sf40": { "d": 10000,  "l": 395000, "o": 0.050 },
        "TMT": { "d": 30000,  "l": 450000, "o": 0.103 }
    },
    "cameras": {
        "ASI071": { "h": 4944, "v": 3284, "p": 4.79, "q": 0.50 },
        "ASI120": { "h": 1280, "v": 960, "p": 3.75, "q": 0.80 },
        "ASI2400MC": { "m": "ZWO", "s": "IMX410", "sm": "Sony", "h": 6072, "v": 4042, "p": 5.94, "q": 0.8 },
        "ASI2600": { "h": 6248, "v": 4176, "p": 3.76, "q": 0.8 },
        "ASI6200": { "m": "ZWO", "s": "IMX455", "sm": "Sony", "h": 9576, "v": 6388, "p": 3.76, "q": 0.91 },
        "ASI1600": { "h": 4656, "v": 3520, "p": 3.8, "q": 0.60 },
        "ASI462MC": { "h": 1936, "v": 1096, "p": 2.9, "q": 0.9 },
        "ASI290": { "h": 1936, "v": 1096, "p": 2.9, "q": 0.8 },
        "ASI294": { "h": 4144, "v": 2822, "p": 4.63, "q": 0.75 },
        "ASI385": { "h": 1936, "v": 1096, "p": 3.75, "q": 0.80 },
        "ASI533": { "h": 3008, "v": 3008, "p": 3.76, "q": 0.80 },
        "ASI183": { "h": 5496, "v": 3672, "p": 2.40, "q": 0.84 },
        "ATIK11000": { "h": 4007, "v": 2671, "p": 9.0, "q": 0.5 },
        "ATIK4000": { "h": 2047, "v": 2047, "p": 7.4, "q": 0.55 },
        "KAI11002": { "h": 4008, "v": 2672, "p": 9.0, "q": 0.5 },
        "ATIK16200": { "h": 4499, "v": 3599, "p": 6.0, "q": 0.6 },
        "ATIK383": { "h": 3354, "v": 2529, "p": 5.4, "q": 0.56 },
        "ATIKONE6": { "h": 2749, "v": 2199, "p": 4.54, "q": 0.66 },
        "ATIKONE9": { "h": 3380, "v": 2704, "p": 3.69, "q": 0.77 },
        "AtikHorizonII": { "h": 4656, "v": 3520, "p": 3.8, "q": 0.60 },
        "EOS40D": { "h": 3888, "v": 2592, "p": 5.7, "q": 0.33 },
        "EOS500D": { "h": 4752 , "v": 3168 , "p": 4.68, "q": 0.38 },
        "EOS550D": { "h": 5184 , "v": 3456, "p": 4.29, "q": 0.4 },
        "EOS70D": { "h": 5472, "v": 3648, "p": 4.1, "q": 0.48 },
        "EOS6D": { "h": 5472, "v": 3648, "p": 6.54, "q": 0.5 },
        "D5300": { "h": 6000, "v": 4000, "p": 3.92, "q": 0.55 },
        "D5600": { "h": 6000, "v": 4000, "p": 3.92, "q": 0.52 },
        "D610": { "m": "Nikon", "h": 6016, "v": 4016, "p":  5.95, "q": 0.49 },
        "KAF3200ME": { "h": 2184, "v": 1472, "p": 6.8, "q": 0.85 },
        "KAF8300": { "h": 3326, "v": 2504, "p": 5.4, "q": 0.56 },
        "QSI683": { "h": 3326, "v": 2504, "p": 5.4, "q": 0.57 },
        "QSI6120": { "m": "QSI", "s": "ICX834", "sm": "Sony", "h": 4250, "v": 2838, "p": 3.1, "q": 0.77 },
        "KAF16803": { "h": 4096, "v": 4096, "p": 9.0, "q": 0.6 },
        "KL4040": { "m": "FLI", "s": "GSense4040", "sm": "GPixel", "h": 4096, "v": 4096, "p": 9.0, "q": 0.74 },
        "QHY163": { "h": 4656, "v": 3522, "p": 3.8, "q": 0.6 },
        "QHY183": { "h": 5544, "v": 3694, "p": 2.4, "q": 0.84 },
        "QHY268M": { "m": "QHY", "sm": "Sony", "s": "IMX571", "h": 6280, "v": 4210, "p": 3.76, "q": 0.9 },
        "QHY23": { "h": 3468, "v": 2728, "p": 3.69, "q": 0.8 },
        "ST10XME": { "m": "SBIG", "h": 2184, "v": 1472, "p": 6.8, "q": 0.5 },
        "SX694": { "h": 2750, "v": 2200, "p": 4.54, "q": 0.77 },
        "SONYA7S": { "h": 4240, "v": 2832, "p": 8.4, "q": 0.65 },
        "IMX511": { "h": 5215, "v": 4927, "p": 1.12, "q": 0.8 },
        "HAWAII-4RG": { "h": 4096, "v": 4096, "p": 15, "q": 0.70 },
        "ACS": { "h": 4096, "v": 4096, "p": 15, "q": 0.9, "r": 1.09 },
        "WFC3": { "h": 4096, "v": 4096, "p": 15, "q": 0.9, "r": 1.354 },
        "EUCLID-VIS": { "h": 24576, "v": 24792, "p": 12, "q": 0.9 }
    }
}
"""


class Gear():
    def __init__(self, file=None):
        print("file {}".format(file))
        self.file_data = None
        self.default_data = json.loads(default_json_data)
        if os.path.isfile(file):
            with open(file) as json_file:
                self.file_data = json.load(json_file)
        self.scopes = {x.lower(): y for x, y in {**self.file_data['scopes'], **self.default_data['scopes']}.items()}
        self.cameras = {x.lower(): y for x, y in {**self.file_data['cameras'], **self.default_data['cameras']}.items()}

    def list_scopes_and_cameras(self, as_json=None):
        if as_json:
            print('Default data:')
            print(json.dumps(self.default_data, indent=4, sort_keys=True))
            print('Custom data:')
            print(json.dumps(self.file_data, indent=4, sort_keys=True))
        else:
            for name in sorted(self.scopes.items()) + sorted(self.cameras.items()):
                line = "{:15s}".format(name[0])
                for key in name[1].keys():
                    value = name[1][key]
                    line += " --{:2s} {:<6}".format(key, value)
                print("{}".format(line))

    def scope(self, name):
        d = None
        di = None
        l = None
        f = None
        o = None
        if name.lower() not in self.scopes:
            print('{} is an unknown telescope'.format(name))
            sys.exit(1)
        scope_dict = self.scopes.get(name.lower())
        if 'd' in scope_dict:
            d = scope_dict['d']
        if 'di' in scope_dict:
            di = scope_dict['di']
        if 'l' in scope_dict:
            l = scope_dict['l']
        if 'f' in scope_dict:
            f = scope_dict['f']
        if 'o' in scope_dict:
            o = scope_dict['o']
        return d, di, l, f, o

    def camera(self, name):
        h = None
        v = None
        p = None
        q = None
        r = 1
        if name.lower() not in self.cameras:
            print('{} is an unknown camera'.format(name))
            sys.exit(1)
        camera_dict = self.cameras.get(name.lower())
        if 'h' in camera_dict:
            h = camera_dict['h']
        if 'v' in camera_dict:
            v = camera_dict['v']
        if 'p' in camera_dict:
            p = camera_dict['p']
        if 'q' in camera_dict:
            q = camera_dict['q']
        if 'r' in camera_dict:
            r = camera_dict['r']
        return h, v, p, q, r


def main():
    parser = argparse.ArgumentParser(
        formatter_class=argparse.RawDescriptionHelpFormatter,
        description=__doc__,
        epilog='Use --formulas to read about the math behind the performance indicators.')
    parser.add_argument("--just_numbers", action="store_true", help="Output just the numbers")
    parser.add_argument("--brief", action="store_true", help="Brief output")
    parser.add_argument("--detail", action="store_true", help="Detail output")
    parser.add_argument("--legend", action="store_true", help="Legend")
    parser.add_argument("--formulas", action="store_true", help="Show the used formulas")
    parser.add_argument("--list", action="store_true", help="Print list of known telescopes and cameras")
    parser.add_argument("--json", action="store_true", help="Print list of known telescopes and cameras as json")

    parser.add_argument("--s1", required=False, type=str, help="Scope 1")
    parser.add_argument("--d1", required=False, type=float, help="Telescope 1 aperture Diameter [mm]")
    parser.add_argument("--di1", required=False, type=float, help="Telescope 1 aperture Diameter [inch]")
    parser.add_argument("--o1", required=False, type=float, help="Telescope 1 central Obstruction ratio [float, 0-1]")
    parser.add_argument("--l1", required=False, type=float, help="Telescope 1 focal Length [mm]")
    parser.add_argument("--f1", required=False, type=float,
                        help="Telescope 1 Focal ratio, defined as focal Length / aperture Diameter [dimensionless]")
    parser.add_argument("--r1", required=False, type=float, help="Telescope 1 focal Reducer factor [float]")
    parser.add_argument("--t1", required=False, type=float, help="Telescope 1 total Transmittance factor [float, 0-1]")
    parser.add_argument("--c1", required=False, type=str, help="Camera 1")
    parser.add_argument("--c1h", required=False, type=int, help="Camera 1 Horizontal pixels [count]")
    parser.add_argument("--c1v", required=False, type=int, help="Camera 1 Vertical pixels [count]")
    parser.add_argument("--c1p", required=False, type=float, help="Camera 1 Pixel size [μm]")
    parser.add_argument("--c1q", required=False, type=float, help="Camera 1 QE ratio [float, 0-1]")
    parser.add_argument("--c1b", required=False, type=float, help="Camera 1 binning factor [integer, 1-]")

    parser.add_argument("--s2", required=False, type=str, help="Scope 2")
    parser.add_argument("--d2", required=False, type=float, help="Telescope 2 aperture Diameter [mm]")
    parser.add_argument("--di2", required=False, type=float, help="Telescope 2 aperture Diameter [inch]")
    parser.add_argument("--o2", required=False, type=float, help="Telescope 2 central obstruction ratio [float, 0-1]")
    parser.add_argument("--l2", required=False, type=float, help="Telescope 2 focal Length [mm]")
    parser.add_argument("--f2", required=False, type=float,
                        help="Telescope 2 Focal ratio, defined as focal Length / aperture Diameter [dimensionless]")
    parser.add_argument("--r2", required=False, type=float, help="Telescope 2 focal Reducer factor [float]")
    parser.add_argument("--t2", required=False, type=float, help="Telescope 2 total Transmittance factor [float, 0-1]")
    parser.add_argument("--c2", required=False, type=str, help="Camera 2")
    parser.add_argument("--c2h", required=False, type=int, help="Camera 2 Horizontal pixels [count]")
    parser.add_argument("--c2v", required=False, type=int, help="Camera 2 Vertical pixels [count]")
    parser.add_argument("--c2p", required=False, type=float, help="Camera 2 Pixel size [μm]")
    parser.add_argument("--c2q", required=False, type=float, help="Camera 2 QE ratio [float, 0-1]")
    parser.add_argument("--c2b", required=False, type=float, help="Camera 2 binning factor [integer, 1-]")

    args = parser.parse_args()
    if args.formulas:
        print_formulas()
        sys.exit(0)
    if args.s1 or args.c1 or args.s2 or args.c2 or args.list or args.json:
        path = os.path.dirname(os.path.realpath(sys.argv[0]))
        gear = Gear(file="{}/telescopes-and-cameras.json".format(path))
    if args.list or args.json:
        gear.list_scopes_and_cameras(args.json)
        sys.exit(0)
    c1r = 1.0
    c2r = 1.0
    if args.s1:
        args.d1, args.di1, args.l1, args.f1, args.o1 = gear.scope(args.s1)
    if args.s2:
        args.d2, args.di2, args.l2, args.f2, args.o2 = gear.scope(args.s2)
    if args.c1:
        args.c1h, args.c1v, args.c1p, args.c1q, c1r = gear.camera(args.c1)
    if args.c2:
        args.c2h, args.c2v, args.c2p, args.c2q, c2r = gear.camera(args.c2)

    t1_aperture_diameter = args.d1 if args.d1 else args.di1 * 25.4 if args.di1 else None
    t1_focal_reducer = args.r1 if args.r1 else 1
    t1_focal_reducer *= c1r
    t1_obstruction_ratio = args.o1 if args.o1 else 0
    t1_transmittance_factor = args.t1 if args.t1 else 1
    if t1_aperture_diameter:
        if args.l1:
            t1_focal_length = args.l1 * t1_focal_reducer
            if args.f1:
                print('Need ONLY 2 out of 3 of Telescope 1 aperture Diameter, Focal length, Focal ratio')
                sys.exit(1)
            t1_focal_ratio = t1_focal_length / t1_aperture_diameter
        else:
            if args.f1:
                t1_focal_ratio = args.f1 * t1_focal_reducer
            else:
                t1_focal_ratio = 10 * t1_focal_reducer  # choose f/10
            t1_focal_length = t1_aperture_diameter * t1_focal_ratio
    else:
        if args.l1:
            t1_focal_length = args.l1 * t1_focal_reducer
            if args.f1:
                t1_focal_ratio = args.f1 * t1_focal_reducer
                t1_aperture_diameter = t1_focal_length / t1_focal_ratio
            else:
                t1_aperture_diameter = 100  # choose d=100mm
                t1_focal_ratio = t1_focal_length / t1_aperture_diameter
        else:
            t1_aperture_diameter = 100  # choose d=100mm
            if args.f1:
                t1_focal_ratio = args.f1 * t1_focal_reducer
            else:
                t1_focal_ratio = 10 * t1_focal_reducer  # choose f/10
            t1_focal_length = t1_aperture_diameter * t1_focal_ratio
    t1_obstruction_diameter = t1_obstruction_ratio * t1_aperture_diameter

    t2_aperture_diameter = args.d2 if args.d2 else args.di2 * 25.4 if args.di2 else None
    t2_focal_reducer = args.r2 if args.r2 else 1
    t2_focal_reducer *= c2r
    t2_obstruction_ratio = args.o2 if args.o2 else 0
    t2_transmittance_factor = args.t2 if args.t2 else 1
    if t2_aperture_diameter:
        if args.l2:
            t2_focal_length = args.l2 * t2_focal_reducer
            if args.f2:
                print('Need ONLY 2 out of 3 of Telescope 2 aperture Diameter, Focal length, Focal ratio')
                sys.exit(1)
            t2_focal_ratio = t2_focal_length / t2_aperture_diameter
        else:
            if args.f2:
                t2_focal_ratio = args.f2 * t2_focal_reducer
            else:
                t2_focal_ratio = 10 * t2_focal_reducer  # choose f/10
            t2_focal_length = t2_aperture_diameter * t2_focal_ratio
    else:
        if args.l2:
            t2_focal_length = args.l2 * t2_focal_reducer
            if args.f2:
                t2_focal_ratio = args.f2 * t2_focal_reducer
                t2_aperture_diameter = t2_focal_length / t2_focal_ratio
            else:
                t2_aperture_diameter = 100  # choose d=100mm
                t2_focal_ratio = t2_focal_length / t2_aperture_diameter
        else:
            t2_aperture_diameter = t1_aperture_diameter
            if args.f2:
                t2_focal_ratio = args.f2 * t2_focal_reducer
            else:
                if args.r2:
                    t2_focal_ratio = (t1_focal_ratio/t1_focal_reducer) * t2_focal_reducer
                else:
                    t2_focal_ratio = t1_focal_ratio
            t2_focal_length = t2_aperture_diameter * t2_focal_ratio
            t2_obstruction_ratio = t1_obstruction_ratio
            t2_transmittance_factor = t1_transmittance_factor
    t2_obstruction_diameter = t2_obstruction_ratio * t2_aperture_diameter

    arcsec_per_radian = (360 / (2 * math.pi)) * 60 * 60  # 206265.something

    t1_obstruction_area = math.pi * (t1_obstruction_diameter / 2) ** 2
    t1_aperture_area = math.pi * (t1_aperture_diameter / 2) ** 2 - t1_obstruction_area
    t1_resolving_power = 1.22 * 500e-9 * 180 / (t1_aperture_diameter / 1000 * math.pi) * 3600  # for green
    t1_plate_scale = arcsec_per_radian / (t1_focal_ratio * t1_aperture_diameter)
    c1_h = args.c1h if args.c1h else 1000  # picked some defaults to work with
    c1_v = args.c1v if args.c1v else 1000
    c1_p = args.c1p if args.c1p else 3.8
    c1_b = args.c1b if args.c1b else 1

    t2_obstruction_area = math.pi * (t2_obstruction_diameter / 2) ** 2
    t2_aperture_area = math.pi * (t2_aperture_diameter / 2) ** 2 - t2_obstruction_area
    t2_resolving_power = 1.22 * 500e-9 * 180 / (t2_aperture_diameter / 1000 * math.pi) * 3600
    t2_plate_scale = arcsec_per_radian / (t2_focal_ratio * t2_aperture_diameter)
    c2_h = args.c2h if args.c2h else c1_h
    c2_v = args.c2v if args.c2v else c1_v
    c2_p = args.c2p if args.c2p else c1_p
    c2_b = args.c2b if args.c2b else 1

    url_args = 'https://lambermont.dyndns.org/astro/code/compare-telescopes.html?a'
    url_args += '&d1={}'.format(args.d1) if args.d1 else ''
    url_args += "&di1={}".format(args.di1) if args.di1 else ''
    url_args += "&o1={}".format(args.o1) if args.o1 else ''
    url_args += "&l1={}".format(args.l1) if args.l1 else ''
    url_args += "&f1={}".format(args.f1) if args.f1 else ''
    url_args += "&r1={}".format(args.r1) if args.r1 else ''
    url_args += "&t1={}".format(args.t1) if args.t1 else ''
    url_args += "&c1h={}".format(args.c1h) if args.c1h else ''
    url_args += "&c1v={}".format(args.c1v) if args.c1v else ''
    url_args += "&c1p={}".format(args.c1p) if args.c1p else ''
    url_args += "&c1q={}".format(args.c1q) if args.c1q else ''
    url_args += "&c1b={}".format(args.c1b) if args.c1b else ''
    url_args += "&d2={}".format(args.d2) if args.d2 else ''
    url_args += "&di2={}".format(args.di2) if args.di2 else ''
    url_args += "&o2={}".format(args.o2) if args.o2 else ''
    url_args += "&l2={}".format(args.l2) if args.l2 else ''
    url_args += "&f2={}".format(args.f2) if args.f2 else ''
    url_args += "&r2={}".format(args.r2) if args.r2 else ''
    url_args += "&t2={}".format(args.t2) if args.t2 else ''
    url_args += "&c2h={}".format(args.c2h) if args.c2h else ''
    url_args += "&c2v={}".format(args.c2v) if args.c2v else ''
    url_args += "&c2p={}".format(args.c2p) if args.c2p else ''
    url_args += "&c2q={}".format(args.c2q) if args.c2q else ''
    url_args += "&c2b={}".format(args.c2b) if args.c2b else ''
    print(url_args + '\n')

    c1_h /= c1_b
    c1_v /= c1_b
    c1_p *= c1_b
    c2_h /= c2_b
    c2_v /= c2_b
    c2_p *= c2_b

    c1_a = c1_h * c1_p * c1_v * c1_p
    c1_q = args.c1q if args.c1q else 1
    c2_a = c2_h * c2_p * c2_v * c2_p
    c2_q = args.c2q if args.c2q else c1_q

    t1_arcsec_p = arcsec_per_radian / t1_focal_length * c1_p / 1000
    t1_view_h = c1_h * arcsec_per_radian / t1_focal_length * c1_p / 1000
    t1_view_v = c1_v * arcsec_per_radian / t1_focal_length * c1_p / 1000
    t1_view_a = t1_view_h * t1_view_v
    t1_etendue = t1_aperture_area * t1_view_a / 1e6  # / (57.296**2 * 3600**2)
    t1_pixel_etendue = t1_aperture_area * t1_arcsec_p ** 2
    t1_pixel_signal = t1_pixel_etendue * c1_q * t1_transmittance_factor

    t2_arcsec_p = arcsec_per_radian / t2_focal_length * c2_p / 1000
    t2_view_h = c2_h * arcsec_per_radian / t2_focal_length * c2_p / 1000
    t2_view_v = c2_v * arcsec_per_radian / t2_focal_length * c2_p / 1000
    t2_view_a = t2_view_h * t2_view_v
    t2_etendue = t2_aperture_area * t2_view_a / 1e6  # / (57.296**2 * 3600**2)
    t2_pixel_etendue = t2_aperture_area * t2_arcsec_p ** 2
    t2_pixel_signal = t2_pixel_etendue * c2_q * t2_transmittance_factor

    t1_t2_extended_object_irradiance_factor = (1 / (t1_focal_ratio / t2_focal_ratio) ** 2)
    t2_t1_extended_object_irradiance_factor = (1 / (t2_focal_ratio / t1_focal_ratio) ** 2)
    t1_t2_point_object_irradiance_factor = (1 / (t1_focal_ratio / t2_focal_ratio) ** 2) * (
            t1_aperture_area / t2_aperture_area)
    t2_t1_point_object_irradiance_factor = (1 / (t2_focal_ratio / t1_focal_ratio) ** 2) * (
            t2_aperture_area / t1_aperture_area)
    t1_t2_aperture_area = t1_aperture_area / t2_aperture_area
    t2_t1_aperture_area = t2_aperture_area / t1_aperture_area
    c1_c2_area = c1_a / c2_a
    c2_c1_area = c2_a / c1_a
    t1_t2_view_factor = t1_view_a / t2_view_a
    t2_t1_view_factor = t2_view_a / t1_view_a
    t1_t2_etendue = t1_etendue / t2_etendue
    t2_t1_etendue = t2_etendue / t1_etendue
    t1_t2_pixel_etendue = t1_pixel_etendue / t2_pixel_etendue
    t2_t1_pixel_etendue = t2_pixel_etendue / t1_pixel_etendue
    t1_t2_pixel_signal = t1_pixel_signal / t2_pixel_signal
    t2_t1_pixel_signal = t2_pixel_signal / t1_pixel_signal

    t1_t2_object_signal = t1_aperture_area / t2_aperture_area * c1_q / c2_q * t1_transmittance_factor / t2_transmittance_factor
    t2_t1_object_signal = t2_aperture_area / t1_aperture_area * c2_q / c1_q * t2_transmittance_factor / t1_transmittance_factor

    if args.brief or not args.detail:
        print(
            'Telescope 1 f/{:<5.2f} l={:4.0f}mm D={:3.0f}mm O={:2.0f}% res={:3.2f}"/p FOV={:2.0f}\'x{:2.0f}\'={:5.2f}x eoi={:5.2f}x poi={:5.2f}x e={:5.2f}x pe={:5.2f}x ps={:5.2f}x os={:5.2f}x'.format(
                t1_focal_ratio, t1_focal_length, t1_aperture_diameter, 100 * t1_obstruction_ratio, t1_arcsec_p,
                                                                       t1_view_h / 60, t1_view_v / 60,
                t1_t2_view_factor, t1_t2_extended_object_irradiance_factor, t1_t2_point_object_irradiance_factor,
                t1_t2_etendue, t1_t2_pixel_etendue, t1_t2_pixel_signal, t1_t2_object_signal))
        print(
            'Telescope 2 f/{:<5.2f} l={:4.0f}mm D={:3.0f}mm O={:2.0f}% res={:3.2f}"/p FOV={:2.0f}\'x{:2.0f}\'={:5.2f}x eoi={:5.2f}x poi={:5.2f}x e={:5.2f}x pe={:5.2f}x ps={:5.2f}x os={:5.2f}x'.format(
                t2_focal_ratio, t2_focal_length, t2_aperture_diameter, 100 * t2_obstruction_ratio, t2_arcsec_p,
                                                                       t2_view_h / 60, t2_view_v / 60,
                t2_t1_view_factor, t2_t1_extended_object_irradiance_factor, t2_t1_point_object_irradiance_factor,
                t2_t1_etendue, t2_t1_pixel_etendue, t2_t1_pixel_signal, t2_t1_object_signal))
        if args.legend:
            print(
                '# F-number focalLength apertureDiameter Obstruction RESolution FieldOfView ExtendedObjectIrradiance PixelOI Etendue PixelEtendue PixelSignal ObjectSignal')
    else:
        print('---')
        print('OTA 1 resolving power {:.3f} [arcsec], plate scale {:.3f} [arcsec/mm] = {:.1f} [μm/arcsec]'.format(
            t1_resolving_power, t1_plate_scale, 1000 / t1_plate_scale))
        print(
            'OTA 1 focal ratio f/{:.1f}, focal length {:.0f} [mm], aperture diameter {:.0f} [mm], central obstruction ratio {:.2f}, diameter {:.0f} [mm]'.format(
                t1_focal_ratio, t1_focal_length, t1_aperture_diameter, t1_obstruction_ratio, t1_obstruction_diameter))
        print('OTA 1 aperture area {:.2f} [mm^2], collects {:.2f}x more photons'.format(
            t1_aperture_area, t1_t2_aperture_area))
        print(
            'Camera 1 pixel size {:.3f} [μm], sensor size {:.0f}x{:.0f} [pixels*pixels], {:.1f}x{:.1f} [mm*mm], sensor area {:.2f} [mm^2] ={:.2f}x larger'.format(
                c1_p, c1_h, c1_v, c1_h * c1_p / 1e3, c1_v * c1_p / 1e3, c1_a / 1e6, c1_c2_area))
        print('Camera 1 quantum efficiency factor {:.2f}'.format(c1_q))
        print(
            'Telescope 1 resolution {:.4f} [arcsec/pixel], FOV {:.3f}x{:.3f} [arcsec*arcsec]={:.2f}x{:.2f} [arcmin*arcmin] ={:.4f}x larger, optical transmittance factor {:.2f}'.format(
                t1_arcsec_p, t1_view_h, t1_view_v, t1_view_h / 60, t1_view_v / 60, t1_t2_view_factor,
                t1_transmittance_factor))
        print('Telescope 1 extended object irradiance is {:.2f}x more'.format(t1_t2_extended_object_irradiance_factor))
        print('Telescope 1    point object irradiance is {:.2f}x more'.format(t1_t2_point_object_irradiance_factor))
        print('Telescope 1       etendue {:.2f} [m^2arcsec^2] ={:.2f}x more'.format(t1_etendue, t1_t2_etendue))
        print('Telescope 1 pixel etendue {:.2f} [mm^2arcsec^2] ={:.2f}x more'.format(t1_pixel_etendue,
                                                                                     t1_t2_pixel_etendue))
        print('Telescope 1 pixel signal is {:.2f}x more'.format(t1_t2_pixel_signal))
        print('Telescope 1 object signal is {:.2f}x more'.format(t1_t2_object_signal))
        print('---')
        print('OTA 2 resolving power {:.3f} [arcsec], plate scale {:.3f} [arcsec/mm] = {:.1f} [μm/arcsec]'.format(
            t2_resolving_power, t2_plate_scale, 1000 / t2_plate_scale))
        print(
            'OTA 2 focal ratio f/{:.1f}, focal length {:.0f} [mm], aperture diameter {:.0f} [mm], central obstruction ratio {:.2f}, diameter {:.0f} [mm]'.format(
                t2_focal_ratio, t2_focal_length, t2_aperture_diameter, t2_obstruction_ratio, t2_obstruction_diameter))
        print('OTA 2 aperture area {:.2f} [mm^2], collects {:.2f}x more photons'.format(
            t2_aperture_area, t2_t1_aperture_area))
        print(
            'Camera 2 pixel size {:.3f} [μm], sensor size {:.0f}x{:.0f} [pixels*pixels], {:.1f}x{:.1f} [mm*mm], sensor area {:.2f} [mm^2] ={:.2f}x larger'.format(
                c2_p, c2_h, c2_v, c2_h * c2_p / 1e3, c2_v * c2_p / 1e3, c2_a / 1e6, c2_c1_area))
        print('Camera 2 quantum efficiency factor {:.2f}'.format(c2_q))
        print(
            'Telescope 2 resolution {:.4f} [arcsec/pixel], FOV {:.3f}x{:.3f} [arcsec*arcsec]={:.2f}x{:.2f} [arcmin*arcmin] ={:.4f}x larger, optical transmittance factor {:.2f}'.format(
                t2_arcsec_p, t2_view_h, t2_view_v, t2_view_h / 60, t2_view_v / 60, t2_t1_view_factor,
                t2_transmittance_factor))
        print('Telescope 2 extended object irradiance is {:.2f}x more'.format(t2_t1_extended_object_irradiance_factor))
        print('Telescope 2    point object irradiance is {:.2f}x more'.format(t2_t1_point_object_irradiance_factor))
        print('Telescope 2       etendue {:.2f} [m^2arcsec^2] ={:.2f}x more'.format(t2_etendue, t2_t1_etendue))
        print('Telescope 2 pixel etendue {:.2f} [mm^2arcsec^2] ={:.2f}x more'.format(t2_pixel_etendue,
                                                                                     t2_t1_pixel_etendue))
        print('Telescope 2 pixel signal is {:.2f}x more'.format(t2_t1_pixel_signal))
        print('Telescope 2 object signal is {:.2f}x more'.format(t2_t1_object_signal))
        print('---')


def print_formulas():
    formulas = textwrap.dedent("""\
    - Pixel Scale, or pixel resolution, is the solid angle that is projected on a single pixel.
      It is measured in arcseconds per pixel, ["/pixel].
      Formula: pixel scale ["/pixel] = 206.265 [k"] * pixel size [μm/pixel] / focal length [mm]
      With 206.265 the amount of arcseconds per radian / 1000
      And arcseconds per radian = (360 / (2 * pi)) * 60 * 60 = 206264.80624709635515795...
    - FOV, Field Of View, is the solid angle that is projected on the camera sensor.
      angle_x ["] = camera_pixels_x [pixels] * pixel scale ["/pixel]
      angle_y ["] = camera_pixels_y [pixels] * pixel scale ["/pixel]
      FOV is displayed in arcminutes [']=["/60]
    - Extended Object Irradiance is the radiant flux (power) received by the sensor per unit area of an extended object.
      Extended Object Irradiance is measured in Watt/m^2.
      We do not compute the irradiance itself because the ratio suffices and that varies as the inverse square of the focal ratio.
      Aperture size alone does not matter for Extended Object Irradiance, only focal ratio does. (Aperture size does matter for Point Object Irradiance).
      An extended object is anything that is not a point source, where a point source can be a star or anything else close to the size of the angular PSF projected onto the sky.
      Formula: Extended_Object_Irradiance_ratio = 1 / (focal ratio of ota 1/focal ratio of ota 2)^2
      The Extended Object Irradiance is also known as the Speed of a film camera where an f/4 is twice as fast as an f/5.6, meaning you need only half the time.
    - Point Object Irradiance is the radiant flux (power) received by the sensor per unit area of a point object.
      For point objects such as stars the image irradiance varies as the aperture area ratio and the inverse square of the focal ratio.
      Aperture size matters for Point Object Irradiance, as well as focal ratio. (Aperture size alone does not matter for Extended Object Irradiance).
      Formula: Point_Object_Irradiance_ratio = (ota 1 aperture area/ota 2 aperture area) * 1 / (focal ratio of ota 1/focal ratio of ota 2)^2
    - Etendue is a measure of the flux gathering capability of the optical system onto the sensor. It is a purely geometric quantity.
      Formula: etendue = aperture_area [m^2] * FOV ["^2]
    - Pixel Etendue is the etendue for a single pixel. It represents the light-gathering power of a single pixel.
      Formula: pixel_etendue = aperture_area [mm^2] * pixel_scale^2 ["^2]
    - Pixel Signal is the Pixel Etendue corrected for the sensor Quantum Efficiency and total optical system Transmittance losses.
      Formula: pixel_signal = pixel_etendue * QE-factor * Transmittance_factor
    - Object Signal is based on the Etendue of an extended object that fits in the FOV of both scopes, corrected for the sensor Quantum Efficiency and total optical system Transmittance losses.
      Formula: object_signal = aperture_area [m^2] * QE-factor * Transmittance_factor
    """)
    print(formulas)


if __name__ == '__main__':
    main()
