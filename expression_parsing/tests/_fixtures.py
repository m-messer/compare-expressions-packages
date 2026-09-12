"""Test fixtures vendored from compareExpressions app/tests/symbolic_evaluation_test.py.

elementary_function_test_cases: (name, input, ?, expected_latex) tuples used by
test_symbolic_preview.test_elementary_functions_preview.
"""

elementary_function_test_cases = [
    ("sin", "Bsin(pi)", "0", r"B \cdot \sin{\left(\pi \right)}"),
    ("sinc", "Bsinc(0)", "B", r"B \cdot 1"),  # r"B \sinc{\left(0 \right)}"
    ("csc", "Bcsc(pi/2)", "B", r"B \cdot \csc{\left(\frac{\pi}{2} \right)}"),
    ("cos", "Bcos(pi/2)", "0", r"B \cdot \cos{\left(\frac{\pi}{2} \right)}"),
    ("sec", "Bsec(0)", "B", r"B \cdot \sec{\left(0 \right)}"),
    ("tan", "Btan(pi/4)", "B", r"B \cdot \tan{\left(\frac{\pi}{4} \right)}"),
    ("cot", "Bcot(pi/4)", "B", r"B \cdot \cot{\left(\frac{\pi}{4} \right)}"),
    ("asin", "Basin(1)", "B*pi/2", r"B \cdot \operatorname{asin}{\left(1 \right)}"),
    ("acsc", "Bacsc(1)", "B*pi/2", r"B \cdot \operatorname{acsc}{\left(1 \right)}"),
    ("acos", "Bacos(1)", "0", r"B \cdot \operatorname{acos}{\left(1 \right)}"),
    ("asec", "Basec(1)", "0", r"B \cdot \operatorname{asec}{\left(1 \right)}"),
    ("atan", "Batan(1)", "B*pi/4", r"B \cdot \operatorname{atan}{\left(1 \right)}"),
    ("acot", "Bacot(1)", "B*pi/4", r"B \cdot \operatorname{acot}{\left(1 \right)}"),
    ("atan2", "Batan2(1,1)", "B*pi/4", r"\frac{\pi}{4} \cdot B"),  # r"B \operatorname{atan2}{\left(1,1 \right)}"
    ("sinh", "Bsinh(x)+Bcosh(x)", "B*exp(x)", r"B \cdot \sinh{\left(x \right)} + B \cdot \cosh{\left(x \right)}"),
    ("cosh", "Bcosh(1)", "B*cosh(-1)", r"B \cdot \cosh{\left(1 \right)}"),
    # ("tanh", "2Btanh(x)/(1+tanh(x)^2)", "B*tanh(2*x)", r"\frac{2 \cdot B \cdot \tanh{\left(x \right)}}{\tanh^{2}{\left(x \right)} + 1}"),  # Ideally this case should print tanh(x)^2 instead of tanh^2(x)
    ("csch", "Bcsch(x)", "B/sinh(x)", r"B \cdot \operatorname{csch}{\left(x \right)}"),
    ("sech", "Bsech(x)", "B/cosh(x)", r"B \cdot \operatorname{sech}{\left(x \right)}"),
    ("asinh", "Basinh(sinh(1))", "B", r"B \cdot \operatorname{asinh}{\left(\sinh{\left(1 \right)} \right)}"),
    ("acosh", "Bacosh(cosh(1))", "B", r"B \cdot \operatorname{acosh}{\left(\cosh{\left(1 \right)} \right)}"),
    ("atanh", "Batanh(tanh(1))", "B", r"B \cdot \operatorname{atanh}{\left(\tanh{\left(1 \right)} \right)}"),
    (
        "asech",
        "Bsech(asech(1))",
        "B",
        r"B \cdot \operatorname{sech}{\left(\operatorname{asech}{\left(1 \right)} \right)}",
    ),
    ("exp", "Bexp(x)exp(x)", "B*exp(2*x)", r"B \cdot e^{x} \cdot e^{x}"),
    ("exp2", "a+b*E^2", "a+b*exp(2)", r"a + b \cdot e^{2}"),
    ("exp3", "a+b*e^2", "a+b*exp(2)", r"a + b \cdot e^{2}"),
    ("ln", "Bexp(ln(10))", "10B", r"B \cdot e^{\ln{\left(10 \right)}}"),
    ("log10", "B*10^(log(10,10))", "10B", r"10^{\log_{10}{\left(10 \right)}} \cdot B"),
    ("logb", "B*b^(log(a,b))", "aB", r"B \cdot b^{\log_{b}{\left(a \right)}}"),
    ("sqrt", "Bsqrt(4)", "2B", r"\sqrt{4} \cdot B"),
    ("sign", "Bsign(1)", "B", r"B \cdot \operatorname{sign}{\left(1 \right)}"),
    ("abs", "BAbs(-2)", "2B", r"B \cdot \left|{-2}\right|"),
    ("Max", "BMax(0,1)", "B", r"B \cdot 1"),  # r"B \max{\left(0,1 \right)}"
    ("Min", "BMin(1,2)", "B", r"B \cdot 1"),  # r"B \min{\left(1,2 \right)}"
    ("arg", "Barg(1)", "0", r"B \cdot \arg{\left(1 \right)}"),
    ("ceiling", "Bceiling(0.6)", "B", r"B \cdot 1"),  # r"B \left\lceil 0.6 \right\rceil"),
    ("floor", "Bfloor(0.6)", "0", r"B \cdot 0"),  # r"B \left\lfloor 0.6 \right\rfloor"),
    (
        "MECH50001_7.2",
        "fs/(1-Mcos(theta))",
        "fs/(1-M*cos(theta))",
        r"\frac{f \cdot s}{1 - M \cdot \cos{\left(\theta \right)}}",
    ),
]
