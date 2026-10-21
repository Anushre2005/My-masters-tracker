"""Quant course: a tutor-style path through GRE quant, one chapter at a time.

Each chapter has a short lesson (concept -> worked example revealed step by step -> "your turn"
question), a timed chapter test, and belongs to a unit with a combined unit test. There are also
GRE-style adaptive section simulations and a weak-spot drill.

Questions come from templates that pick fresh numbers every time; the answer and the explanation
are computed from the same numbers, so retakes never repeat. Chapter tests also mix in the
hand-written questions from gre_quiz.BANK.
"""
import math
import random
from collections import Counter
from fractions import Fraction as F

from . import gre_plan, gre_quiz

QC_CHOICES = gre_quiz.QC
NAMES = ['Priya', 'Arjun', 'Meera', 'Rahul', 'Sara', 'Kabir', 'Anita', 'Dev', 'Nisha', 'Omar']
PRIMES = [p for p in range(2, 200) if all(p % d for d in range(2, int(p ** .5) + 1))]

# ====================================================================== formatting helpers
_SUP = str.maketrans('0123456789-+', '⁰¹²³⁴⁵⁶⁷⁸⁹⁻⁺')


def sup(v):
    return str(v).translate(_SUP)


def pw(b, e):
    """b to the power e, written with a superscript (no superscript for e = 1)."""
    return f'{b}{sup(e)}' if e != 1 else str(b)


def num(v):
    """Integer with thousands commas or a fraction a/b, with a real minus sign."""
    v = F(v)
    if v.denominator == 1:
        s = f'{abs(v.numerator):,}'
    else:
        s = f'{abs(v.numerator)}/{v.denominator}'
    return ('−' if v < 0 else '') + s


def dec(v):
    """Exact decimal for terminating fractions (0.125); otherwise a fraction."""
    v = F(v)
    d = v.denominator
    while d % 2 == 0:
        d //= 2
    while d % 5 == 0:
        d //= 5
    if d != 1:
        return num(v)
    a = abs(v)
    ip = a.numerator // a.denominator
    rem = a - ip
    digits = ''
    while rem:
        rem *= 10
        k = rem.numerator // rem.denominator
        digits += str(k)
        rem -= k
    return ('−' if v < 0 else '') + f'{ip:,}' + ('.' + digits if digits else '')


def pct(v):
    """A percent value (already ×100): 20 -> '20%', 100/3 -> '33 1/3%'."""
    v = F(v)
    d = v.denominator
    while d % 2 == 0:
        d //= 2
    while d % 5 == 0:
        d //= 5
    if d == 1:
        return dec(v) + '%'
    w = v.numerator // v.denominator
    f = v - w
    return f'{w} {f.numerator}/{f.denominator}%' if w else f'{f.numerator}/{f.denominator}%'


def pn(v):
    """Number in brackets when negative, for use after an operator: 3 − (−2)."""
    return num(v) if F(v) >= 0 else f'({num(v)})'


def money(v):
    v = F(v)
    return '$' + (f'{v.numerator // v.denominator:,}' if v.denominator == 1 else f'{float(v):,.2f}')


def term(v, var=''):
    """Signed term for the middle of an expression: ' + 3x', ' − x', ' − 7'."""
    v = F(v)
    if v == 0:
        return ''
    a = abs(v)
    body = (num(a) if (a != 1 or not var) else '') + var
    return (' + ' if v > 0 else ' − ') + body


def lead(v, var=''):
    """First term of an expression: '3x', '−x', '5'."""
    v = F(v)
    a = abs(v)
    body = (num(a) if (a != 1 or not var) else '') + var
    return ('−' if v < 0 else '') + body


def poly(a, b, c, var='x'):
    return lead(a, var + '²') + term(b, var) + term(c)


def lin(p, var='x', a=1):
    """(ax + p)."""
    return f'({lead(a, var)}{term(p)})'


def factor(n):
    out, p = {}, 2
    while p * p <= n:
        while n % p == 0:
            out[p] = out.get(p, 0) + 1
            n //= p
        p += 1
    if n > 1:
        out[n] = out.get(n, 0) + 1
    return out


def fstr(n):
    return ' × '.join(pw(p, e) for p, e in sorted(factor(n).items()))


# ====================================================================== question builders
def _isint(v):
    return F(v).denominator == 1


def mc(q, right, wrong, x, show=num, step=None, pos=False, hi=None, ints=True):
    """Numeric multiple choice. `wrong` = values from likely mistakes; topped up with nearby values.
    Choices are listed in increasing order, as on the GRE."""
    R = F(right)
    vals, seen = [R], {show(R)}

    def add(v):
        if v is None or len(vals) >= 5:
            return
        v = F(v)
        if (pos and v <= 0) or (hi is not None and v > hi) or (ints and _isint(R) and not _isint(v)):
            return
        if step and any(abs(v - u) < F(step) * F(7, 10) for u in vals):
            return
        s = show(v)
        if s not in seen:
            vals.append(v)
            seen.add(s)

    for w in wrong:
        add(w)
    st = F(step) if step else (F(1) if _isint(R) else F(1, R.denominator))
    if not step and abs(R) >= 40:
        st = F(max(1, round(abs(R) / 10)))
    k = 1
    while len(vals) < 5 and k < 60:
        add(R + k * st)
        add(R - k * st)
        k += 1
    vals.sort()
    return dict(kind='mc', q=q, c=[show(v) for v in vals], a=vals.index(R), x=x)


def mct(r, q, right, wrong, x):
    """Text multiple choice: the right answer is put at a random position among the wrong ones."""
    opts = [w for w in dict.fromkeys(wrong) if w != right][:4]
    i = r.randint(0, len(opts))
    opts.insert(i, right)
    return dict(kind='mc', q=q, c=opts, a=i, x=x)


def ne(q, v, x, show=num):
    """Numeric entry: the student types the answer (integers, decimals or a fraction like 3/4)."""
    v = F(v)
    d = v.denominator
    while d % 2 == 0:
        d //= 2
    while d % 5 == 0:
        d //= 5
    if d != 1:
        q += '\n(Enter your answer as a fraction, e.g. 7/3.)'
    return dict(kind='ne', q=q, a=show(v), v=[v.numerator, v.denominator], x=x)


def qc(given, a, b, ans, x):
    return dict(kind='qc', q=(given + '\n' if given else '') + f'Quantity A: {a}\nQuantity B: {b}', c=QC_CHOICES, a=ans, x=x)


def ma(r, q, items, x):
    """Select-all: items = [(text, is_right), ...]."""
    items = list(items)
    r.shuffle(items)
    return dict(kind='ma', q=q, c=[t for t, _ in items], a=[i for i, (_, ok) in enumerate(items) if ok], x=x)


GENS = {}  # chapter -> [(fn, difficulty 1-3, concept index)]


def gen(ch, diff, concept):
    def deco(fn):
        GENS.setdefault(ch, []).append((fn, diff, concept))
        return fn
    return deco


# ====================================================================== 1. Arithmetic & number sense
@gen('arithmetic', 1, 0)
def ar_pemdas(r):
    s, b = r.randint(2, 5), r.randint(2, 6)
    e = r.choice([k for k in range(2, 13) if b * s * s % k == 0])
    c = r.randint(-3, 6)
    d, a = c + s, r.randint(5, 30)
    t = b * s * s // e
    return mc(f'What is the value of {a} − {b} × ({num(c)} − {d})² ÷ {e}?', a - t,
              [F((a - b) * s * s, e), a + t, a - b * s * s, F(a - 2 * b * s, e)],
              f'Brackets first: {num(c)} − {d} = −{s}, and (−{s})² = {s * s}. Then × and ÷ from left to right: '
              f'{b} × {s * s} = {b * s * s}, and {b * s * s} ÷ {e} = {t}. Last, {a} − {t} = {num(a - t)}.')


@gen('arithmetic', 1, 1)
def ar_negpow(r):
    a, b, n, m = r.randint(2, 4), r.randint(2, 3), r.randint(2, 5), r.randint(2, 4)
    if r.random() < .5:
        v = (-a) ** n + (-b) ** m
        why = 'even power → positive' if n % 2 == 0 else 'odd power keeps the minus sign'
        return mc(f'(−{a}){sup(n)} + (−{b}){sup(m)} = ?', v, [a ** n + b ** m, -(a ** n) - b ** m, (-a) ** n - (-b) ** m, -(a ** n) + (-b) ** m],
                  f'(−{a}){sup(n)} = {num((-a) ** n)} ({why}); (−{b}){sup(m)} = {num((-b) ** m)}. Sum = {num(v)}.')
    v = -(a ** n) + (-b) ** m
    return mc(f'−{a}{sup(n)} + (−{b}){sup(m)} = ?', v, [(-a) ** n + (-b) ** m, a ** n + b ** m, -(a ** n) - (-b) ** m],
              f'Without brackets the power is done first, then the minus: −{a}{sup(n)} = −({a ** n}) = {num(-(a ** n))}. '
              f'With brackets, (−{b}){sup(m)} = {num((-b) ** m)}. Sum = {num(v)}.')


DEC_X = [F(1, 4), F(2, 5), F(3, 4), F(6, 5), F(1, 2), F(3, 2), F(4, 5), F(1, 5)]
DEC_Z = [F(1, 20), F(1, 50), F(1, 10), F(1, 4), F(1, 5), F(1, 25)]


@gen('arithmetic', 1, 2)
def ar_decimal(r):
    x, y, z = r.choice(DEC_X), r.choice(DEC_X), r.choice(DEC_Z)
    v = x * y / z
    return mc(f'{dec(x)} × {dec(y)} ÷ {dec(z)} = ?', v, [v * 10, v / 10, v * 100, x * y * z],
              f'{dec(x)} × {dec(y)} = {dec(x * y)}. Dividing by {dec(z)} is the same as multiplying by {num(1 / z)}: '
              f'{dec(x * y)} × {num(1 / z)} = {dec(v)}. Count decimal places carefully - most wrong answers are off by a factor of 10.', show=dec, ints=False)


AR_QC = [
    ('0 < x < 1', 'x²', 'x³', 0, 'For 0 < x < 1 each extra power makes the number smaller: x = 1/2 gives x² = 1/4 and x³ = 1/8.'),
    ('0 < x < 1', '√x', 'x', 0, 'Square-rooting a number between 0 and 1 makes it bigger: √(1/4) = 1/2 > 1/4.'),
    ('0 < x < 1', 'x', '1/x', 1, 'The reciprocal of a number between 0 and 1 is greater than 1: x = 1/2 gives 1/x = 2.'),
    ('−1 < x < 0', 'x³', 'x', 0, 'With x = −1/2: x³ = −1/8, which is greater than −1/2 (closer to zero).'),
    ('−1 < x < 0', 'x', 'x²', 1, 'x is negative but x² is positive, so x² is always greater.'),
    ('−1 < x < 0', '1/x', 'x', 1, 'With x = −1/2, 1/x = −2, which is less than −1/2. Reciprocals of numbers between −1 and 0 are below −1.'),
    ('x < −1', 'x³', 'x', 1, 'With x = −2: x³ = −8 < −2. Odd powers of numbers below −1 get more negative.'),
    ('x ≠ 0', 'x²', 'x', 3, 'x = 2 gives A = 4 > 2, but x = 1/2 gives A = 1/4 < 1/2. It depends on x → (D).'),
    ('x > 1', 'x²', 'x³', 1, 'For x > 1 higher powers are bigger: x = 2 gives 4 vs 8.'),
    ('0 < x < 1', 'x² − x', '0', 1, 'x² − x = x(x − 1): positive × negative = negative, so A < 0.'),
]


@gen('arithmetic', 2, 3)
def ar_qc(r):
    return qc(*r.choice(AR_QC))


@gen('arithmetic', 2, 3)
def ar_estimate(r):
    while True:
        a, c, e = r.randint(11, 60), r.randint(11, 60), r.choice([4, 5, 8, 10, 20, 25])
        if a * c % e == 0 and a * c // e >= 10:
            break
    A, C, E = (F(k * 10 + r.choice([-3, -2, -1, 1, 2, 3]), 10) for k in (a, c, e))
    v = a * c // e
    return mc(f'Which of the following is closest to ({dec(A)} × {dec(C)}) ÷ {dec(E)}?', v,
              [round(F(v, 10)), round(F(v, 3)), v * 3, v * 10], f'Round each number: {a} × {c} ÷ {e} = {a * c} ÷ {e} = {v}. '
              'The true value is very close; the other choices are far away. On the GRE, glance at how far apart the choices are before calculating.', pos=True)


AR_SIGN = {'y − x': (True, 'positive minus negative = positive'), 'xy': (False, 'negative × positive = negative'),
           'x²y': (True, 'x² is positive, times positive y'), 'x/y': (False, 'negative ÷ positive = negative'),
           'y² − x': (True, 'positive minus a negative = positive'), 'x + y': (False, 'depends on which is bigger in size'),
           '−x/y': (True, '−x is positive, ÷ positive y'), 'x³y': (False, 'x³ is negative'), 'xy²': (False, 'negative × positive')}


@gen('arithmetic', 2, 1)
def ar_signs(r):
    pick = r.sample(list(AR_SIGN), 5)
    if not any(AR_SIGN[k][0] for k in pick):
        pick[0] = 'y − x'
    return ma(r, 'If x < 0 < y, which of the following must be positive?\n(Select ALL that apply.)', [(k, AR_SIGN[k][0]) for k in pick],
              'Track the signs (x negative, y positive): ' + '; '.join(f'{k}: {AR_SIGN[k][1]}' for k in pick) + '.')


# ====================================================================== 2. Fractions & decimals
def _frac(r, dens, top=4):
    while True:
        f = F(r.randint(1, top), r.choice(dens))
        if f.denominator > 1:
            return f


@gen('fractions', 1, 0)
def fr_ops(r):
    while True:
        p, q, s = _frac(r, [2, 3, 4, 5, 6, 8]), _frac(r, [2, 3, 4, 5, 6, 8]), _frac(r, [2, 3, 4, 5, 6], 5)
        v = (p + q) / s
        if v != 1 / v and p != q:
            break
    naive = F(p.numerator + q.numerator, p.denominator + q.denominator) / s
    return mc(f'({num(p)} + {num(q)}) ÷ ({num(s)}) = ?', v, [(p + q) * s, naive, 1 / v, p + q],
              f'Common denominator first: {num(p)} + {num(q)} = {num(p + q)}. Dividing by {num(s)} means multiplying by its reciprocal {num(1 / s)}: '
              f'{num(p + q)} × {num(1 / s)} = {num(v)}.')


_FRACS = sorted({F(n, d) for d in range(3, 16) for n in range(1, d)})


@gen('fractions', 2, 1)
def fr_compare(r):
    while True:
        lo = F(r.randint(45, 70), 100)
        cand = [f for f in _FRACS if lo <= f <= lo + F(15, 100)]
        if len(cand) >= 5:
            break
    pick = r.sample(cand, 5)
    big = r.random() < .5
    right = max(pick) if big else min(pick)
    return mct(r, f'Which of the following is the {"greatest" if big else "least"}?', num(right), [num(f) for f in pick if f != right],
               'As decimals: ' + ', '.join(f'{num(f)} ≈ {float(f):.3f}' for f in pick) + f'. So the answer is {num(right)}. '
               'To compare just two fractions, cross-multiply: a/b > c/d when ad > bc.')


