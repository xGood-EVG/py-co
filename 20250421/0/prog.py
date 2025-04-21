def sqroots(coeffs: str) -> str:
    a, b, c = list(map(int, coeffs.split()))
    d = b*b - 4*a*c
    if d < 0:
        return ""
    x1 = (-b + d**0.5) / (2*a)
    x2 = (-b - d**0.5) / (2*a)
    if x1 == x2:
        return f"{x1}"
    return f"{x1} {x2}"

