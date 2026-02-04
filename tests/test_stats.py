import unittest
from src.engine import ExperimentEngine

class TestOptiSample(unittest.TestCase):
    def setUp(self):
        self.engine = ExperimentEngine()

    def test_sample_size_output(self):
        """Verify that sample size calculation returns integers."""
        res = self.engine.calculate_sample_size(sm_type='cr', sm_control=0.02)
        self.assertIsInstance(res['control_sample_size'], int)
        self.assertIsInstance(res['variant_sample_size_per_variant'], int)

    def test_cr_significance(self):
        """Verify that a clear winner is marked as significant."""
        # 10% CR vs 2% CR should be highly significant
        res = self.engine.analyze_results(
            sm_type='cr',
            control_n=1000, control_conv=20,
            variant_n=1000, variant_conv=100
        )
        self.assertEqual(res['is_significant'], 1)

    def test_epc_insignificance(self):
        """Verify that identical revenue means are not significant."""
        res = self.engine.analyze_results(
            sm_type='epc',
            c_mean=5.0, c_std=1.0, c_n=100,
            v_mean=5.0, v_std=1.0, v_n=100
        )
        self.assertEqual(res['is_significant'], 0)

if __name__ == '__main__':
    unittest.main()