@gen('fractions', 2, 2)
def fr_tank(r):
    while True:
        a, b = F(r.randint(2, 7), r.choice([5, 6, 7, 8, 9])), F(r.randint(1, 4), r.choice([3, 4, 5, 6]))
        if 0 < b < a < 1:
            break
    cap = math.lcm(a.denominator, b.denominator)
    cap *= r.randint(max(1, -(-4 // int(cap * (a - b)))), max(2, -(-12 // int(cap * (a - b)))))
    rem = cap * (a - b)
    return mc(f'A tank is {num(a)} full. After {num(rem)} litres are drained from it, the tank is {num(b)} full. What is the capacity of the tank, in litres?',
              cap, [rem / a, rem / b, rem * (a - b), rem / (1 - b), cap * 2], f'The {num(rem)} litres drained are {num(a)} − {num(b)} = {num(a - b)} of the tank. '
              f'Capacity = {num(rem)} ÷ {num(a - b)} = {num(cap)}.', pos=True)


@gen('fractions', 2, 2)
def fr_remainder(r):
    a, b = F(1, r.choice([2, 3, 4, 5])), F(r.choice([1, 2]), r.choice([3, 5]))
    S = a.denominator * b.denominator * r.randint(5, 25) * 10
    left = S * (1 - a) * (1 - b)
    nm = r.choice(NAMES)
    return mc(f'{nm} spends {num(a)} of a monthly salary on rent and {num(b)} of what remains on food, leaving ${num(left)}. What is the monthly salary?',
              S, [left / (1 - a - b) if a + b < 1 else None, left / (1 - a), left / (1 - b), S * (1 - a)],
              f'After rent, {num(1 - a)} of the salary is left; food takes {num(b)} of that, leaving {num(1 - b)} of it. So {num(1 - a)} × {num(1 - b)} = '
              f'{num((1 - a) * (1 - b))} of the salary = ${num(left)}. Salary = {num(left)} ÷ {num((1 - a) * (1 - b))} = ${num(S)}. '
              '"Of the remainder" means multiply the fractions - do not subtract both from the whole.', show=lambda v: '$' + num(v), pos=True)


@gen('fractions', 2, 1)
def fr_qc(r):
    if r.random() < .5:
        n = r.randint(2, 8)
        d, k = r.randint(n + 1, 13), r.randint(1, 5)
        return qc('', f'{n}/{d}', f'{n + k}/{d + k}', 1, f'Cross-multiply: {n} × {d + k} = {n * (d + k)} and {d} × {n + k} = {d * (n + k)}. '
                  'B is bigger. Rule: adding the same positive number to the top and bottom of a fraction less than 1 moves it towards 1.')
    if r.random() < .5:
        return qc('x > y > 0', 'y/x', '(y + 1)/(x + 1)', 1, 'y/x is less than 1; adding 1 to top and bottom pulls it towards 1, so B is bigger. Check: x = 2, y = 1 gives 1/2 vs 2/3.')
    return qc('x > y > 0', 'x/y', '(x + 1)/(y + 1)', 0, 'x/y is greater than 1; adding 1 to top and bottom pulls it down towards 1, so A is bigger. Check: x = 2, y = 1 gives 2 vs 3/2.')


@gen('fractions', 1, 3)
def fr_to_dec(r):
    p, q = _frac(r, [2, 4, 5, 8, 20, 25], 7), _frac(r, [2, 4, 5, 8, 20, 25], 7)
    return ne(f'Write {num(p)} + {num(q)} as a decimal.', p + q, f'{num(p)} = {dec(p)} and {num(q)} = {dec(q)}, so the sum is {dec(p + q)}. '
              'Know these: 1/8 = 0.125, 1/20 = 0.05, 1/25 = 0.04.', show=dec)


@gen('fractions', 1, 0)
def fr_pieces(r):
    a, b = r.choice([(1, 2), (1, 3), (2, 3), (3, 4), (1, 4), (2, 5), (3, 5), (3, 8), (5, 6)])
    piece, m = F(a, b), r.randint(2, 9)
    L = piece * b * m
    return ne(f'How many pieces, each {num(piece)} metre long, can be cut from a rope {num(L)} metres long?', L / piece,
              f'Divide: {num(L)} ÷ {num(piece)} = {num(L)} × {num(1 / piece)} = {num(L / piece)}.')


# ====================================================================== 3. Divisibility, primes, GCF/LCM
@gen('integers', 1, 0)
def in_prime_count(r):
    a = r.randint(10, 80)
    b = a + r.randint(10, 25)
    ps = [p for p in PRIMES if a < p < b]
    return ne(f'How many prime numbers are greater than {a} and less than {b}?', len(ps),
              f'Skip even numbers and numbers ending in 5, then test the rest for 3, 7 and 11. The primes are {", ".join(map(str, ps)) or "none"} - {len(ps)} in total.')


@gen('integers', 1, 0)
def in_bigprime(r):
    while True:
        fs = sorted(r.sample([2, 3, 5, 7, 11, 13, 17, 19, 23, 29], 3))
        if r.random() < .5:
            fs = sorted(fs + [r.choice(fs[:2])])
        N = math.prod(fs)
        if N < 6000:
            break
    big = fs[-1]
    others = [p for p in PRIMES if p != big and abs(p - big) < 14]
    return mc(f'What is the greatest prime factor of {num(N)}?', big, list(dict.fromkeys(fs[:-1])) + others,
              f'Build a factor tree: {num(N)} = {fstr(N)}. The greatest prime factor is {big}.')


@gen('integers', 2, 1)
def in_divisors(r):
    while True:
        ps = sorted(r.sample([2, 3, 5, 7], r.choice([2, 2, 3])))
        es = [r.randint(1, 3) for _ in ps]
        N = math.prod(p ** e for p, e in zip(ps, es))
        if N < 3000:
            break
    v = math.prod(e + 1 for e in es)
    return mc(f'How many positive divisors does {num(N)} have?', v, [math.prod(es), sum(es), sum(es) + 1, v + 2, v - 2],
              f'{num(N)} = {fstr(N)}. Add 1 to each exponent and multiply: ' + ' × '.join(f'({e} + 1)' for e in es) + f' = {v}.', pos=True)


def _gl_pair(r):
    while True:
        g = r.choice([2, 3, 4, 6, 7, 12, 14])
        m, n = r.sample(range(2, 12), 2)
        if math.gcd(m, n) == 1:
            return g, g * m, g * n


@gen('integers', 1, 2)
def in_gcf_lcm(r):
    g, a, b = _gl_pair(r)
    L = math.lcm(a, b)
    exp = f'{a} = {fstr(a)} and {b} = {fstr(b)}. '
    if r.random() < .5:
        return mc(f'What is the greatest common factor of {a} and {b}?', g, [L, g * 2, g // 2 if g % 2 == 0 else g * 3, abs(a - b) if abs(a - b) != g else None],
                  exp + f'GCF: take the smallest power of each prime they share → {g}.', pos=True)
    return mc(f'What is the least common multiple of {a} and {b}?', L, [a * b, g, L * 2, L // 2 if L % 2 == 0 else L * 3],
              exp + f'LCM: take the largest power of every prime that appears → {num(L)}. (Product {num(a * b)} is only the LCM when the numbers share no factor.)', pos=True)


@gen('integers', 2, 2)
def in_gl_product(r):
    g, a, b = _gl_pair(r)
    L = math.lcm(a, b)
    return ne(f'The greatest common factor of two positive integers is {g} and their least common multiple is {num(L)}. If one of the integers is {a}, what is the other?',
              b, f'For any two positive integers, GCF × LCM = product of the numbers. So the other = {g} × {num(L)} ÷ {a} = {num(g * L)} ÷ {a} = {b}.')


@gen('integers', 2, 3)
def in_must_divide(r):
    while True:
        m1, m2 = r.sample([4, 6, 8, 9, 10, 12, 14, 15], 2)
        if m1 % m2 == 0 or m2 % m1 == 0:
            continue
        L = math.lcm(m1, m2)
        yes = [d for d in range(2, L + 1) if L % d == 0 and d not in (m1, m2)]
        no = [d for d in range(4, 3 * L) if L % d and (m1 * m2 * 2) % d == 0]
        if len(yes) >= 2 and len(no) >= 2:
            break
    items = [(str(d), True) for d in r.sample(yes, r.randint(2, min(3, len(yes))))] + [(str(d), False) for d in r.sample(no, 2 if len(no) < 3 else r.randint(2, 3))]
    return ma(r, f'The integer n is divisible by both {m1} and {m2}. Which of the following must also divide n?\n(Select ALL that apply.)', items,
              f'n must be a multiple of LCM({m1}, {m2}) = {L} = {fstr(L)}. A number must divide n only if it divides {L}: '
              + ', '.join(f'{t} {"✓" if ok else "✗"}' for t, ok in items) + f'. Test the smallest possible n, which is {L}.')


@gen('integers', 3, 0)
def in_zeros(r):
    n = r.randint(15, 99)
    v = n // 5 + n // 25
    return mc(f'How many zeros are at the end of {n}! (that is, 1 × 2 × 3 × … × {n})?', v, [n // 5, n // 10, n // 10 + n // 100, v + 1],
              f'Each trailing zero needs a 2 × 5, and 5s are scarcer. Count the 5s: {n} ÷ 5 → {n // 5} multiples of 5, '
              f'plus {n // 25} multiples of 25 (each gives an extra 5). Total {v}.', pos=True)


# ====================================================================== 4. Odd/even & remainders
OE_EXPR = [('a + b', lambda a, b: a + b), ('ab', lambda a, b: a * b), ('a + 2b', lambda a, b: a + 2 * b), ('2a + b', lambda a, b: 2 * a + b),
           ('a² + b', lambda a, b: a * a + b), ('ab + a', lambda a, b: a * b + a), ('a + b + 1', lambda a, b: a + b + 1),
           ('3a + b', lambda a, b: 3 * a + b), ('b² − a', lambda a, b: b * b - a), ('(a + 1)(b + 1)', lambda a, b: (a + 1) * (b + 1)),
           ('a² + b²', lambda a, b: a * a + b * b), ('ab + 1', lambda a, b: a * b + 1)]


@gen('odd_even', 2, 0)
def oe_parity(r):
    cond, A, B = r.choice([('a is odd and b is even', 3, 2), ('a and b are both odd', 3, 3), ('a is even and b is odd', 2, 3)])
    target = r.choice(['odd', 'even'])
    want = 1 if target == 'odd' else 0
    good = [e for e in OE_EXPR if e[1](A, B) % 2 == want]
    bad = [e for e in OE_EXPR if e[1](A, B) % 2 != want]
    right, wrong = r.choice(good), r.sample(bad, 4)
    shown = [right] + wrong
    return mct(r, f'If a and b are integers and {cond}, which of the following must be {target}?', right[0], [w[0] for w in wrong],
               f'Test small values (a = {A}, b = {B}): ' + ', '.join(f'{t} = {f(A, B)}' for t, f in shown) + f'. Only {right[0]} is {target}. '
               'Rules: odd ± odd = even, odd ± even = odd; a product is odd only if every factor is odd.')


@gen('odd_even', 2, 1)
def oe_rem(r):
    d = r.randint(5, 11)
    rem, k = r.randint(1, d - 1), r.randint(2, 6)
    expr, val = r.choice([(f'{k}n', k * rem), (f'n + {k * d + k}', rem + k * d + k), ('n²', rem * rem), (f'{k}n + 1', k * rem + 1)])
    return ne(f'When the positive integer n is divided by {d}, the remainder is {rem}. What is the remainder when {expr} is divided by {d}?', val % d,
              f'Pick the simplest n that works: n = {rem}. Then {expr} = {val}, and {val} ÷ {d} leaves remainder {val % d}. '
              '(Any n = ' + f'{d}q + {rem} gives the same remainder.)')


@gen('odd_even', 2, 1)
def oe_rem_lcm(r):
    ds = sorted(r.sample([3, 4, 5, 6, 7, 8, 9], 3))
    rem = r.randint(1, ds[0] - 1)
    L = math.lcm(*ds)
    return mc(f'What is the smallest integer greater than {rem} that leaves a remainder of {rem} when divided by each of {ds[0]}, {ds[1]} and {ds[2]}?', L + rem,
              [math.prod(ds) + rem, L - rem, L, 2 * L + rem], f'Numbers divisible by all three are multiples of LCM({ds[0]}, {ds[1]}, {ds[2]}) = {L}. '
              f'Add the remainder: {L} + {rem} = {L + rem}. (The product {math.prod(ds)} is only the LCM when no factors are shared.)', pos=True)


@gen('odd_even', 1, 1)
def oe_rem_sub(r):
    d1 = r.choice([12, 15, 18, 20, 24, 30])
    d2 = r.choice([k for k in range(3, d1) if d1 % k == 0])
    rem = r.randint(d2, d1 - 1)
    return ne(f'When n is divided by {d1}, the remainder is {rem}. What is the remainder when n is divided by {d2}?', rem % d2,
              f'n = {d1}q + {rem}. Since {d2} divides {d1}, the {d1}q part leaves no remainder, so only {rem} matters: {rem} ÷ {d2} leaves {rem % d2}. '
              f'Check with n = {rem}: remainder {rem % d2}.')


@gen('odd_even', 2, 2)
def oe_consec_sum(r):
    k = r.choice([3, 5, 7, 4, 6])
    if k % 2:
        return mc(f'The sum of any {k} consecutive integers must be divisible by which of the following?', k, [2 * k, k + 1, k - 1, k + 2, k * k],
                  f'Write them as n, n + 1, …, n + {k - 1}. The sum is {k}n + {k * (k - 1) // 2} = {k}(n + {(k - 1) // 2}), always a multiple of {k}. '
                  'For an odd count, the sum = count × middle number.', pos=True)
    h = k // 2
    return mc(f'The sum of any {k} consecutive integers must be divisible by which of the following?', h, [k, 2 * k, k + 1, k - 1 if k - 1 != h else None, h + 1 if h + 1 != k else k + 2],
              f'n + (n + 1) + … + (n + {k - 1}) = {k}n + {k * (k - 1) // 2} = {h}(2n + {k - 1}). The bracket is odd, so the sum is a multiple of {h} but never of {k}. '
              f'Check: 1 + … + {k} = {k * (k + 1) // 2}.', pos=True)


@gen('odd_even', 2, 2)
def oe_consec_prod(r):
    k = r.choice([3, 4])
    if k == 3:
        return mc('The product of any 3 consecutive positive integers must be divisible by which of the following?', 6, [4, 9, 12, 5],
                  'Among 3 consecutive integers one is a multiple of 3 and at least one is even, so the product is a multiple of 3! = 6. Check 1 × 2 × 3 = 6: not divisible by 4, 9, 12 or 5.')
    return mc('The product of any 4 consecutive positive integers must be divisible by which of the following?', 24, [16, 36, 48, 18],
              'The product of k consecutive integers is divisible by k!. Here 4! = 24. Check 1 × 2 × 3 × 4 = 24: not divisible by 16, 18, 36 or 48.')


# ====================================================================== 5. Exponents
@gen('exponents', 1, 0)
def ex_rules(r):
    a, b, c = r.randint(2, 6), r.randint(1, 5), r.randint(2, 4)
    d = r.randint(1, (a + b) * c - 1)
    v = (a + b) * c - d
    return ne(f'If (x{sup(a)} · x{sup(b)}){sup(c)} ÷ x{sup(d)} = xⁿ for x ≠ 0, what is n?', v,
              f'Multiply same base → add exponents: x{sup(a + b)}. Power of a power → multiply: x{sup((a + b) * c)}. Divide → subtract: {(a + b) * c} − {d} = {v}.')


@gen('exponents', 2, 1)
def ex_common_base(r):
    B = r.choice([2, 3])
    a, b, c = r.randint(3, 12), r.randint(1, 5), r.randint(1, 4)
    k = a + 2 * b - 3 * c
    return ne(f'If {pw(B, a)} × {pw(B * B, b)} ÷ {pw(B ** 3, c)} = {B}ˣ, what is x?', k,
              f'Write everything as a power of {B}: {pw(B * B, b)} = {pw(B, 2 * b)} and {pw(B ** 3, c)} = {pw(B, 3 * c)}. So x = {a} + {2 * b} − {3 * c} = {num(k)}.')


@gen('exponents', 1, 1)
def ex_solve(r):
    B = r.choice([2, 3, 5])
    m = r.randint(3, {2: 9, 3: 6, 5: 4}[B])
    if r.random() < .5:
        k = r.randint(1, m - 1)
        return mc(f'If {B}^(x + {k}) = {num(B ** m)}, what is x?', m - k, [m, m + k, k, B ** m // B],
                  f'{num(B ** m)} = {pw(B, m)}, so x + {k} = {m} and x = {m - k}.')
    m = m if m % 2 else m + 1
    return mc(f'If {B}^(2x − 1) = {num(B ** m)}, what is x?', (m + 1) // 2, [m, m - 1, (m - 1) // 2, m + 1],
              f'{num(B ** m)} = {pw(B, m)}, so 2x − 1 = {m}, 2x = {m + 1} and x = {(m + 1) // 2}.', pos=True)


@gen('exponents', 1, 2)
def ex_neg(r):
    while True:
        base = F(r.randint(1, 4), r.randint(2, 5))
        if base != 1 and base.denominator > 1:
            break
    n = r.randint(2, 3)
    v = (1 / base) ** n
    return mc(f'({num(base)}){sup(-n)} = ?', v, [base ** n, -v, -(base ** n), (1 / base) * n],
              f'A negative exponent means "flip, then power": ({num(base)}){sup(-n)} = ({num(1 / base)}){sup(n)} = {num(v)}. It never makes the number negative.')


@gen('exponents', 2, 3)
def ex_add_powers(r):
    b, n = r.choice([3, 4, 5]), r.randint(10, 30)
    return mct(r, ' + '.join([pw(b, n)] * b) + ' = ?', pw(b, n + 1), [pw(b, n * b), pw(b * b, n), pw(b, n + b), pw(b * b, n * b)],
               f'There are {b} copies of {pw(b, n)}, so the sum is {b} × {pw(b, n)} = {pw(b, n + 1)}. Adding equal powers is multiplication - you never add exponents across a + sign.')


@gen('exponents', 2, 3)
def ex_units(r):
    b, n = r.choice([2, 3, 7, 8, 4, 9]), r.randint(10, 60)
    cyc = []
    x = b % 10
    while x not in cyc:
        cyc.append(x)
        x = x * b % 10
    pos = n % len(cyc) or len(cyc)
    v = cyc[pos - 1]
    return ne(f'What is the units digit of {pw(b, n)}?', v, f'Units digits of powers of {b} repeat in a cycle of {len(cyc)}: {", ".join(map(str, cyc))}. '
              f'{n} ÷ {len(cyc)} leaves remainder {n % len(cyc)}, so take position {pos} in the cycle: {v}.')


@gen('exponents', 3, 3)
def ex_factor_out(r):
    b, m, n = r.choice([2, 3, 5]), r.randint(1, 3), r.randint(5, 20)
    plus = r.random() < .5
    k = b ** m + 1 if plus else b ** m - 1
    sg = '+' if plus else '−'
    return ne(f'If {pw(b, n + m)} {sg} {pw(b, n)} = k × {pw(b, n)}, what is k?', k,
              f'Factor out the smaller power: {pw(b, n + m)} {sg} {pw(b, n)} = {pw(b, n)}({pw(b, m)} {sg} 1) = {pw(b, n)} × {k}.')


# ====================================================================== 6. Roots
@gen('roots', 1, 0)
def rt_sum(r):
    k = r.choice([2, 3, 5, 6, 7])
    a, b = r.sample(range(2, 7), 2)
    return mct(r, f'√{a * a * k} + √{b * b * k} = ?', f'{a + b}√{k}', [f'√{(a * a + b * b) * k}', f'{a * b}√{k}', f'{a + b}√{2 * k}', f'{a * a + b * b}√{k}'],
               f'√{a * a * k} = √({a * a} × {k}) = {a}√{k}, and √{b * b * k} = {b}√{k}. Like roots add: {a + b}√{k}. You cannot add under the root sign.')


@gen('roots', 1, 0)
def rt_closest(r):
    while True:
        N = r.randint(20, 400)
        if math.isqrt(N) ** 2 != N:
            break
    k = math.isqrt(N)
    v = k if N <= k * k + k else k + 1
    return ne(f'Which integer is closest to √{N}?', v, f'{k}² = {k * k} and {k + 1}² = {(k + 1) ** 2}, so √{N} is between {k} and {k + 1}. '
              f'The halfway point is {k}.5, and {k}.5² = {dec(F(2 * k + 1, 2) ** 2)}. {N} is {"below" if v == k else "above"} that, so the closest integer is {v}.')


@gen('roots', 2, 1)
def rt_conj(r):
    if r.random() < .5:
        a, b = r.sample([2, 3, 5, 6, 7, 8, 10, 11, 12, 13], 2)
        return mc(f'(√{a} + √{b})(√{a} − √{b}) = ?', a - b, [a + b, a * a - b * b, (a - b) ** 2, a * b],
                  f'Difference of squares: (√{a})² − (√{b})² = {a} − {b} = {num(a - b)}.')
    a, b = r.choice([2, 3, 5, 6, 7, 8, 10, 11, 12, 13, 14, 15]), r.randint(1, 4)
    return mc(f'(√{a} + {b})(√{a} − {b}) = ?', a - b * b, [a - b, a + b * b, a * a - b * b, a - 2 * b],
              f'Difference of squares: (√{a})² − {b}² = {a} − {b * b} = {num(a - b * b)}.')


RT_FRAC = [(8, 2, 3), (27, 2, 3), (16, 3, 4), (32, 3, 5), (64, 2, 3), (81, 3, 4), (125, 2, 3), (16, 5, 4), (4, 3, 2), (9, 3, 2), (25, 3, 2), (64, 5, 6), (27, 4, 3)]
ORD = {2: 'square', 3: 'cube', 4: '4th', 5: '5th', 6: '6th'}


@gen('roots', 2, 2)
def rt_frac_exp(r):
    N, p, q = r.choice(RT_FRAC)
    root = round(N ** (1 / q))
    v = root ** p
    if r.random() < .3:
        return mc(f'{N}^(−{p}/{q}) = ?', F(1, v), [v, -v, F(1, root), F(-1, v)],
                  f'Negative exponent = reciprocal. {ORD[q].capitalize()} root of {N} is {root}; {root}^{p} = {v}; so the answer is 1/{v}.')
    return mc(f'{N}^({p}/{q}) = ?', v, [root, root ** (p + 1), N * p // q, v * 2], f'The bottom of the fraction is the root, the top is the power. '
              f'{ORD[q].capitalize()} root of {N} = {root}, then {root}^{p} = {v}. Take the root first - the numbers stay small.', pos=True)


@gen('roots', 3, 3)
def rt_extraneous(r):
    while True:
        q0 = r.randint(1, 6)
        x0 = r.randint(q0 + 1, q0 + 9)
        p = (x0 - q0) ** 2 - x0
        x1 = 2 * q0 + 1 - x0
        if x1 != x0 and x1 < q0 and x1 + p >= 0:
            break
    c = q0 * q0 - p
    inner = 'x' + term(p)
    lo, hi = sorted([x1, x0])
    return mct(r, f'If √({inner}) = x − {q0}, what is x?', num(x0), [num(x1), f'{num(lo)} or {num(hi)}', 'There is no solution', num(x0 + x1), num(q0), num(x0 + 1)],
               f'Square both sides: {inner} = x² − {2 * q0}x + {q0 * q0}, so {poly(1, -(2 * q0 + 1), c)} = 0, giving x = {num(x1)} or x = {num(x0)}. '
               f'Check in the original: x = {num(x1)} gives √{x1 + p} = {math.isqrt(x1 + p)} on the left but {num(x1 - q0)} on the right - a square root is never negative, '
               f'so {num(x1)} is extraneous. Answer: {num(x0)}.')


@gen('roots', 2, 1)
def rt_qc(r):
    if r.random() < .5:
        k = r.randint(4, 12)
        N = k * k + r.choice([-3, -2, -1, 0, 1, 2, 3])
        ans = 0 if N > k * k else 1 if N < k * k else 2
        return qc('', f'√{N}', str(k), ans, f'{k} = √{k * k}. Compare {N} with {k * k}: ' + ('they are equal.' if ans == 2 else f'√{N} is {"bigger" if ans == 0 else "smaller"}.'))
    return qc(*r.choice([
        ('a > 0, b > 0', '√a + √b', '√(a + b)', 0, 'Square both: A² = a + b + 2√(ab) and B² = a + b. A² is bigger, so A is bigger. Check a = b = 1: 2 vs √2.'),
        ('a > 0, b > 0', '√(ab)', '√a × √b', 2, '√(ab) = √a × √b for non-negative numbers - always equal.'),
        ('x < 0', '√(x²)', 'x', 0, '√(x²) = |x|, which is positive, while x is negative.'),
        ('x > 0', '√(x²)', 'x', 2, '√(x²) = |x| = x when x is positive.'),
        ('', '√2 + √3', '√5', 0, '(√2 + √3)² = 5 + 2√6 > 5, so A is bigger. Roots do not add like that.'),
    ]))


# ====================================================================== 7. Algebraic expressions
def _nz(r, lo, hi):
    return r.choice([i for i in range(lo, hi + 1) if i])


@gen('algebra_expr', 1, 0)
def al_factor(r):
    while True:
        p, q = r.sample([i for i in range(-9, 10) if i], 2)
        if p + q:
            break
    fp = lambda a, b: lin(max(a, b)) + lin(min(a, b))  # noqa: E731
    pairs = [(-p, -q), (-p, q), (p, -q), (p * q, 1), (-p * q, -1), (p + q, 1), (p - 1, q + 1)]
    return mct(r, f'Which of the following is a factorisation of {poly(1, p + q, p * q)}?', fp(p, q),
               [fp(a, b) for a, b in pairs if sorted((a, b)) != sorted((p, q)) and a and b],
               f'Find two numbers that multiply to {num(p * q)} and add to {num(p + q)}: {num(p)} and {num(q)}. So {lin(p)}{lin(q)}. Check by expanding.')


@gen('algebra_expr', 1, 1)
def al_expand(r):
    a, c = r.randint(1, 5), r.randint(1, 5)
    b, d = _nz(r, -9, 9), _nz(r, -9, 9)
    v = a * d + b * c
    return ne(f'When {lin(b, a=a)}{lin(d, a=c)} is expanded, what is the coefficient of x?', v,
              f'FOIL: the x terms come from Outer and Inner: {lead(a, "x")} × {num(d)} = {lead(a * d, "x")} and {num(b)} × {lead(c, "x")} = {lead(b * c, "x")}. '
              f'Together: {num(v)}. (Full expansion: {poly(a * c, v, b * d)}.)')


@gen('algebra_expr', 2, 2)
def al_diffsq(r):
    x_, y_ = r.sample(range(-5, 12), 2)
    s, d = x_ + y_, x_ - y_
    if r.random() < .6 and s and d:
        return mc(f'If x + y = {num(s)} and x − y = {num(d)}, what is x² − y²?', s * d, [s * s - d * d, s + d, s * s, d * d],
                  f'x² − y² = (x + y)(x − y) = {num(s)} × {num(d)} = {num(s * d)}. No need to find x and y.')
    while not s:
        x_, y_ = r.sample(range(1, 12), 2)
        s, d = x_ + y_, x_ - y_
    return ne(f'If x² − y² = {num(s * d)} and x + y = {num(s)}, what is x − y?', d,
              f'x² − y² = (x + y)(x − y), so {num(s * d)} = {num(s)} × (x − y) and x − y = {num(d)}.')


@gen('algebra_expr', 2, 2)
def al_sqid(r):
    a, b = _nz(r, -6, 7), _nz(r, -6, 7)
    S, P = a * a + b * b, a * b
    if r.random() < .5:
        return mc(f'If a² + b² = {S} and ab = {num(P)}, what is (a + b)²?', S + 2 * P, [S + P, S - 2 * P, S, S + 4 * P],
                  f'(a + b)² = a² + 2ab + b² = {S} + 2({num(P)}) = {num(S + 2 * P)}.')
    return mc(f'If a² + b² = {S} and ab = {num(P)}, what is (a − b)²?', S - 2 * P, [S + 2 * P, S - P, S, S - 4 * P],
              f'(a − b)² = a² − 2ab + b² = {S} − 2({num(P)}) = {num(S - 2 * P)}.')


@gen('algebra_expr', 3, 2)
def al_xinv(r):
    k = r.randint(2, 7)
    if r.random() < .5:
        return mc(f'If x + 1/x = {k}, what is x² + 1/x²?', k * k - 2, [k * k, k * k + 2, k * k - 1, 2 * k],
                  f'Square both sides: x² + 2(x)(1/x) + 1/x² = {k * k}, i.e. x² + 2 + 1/x² = {k * k}, so x² + 1/x² = {k * k - 2}.', pos=True)
    return mc(f'If x − 1/x = {k}, what is x² + 1/x²?', k * k + 2, [k * k, k * k - 2, k * k + 1, 2 * k],
              f'Square both sides: x² − 2 + 1/x² = {k * k}, so x² + 1/x² = {k * k + 2}.', pos=True)


@gen('algebra_expr', 2, 3)
def al_rational(r):
    a = r.randint(1, 7)
    b = r.choice([i for i in range(1, 8) if i != a])
    v = r.randint(0, 2)
    if v == 0:
        q, right = f'({poly(1, 0, -a * a)}) ÷ ({poly(1, 2 * a, a * a)})', f'(x − {a})/(x + {a})'
        x = f'Top: x² − {a * a} = (x − {a})(x + {a}). Bottom: (x + {a})². Cancel one (x + {a}).'
    elif v == 1:
        q, right = f'({poly(1, 0, -a * a)}) ÷ ({poly(1, -2 * a, a * a)})', f'(x + {a})/(x − {a})'
        x = f'Top: (x − {a})(x + {a}). Bottom: (x − {a})². Cancel one (x − {a}).'
    else:
        q, right = f'({poly(1, a + b, a * b)}) ÷ ({poly(1, 0, -b * b)})', f'(x + {a})/(x − {b})'
        x = f'Top: (x + {a})(x + {b}). Bottom: (x + {b})(x − {b}). Cancel (x + {b}).'
    wrong = [f'(x − {a})/(x + {a})', f'(x + {a})/(x − {a})', f'(x + {a})/(x + {a})', f'1/(x + {a})', '−1', f'(x − {a})/(x − {b})']
    return mct(r, f'For values of x where it is defined, simplify {q}.', right, r.sample([w for w in wrong if w != right], 4),
               x + ' You can only cancel factors (things multiplied), never terms that are added.')


# ====================================================================== 8. Equations & systems
@gen('equations', 1, 0)
def eq_linear(r):
    while True:
        x0 = r.randint(-10, 15)
        a, c = r.sample(range(1, 10), 2)
        b = _nz(r, -20, 20)
        d = a * x0 + b - c * x0
        if d and x0 and d != b:
            break
    return ne(f'If {lead(a, "x")}{term(b)} = {lead(c, "x")}{term(d)}, what is x?', x0,
              f'Collect x on one side: {lead(a - c, "x")} = {num(d)} − {pn(b)} = {num(d - b)}, so x = {num(d - b)} ÷ {num(a - c)} = {num(x0)}.')


@gen('equations', 2, 1)
def eq_system(r):
    x0, y0 = r.randint(-5, 9), r.randint(-5, 9)
    if r.random() < .5:
        a, b = r.sample(range(1, 7), 2)
        A, B = a * x0 + b * y0, b * x0 + a * y0
        return mc(f'If {lead(a, "x")}{term(b, "y")} = {num(A)} and {lead(b, "x")}{term(a, "y")} = {num(B)}, what is x + y?', x0 + y0,
                  [x0, y0, x0 - y0, x0 * y0], f'Add the two equations: {a + b}x + {a + b}y = {num(A + B)}, so x + y = {num(A + B)} ÷ {a + b} = {num(x0 + y0)}. '
                  'When the question asks for a combination like x + y, look for a shortcut before solving for each variable.')
    while True:
        a, b, c, d = _nz(r, -4, 5), _nz(r, -4, 5), _nz(r, -4, 5), _nz(r, -4, 5)
        if a * d - b * c:
            break
    A, B = a * x0 + b * y0, c * x0 + d * y0
    return mc(f'If {lead(a, "x")}{term(b, "y")} = {num(A)} and {lead(c, "x")}{term(d, "y")} = {num(B)}, what is x + y?', x0 + y0,
              [x0, y0, x0 - y0, x0 * y0], f'Eliminate one variable (multiply so the y-coefficients match, then subtract) to get x = {num(x0)}, then substitute: y = {num(y0)}. '
              f'x + y = {num(x0 + y0)}.')


@gen('equations', 2, 2)
def eq_roots(r):
    a = r.choice([1, 1, 2, 3])
    p, q = _nz(r, -8, 8), _nz(r, -8, 8)
    b, c = -a * (p + q), a * p * q
    if r.random() < .5:
        return mc(f'What is the sum of the solutions of {poly(a, b, c)} = 0?', p + q, [F(b, a), F(c, a), -F(c, a), p * q],
                  f'Factor: {a if a > 1 else ""}{lin(-p)}{lin(-q)} = 0, so x = {num(p)} or {num(q)}; sum = {num(p + q)}. '
                  f'Shortcut: for ax² + bx + c = 0 the solutions add to −b/a = {num(F(-b, a))}.')
    return mc(f'What is the product of the solutions of {poly(a, b, c)} = 0?', p * q, [F(b, a), -F(b, a), p + q, -p * q],
              f'Factor: {a if a > 1 else ""}{lin(-p)}{lin(-q)} = 0, so x = {num(p)} or {num(q)}; product = {num(p * q)}. Shortcut: product = c/a = {num(F(c, a))}.')


@gen('equations', 2, 0)
def eq_cross(r):
    while True:
        k, m = r.sample(range(1, 8), 2)
        a, b = r.randint(1, 9), r.randint(1, 9)
        x0 = F(-m * a - k * b, k - m)
        if x0.denominator == 1 and x0 != a and x0 != -b:
            break
    return mc(f'If {k}/(x − {a}) = {m}/(x + {b}), what is x?', x0, [-x0, x0 + 1, F(m * a + k * b, k + m), a + b],
              f'Cross-multiply: {k}(x + {b}) = {m}(x − {a}) → {k}x + {k * b} = {m}x − {m * a} → {lead(k - m, "x")} = {num(-m * a - k * b)}'
              + ('.' if k - m == 1 else f' → x = {num(x0)}.'))


@gen('equations', 3, 3)
def eq_nosol(r):
    a, b, m = r.randint(1, 6), r.randint(1, 6), r.choice([2, 3])
    c = r.randint(1, 12)
    d = m * c + _nz(r, -5, 5)
    return ne(f'For what value of k does the system {lead(a, "x")} + {lead(b, "y")} = {c} and kx + {m * b}y = {d} have no solution?', m * a,
              f'No solution means parallel lines: same x and y proportions but a different constant. The y-coefficient was multiplied by {m}, '
              f'so k = {m} × {a} = {m * a}. Then the second equation says {lead(a, "x")} + {lead(b, "y")} = {num(F(d, m))}, which contradicts = {c}.')


@gen('equations', 1, 0)
def eq_consec(r):
    k = r.choice([3, 4, 5])
    kind = r.choice(['even', 'odd'])
    first = 2 * r.randint(2, 30) + (1 if kind == 'odd' else 0)
    S = sum(first + 2 * i for i in range(k))
    big = first + 2 * (k - 1)
    return ne(f'The sum of {k} consecutive {kind} integers is {S}. What is the largest of them?', big,
              f'Call them n, n + 2, …, n + {2 * (k - 1)}. Sum = {k}n + {k * (k - 1)} = {S} → n = {first}. Largest = {big}. '
              f'Shortcut: the average {num(F(S, k))} is the middle of the list.')


@gen('equations', 1, 2)
def eq_quad_pos(r):
    p, q = r.randint(1, 9), -r.randint(1, 9)
    return ne(f'What is the positive solution of {poly(1, -(p + q), p * q)} = 0?', p,
              f'Two numbers that multiply to {num(p * q)} and add to {num(-(p + q))}: {num(-p)} and {num(-q)}. So {lin(-p)}{lin(-q)} = 0 and x = {p} or x = {num(q)}.')


# ====================================================================== 9. Inequalities & absolute value
@gen('inequalities', 1, 0)
def ie_flip(r):
    a, b, t = r.randint(2, 6), r.randint(-10, 20), _nz(r, -8, 8)
    c = b - a * t
    return mct(r, f'If {num(b)} − {a}x > {num(c)}, which of the following must be true?', f'x < {num(t)}',
               [f'x > {num(t)}', f'x < {num(-t)}', f'x > {num(-t)}', f'x < {num(t + 1)}'],
               f'Subtract {num(b)}: −{a}x > {num(c - b)}. Divide by −{a} and FLIP the sign: x < {num(t)}.')


@gen('inequalities', 2, 1)
def ie_abs_count(r):
    a, b = r.randint(-6, 8), r.randint(2, 8)
    strict = r.random() < .5
    v = 2 * b - 1 if strict else 2 * b + 1
    sym = '<' if strict else '≤'
    return ne(f'How many integers x satisfy |x {"−" if a >= 0 else "+"} {abs(a)}| {sym} {b}?', v,
              f'|x − ({num(a)})| {sym} {b} means x is within {b} of {num(a)}: {num(a - b)} {sym} x {sym} {num(a + b)}. '
              f'Integers from {num(a - b + (1 if strict else 0))} to {num(a + b - (1 if strict else 0))}: {v} of them.')


@gen('inequalities', 2, 2)
def ie_range(r):
    p, q = sorted(r.sample(range(-6, 7), 2))
    s, t = sorted(r.sample(range(-6, 7), 2))
    right = f'{num(p - t)} < a − b < {num(q - s)}'
    cands = [(p - s, q - t), (p + s, q + t), (p - t + 1, q - s - 1), (p - t, q - s + 2), (s - q, t - p), (p - t - 2, q - s), (p - t - 1, q - s + 1)]
    wrong = [f'{num(lo)} < a − b < {num(hi)}' for lo, hi in (sorted(c) for c in cands) if lo < hi]
    return mct(r, f'If {num(p)} < a < {num(q)} and {num(s)} < b < {num(t)}, which gives all possible values of a − b?', right, wrong,
               f'Smallest a − b = smallest a − largest b = {num(p)} − {pn(t)} = {num(p - t)}. Largest = largest a − smallest b = {num(q)} − {pn(s)} = {num(q - s)}.')


@gen('inequalities', 2, 1)
def ie_abs_sum(r):
    k, m, n = r.randint(1, 4), _nz(r, -9, 9), r.randint(1, 12)
    s1, s2 = F(n - m, k), F(-n - m, k)
    return mc(f'What is the sum of all values of x for which |{lead(k, "x")}{term(m)}| = {n}?', s1 + s2, [s1, s2, s1 - s2, F(2 * m, k)],
              f'Split into two cases: {lead(k, "x")}{term(m)} = {n} gives x = {num(s1)}; {lead(k, "x")}{term(m)} = −{n} gives x = {num(s2)}. Sum = {num(s1 + s2)}.')


@gen('inequalities', 3, 2)
def ie_extreme(r):
    p, q = r.randint(1, 6), r.randint(1, 6)
    if r.random() < .5:
        s, t = r.randint(1, 4), r.randint(5, 9)
        v = max(p, q) ** 2 - s
        return ne(f'If −{p} ≤ x ≤ {q} and {s} ≤ y ≤ {t}, what is the greatest possible value of x² − y?', v,
                  f'Make x² as big as possible and y as small as possible. x² is largest at the end farthest from 0: x = {num(-p if p >= q else q)}, x² = {max(p, q) ** 2}. '
                  f'Smallest y = {s}. Greatest x² − y = {v}. Trap: the largest x is not always the largest x².')
    s, t = -r.randint(1, 6), r.randint(1, 6)
    corners = [a * b for a in (-p, q) for b in (s, t)]
    v = max(corners)
    return ne(f'If −{p} ≤ x ≤ {q} and {num(s)} ≤ y ≤ {t}, what is the greatest possible value of xy?', v,
              f'For products, test the four corners: ' + ', '.join(f'({num(a)})({num(b)}) = {num(a * b)}' for a in (-p, q) for b in (s, t)) + f'. Greatest = {num(v)}.')


IE_QC = [
    ('x² < x', 'x', '1', 1, 'x² < x → x(x − 1) < 0 → 0 < x < 1. So x is always less than 1.'),
    ('x² > 4', 'x', '2', 3, 'x² > 4 means x > 2 OR x < −2. x = 3 gives A > B; x = −3 gives A < B → (D).'),
    ('x³ < x', 'x', '0', 3, 'x³ < x holds for x < −1 (e.g. −2) and for 0 < x < 1 (e.g. 1/2). x can be either side of 0 → (D).'),
    ('|x| < 3', 'x²', '9', 1, '|x| < 3 means −3 < x < 3, so x² < 9.'),
    ('|x − 2| ≤ 1', 'x', '0', 0, '|x − 2| ≤ 1 means 1 ≤ x ≤ 3, so x is always positive.'),
]


@gen('inequalities', 2, 0)
def ie_qc(r):
    if r.random() < .5:
        a, b, t = r.randint(2, 6), r.randint(-10, 10), _nz(r, -6, 6)
        c = b - a * t
        return qc(f'{num(b)} − {a}x > {num(c)}', 'x', num(t), 1, f'−{a}x > {num(c - b)} → divide by −{a} and flip: x < {num(t)}. So B is greater.')
    return qc(*r.choice(IE_QC))


# ====================================================================== 10. Functions & symbols
@gen('functions', 1, 0)
def fn_eval(r):
    a, b, c, x0 = _nz(r, -3, 4), _nz(r, -6, 6), r.randint(-9, 9), -r.randint(1, 5)
    v = a * x0 * x0 + b * x0 + c
    return ne(f'If f(x) = {poly(a, b, c)}, what is f({num(x0)})?', v,
              f'Substitute in brackets: {num(a)}({num(x0)})² + ({num(b)})({num(x0)}) + ({num(c)}) = {num(a * x0 * x0)} + ({num(b * x0)}) + ({num(c)}) = {num(v)}. '
              'Brackets around negatives prevent sign mistakes.')


FN_OPS = [('x² − {k}y', lambda x, y, k: x * x - k * y), ('xy + {k}x', lambda x, y, k: x * y + k * x),
          ('{k}x − y', lambda x, y, k: k * x - y), ('x² + y − {k}', lambda x, y, k: x * x + y - k)]


@gen('functions', 2, 1)
def fn_symbol(r):
    form, f = r.choice(FN_OPS)
    k = r.randint(1, 4)
    form = form.format(k=k)
    a, b, c = r.randint(1, 4), r.randint(1, 4), r.randint(1, 4)
    inner = f(b, c, k)
    v = f(a, inner, k)
    return ne(f'For all numbers x and y, x ◊ y = {form}. What is {a} ◊ ({b} ◊ {c})?', v,
              f'Inside first: {b} ◊ {c} = {num(inner)}. Then {a} ◊ {num(inner)} = {num(v)}. A strange symbol is just a rule - substitute carefully.')


@gen('functions', 2, 2)
def fn_compose(r):
    a, b, c, k = _nz(r, -4, 5), r.randint(-6, 6), r.randint(-5, 5), r.randint(-3, 4)
    f = lambda x: a * x + b  # noqa: E731
    g = lambda x: x * x + c  # noqa: E731
    if r.random() < .5:
        return ne(f'If f(x) = {lead(a, "x")}{term(b)} and g(x) = x²{term(c)}, what is f(g({num(k)}))?', f(g(k)),
                  f'Work from the inside out: g({num(k)}) = {num(g(k))}, then f({num(g(k))}) = {num(f(g(k)))}.')
    return ne(f'If f(x) = {lead(a, "x")}{term(b)} and g(x) = x²{term(c)}, what is g(f({num(k)}))?', g(f(k)),
              f'Inside out: f({num(k)}) = {num(f(k))}, then g({num(f(k))}) = {num(f(k))}²{term(c)} = {num(g(f(k)))}.')


@gen('functions', 1, 3)
def fn_solve(r):
    a, b, t = r.randint(2, 7), r.randint(-9, 9), r.randint(-6, 10)
    v = a * t - b
    return ne(f'If f(x) = {a}x{term(-b)} and f(t) = {num(v)}, what is t?', t,
              f'{a}t{term(-b)} = {num(v)} → {a}t = {num(v + b)} → t = {num(t)}.')


@gen('functions', 3, 0)
def fn_linear(r):
    a, b = _nz(r, -5, 6), r.randint(-9, 9)
    P, Q = a + b, 3 * a + b
    return ne(f'f is a linear function with f(1) = {num(P)} and f(3) = {num(Q)}. What is f(5)?', 5 * a + b,
              f'From x = 1 to x = 3 the output changes by {num(Q - P)}, so the slope is {num(a)} per unit. From 3 to 5 it changes by another {num(2 * a)}: '
              f'f(5) = {num(Q)} + 2 × ({num(a)}) = {num(5 * a + b)}.')


# ====================================================================== 11. Percents
def chg(v):
    """Net change as a fraction of 1 -> '4% decrease'."""
    if v == 0:
        return 'No change'
    return f'{pct(abs(v) * 100)} {"increase" if v > 0 else "decrease"}'


@gen('percents', 1, 1)
def pc_successive(r):
    p, q = r.choice([10, 20, 25, 30, 40, 50]), r.choice([10, 20, 25, 30, 40, 50])
    up_first = r.random() < .5
    net = F(100 + p, 100) * F(100 - q, 100) - 1
    naive = F(p - q, 100)
    q_txt = f'rises by {p}% and then falls by {q}%' if up_first else f'falls by {q}% and then rises by {p}%'
    return mct(r, f'The price of an item {q_txt}. What is the overall change?', chg(net),
               [chg(naive), chg(-net) if net else '2% decrease', chg(net + F(1, 100)), chg(net - F(2, 100)), chg(F(p + q, 100))],
               f'Use multipliers: {dec(F(100 + p, 100))} × {dec(F(100 - q, 100))} = {dec(1 + net)}, ' + (f'a {chg(net)}. ' if net else 'so there is no change overall. ') +
               'Successive percent changes multiply - they never simply add.')


@gen('percents', 1, 0)
def pc_of(r):
    p = r.choice([5, 8, 12, 15, 20, 25, 30, 40, 45, 60, 75, 120, 150])
    N = r.randint(2, 40) * 20
    X = F(p * N, 100)
    return ne(f'{dec(X)} is {p}% of what number?', N, f'{p}% of N = {dec(X)} → {dec(F(p, 100))} × N = {dec(X)} → N = {dec(X)} ÷ {dec(F(p, 100))} = {num(N)}.')


PC_ML = [(25, F(20)), (50, F(100, 3)), (20, F(50, 3)), (100, F(50)), (60, F(75, 2)), (150, F(60)), (300, F(75)), (400, F(80)), (10, F(100, 11))]


@gen('percents', 2, 3)
def pc_more_less(r):
    p, v = r.choice(PC_ML)
    return mct(r, f'A is {p}% greater than B. B is what percent less than A?', pct(v), [pct(p), pct(100 - v), pct(F(p, 2)), pct(v + 5), pct(v - 5), pct(F(p, 2) + 5), pct(v + 10)],
               f'Let B = 100, so A = {100 + p}. B is {p} less than A, and as a percent of A that is {p}/{100 + p} = {pct(v)}. '
               'The base (the "than" number) changes, so the two percents are not equal.')


@gen('percents', 2, 1)
def pc_compound(r):
    P, rate, n = r.choice([1000, 2000, 5000, 10000]), r.choice([5, 10, 20]), r.choice([2, 3])
    m = F(100 + rate, 100)
    v = P * m ** n
    return mc(f'An investment of ${num(P)} earns {rate}% interest per year, compounded annually. What is it worth after {n} years?', v,
              [P * (1 + F(rate * n, 100)), P * m ** (n - 1), P * m ** (n + 1), P * F(rate * n, 100)],
              f'Compound growth multiplies each year: {num(P)} × {dec(m)}{sup(n)} = {money(v)}. Simple interest ({money(P * (1 + F(rate * n, 100)))}) is the trap.', show=money)


@gen('percents', 2, 2)
def pc_reverse(r):
    p = r.choice([10, 20, 25, 30, 40, 50, 15])
    orig = r.randint(4, 30) * 20
    X = orig * F(100 - p, 100)
    return mc(f'After a {p}% discount, a jacket costs {money(X)}. What was the original price?', orig,
              [X * F(100 + p, 100), X + p, X * F(100 - p, 100), X / F(100 + p, 100)],
              f'Sale price = {dec(F(100 - p, 100))} × original, so original = {money(X)} ÷ {dec(F(100 - p, 100))} = {money(orig)}. '
              f'Adding {p}% back on to the sale price is the classic trap - the {p}% was of the original, not the sale price.', show=money)


@gen('percents', 1, 1)
def pc_change(r):
    a = r.randint(2, 30) * 20
    k = r.choice([5, 10, 15, 20, 25, 30, 35, 40, 45, 50, 60, 75])
    up = r.random() < .5
    b = a * F(100 + (k if up else -k), 100)
    return ne(f'A value changes from {num(a)} to {dec(b)}. By what percent did it {"increase" if up else "decrease"}?', k,
              f'Percent change = change ÷ original = {dec(abs(b - a))} ÷ {num(a)} = {dec(F(k, 100))} = {k}%. Always divide by the starting value.')


# ====================================================================== 12. Ratios
@gen('ratios', 1, 0)
def ra_split(r):
    a, b = r.sample(range(1, 10), 2)
    g = math.gcd(a, b)
    a, b = a // g, b // g
    k = r.randint(2, 15)
    T = (a + b) * k
    who = r.choice(['boys', 'girls'])
    return ne(f'The ratio of boys to girls in a group of {T} is {a} : {b}. How many {who} are there?', (a if who == 'boys' else b) * k,
              f'{a} + {b} = {a + b} parts. Each part = {T} ÷ {a + b} = {k}. {who.capitalize()} = {a if who == "boys" else b} × {k} = {(a if who == "boys" else b) * k}.')


def _rat(x, y):
    g = math.gcd(x, y)
    return f'{x // g} : {y // g}'


@gen('ratios', 2, 1)
def ra_chain(r):
    while True:
        a, b, c, d = (r.randint(1, 9) for _ in range(4))
        if math.gcd(a, b) == 1 and math.gcd(c, d) == 1 and b != c:
            break
    L = math.lcm(b, c)
    A, C = a * L // b, d * L // c
    right = _rat(A, C)
    return mct(r, f'If a : b = {a} : {b} and b : c = {c} : {d}, what is a : c?', right,
               [_rat(a, d), _rat(a * c, b * d), _rat(b, c), _rat(C, A), _rat(a * b, c * d), _rat(a + c, b + d), _rat(A + C, C), _rat(A, A + C)],
               f'Make b the same number in both: a : b = {A} : {L} and b : c = {L} : {C}. So a : c = {A} : {C}' + ('.' if _rat(A, C) == f'{A} : {C}' else f' = {right}.'))


@gen('ratios', 1, 0)
def ra_diff(r):
    a, b = sorted(r.sample(range(1, 12), 2))
    g = math.gcd(a, b)
    a, b = a // g, b // g
    k = r.randint(2, 12)
    return ne(f'The ratio of x to y is {a} : {b}, and x + y = {(a + b) * k}. What is y − x?', (b - a) * k,
              f'{a + b} parts = {(a + b) * k}, so 1 part = {k}. x = {a * k}, y = {b * k}, difference = {(b - a) * k}. (Or: {b - a} part{"s" if b - a > 1 else ""} × {k}.)')


@gen('ratios', 3, 2)
def ra_change(r):
    while True:
        a, b, c, d, k = r.randint(1, 5), r.randint(2, 7), r.randint(1, 5), r.randint(1, 5), r.randint(2, 9)
        if math.gcd(a, b) == 1 and math.gcd(c, d) == 1 and F(c, d) > F(a, b):
            n = F(k * (c * b - d * a), d)
            if n.denominator == 1 and n > 0:
                break
    n = int(n)
    return ne(f'In a club the ratio of men to women is {a} : {b}. After {n} more men join, the ratio becomes {c} : {d}. How many women are in the club?', b * k,
              f'Let men = {a}k and women = {b}k. Then ({a}k + {n}) : {b}k = {c} : {d} → {d}({a}k + {n}) = {c}({b}k) → {d * a}k + {d * n} = {c * b}k → k = {k}. '
              f'Women = {b} × {k} = {b * k}. The number of women does not change - anchor on it.')


@gen('ratios', 2, 0)
def ra_three(r):
    a, b, c = sorted(r.sample(range(1, 10), 3))
    k = r.randint(2, 12)
    T = (a + b + c) * k
    return ne(f'${num(T)} is shared among three people in the ratio {a} : {b} : {c}. How many dollars does the person with the largest share get?', c * k,
              f'{a} + {b} + {c} = {a + b + c} parts; 1 part = {num(T)} ÷ {a + b + c} = {k}. Largest share = {c} × {k} = {c * k}.')


@gen('ratios', 1, 0)
def ra_scale(r):
    s, d = r.choice([F(5, 2), F(3, 2), 2, 4, 5, F(1, 2), 10, F(5, 4)]), r.randint(3, 15)
    return ne(f'On a map, 1 cm represents {dec(s)} km. Two towns are {d} cm apart on the map. How far apart are they in km?', s * d,
              f'{d} × {dec(s)} = {dec(s * d)} km.', show=dec)


# ====================================================================== 13. Rate, distance & age
def _avg_pairs():
    out = []
    for v1 in range(10, 95, 5):
        for v2 in range(v1 + 5, 125, 5):
            h = F(2 * v1 * v2, v1 + v2)
            if h.denominator == 1 and (v1 + v2) % 2 == 0 and (v1 + v2) // 2 != h:
                out.append((v1, v2, int(h)))
    return out


AVG_PAIRS = _avg_pairs()


@gen('word_motion', 2, 1)
def mo_avg(r):
    v1, v2, h = r.choice(AVG_PAIRS)
    D = math.lcm(v1, v2) * r.choice([1, 2])
    return mc(f'A car travels {D} km at {v1} km/h and returns the same {D} km at {v2} km/h. What is its average speed for the whole trip, in km/h?', h,
              [(v1 + v2) // 2, v2 - v1, h + 5, h - 5], f'Average speed = total distance ÷ total time = {2 * D} ÷ ({num(F(D, v1))} + {num(F(D, v2))}) = {2 * D} ÷ {num(F(D, v1) + F(D, v2))} = {h}. '
              f'Never just average the speeds ({(v1 + v2) // 2} is the trap) - more time is spent at the slower speed.', pos=True)


@gen('word_motion', 1, 2)
def mo_meet(r):
    v1, v2 = r.randint(3, 16) * 5, r.randint(3, 16) * 5
    t = r.choice([F(3, 2), 2, F(5, 2), 3, 4, F(1, 2), 1])
    D = (v1 + v2) * t
    return ne(f'Two trains are {dec(D)} km apart and travel towards each other at {v1} km/h and {v2} km/h. After how many hours do they meet?', t,
              f'Moving towards each other, the gap closes at {v1} + {v2} = {v1 + v2} km/h. Time = {dec(D)} ÷ {v1 + v2} = {dec(t)} hours.', show=dec)


@gen('word_motion', 2, 2)
def mo_catch(r):
    while True:
        v1, v2, h = r.randint(4, 12) * 5, r.randint(5, 16) * 5, r.randint(1, 4)
        if v2 > v1 and (v1 * h) % (v2 - v1) == 0:
            break
    t = v1 * h // (v2 - v1)
    a, b = r.sample(NAMES, 2)
    return ne(f'{a} leaves town at {v1} km/h. {h} hour{"s" if h > 1 else ""} later, {b} leaves from the same place along the same road at {v2} km/h. '
              f'How many hours after {b} sets off does {b} catch up?', t,
              f'Head start = {v1} × {h} = {v1 * h} km. Same direction → the gap closes at {v2} − {v1} = {v2 - v1} km/h. Time = {v1 * h} ÷ {v2 - v1} = {t} h.')


@gen('word_motion', 2, 3)
def mo_age(r):
    while True:
        m, k, n = r.randint(2, 5), r.randint(2, 4), r.randint(2, 20)
        if k < m and (n * (k - 1)) % (m - k) == 0:
            B = n * (k - 1) // (m - k)
            if 2 <= B <= 30:
                break
    a, b = r.sample(NAMES, 2)
    return mc(f'{a} is {m} times as old as {b}. In {n} years, {a} will be {k} times as old as {b}. How old is {a} now?', m * B,
              [B, m * B + n, k * B, m * (B + 1)], f'Let {b} = b now, so {a} = {m}b. In {n} years: {m}b + {n} = {k}(b + {n}) → {m - k}b = {k * n - n} → b = {B}. '
              f'{a} = {m} × {B} = {m * B}. A small table (now / in {n} years) keeps it straight.', pos=True)


@gen('word_motion', 3, 0)
def mo_late(r):
    while True:
        v1 = r.randint(2, 12) * 2
        v2 = v1 + r.choice([1, 2, 3, 4, 5, 6])
        d = r.randint(2, 30)
        tot = F(60 * d * (v2 - v1), v1 * v2)
        if tot.denominator == 1 and 10 <= tot <= 60:
            break
    tot = int(tot)
    late = r.randint(2, tot - 2)
    nm = r.choice(NAMES)
    return ne(f'Cycling at {v1} km/h, {nm} reaches the station {late} minutes late; at {v2} km/h {nm} arrives {tot - late} minutes early. How far away is the station, in km?', d,
              f'The two trips differ by {late} + {tot - late} = {tot} minutes = {num(F(tot, 60))} h. d/{v1} − d/{v2} = {num(F(tot, 60))} → '
              f'd × {num(F(v2 - v1, v1 * v2))} = {num(F(tot, 60))} → d = {d} km.')


@gen('word_motion', 1, 0)
def mo_basic(r):
    s, m = r.randint(4, 16) * 6, r.choice([10, 15, 20, 30, 40, 45, 50])
    d = F(s * m, 60)
    return ne(f'A cyclist covers {dec(d)} km in {m} minutes at a constant speed. What is the speed in km per hour?', s,
              f'{m} minutes = {num(F(m, 60))} hour. Speed = distance ÷ time = {dec(d)} ÷ {num(F(m, 60))} = {s} km/h. Convert minutes to hours first.')


# ====================================================================== 14. Work, mixtures & overlapping sets
def _nice(v):
    d = F(v).denominator
    return d in (1, 2, 4, 5, 10)


@gen('work_mix_sets', 1, 0)
def wk_together(r):
    while True:
        a, b = r.sample(range(2, 31), 2)
        t = F(a * b, a + b)
        if _nice(t) and t >= 1:
            break
    x, y = r.sample(NAMES, 2)
    return mc(f'{x} can finish a job alone in {a} hours and {y} can finish it alone in {b} hours. Working together at these rates, how many hours will they take?', t,
              [F(a + b, 2), abs(a - b), F(min(a, b), 2), a + b], f'Add rates: 1/{a} + 1/{b} = {num(F(1, a) + F(1, b))} of the job per hour. Time = 1 ÷ {num(F(1, a) + F(1, b))} = {dec(t)} hours. '
              f'Shortcut: ab/(a + b) = {a * b}/{a + b}. The answer must be less than the faster person alone ({min(a, b)} h).', show=dec, pos=True)


@gen('work_mix_sets', 2, 0)
def wk_pipe(r):
    while True:
        a, b = sorted(r.sample(range(2, 25), 2))
        t = F(a * b, b - a)
        if t.denominator == 1 and t <= 60:
            break
    return mc(f'A pipe can fill a tank in {a} hours and a drain can empty the full tank in {b} hours. With both open, how many hours does it take to fill the empty tank?', t,
              [F(a * b, a + b), b - a, a + b, t * 2], f'Net rate = 1/{a} − 1/{b} = {num(F(1, a) - F(1, b))} tank per hour, so the time is {num(t)} hours. Rates add; a drain\'s rate is subtracted.', show=dec, pos=True)


@gen('work_mix_sets', 3, 0)
def wk_partial(r):
    while True:
        a, b, t = r.randint(4, 12), r.randint(4, 15), r.randint(1, 3)
        rest = 1 - t * (F(1, a) + F(1, b))
        if rest > 0 and _nice(rest * b):
            break
    x, y = r.sample(NAMES, 2)
    return ne(f'{x} can do a job alone in {a} hours; {y} alone in {b} hours. They work together for {t} hour{"s" if t > 1 else ""}, then {x} leaves. How many more hours does {y} need to finish the job?',
              rest * b, f'Together they do {num(F(1, a) + F(1, b))} per hour, so in {t} h they finish {num(t * (F(1, a) + F(1, b)))}. Left: {num(rest)} of the job. '
              f'{y} does 1/{b} per hour → {num(rest)} × {b} = {dec(rest * b)} hours.', show=dec)


@gen('work_mix_sets', 2, 1)
def wk_mix(r):
    while True:
        v1, v2 = r.randint(1, 8) * 5, r.randint(1, 8) * 5
        p1, p2 = r.sample([10, 20, 25, 30, 40, 50, 60], 2)
        c = F(v1 * p1 + v2 * p2, v1 + v2)
        if _nice(c):
            break
    return mc(f'{v1} litres of a {p1}% salt solution are mixed with {v2} litres of a {p2}% salt solution. What is the salt concentration of the mixture?', c,
              [F(p1 + p2, 2), c + 2, c - 2, F(p1 * v2 + p2 * v1, v1 + v2)], f'Track the salt: {dec(F(v1 * p1, 100))} + {dec(F(v2 * p2, 100))} = {dec(F(v1 * p1 + v2 * p2, 100))} litres in {v1 + v2} litres '
              f'→ {pct(c)}. Sanity check: the answer is closer to the concentration you have more of.', show=pct)


@gen('work_mix_sets', 2, 1)
def wk_dilute(r):
    while True:
        V, p, q = r.randint(2, 12) * 5, r.choice([20, 25, 30, 40, 50, 60]), r.choice([5, 10, 12, 15, 20, 25, 30])
        W = F(V * (p - q), q)
        if q < p and W.denominator == 1:
            break
    return ne(f'How many litres of water must be added to {V} litres of a {p}% acid solution to make a {q}% acid solution?', W,
              f'The acid stays the same: {dec(F(V * p, 100))} litres. It must be {q}% of the new total: {dec(F(V * p, 100))} ÷ {dec(F(q, 100))} = {num(V + W)} litres. '
              f'Water to add = {num(V + W)} − {V} = {num(W)}.')


@gen('work_mix_sets', 1, 2)
def wk_sets(r):
    T = r.randint(4, 12) * 10
    a, b = r.randint(T // 4, T // 2 + 5), r.randint(T // 4, T // 2 + 5)
    both = r.randint(3, min(a, b) - 2)
    neither = T - (a + b - both)
    if neither < 0:
        T += -neither + 5
        neither = 5
    if r.random() < .5:
        return ne(f'In a class of {T} students, {a} study French, {b} study Spanish and {both} study both. How many study neither?', neither,
                  f'Either language = {a} + {b} − {both} = {a + b - both} (subtract "both" once, since they were counted twice). Neither = {T} − {a + b - both} = {neither}.')
    return ne(f'Of {T} people, {a} like tea, {b} like coffee and {neither} like neither. How many like both?', both,
              f'At least one = {T} − {neither} = {T - neither}. Total = A + B − Both + Neither → {T} = {a} + {b} − Both + {neither} → Both = {both}.')


# ====================================================================== 15. Sequences & series
@gen('sequences', 1, 0)
def sq_arith(r):
    a1, d = r.randint(-10, 20), _nz(r, -6, 9)
    i, j = sorted(r.sample(range(2, 15), 2))
    ti, tj = a1 + (i - 1) * d, a1 + (j - 1) * d
    return mc(f'In an arithmetic sequence, term {i} is {num(ti)} and term {j} is {num(tj)}. What is the first term?', a1,
              [ti - i * d, ti - d, a1 + d, tj - j * d], f'From term {i} to term {j} is {j - i} steps, adding {num(tj - ti)}, so d = {num(d)}. '
              f'First term = {num(ti)} − {i - 1} × ({num(d)}) = {num(a1)}. (aₙ = a₁ + (n − 1)d.)')


@gen('sequences', 2, 1)
def sq_sum(r):
    if r.random() < .5:
        a, b = r.randint(1, 30), r.randint(40, 120)
        n = b - a + 1
        return ne(f'What is the sum of all integers from {a} to {b}, inclusive?', n * (a + b) // 2 if n * (a + b) % 2 == 0 else F(n * (a + b), 2),
                  f'Number of terms = {b} − {a} + 1 = {n}. Average = ({a} + {b}) ÷ 2 = {num(F(a + b, 2))}. Sum = {n} × {num(F(a + b, 2))} = {num(F(n * (a + b), 2))}.')
    a, b = 2 * r.randint(1, 15), 2 * r.randint(25, 60)
    n = (b - a) // 2 + 1
    return ne(f'What is the sum of the even integers from {a} to {b}, inclusive?', n * (a + b) // 2,
              f'Number of terms = ({b} − {a}) ÷ 2 + 1 = {n}. Average = ({a} + {b}) ÷ 2 = {(a + b) // 2}. Sum = {n} × {(a + b) // 2} = {num(n * (a + b) // 2)}.')


@gen('sequences', 1, 1)
def sq_count(r):
    k, a, b = r.randint(3, 13), r.randint(10, 150), r.randint(200, 999)
    v = b // k - (a - 1) // k
    first, last = ((a + k - 1) // k) * k, (b // k) * k
    return ne(f'How many multiples of {k} are there from {a} to {b}, inclusive?', v,
              f'First multiple ≥ {a} is {first}; last ≤ {b} is {last}. Count = ({last} − {first}) ÷ {k} + 1 = {v}.')


@gen('sequences', 2, 2)
def sq_geo(r):
    a, q, n = r.randint(1, 5), r.choice([2, 3, -2]), r.randint(4, 7)
    v = a * q ** (n - 1)
    return mc(f'In a sequence, the first term is {a} and each term after the first is {num(q)} times the previous term. What is term {n}?', v,
              [a * q ** n, a * q ** (n - 2), a + q * (n - 1), -v], f'Term n = first × ratio^(n − 1) = {a} × ({num(q)}){sup(n - 1)} = {num(v)}. There are {n - 1} multiplications to reach term {n}.')


@gen('sequences', 2, 2)
def sq_rec(r):
    s, p, c = r.randint(1, 5), r.choice([2, 3, -1]), _nz(r, -3, 4)
    seq = [s]
    for _ in range(4):
        seq.append(p * seq[-1] + c)
    return ne(f'A sequence has a₁ = {s} and aₙ = {num(p)}aₙ₋₁{term(c)} for n > 1. What is a₅?', seq[4],
              'Build it term by term: ' + ', '.join(f'a{"₁₂₃₄₅"[i]} = {num(v)}' for i, v in enumerate(seq)) + '. For short recursive sequences just list the terms.')


@gen('sequences', 1, 1)
def sq_inclusive(r):
    a, b = r.randint(5, 80), r.randint(100, 400)
    nm = r.choice(NAMES)
    return ne(f'{nm} reads pages {a} to {b} of a book, inclusive. How many pages is that?', b - a + 1,
              f'Inclusive count = last − first + 1 = {b} − {a} + 1 = {b - a + 1}. Forgetting the +1 is the classic error.')


# ====================================================================== 16. Statistics
@gen('stats', 1, 0)
def st_remove(r):
    n, m = r.randint(4, 9), r.randint(8, 30)
    m2 = m - _nz(r, -4, 4)
    x = n * m - (n - 1) * m2
    if x <= 0:
        m2, x = m - 2, n * m - (n - 1) * (m - 2)
    return mc(f'The average of {n} numbers is {m}. When one number is removed, the average of the remaining numbers is {m2}. What number was removed?', x,
              [m - m2, m, n * m - n * m2, x + m2], f'Total before = {n} × {m} = {n * m}. Total after = {n - 1} × {m2} = {(n - 1) * m2}. Removed = {n * m} − {(n - 1) * m2} = {x}. '
              'Sum = mean × count is the key stats fact.')


@gen('stats', 1, 1)
def st_median(r):
    n = r.choice([6, 7, 8])
    data = r.sample(range(1, 40), n)
    s = sorted(data)
    med = F(s[n // 2]) if n % 2 else F(s[n // 2 - 1] + s[n // 2], 2)
    return mc('What is the median of the list ' + ', '.join(map(str, data)) + '?', med, [data[n // 2], F(sum(data), n), s[n // 2], s[n // 2 - 1]],
              f'Sort first: {", ".join(map(str, s))}. ' + (f'Odd count → middle value {num(med)}.' if n % 2 else f'Even count → average the middle two: ({s[n // 2 - 1]} + {s[n // 2]}) ÷ 2 = {dec(med)}.'), show=dec)


@gen('stats', 2, 1)
def st_weighted(r):
    while True:
        na, nb, ma_, mb = r.randint(1, 8) * 5, r.randint(1, 8) * 5, r.randint(55, 90), r.randint(55, 90)
        avg = F(na * ma_ + nb * mb, na + nb)
        if ma_ != mb and na != nb and _nice(avg):
            break
    return mc(f'Group A ({na} students) has an average score of {ma_} and group B ({nb} students) has an average of {mb}. What is the average of all {na + nb} students?', avg,
              [F(ma_ + mb, 2), avg + 1, avg - 1, F(na * mb + nb * ma_, na + nb)], f'({na} × {ma_} + {nb} × {mb}) ÷ {na + nb} = {na * ma_ + nb * mb} ÷ {na + nb} = {dec(avg)}. '
              'The weighted average sits closer to the bigger group.', show=dec)


ST_SD = [
    ('If 5 is added to every number in a data set, what happens to the standard deviation?', 'It does not change',
     ['It increases by 5', 'It increases by 25', 'It is multiplied by 5', 'It decreases by 5'], 'Adding a constant shifts every value equally; the spread is unchanged.'),
    ('If every number in a data set is multiplied by 3, what happens to the standard deviation?', 'It is multiplied by 3',
     ['It does not change', 'It is multiplied by 9', 'It increases by 3', 'It is divided by 3'], 'Multiplying by k multiplies every distance from the mean by k, so the SD is multiplied by |k|.'),
    ('A number equal to the mean is added to a data set (that is not all equal). What happens to the standard deviation?', 'It decreases',
     ['It increases', 'It does not change', 'It doubles', 'It cannot be determined'], 'The new value is 0 from the mean, so the average distance from the mean gets smaller.'),
    ('Which data set has the greatest standard deviation?', '{1, 10, 19}', ['{9, 10, 11}', '{10, 10, 10}', '{5, 10, 15}', '{8, 10, 12}'],
     'All have mean 10; {1, 10, 19} is the most spread out. SD measures spread, not size.'),
    ('Two numbers far from the mean are removed from a data set. What happens to the standard deviation?', 'It decreases',
     ['It increases', 'It does not change', 'It becomes 0', 'It cannot be determined'], 'Removing the most spread-out values makes the remaining data tighter around the mean.'),
]


@gen('stats', 2, 2)
def st_sd(r):
    q, right, wrong, x = r.choice(ST_SD)
    return mct(r, q, right, wrong, x)


@gen('stats', 2, 2)
def st_normal(r):
    m, s = r.randint(5, 20) * 5, r.randint(2, 10)
    k = r.randint(0, 3)
    q, v = [(f'between {m - s} and {m + s}', 68), (f'between {m} and {m + 2 * s}', F(95, 2)), (f'greater than {m + s}', 16), (f'less than {m - 2 * s}', F(5, 2))][k]
    return mct(r, f'A set of measurements is normally distributed with mean {m} and standard deviation {s}. Approximately what percent of the measurements are {q}?',
               pct(v), [pct(x) for x in (68, F(95, 2), 16, F(5, 2), 34, 95, 50) if x != v],
               'Normal distribution: about 68% lie within 1 SD of the mean (34% on each side), about 95% within 2 SD (47.5% each side), '
               f'so about 16% are above +1 SD and 2.5% below −2 SD. Here that gives {pct(v)}.')


@gen('stats', 1, 0)
def st_needed(r):
    n, target = r.randint(3, 5), r.randint(70, 90)
    scores = [target + r.randint(-12, 12) for _ in range(n)]
    need = target * (n + 1) - sum(scores)
    if not 40 <= need <= 100:
        scores[0] += need - 85
        need = 85
    return ne(f'A student scored {", ".join(map(str, scores))} on the first {n} tests. What score is needed on the next test for an average of exactly {target}?', need,
              f'Needed total = {target} × {n + 1} = {target * (n + 1)}. Current total = {sum(scores)}. Next score = {target * (n + 1)} − {sum(scores)} = {need}.')


# ====================================================================== 17. Counting
@gen('counting', 1, 0)
def ct_fcp(r):
    a, b, c = r.randint(2, 6), r.randint(2, 5), r.randint(2, 4)
    return mc(f'A menu offers {a} starters, {b} main courses and {c} desserts. How many different 3-course meals (one of each) are possible?', a * b * c,
              [a + b + c, a * b + c, a * b * c * 2, math.comb(a + b + c, 3)], f'Fundamental counting principle - multiply the choices at each step: {a} × {b} × {c} = {a * b * c}.', pos=True)


@gen('counting', 1, 1)
def ct_perm(r):
    n, k = r.randint(5, 10), r.randint(2, 3)
    roles = ['a president', 'a vice-president', 'a treasurer'][:k]
    return mc(f'From a club of {n} members, {", ".join(roles[:-1])} and {roles[-1]} are chosen (no one holds two roles). In how many ways can this be done?', math.perm(n, k),
              [math.comb(n, k), n ** k, n * k, math.perm(n, k) // 2], f'Order matters (the roles are different): {" × ".join(str(n - i) for i in range(k))} = {math.perm(n, k)}. '
              f'If the {k} people had identical roles, you would divide by {k}! to get C({n},{k}) = {math.comb(n, k)}.', pos=True)


@gen('counting', 1, 2)
def ct_comb(r):
    n, k = r.randint(6, 12), r.randint(2, 4)
    return mc(f'In how many ways can a committee of {k} be chosen from {n} people?', math.comb(n, k),
              [math.perm(n, k), n * k, math.comb(n, k - 1), math.comb(n, k) * 2], f'Order does not matter: C({n},{k}) = ({" × ".join(str(n - i) for i in range(k))}) ÷ {k}! = '
              f'{math.perm(n, k)} ÷ {math.factorial(k)} = {math.comb(n, k)}.', pos=True)


WORDS = ['LEVEL', 'BANANA', 'ATTEND', 'LETTER', 'APPLE', 'PEPPER', 'COFFEE', 'GOOGLE', 'BOOKS', 'TOOTH', 'ASSESS', 'SEEDS']


@gen('counting', 2, 1)
def ct_repeat(r):
    w = r.choice(WORDS)
    cnt = Counter(w)
    reps = [c for c in cnt.values() if c > 1]
    v = math.factorial(len(w)) // math.prod(math.factorial(c) for c in reps)
    rep_txt = ', '.join(f'{c} {k}s' for k, c in cnt.items() if c > 1)
    return mc(f'How many different arrangements are there of the letters in the word {w}?', v,
              [math.factorial(len(w)), math.factorial(len(w)) // math.factorial(max(reps)), v * 2, math.factorial(len(w) - 1)],
              f'{len(w)}! arrangements if all letters were different, but the repeats ({rep_txt}) are identical, so divide by each repeat\'s factorial: '
              f'{len(w)}! ÷ ({" × ".join(f"{c}!" for c in reps)}) = {math.factorial(len(w))} ÷ {math.prod(math.factorial(c) for c in reps)} = {v}.', pos=True)


@gen('counting', 2, 3)
def ct_together(r):
    n = r.randint(4, 7)
    tog = 2 * math.factorial(n - 1)
    if r.random() < .5:
        return mc(f'{n} people sit in a row. If two particular people must sit next to each other, how many seatings are possible?', tog,
                  [math.factorial(n - 1), math.factorial(n), math.factorial(n) - tog, 2 * math.factorial(n - 2)],
                  f'Glue the pair into one unit: {n - 1} units → {n - 1}! = {math.factorial(n - 1)} arrangements, × 2 for the order within the pair = {tog}.', pos=True)
    return mc(f'{n} people sit in a row. If two particular people must NOT sit next to each other, how many seatings are possible?', math.factorial(n) - tog,
              [tog, math.factorial(n), math.factorial(n - 1), math.factorial(n) - math.factorial(n - 1)],
              f'Total − together: {n}! − 2 × {n - 1}! = {math.factorial(n)} − {tog} = {math.factorial(n) - tog}. "Not" questions are easiest as total minus the opposite.', pos=True)


@gen('counting', 3, 3)
def ct_committee(r):
    w, m, k = r.randint(3, 6), r.randint(3, 7), r.randint(3, 4)
    if r.random() < .5:
        j = r.randint(1, min(w, k - 1))
        v = math.comb(w, j) * math.comb(m, k - j)
        return mc(f'A committee of {k} is chosen from {w} women and {m} men. How many committees have exactly {j} wom{"a" if j == 1 else "e"}n?', v,
                  [math.comb(w + m, k), math.comb(w, j) + math.comb(m, k - j), math.comb(w + m, k) - math.comb(m, k), math.perm(w, j) * math.perm(m, k - j)],
                  f'Choose the women and the men separately, then multiply: C({w},{j}) × C({m},{k - j}) = {math.comb(w, j)} × {math.comb(m, k - j)} = {v}.', pos=True)
    v = math.comb(w + m, k) - math.comb(m, k)
    return mc(f'A committee of {k} is chosen from {w} women and {m} men. How many committees include at least one woman?', v,
              [math.comb(w + m, k), math.comb(w, 1) * math.comb(w + m - 1, k - 1), math.comb(m, k), math.comb(w, 1) * math.comb(m, k - 1)],
              f'"At least one" = total − none: C({w + m},{k}) − C({m},{k}) = {math.comb(w + m, k)} − {math.comb(m, k)} = {v}.', pos=True)


def pmc(*a, **k):
    return mc(*a, hi=1, pos=True, **k)


# ====================================================================== 18. Probability
@gen('probability', 1, 0)
def pb_dice(r):
    s = r.randint(3, 11)
    if r.random() < .6:
        ways = sum(1 for a in range(1, 7) for b in range(1, 7) if a + b == s)
        return pmc(f'Two fair six-sided dice are rolled. What is the probability that the sum is {s}?', F(ways, 36), [F(1, 6), F(ways, 12), F(s, 36), F(1, 11)],
                  f'36 equally likely outcomes. Pairs with sum {s}: {ways}. Probability = {ways}/36 = {num(F(ways, 36))}.')
    ways = sum(1 for a in range(1, 7) for b in range(1, 7) if a + b >= s)
    return pmc(f'Two fair six-sided dice are rolled. What is the probability that the sum is at least {s}?', F(ways, 36), [F(ways - 1, 36), F(36 - ways, 36), F(1, 2), F(ways, 12)],
              f'Count outcomes with sum ≥ {s}: {ways} of 36 → {num(F(ways, 36))}.')


@gen('probability', 2, 2)
def pb_atleast(r):
    if r.random() < .5:
        n = r.randint(2, 6)
        return pmc(f'A fair coin is tossed {n} times. What is the probability of getting at least one head?', 1 - F(1, 2 ** n),
                  [F(1, 2 ** n), F(1, 2), F(n, 2 ** n), F(n, n + 1)], f'Use the complement: P(no heads) = (1/2){sup(n)} = 1/{2 ** n}. P(at least one) = 1 − 1/{2 ** n} = {num(1 - F(1, 2 ** n))}.')
    n = r.randint(2, 3)
    return pmc(f'A fair die is rolled {n} times. What is the probability of rolling at least one 6?', 1 - F(5, 6) ** n,
              [F(n, 6), F(5, 6) ** n, F(1, 6) ** n, F(1, 2)], f'P(no 6 in one roll) = 5/6, so P(no 6 in {n} rolls) = {num(F(5, 6) ** n)}. P(at least one 6) = {num(1 - F(5, 6) ** n)}. '
              f'Adding 1/6 {n} times ({num(F(n, 6))}) is the trap.')


@gen('probability', 2, 2)
def pb_norep(r):
    R, B = r.randint(3, 7), r.randint(2, 6)
    T = R + B
    if r.random() < .5:
        v = F(R, T) * F(R - 1, T - 1)
        return pmc(f'A bag holds {R} red and {B} blue marbles. Two are drawn without replacement. What is the probability that both are red?', v,
                  [F(R, T) ** 2, F(R, T), F(R - 1, T), F(R * (R - 1), T * T)], f'{R}/{T} × {R - 1}/{T - 1} = {num(v)}. After one red is taken, there is one fewer red and one fewer marble.')
    v = 2 * F(R, T) * F(B, T - 1)
    return pmc(f'A bag holds {R} red and {B} blue marbles. Two are drawn without replacement. What is the probability of getting one of each colour?', v,
              [F(R, T) * F(B, T - 1), F(R * B, T * T), F(1, 2), 2 * F(R * B, T * T)], f'Red then blue: {R}/{T} × {B}/{T - 1}; blue then red: {B}/{T} × {R}/{T - 1}. '
              f'Add both orders: {num(v)}. (Or C({R},1)·C({B},1)/C({T},2).)')


@gen('probability', 2, 1)
def pb_or(r):
    a, b = r.choice([F(1, 5), F(3, 10), F(2, 5), F(1, 2), F(3, 5), F(1, 4)]), r.choice([F(1, 5), F(3, 10), F(2, 5), F(1, 2), F(1, 4)])
    v = a + b - a * b
    return pmc(f'Events A and B are independent, with P(A) = {dec(a)} and P(B) = {dec(b)}. What is P(A or B)?', v,
              [a + b if a + b <= 1 else None, a * b, 1 - a * b, 1 - (1 - a) - (1 - b) if a + b > 1 else None, v + F(1, 10)],
              f'P(A or B) = P(A) + P(B) − P(A and B) = {dec(a)} + {dec(b)} − {dec(a)} × {dec(b)} = {dec(v)}. (Or: 1 − P(neither) = 1 − {dec(1 - a)} × {dec(1 - b)}.)', show=dec)


@gen('probability', 1, 1)
def pb_multiple(r):
    N = r.choice([20, 24, 30, 36, 40, 50, 60])
    a, b = r.sample([2, 3, 4, 5, 6, 7], 2)
    L = math.lcm(a, b)
    v = N // a + N // b - N // L
    return pmc(f'A number is picked at random from the integers 1 to {N}. What is the probability that it is a multiple of {a} or of {b}?', F(v, N),
              [F(N // a + N // b, N), F(N // L, N), F(N // a, N), F(v + 1, N)],
              f'Multiples of {a}: {N // a}; of {b}: {N // b}; of both (multiples of {L}): {N // L}. {N // a} + {N // b} − {N // L} = {v}, so P = {v}/{N} = {num(F(v, N))}.')


@gen('probability', 3, 2)
def pb_pick(r):
    n, k = r.randint(6, 10), r.randint(3, 4)
    a, b = r.sample(NAMES, 2)
    v = F(math.comb(n - 2, k - 2), math.comb(n, k))
    return pmc(f'{k} people are chosen at random from a group of {n} that includes {a} and {b}. What is the probability that both {a} and {b} are chosen?', v,
              [F(k, n) ** 2, F(k, n), F(1, math.comb(n, k)), F(2, n)],
              f'Total groups: C({n},{k}) = {math.comb(n, k)}. Groups containing both: choose the other {k - 2} from the remaining {n - 2}: C({n - 2},{k - 2}) = {math.comb(n - 2, k - 2)}. '
              f'P = {math.comb(n - 2, k - 2)}/{math.comb(n, k)}' + (f' = {num(v)}.' if v.numerator != math.comb(n - 2, k - 2) else '.'))


# ====================================================================== 19. Data interpretation
def _table(r):
    y0 = r.randint(2016, 2020)
    vals = [r.randint(6, 24) * 5 for _ in range(5)]
    for i in range(1, 5):
        if vals[i] == vals[i - 1]:
            vals[i] += 5
    yrs = [y0 + i for i in range(5)]
    co = r.choice(['Company X', 'Brand Y', 'Store Z'])
    head = f'Annual revenue of {co} ($ millions)\n' + '   '.join(f'{y}: {v}' for y, v in zip(yrs, vals)) + '\n\n'
    return yrs, vals, head


@gen('di', 1, 0)
def di_change(r):
    yrs, vals, head = _table(r)
    i = r.randint(0, 3)
    a, b = vals[i], vals[i + 1]
    v = F(b - a, a) * 100
    right = round(abs(v))
    word = 'increase' if b > a else 'decrease'
    return mc(head + f'Approximately what was the percent {word} in revenue from {yrs[i]} to {yrs[i + 1]}?', right,
              [round(abs(F(b - a, b)) * 100), abs(b - a), round(abs(v)) + 10, round(abs(v)) * 2], f'Percent change = change ÷ starting value = {abs(b - a)} ÷ {a} ≈ {float(abs(v)):.1f}%. '
              f'Dividing by the later year ({b}) is the common mistake.', show=lambda x: f'{num(x)}%', step=4, pos=True)


@gen('di', 1, 1)
def di_avg(r):
    yrs, vals, head = _table(r)
    return ne(head + f'What was the average annual revenue over the five years, in $ millions?', F(sum(vals), 5),
              f'Total = {" + ".join(map(str, vals))} = {sum(vals)}. Average = {sum(vals)} ÷ 5 = {dec(F(sum(vals), 5))}.', show=dec)


@gen('di', 2, 0)
def di_biggest(r):
    while True:
        yrs, vals, head = _table(r)
        ch = [F(vals[i + 1] - vals[i], vals[i]) for i in range(4)]
        best = max(range(4), key=lambda i: ch[i])
        if ch[best] > 0 and sorted(ch)[-1] - sorted(ch)[-2] > F(2, 100):
            break
    return mct(r, head + 'In which year was the percent increase in revenue over the previous year the greatest?', str(yrs[best + 1]),
               [str(y) for y in yrs[1:] if y != yrs[best + 1]] + ['Cannot be determined'],
               'Percent change each year: ' + ', '.join(f'{yrs[i + 1]}: {float(ch[i]) * 100:+.0f}%'.replace('-', '−') for i in range(4)) + f'. Greatest: {yrs[best + 1]}. '
               'The biggest jump in dollars is not always the biggest percent - smaller starting values give bigger percents.')


@gen('di', 2, 2)
def di_share(r):
    yrs, vals, head = _table(r)
    i = r.randint(0, 4)
    v = F(vals[i], sum(vals)) * 100
    return mc(head + f'Revenue in {yrs[i]} was approximately what percent of total revenue for the five years?', round(v),
              [round(F(vals[i], sum(vals) - vals[i]) * 100), 20, round(v) + 9, round(v) * 2], f'{vals[i]} ÷ {sum(vals)} ≈ {float(v):.1f}%. '
              f'Estimate first: one year out of five averages 20%, and {yrs[i]} is a {"bigger" if v > 20 else "smaller"}-than-average year, so expect {"more" if v > 20 else "less"} than 20%.', show=lambda x: f'{num(x)}%', step=4, pos=True)


@gen('di', 2, 1)
def di_budget(r):
    T = r.choice([200, 400, 500, 800, 1000, 1200])
    parts = r.sample([10, 15, 20, 25, 30, 35], 3)
    parts.append(100 - sum(parts))
    if parts[-1] <= 0:
        parts = [40, 25, 20, 15]
    cats = ['Salaries', 'Rent', 'Marketing', 'Other']
    head = f'A company\'s annual budget of ${T} thousand is split: ' + ', '.join(f'{c} {p}%' for c, p in zip(cats, parts)) + '.\n\n'
    i, j = r.sample(range(4), 2)
    v = F(T * (parts[i] - parts[j]), 100)
    return ne(head + f'How many thousand dollars more is spent on {cats[i]} than on {cats[j]}?', v,
              f'Difference in share = {parts[i]}% − {parts[j]}% = {parts[i] - parts[j]}%. {parts[i] - parts[j]}% of {T} = {dec(v)} thousand dollars.', show=dec)


# ====================================================================== 20. Lines, angles & triangles
@gen('triangles', 1, 0)
def tr_ratio(r):
    while True:
        a, b, c = sorted(r.sample(range(1, 10), 3))
        if 180 % (a + b + c) == 0:
            break
    k = 180 // (a + b + c)
    big = r.random() < .5
    v = c * k if big else a * k
    return mc(f'The angles of a triangle are in the ratio {a} : {b} : {c}. What is the {"largest" if big else "smallest"} angle, in degrees?', v,
              [c * 10 if big else a * 10, 180 // c if big else 180 // a, b * k, 90], f'{a} + {b} + {c} = {a + b + c} parts = 180°, so 1 part = {k}°. Answer: {v}°.', show=lambda x: f'{num(x)}°', pos=True)


@gen('triangles', 1, 0)
def tr_exterior(r):
    a, b = r.randint(25, 80), r.randint(25, 80)
    return ne(f'In a triangle, two interior angles are {a}° and {b}°. What is the exterior angle at the third vertex, in degrees?', a + b,
              f'An exterior angle equals the sum of the two remote interior angles: {a} + {b} = {a + b}°. (Third interior angle = {180 - a - b}°, and {180} − {180 - a - b} = {a + b}.)')


TRIPLES = [(3, 4, 5), (5, 12, 13), (8, 15, 17), (7, 24, 25)]


@gen('triangles', 1, 1)
def tr_pyth(r):
    a, b, c = r.choice(TRIPLES)
    k = r.randint(1, 4) if c < 20 else 1
    a, b, c = a * k, b * k, c * k
    if r.random() < .5:
        return ne(f'A right triangle has legs of length {a} and {b}. What is the length of the hypotenuse?', c,
                  f'{a}² + {b}² = {a * a} + {b * b} = {c * c} = {c}². Spot the triple: a multiple of {a // k}-{b // k}-{c // k}.')
    return ne(f'A right triangle has a hypotenuse of {c} and one leg of {a}. What is the length of the other leg?', b,
              f'{c}² − {a}² = {c * c} − {a * a} = {b * b}, so the leg is {b} (the {a // k}-{b // k}-{c // k} triple × {k}).')


@gen('triangles', 2, 2)
def tr_special(r):
    k = r.randint(1, 6)
    v = r.randint(0, 2)
    if v == 0:
        return mc(f'An isosceles right triangle has a hypotenuse of {2 * k}. What is its area?', F(k * k), [2 * k * k, 4 * k * k, F(k * k, 2), 2 * k], f'45-45-90 sides are x : x : x√2. x√2 = {2 * k} → x = {k}√2. Area = ½ × x × x = ½ × {2 * k * k} = {k * k}.', pos=True)
    if v == 1:
        return mct(r, f'In a 30-60-90 triangle the shortest side is {k}. What is the length of the longest side?', str(2 * k),
                   [f'{k}√3', f'{k}√2', str(3 * k), f'{2 * k}√3'], f'30-60-90 sides are x : x√3 : 2x. With x = {k}, the hypotenuse (longest) is {2 * k}; the middle side is {k}√3.')
    s = 2 * k
    return mct(r, f'What is the area of an equilateral triangle with side {s}?', f'{k * k}√3' if k > 1 else '√3',
               [f'{s * s // 2}√3', f'{s * s}', f'{k * k * 2}', f'{s * s // 4 * 2}√2'],
               f'Area = (√3/4) × side² = (√3/4) × {s * s} = {k * k}√3. (Or: height = {k}√3 from a 30-60-90 half, area = ½ × {s} × {k}√3.)')


@gen('triangles', 2, 3)
def tr_third(r):
    a, b = r.sample(range(3, 15), 2)
    lo, hi = abs(a - b), a + b
    if r.random() < .5:
        return ne(f'Two sides of a triangle have lengths {a} and {b}. How many different integer lengths are possible for the third side?', hi - lo - 1,
                  f'The third side must be strictly between the difference ({lo}) and the sum ({hi}): {lo} < c < {hi}. Integers {lo + 1} to {hi - 1}: {hi - lo - 1} values.')
    ok = r.randint(lo + 1, hi - 1)
    return mct(r, f'Two sides of a triangle are {a} and {b}. Which of the following could be the length of the third side?', str(ok),
               [str(v) for v in dict.fromkeys([lo, hi, hi + r.randint(1, 4), lo - 1, hi + 5, 2 * hi]) if v > 0],
               f'Third side must be greater than the difference ({lo}) and less than the sum ({hi}). Only {ok} fits; {lo} and {hi} themselves are not allowed.')


@gen('triangles', 2, 3)
def tr_similar(r):
    a, b = r.sample(range(1, 6), 2)
    A = a * a * r.randint(1, 6)
    v = F(A * b * b, a * a)
    return mc(f'Two triangles are similar, with corresponding sides in the ratio {a} : {b}. If the first triangle has area {A}, what is the area of the second?', v, [F(A * b, a), A * b, F(A * b ** 3, a ** 3), A + b - a],
              f'Areas scale with the square of the side ratio: {A} × ({b}/{a})² = {A} × {b * b}/{a * a} = {num(v)}. Using the plain ratio ({num(F(A * b, a))}) is the trap.')


# ====================================================================== 21. Circles, polygons & solids
@gen('circles_polys', 1, 0)
def cp_angles(r):
    n = r.choice([5, 6, 8, 9, 10, 12, 15, 18, 20])
    if r.random() < .5:
        return ne(f'What is the sum of the interior angles of a polygon with {n} sides, in degrees?', (n - 2) * 180,
                  f'Sum = (n − 2) × 180 = {n - 2} × 180 = {(n - 2) * 180}°. (The polygon splits into {n - 2} triangles.)')
    return ne(f'What is each interior angle of a regular polygon with {n} sides, in degrees?', F((n - 2) * 180, n),
              f'Sum = {n - 2} × 180 = {(n - 2) * 180}°; ÷ {n} = {dec(F((n - 2) * 180, n))}°. Shortcut: exterior angle = 360/{n} = {dec(F(360, n))}°, interior = 180 − exterior.', show=dec)


def pi(v):
    v = F(v)
    return ('' if v == 1 else num(v)) + 'π'


def picks(v, cands):
    """Wrong 'kπ' choices: whole-number candidates, topped up with nearby multiples."""
    ws = [w for w in dict.fromkeys(F(c) for c in cands) if w.denominator == 1 and w > 0 and w != v]
    k = 1
    while len(ws) < 4:
        for w in (v + k, v * (k + 1)):
            if w not in ws and w != v and len(ws) < 4:
                ws.append(F(w))
        k += 1
    return [pi(w) for w in ws]


@gen('circles_polys', 1, 1)
def cp_circle(r):
    rad = r.randint(2, 12)
    if r.random() < .5:
        return mct(r, f'A circle has area {pi(rad * rad)}. What is its circumference?', pi(2 * rad), [pi(v) for v in (rad, 4 * rad, rad * rad, 2 * rad * rad, 3 * rad, 4 * rad * rad)],
                   f'πr² = {pi(rad * rad)} → r = {rad}. Circumference = 2πr = {pi(2 * rad)}.')
    return mct(r, f'A circle has circumference {pi(2 * rad)}. What is its area?', pi(rad * rad), [pi(v) for v in (4 * rad * rad, 2 * rad, rad, 2 * rad * rad, (rad + 1) ** 2, rad * rad + 2 * rad)],
               f'2πr = {pi(2 * rad)} → r = {rad}. Area = πr² = {pi(rad * rad)}.')


@gen('circles_polys', 2, 1)
def cp_arc(r):
    while True:
        rad, th = r.randint(2, 18), r.choice([30, 40, 45, 60, 72, 90, 120, 135, 150, 240])
        if r.random() < .5:
            v = F(th * 2 * rad, 360)
            if v.denominator == 1:
                return mct(r, f'In a circle of radius {rad}, what is the length of an arc with a central angle of {th}°?', pi(v),
                           picks(v, (F(th * rad * rad, 360), 2 * rad, 2 * v, rad, 3 * v)),
                           f'Arc = (angle/360) × 2πr = ({th}/360) × {pi(2 * rad)} = {pi(v)}.')
        else:
            v = F(th * rad * rad, 360)
            if v.denominator == 1:
                return mct(r, f'In a circle of radius {rad}, what is the area of a sector with a central angle of {th}°?', pi(v),
                           picks(v, (F(th * 2 * rad, 360), rad * rad, 2 * v, v + rad, 3 * v)),
                           f'Sector = (angle/360) × πr² = ({th}/360) × {pi(rad * rad)} = {pi(v)}.')


QUADS = [(1, 2, 2, 3), (2, 3, 6, 7), (1, 4, 8, 9), (4, 4, 7, 9), (2, 6, 9, 11), (6, 6, 7, 11), (2, 10, 11, 15), (3, 4, 12, 13), (8, 9, 12, 17)]


@gen('circles_polys', 2, 2)
def cp_solids(r):
    if r.random() < .5:
        rad, h = r.randint(1, 6), r.randint(2, 10)
        return mct(r, f'What is the volume of a cylinder with radius {rad} and height {h}?', pi(rad * rad * h),
                   picks(rad * rad * h, (2 * rad * h, rad * h, rad * rad * h * 2, 2 * rad * rad + 2 * rad * h)),
                   f'V = πr²h = π × {rad * rad} × {h} = {pi(rad * rad * h)}. (2πrh is the curved surface area, not the volume.)')
    a, b, c, d = r.choice(QUADS)
    k = r.randint(1, 2)
    return ne(f'A rectangular box measures {a * k} × {b * k} × {c * k}. What is the length of the longest straight line that fits inside it (the space diagonal)?', d * k,
              f'Diagonal = √(l² + w² + h²) = √({(a * k) ** 2} + {(b * k) ** 2} + {(c * k) ** 2}) = √{(d * k) ** 2} = {d * k}.')


@gen('circles_polys', 1, 0)
def cp_rect(r):
    a, b, c = r.choice(TRIPLES[:3])
    k = r.randint(1, 3)
    return mc(f'A rectangle has a diagonal of {c * k} and one side of {a * k}. What is its area?', a * b * k * k,
              [a * c * k * k, F(a * b * k * k, 2), (a + b) * 2 * k, b * c * k * k], f'The diagonal makes a right triangle: other side = √({(c * k) ** 2} − {(a * k) ** 2}) = {b * k} '
              f'({a}-{b}-{c} triple). Area = {a * k} × {b * k} = {a * b * k * k}.', pos=True)


@gen('circles_polys', 3, 1)
def cp_inscribed(r):
    k = r.randint(1, 8)
    if r.random() < .5:
        return ne(f'A square is drawn inside a circle of radius {k} so that all four corners touch the circle. What is the area of the square?', 2 * k * k,
                  f'The square\'s diagonal is the circle\'s diameter, {2 * k}. Area of a square = diagonal² ÷ 2 = {4 * k * k} ÷ 2 = {2 * k * k}.')
    s = 2 * k
    return mct(r, f'A circle is drawn inside a square of side {s} so that it touches all four sides. What is the area of the circle?', pi(k * k),
               [pi(v) for v in (s * s, 2 * k * k, s, k, 3 * k * k, 8 * k * k, (k + 1) ** 2)], f'The circle\'s diameter equals the side, {s}, so r = {k} and area = {pi(k * k)}.')


# ====================================================================== 22. Coordinate geometry
@gen('coordinate', 1, 0)
def co_slope(r):
    while True:
        x1, y1, x2, y2 = (r.randint(-8, 9) for _ in range(4))
        if x1 != x2 and y1 != y2:
            break
    m = F(y2 - y1, x2 - x1)
    return mc(f'What is the slope of the line through ({num(x1)}, {num(y1)}) and ({num(x2)}, {num(y2)})?', m, [1 / m, -m, -1 / m, m + 1],
              f'Slope = (y₂ − y₁)/(x₂ − x₁) = ({num(y2)} − {pn(y1)})/({num(x2)} − {pn(x1)}) = {num(y2 - y1)}/{num(x2 - x1)}' + ('' if F(y2 - y1, 1) / (x2 - x1) == m and abs(x2 - x1) == m.denominator and (y2 - y1) == m.numerator else f' = {num(m)}') + '. Rise over run - y on top.')


@gen('coordinate', 1, 1)
def co_dist(r):
    a, b, c = r.choice(TRIPLES[:3])
    k = r.randint(1, 2)
    x1, y1 = r.randint(-6, 6), r.randint(-6, 6)
    dx, dy = a * k * r.choice([1, -1]), b * k * r.choice([1, -1])
    return ne(f'What is the distance between ({num(x1)}, {num(y1)}) and ({num(x1 + dx)}, {num(y1 + dy)})?', c * k,
              f'Horizontal gap {abs(dx)}, vertical gap {abs(dy)}. Distance = √({abs(dx)}² + {abs(dy)}²) = √{(c * k) ** 2} = {c * k}. It is just Pythagoras.')


@gen('coordinate', 1, 1)
def co_mid(r):
    x1, y1, x2, y2 = (r.randint(-9, 9) * 1 for _ in range(4))
    if (x1 + x2) % 2:
        x2 += 1
    if (y1 + y2) % 2:
        y2 += 1
    M = ((x1 + x2) // 2, (y1 + y2) // 2)
    pt = lambda a, b: f'({num(a)}, {num(b)})'  # noqa: E731
    return mct(r, f'What is the midpoint of {pt(x1, y1)} and {pt(x2, y2)}?', pt(*M),
               [pt(x2 - x1, y2 - y1), pt((x2 - x1) // 2 if (x2 - x1) % 2 == 0 else x2 - x1, (y2 - y1) // 2 if (y2 - y1) % 2 == 0 else y2 - y1), pt(M[1], M[0]), pt(x1 + x2, y1 + y2), pt(-M[0], M[1]), pt(M[0] + 1, M[1] - 1), pt(M[0] - 2, M[1] + 2), pt(M[0], -M[1] + 1)],
               f'Average the coordinates: x = ({num(x1)} + {pn(x2)})/2 = {num(M[0])} and y = ({num(y1)} + {pn(y2)})/2 = {num(M[1])}, so {pt(*M)}.')


@gen('coordinate', 1, 2)
def co_xint(r):
    m, x0 = r.choice([-5, -4, -3, -2, 1, 2, 3, 4, 5]), _nz(r, -8, 8)
    b = -m * x0
    return mc(f'At what value of x does the line y = {lead(m, "x")}{term(b)} cross the x-axis?', x0, [b, -x0, F(b, 1) if m == 1 else m * b, F(-b, 1) / 2],
              f'On the x-axis, y = 0: {lead(m, "x")}{term(b)} = 0 → x = ' + (f'{num(-b)} ÷ {pn(m)} = ' if m != 1 else '') + f'{num(x0)}. (The y-intercept is {num(b)} - a common mix-up.)')


@gen('coordinate', 2, 2)
def co_perp(r):
    a, b = _nz(r, -6, 6), _nz(r, -6, 6)
    c = r.randint(-10, 10)
    m = F(-a, b)
    return mc(f'What is the slope of a line perpendicular to the line {lead(a, "x")}{term(b, "y")} = {num(c)}?', -1 / m, [m, 1 / m, -m, F(a, 1)],
              f'Rewrite as y = mx + b: y = ({num(m)})x + …, so the slope is {num(m)}. A perpendicular slope is the negative reciprocal: {num(-1 / m)}.')


@gen('coordinate', 2, 0)
def co_line(r):
    m, b = _nz(r, -4, 4), r.randint(-9, 9)
    x1, x2 = r.sample(range(-5, 6), 2)
    return ne(f'A line passes through ({num(x1)}, {num(m * x1 + b)}) and ({num(x2)}, {num(m * x2 + b)}). What is its y-intercept?', b,
              f'Slope = {num(m * (x2 - x1))}/{num(x2 - x1)} = {num(m)}. Use y = mx + b with ({num(x1)}, {num(m * x1 + b)}): {num(m * x1 + b)} = {num(m)}({num(x1)}) + b → b = {num(b)}.')


@gen('coordinate', 2, 1)
def co_reflect(r):
    x, y = _nz(r, -9, 9), _nz(r, -9, 9)
    while abs(x) == abs(y):
        y = _nz(r, -9, 9)
    pt = lambda a, b: f'({num(a)}, {num(b)})'  # noqa: E731
    kind = r.randint(0, 3)
    name, res, rule = [('the x-axis', (x, -y), '(x, y) → (x, −y)'), ('the y-axis', (-x, y), '(x, y) → (−x, y)'),
                       ('the line y = x', (y, x), '(x, y) → (y, x)'), ('the origin', (-x, -y), '(x, y) → (−x, −y)')][kind]
    allp = {pt(x, -y), pt(-x, y), pt(y, x), pt(-x, -y), pt(-y, -x)}
    return mct(r, f'The point {pt(x, y)} is reflected over {name}. What are the coordinates of the image?', pt(*res), sorted(allp - {pt(*res)}),
               f'Reflection over {name}: {rule}. So {pt(x, y)} → {pt(*res)}.')


# ====================================================================== lessons
def ex(q, steps, a):
    return dict(q=q, steps=steps, a=a)


LESSONS = {
    'arithmetic': [
        dict(t='Order of operations', teach=['Work in this order: Brackets → Exponents → × and ÷ (left to right) → + and − (left to right).',
                                              '× and ÷ have equal rank: do whichever comes first reading left to right. Same for + and −.'],
             ex=ex('Evaluate 20 − 2 × (1 − 4)² ÷ 6.', ['Brackets: 1 − 4 = −3.', 'Exponent: (−3)² = 9.', '× and ÷ left to right: 2 × 9 = 18, then 18 ÷ 6 = 3.', 'Subtract: 20 − 3 = 17.'], '17'),
             hint='Do the bracket and the square first, then × and ÷ from left to right, then subtract.'),
        dict(t='Signs and powers of negatives', teach=['neg × neg = pos; neg × pos = neg.', 'An even power of a negative is positive; an odd power stays negative.',
                                                       '−3² means −(3²) = −9, but (−3)² = 9. Brackets matter.'],
             ex=ex('If x < 0 < y, is xy² positive or negative?', ['y² is positive (any non-zero number squared).', 'x is negative.', 'negative × positive = negative.'], 'Negative'),
             hint='Decide the sign of each piece first; count the negatives.'),
        dict(t='Decimals and place value', teach=['Multiply decimals as whole numbers, then count the total decimal places.',
                                                  'Dividing by 0.05 = multiplying by 20; dividing by 0.25 = multiplying by 4. Turn decimal divisors into fractions.'],
             ex=ex('0.6 × 0.5 ÷ 0.02 = ?', ['0.6 × 0.5 = 0.30 (6 × 5 = 30, two decimal places).', '0.02 = 1/50, so ÷ 0.02 = × 50.', '0.3 × 50 = 15.'], '15'),
             hint='Count decimal places, and turn ÷ 0.0x into × a whole number.'),
        dict(t='Number sense: between 0 and 1, and estimation', teach=['For 0 < x < 1: x³ < x² < x < √x < 1 < 1/x.',
                                                                       'Estimate before calculating: if the answer choices are far apart, round hard and pick the closest.'],
             ex=ex('If 0 < x < 1, which is larger: x² or √x?', ['Try x = 1/4.', 'x² = 1/16 and √x = 1/2.', 'So √x is larger for every x between 0 and 1.'], '√x'),
             hint='Plug in a simple fraction like 1/4 or 1/2 and compare.'),
    ],
    'fractions': [
        dict(t='Operations with fractions', teach=['Add/subtract: common denominator first. Multiply: tops × tops, bottoms × bottoms.',
                                                   'Divide: multiply by the reciprocal (flip the second fraction).'],
             ex=ex('(1/2 + 1/3) ÷ 5/6 = ?', ['1/2 + 1/3 = 3/6 + 2/6 = 5/6.', '÷ 5/6 = × 6/5.', '5/6 × 6/5 = 1.'], '1'),
             hint='Common denominator inside the bracket, then flip and multiply.'),
        dict(t='Comparing fractions', teach=['Cross-multiply: a/b > c/d exactly when ad > bc (b, d positive).',
                                             'Benchmarks help: is it more or less than 1/2? Than 2/3?',
                                             'Adding the same positive number to top and bottom pulls a fraction towards 1.'],
             ex=ex('Which is bigger, 5/8 or 7/11?', ['Cross-multiply: 5 × 11 = 55 and 7 × 8 = 56.', '56 is bigger, so 7/11 is bigger.'], '7/11'),
             hint='Cross-multiply the two fractions you are unsure about.'),
        dict(t='Fraction word problems (fraction of the remainder)', teach=['"Of" means multiply.', '"x of the remainder" - work out what is left first, then take the fraction of that.',
                                                                            'Turn the final remaining fraction into an equation: (fraction) × whole = amount.'],
             ex=ex('Half of a cake is eaten, then 1/3 of what is left. What fraction remains?', ['After half: 1/2 left.', '1/3 of that is eaten → 2/3 of it stays.', '1/2 × 2/3 = 1/3.'], '1/3'),
             hint='Multiply the "left over" fractions step by step.'),
        dict(t='Fractions ↔ decimals', teach=['Memorise: 1/8 = 0.125, 3/8 = 0.375, 1/20 = 0.05, 1/25 = 0.04, 1/6 ≈ 0.167, 1/7 ≈ 0.143, 1/9 = 0.111…',
                                              'A fraction (in lowest terms) is a terminating decimal only if the denominator has no primes other than 2 and 5.'],
             ex=ex('Write 3/8 + 1/20 as a decimal.', ['3/8 = 0.375.', '1/20 = 0.05.', 'Sum = 0.425.'], '0.425'),
             hint='Convert each fraction separately, then add.'),
    ],
    'integers': [
        dict(t='Primes and prime factorisation', teach=['A prime has exactly two factors: 1 and itself. 2 is the only even prime; 1 is not prime.',
                                                        'Primes under 50: 2, 3, 5, 7, 11, 13, 17, 19, 23, 29, 31, 37, 41, 43, 47.',
                                                        'Factor tree: keep splitting until every branch is prime.'],
             ex=ex('Prime-factorise 360.', ['360 = 36 × 10.', '36 = 2² × 3², 10 = 2 × 5.', '360 = 2³ × 3² × 5.'], '2³ × 3² × 5'),
             hint='Split into any two factors, then keep splitting until all are prime.'),
        dict(t='Counting divisors', teach=['If n = pᵃ × qᵇ × rᶜ, the number of positive divisors is (a + 1)(b + 1)(c + 1).'],
             ex=ex('How many positive divisors does 360 have?', ['360 = 2³ × 3² × 5¹.', '(3 + 1)(2 + 1)(1 + 1) = 4 × 3 × 2.', '= 24.'], '24'),
             hint='Prime-factorise, add 1 to each exponent, multiply.'),
        dict(t='GCF and LCM', teach=['GCF: smallest power of each prime the numbers share.', 'LCM: largest power of every prime that appears.',
                                     'For two numbers: GCF × LCM = their product.'],
             ex=ex('GCF and LCM of 24 and 90?', ['24 = 2³ × 3; 90 = 2 × 3² × 5.', 'GCF = 2 × 3 = 6.', 'LCM = 2³ × 3² × 5 = 360.', 'Check: 6 × 360 = 2,160 = 24 × 90.'], 'GCF 6, LCM 360'),
             hint='Write both as prime powers, then take the smallest (GCF) or largest (LCM) powers.'),
        dict(t='Divisibility and "must divide"', teach=['If n is divisible by a and b, it is divisible by LCM(a, b) - and by every divisor of that LCM.',
                                                        'To test "must", try the smallest possible n.'],
             ex=ex('n is divisible by 6 and 8. Must n be divisible by 48?', ['LCM(6, 8) = 24.', 'n = 24 works and 24 is not divisible by 48.', 'So no - but n must be divisible by 12, 8, 6, 4, 3, 2.'], 'No'),
             hint='Find the LCM and check which choices divide it.'),
    ],
    'odd_even': [
        dict(t='Odd and even rules', teach=['odd ± odd = even; even ± even = even; odd ± even = odd.', 'A product is even if ANY factor is even; odd only if all are odd.',
                                            'When unsure, test small numbers (1, 2, 3).'],
             ex=ex('a is odd, b is even. Is a² + ab odd or even?', ['a² = odd × odd = odd.', 'ab = odd × even = even.', 'odd + even = odd.'], 'Odd'),
             hint='Work out the parity of each term, then combine.'),
        dict(t='Remainders', teach=['"n leaves remainder r when divided by d" means n = dq + r, with 0 ≤ r < d.',
                                    'Fastest method: let n = r (the smallest value that works) and compute.',
                                    'Remainders add and multiply: remainder of 3n = remainder of 3r.'],
             ex=ex('n ÷ 7 leaves 4. What is the remainder of 2n ÷ 7?', ['Try n = 4.', '2n = 8.', '8 ÷ 7 leaves 1.'], '1'),
             hint='Replace n by the remainder itself and compute.'),
        dict(t='Consecutive integers', teach=['Sum of an odd number of consecutive integers = count × middle number.',
                                              'The product of k consecutive integers is divisible by k! (e.g. any 3 consecutive → divisible by 6).'],
             ex=ex('Sum of 5 consecutive integers is 85. What is the largest?', ['Middle = 85 ÷ 5 = 17.', 'They are 15, 16, 17, 18, 19.'], '19'),
             hint='Use the middle term: sum ÷ count.'),
    ],
    'exponents': [
        dict(t='Exponent rules', teach=['xᵃ · xᵇ = xᵃ⁺ᵇ; xᵃ ÷ xᵇ = xᵃ⁻ᵇ; (xᵃ)ᵇ = xᵃᵇ.', 'These only work with the SAME base.'],
             ex=ex('(x³ · x⁴)² ÷ x⁵ = xⁿ. Find n.', ['x³ · x⁴ = x⁷.', '(x⁷)² = x¹⁴.', 'x¹⁴ ÷ x⁵ = x⁹.'], 'n = 9'),
             hint='Add for ×, multiply for a power of a power, subtract for ÷.'),
        dict(t='Common base and solving', teach=['Rewrite numbers as powers of the same prime: 4 = 2², 8 = 2³, 9 = 3², 27 = 3³, 125 = 5³.',
                                                 'If bᵃ = bᶜ (same base, b ≠ 0, ±1) then a = c.'],
             ex=ex('Solve 4ˣ = 8³.', ['4ˣ = (2²)ˣ = 2²ˣ.', '8³ = (2³)³ = 2⁹.', '2x = 9 → x = 4.5.'], 'x = 4.5'),
             hint='Write both sides as a power of 2 (or 3, or 5), then set exponents equal.'),
        dict(t='Zero, negative and fraction bases', teach=['x⁰ = 1 (x ≠ 0). x⁻ⁿ = 1/xⁿ - flip, then power.', '(a/b)⁻ⁿ = (b/a)ⁿ. A negative exponent never makes the value negative.'],
             ex=ex('(2/3)⁻² = ?', ['Flip: 3/2.', 'Square: 9/4.'], '9/4'),
             hint='Flip the fraction first, then apply the positive power.'),
        dict(t='Adding powers and units digits', teach=['Adding equal powers is multiplication: 3ⁿ + 3ⁿ + 3ⁿ = 3 × 3ⁿ = 3ⁿ⁺¹.',
                                                        'Factor out the smallest power: 2ⁿ⁺³ − 2ⁿ = 2ⁿ(8 − 1) = 7 · 2ⁿ.',
                                                        'Units digits of powers repeat in cycles of at most 4 (2: 2, 4, 8, 6).'],
             ex=ex('Units digit of 3⁴⁷?', ['Cycle of 3: 3, 9, 7, 1 (length 4).', '47 ÷ 4 leaves remainder 3.', 'Third in the cycle: 7.'], '7'),
             hint='Find the cycle, then use the remainder of the exponent ÷ cycle length.'),
    ],
    'roots': [
        dict(t='Simplifying roots', teach=['√(ab) = √a × √b. Pull out perfect squares: √72 = √(36 × 2) = 6√2.', 'Only like roots add: 2√3 + 5√3 = 7√3, but √2 + √3 ≠ √5.'],
             ex=ex('√45 + √20 = ?', ['√45 = √(9 × 5) = 3√5.', '√20 = √(4 × 5) = 2√5.', 'Sum = 5√5.'], '5√5'),
             hint='Find the biggest perfect square inside each root.'),
        dict(t='Multiplying roots and conjugates', teach=['(√a + √b)(√a − √b) = a − b (difference of squares).',
                                                          'To remove a root from a denominator, multiply top and bottom by the conjugate.'],
             ex=ex('Simplify 1/(√5 − 2).', ['Multiply by (√5 + 2)/(√5 + 2).', 'Bottom: 5 − 4 = 1.', 'Result: √5 + 2.'], '√5 + 2'),
             hint='Use (a + b)(a − b) = a² − b².'),
        dict(t='Fractional exponents', teach=['x^(p/q) = (q-th root of x)ᵖ. The bottom is the root, the top is the power.', 'Take the root first so numbers stay small.'],
             ex=ex('27^(2/3) = ?', ['Cube root of 27 = 3.', '3² = 9.'], '9'),
             hint='Root (denominator) first, then power (numerator).'),
        dict(t='Equations with roots', teach=['Isolate the root, then square both sides.', 'Squaring can create fake solutions - always check each answer in the ORIGINAL equation.',
                                              'A square root (√) is never negative.'],
             ex=ex('Solve √(x + 2) = x.', ['Square: x + 2 = x².', 'x² − x − 2 = 0 → (x − 2)(x + 1) = 0 → x = 2 or −1.', 'Check x = −1: √1 = 1 ≠ −1. Reject.', 'x = 2: √4 = 2 ✓.'], 'x = 2'),
             hint='Square, solve, then test each solution in the original equation.'),
    ],
    'algebra_expr': [
        dict(t='Factoring quadratics', teach=['x² + bx + c = (x + p)(x + q) where p × q = c and p + q = b.', 'Signs: c positive → p, q same sign as b; c negative → opposite signs.'],
             ex=ex('Factor x² − 2x − 15.', ['Need two numbers: product −15, sum −2.', '−5 and +3.', '(x − 5)(x + 3).'], '(x − 5)(x + 3)'),
             hint='List factor pairs of c and find the pair that adds to b.'),
        dict(t='Expanding (FOIL)', teach=['(a + b)(c + d) = ac + ad + bc + bd: First, Outer, Inner, Last.', 'The x-term comes only from Outer + Inner.'],
             ex=ex('Expand (2x − 3)(x + 5).', ['F: 2x².', 'O + I: 10x − 3x = 7x.', 'L: −15.', '2x² + 7x − 15.'], '2x² + 7x − 15'),
             hint='Multiply each term in the first bracket by each in the second.'),
        dict(t='Special products - use them, do not solve', teach=['(a + b)² = a² + 2ab + b²; (a − b)² = a² − 2ab + b²; a² − b² = (a + b)(a − b).',
                                                                  'If a question gives a + b, a − b or ab, it wants one of these identities - do not solve for a and b.'],
             ex=ex('If x + y = 9 and x − y = 4, what is x² − y²?', ['x² − y² = (x + y)(x − y).', '= 9 × 4 = 36.'], '36'),
             hint='Which identity contains exactly the pieces you are given?'),
        dict(t='Simplifying algebraic fractions', teach=['Factor top and bottom completely, then cancel common FACTORS.', 'You can never cancel terms that are added: (x + 3)/3 ≠ x.'],
             ex=ex('Simplify (x² − 4)/(x² + 4x + 4).', ['Top = (x − 2)(x + 2).', 'Bottom = (x + 2)².', 'Cancel (x + 2): (x − 2)/(x + 2).'], '(x − 2)/(x + 2)'),
             hint='Factor both, cancel a bracket that appears in both.'),
    ],
    'equations': [
        dict(t='Linear equations', teach=['Do the same thing to both sides. Collect x-terms on one side, numbers on the other.',
                                          'Clear fractions first by multiplying by the common denominator; cross-multiply when two fractions are equal.'],
             ex=ex('Solve 5x − 7 = 2x + 8.', ['Subtract 2x: 3x − 7 = 8.', 'Add 7: 3x = 15.', 'x = 5.'], 'x = 5'),
             hint='Move x terms to one side and numbers to the other.'),
        dict(t='Systems of two equations', teach=['Elimination: add/subtract the equations to remove a variable. Substitution: solve one for a variable and plug in.',
                                                  'Look at what is asked - adding the equations often gives x + y directly.'],
             ex=ex('3x + 2y = 17 and 2x + 3y = 18. Find x + y.', ['Add: 5x + 5y = 35.', 'x + y = 7.'], '7'),
             hint='Try adding or subtracting the two equations first.'),
        dict(t='Quadratic equations', teach=['Set equal to 0, factor, set each factor = 0.', 'For ax² + bx + c = 0: sum of roots = −b/a, product = c/a.'],
             ex=ex('Solve x² + x − 12 = 0.', ['(x + 4)(x − 3) = 0.', 'x = −4 or x = 3.', 'Check: sum −1 = −b/a ✓, product −12 = c/a ✓.'], 'x = −4 or 3'),
             hint='Factor, then each bracket = 0.'),
        dict(t='No solution / infinitely many', teach=['Two linear equations: same proportions in x and y but a different constant → parallel lines → no solution.',
                                                       'Same proportions AND same constant → the same line → infinitely many solutions.'],
             ex=ex('For what k does 2x + 3y = 5 and kx + 6y = 7 have no solution?', ['y-coefficient doubled (3 → 6).', 'So k must be 4 for parallel lines.', 'Constants: 5 × 2 = 10 ≠ 7, so no solution.'], 'k = 4'),
             hint='Match the ratio of the coefficients; the constants must not match.'),
    ],
    'inequalities': [
        dict(t='Solving inequalities', teach=['Solve like an equation, BUT flip the sign when you multiply or divide by a negative.',
                                              'Never multiply both sides by a variable unless you know its sign.'],
             ex=ex('Solve 7 − 3x > 19.', ['Subtract 7: −3x > 12.', 'Divide by −3 and flip: x < −4.'], 'x < −4'),
             hint='When you divide by a negative, flip the inequality.'),
        dict(t='Absolute value', teach=['|x − a| is the distance from x to a.', '|x − a| < b ⇔ a − b < x < a + b. |x − a| > b ⇔ x < a − b or x > a + b.',
                                        '|expr| = k has two cases: expr = k or expr = −k.'],
             ex=ex('How many integers satisfy |x − 1| ≤ 3?', ['−3 ≤ x − 1 ≤ 3.', '−2 ≤ x ≤ 4.', 'Integers −2 … 4: 7.'], '7'),
             hint='Rewrite as a double inequality centred on a.'),
        dict(t='Ranges and extreme values', teach=['For a + b: min = min a + min b. For a − b: min = min a − max b.',
                                                   'For products and squares, test the END values (corners) - x² is biggest at the end farthest from 0.'],
             ex=ex('−4 ≤ x ≤ 3 and 1 ≤ y ≤ 2. Greatest x² − y?', ['x² is largest at x = −4 → 16.', 'Smallest y = 1.', '16 − 1 = 15.'], '15'),
             hint='List the end values and test the combinations.'),
    ],
    'functions': [
        dict(t='Evaluating functions', teach=['f(x) = … is a rule. f(−2) means put −2 everywhere x appears - in brackets.'],
             ex=ex('f(x) = 2x² − 3x. f(−2)?', ['2(−2)² − 3(−2).', '= 8 + 6.', '= 14.'], '14'),
             hint='Substitute with brackets around negatives.'),
        dict(t='Symbol functions', teach=['Made-up symbols (◊, #, ⊕) are just functions. Read the rule and substitute.', 'Nested: do the inside bracket first.'],
             ex=ex('a # b = a² − b. Find 3 # (2 # 1).', ['2 # 1 = 4 − 1 = 3.', '3 # 3 = 9 − 3 = 6.'], '6'),
             hint='Evaluate the inner bracket first.'),
        dict(t='Composition', teach=['f(g(x)): apply g first, then f. Work from the inside out.'],
             ex=ex('f(x) = x + 4, g(x) = x². f(g(3))?', ['g(3) = 9.', 'f(9) = 13.'], '13'),
             hint='Inside function first.'),
        dict(t='Working backwards', teach=['If f(t) = value, set the rule equal to the value and solve for t.', 'Linear functions change by the same amount for each step in x.'],
             ex=ex('f(x) = 4x − 3 and f(t) = 21. Find t.', ['4t − 3 = 21.', '4t = 24.', 't = 6.'], '6'),
             hint='Write the rule = the value, and solve.'),
    ],
    'percents': [
        dict(t='Percent basics', teach=['p% of N = (p/100) × N. "X is p% of N" → X = (p/100)N.', 'Pick 100 as the starting value when no number is given.'],
             ex=ex('18 is 45% of what?', ['0.45 × N = 18.', 'N = 18 ÷ 0.45 = 40.'], '40'),
             hint='Write it as an equation: decimal × N = value.'),
        dict(t='Percent change and multipliers', teach=['Percent change = (new − old)/old × 100.', 'Multipliers: +15% → × 1.15; −15% → × 0.85. Successive changes MULTIPLY.'],
             ex=ex('A price goes up 10% then up 20%. Overall?', ['1.1 × 1.2 = 1.32.', '32% increase (not 30%).'], '32% increase'),
             hint='Turn each change into a multiplier and multiply.'),
        dict(t='Reverse percents', teach=['If after a p% discount the price is X, then original × (1 − p/100) = X, so divide.', 'Never add the percent back onto the new value.'],
             ex=ex('After a 20% cut, a salary is 48,000. Original?', ['0.8 × S = 48,000.', 'S = 60,000.'], '60,000'),
             hint='New value = multiplier × original. Divide by the multiplier.'),
        dict(t='"Greater than" vs "less than"', teach=['"A is p% more than B" uses B as the base. "B is ?% less than A" uses A as the base - a different answer.'],
             ex=ex('A is 25% more than B. B is what % less than A?', ['B = 100, A = 125.', 'Difference 25, as a percent of A: 25/125 = 20%.'], '20%'),
             hint='Use B = 100 and divide the difference by the new base.'),
    ],
    'ratios': [
        dict(t='Ratios as parts', teach=['a : b means a parts and b parts - a + b parts in total.', 'Find one part (total ÷ number of parts), then multiply.'],
             ex=ex('Split 72 in the ratio 5 : 3.', ['8 parts → 1 part = 9.', '45 and 27.'], '45 and 27'),
             hint='Total ÷ total parts gives one part.'),
        dict(t='Combining ratios', teach=['To join a : b and b : c, make the shared term (b) the same number in both - use the LCM.'],
             ex=ex('a : b = 2 : 3 and b : c = 4 : 5. a : c?', ['Make b = 12: a : b = 8 : 12 and b : c = 12 : 15.', 'a : c = 8 : 15.'], '8 : 15'),
             hint='Scale both ratios so the middle term matches.'),
        dict(t='Ratios that change', teach=['Write the quantities as ak and bk, apply the change, and set up the new ratio as an equation.',
                                            'Anchor on the quantity that does NOT change.'],
             ex=ex('Boys : girls = 3 : 4. After 5 boys join it is 1 : 1. Girls?', ['3k + 5 = 4k.', 'k = 5.', 'Girls = 4k = 20.'], '20'),
             hint='Use 3k and 4k, then write the new ratio as an equation.'),
    ],
    'word_motion': [
        dict(t='Distance = rate × time', teach=['d = r × t. Keep units consistent - convert minutes to hours (÷ 60).', 'Translate words into equations sentence by sentence.'],
             ex=ex('24 km in 40 minutes - speed in km/h?', ['40 min = 2/3 h.', '24 ÷ 2/3 = 36 km/h.'], '36 km/h'),
             hint='Convert minutes to hours first.'),
        dict(t='Average speed', teach=['Average speed = TOTAL distance ÷ TOTAL time. Never the average of the speeds.'],
             ex=ex('60 km at 30 km/h, then 60 km at 60 km/h. Average?', ['Times: 2 h + 1 h = 3 h.', '120 ÷ 3 = 40 km/h.'], '40 km/h'),
             hint='Find each leg\'s time, add, then total distance ÷ total time.'),
        dict(t='Relative speed', teach=['Towards each other (or apart): ADD speeds. Same direction (catching up): SUBTRACT speeds.'],
             ex=ex('Two cars 210 km apart drive towards each other at 50 and 55 km/h. Meet after?', ['Closing speed 105 km/h.', '210 ÷ 105 = 2 h.'], '2 hours'),
             hint='Combine the speeds, then time = gap ÷ combined speed.'),
        dict(t='Age problems', teach=['Use a table: rows = people, columns = now / in n years / n years ago.', 'Everyone ages by the same amount.'],
             ex=ex('A is 4 times B. In 6 years A will be twice B. A now?', ['A = 4b.', '4b + 6 = 2(b + 6) → 2b = 6 → b = 3.', 'A = 12.'], '12'),
             hint='Write both people\'s ages with one variable, then use the future condition.'),
    ],
    'work_mix_sets': [
        dict(t='Work rates', teach=['Rate = 1/time (jobs per hour). Rates of people working together ADD.', 'Together time = ab/(a + b) for two workers.'],
             ex=ex('A: 4 h alone, B: 12 h alone. Together?', ['1/4 + 1/12 = 4/12 = 1/3 per hour.', 'Time = 3 h.'], '3 hours'),
             hint='Add the rates 1/a + 1/b, then flip.'),
        dict(t='Mixtures', teach=['Track the amount of the pure substance (salt, acid), not the percents.', 'Adding water changes the total but not the amount of substance.'],
             ex=ex('20 L of 30% + 30 L of 10%. Concentration?', ['Salt: 6 + 3 = 9 L.', 'Total 50 L.', '9/50 = 18%.'], '18%'),
             hint='Compute litres of the substance in each part, add, divide by the total.'),
        dict(t='Overlapping sets', teach=['Total = A + B − Both + Neither.', 'For two yes/no attributes (e.g. gender × major) draw a 2 × 2 table with totals.'],
             ex=ex('50 people: 30 like tea, 25 coffee, 10 both. Neither?', ['Either = 30 + 25 − 10 = 45.', 'Neither = 50 − 45 = 5.'], '5'),
             hint='Total = A + B − Both + Neither.'),
    ],
    'sequences': [
        dict(t='Arithmetic sequences', teach=['aₙ = a₁ + (n − 1)d.', 'Between term i and term j there are (j − i) steps of d.'],
             ex=ex('Term 3 is 11 and term 8 is 31. First term?', ['5 steps add 20 → d = 4.', 'a₁ = 11 − 2 × 4 = 3.'], '3'),
             hint='Find d from two terms, then step back to term 1.'),
        dict(t='Sums and counting terms', teach=['Inclusive count from a to b = b − a + 1.', 'Sum of an evenly spaced list = number of terms × average of first and last.',
                                                 'Count multiples of k in [a, b]: (last − first)/k + 1.'],
             ex=ex('Sum of 10 to 30 inclusive?', ['21 terms.', 'Average (10 + 30)/2 = 20.', 'Sum = 420.'], '420'),
             hint='Count the terms, average the ends, multiply.'),
        dict(t='Geometric and recursive sequences', teach=['Geometric: aₙ = a₁ × rⁿ⁻¹.', 'Recursive rules (aₙ from aₙ₋₁): just list the terms one by one.'],
             ex=ex('a₁ = 2, aₙ = 3aₙ₋₁ − 1. a₄?', ['a₂ = 5.', 'a₃ = 14.', 'a₄ = 41.'], '41'),
             hint='Write out the terms one at a time.'),
    ],
    'stats': [
        dict(t='Mean: think in totals', teach=['Sum = mean × count. Use totals for "add/remove a number" questions.'],
             ex=ex('Mean of 6 numbers is 10; one is removed and the mean of the rest is 9. Removed?', ['Total 60.', 'New total 5 × 9 = 45.', 'Removed 15.'], '15'),
             hint='Convert every average into a total.'),
        dict(t='Median and weighted average', teach=['Median: sort, take the middle (even count → average the two middle values).',
                                                     'Weighted average = (n₁m₁ + n₂m₂)/(n₁ + n₂); it sits closer to the bigger group.'],
             ex=ex('Median of 7, 2, 9, 4, 12, 5?', ['Sort: 2, 4, 5, 7, 9, 12.', 'Middle two: 5 and 7.', 'Median 6.'], '6'),
             hint='Sort first.'),
        dict(t='Standard deviation and the normal curve', teach=['SD measures spread around the mean. Adding a constant: SD unchanged. Multiplying by k: SD × |k|.',
                                                                 'Normal: ~68% within 1 SD, ~95% within 2 SD (so ~16% above +1 SD, ~2.5% below −2 SD).'],
             ex=ex('Mean 50, SD 5, normal. About what % are above 55?', ['55 is +1 SD.', '50% above the mean, 34% between 50 and 55.', '50 − 34 = 16%.'], '16%'),
             hint='Count how many SDs from the mean, then use 34 / 13.5 / 2.5.'),
    ],
    'counting': [
        dict(t='Fundamental counting principle', teach=['Independent choices in sequence: MULTIPLY the number of options at each step.'],
             ex=ex('3 shirts, 4 trousers, 2 shoes. Outfits?', ['3 × 4 × 2 = 24.'], '24'),
             hint='Multiply the options at each stage.'),
        dict(t='Permutations (order matters)', teach=['Arranging n distinct things: n!. Choosing an ordered r from n: n × (n − 1) × … (r factors).',
                                                      'Repeated items: divide by the factorial of each repeat (BOOK: 4!/2!).'],
             ex=ex('How many ways to give gold, silver, bronze to 8 runners?', ['8 × 7 × 6 = 336.'], '336'),
             hint='Ask: does swapping two people give a different outcome? If yes, order matters.'),
        dict(t='Combinations (order does not matter)', teach=['nCr = n! / (r!(n − r)!). Groups, committees, handshakes.',
                                                              'Shortcut: nCr = (n × (n − 1) × … r factors) ÷ r!.'],
             ex=ex('Choose 3 from 7 people.', ['(7 × 6 × 5) ÷ (3 × 2 × 1) = 210 ÷ 6 = 35.'], '35'),
             hint='Ordered count ÷ r!.'),
        dict(t='Restrictions', teach=['"Must be together": glue them into one block, then × internal arrangements.',
                                      '"Not together" / "at least one": total − the opposite.', 'Mixed groups: choose each subgroup separately and multiply.'],
             ex=ex('5 people in a row, A and B together?', ['Block AB + 3 others = 4 units → 4! = 24.', 'A and B swap: × 2 = 48.'], '48'),
             hint='Handle the restriction first (glue, or subtract the opposite).'),
    ],
    'probability': [
        dict(t='Basic probability', teach=['P = favourable outcomes ÷ total outcomes (when equally likely).', 'Two dice: 36 outcomes; list them when unsure.'],
             ex=ex('Two dice: P(sum = 8)?', ['Pairs: (2,6),(3,5),(4,4),(5,3),(6,2) = 5.', '5/36.'], '5/36'),
             hint='Count favourable outcomes out of 36.'),
        dict(t='AND / OR', teach=['Independent AND: multiply. OR: P(A) + P(B) − P(A and B).', 'Mutually exclusive (cannot both happen): just add.'],
             ex=ex('P(A) = 0.5, P(B) = 0.4, independent. P(A or B)?', ['P(A and B) = 0.2.', '0.5 + 0.4 − 0.2 = 0.7.'], '0.7'),
             hint='Subtract the overlap.'),
        dict(t='At least one; without replacement', teach=['"At least one" = 1 − P(none).', 'Without replacement: the second fraction loses one from the top and the bottom.',
                                                           'Probability with combinations = (ways you want) ÷ (all ways).'],
             ex=ex('3 coin tosses: P(at least one head)?', ['P(no heads) = 1/8.', '1 − 1/8 = 7/8.'], '7/8'),
             hint='Find the probability of "none", subtract from 1.'),
    ],
    'di': [
        dict(t='Reading the chart and percent change', teach=['Spend 20 seconds on title, units, scale and legend before any question.',
                                                              'Percent change = change ÷ the EARLIER value.'],
             ex=ex('Sales went 40 → 50. Percent increase?', ['Change 10.', '10 ÷ 40 = 25%.'], '25%'),
             hint='Divide the change by the starting value.'),
        dict(t='Totals, averages and parts of a whole', teach=['Average = total ÷ count. A share = part ÷ total.', 'Pie/percent charts: amount = percent × total.'],
             ex=ex('Budget 500; rent 30%, salaries 45%. Difference?', ['45% − 30% = 15%.', '15% of 500 = 75.'], '75'),
             hint='Subtract the percents first, then take that percent of the total.'),
        dict(t='Estimate', teach=['DI answer choices are usually far apart - round numbers before dividing.', 'Compare percent changes: a small base makes a big percent.'],
             ex=ex('Which is bigger: 18 → 27 or 60 → 80?', ['18 → 27: +9 on 18 = 50%.', '60 → 80: +20 on 60 ≈ 33%.', 'The first is bigger.'], '18 → 27'),
             hint='Compute change/base for each and compare.'),
    ],
    'triangles': [
        dict(t='Angles', teach=['Triangle angles sum to 180°; straight line 180°; around a point 360°.', 'Exterior angle = sum of the two remote interior angles.'],
             ex=ex('Angles in ratio 1 : 2 : 3. Largest?', ['6 parts = 180° → 30° each.', 'Largest = 90°.'], '90°'),
             hint='Total parts = 180°.'),
        dict(t='Right triangles', teach=['a² + b² = c². Know the triples 3-4-5, 5-12-13, 8-15-17, 7-24-25 and their multiples (6-8-10, 9-12-15).'],
             ex=ex('Legs 9 and 12. Hypotenuse?', ['9-12 is 3-4 × 3.', 'Hypotenuse 5 × 3 = 15.'], '15'),
             hint='Look for a multiple of a known triple.'),
        dict(t='Special triangles and area', teach=['45-45-90: x : x : x√2. 30-60-90: x : x√3 : 2x.', 'Area = ½ × base × height. Equilateral: (√3/4)s².'],
             ex=ex('45-45-90 with hypotenuse 10. Leg?', ['x√2 = 10.', 'x = 10/√2 = 5√2.'], '5√2'),
             hint='Match the side you know to its place in the ratio.'),
        dict(t='Side rules and similar triangles', teach=['Third side: strictly between the difference and the sum of the other two.',
                                                          'Similar triangles: sides in ratio k → areas in ratio k².'],
             ex=ex('Sides 4 and 9. Possible integer third sides?', ['5 < c < 13.', '6, 7, …, 12 → 7 values.'], '7'),
             hint='Difference < third side < sum.'),
    ],
    'circles_polys': [
        dict(t='Polygons and rectangles', teach=['Sum of interior angles = (n − 2) × 180°. Regular polygon: each = sum ÷ n.', 'Rectangle diagonal = √(l² + w²).'],
             ex=ex('Each interior angle of a regular hexagon?', ['Sum = 4 × 180 = 720°.', '720 ÷ 6 = 120°.'], '120°'),
             hint='(n − 2) × 180, then divide by n.'),
        dict(t='Circles, arcs and sectors', teach=['C = 2πr, A = πr².', 'Arc = (θ/360) × 2πr. Sector = (θ/360) × πr².',
                                                   'A square inside a circle: its diagonal is the diameter.'],
             ex=ex('Radius 6, central angle 60°. Arc length?', ['60/360 = 1/6.', '1/6 × 12π = 2π.'], '2π'),
             hint='Fraction of the circle × the full circumference (or area).'),
        dict(t='Solids', teach=['Box: V = lwh; space diagonal √(l² + w² + h²).', 'Cylinder: V = πr²h; curved surface 2πrh.'],
             ex=ex('Cylinder r = 3, h = 4. Volume?', ['π × 9 × 4 = 36π.'], '36π'),
             hint='Area of the base × height.'),
    ],
    'coordinate': [
        dict(t='Slope and the equation of a line', teach=['Slope = rise/run = (y₂ − y₁)/(x₂ − x₁).', 'y = mx + b: m is the slope, b the y-intercept.'],
             ex=ex('Line through (1, 2) and (3, 8): equation?', ['Slope = 6/2 = 3.', '2 = 3(1) + b → b = −1.', 'y = 3x − 1.'], 'y = 3x − 1'),
             hint='Find the slope, then plug in one point to get b.'),
        dict(t='Distance, midpoint and reflections', teach=['Distance = √((Δx)² + (Δy)²) - Pythagoras.', 'Midpoint = average the x\'s and average the y\'s.',
                                                            'Reflect over x-axis: (x, −y); y-axis: (−x, y); y = x: (y, x).'],
             ex=ex('Distance from (1, 1) to (7, 9)?', ['Δx = 6, Δy = 8.', '√(36 + 64) = 10.'], '10'),
             hint='Make a right triangle from the gaps in x and y.'),
        dict(t='Intercepts, parallel and perpendicular', teach=['x-intercept: set y = 0. y-intercept: set x = 0.', 'Parallel lines: equal slopes. Perpendicular: slopes are negative reciprocals (product −1).'],
             ex=ex('Slope perpendicular to 2x + 4y = 7?', ['y = −½x + 7/4 → slope −½.', 'Negative reciprocal: 2.'], '2'),
             hint='Rewrite as y = mx + b, then take −1/m.'),
    ],
}

# ====================================================================== chapters & units
UNITS = [
    dict(key='u1', title='Unit 1 · Number properties', chapters=['arithmetic', 'fractions', 'integers', 'odd_even']),
    dict(key='u2', title='Unit 2 · Exponents, roots & expressions', chapters=['exponents', 'roots', 'algebra_expr']),
    dict(key='u3', title='Unit 3 · Equations, inequalities & functions', chapters=['equations', 'inequalities', 'functions']),
    dict(key='u4', title='Unit 4 · Word problems', chapters=['percents', 'ratios', 'word_motion', 'work_mix_sets']),
    dict(key='u5', title='Unit 5 · Data analysis', chapters=['sequences', 'stats', 'counting', 'probability', 'di']),
    dict(key='u6', title='Unit 6 · Geometry', chapters=['triangles', 'circles_polys', 'coordinate']),
]
# schedule from the 100-day plan: the day each chapter is taught, unit-test days, retests and section simulations
CH_DAY = {c: gre_plan.CH_DAY[c] for u in UNITS for c in u['chapters']}
for _u in UNITS:
    _u['day'] = gre_plan.UNIT_DAY[_u['key']]
RETEST_DAYS = gre_plan.retest_days('u')
SECTION_DAYS = gre_plan.SECTION_DAYS['quant']
UNIT_OF = {c: u['key'] for u in UNITS for c in u['chapters']}
UNIT_BY_KEY = {u['key']: u for u in UNITS}
CHAPTERS = [c for u in UNITS for c in u['chapters']]

TEST_SPEC = {'chapter': (10, 15), 'unit': (20, 32), 'section1': (12, 21), 'section2': (15, 26), 'drill': (10, 15)}
DIFF_MIX = {'easy': {1: .5, 2: .4, 3: .1}, 'mixed': {1: .3, 2: .5, 3: .2}, 'hard': {1: .1, 2: .45, 3: .45}}


def title(ch):
    return gre_quiz.TOPIC_NAMES.get(ch, ch)


def _make(ch, fn, diff, concept, r):
    q = fn(r)
    return {**q, 'chapter': ch, 'concept': concept, 'diff': diff, 'gen': fn.__name__, 'ctitle': title(ch), 'cname': LESSONS[ch][concept]['t']}


def try_question(ch, concept, seed=None):
    """One fresh 'your turn' question for a lesson concept."""
    r = random.Random(seed)
    pool = [g for g in GENS[ch] if g[2] == concept] or GENS[ch]
    fn, d, c = r.choice(pool)
    return _make(ch, fn, d, c, r)


EXCLUDED_GENS = set()  # generators / hand-written questions reported as bad (filled by gre.load_exclusions)
EXCLUDED_TEXT = set()


def _pick(r, ch, n, mix, concepts=None, bank=0):
    """n questions from one chapter, covering concepts and following a difficulty mix."""
    ok = [g for g in GENS[ch] if g[0].__name__ not in EXCLUDED_GENS] or GENS[ch]
    gens = [g for g in ok if concepts is None or g[2] in concepts] or ok
    out, seen = [], set()
    # cover every concept once (as far as n allows), then fill by difficulty weights
    order = []
    cs = sorted({g[2] for g in gens})
    if n >= len(cs):  # enough questions to touch every concept once; otherwise let difficulty decide
        for c in cs:
            order.append(r.choice([g for g in gens if g[2] == c]))
        r.shuffle(order)
    while len(order) < n:
        want = r.choices([1, 2, 3], weights=[mix[1], mix[2], mix[3]])[0]
        cands = [g for g in gens if g[1] == want and sum(1 for o in order if o is g) < 2] or gens
        order.append(r.choice(cands))
    for fn, d, c in order:
        for _ in range(8):
            q = _make(ch, fn, d, c, r)
            if q['q'] not in seen:
                break
        seen.add(q['q'])
        out.append(q)
    bank_pool = [b for b in gre_quiz.BANK.get(ch, []) if b['q'] not in EXCLUDED_TEXT]
    if bank and bank_pool:
        for i, b in enumerate(r.sample(bank_pool, min(bank, len(bank_pool)))):
            item = {'kind': 'ma' if isinstance(b['a'], list) else ('qc' if b['c'] == QC_CHOICES else 'mc'), **b,
                    'chapter': ch, 'concept': None, 'diff': 2, 'gen': 'bank', 'ctitle': title(ch), 'cname': 'Mixed practice'}
            mids = [k for k, q in enumerate(out) if q['diff'] == 2] or list(range(len(out)))
            out[mids[i % len(mids)]] = item
    return out


def build_test(kind, key=None, level='mixed', chapters=None, concepts=None, seed=None):
    """kind: chapter (key = chapter), unit (key = unit), section1/section2 (chapters = pool), drill (concepts = [(ch, c), ...])."""
    r = random.Random(seed)
    n, minutes = TEST_SPEC[kind]
    mix = DIFF_MIX.get(level, DIFF_MIX['mixed'])
    if kind == 'chapter':
        qs = _pick(r, key, n, mix, bank=2)
        qs.sort(key=lambda q: (q['diff'], r.random()))  # easy → hard, like a tutor's test
        return dict(kind=kind, key=key, title=f'Chapter test · {title(key)}', minutes=minutes, questions=qs)
    if kind == 'unit':
        chs = UNIT_BY_KEY[key]['chapters']
        per = [n // len(chs) + (1 if i < n % len(chs) else 0) for i in range(len(chs))]
        qs = [q for ch, k in zip(chs, per) for q in _pick(r, ch, k, mix, bank=1 if k >= 5 else 0)]
        r.shuffle(qs)
        return dict(kind=kind, key=key, title=f'{UNIT_BY_KEY[key]["title"]} - combined test', minutes=minutes, questions=qs)
    if kind in ('section1', 'section2'):
        pool = chapters or CHAPTERS
        chosen = [r.choice(pool) for _ in range(n)]
        qs = []
        for ch, k in Counter(chosen).items():
            qs += _pick(r, ch, k, mix)
        r.shuffle(qs)
        label = 'Section 1' if kind == 'section1' else f'Section 2 ({"harder" if level == "hard" else "easier" if level == "easy" else "medium"})'
        return dict(kind=kind, key=level, title=f'Quant {label} - GRE timing', minutes=minutes, questions=qs)
    if kind == 'drill':
        concepts = concepts or [(CHAPTERS[0], 0)]
        qs = []
        for i in range(n):
            ch, c = concepts[i % len(concepts)]
            qs += _pick(r, ch, 1, mix, concepts={c})
        r.shuffle(qs)
        return dict(kind=kind, key='drill', title='Weak-spot drill', minutes=minutes, questions=qs)
    raise ValueError(kind)


def lesson(ch):
    return {'chapter': ch, 'title': title(ch), 'unit': UNIT_OF[ch], 'day': CH_DAY[ch],
            'concepts': [{'i': i, 'title': c['t'], 'teach': c['teach'], 'example': c['ex'], 'hint': c['hint']} for i, c in enumerate(LESSONS[ch])]}


def concept_name(ch, c):
    try:
        return LESSONS[ch][c]['t']
    except (KeyError, IndexError, TypeError):
        return title(ch)
