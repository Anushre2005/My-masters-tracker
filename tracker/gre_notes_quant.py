"""Study notes - Quant. Original, concise, topic-wise reading for each class (written for this app).

Markup (parsed by gre_notes.parse):
  # Heading          ## Sub-heading         plain line = paragraph       - bullet
  ! rule / formula box (one line each)       > tip                        x trap (common mistake)
  EX: question || step || step || => answer  (worked example, steps revealed one by one)
  Q: question => answer                       (quick check, answer hidden until you click)
  | a | b | c |                               (table row; first row = header)
"""

NOTES = {}


def note(key, title, minutes, body):
    NOTES[key] = dict(title=title, minutes=minutes, body=body, subject='quant')


note('math_strategy', 'How to approach GRE maths', 12, """
# What the Quant section really tests
The GRE tests school-level maths (roughly up to Class 10) under time pressure. Most questions are 2-3 short steps; the difficulty comes from traps and from not seeing the quickest route.
- 27 questions in two sections: 12 in 21 minutes, then 15 in 26 minutes - about 1 minute 45 seconds each.
- Four formats: Quantitative Comparison (QC), multiple choice (one answer), multiple answer ("select all"), and numeric entry (type the number).
- An on-screen calculator is available. It is slow - use it for ugly arithmetic only, never as a first move.
# A routine for every question
- Read the whole question and underline what it actually asks (the value of x? of 2x? the percent change?).
- Write down what you know in maths, not words.
- Look at the answer choices before calculating: if they are far apart, estimate.
- Pick the method: algebra, plugging in numbers, backsolving from the choices, or estimation.
- After answering, re-read the question once: did you answer what was asked?
# Quantitative Comparison basics
Each QC question gives Quantity A and Quantity B. The answers are always: (A) A is greater, (B) B is greater, (C) equal, (D) cannot be determined.
! If both quantities are plain numbers (no variables), the answer can never be (D).
! You may add, subtract, multiply or divide BOTH sides by the same positive number to simplify.
x Never multiply or divide both sides by something that could be negative or zero - it can flip the comparison.
> With variables, plug in at least two very different values: try 0, 1, −1, a fraction like 1/2, and a big number like 10. If the answer changes, it is (D).
EX: x > 0. Quantity A: x². Quantity B: x. || Try x = 2: A = 4, B = 2, so A is bigger. || Try x = 1/2: A = 1/4, B = 1/2, so B is bigger. || The relationship changes with x. || => (D) cannot be determined
# Mental maths you should know cold
| Fact | Value |
| Squares 11² to 20² | 121, 144, 169, 196, 225, 256, 289, 324, 361, 400 |
| Powers of 2 | 2, 4, 8, 16, 32, 64, 128, 256, 512, 1024 |
| Cubes 1³ to 6³ | 1, 8, 27, 64, 125, 216 |
| √2, √3 | ≈ 1.41, ≈ 1.73 |
> Multiply by 5 = multiply by 10 then halve. Multiply by 25 = multiply by 100 then divide by 4.
Q: 48 × 25 = ? => 4800 ÷ 4 = 1200
Q: Quantity A: 7/8 of 64. Quantity B: 56. Which is greater? => Equal (C): 64 ÷ 8 × 7 = 56
""")

note('arith', 'Numbers, signs, decimals and order of operations', 15, """
# The number line
Numbers to the right are bigger. Negative numbers with bigger size are smaller: −10 < −2.
! Integers: …, −2, −1, 0, 1, 2, … Zero is an even integer and is neither positive nor negative.
! |x| (absolute value) = distance from 0, so it is never negative: |−7| = 7.
# Signs
! positive × positive = positive; negative × negative = positive; positive × negative = negative.
! An even power of a negative is positive: (−2)⁴ = 16. An odd power stays negative: (−2)³ = −8.
x −3² means −(3²) = −9. Only (−3)² = 9. The bracket matters.
EX: If x < 0 < y, what is the sign of x²y? || x² is positive (any non-zero number squared). || y is positive. || positive × positive = positive. || => positive
# Order of operations (PEMDAS)
Brackets → Exponents → × and ÷ from left to right → + and − from left to right.
x × and ÷ have the SAME rank: do whichever comes first reading left to right. 12 ÷ 3 × 2 = 4 × 2 = 8, not 12 ÷ 6.
EX: 20 − 2 × (1 − 4)² ÷ 6 || Bracket: 1 − 4 = −3. || Exponent: (−3)² = 9. || Left to right: 2 × 9 = 18, then 18 ÷ 6 = 3. || 20 − 3. || => 17
# Decimals and place value
In 4,385.27: 4 thousands, 3 hundreds, 8 tens, 5 units, 2 tenths, 7 hundredths.
! Multiply decimals as whole numbers, then count total decimal places: 0.3 × 0.04 = 12 with 3 places = 0.012.
> Dividing by a decimal: turn the divisor into a fraction. ÷ 0.25 = × 4, ÷ 0.05 = × 20, ÷ 0.125 = × 8.
! Rounding: look at the digit to the right; 5 or more rounds up. 3.146 to the nearest hundredth = 3.15.
# Numbers between 0 and 1
For 0 < x < 1: x³ < x² < x < √x < 1 < 1/x. Squaring makes such numbers SMALLER.
EX: Which is larger when x = 0.25: x² or √x? || x² = 0.0625. || √x = 0.5. || => √x is larger
Q: (−1)¹⁰¹ + (−1)¹⁰⁰ = ? => −1 + 1 = 0
Q: 0.6 × 0.5 ÷ 0.02 = ? => 0.3 × 50 = 15
Q: Is 0 positive, negative, even or odd? => Even; neither positive nor negative
""")

note('fractions', 'Fractions', 15, """
# Fraction basics
A fraction a/b means a parts out of b equal parts. The bottom (denominator) can never be 0.
! Add / subtract: common denominator first. 2/3 + 1/4 = 8/12 + 3/12 = 11/12.
! Multiply: tops × tops, bottoms × bottoms. Cancel first to keep numbers small.
! Divide: multiply by the reciprocal. (3/4) ÷ (9/8) = 3/4 × 8/9 = 2/3.
# Comparing fractions
! Cross-multiply: a/b > c/d when ad > bc (b, d positive).
> Benchmarks are faster: is each fraction above or below 1/2? Close to 1? 7/15 < 1/2 < 8/15.
! Adding the same positive number to top and bottom pulls a fraction towards 1: 2/5 < 3/6 < 4/7.
EX: Which is bigger, 5/8 or 7/11? || Cross-multiply: 5 × 11 = 55 and 7 × 8 = 56. || 56 > 55. || => 7/11
# Mixed numbers and improper fractions
2 3/4 = (2 × 4 + 3)/4 = 11/4. Convert to improper fractions before multiplying or dividing.
# Fraction ↔ decimal ↔ percent
| Fraction | Decimal | Percent |
| 1/2 | 0.5 | 50% |
| 1/3 | 0.333… | 33⅓% |
| 1/4 | 0.25 | 25% |
| 1/5 | 0.2 | 20% |
| 1/6 | 0.1666… | 16⅔% |
| 1/8 | 0.125 | 12.5% |
| 1/9 | 0.111… | 11.1% |
| 1/12 | 0.0833… | 8⅓% |
> A fraction in lowest terms gives a terminating decimal only if its denominator has no prime factors other than 2 and 5 (1/8 terminates, 1/6 does not).
# Complex fractions
Work the top and the bottom separately, then divide.
EX: (1/2 + 1/3) ÷ (1 − 1/6) || Top: 3/6 + 2/6 = 5/6. || Bottom: 5/6. || 5/6 ÷ 5/6. || => 1
x 1/(a + b) is NOT 1/a + 1/b. You can split a fraction over its top, never over its bottom.
Q: 3/4 ÷ 3/8 = ? => 3/4 × 8/3 = 2
Q: Which is greater: 4/9 or 0.45? => 0.45 (4/9 = 0.444…)
Q: Simplify (2/3) / (4/9) => 2/3 × 9/4 = 3/2
""")

