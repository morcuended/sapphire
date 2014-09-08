"""Perform simple simulations for timing

Throw a flat shower front on a cluster from various angles.
Simulate just the arrival times.

Example usage::

    import tables

    from sapphire.simulations.showerfront import FlatFrontSimulation
    from sapphire.clusters import ScienceParkCluster

    data = tables.open_file('/tmp/test_showerfront_simulation.h5', 'w')
    cluster = ScienceParkCluster()

    sim = FlatFrontSimulation(cluster, data, '/', 200)
    sim.run()

"""
from math import pi, sin, cos, tan, floor

import numpy as np

from .detector import HiSPARCSimulation
from ..utils import pbar


class FlatFrontSimulation(HiSPARCSimulation):

    def __init__(self, *args, **kwargs):
        super(FlatFrontSimulation, self).__init__(*args, **kwargs)

        for station in self.cluster.stations:
            station.gps_offset = self.simulate_station_offset()
            for detector in station.detectors:
                detector.offset = self.simulate_detector_offset()

        # Store updated version of the cluster
        self.coincidence_group._v_attrs.cluster = self.cluster

        # Since the cluster is not rotated detector positions can be stored.
        for station in self.cluster.stations:
            for detector in station.detectors:
                detector.cylindrical_coordinates = \
                    detector.get_cylindrical_coordinates()

    def generate_shower_parameters(self):
        """Generate shower parameters, i.e. azimuth and zenith angles.

        For this groundparticles simulation, only the shower core position
        and rotation angle of the shower are generated.  Do *not*
        interpret these parameters as the position of the cluster, or the
        rotation of the cluster!  Interpret them as *shower* parameters.

        :returns: dictionary with shower parameters: core_pos
                  (x, y-tuple) and azimuth.

        """
        for i in pbar(range(self.N)):
            shower_parameters = {'ext_timestamp': (int(1e9) + i) * int(1e9),
                                 'azimuth': self.generate_azimuth(),
                                 'zenith': self.generate_zenith(),
                                 'core_pos': (None, None),
                                 'size': None,
                                 'energy': None}

            yield shower_parameters

    def simulate_detector_response(self, detector, shower_parameters):
        """Simulate detector response to a shower.

        Return the arrival time of shower front passing the center of
        the detector.

        """
        arrival_time = self.simulate_adc_sampling(
                           self.get_arrival_time(detector, shower_parameters) +
                           self.simulate_signal_transport_time(1)[0] +
                           detector.offset)
        observables = {'t': arrival_time}

        return observables

    def get_arrival_time(self, detector, shower_parameters):
        """Calculate arrival time

        Assumes a flat shower front and core position to be
        the center of the cluster.

        Equation based on Fokkema2012 sec 4.2, eq 4.9.
        With additions to account for altitude.
        (DOI: 10.3990/1.9789036534383)
        The directional vector c * dt should be negative,
        not apparent in Fokkema2012 fig 4.4.


        :returns: Shower front arrival time in ns.

        """
        c = 0.3
        r1, phi1, z1 = detector.cylindrical_coordinates
        phi = shower_parameters['azimuth']
        theta = shower_parameters['zenith']
        r = r1 * cos(phi - phi1) - z1 * tan(theta)
        cdt = - (r * sin(theta) + z1 / cos(theta))
        dt = cdt / c
        return dt

    def simulate_gps(self, station_observables, shower_parameters, station):
        """Simulate gps timestamp

        Ensure that all detector arrival times are positive.

        """
        n_detectors = len(station.detectors)
        ids = range(1, n_detectors + 1)
        arrival_times = [station_observables['t%d' % id] for id in ids]
        ext_timestamp = shower_parameters['ext_timestamp']

        first_time = sorted(arrival_times)[0]
        for id in ids:
            station_observables['t%d' % id] -= first_time

        arrival_times = [station_observables['t%d' % id] for id in ids]
        trigger_time = sorted(arrival_times)[1]
        station_observables['t_trigger'] = trigger_time

        ext_timestamp += int(first_time + trigger_time + station.gps_offset +
                             self.simulate_gps_uncertainty())
        timestamp = int(ext_timestamp / int(1e9))
        nanoseconds = int(ext_timestamp % int(1e9))

        gps_timestamp = {'ext_timestamp': ext_timestamp,
                         'timestamp': timestamp, 'nanoseconds': nanoseconds}
        station_observables.update(gps_timestamp)

        return station_observables


class FlatFrontSimulationWithoutErrors(FlatFrontSimulation):

    """This simulation does not simulate errors/uncertainties

    This should result in perfect timing for the detectors.

    """

    def simulate_detector_response(self, detector, shower_parameters):
        """Simulate detector response to a shower.

        Return the arrival time of shower front passing the center of
        the detector.

        """
        arrival_time = self.get_arrival_time(detector, shower_parameters)
        observables = {'t': arrival_time}

        return observables

    def simulate_detector_offset(self):
        """Disable detector offsets"""

        return 0.

    def simulate_station_offset(self):
        """Disable station offsets"""

        return 0.

    def simulate_gps_uncertainty(self):
        """Disable GPS uncertainty"""

        return 0.


class FlatFrontSimulation2D(FlatFrontSimulation):

    """This simualtion ignores detector altitudes."""

    def get_arrival_time(self, detector, shower_parameters):
        """Calculate arrival time

        Ignore detector altitudes

        Equation based on Fokkema2012 sec 4.2, eq 4.9.
        (DOI: 10.3990/1.9789036534383)

        """
        c = 0.3
        r1, phi1, _ = detector.cylindrical_coordinates
        phi = shower_parameters['azimuth']
        theta = shower_parameters['zenith']
        r = r1 * cos(phi - phi1)
        cdt = -r * sin(theta)
        dt = cdt / c
        return dt

class FlatFrontSimulation2DWithoutErrors(FlatFrontSimulation2D,
                                         FlatFrontSimulationWithoutErrors):

    """Ignore altitude of detectors and do not simulate errors."""

    pass
