import unittest
from pysoundlocalization.core.Simulation import Simulation


class TestSimulation(unittest.TestCase):
    def setUp(self):
        pass

    def test_simulation(self):
        simulation = Simulation()
        self.assertEqual(simulation.rooms, [])


if __name__ == "__main__":
    unittest.main()