note('fraction_wp', 'Fractions in word problems + estimation', 12, """
# "Of" means multiply
"3/5 of 40" = 3/5 × 40 = 24.
# Fraction of the remainder
When a question takes a fraction of what is LEFT, work step by step on the remainder, not on the original.
EX: Ravi spends 1/3 of his salary on rent and 1/4 of the remainder on food. What fraction is left? || After rent: 2/3 left. || Food = 1/4 of 2/3 = 1/6 of the salary. || Left = 2/3 − 1/6 = 1/2. || => 1/2 of the salary
> Shortcut: multiply the "left over" fractions. After rent 2/3 is left; after food 3/4 of that is left: 2/3 × 3/4 = 1/2.
# Turning a fraction into an equation
If "after removing 12 litres the tank goes from 3/5 full to 1/3 full", the 12 litres are the DIFFERENCE of the fractions.
EX: A tank is 3/5 full. After 12 L are used it is 1/3 full. Capacity? || 3/5 − 1/3 = 9/15 − 5/15 = 4/15 of the tank = 12 L. || Capacity = 12 ÷ 4/15 = 12 × 15/4. || => 45 litres
# Pick a smart number
When no actual totals are given, choose a number every denominator divides (the LCM), e.g. 60 for thirds, quarters and fifths.
EX: 1/3 of a class are boys; 3/5 of the boys wear glasses. What fraction of the class are boys with glasses? || Pick 15 students: 5 boys. || 3/5 of 5 = 3 boys with glasses. || 3/15 = 1/5. || => 1/5
# Estimation
x Calculating exactly when the choices are far apart wastes a minute. Round, then pick the closest choice.
EX: Approximately 0.49 × 812 / 3.9 ≈ ? (choices 10, 50, 100, 200, 400) || 0.49 ≈ 1/2, 812 ≈ 800, 3.9 ≈ 4. || 1/2 × 800 / 4 = 100. || => 100
Q: 2/3 of a number is 18. What is 5/6 of it? => The number is 27; 5/6 × 27 = 22.5
Q: A pizza is cut into 8 slices; Ana eats 1/4 of it and Ben eats 1/2 of what is left. How many slices remain? => 8 − 2 = 6, Ben eats 3, so 3 remain
""")

note('divisibility', 'Divisibility, primes, factors, GCF and LCM', 18, """
# Factors and multiples
A factor of n divides n exactly; a multiple of n is n × an integer. Factors of 12: 1, 2, 3, 4, 6, 12.
# Divisibility rules
| Divisible by | Rule |
| 2 | last digit even |
| 3 | digit sum divisible by 3 |
| 4 | last two digits divisible by 4 |
| 5 | last digit 0 or 5 |
| 6 | divisible by 2 and 3 |
| 8 | last three digits divisible by 8 |
| 9 | digit sum divisible by 9 |
# Primes
! A prime has exactly two factors: 1 and itself. 1 is NOT prime. 2 is the only even prime.
! Primes under 50: 2, 3, 5, 7, 11, 13, 17, 19, 23, 29, 31, 37, 41, 43, 47.
# Prime factorisation - the master tool
Break a number into primes with a factor tree: 360 = 2³ × 3² × 5.
! Number of positive factors = multiply (each exponent + 1). 360 → (3+1)(2+1)(1+1) = 24 factors.
EX: How many positive divisors does 72 have? || 72 = 8 × 9 = 2³ × 3². || (3 + 1)(2 + 1) = 12. || => 12
> "Is n divisible by k?" - check that every prime power in k appears in n's factorisation. 2³ × 3 × 7 is divisible by 12 (2² × 3) but not by 9.
# GCF and LCM
! GCF (greatest common factor): shared primes, SMALLEST power of each.
! LCM (least common multiple): every prime that appears, LARGEST power of each.
! GCF × LCM = product of the two numbers.
EX: GCF and LCM of 84 and 126? || 84 = 2² × 3 × 7; 126 = 2 × 3² × 7. || GCF = 2 × 3 × 7 = 42. || LCM = 2² × 3² × 7 = 252. || => GCF 42, LCM 252 (check: 42 × 252 = 84 × 126)
> LCM problems in disguise: "two lights blink every 6 and 10 seconds - when do they blink together again?" = LCM(6, 10) = 30 seconds.
# Trailing zeros
Each trailing zero needs a 10 = 2 × 5. In n!, count the 5s: 25! has 25/5 + 25/25 = 6 trailing zeros.
x A number divisible by both 4 and 6 is not necessarily divisible by 24 - only by LCM(4, 6) = 12.
Q: How many factors does 100 have? => 100 = 2² × 5², so 3 × 3 = 9
Q: LCM of 12, 18 and 30? => 2² × 3² × 5 = 180
Q: Is 1001 prime? => No: 7 × 11 × 13
""")

note('odd_even', 'Odds, evens, remainders and testing cases', 15, """
# Odd and even rules
| Operation | Result |
| even ± even | even |
| odd ± odd | even |
| even ± odd | odd |
| even × anything | even |
| odd × odd | odd |
x There are no simple rules for division: 6 ÷ 2 = 3 is odd, 8 ÷ 2 = 4 is even.
> Fastest method: test with small numbers - 2 for even, 1 or 3 for odd.
EX: a and b are integers and ab is odd. Which must be even: a + b, ab + 2, a²? || ab odd → both a and b are odd. || odd + odd = even. || ab + 2 is odd; a² is odd. || => a + b
# Consecutive integers
! n(n + 1) is always even. The product of any k consecutive integers is divisible by k! (e.g. three in a row → divisible by 6).
! The sum of an odd number of consecutive integers = (number of terms) × (middle term).
# Remainders
"n divided by d leaves remainder r" means n = dq + r, with 0 ≤ r < d.
! List the numbers: remainder 3 when divided by 5 → n = 3, 8, 13, 18, …
! Remainders add and multiply: (remainder of a × remainder of b), then take the remainder again.
EX: n leaves remainder 5 when divided by 7. Remainder of 3n divided by 7? || Use n = 5: 3n = 15. || 15 = 2 × 7 + 1. || => 1
EX: Smallest positive integer leaving remainder 2 when divided by 3, 4 and 5? || n − 2 must be divisible by 3, 4 and 5. || LCM = 60, so n − 2 = 60. || => 62
# Testing cases for "must be true" questions
To prove a choice is NOT always true, find one counter-example. Try 0, 1, −1, a fraction and a large number.
x Forgetting zero and negatives is the most common error in number-property questions.
Q: If n is odd, is n² + n even or odd? => Even (n(n + 1) is always even)
Q: Remainder when 100 is divided by 7? => 2 (98 = 14 × 7)
Q: x is an integer. Must x² − x be even? => Yes: x(x − 1) is a product of consecutive integers
""")

