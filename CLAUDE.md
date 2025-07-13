# CLAUDE.md

This file provides guidance to Claude Code (claude.ai/code) when working with code in this repository.

## Project Overview

Compare Telescopes is a specialized astrophotography tool that compares the imaging performance of two telescopes across 8 key performance indicators: pixel scale (res), FOV, extended object irradiance (eoi), point object irradiance (poi), etendue (e), pixel etendue (pe), pixel signal (ps), and object signal (os).

The project has dual interfaces - a Python CLI tool and a web-based HTML version that provide identical functionality.

## Key Architecture

**Core Components:**
- `compare-telescopes.py`: Main CLI application (573 lines) with comprehensive comparison logic
- `compare-telescopes.html`: Web interface with interactive forms
- `telescopes-and-cameras.js`: Database of 94+ telescopes and 37+ cameras with specifications

**Database Structure:**
- Telescopes: aperture diameter (`d`/`di`), focal length (`l`), focal ratio (`f`), obstruction ratio (`o`), transmittance (`t`)
- Cameras: horizontal/vertical pixels (`h`/`v`), pixel size (`p`), quantum efficiency (`q`)
- Support for both metric (`d` in mm) and imperial (`di` in inches) units

## Common Commands

**Basic Usage:**
```bash
# Compare two telescopes with basic parameters
python3 compare-telescopes.py --d1 100 --f1 6 --d2 80 --f2 7

# Use known telescopes and cameras from database
python3 compare-telescopes.py -s1 C11 -c1 ASI1600 -s2 SV102ED -c2 ASI533

# Detailed output with full calculations
python3 compare-telescopes.py --d1 100 --f1 6 --d2 80 --f2 7 --detail

# Show formulas and mathematical explanations
python3 compare-telescopes.py --formulas
```

**Output Modes:**
- Default: Brief comparison with ratios
- `--detail`: Full calculations with units and explanations
- `--just_numbers`: Numeric output only
- `--formulas`: Mathematical formulas and theory

## Development Notes

**Technology Stack:**
- Pure Python 3 with only standard library dependencies
- No build system required - direct script execution
- HTML/JavaScript web version mirrors CLI functionality

**Parameter Validation:**
- Only 2 of 3 optical parameters (aperture, focal length, focal ratio) can be specified
- Program calculates the third parameter automatically
- Supports focal reducers and camera binning

**Database Management:**
- JavaScript format for telescope and camera specifications (telescopes-and-cameras.js)
- Python script reads the JS file and extracts the data structure
- Single source of truth shared between Python CLI and HTML web interface

## Code Conventions

**Naming Patterns:**
- Telescope parameters: `d1`/`d2` (diameter), `l1`/`l2` (length), `f1`/`f2` (focal ratio)
- Camera parameters: `c1h`/`c1v` (pixels), `c1p` (pixel size), `c1q` (quantum efficiency)
- Imperial units: `di1`/`di2` for diameter in inches
- Obstruction: `o1`/`o2` for central obstruction ratio

**Performance Metrics:**
- `res`: Pixel scale (arcsec/pixel)
- `eoi`: Extended object irradiance (for nebulae/galaxies)
- `poi`: Point object irradiance (for stars)
- `e`: Etendue (total light gathering)
- `pe`: Pixel etendue (per-pixel light gathering)
- `ps`: Pixel signal (QE and transmittance corrected)
- `os`: Object signal (for extended objects)

**Mathematical Foundation:**
All calculations follow rigorous astrophotography principles with proper handling of:
- Aperture area calculations including central obstructions
- Plate scale conversions (206.265 arcsec/radian factor)
- Quantum efficiency and transmittance corrections
- Comparative ratio calculations between telescopes