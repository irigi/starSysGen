import numpy as np
import random
import matplotlib.pyplot as plt
import os


def strip_non_ascii(string):
    """ Returns the string without non ASCII characters"""
    stripped = (c for c in string if 0 < ord(c) < 127)
    return ''.join(stripped)


def get_from_kepler():
    import kplr

    client = kplr.API()

    if os.path.isfile('planet_cache.npz'):
        with np.load('planet_cache.npz') as dat:
            plas = dat['planets']
    else:
        plas = client.planets(max_records='10000')
        np.savez_compressed('planet_cache.npz', planets=plas)

    print(len(plas))

    np.zeros(len(plas), dtype=[('kepler_name', 'O'),
                               ('period', 'f8'),
                               ('semi_major_axis', 'f8'),
                               ('stellar_age', 'f8'),
                               ('stellar_mass', 'f8'),
                               ('stellar_radius', 'f8'),
                               ('stellar_metallicity', 'f8'),
                               ('stellar_temperature', 'f8'),
                               ])

    # TODO: not finished, replaced by the open exoplanet catallogue, perhaps delete


def get_from_open_exoplanet_catallogue():
    import xml.etree.ElementTree as ET, urllib.request, gzip, io

    url = "https://github.com/OpenExoplanetCatalogue/oec_gzip/raw/master/systems.xml.gz"
    file = r'systems.xml.gz'
    #oec = ET.parse(gzip.GzipFile(fileobj=io.BytesIO(urllib.request.urlopen(url).read())))
    with open(file, 'rb') as f:
        oec = ET.parse(gzip.GzipFile(fileobj=f))

        planets = np.zeros(5000, dtype=[
            ('name', 'O'),
            ('semimajoraxis', 'f8'),
            ('eccentricity', 'f8'),
            ('period', 'f8'),
            ('mass', 'f8'),
            ('radius', 'f8'),
            ('discoverymethod', 'O'),
            ('star_metallicity', 'f8'),
            ('star_mass', 'f8'),
            ('star_radius', 'f8'),
            ('star_age', 'f8'),
            ('star_name', 'O'),
            ('star_spectraltype', 'O'),
        ])

        # Output distance to planetary system (in pc, if known) and number of planets in system
        NNN = 0
        for system in oec.findall(".//system"):

            # no binaries
            stars = [star for star in system.findall(".//star")]
            if len(stars) > 1:
                continue

            if len(stars) == 0:
                continue

            # Output mass and radius of all planets
            for planet in system.findall(".//planet"):
                for prop in [
                    'name',
                    'discoverymethod',
                    'semimajoraxis',
                    'eccentricity',
                    'period',
                    'mass',
                    'radius',
                ]:
                    try:
                        txt = planet.findtext(prop)
                        txt = None if txt == '' else txt
                        planets[NNN][prop] = txt
                    except UnicodeEncodeError:
                        txt = strip_non_ascii(txt)
                        planets[NNN][prop] = txt

                for prop in ['name', 'mass', 'radius', 'metallicity', 'spectraltype']:
                    try:
                        txt = stars[0].findtext(prop)
                        txt = None if txt == '' else txt
                        planets[NNN]['star_' + prop] = txt
                    except UnicodeEncodeError:
                        txt = strip_non_ascii(txt)
                        planets[NNN]['star_' + prop] = txt

                NNN += 1

        return planets[:NNN]
        print(NNN)


if __name__ == "__main__":
    np.random.seed(42)
    random.seed(42)

    planets = get_from_open_exoplanet_catallogue()

    for star in set(planets['star_name']):
        plas = planets[planets['star_name'] == star]
        # TODO: System extraction logic

    mask_rv = planets['discoverymethod'] == 'RV'
    mask_trasit = planets['discoverymethod'] == 'transit'

    ax = plt.gca()
    ax.set_yscale('log')
    ax.set_xscale('log')
    ax.set_xlabel('semi major axis [AU]')
    ax.set_ylabel('mass [Mjup]')
    ax.scatter(planets[mask_rv]['semimajoraxis'], planets[mask_rv]['mass'], label='radial velocity')
    ax.scatter(planets[mask_trasit]['semimajoraxis'], planets[mask_trasit]['mass'], label='transit')
    ax.legend()
    plt.show()

    print(set(planets['discoverymethod']))
    print(len(planets))
    print(len(planets[planets['discoverymethod'] == 'RV']))
    print(len(planets[planets['discoverymethod'] == 'transit']))
