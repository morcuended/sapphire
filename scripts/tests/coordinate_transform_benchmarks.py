import datetime
import matplotlib.pyplot as plt
import numpy as np
import random as r

from sapphire.transformations import celestial, clock

def test_transformations():
    """
    This function numerically evaluates a number of preprogrammed
    values and the difference between our new and old transformations
    New values may be added to testcases
    :return: None

    Ethan van Woerkom is responsible for the benchmarking functions; refer to him for when something is unclear
    """
    # This tuple list contains all the used testcases for the test.
    # The meanings of the tuple entries are:
    # 0: latitude (deg) 1: longitude (deg) 2: utc_timestamp 3: J2000 RA (rad)
    # 4: J2000 DEC (rad) 5: horizontal az. (rad) 6: horizontal alt. (rad)
    # 7: source of test name
    testcases = [(48.86, 2.34, 1497003786, 0.8381070981, -0.5059006522, 3.26454625, 0.207694181, "stell. paris, alpha-for"),
                 (48.86, 2.34, 1497256975, 1.549728749, 0.1292784768, 1.969511946, 0.4898557422, "stell. paris, betelgeuse"),
                 (31.9633, -111.6, 2271646799, 0.05388704, 0.2650006125, 4.623697166, 0.66167856, "hor2eq IDL")]
    ARC_RAD = 2*np.pi / 360 / 3600 # one arcsecond in rad
    for i in testcases:
        print 'Transformation test using:'
        print 'lat, long:', i[0], i[1], 'utc_time:', i[2], 'RA, DEC:', i[3], i[4]
        print 'az, alt:', i[5], i[6], 'from source: ', i[7]

        t = celestial.equatorial_to_horizontal_astropy(i[0], i[1], i[2], [(i[3], i[4])])
        print "equatorial_to_horizontal_astropy gave: ", t[0]
        print "Should have been:                      ", (i[5],i[6])
        print "Difference (dAZ, dALT) (arcsec):       ", ((t[0][0]-i[5])/ARC_RAD,(t[0][1]-i[6])/ARC_RAD)

        t = celestial.horizontal_to_equatorial_astropy(i[0], i[1], i[2], [(i[5], i[6])])
        print "horizontal_to_equatorial_astropy gave: ", t[0]
        print "Should have been:                      ", (i[3],i[4])
        print "Difference (dAZ, dALT) (arcsec):       ", ((t[0][0]-i[3])/ARC_RAD,(t[0][1]-i[4])/ARC_RAD)

        # equatorial to horizontal is actually a zenithazimuth to horizontal
        t = celestial.equatorial_to_horizontal(i[0], i[1], clock.utc_to_gps(i[2]), i[3], i[4])
        print "equatorial_to_horizontal gave:         ", (t[1], t[0])
        a,b = celestial.horizontal_to_zenithazimuth(i[6], i[5])
        print "Should have been:                      ", (b,a)
        print "Difference (dAZ, dALT) (arcsec):       ", ((t[1] - b) / ARC_RAD, (t[0] - a) / ARC_RAD)

        t = celestial.horizontal_to_equatorial(i[0], clock.utc_to_lst(datetime.datetime.utcfromtimestamp(i[2]), i[1]), i[6], i[5])
        print "horizontal_to_equatorial (is zenaz):   ", (t[0],t[1])
        print "Should have been:                      ", (i[3], i[4])
        print "Difference (dAZ, dALT) (arcsec):       ", ((t[0] - i[3]) / ARC_RAD, (t[1] - i[4]) / ARC_RAD)

        print("\n")

