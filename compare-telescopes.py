#!/usr/bin/env python3
# 1589054759

import argparse

def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("--brief", action="store_true", help="Brief output")

    parser.add_argument("--a1", required=True, type=int, help="Telescope 1 Aperture in mm")
    parser.add_argument("--f1", required=True, type=int, help="Telescope 1 Focal Length in mm")
    parser.add_argument("--c1h", required=True, type=int, help="Telescope 1 Camera horizontal pixel count")
    parser.add_argument("--c1v", required=True, type=int, help="Telescope 1 Camera vertical pixel count")
    parser.add_argument("--c1p", required=True, type=float, help="Telescope 1 Camera pixel size in micrometer")

    parser.add_argument("--a2", required=True, type=int, help="Telescope 2 Aperture in mm")
    parser.add_argument("--f2", required=True, type=int, help="Telescope 2 Focal Length in mm")
    parser.add_argument("--c2h", required=False, type=int, help="Telescope 2 Camera horizontal pixel count")
    parser.add_argument("--c2v", required=False, type=int, help="Telescope 2 Camera vertical pixel count")
    parser.add_argument("--c2p", required=False, type=float, help="Telescope 2 Camera pixel size in micrometer")

    args = parser.parse_args()

    aperture1 = args.a1
    focal_length1 = args.f1
    focal_ratio1 = focal_length1 / aperture1
    cam1_h = args.c1h
    cam1_v = args.c1v
    cam1_p = args.c1p
    cam1_a = cam1_h * cam1_p * cam1_v * cam1_p

    aperture2 = args.a2
    focal_length2 = args.f2
    focal_ratio2 = focal_length2 / aperture2
    if args.c2h:
        cam2_h = args.c2h
        cam2_v = args.c2v
        cam2_p = args.c2p
    else:
        cam2_h = cam1_h
        cam2_v = cam1_v
        cam2_p = cam1_p
    cam2_a = cam2_h * cam2_p * cam2_v * cam2_p

    t1_arcsec_p = 206.265/focal_length1 * cam1_p
    t1_view_h = (cam1_h * 206.265/focal_length1 * cam1_p)/60
    t1_view_v = (cam1_v * 206.265/focal_length1 * cam1_p)/60
    t1_view_a = t1_view_h * t1_view_v

    t2_arcsec_p = 206.265/focal_length2 * cam2_p
    t2_view_h = (cam2_h * 206.265/focal_length2 * cam2_p)/60
    t2_view_v = (cam2_v * 206.265/focal_length2 * cam2_p)/60
    t2_view_a = t2_view_h * t2_view_v

    #t1_t2_speed_factor = (1 / (focal_ratio1/focal_ratio2)**2) * (cam1_a/cam2_a)
    #t2_t1_speed_factor = (1 / (focal_ratio2/focal_ratio1)**2) * (cam2_a/cam1_a)
    t1_t2_speed_factor = (1 / (focal_ratio1/focal_ratio2)**2)
    t2_t1_speed_factor = (1 / (focal_ratio2/focal_ratio1)**2)
    t1_t2_view_factor = t1_view_a / t2_view_a
    t2_t1_view_factor = t2_view_a / t1_view_a

    if args.brief:
        print('{:.1f} {:.2f} {:.0f}x{:.0f} {:.2f} {:.2f}'.format(
            focal_ratio1, t1_arcsec_p, t1_view_h, t1_view_v, t1_t2_view_factor, t1_t2_speed_factor))
        print('{:.1f} {:.2f} {:.0f}x{:.0f} {:.2f} {:.2f}'.format(
            focal_ratio2, t2_arcsec_p, t2_view_h, t2_view_v, t2_t1_view_factor, t2_t1_speed_factor))
    else:
        print('Telescope 1 f/{:.1f} resolution = {:.2f} [arcsec/pixel], FOV = {:.0f}x{:.0f} [arcmin*arcmin], {:.2f}x larger, imaging is {:.2f}x faster'.format(
            focal_ratio1, t1_arcsec_p, t1_view_h, t1_view_v, t1_t2_view_factor, t1_t2_speed_factor))
        print('Telescope 2 f/{:.1f} resolution = {:.2f} [arcsec/pixel], FOV = {:.0f}x{:.0f} [arcmin*arcmin], {:.2f}x larger, imaging is {:.2f}x faster'.format(
            focal_ratio2, t2_arcsec_p, t2_view_h, t2_view_v, t2_t1_view_factor, t2_t1_speed_factor))

if __name__ == '__main__':
    main()
