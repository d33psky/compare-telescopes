#!/usr/bin/env python3
# 1589460783

import argparse
import math

def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("--brief", action="store_true", help="Brief output")
    parser.add_argument("--extended", action="store_true", help="Extended output")

    parser.add_argument("--d1", required=False, type=float, help="Telescope 1 aperture Diameter [mm]")
    parser.add_argument("--di1", required=False, type=float, help="Telescope 1 aperture Diameter [inch]")
    parser.add_argument("--f1", required=False, type=float, help="Telescope 1 Focal length [mm]")
    parser.add_argument("--r1", required=False, type=float, help="Telescope 1 focal Ratio, defined as Focal length / aperture Diameter [dimensionless]")
    parser.add_argument("--c1h", required=False, type=int, help="Camera 1 Horizontal pixels [count]")
    parser.add_argument("--c1v", required=False, type=int, help="Camera 1 Vertical pixels [count]")
    parser.add_argument("--c1p", required=False, type=float, help="Camera 1 Pixel size [μm]")
    parser.add_argument("--c1q", required=False, type=float, help="Camera 1 QE [percent]")

    parser.add_argument("--d2", required=False, type=float, help="Telescope 2 aperture Diameter [mm]")
    parser.add_argument("--di2", required=False, type=float, help="Telescope 2 aperture Diameter [inch]")
    parser.add_argument("--f2", required=False, type=float, help="Telescope 2 Focal length [mm]")
    parser.add_argument("--r2", required=False, type=float, help="Telescope 2 focal Ratio, defined as Focal length / aperture Diameter [dimensionless]")
    parser.add_argument("--c2h", required=False, type=int, help="Camera 2 Horizontal pixels [count]")
    parser.add_argument("--c2v", required=False, type=int, help="Camera 2 Vertical pixels [count]")
    parser.add_argument("--c2p", required=False, type=float, help="Camera 2 Pixel size [μm]")
    parser.add_argument("--c2q", required=False, type=float, help="Camera 2 QE [percent]")

    args = parser.parse_args()

    t1_aperture_diameter = args.d1 if args.d1 else args.di1*25.4 if args.di1 else None
    if t1_aperture_diameter:
        if args.f1:
            t1_focal_length = args.f1
            if args.r1:
                print('Need ONLY 2 out of 3 of Telescope 1 aperture Diameter, Focal length, Focal ratio')
                quit(1)
            t1_focal_ratio = t1_focal_length / t1_aperture_diameter
        else:
            if args.r1:
                t1_focal_ratio = args.r1
                t1_focal_length = t1_aperture_diameter * t1_focal_ratio
            else:
                print('Need 2 out of 3 of Telescope 1 aperture Diameter, Focal length, Focal ratio')
                quit(1)
    else:
        if args.f1:
            t1_focal_length = args.f1
            if args.r1:
                t1_focal_ratio = args.r1
                t1_aperture_diameter = t1_focal_length / t1_focal_ratio
            else:
                print('Need 2 out of 3 of Telescope 1 aperture Diameter, Focal length, Focal ratio')
                quit(1)
        else:
            print('Need 2 out of 3 of Telescope 1 aperture Diameter, Focal length, Focal ratio')
            quit(1)

    t2_aperture_diameter = args.d2 if args.d2 else args.di2*25.4 if args.di2 else None
    if t2_aperture_diameter:
        if args.f2:
            t2_focal_length = args.f2
            if args.r2:
                print('Need ONLY 2 out of 3 of Telescope 2 aperture Diameter, Focal length, Focal ratio')
                quit(1)
            t2_focal_ratio = t2_focal_length / t2_aperture_diameter
        else:
            if args.r2:
                t2_focal_ratio = args.r2
                t2_focal_length = t2_aperture_diameter * t2_focal_ratio
            else:
                print('Need 2 out of 3 of Telescope 2 aperture Diameter, Focal length, Focal ratio')
                quit(1)
    else:
        if args.f2:
            t2_focal_length = args.f2
            if args.r2:
                t2_focal_ratio = args.r2
                t2_aperture_diameter = t2_focal_length / t2_focal_ratio
            else:
                print('Need 2 out of 3 of Telescope 2 aperture Diameter, Focal length, Focal ratio')
                quit(1)
        else:
            print('Need 2 out of 3 of Telescope 2 aperture Diameter, Focal length, Focal ratio')
            quit(1)

    arcsec_per_radian = (360 / (2 * math.pi)) * 60 * 60 # 206265.something

    t1_aperture_area = math.pi * (t1_aperture_diameter/2)**2
    t1_resolving_power = 1.22 * 500e-9 * 180 / (t1_aperture_diameter/1000 * math.pi) * 3600 # for green
    t1_plate_scale = arcsec_per_radian/(t1_focal_ratio * t1_aperture_diameter)
    c1_h = args.c1h if args.c1h else 1000 # picked some defaults to work with
    c1_v = args.c1v if args.c1v else 1000
    c1_p = args.c1p if args.c1p else 4
    c1_a = c1_h * c1_p * c1_v * c1_p
    c1_q = args.c1q if args.c1q else 100

    t2_aperture_area = math.pi * (t2_aperture_diameter/2)**2
    t2_resolving_power = 1.22 * 500e-9 * 180 / (t2_aperture_diameter/1000 * math.pi) * 3600
    t2_plate_scale = arcsec_per_radian/(t2_focal_ratio * t2_aperture_diameter)
    c2_h = args.c2h if args.c2h else c1_h
    c2_v = args.c2v if args.c2v else c1_v
    c2_p = args.c2p if args.c2p else c1_p
    c2_a = c2_h * c2_p * c2_v * c2_p
    c2_q = args.c2q if args.c2q else 100

    t1_arcsec_p = arcsec_per_radian/t1_focal_length * c1_p / 1000
    t1_view_h = c1_h * arcsec_per_radian/t1_focal_length * c1_p / 1000
    t1_view_v = c1_v * arcsec_per_radian/t1_focal_length * c1_p / 1000
    t1_view_a = t1_view_h * t1_view_v
