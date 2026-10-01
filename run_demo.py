"""Dream-RSI vs Recursive Fixed Exploration on a synthetic discovery agent."""
from dream_rsi import dream_rsi
from dream_rsi.replay import Coeffs

C = Coeffs(beta1=0.002, beta2=0.0)
for seed in range(3):
    kw = dict(rounds=5, workers=10, k1=11, k2=11, m_versions=12, coeffs=C)
    for name, adapt in [("fixed", False), ("dream", True)]:
        r = dream_rsi(adapt=adapt, make_agent=lambda t, s=seed: __import__("dream_rsi.synthetic", fromlist=["x"]).SyntheticAgent(seed=s * 100 + t), **kw)
        bests = [f"{l.online_best - C.beta1 * l.online_requests:.3f} (best {l.online_best:.2f}, N={l.online_requests})" for l in r.logs]
        print(f"seed{seed} {name:5s} online V=best-beta1*N per round: {bests}")
    print("   final policy:", r.policy.describe())
