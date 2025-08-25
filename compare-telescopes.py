#!/usr/bin/env python3
"""
Compare the imaging performance of 2 telescopes for astrophotography.
Performance indicators are: pixel scale (res), FOV, extended object irradiance (eoi), point object irradiance (poi), etendue (e), pixel etendue (pe), pixel signal (ps) and object signal (os).

Version 1.6 Winner highlighting with soft colors (--nocolor to disable), exclude ambiguous metrics (f-ratio, resolution)
Version 1.5 shared JS database between Python and HTML versions, HTML telescope/camera dropdowns
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


def green(text, nocolor=False):
    """Return text with soft green background if nocolor is False"""
    # Using 256-color mode for softer colors similar to code diffs
    # Double reset and explicit default background to prevent bleeding
    return f'\033[48;5;194m\033[38;5;22m{text}\033[49m\033[39m\033[0m' if not nocolor else text


def red(text, nocolor=False):
    """Return text with soft red background if nocolor is False"""
    # Using 256-color mode for softer colors similar to code diffs
    # Double reset and explicit default background to prevent bleeding
    return f'\033[48;5;224m\033[38;5;52m{text}\033[49m\033[39m\033[0m' if not nocolor else text


def colorize_values(val1, val2, str1, str2, lower_is_better=False, nocolor=False):
    """Return colored versions of str1 and str2 based on which value is better"""
    if val1 == val2:
        return str1, str2  # No coloring for ties
    if lower_is_better:
        return (green(str1, nocolor), red(str2, nocolor)) if val1 < val2 else (red(str1, nocolor), green(str2, nocolor))
    else:
        return (green(str1, nocolor), red(str2, nocolor)) if val1 > val2 else (red(str1, nocolor), green(str2, nocolor))


class Gear():
    def __init__(self, file=None):
        # Use JS file as single source of truth
        if file is None:
            # Get the directory where the script is located
            script_dir = os.path.dirname(os.path.realpath(__file__))
            file = os.path.join(script_dir, "telescopes-and-cameras.js")

        print("Loading equipment data from: {}".format(file))
        if not os.path.isfile(file):
            print("Error: Equipment data file '{}' not found!".format(file))
            print("Please ensure telescopes-and-cameras.js is in the same directory as compare-telescopes.py.")
            sys.exit(1)

        # Load JavaScript file and extract data
        with open(file, 'r') as js_file:
            js_content = js_file.read()
            # Extract the data from the JavaScript variable
            start = js_content.find('{')
            end = js_content.rfind('}') + 1
            if start != -1 and end != 0:
                data_str = js_content[start:end]
                try:
                    self.file_data = json.loads(data_str)
                    self.scopes = {x.lower(): y for x, y in self.file_data['scopes'].items()}
                    self.cameras = {x.lower(): y for x, y in self.file_data['cameras'].items()}
                except json.JSONDecodeError as e:
                    print("Error: Could not parse data from JS file '{}': {}".format(file, e))
                    sys.exit(1)
            else:
                print("Error: Could not extract data from JS file '{}'.".format(file))
                print("The file format may be incorrect.")
                sys.exit(1)

    def list_scopes_and_cameras(self, as_json=None):
        if as_json:
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
    parser.add_argument("--nocolor", action="store_true", help="Disable colored output")

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
        # Let Gear class find the JS file automatically
        gear = Gear()
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
        # Calculate field widths dynamically based on actual values
        # For focal ratio
        fr_width = max(len('{:.2f}'.format(t1_focal_ratio)), len('{:.2f}'.format(t2_focal_ratio)))
        # For focal length
        fl_width = max(len('{:.0f}'.format(t1_focal_length)), len('{:.0f}'.format(t2_focal_length)))
        # For diameter
        d_width = max(len('{:.0f}'.format(t1_aperture_diameter)), len('{:.0f}'.format(t2_aperture_diameter)))
        # For obstruction percentage
        o_width = max(len('{:.0f}'.format(100 * t1_obstruction_ratio)), len('{:.0f}'.format(100 * t2_obstruction_ratio)))
        # For resolution - adjust precision based on value magnitude
        if t1_arcsec_p < 0.1 or t2_arcsec_p < 0.1:
            res1_str = '{:.3f}'.format(t1_arcsec_p) if t1_arcsec_p < 0.1 else '{:.2f}'.format(t1_arcsec_p)
            res2_str = '{:.3f}'.format(t2_arcsec_p) if t2_arcsec_p < 0.1 else '{:.2f}'.format(t2_arcsec_p)
            res_width = max(len(res1_str), len(res2_str))
        else:
            res_width = max(len('{:.2f}'.format(t1_arcsec_p)), len('{:.2f}'.format(t2_arcsec_p)))
        # For FOV values
        fov_h1_width = max(len('{:.1f}'.format(t1_view_h / 60)), len('{:.1f}'.format(t2_view_h / 60)))
        fov_v1_width = max(len('{:.1f}'.format(t1_view_v / 60)), len('{:.1f}'.format(t2_view_v / 60)))
        # For comparison factors
        fov_factor_width = max(len('{:.2f}'.format(t1_t2_view_factor)), len('{:.2f}'.format(t2_t1_view_factor)))
        eoi_width = max(len('{:.2f}'.format(t1_t2_extended_object_irradiance_factor)), len('{:.2f}'.format(t2_t1_extended_object_irradiance_factor)))
        poi_width = max(len('{:.2f}'.format(t1_t2_point_object_irradiance_factor)), len('{:.2f}'.format(t2_t1_point_object_irradiance_factor)))
        e_width = max(len('{:.2f}'.format(t1_t2_etendue)), len('{:.2f}'.format(t2_t1_etendue)))
        pe_width = max(len('{:.2f}'.format(t1_t2_pixel_etendue)), len('{:.2f}'.format(t2_t1_pixel_etendue)))
        ps_width = max(len('{:.2f}'.format(t1_t2_pixel_signal)), len('{:.2f}'.format(t2_t1_pixel_signal)))
        os_width = max(len('{:.2f}'.format(t1_t2_object_signal)), len('{:.2f}'.format(t2_t1_object_signal)))

        # Helper function to format values with aligned decimal points
        def format_with_precision(val1, val2, default_precision=2, small_threshold=0.1, zero_threshold=0.005):
            """Format two values ensuring decimal points align and no false zeros."""
            # Determine precision needed
            if val1 < small_threshold or val2 < small_threshold:
                precision = 3
            else:
                precision = default_precision

            # Format both values with same precision
            str1 = '{{:.{}f}}'.format(precision).format(val1)
            str2 = '{{:.{}f}}'.format(precision).format(val2)

            # Check if either rounds to zero and increase precision if needed
            while (float(str1) == 0 and val1 > zero_threshold) or (float(str2) == 0 and val2 > zero_threshold):
                precision += 1
                str1 = '{{:.{}f}}'.format(precision).format(val1)
                str2 = '{{:.{}f}}'.format(precision).format(val2)

            return str1, str2, max(len(str1), len(str2))

        # Build format strings with dynamic widths
        # Format all values with proper decimal alignment
        res1_str, res2_str, res_width = format_with_precision(t1_arcsec_p, t2_arcsec_p, 2, 0.1, 0.005)

        # Format focal ratios with same precision
        fr1_str = '{:.2f}'.format(t1_focal_ratio)
        fr2_str = '{:.2f}'.format(t2_focal_ratio)
        fr_width = max(len(fr1_str), len(fr2_str))

        # Format FOV values
        fov_h1_str, fov_h2_str, fov_h_width = format_with_precision(t1_view_h / 60, t2_view_h / 60, 1, 1.0, 0.05)
        fov_v1_str, fov_v2_str, fov_v_width = format_with_precision(t1_view_v / 60, t2_view_v / 60, 1, 1.0, 0.05)

        # Format comparison factors
        fov_factor1_str, fov_factor2_str, fov_factor_width = format_with_precision(t1_t2_view_factor, t2_t1_view_factor, 2, 0.1, 0.005)
        eoi1_str, eoi2_str, eoi_width = format_with_precision(t1_t2_extended_object_irradiance_factor, t2_t1_extended_object_irradiance_factor, 2, 0.1, 0.005)
        poi1_str, poi2_str, poi_width = format_with_precision(t1_t2_point_object_irradiance_factor, t2_t1_point_object_irradiance_factor, 2, 0.1, 0.005)
        e1_str, e2_str, e_width = format_with_precision(t1_t2_etendue, t2_t1_etendue, 2, 0.1, 0.005)
        pe1_str, pe2_str, pe_width = format_with_precision(t1_t2_pixel_etendue, t2_t1_pixel_etendue, 2, 0.1, 0.005)
        ps1_str, ps2_str, ps_width = format_with_precision(t1_t2_pixel_signal, t2_t1_pixel_signal, 2, 0.1, 0.005)
        os1_str, os2_str, os_width = format_with_precision(t1_t2_object_signal, t2_t1_object_signal, 2, 0.1, 0.005)

        # Format aperture and obstruction values
        d1_str = '{:.0f}'.format(t1_aperture_diameter)
        d2_str = '{:.0f}'.format(t2_aperture_diameter)
        o1_str = '{:.0f}'.format(100 * t1_obstruction_ratio)
        o2_str = '{:.0f}'.format(100 * t2_obstruction_ratio)

        # Build telescope output lines with proper alignment
        # Apply padding first, then coloring
        fr1_padded = fr1_str.rjust(fr_width)
        fr2_padded = fr2_str.rjust(fr_width)
        # No coloring for f-ratio - too ambiguous
        fr1_colored, fr2_colored = fr1_padded, fr2_padded

        d1_padded = d1_str.rjust(d_width)
        d2_padded = d2_str.rjust(d_width)
        d1_colored, d2_colored = colorize_values(t1_aperture_diameter, t2_aperture_diameter, d1_padded, d2_padded, lower_is_better=False, nocolor=args.nocolor)

        o1_padded = o1_str.rjust(o_width)
        o2_padded = o2_str.rjust(o_width)
        o1_colored, o2_colored = colorize_values(t1_obstruction_ratio, t2_obstruction_ratio, o1_padded, o2_padded, lower_is_better=True, nocolor=args.nocolor)

        res1_padded = res1_str.rjust(res_width)
        res2_padded = res2_str.rjust(res_width)
        # No coloring for resolution - too ambiguous
        res1_colored, res2_colored = res1_padded, res2_padded

        fov_factor1_padded = fov_factor1_str.rjust(fov_factor_width)
        fov_factor2_padded = fov_factor2_str.rjust(fov_factor_width)
        fov_factor1_colored, fov_factor2_colored = colorize_values(t1_t2_view_factor, t2_t1_view_factor, fov_factor1_padded, fov_factor2_padded, lower_is_better=False, nocolor=args.nocolor)

        eoi1_padded = eoi1_str.rjust(eoi_width)
        eoi2_padded = eoi2_str.rjust(eoi_width)
        eoi1_colored, eoi2_colored = colorize_values(t1_t2_extended_object_irradiance_factor, t2_t1_extended_object_irradiance_factor, eoi1_padded, eoi2_padded, lower_is_better=False, nocolor=args.nocolor)

        poi1_padded = poi1_str.rjust(poi_width)
        poi2_padded = poi2_str.rjust(poi_width)
        poi1_colored, poi2_colored = colorize_values(t1_t2_point_object_irradiance_factor, t2_t1_point_object_irradiance_factor, poi1_padded, poi2_padded, lower_is_better=False, nocolor=args.nocolor)

        e1_padded = e1_str.rjust(e_width)
        e2_padded = e2_str.rjust(e_width)
        e1_colored, e2_colored = colorize_values(t1_t2_etendue, t2_t1_etendue, e1_padded, e2_padded, lower_is_better=False, nocolor=args.nocolor)

        pe1_padded = pe1_str.rjust(pe_width)
        pe2_padded = pe2_str.rjust(pe_width)
        pe1_colored, pe2_colored = colorize_values(t1_t2_pixel_etendue, t2_t1_pixel_etendue, pe1_padded, pe2_padded, lower_is_better=False, nocolor=args.nocolor)

        ps1_padded = ps1_str.rjust(ps_width)
        ps2_padded = ps2_str.rjust(ps_width)
        ps1_colored, ps2_colored = colorize_values(t1_t2_pixel_signal, t2_t1_pixel_signal, ps1_padded, ps2_padded, lower_is_better=False, nocolor=args.nocolor)

        os1_padded = os1_str.rjust(os_width)
        os2_padded = os2_str.rjust(os_width)
        os1_colored, os2_colored = colorize_values(t1_t2_object_signal, t2_t1_object_signal, os1_padded, os2_padded, lower_is_better=False, nocolor=args.nocolor)

        line1_parts = [
            'Telescope 1',
            'f/{}'.format(fr1_colored),
            'fl={:>{}.0f}mm'.format(t1_focal_length, fl_width),
            'D={}mm'.format(d1_colored),
            'O={}%'.format(o1_colored),
            'res={}\"/p'.format(res1_colored),
            'FOV={:>{}}\'x{:>{}}\'={}x'.format(fov_h1_str, fov_h_width, fov_v1_str, fov_v_width, fov_factor1_colored),
            'eoi={}x'.format(eoi1_colored),
            'poi={}x'.format(poi1_colored),
            'e={}x'.format(e1_colored),
            'pe={}x'.format(pe1_colored),
            'ps={}x'.format(ps1_colored),
            'os={}x'.format(os1_colored)
        ]

        line2_parts = [
            'Telescope 2',
            'f/{}'.format(fr2_colored),
            'fl={:>{}.0f}mm'.format(t2_focal_length, fl_width),
            'D={}mm'.format(d2_colored),
            'O={}%'.format(o2_colored),
            'res={}\"/p'.format(res2_colored),
            'FOV={:>{}}\'x{:>{}}\'={}x'.format(fov_h2_str, fov_h_width, fov_v2_str, fov_v_width, fov_factor2_colored),
            'eoi={}x'.format(eoi2_colored),
            'poi={}x'.format(poi2_colored),
            'e={}x'.format(e2_colored),
            'pe={}x'.format(pe2_colored),
            'ps={}x'.format(ps2_colored),
            'os={}x'.format(os2_colored)
        ]

        print(' '.join(line1_parts))
        print(' '.join(line2_parts))
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