def oldvsnew_diagram():
    """
    Visual accuracy comparisons of old and new transformations.
    Compares the correlations between the transformations:
    equatorial_to_horizontal and equatorial_to_zenith_azimuth_astropy
    horizontal_to_equatorial and horizontal_to_zenith_azimuth_astropy
    Makes a histogram of the error differences between these two functions as well
    The errors seem to be in the order of 1000 arcsec
    :return: None

    Ethan van Woerkom is responsible for the benchmarking functions; refer to him for when something is unclear
    """
    # make random frames, in correct angle range and from utc time 2000-2020
    frames = []
    # boxes for the four different transformation results
    etoha = []
    etoh = []
    htoe = []
    htoea = []
    straight = lambda x : x # straight trendline function

    # Create the data sets for eq to az
    for i in range(100):
        frames.append((r.uniform(-90, 90), r.uniform(-180,180), r.randint(946684800,1577836800), r.uniform(0, 2*np.pi), r.uniform(-0.5*np.pi,0.5*np.pi)))
    for i in frames:
        etoha.append(celestial.equatorial_to_zenithazimuth_astropy(i[0],i[1], i[2], [(i[3], i[4])])[0])
        etoh.append(celestial.equatorial_to_horizontal(i[0], i[1], clock.utc_to_gps(i[2]), i[3], i[4]))
    # Data sets for hor to eq
    for i in frames:
        htoe.append(celestial.horizontal_to_equatorial(i[0], clock.utc_to_lst(datetime.datetime.utcfromtimestamp(i[2]), i[1]), i[4], i[3]))
        htoea.extend(celestial.horizontal_to_equatorial_astropy(i[0], i[1], i[2], [(i[3], i[4])]))

    # Make figs eq -> zenaz
    plt.figure(1)
    plt.suptitle('Zen/Az correlation in rads (equatorial_to_zenithazimuth/horizontal)')

    zenrange = [0, np.pi]
    plt.subplot(211)
    plt.title('Zenith')
    plt.axis(zenrange*2)
    plt.xlabel('New (Astropy)')
    plt.ylabel('Old')

    # Make figure and add 1:1 trendline

    plt.plot([co[0] for co in etoha], [co[0] for co in etoh], 'r.', zenrange, straight(zenrange), '-')

    plt.subplot(212)
    plt.title('Azimuth')
    azrange = [-np.pi, np.pi]
    plt.axis(azrange*2)
    plt.xlabel('New (Astropy)')
    plt.ylabel('Old')
    # Make figure and add 1:1 trendline
    plt.plot([co[1] for co in etoha], [co[1] for co in etoh], 'b.', azrange, straight(azrange), '-')
    plt.tight_layout() # Prevent titles merging
    plt.subplots_adjust(top=0.85)

    # Make histogram of differences
    plt.figure(2)
    nieuw = (np.array(etoh)-np.array(etoha))/2/np.pi*360*3600 # Take difference and convert to arcsec
    plt.hist([i[0] for i in nieuw], bins = 20)
    plt.title('Zenith Old-New Error (equatorial_to_zenithazimuth/horizontal)')
    plt.xlabel('Error (arcsec)')
    plt.ylabel('Counts')

    plt.figure(3)
    plt.hist([i[1] for i in nieuw], bins=20)
    plt.title('Azimuth Old-New Error (equatorial_to_zenithazimuth/horizontal)')
    plt.xlabel('Error (arcsec)')
    plt.ylabel('Counts')

    # Make figs hor - > eq

    plt.figure(4)
    plt.suptitle('RA/DEC  correlation in rads (horizontal_to_equatorial)')
    altrange = [-0.5*np.pi, 0.5*np.pi]
    plt.subplot(211)
    plt.title('Declination')
    plt.axis(altrange * 2)
    plt.xlabel('New (Astropy)')
    plt.ylabel('Old')
    # Make figure and add 1:1 trendline
    plt.plot([co[1] for co in htoea], [co[1] for co in htoe], 'r.', altrange, straight(altrange), '-')

    plt.subplot(212)
    plt.title('Right Ascension')
    azrange = [0, 2*np.pi]
    plt.axis(azrange * 2)
    plt.xlabel('New (Astropy)')
    plt.ylabel('Old')
    # Make figure and add 1:1 trendline
    plt.plot([co[0] for co in htoea], [co[0] for co in htoe], 'b.', azrange, straight(azrange), '-')
    plt.tight_layout()  # Prevent titles merging
    plt.subplots_adjust(top = 0.85)

    # Make histogram of differences
    plt.figure(5)
    nieuw = (np.array(htoe) - np.array(htoea)) / 2 / np.pi * 360 * 3600  # Take difference and convert to arcsec
    plt.hist([i[1] for i in nieuw], bins=20)
    plt.title('Declination Old-New Error (horizontal_to_equatorial)')
    plt.xlabel('Error (arcsec)')
    plt.ylabel('Counts')

    plt.figure(6)
    nieuw = (np.array(htoe) - np.array(htoea)) / 2 / np.pi * 360 * 3600  # Take difference and convert to arcsec
    plt.hist([i[0] for i in nieuw], bins=20)
    plt.title('Right Ascension Old-New Error (horizontal_to_equatorial)')
    plt.xlabel('Error (arcsec)')
    plt.ylabel('Counts')

    plt.show()
    return

