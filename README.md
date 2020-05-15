# compare-telescopes
Compare the imaging performance of 2 telescopes for astrophotography.

## TL;DR example
Compare a 100mm aperture f/6 with an 80mm aperture f/7 :

`compare-telescopes.py --d1 100 --f1 6 --d2 80 --f2 7`

```
Telescope 1 f/6.00  f= 600mm D=100mm O= 0% res=1.38"/p FOV=23'x23'= 0.87x eoi= 1.36x poi= 2.13x etendue= 1.36x signal= 1.36x
Telescope 2 f/7.00  f= 560mm D= 80mm O= 0% res=1.47"/p FOV=25'x25'= 1.15x eoi= 0.73x poi= 0.47x etendue= 0.73x signal= 0.73x
```

The larger and f/6 telescope is 1.36x faster than the smaller and f/7 one (but this is not the whole story, look at the other examples).

No camera is specified here, one is made up for the comparison with 1000x1000 pixels, 4μm pixel size, 100% QE.

For US-folk: replace --d1 with --di1 which accepts inches.

## Brief output mode
For example compare these two telescopes :

1. 10" LX200, f = 2970mm, central obstruction 37%, KAF-16803 camera 4096x4096, 9μm pixels, QE 60%
2. 102mm Stellarvue SV102ED, f-ratio = 6.95, ASI1600MM camera 4656x3520, 3.8µm pixels, QE 75%

`compare-telescopes.py --di1 10 --l1 2970 --o1 0.37 --c1h 4096 --c1v 4096 --c1p 9 --c1q 0.60 --d2 102 --f2 6.95 --c2h 4656 --c2v 3520 --c2p 3.8 --c2q 0.75 --brief`

``` 
Telescope 1 f/11.69 f=2970mm D=254mm O=37% res=0.63"/p FOV=43'x43'= 0.33x eoi= 0.35x poi= 1.89x etendue= 1.71x signal= 1.37x
Telescope 2 f/6.95  f= 709mm D=102mm O= 0% res=1.11"/p FOV=86'x65'= 3.06x eoi= 2.83x poi= 0.53x etendue= 0.58x signal= 0.73x
```
The LX200 has both more resolution per pixel, and 1.37x more signal thanks to the large camera pixel size than the SV102ED.

This changes completely around when we use the ASI1600MM also on the LX200 :
 
`compare-telescopes.py --di1 10 --l1 2970 --o1 0.37 --c1h 4656 --c1v 3520 --c1p 3.8 --c1q 0.75 --d2 102 --f2 6.95 --brief`

``` 
Telescope 1 f/11.69 f=2970mm D=254mm O=37% res=0.26"/p FOV=20'x15'= 0.06x eoi= 0.35x poi= 1.89x etendue= 0.30x signal= 0.30x
Telescope 2 f/6.95  f= 709mm D=102mm O= 0% res=1.11"/p FOV=86'x65'=17.55x eoi= 2.83x poi= 0.53x etendue= 3.28x signal= 3.28x
```

Now the LX200 has an unrealistic high resolution of 0.26"/pixel, and the refractor gets 3.28x more signal at the sensor.

Note that the second camera arguments were not given in which case those of the first camera are copied internally.

Of the f-ratio, aperture diameter and focal length only 2 can be specified at the same time, the program then calculates the third.

Many other parameters are optional.

## Detailed output mode

1. 14" Celestron, f/10.8, central obstruction 32%, KAF-16803 camera 4096x4096, 9μm pixels, QE 65%
2. 11" Celestron, f/10, central obstruction 31%, ASI1600MM camera 4656x3520, 3.8µm pixels, QE 75%

`compare-telescopes.py --di1 14 --f1 10.8 --o1 0.32 --c1h 4096 --c1v 4096 --c1p 9 --c1q 0.65 --di2 11 --f2 10 --o2 0.31 --c2h 4656 --c2v 3520 --c2p 3.8 --c2q 0.75 --detail`

