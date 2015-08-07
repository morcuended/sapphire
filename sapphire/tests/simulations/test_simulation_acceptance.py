import os
import unittest
import warnings

from sapphire.tests.validate_results import validate_results
from perform_simulation import (create_tempfile_path,
                                perform_groundparticlessimulation,
                                perform_flatfrontsimulation,
                                test_data_path, test_data_flat)


class GroundparticlesSimulationAcceptanceTest(unittest.TestCase):

    def setUp(self):
        warnings.filterwarnings('ignore')

    def tearDown(self):
        warnings.resetwarnings()

    def test_simulation_output(self):
        """Perform a simulation and verify the output"""

        output_path = create_tempfile_path()
        perform_groundparticlessimulation(output_path)
        validate_results(self, test_data_path, output_path)
        os.remove(output_path)


class FlatFrontSimulationAcceptanceTest(unittest.TestCase):

    def test_simulation_output(self):
        """Perform a simulation and verify the output"""

        output_path = create_tempfile_path()
        perform_flatfrontsimulation(output_path)
        validate_results(self, test_data_flat, output_path)
        os.remove(output_path)


if __name__ == '__main__':
    unittest.main()
