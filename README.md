# neuroneq
A GUI-based python tool to visualize equations used in simulated neurons.

## Code example

Easily convert from alpha/beta to tau/inf

```
import matplotlib.pyplot as plt
from neuroneq import ab2inf_tau, fit_inf
import numpy as np

alpha = "((v+45)/10)/(1-exp(-(v+45)/10))"
beta = "4*exp(-(v+70)/18)"

# convert to inf, tau
inf, tau = ab2inf_tau(alpha,beta)

# fit the equation to standard form
fit_equation = fit_inf(inf)

print(fit_equation)
# 1.0/(1.0+(exp((v+44.57)/(-9.55))))

# plot
min_v, max_v = -100, 50
v = np.linspace(float(min_v),float(max_v),2000)
fit_equation_np = fit_equation.replace("exp(","np.exp(")
y = eval(fit_equation_np)
plt.plot(v, y, 'r-',label="fit")
plt.show()

```