try:
    # This try-except block contains a pyephem accuracy benchmarking function.
    # It uses this structure to accommodate people without pyephem.
    import ephem
    def pyephem_comp():
        """
        This function compares the values from transformations done by our new astropy functions
        with the pyephem numbers. It generates correlation graphs between the new and old functions
        and histograms of the frequency of errors.
        Most errors do not much exceed 10 arcsec. There is complete correlation i.e. visually all points
        are on the same 1:1 line.
        These comparisons are done on the basis of 100 randomly generated points
        :return: None

        Ethan van Woerkom is responsible for the benchmarking functions; refer to him for when something is unclear
        """
        # Set up randoms equatorial J2000 bodies that we will convert the RAs/Decs of.
        eq = [] # random frames to use
        for i in range(100):
            eq.append((r.uniform(-90, 90), r.uniform(-180, 180), r.randint(946684800, 1577836800),
                           r.uniform(0, 2 * np.pi), r.uniform(-0.5 * np.pi, 0.5 * np.pi)))
        efemeq = [] # store pyephem transformations to equatorial
        altaz = [] # store pyephem transformations to altaz (horizontal)
        htoea = [] # store astropy transformations to equatorial
        etoha = [] # store astropy transformations to horizontal (altaz)
        for i in eq:
            # Calculate altaz
            # Set observer for each case
            obs = ephem.Observer()
            obs.lat = str(i[0])
            obs.lon = str(i[1])
            obs.date = datetime.datetime.utcfromtimestamp(i[2])
            obs.pressure = 0 # Crucial to prevent refraction correction!

            # Set body for each case
            coord = ephem.FixedBody()
            coord._ra = i[3]
            coord._dec = i[4]

            # Do calculation and add to list, it is necessary to force the coords into radians
            coord.compute(obs)
            altaz.append((float(coord.az),float(coord.alt)))

            # Also calculate efemeq using eq
            result = obs.radec_of(i[3], i[4])
            efemeq.append((float(result[0]), float(result[1])))

        # Produce horizontal_to_equatorial_astropy results
        for i in eq:
            result = celestial.horizontal_to_equatorial_astropy(i[0], i[1], i[2], [(i[3],i[4])])
            htoea.extend(result)

        # Produce equatorial_to_horizontal_astropy results
        for i in eq:
            result = celestial.equatorial_to_horizontal_astropy(i[0], i[1], i[2], [(i[3], i[4])])
            etoha.extend(result)

        altdecrange = [-0.5*np.pi, 0.5*np.pi]
        azrarange = [0, 2*np.pi]

        plt.figure(1)
        plt.suptitle('RA/Dec correlation Altaz->(Astropy/Pyephem)->RA,DEC')

        # Create RA correlation subplot
        plt.subplot(211)
        plt.title('RA')
        plt.axis(azrarange*2)
        plt.xlabel('Pyephem RA (rad)')
        plt.ylabel('Astropy RA (rad)')

        # Plot RA correlation and trendline
        plt.plot([co[0] for co in efemeq], [co[0] for co in htoea], 'b.', azrarange, azrarange, '-')

        # DEC correlation subplot
        plt.subplot(212)
        plt.title('DEC')
        plt.axis(altdecrange*2)
        plt.xlabel('Pyephem DEC (rad)')
        plt.ylabel('Astropy DEC (rad)')

        # Plot DEC correlation and trendline
        plt.plot([co[1] for co in efemeq], [co[1] for co in htoea], 'r.', altdecrange, altdecrange, '-')

        # Formatting
        plt.tight_layout()
        plt.subplots_adjust(top=0.85)

        # Make RA error histogram
        plt.figure(2)
        plt.title('RA Error Altaz->(Astropy/Pyephem)->RA,DEC')
        nieuw = (np.array(htoea) - np.array(efemeq))/2/np.pi* 360 * 3600 # Get differences in arcsec
        plt.hist([co[0] for co in nieuw], bins=20)

        plt.ylabel('Counts')
        plt.xlabel('Error (arcsec)')

        # Make DEC error histogram
        plt.figure(3)
        plt.title('DEC Error Altaz->(Astropy/Pyephem)->RA,DEC')
        plt.hist([co[1] for co in nieuw], bins=20)

        plt.ylabel('Counts')
        plt.xlabel('Error (arcsec)')

        # Altaz comparison plot
        plt.figure(4)
        plt.suptitle('Alt/Az correlation RA,DEC->(pyephem/astropy)->Altaz')

        # Altitude
        plt.subplot(211)
        plt.title('Altitude')
        plt.axis(altdecrange*2)
        plt.xlabel('Pyephem Altitude (rad)')
        plt.ylabel('Astropy Altitude (rad')

        # Plot with trendline
        plt.plot([co[1] for co in altaz], [co[1] for co in etoha], 'b.', altdecrange, altdecrange, '-')

        # Azimuth
        plt.subplot(212)
        plt.title('Azimuth')
        plt.axis(azrarange*2)
        plt.xlabel('Pyephem Azimuth (rad)')
        plt.ylabel('Astropy Azimuth (rad)')

        plt.plot([co[0] for co in altaz], [co[0] for co in etoha], 'r.', azrarange, azrarange, '-')

        # Formatting
        plt.tight_layout()
        plt.subplots_adjust(top=0.85)

        # Alt error histogram
        plt.figure(5)
        plt.title('Altitude Error RA,DEC->(pyephem/astropy)->Altaz')
        nieuw = (np.array(etoha)-np.array(altaz))/2/np.pi*360*3600
        plt.hist([co[1] for co in nieuw], bins=20)

        plt.ylabel('Counts')
        plt.xlabel('Error (arcsec)')

        # Az error histogram
        plt.figure(6)
        plt.title('Azimuth Error RA,DEC->(pyephem/astropy)->Altaz')
        plt.hist([co[0] for co in nieuw], bins=20)

        plt.ylabel('Counts')
        plt.xlabel('Error (arcsec)')
        # Done; output
        plt.show()


except ImportError:
    # Pyephem is not required so there is a case for when it is not present
    def pyephem_comp():
        print "Pyephem not present; no comparisons will be done"