```
OTA 1 resolving power 0.354 [arcsec], plate scale 53.708 [arcsec/mm] = 18.6 [μm/arcsec]
OTA 1 focal ratio f/10.8, focal length 3840 [mm], aperture diameter 356 [mm], central obstruction ratio 0.32, diameter 114 [mm]
OTA 1 aperture area 89144.84 [mm^2], collects 1.61x more photons
Camera 1 pixel size 9.00 [μm], sensor size 4096x4096 [pixels*pixels], 36.9x36.9 [mm*mm], sensor area 1358.95 [mm^2], 5.74x larger
Camera 1 quantum efficiency  1 [%]
Telescope 1 resolution 0.48 [arcsec/pixel], FOV 33x33 [arcmin*arcmin], 3.04x larger
Telescope 1 extended object irradiance is 0.86x more
Telescope 1    point object irradiance is 1.38x more
Telescope 1 pixel etendue 20828.62 [mm^2arcsec^2], 4.78x more
Telescope 1 pixel signal is 4.14x more
---
OTA 2 resolving power 0.450 [arcsec], plate scale 73.824 [arcsec/mm] = 13.5 [μm/arcsec]
OTA 2 focal ratio f/10.0, focal length 2794 [mm], aperture diameter 279 [mm], central obstruction ratio 0.31, diameter 87 [mm]
OTA 2 aperture area 55419.56 [mm^2], collects 0.62x more photons
Camera 2 pixel size 3.80 [μm], sensor size 4656x3520 [pixels*pixels], 17.7x13.4 [mm*mm], sensor area 236.66 [mm^2], 0.17x larger
Camera 2 quantum efficiency  1 [%]
Telescope 2 resolution 0.28 [arcsec/pixel], FOV 22x16 [arcmin*arcmin], 0.33x larger
Telescope 2 extended object irradiance is 1.17x more
Telescope 2    point object irradiance is 0.73x more
Telescope 2 pixel etendue 4361.42 [mm^2arcsec^2], 0.21x more
Telescope 2 pixel signal is 0.24x more
```

The 11" focal ratio may be faster but the 14" gets 4.14x more signal at a sensor pixel.

## Usage

`compare-telescopes.py --help`
``` 
usage: compare-telescopes.py [-h] [--brief] [--detail] [--legend]
                             [--d1 D1] [--di1 DI1] [--o1 O1] [--l1 L1]
                             [--f1 F1] [--r1 R1] [--c1h C1H] [--c1v C1V]
                             [--c1p C1P] [--c1q C1Q] [--d2 D2] [--di2 DI2]
                             [--o2 O2] [--l2 L2] [--f2 F2] [--r2 R2]
                             [--c2h C2H] [--c2v C2V] [--c2p C2P] [--c2q C2Q]

optional arguments:
  -h, --help      show this help message and exit
  --brief         Brief output
  --detail        Detail output
  --legend        Legend
  --d1 D1         Telescope 1 aperture Diameter [mm]
  --di1 DI1       Telescope 1 aperture Diameter [inch]
  --o1 O1         Telescope 1 central Obstruction ratio [float]
  --l1 L1         Telescope 1 focal Length [mm]
  --f1 F1         Telescope 1 Focal ratio, defined as focal Length / aperture Diameter [dimensionless]
  --r1 R1         Telescope 1 focal Reducer [float]
  --c1h C1H       Camera 1 Horizontal pixels [count]
  --c1v C1V       Camera 1 Vertical pixels [count]
  --c1p C1P       Camera 1 Pixel size [μm]
  --c1q C1Q       Camera 1 QE [percent]
  --d2 D2         Telescope 2 aperture Diameter [mm]
  --di2 DI2       Telescope 2 aperture Diameter [inch]
  --o2 O2         Telescope 2 central obstruction ratio [float]
  --l2 L2         Telescope 2 focal Length [mm]
  --f2 F2         Telescope 2 Focal ratio, defined as focal Length / aperture Diameter [dimensionless]
  --r2 R2         Telescope 2 focal Reducer [float]
  --c2h C2H       Camera 2 Horizontal pixels [count]
  --c2v C2V       Camera 2 Vertical pixels [count]
  --c2p C2P       Camera 2 Pixel size [μm]
  --c2q C2Q       Camera 2 QE [percent]
```