note('np_mixed', 'Number properties: putting it together', 10, """
# How mixed questions hide the topic
The real test never labels a question "remainders" or "primes". Ask: what is the question really about?
- "How many factors / is it divisible" → prime factorisation.
- "Must be odd / even" → odd-even rules, test small numbers.
- "Remainder" → list the numbers n = dq + r.
- "Must be true / could be true" → counter-examples with 0, 1, −1, fractions.
# Strategy for "must be true" with three statements
Check each statement separately. One counter-example kills a statement; it does not decide the others.
EX: x is a positive integer and x² is divisible by 12. Which must be true? I: x divisible by 6. II: x divisible by 12. III: x² divisible by 36. || 12 = 2² × 3, so x² contains 2² and 3; x must contain 2 and 3, i.e. 6 divides x. || x = 6 works (x² = 36), so II is not necessary. || x divisible by 6 → x² divisible by 36. || => I and III only
> In a squared or cubed number, every prime appears an even (or multiple-of-3) number of times. Use that to reverse-engineer x.
Q: n is a positive integer; 2n is a perfect square and 3n is a perfect cube. Smallest n? => n = 2³ × 3² = 72 (2n = 144, 3n = 216)
Q: Must the sum of two primes be even? => No: 2 + 3 = 5
""")

note('exponents', 'Exponents', 15, """
# The rules
! xᵃ × xᵇ = xᵃ⁺ᵇ      xᵃ ÷ xᵇ = xᵃ⁻ᵇ      (xᵃ)ᵇ = xᵃᵇ
! (xy)ᵃ = xᵃyᵃ      x⁰ = 1 (x ≠ 0)      x⁻ⁿ = 1/xⁿ
! x^(1/2) = √x, x^(1/3) = ∛x, x^(a/b) = (ᵇ√x)ᵃ
x xᵃ + xᵇ is NOT xᵃ⁺ᵇ. Adding powers needs factoring: 2⁵ + 2⁵ = 2 × 2⁵ = 2⁶.
# Common bases
Rewrite numbers with the same base before comparing or solving.
EX: Solve 4ˣ = 8. || 4 = 2², 8 = 2³. || 2²ˣ = 2³, so 2x = 3. || => x = 3/2
EX: Which is bigger: 2⁴⁰ or 3²⁵? || Compare 2⁴⁰ = (2⁸)⁵ = 256⁵ and 3²⁵ = (3⁵)⁵ = 243⁵. || 256 > 243. || => 2⁴⁰
# Factoring out powers
EX: Simplify (3¹⁰ + 3⁹) / 3⁸ || Factor 3⁸ out of the top: 3⁸(3² + 3) = 3⁸ × 12. || Divide by 3⁸. || => 12
# Negatives and fractions as bases
! (−2)⁴ = 16 but −2⁴ = −16. (1/2)³ = 1/8 - a fraction gets smaller when raised to a power.
# Units digits
Units digits of powers repeat in cycles of at most 4. Powers of 7: 7, 9, 3, 1, 7, 9, …
EX: Units digit of 7²³? || Cycle 7, 9, 3, 1 has length 4. || 23 = 4 × 5 + 3, so take the 3rd in the cycle. || => 3
Q: (2³)² × 2⁻⁴ = ? => 2⁶⁻⁴ = 4
Q: If 9ˣ = 27, x = ? => 3²ˣ = 3³, x = 3/2
Q: 5ⁿ + 5ⁿ + 5ⁿ + 5ⁿ + 5ⁿ = ? => 5 × 5ⁿ = 5ⁿ⁺¹
""")

note('roots', 'Roots', 15, """
# Square roots
√x means the non-negative root: √25 = 5 (not ±5). But x² = 25 has two solutions: x = 5 or −5.
! √(ab) = √a × √b      √(a/b) = √a / √b
x √(a + b) is NOT √a + √b: √(9 + 16) = 5, but √9 + √16 = 7.
# Simplifying
Pull out the largest perfect square: √72 = √(36 × 2) = 6√2.
! Only like roots add: 3√2 + 5√2 = 8√2, but √2 + √3 cannot be combined.
EX: √50 + √18 − √8 || √50 = 5√2, √18 = 3√2, √8 = 2√2. || 5 + 3 − 2 = 6. || => 6√2
# Rationalising
To remove a root from the bottom, multiply top and bottom by the root (or the conjugate).
! 1/(√a − b) × (√a + b)/(√a + b) = (√a + b)/(a − b²)
EX: Simplify 2/(√3 − 1) || Multiply by (√3 + 1)/(√3 + 1). || Bottom: 3 − 1 = 2. || Top: 2(√3 + 1). || => √3 + 1
# Estimating roots
Find the perfect squares around the number: √50 is a little more than 7 (√49). √2 ≈ 1.41, √3 ≈ 1.73, √5 ≈ 2.24.
# Equations with roots
Square both sides, then CHECK every solution in the original equation - squaring can create fake ones.
EX: Solve √(x + 7) = x − 5 || Square: x + 7 = x² − 10x + 25 → x² − 11x + 18 = 0 → (x − 2)(x − 9) = 0. || x = 2 gives √9 = 3 but 2 − 5 = −3: reject. || x = 9 gives √16 = 4 = 9 − 5: works. || => x = 9
Q: Simplify √(12) × √(3) => √36 = 6
Q: Between which integers is √90? => 9 and 10
Q: (√5 + √3)(√5 − √3) = ? => 5 − 3 = 2
""")

note('algebra_expr', 'Algebraic expressions and factoring', 15, """
# Combining and distributing
Only like terms combine: 3x² + 2x − x² + 4x = 2x² + 6x.
! Distribute: a(b + c) = ab + ac. FOIL: (a + b)(c + d) = ac + ad + bc + bd.
x −(x − 3) = −x + 3. The minus sign hits every term inside.
# The three identities - memorise them
! (a + b)² = a² + 2ab + b²
! (a − b)² = a² − 2ab + b²
! a² − b² = (a + b)(a − b)
> When a question gives x + y and xy, or x − y and x + y, it wants an identity - don't solve for x and y separately.
EX: x + y = 7 and xy = 10. Find x² + y². || (x + y)² = x² + 2xy + y². || 49 = x² + y² + 20. || => x² + y² = 29
EX: 51² − 49² = ? || Difference of squares: (51 + 49)(51 − 49). || 100 × 2. || => 200
# Factoring
1. Take out the GCF first: 6x³ − 9x² = 3x²(2x − 3).
2. Quadratic x² + bx + c: find two numbers that multiply to c and add to b. x² − 5x + 6 = (x − 2)(x − 3).
3. Look for a difference of squares: 4x² − 25 = (2x + 5)(2x − 5).
# Simplifying fractions with variables
Factor the top and bottom, then cancel common FACTORS (never terms).
EX: Simplify (x² − 9)/(x² + x − 6) || Top = (x + 3)(x − 3). Bottom = (x + 3)(x − 2). || Cancel (x + 3). || => (x − 3)/(x − 2)
x You may cancel (x + 3) because it is a factor of both; you may NOT cancel x² from x² − 9 and x² + x − 6.
Q: Expand (2x − 3)² => 4x² − 12x + 9
Q: If x − y = 3 and x + y = 8, x² − y² = ? => 3 × 8 = 24
Q: Factor x² + 7x + 12 => (x + 3)(x + 4)
""")