#    t1_pixel_etendue = math.pi/4 * t1_aperture_diameter**2 * t1_arcsec_p**2 * c1_q/100
    t1_pixel_etendue = t1_aperture_diameter**2 * t1_arcsec_p**2 * (c1_q/100) / (math.pi*4)

    t2_arcsec_p = arcsec_per_radian/t2_focal_length * c2_p / 1000
    t2_view_h = c2_h * arcsec_per_radian/t2_focal_length * c2_p / 1000
    t2_view_v = c2_v * arcsec_per_radian/t2_focal_length * c2_p / 1000
    t2_view_a = t2_view_h * t2_view_v
    t2_pixel_etendue = t2_aperture_diameter**2 * t2_arcsec_p**2 * (c2_q/100) / (math.pi*4)

    t1_t2_extended_object_irradiance_factor = (1 / (t1_focal_ratio/t2_focal_ratio)**2)
    t2_t1_extended_object_irradiance_factor = (1 / (t2_focal_ratio/t1_focal_ratio)**2)
    t1_t2_point_object_irradiance_factor = (1 / (t1_focal_ratio/t2_focal_ratio)**2) * (t1_aperture_area/t2_aperture_area)
    t2_t1_point_object_irradiance_factor = (1 / (t2_focal_ratio/t1_focal_ratio)**2) * (t2_aperture_area/t1_aperture_area)
    t1_t2_aperture_area = t1_aperture_area / t2_aperture_area
    t2_t1_aperture_area = t2_aperture_area / t1_aperture_area
    c1_c2_area = c1_a / c2_a
    c2_c1_area = c2_a / c1_a
    t1_t2_view_factor = t1_view_a / t2_view_a
    t2_t1_view_factor = t2_view_a / t1_view_a
    t1_t2_pixel_etendue = t1_pixel_etendue / t2_pixel_etendue
    t2_t1_pixel_etendue = t2_pixel_etendue / t1_pixel_etendue

    if args.brief:
        print('{:.1f} {:.2f} {:.0f}x{:.0f} {:.2f} {:.2f}'.format(
            t1_focal_ratio, t1_arcsec_p, t1_view_h/60, t1_view_v/60, t1_t2_view_factor, t1_t2_point_object_irradiance_factor))
        print('{:.1f} {:.2f} {:.0f}x{:.0f} {:.2f} {:.2f}'.format(
            t2_focal_ratio, t2_arcsec_p, t2_view_h/60, t2_view_v/60, t2_t1_view_factor, t2_t1_point_object_irradiance_factor))
    elif args.extended:
        print('---')

        print('OTA 1 resolving power {:.3f} [arcsec], plate scale {:.3f} [arcsec/mm] / {:.1f} [μm/arcsec]'.format(
            t1_resolving_power, t1_plate_scale, 1000/t1_plate_scale))
        print('OTA 1 focal ratio f/{:.1f}, focal length {:.0f} [mm], aperture diameter {:.0f} [mm], aperture area {:.2f} [mm^2], collects {:.2f}x more photons'.format(
            t1_focal_ratio, t1_focal_length, t1_aperture_diameter, t1_aperture_area, t1_t2_aperture_area))
        print('Camera 1 pixel size {:.2f} [μm], sensor size {}x{} [pixels*pixels], {:.1f}x{:.1f} [mm*mm], sensor area {:.2f} [mm^2], {:.2f}x larger'.format(
            c1_p, c1_h, c1_v, c1_h * c1_p/1e3, c1_v * c1_p/1e3, c1_a/1e6, c1_c2_area))
        print('Telescope 1 resolution {:.2f} [arcsec/pixel], FOV {:.0f}x{:.0f} [arcmin*arcmin], {:.2f}x larger'.format(
            t1_arcsec_p, t1_view_h/60, t1_view_v/60, t1_t2_view_factor))
        print('Telescope 1 extended object irradiance is {:.2f}x more'.format(t1_t2_extended_object_irradiance_factor))
        print('Telescope 1 point    object irradiance is {:.2f}x more'.format(t1_t2_point_object_irradiance_factor))
        print('Telescope 1 pixel etendue {:.2f} [mm^2arcsec^2], {:.2f}x more'.format(t1_pixel_etendue, t1_t2_pixel_etendue))
        print('---')

        print('OTA 2 resolving power {:.3f} [arcsec], plate scale {:.3f} [arcsec/mm] / {:.1f} [μm/arcsec]'.format(
            t2_resolving_power, t2_plate_scale, 1000/t2_plate_scale))
        print('OTA 2 focal ratio f/{:.1f}, focal length {:.0f} [mm], aperture diameter {:.0f} [mm], aperture area {:.2f} [mm^2], collects {:.2f}x more photons'.format(
            t2_focal_ratio, t2_focal_length, t2_aperture_diameter, t2_aperture_area, t2_t1_aperture_area))
        print('Camera 2 pixel size {:.2f} [μm], sensor size {}x{} [pixels*pixels], {:.1f}x{:.1f} [mm*mm], sensor area {:.2f} [mm^2], {:.2f}x larger'.format(
            c2_p, c2_h, c2_v, c2_h * c2_p/1e3, c2_v * c2_p/1e3, c2_a/1e6, c2_c1_area))
        print('Telescope 2 resolution {:.2f} [arcsec/pixel], FOV {:.0f}x{:.0f} [arcmin*arcmin], {:.2f}x larger'.format(
            t2_arcsec_p, t2_view_h/60, t2_view_v/60, t2_t1_view_factor))
        print('Telescope 2 extended object irradiance is {:.2f}x more'.format(t2_t1_extended_object_irradiance_factor))
        print('Telescope 2 point    object irradiance is {:.2f}x more'.format(t2_t1_point_object_irradiance_factor))
        print('Telescope 2 pixel etendue {:.2f} [mm^2arcsec^2], {:.2f}x more'.format(t2_pixel_etendue, t2_t1_pixel_etendue))
        print('---')

    else:
        print('Telescope 1 f/{:.1f} resolution = {:.2f} [arcsec/pixel], FOV = {:.0f}x{:.0f} [arcmin*arcmin], {:.2f}x larger, imaging is {:.2f}x faster'.format(
            t1_focal_ratio, t1_arcsec_p, t1_view_h/60, t1_view_v/60, t1_t2_view_factor, t1_t2_point_object_irradiance_factor))
        print('Telescope 2 f/{:.1f} resolution = {:.2f} [arcsec/pixel], FOV = {:.0f}x{:.0f} [arcmin*arcmin], {:.2f}x larger, imaging is {:.2f}x faster'.format(
            t2_focal_ratio, t2_arcsec_p, t2_view_h/60, t2_view_v/60, t2_t1_view_factor, t2_t1_point_object_irradiance_factor))

if __name__ == '__main__':
    main()
