# OptiSample: A/B Testing Infrastructure for AdTech

OptiSample is a Python-based statistical engine designed to handle the complexities of online advertising experimentation. Unlike standard A/B test calculators, this tool is built for high-traffic environments where uneven traffic allocation and multiple variant testing (A/B/n) are standard.

## 🚀 Features
* **Dual Metric Support:** Optimized for Conversion Rate (Bernoulli) and Earning Per Click (Continuous).
* **Multi-Variant Correction:** Built-in Bonferroni correction for `alpha` to control family-wise error rates.
* **Flexible Allocation:** Handles uneven traffic splits (e.g., 80% Control, 20% Variants) which is critical for risk mitigation in production.
* **Power Analysis:** Determine the exact sample size needed before launching a test to avoid "peeking" errors.

## 📊 How it Works

### 1. Power Analysis (Sample Size Calculation)
Before running a test, use the engine to calculate how many impressions you need:
```python
from src.engine import ExperimentEngine

engine = ExperimentEngine()
sizes = engine.calculate_sample_size(
    sm_type='cr',
    sm_control=0.02, # 2% baseline CR
    num_variants=2,
    control_traffic_share=0.70
)
print(sizes)
```

### 2. Post-Test Analysis
After the experiment concludes, determine if the observed lift is statistically significant.

```python
# For Conversion Rate results
results = engine.analyze_results(
    sm_type='cr',
    control_n=50000, control_conv=1200,
    variant_n=10000, variant_conv=310
)

# For Revenue (EPC) results
results = engine.analyze_results(
    sm_type='epc',
    c_mean=4.50, c_std=0.8, c_n=50000,
    v_mean=4.75, v_std=0.9, v_n=10000
)
print(f"Significant Increase: {bool(results['is_significant'])}")