note('linear', 'Linear equations and systems', 12, """
# Solving one equation
Do the same thing to both sides until the variable is alone. Clear fractions first by multiplying by the common denominator.
EX: x/3 + x/4 = 14 || Multiply everything by 12: 4x + 3x = 168. || 7x = 168. || => x = 24
# Two equations, two unknowns
! Elimination: add or subtract the equations so one variable disappears.
! Substitution: solve one equation for a variable, plug into the other.
EX: 3x + 2y = 16 and x − 2y = 0 || Add them: 4x = 16, x = 4. || 4 − 2y = 0, y = 2. || => x = 4, y = 2
> Look at what is asked. If the question wants x + y, adding or subtracting the equations may give it directly.
EX: 2x + 3y = 17 and 3x + 2y = 18. Find x + y. || Add: 5x + 5y = 35. || => x + y = 7
# How many solutions?
! Same slope, different intercepts → no solution. Equations that are multiples of each other → infinitely many solutions.
EX: For which k do 2x + 3y = 5 and 4x + ky = 7 have no solution? || The left sides must be proportional: k = 6. || Then the right sides 5 and 7 are not in the same ratio, so no solution. || => k = 6
# Word problems → equations
Name the unknown in words ("let p = price of one pen"), translate each sentence, solve, then answer the question asked.
x A very common miss: solving for x correctly and then choosing x when the question asked for 2x or x + 5.
Q: 5 − 2(x − 1) = 3x − 8. x = ? => 5 − 2x + 2 = 3x − 8 → 15 = 5x → x = 3
Q: Pens cost 3 each and notebooks 5 each; 10 items cost 38. How many notebooks? => p + n = 10, 3p + 5n = 38 → 2n = 8 → 4
""")

note('quadratics', 'Quadratics and harder equations', 15, """
# Solving quadratics
Get everything to one side so it equals 0, factor, then set each factor to 0.
EX: x² = 5x + 14 || x² − 5x − 14 = 0. || (x − 7)(x + 2) = 0. || => x = 7 or x = −2
! Sum of roots = −b/a, product of roots = c/a for ax² + bx + c = 0.
x Never divide both sides by x - you lose the solution x = 0. x² = 3x → x² − 3x = 0 → x(x − 3) = 0 → x = 0 or 3.
# Special patterns
! x² = k has two solutions ±√k (if k > 0). (x − 3)² = 16 → x − 3 = ±4 → x = 7 or −1.
! a quadratic that is a perfect square (x² − 6x + 9 = (x − 3)²) has ONE solution.
# Equations with exponents
Rewrite both sides with the same base, then set the exponents equal.
EX: 2ˣ⁺¹ = 8ˣ⁻¹ || 8 = 2³, so 2ˣ⁺¹ = 2³ˣ⁻³. || x + 1 = 3x − 3. || => x = 2
# Absolute-value equations
|expression| = k (k ≥ 0) splits into two cases: expression = k or expression = −k.
EX: |2x − 3| = 7 || 2x − 3 = 7 → x = 5. || 2x − 3 = −7 → x = −2. || => x = 5 or −2
> On QC questions with a quadratic, solve it - there are often two roots, and one may be bigger than the other quantity while the other is smaller, giving (D).
Q: Solve x² − 9x + 20 = 0 => (x − 4)(x − 5) → 4 or 5
Q: The roots of x² + bx + 12 = 0 are 3 and 4. b = ? => sum = 7 = −b, so b = −7
Q: 3²ˣ = 81. x = ? => 3²ˣ = 3⁴ → x = 2
""")

note('inequalities', 'Inequalities and absolute value', 15, """
# Solving inequalities
Like equations, with one extra rule:
! Multiplying or dividing by a NEGATIVE number flips the sign. −2x > 6 → x < −3.
x You cannot multiply both sides by a variable unless you know its sign.
EX: Solve 5 − 3x ≥ 17 || −3x ≥ 12. || Divide by −3 and flip. || => x ≤ −4
# Compound inequalities
Do the same thing to all three parts: −1 < 2x + 3 < 9 → −4 < 2x < 6 → −2 < x < 3.
# Combining ranges
To find the range of a + b, a − b or ab, test the extreme values.
! min(a − b) = min(a) − max(b); max(a − b) = max(a) − min(b).
EX: 2 < a < 5 and −1 < b < 3. Range of a − b? || Largest: 5 − (−1) = 6. || Smallest: 2 − 3 = −1. || => −1 < a − b < 6
x For products ab with negatives involved, test all four corner combinations - the extremes may come from two negatives.
# Absolute value as distance
|x − a| = distance between x and a on the number line.
! |x − a| < b → a − b < x < a + b (inside the band).
! |x − a| > b → x < a − b or x > a + b (outside the band).
EX: How many integers satisfy |x − 4| ≤ 2? || 2 ≤ x ≤ 6. || Integers 2, 3, 4, 5, 6. || => 5
# Squares and inequalities
! x² < 9 means −3 < x < 3. x² > 9 means x < −3 or x > 3.
Q: Solve −4 ≤ 1 − x < 3 => −5 ≤ −x < 2 → −2 < x ≤ 5
Q: |x + 1| < 3. Range of x? => −4 < x < 2
Q: If x² < x, what can x be? => 0 < x < 1
""")

note('functions', 'Functions, symbols and formulas', 12, """
# Function notation
f(x) = 2x² − 3 is a rule. f(4) means replace every x with 4: 2(16) − 3 = 29.
x Substitute with brackets: f(−2) = 2(−2)² − 3 = 5, not 2 × −4 − 3.
! f(a + 1) means replace x with (a + 1): f(a + 1) = 2(a + 1)² − 3.
# Composite functions
f(g(x)): do the inside function first.
EX: f(x) = x + 3 and g(x) = x². Find f(g(2)) and g(f(2)). || g(2) = 4, f(4) = 7. || f(2) = 5, g(5) = 25. || => f(g(2)) = 7, g(f(2)) = 25
# Made-up symbols
The GRE invents operations like a ◊ b = a² − 2b. Treat them exactly like functions - just substitute.
EX: a ◊ b = a² − 2b. Find (3 ◊ 1) ◊ 2. || 3 ◊ 1 = 9 − 2 = 7. || 7 ◊ 2 = 49 − 4 = 45. || => 45
# Formulas: "what happens if…"
When a variable changes by a factor, substitute numbers or use ratios.
EX: V = πr²h. If r doubles and h halves, what happens to V? || New V = π(2r)²(h/2) = π × 4r² × h/2 = 2πr²h. || => V doubles
# Graphs of functions
! y = f(x) + k shifts the graph UP by k; y = f(x − k) shifts it RIGHT by k.
! The x-intercepts of y = f(x) are the solutions of f(x) = 0.
! y = x² is a U-shaped parabola with its lowest point at (0, 0); y = −x² opens downward.
Q: f(x) = 3x − 1. Solve f(x) = 11 => 3x − 1 = 11 → x = 4
Q: If f(x) = x² and f(a) = 9, what can a be? => 3 or −3
Q: A circle's area A = πr². If r grows by 50%, A grows by? => 1.5² = 2.25 → by 125%
""")

