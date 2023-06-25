import numpy as np
from scipy.optimize import curve_fit
import sympy

def ab2inf_tau(alpha:str, beta:str, simplify:bool=True) -> tuple:
    """
    Takes the alpha and beta equations and returns
    the (inf, tau) symbolic equations
    """

    inf_expression = alpha + "/( " + alpha + " + " + beta + ")"
    tau_expression = "1/( " + alpha + " + " + beta + ")"
    
    if simplify:
        return str(sympy.simplify(inf_expression)), str(sympy.simplify(tau_expression))
    else:
        return inf_expression, tau_expression
    
    #np.linspace(float(self.min_row.value()),float(self.max_row.value()),2000)


def fit_inf(inf_expression:str, min_v=-100, max_v=50) -> str:
    """
    Convert an "ugly" inf equation to the standard format
    """
    v = np.linspace(float(min_v),float(max_v),2000)

    inf_expression_np = inf_expression.replace("exp(","np.exp(")
    y = eval(inf_expression_np)

    def inf_func(v,vh,tau):
        return 1.0/(1.0+(np.exp((v+vh)/(tau))))

    popt_n, pcov_n = curve_fit(inf_func, v, y, bounds=((-1000,-1000),(1000,-0.00001)))
    popt_p, pcov_p = curve_fit(inf_func, v, y, bounds=((-1000,0.00001),(1000,1000)))

    resid_n = np.linalg.norm(y-inf_func(v, *popt_n))
    resid_p = np.linalg.norm(y-inf_func(v, *popt_p))

    if resid_n <= resid_p:
        popt = popt_n
    else:
        popt = popt_p

    inf_func_vh = round(popt[0],2)
    inf_func_tau = round(popt[1],2)
    inf_func_str = "1.0/(1.0+(exp((v+" + str(inf_func_vh) + ")/("+ str(inf_func_tau)+"))))"

    return inf_func_str