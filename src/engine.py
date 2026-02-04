import logging
import numpy as np
from scipy import stats
from statsmodels.stats.power import NormalIndPower
from statsmodels.stats.proportion import proportion_effectsize, proportions_ztest
from typing import Dict, Optional, Union

# Configuration for logging
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)

class ExperimentEngine:
    """
    Statistical engine for designing and analyzing A/B/n tests.
    Specialized for landing page forms and AdTech revenue metrics.
    """

    @staticmethod
    def calculate_sample_size(
        sm_type: str,
        sm_control: float,
        std_dev_control: Optional[float] = None,
        mde_relative: Optional[float] = None,
        power: float = 0.8,
        alpha: float = 0.05,
        control_traffic_share: float = 0.8,
        num_variants: int = 1
    ) -> Dict[str, int]:
        """
        Calculates required sample size per group using power analysis.
        Accounts for Bonferroni correction for multiple variants.
        """
        # --- Validation ---
        if not (0 < power < 1 and 0 < alpha < 1):
            raise ValueError("Power and alpha must be between 0 and 1.")
        
        # Adjusting Alpha for Multiple Comparisons (Bonferroni)
        adjusted_alpha = alpha / num_variants
        
        # Default MDE assignments
        if mde_relative is None:
            mde_mapping = {'cr': 0.05, 'epc': 0.10}
            mde_relative = mde_mapping.get(sm_type)
            if mde_relative is None:
                raise ValueError(f"Unknown sm_type: {sm_type}")

        mde_absolute = sm_control * mde_relative
        
        # Traffic Ratio Calculation (N_variant / N_control)
        variant_share = (1.0 - control_traffic_share) / num_variants
        ratio = variant_share / control_traffic_share

        analysis = NormalIndPower()

        if sm_type == 'cr':
            effect_size = proportion_effectsize(sm_control, sm_control + mde_absolute)
        elif sm_type == 'epc':
            if not std_dev_control:
                raise ValueError("std_dev_control is required for EPC calculations.")
            effect_size = mde_absolute / std_dev_control
        else:
            raise ValueError("sm_type must be 'cr' or 'epc'")

        n_control = analysis.solve_nobs_two_indep(
            effect_size=effect_size, alpha=adjusted_alpha, 
            power=power, ratio=ratio, alternative='larger'
        )

        return {
            'control_sample_size': int(np.ceil(n_control)),
            'variant_sample_size_per_variant': int(np.ceil(n_control * ratio))
        }

    @staticmethod
    def analyze_results(
        sm_type: str,
        alpha: float = 0.05,
        **kwargs
    ) -> Optional[Dict[str, Union[int, float]]]:
        """
        Computes p-values and determines statistical significance.
        """
        try:
            if sm_type == 'cr':
                # Expected kwargs: control_n, control_conv, variant_n, variant_conv
                stat, p_val = proportions_ztest(
                    count=[kwargs['variant_conv'], kwargs['control_conv']],
                    nobs=[kwargs['variant_n'], kwargs['control_n']],
                    alternative='larger'
                )
                diff = (kwargs['variant_conv']/kwargs['variant_n']) - (kwargs['control_conv']/kwargs['control_n'])
            
            elif sm_type == 'epc':
                # Expected kwargs: c_mean, c_std, c_n, v_mean, v_std, v_n
                stat, p_val = stats.ttest_ind_from_stats(
                    mean1=kwargs['v_mean'], std1=kwargs['v_std'], nobs1=kwargs['v_n'],
                    mean2=kwargs['c_mean'], std2=kwargs['c_std'], nobs2=kwargs['c_n'],
                    equal_var=False, alternative='greater'
                )
                diff = kwargs['v_mean'] - kwargs['c_mean']
            
            return {
                'is_significant': 1 if p_val < alpha else 0,
                'p_value': round(p_val, 4),
                'observed_diff': round(diff, 4)
            }
        except Exception as e:
            logger.error(f"Analysis failed: {e}")
            return None