note('qc', 'Quantitative comparison strategies', 15, """
# The four answers
(A) Quantity A is greater · (B) Quantity B is greater · (C) equal · (D) cannot be determined.
! (D) is right only when different allowed values give different relationships.
! If no variables (just numbers), the answer is never (D).
# Strategy 1 - Simplify both sides like a balance
Do the same operation to both quantities: subtract the same term, multiply by the same positive number, square both if both are positive.
EX: Quantity A: 3/7 + 1/5. Quantity B: 1/5 + 2/5 − 1/35. || Remove 1/5 from both: compare 3/7 with 2/5 − 1/35 = 14/35 − 1/35 = 13/35. || 3/7 = 15/35 > 13/35. || => (A)
# Strategy 2 - Plug in numbers (for variables)
Use the constraints given, then try very different values: positive and negative, integers and fractions, 0 and 1.
EX: x < 0. Quantity A: x³. Quantity B: x². || Any negative x: x³ is negative, x² is positive. || => (B)
> If your first two tries give the same answer, try an extreme or an unusual value (fraction between 0 and 1, a negative) before choosing (A), (B) or (C).
# Strategy 3 - Look for the hidden twist
x Figures are not drawn to scale unless stated. Imagine stretching or squashing them.
x "x² = 16" means x could be 4 or −4.
x Integers are not the only numbers - if the question does not say integer, try fractions.
# Strategy 4 - Estimate
Often you only need to know which side is bigger, not by how much. 99 × 101 vs 100² → (100 − 1)(100 + 1) = 100² − 1, so B is bigger.
Q: Quantity A: (0.9)¹⁰. Quantity B: 0.9. => (B): raising a number between 0 and 1 to a power makes it smaller
Q: x² = 9. Quantity A: x. Quantity B: 0. => (D): x could be 3 or −3
""")

note('percents', 'Percents', 15, """
# Percent means "out of 100"
! x% of y = (x/100) × y. Note: x% of y = y% of x (8% of 50 = 50% of 8 = 4).
# Multipliers - the fastest tool
! Increase by p% → multiply by (1 + p/100). +20% → × 1.2.
! Decrease by p% → multiply by (1 − p/100). −15% → × 0.85.
! Successive changes multiply: +20% then −20% = 1.2 × 0.8 = 0.96, a 4% LOSS overall.
x +20% followed by −20% is not "no change", and +10% twice is +21%, not +20%.
# Percent change
! Percent change = (new − old) / old × 100.
EX: A price rises from 80 to 100. Percent increase? Then it falls back to 80 - percent decrease? || Increase: 20/80 = 25%. || Decrease: 20/100 = 20%. || => 25% up, 20% down
# Reverse percents
If you know the value AFTER a change, divide by the multiplier.
EX: After a 25% discount a shirt costs 600. Original price? || 600 = 0.75 × original. || 600 ÷ 0.75. || => 800
x Do not take 25% of 600 and add it back (that gives 750).
# "More than / less than" percentages
! A is p% more than B: A = B(1 + p/100). If A is 25% more than B, then B is 20% less than A (1/1.25 = 0.8).
# Simple and compound interest
! Simple interest: I = P × r × t (interest only on the original amount).
! Compound interest: A = P(1 + r)ⁿ (interest on interest). 10% for 2 years → × 1.21.
EX: 5,000 at 10% compounded yearly for 2 years || 5,000 × 1.1 × 1.1. || => 6,050 (simple interest would give 6,000)
> With no numbers given, start with 100.
Q: 30 is what percent of 120? => 25%
Q: A number increased by 10% then decreased by 10%. Net change? => 1.1 × 0.9 = 0.99 → 1% decrease
Q: Sales fell 20% to 640. Original sales? => 640 ÷ 0.8 = 800
""")

note('ratios', 'Ratios and proportions', 12, """
# What a ratio means
A ratio compares parts. Boys : girls = 3 : 5 means for every 3 boys there are 5 girls - 8 parts in total.
! Fraction of the total: boys = 3/8 of the class, girls = 5/8.
EX: A class of 40 has boys : girls = 3 : 5. How many girls? || 8 parts = 40, so 1 part = 5. || Girls = 5 parts. || => 25
# Unknown multiplier
Write the quantities as 3k and 5k. Use the other information to find k.
EX: Ratio 4 : 7; the larger number exceeds the smaller by 18. Numbers? || 7k − 4k = 3k = 18, k = 6. || => 24 and 42
# Changing ratios
EX: Red : blue marbles = 2 : 3. After adding 10 red the ratio is 4 : 3. How many blue? || Red 2k, blue 3k. (2k + 10)/(3k) = 4/3. || 6k + 30 = 12k → k = 5. || => 15 blue
# Combining ratios
Make the shared term equal. a : b = 2 : 3 and b : c = 4 : 5 → make b = 12: a : b : c = 8 : 12 : 15.
# Proportions
! a/b = c/d → ad = bc (cross-multiply). Direct proportion: y = kx. Inverse proportion: xy = k.
EX: 6 workers finish a job in 10 days. How long for 4 workers (same rate)? || Workers × days is constant: 60 worker-days. || 60 ÷ 4. || => 15 days
x Ratios do not tell you actual numbers. "Ratio 2 : 3" does not mean there are 5 items - there could be 50.
Q: a : b = 3 : 4 and b : c = 2 : 5. a : c = ? => b = 4: a : b : c = 3 : 4 : 10 → 3 : 10
Q: A map scale is 1 : 50,000. 4 cm on the map = ? km => 200,000 cm = 2 km
""")

note('word_motion', 'Word problems: setting up, age and motion', 15, """
# Translating words into maths
| Words | Maths |
| is, was, will be | = |
| of | × |
| more than, older than | + |
| less than, fewer than | − |
| per, for each | ÷ |
| what, a number | x |
x "5 less than x" is x − 5, not 5 − x.
# Rate, distance, time
! Distance = rate × time (D = RT). Keep units consistent (minutes vs hours!).
! Average speed = total distance ÷ total time - never the average of the speeds.
EX: A car goes 60 km at 30 km/h and returns at 60 km/h. Average speed? || Time out = 2 h, time back = 1 h. || 120 km in 3 h. || => 40 km/h (not 45)
! Moving towards each other: add speeds. Same direction (catching up): subtract speeds.
EX: Two trains 300 km apart move towards each other at 70 and 80 km/h. When do they meet? || Closing speed = 150 km/h. || 300 ÷ 150. || => 2 hours
# Age problems
Make a table with "now" and "in n years" (or "n years ago") columns - everyone ages by the same amount.
EX: A mother is 3 times as old as her son. In 12 years she will be twice as old. Son's age now? || Now: son s, mother 3s. In 12 years: s + 12 and 3s + 12. || 3s + 12 = 2(s + 12) → s = 12. || => 12 (mother 36)
# Check your answer against the story
Plug your answer back into the words: ages must be positive, people must be whole numbers.
Q: A cyclist rides 45 km in 2 h 30 min. Speed? => 45 ÷ 2.5 = 18 km/h
Q: 7 more than twice a number is 31. The number? => 2x + 7 = 31 → 12
Q: A runner chases another who has a 200 m lead; speeds 6 m/s and 4 m/s. Time to catch up? => 200 ÷ 2 = 100 s
""")

note('work_mix_sets', 'Work, mixtures and overlapping sets', 15, """
# Work problems: think in rates
! If someone finishes a job in t hours, their rate is 1/t of the job per hour. Rates ADD when people work together.
EX: A fills a tank in 6 h and B in 3 h. Together? || 1/6 + 1/3 = 1/6 + 2/6 = 1/2 tank per hour. || => 2 hours
! Together time for two = ab/(a + b).
x Never average the times: 6 h and 3 h together is not 4.5 h.
EX: A pipe fills a tank in 4 h; a drain empties it in 6 h. Both open? || 1/4 − 1/6 = 1/12 per hour. || => 12 hours
# Mixtures: track the pure stuff
EX: 20 L of a 30% salt solution is mixed with 30 L of a 10% solution. Percentage of the mixture? || Salt: 6 L + 3 L = 9 L. || Total 50 L. || => 18%
> The result always lies between the two concentrations, closer to the larger volume.
EX: How much water must be added to 10 L of 40% acid to make it 25%? || Acid = 4 L stays the same. || 4 = 0.25 × new total → total = 16 L. || => 6 L of water
# Overlapping sets
! Two groups: Total = A + B − Both + Neither.
EX: In a class of 40, 25 play cricket, 18 play football and 7 play neither. How many play both? || 40 = 25 + 18 − Both + 7. || Both = 10. || => 10
> With two yes/no attributes (e.g. male/female and glasses/no glasses), draw a 2 × 2 table with totals and fill in what you know.
Q: Two workers take 10 and 15 days alone. Together? => 10 × 15 / 25 = 6 days
Q: 100 students: 60 study French, 50 Spanish, 20 both. How many study neither? => 100 − (60 + 50 − 20) = 10
""")

note('sequences', 'Sequences, consecutive integers, backsolving and VICs', 15, """
# Arithmetic sequences (constant difference d)
! nth term: aₙ = a₁ + (n − 1)d.
! Sum = number of terms × (first + last)/2.
EX: Sum of 3 + 7 + 11 + … + 99? || d = 4: number of terms = (99 − 3)/4 + 1 = 25. || Average of first and last = 51. || => 25 × 51 = 1275
! Count of integers from a to b inclusive = b − a + 1. Multiples of k between two numbers: (last multiple − first multiple)/k + 1.
# Geometric sequences (constant ratio r)
! nth term = a₁ × rⁿ⁻¹. 3, 6, 12, 24, … the 10th term = 3 × 2⁹ = 1536.
# Recursive sequences
"aₙ = 2aₙ₋₁ − 1 and a₁ = 3" - just compute term by term: 3, 5, 9, 17, …
# Backsolving (working from the answers)
When the choices are numbers and the question is a "story", test the choices. Start with the middle one; if it is too big or too small, you know which way to go.
EX: The sum of three consecutive even integers is 78. The largest is? (A) 24 (B) 26 (C) 28 (D) 30 (E) 32 || Try (C) 28: 24 + 26 + 28 = 78. || It works. || => 28
# Variables in the answer choices (VICs)
Pick simple numbers for the variables, find the target value, then test EVERY choice.
EX: A store sells p pens for d dollars. How many pens can be bought for c dollars? || Pick p = 4, d = 2, c = 10: price = 0.5, so 20 pens. || Test cp/d = 10 × 4 / 2 = 20. ✓ || => cp/d
x Avoid picking 0, 1 or numbers that already appear in the question - several choices may match by accident.
Q: How many multiples of 7 are between 50 and 150? => 56 to 147: (147 − 56)/7 + 1 = 14
Q: In 5, 9, 13, …, what is the 40th term? => 5 + 39 × 4 = 161
""")

note('stats1', 'Statistics I: mean, median, mode and weighted averages', 15, """
# The big three
! Mean (average) = sum ÷ count. The most useful form: Sum = mean × count.
! Median = middle value after sorting (average of the two middle values when the count is even).
! Mode = most frequent value. Range = max − min.
EX: The average of 5 numbers is 18. One number is removed and the average becomes 16. Which number was removed? || Sum before = 90. Sum after = 4 × 16 = 64. || 90 − 64. || => 26
# Adding or removing values
- Adding a value above the mean raises the mean; below the mean lowers it.
- The median changes only by moving to the next value - it is resistant to extreme values; the mean is not.
# Weighted averages
! Weighted average = (w₁x₁ + w₂x₂) / (w₁ + w₂). It lies closer to the value with the bigger weight.
EX: 20 students average 70 and 30 students average 80. Overall average? || (20 × 70 + 30 × 80)/50 = (1400 + 2400)/50. || => 76
EX: What score is needed on a 5th test to raise an average of 82 (4 tests) to 85? || Needed total = 5 × 85 = 425. Current total = 328. || => 97
# Evenly spaced sets
! For evenly spaced numbers (like consecutive integers), mean = median = (first + last)/2.
# Reading data summaries
Frequency tables list each value with how many times it occurs. To find the median of a frequency table, add up the counts until you pass the halfway position.
EX: Scores 1 (×3), 2 (×5), 3 (×4), 4 (×8). Median? || 20 values: the median is the average of the 10th and 11th. || Counts reach 3, 8, 12 → the 10th and 11th are both 3. || => 3
Q: Mean of 4, 7, 7, 9, 13? Median? Mode? => Mean 8, median 7, mode 7
Q: Average of x, 2x and 3x is 12. x = ? => 6x/3 = 12 → x = 6
""")

note('stats2', 'Statistics II: spread, percentiles, box plots and distributions', 15, """
# Standard deviation (SD) - measuring spread
SD measures how far values typically are from the mean. You never have to compute it exactly on the GRE - compare it.
! Adding the same number to every value: SD unchanged. Multiplying every value by k: SD multiplied by |k|.
! The set with values farther from its mean has the bigger SD. {9, 10, 11} has a smaller SD than {1, 10, 19}.
x A bigger mean does not mean a bigger SD. {100, 101, 102} has the same SD as {1, 2, 3}.
# Normal distribution
A symmetric bell curve: mean = median = mode.
! About 68% of values lie within 1 SD of the mean, about 95% within 2 SD, about 99.7% within 3 SD.
EX: Heights are normal with mean 170 cm and SD 6 cm. About what percent are taller than 182 cm? || 182 = mean + 2 SD. || 95% are within 2 SD, so 5% are outside - half of that above. || => about 2.5%
# Quartiles, percentiles and box plots
! Q1 (25th percentile), median (50th), Q3 (75th) split sorted data into four equal-count groups. IQR = Q3 − Q1.
! The pth percentile is the value with p% of the data at or below it.
A box plot shows min, Q1, median, Q3, max. A longer whisker or box half means those values are more spread out - NOT that there are more of them.
x Each quarter of a box plot holds the same NUMBER of values, regardless of its length.
# Graphs you must be able to read
- Histogram: bars show how many values fall in each interval.
- Scatterplot: each dot is one item with two values; an upward trend means positive correlation.
- Time plot (line graph): a quantity over time - read the scale and units first.
Q: Each value of a set is multiplied by 3 and then 5 is added. What happens to the SD? => It is multiplied by 3
Q: In a normal distribution with mean 50 and SD 10, about what percent lie between 40 and 60? => About 68%
Q: In a box plot, the box from Q1 to the median is twice as long as from the median to Q3. Which part has more values? => Neither - each holds 25% of the values
""")

note('counting', 'Counting', 15, """
# The counting principle
! If one choice has m options and an independent second choice has n options, together there are m × n outcomes.
EX: A password is 2 letters followed by 3 digits (repetition allowed). How many? || 26 × 26 × 10 × 10 × 10. || => 676,000
# Permutations - order matters
! n distinct objects in a row: n! (5! = 120).
! Choosing and arranging r of n: nPr = n!/(n − r)!
EX: How many ways can gold, silver and bronze go to 8 runners? || 8 × 7 × 6. || => 336
# Combinations - order does not matter
! nCr = n! / (r!(n − r)!)
EX: How many 3-person committees from 8 people? || 8C3 = (8 × 7 × 6)/(3 × 2 × 1). || => 56
> Ask "if I swap two chosen items, is it a different outcome?" Yes → permutation; no → combination.
# Identical items
! Arrangements of letters with repeats: divide by the factorial of each repeat. LEVEL: 5!/(2! × 2!) = 30.
# Restrictions
- "Must sit together": glue them into one block, arrange the blocks, then multiply by arrangements inside the block.
- "Must not sit together": total − (arrangements where they are together).
- "At least one": total − (none).
EX: 5 people in a row; A and B must be together. How many arrangements? || Block AB + 3 others = 4 units: 4! = 24. || Inside the block: 2 ways. || => 48
EX: Committees of 3 from 5 men and 4 women with at least one woman? || All committees: 9C3 = 84. || All-men committees: 5C3 = 10. || => 74
Q: How many ways to choose 2 toppings from 6? => 6C2 = 15
Q: Arrangements of the letters of BOOK? => 4!/2! = 12
""")

note('prob1', 'Probability basics', 15, """
# Probability = favourable / total
! P(event) = (number of favourable outcomes) / (total equally likely outcomes). It is always between 0 and 1.
! P(not A) = 1 − P(A).
EX: A bag has 4 red and 6 blue balls. P(red)? || 4 favourable out of 10. || => 2/5
# "Or" and "and"
! P(A or B) = P(A) + P(B) − P(A and B). If A and B cannot both happen (mutually exclusive), just add.
! P(A and B) = P(A) × P(B) when A and B are independent.
EX: Roll a die: P(even or greater than 4)? || Even: 2, 4, 6. Greater than 4: 5, 6. Both: 6. || 3/6 + 2/6 − 1/6. || => 4/6 = 2/3
# Without replacement (dependent events)
After one item is taken, the second probability uses the new totals.
EX: Two cards from 4 red and 6 blue, without replacement. P(both red)? || 4/10 × 3/9. || => 12/90 = 2/15
# Conditional probability
! P(A given B) = P(A and B) / P(B) - restrict the "total" to the cases where B happened.
EX: 60% of a class passed Maths, 30% passed both Maths and Physics. P(passed Physics given passed Maths)? || 0.30 / 0.60. || => 1/2
x Independent ≠ mutually exclusive. If A and B are mutually exclusive (and possible), they are NOT independent - knowing A happened tells you B did not.
Q: Two fair coins: P(exactly one head)? => HT or TH: 2/4 = 1/2
Q: P(rain) = 0.3. P(no rain on two independent days)? => 0.7 × 0.7 = 0.49
""")

note('prob2', 'Probability: "at least", counting and strategy', 12, """
# "At least one" - use the complement
! P(at least one) = 1 − P(none).
EX: A coin is tossed 4 times. P(at least one head)? || P(no heads) = (1/2)⁴ = 1/16. || 1 − 1/16. || => 15/16
# Probability with combinations
P = (ways to get what you want) / (total ways), both counted with combinations.
EX: 3 people are chosen from 5 men and 3 women. P(exactly 2 women)? || Favourable: 3C2 × 5C1 = 3 × 5 = 15. || Total: 8C3 = 56. || => 15/56
# Exactly k successes in n tries (binomial)
! P(exactly k) = nCk × pᵏ × (1 − p)ⁿ⁻ᵏ.
EX: A die is rolled 3 times. P(exactly two sixes)? || 3C2 × (1/6)² × (5/6). || 3 × 1/36 × 5/6. || => 15/216 = 5/72
# When to just list
If there are fewer than about 15 outcomes, list them - it is faster and safer than a formula.
EX: Two dice. P(sum = 9)? || (3,6), (4,5), (5,4), (6,3). || 4 out of 36. || => 1/9
x In "at least" questions, adding P(1) + P(2) + … is slow and error-prone. Use 1 − P(none).
Q: 3 fair coins: P(at least 2 heads)? => HHT, HTH, THH, HHH: 4/8 = 1/2
Q: Two dice: P(doubles)? => 6/36 = 1/6
""")

note('di1', 'Data interpretation: reading graphs and tables', 15, """
# Read the graph before the question
Spend 20-30 seconds on: title, what each axis means, units (thousands? percent?), the legend, and any notes under the graph.
x Many DI errors come from reading percent as an absolute number, or missing "in thousands".
# Common graph types
- Bar graph: compare amounts. Stacked bars: each segment is one part of the total.
- Line graph: change over time - the slope shows how fast it changes.
- Pie (circle) graph: parts of a whole; a 90° slice = 25%.
- Table: exact values - look for the right row and column carefully.
# The questions you will see
! Percent of total = part / whole × 100.
! Percent change = (new − old) / old × 100.
! Ratio of two categories = one value / the other.
EX: Sales were 240 (2020) and 300 (2021). Percent increase? || (300 − 240)/240 = 60/240. || => 25%
# Estimate
DI answer choices are usually far apart. Round to 1-2 significant figures and compare.
EX: About what percent of 1,987 is 412? (10%, 20%, 30%, 40%) || 412/2000 ≈ 0.206. || => about 20%
> Set up the calculation first, then use the calculator for the ugly arithmetic only.
# Multiple graphs
Questions often combine two graphs, e.g. a pie chart of percentages and a bar of totals: amount = percent × total.
Q: A pie slice is 72°. What percent is it? => 72/360 = 20%
Q: A value goes from 50 to 40. Percent change? => −20%
""")

note('di2', 'Data interpretation II: harder sets', 12, """
# Mixed scales and units
Check whether each graph shows absolute values (number of people) or relative values (percent). You cannot compare a percent from one group with a percent from another unless you know the group sizes.
EX: Company X's profit rose 20% and company Y's rose 10%. Did X gain more money? || Unknown - if Y's profit is much bigger, 10% of it can be more than 20% of X's. || => Cannot tell without the actual profits
# "Approximately" means estimate
Round aggressively: 19.8% of 4,985 ≈ 20% of 5,000 = 1,000.
# Multiple-answer DI questions
Judge each choice separately against the data; any number of them can be right.
# Change over time
- "Greatest increase" (absolute) - look for the biggest jump.
- "Greatest percent increase" - divide each jump by its starting value; small starting values can win.
EX: A: 10 → 15. B: 100 → 120. Which grew more in percent? || A: 5/10 = 50%. B: 20/100 = 20%. || => A, even though B grew more in absolute terms
> If a DI question takes more than 3 minutes, guess, mark it, and move on - the set's other questions may be quicker.
Q: A total of 800 is split 35% / 25% / 40%. How much is the largest part? => 0.4 × 800 = 320
Q: Spending rose from 2.5 to 3.0 million. Percent change? => 0.5/2.5 = 20%
""")

note('triangles', 'Lines, angles and triangles', 18, """
# Lines and angles
! Angles on a straight line add to 180°. Angles around a point add to 360°. Vertical (opposite) angles are equal.
! A line crossing two parallel lines makes equal corresponding and alternate angles; co-interior angles add to 180°.
# Triangle basics
! Angles add to 180°. The exterior angle equals the sum of the two remote interior angles.
! The largest side is opposite the largest angle.
! Third-side rule: any side is less than the sum and more than the difference of the other two.
EX: Two sides of a triangle are 5 and 9. Possible lengths of the third side? || 9 − 5 < x < 9 + 5. || => 4 < x < 14
! Area = ½ × base × height (the height is perpendicular to the base).
# Special triangles
! Isosceles: two equal sides and two equal base angles. Equilateral: all sides equal, all angles 60°, area = (√3/4)s².
# Right triangles
! Pythagoras: a² + b² = c² (c = hypotenuse).
! Triples: 3-4-5, 5-12-13, 8-15-17, 7-24-25 and their multiples (6-8-10, 9-12-15…).
! 45-45-90: sides x : x : x√2. 30-60-90: sides x : x√3 : 2x.
EX: A 30-60-90 triangle has hypotenuse 10. Other sides? || Hypotenuse = 2x = 10, x = 5. || => 5 and 5√3
EX: The diagonal of a square is 8. Its area? || Side = 8/√2 = 4√2. || Area = 32. || => 32 (or: diagonal²/2)
# Similar triangles
Same angles → sides in the same ratio. If sides are in ratio k, areas are in ratio k².
x Figures on the GRE are not drawn to scale unless stated. Do not trust what an angle looks like.
Q: A right triangle has legs 9 and 12. Hypotenuse? => 15 (3-4-5 × 3)
Q: Two similar triangles have sides in ratio 2 : 3. Ratio of areas? => 4 : 9
Q: An isosceles triangle has a 40° vertex angle. Base angles? => 70° each
""")

note('circles_polys', 'Polygons, quadrilaterals and circles', 18, """
# Polygons
! Sum of interior angles of an n-sided polygon = (n − 2) × 180°. Each angle of a regular polygon = that ÷ n.
EX: Each interior angle of a regular hexagon? || (6 − 2) × 180 = 720. || 720 ÷ 6. || => 120°
! Exterior angles of any polygon add to 360°.
# Quadrilaterals
| Shape | Area | Notes |
| Rectangle | length × width | diagonal = √(l² + w²) |
| Square | s² | diagonal = s√2 |
| Parallelogram | base × height | opposite sides and angles equal |
| Trapezoid | ½(a + b) × h | a, b = the parallel sides |
| Rhombus | ½ × d₁ × d₂ | all sides equal; diagonals perpendicular |
x Parallelogram area uses the HEIGHT, not the slanted side.
# Circles
! Circumference = 2πr = πd. Area = πr².
! Arc length = (θ/360) × 2πr. Sector area = (θ/360) × πr².
EX: A sector of a circle with radius 6 has a 60° angle. Arc length and area? || Fraction = 60/360 = 1/6. || Arc = 1/6 × 12π = 2π. Area = 1/6 × 36π = 6π. || => 2π and 6π
! An inscribed angle is half the central angle on the same arc. An angle inscribed in a semicircle is 90°.
! A tangent is perpendicular to the radius at the point of contact.
# Shapes inside shapes
EX: A square is inscribed in a circle of radius 5. Area of the square? || The square's diagonal = diameter = 10. || Area = diagonal²/2. || => 50
EX: Shaded area = circle of radius 4 minus a square of side 4 inside it. || 16π − 16. || => 16π − 16 ≈ 34.3
Q: Sum of interior angles of an octagon? => 6 × 180 = 1080°
Q: Circumference 10π. Area? => r = 5, area = 25π
Q: Trapezoid with parallel sides 6 and 10, height 4. Area? => ½ × 16 × 4 = 32
""")

note('coordinate', 'Coordinate geometry', 15, """
# Points and distance
! Distance between (x₁, y₁) and (x₂, y₂) = √((x₂ − x₁)² + (y₂ − y₁)²) - it is just Pythagoras.
! Midpoint = ((x₁ + x₂)/2, (y₁ + y₂)/2).
EX: Distance from (1, 2) to (7, 10)? || Δx = 6, Δy = 8. || √(36 + 64). || => 10
# Slope and lines
! Slope m = rise/run = (y₂ − y₁)/(x₂ − x₁). Positive slope rises to the right; horizontal lines have slope 0; vertical lines have undefined slope.
! Slope-intercept form: y = mx + b, where b is the y-intercept.
! Parallel lines have equal slopes. Perpendicular slopes multiply to −1 (negative reciprocals).
EX: Line through (2, 3) perpendicular to y = 2x + 1? || Perpendicular slope = −1/2. || 3 = −1/2 × 2 + b → b = 4. || => y = −x/2 + 4
# Intercepts
! x-intercept: set y = 0. y-intercept: set x = 0.
EX: Area of the triangle formed by 3x + 4y = 12 and the axes? || x-intercept 4, y-intercept 3. || ½ × 4 × 3. || => 6
# Reflections and quadrants
! Over the x-axis: (x, y) → (x, −y). Over the y-axis: (−x, y). Over y = x: (y, x).
! Quadrant I (+, +), II (−, +), III (−, −), IV (+, −).
# Graphs of equations
- A point is on a graph exactly when its coordinates satisfy the equation.
- y = x² is a parabola opening upward with vertex (0, 0); y = (x − 2)² + 1 has vertex (2, 1).
- (x − a)² + (y − b)² = r² is a circle with centre (a, b) and radius r.
Q: Slope of the line through (−1, 4) and (3, −4)? => −8/4 = −2
Q: Is (2, 5) on y = 3x − 1? => Yes: 3 × 2 − 1 = 5
Q: Where does y = 2x − 6 cross the x-axis? => (3, 0)
""")

note('solids', '3-D shapes and mixed geometry', 12, """
# Rectangular boxes and cubes
! Volume = l × w × h. Surface area = 2(lw + lh + wh). Space diagonal = √(l² + w² + h²).
! Cube with side s: volume s³, surface area 6s², diagonal s√3.
EX: A box is 3 × 4 × 12. Length of its longest diagonal? || √(9 + 16 + 144) = √169. || => 13
# Cylinders
! Volume = πr²h. Curved surface = 2πrh. Total surface = 2πr² + 2πrh.
EX: A cylinder has radius 3 and volume 72π. Height? || 9π × h = 72π. || => h = 8
> How many small cubes fit in a box: divide volumes only if the dimensions divide evenly - otherwise count along each edge.
# Scaling
! Multiply every length by k: areas × k², volumes × k³.
EX: A cube's side doubles. What happens to its volume? || 2³ = 8. || => 8 times larger
# Mixed geometry strategy
1. Draw the figure and label every length and angle you know.
2. Look for right triangles (and special ones), radii, and parallel lines.
3. Write the formula for what is asked and fill in the gaps.
EX: A circle is inscribed in a square of side 10. Area between them? || Circle radius = 5, area 25π. || Square area 100. || => 100 − 25π
Q: Volume of a cube with surface area 54? => 6s² = 54 → s = 3 → volume 27
Q: A cylinder's radius doubles and its height halves. Volume changes by? => 2² × ½ = 2 → doubles
""")

note('hard_quant', 'Hard quant problems: how to attack them', 10, """
# What makes a question hard
Usually not harder maths - it is one of: a hidden constraint, an extra step, a trap answer, or wording that hides a simple idea.
# A routine for hard questions
- Rewrite the question in your own words. What exactly is being asked?
- List every constraint (integer? positive? distinct? "not drawn to scale"?).
- Try the simplest numbers that obey the constraints.
- Look for structure: a difference of squares, a common base, a ratio, symmetry.
- If you are stuck after 90 seconds, guess intelligently, mark it, move on.
# Traps to expect on hard questions
x Answering a different quantity than asked (x vs 2x, percent vs percentage points).
x Forgetting negative values or fractions in number properties.
x Assuming a figure is drawn to scale.
x In "how many" questions, forgetting the first or last item (inclusive counting).
x In probability, treating dependent events as independent.
# How to study from a hard problem
After solving, write one sentence: "the key was ___". That sentence is what you will remember on test day.
""")

note('quant_pacing', 'Quant section strategy and pacing', 8, """
# The clock
Section 1: 12 questions in 21 minutes. Section 2: 15 questions in 26 minutes. That is about 1 minute 45 seconds per question.
# A pacing plan
- First pass: answer everything you can do in under 2 minutes. Mark anything longer and move on.
- Second pass: go back to marked questions with the time left.
- Final minute: make sure no question is blank - there is no penalty for guessing.
> QC questions are usually the quickest - do not spend 3 minutes on one.
> Data interpretation sets often have one easy question - do it even if the others look long.
# Using the calculator well
Set up the expression on paper first. Use the calculator for multiplication and division of ugly numbers, not for 12 × 5.
""")
