"""100-day GRE study plan (100 study days: 16 weeks of 6 + a 4-day final week) built on the shared GRE Drive folder.

Phases: weeks 1-11 learn every topic (one class per day, a review/test every Saturday), weeks 12-15 revise
under GRE timing with practice tests, weeks 16-17 final tests and taper.

Each day is one "class": class notes (the key ideas), what to watch (Magoosh lesson videos),
what to read (notes / strategy-guide chapters), exercises (Magoosh practice questions with video
solutions + book assignments with answer keys), a quiz in the app, and homework.
A day can also carry tutor-course items (`course=`): the quant/verbal chapter taught that day, unit tests,
unit retests and section simulations. gre_course and gre_verbal read their schedules from here.

Magoosh practice questions are handed out in order per question type, so no question repeats.
Vocab: one new GregMat group (30 words) per weekday until all 37 are done, then review.
"""
import re

try:
    from .gre_resources import FILES, LESSONS, PRACTICE
except ImportError:  # the Drive index is personal and not in the public repo - see gre_resources_example.py
    from .gre_resources_example import FILES, LESSONS, PRACTICE

POWERPREP = 'https://www.ets.org/gre/test-takers/general-test/prepare/powerprep.html'
ETS_WRITING = 'https://www.ets.org/gre/test-takers/general-test/prepare/content/analytical-writing.html'
ETS_REGISTER = 'https://www.ets.org/gre/test-takers/general-test/register.html'
ETS_BOOKS = 'https://www.ets.org/gre/test-takers/general-test/prepare/prep-books-services.html'
ETS_MATH_REVIEW = 'https://www.ets.org/pdfs/gre/gre-math-review.pdf'
ETS_ISSUE = 'https://www.ets.org/gre/test-takers/general-test/prepare/content/analytical-writing/issue.html'
ETS_MINI_QUIZ = 'https://www.ets.org/gre/gre-mini-quiz.html'
MANHATTAN_FREE_TEST = 'https://www.manhattanprep.com/gre/free-gre-practice-test/'

# short codes -> Magoosh practice folders
PTYPES = {'MC': 'Multiple Choice', 'QC': 'Quant Comparsion', 'NE': 'Numeric Entry', 'MA': 'Multiple Answer',
          'DI': 'Data Interpreataion', 'TC': 'TC', 'SE': 'SE', 'RC': 'RC'}
PNAMES = {'MC': 'Multiple choice', 'QC': 'Quantitative comparison', 'NE': 'Numeric entry', 'MA': 'Multiple answer',
          'DI': 'Data interpretation', 'TC': 'Text completion', 'SE': 'Sentence equivalence', 'RC': 'Reading comprehension'}

MAN = 'MANHATTAN GRE/4th edition Strategy guides'
GUIDE = {
    'alg': '[Manhattan_Prep]_GRE_Algebra_Strategy_Guide(superingenious.com).pdf',
    'fdp': '[Manhattan_Prep]_GRE_Fractions,_Decimals,_&_Percen(superingenious.com).pdf',
    'geo': '[Manhattan_Prep]_GRE_Geometry(superingenious.com).pdf',
    'np': '[Manhattan_Prep]_GRE_Number_Properties(superingenious.com).pdf',
    'qcdi': '[Manhattan_Prep]_GRE_Quantitative_Comparisons_&_Da(superingenious.com).pdf',
    'rc': '[Manhattan_Prep]_GRE_Reading_Comprehension_&_Essay(superingenious.com).pdf',
    'tcse': '[Manhattan_Prep]_GRE_Text_Completion_&_Sentence_Eq(superingenious.com).pdf',
    'wp': '[Manhattan_Prep]_GRE_Word_Problems(superingenious.com).pdf',
}
FIVE_LB = '5 lb. Book of GRE Practice Problems - Manhattan Prep 2018-1 (1).pdf'


def file_url(name):
    for path, n, fid in FILES:
        if n == name:
            return f'https://drive.google.com/file/d/{fid}/view'
    return None  # file not in your Drive index - the item is shown without a link


def R(name, note=''):
    """A book / notes reference."""
    return {'name': name, 'note': note, 'url': file_url(name)}


def G(key, note):
    return R(GUIDE[key], note)


def W(name, note, url):
    """A web resource (official ETS pages, free tests) rather than a Drive file."""
    return {'name': name, 'note': note, 'url': url}


# official ETS books - not in the Drive folder; buy them from ETS (or use your own copy)
OG = 'The Official Guide to the GRE General Test (4th ed.)'
OQ = 'Official GRE Quantitative Reasoning Practice Questions, Vol. 1'
OV = 'Official GRE Verbal Reasoning Practice Questions, Vol. 1'


def off(book, note):
    return W(f'{book} - official ETS book', note + ' (your own copy; buy from ETS if you do not have it)', ETS_BOOKS)


def mreview(part):
    return W('ETS Math Review (free official PDF)', f'Read the {part} part and do its exercises - this is the official quant syllabus', ETS_MATH_REVIEW)


def L(folder, a=1, b=None):
    """Magoosh lesson videos a..b (1-based, inclusive) from a lesson folder."""
    return ('lesson', folder, a, b)


def D(section, title, *, learn=(), read=(), drill=None, books=(), quiz=(), notes=(), homework='', mock=None, essay=False, minutes=90, course=None):
    """course = {'ch': [chapters taught], 'units': [unit tests], 'retest': [units retested], 'sections': ['quant' / 'verbal']}"""
    return dict(section=section, title=title, learn=list(learn), read=list(read), drill=drill or {}, books=list(books),
                quiz=list(quiz), notes=list(notes), homework=homework, mock=mock, essay=essay, minutes=minutes, course=course or {})


# ---------------------------------------------------------------- other books in the folder
P1014 = '1,014 Practice Questions for the New GRE, 2nd Edition.pdf'
FLASH = '500 Math GRE Flash Cards.pdf'
GRAIL = 'GRE_VERBAL_GRAIL_.pdf'
RC99 = 'RC99.pdf'
MSTRAT = next((n for _, n, _ in FILES if n.startswith('GRE MathStrategies 2018')), 'GRE MathStrategies 2018 Manhattan Prep.pdf')  # odd character in the Drive name
VSTRAT = 'Manhattan_Prep_GRE_2018_Verbal_Strategies.pdf'
WORKOUT = 'Verbal_Workout_for_the_New_GRE_4nd_Edition.pdf'
CRACK = '[The_Princeton_Review]_Cracking_the_GRE_Premium_Ed(z-lib.org).pdf'
TOUGH = 'GMAT-Maths-Tough-Problems.pdf'
BARRON6 = "[Vince_Kotchian,_David_Freeling]_Barron-'s_6_GRE_Pr(z-lib.org).pdf"
KAPLAN = '1kaplan_test_prep_gre_prep_2019_practice_tests_proven_strateg.pdf'


def q1014(topic):
    return R(P1014, f'Extra drill: 8-10 {topic} questions from the Math section (answers and explanations at the back)')


def flash(topic):
    return R(FLASH, f'Flip through the {topic} cards - 10 minutes, any time of day')


def rc99(a, b):
    return R(RC99, f'Passages {a}-{b} - time yourself (about 2-3 minutes per passage plus questions)')


def tough(topic):
    return R(TOUGH, f'Hard problems: 5 on {topic}')


REVIEW_NOTES = [
    'Redo every question you got wrong this week without looking at the solution, then watch the video solution.',
    'Open the Error log, sort every "Unsorted" mistake (concept / careless / timing / vocab / misread) and write the rule you will use next time.',
    'Revise the week\'s vocab groups in the Vocab trainer until every word is in box 3 or higher.',
]
MOCK_NOTES = ['Take it in one sitting at the time of day you plan to test. No pausing, no phone.',
              'Afterwards, review every question - wrong ones AND ones you guessed right. Log them in the Error log.',
              'Record your scores in the app so the Progress tab can compare them with your predicted scores.']

PLAN = [
    # ================================================================ PHASE 1 - LEARN (weeks 1-11)
    # ---------------------------------------------------------------- WEEK 1 - foundations
    D('Orientation', 'How the GRE works + baseline', learn=[L('Introduction to the GRE')],
      read=[R('GRE Uncovered.pdf', 'Skim the overview chapters on test structure and scoring'),
            R('GRE Quant - Formula Sheet - Target Test Prep.pdf', 'Print or save it - you will use it all course'),
            R(CRACK, 'Princeton\'s "Cracking the GRE": read the opening chapters on test format and general strategy')],
      drill={'MC': 5, 'TC': 3, 'SE': 2}, quiz=['arithmetic', 'tc_basic'],
      notes=['Current GRE (since Sept 2023): about 1 h 58 min. One Issue essay (30 min), Verbal 2 sections (12 Q / 18 min, 15 Q / 23 min), Quant 2 sections (12 Q / 21 min, 15 Q / 26 min).',
             'Scores: Verbal and Quant 130-170 each, Writing 0-6. Section-level adaptive: doing well on section 1 gives a harder section 2.',
             'The Magoosh videos were recorded for the older, longer test - ignore anything about the Argument essay or an unscored section; strategy content is still valid.',
             'There is no penalty for wrong answers: never leave a question blank. Mark and move on, then come back.',
             'This plan has 100 classes: 11 weeks to learn every topic, 4 weeks of timed revision and practice tests, then a short taper before test day.',
             'Target for business-analytics programmes: aim for 165+ Quant and 155+ Verbal (check each programme page).'],
      homework='Note your baseline accuracy from today\'s drill. Set up a notebook (or the Error log) for mistakes.'),
    D('Quant', 'Math strategy, mental math and QC basics', learn=[L('General Math Strategies')],
      read=[R('Magoosh_GRE_Math_Formula_eBook.pdf', 'Read the arithmetic and number-properties pages'),
            R('gre_math_conventions.pdf', 'ETS math conventions - what figures and notation mean on the test'),
            R(MSTRAT, 'Manhattan Math Strategies: read the introduction and the chapter on approaching quant questions'),
            R('Maths Shortcuts.pdf', 'Shortcut tricks for fast mental maths')],
      drill={'QC': 5, 'MC': 5}, quiz=['arithmetic', 'qc'],
      notes=['QC answer (D) is only correct when the relationship can change. If both quantities are just numbers, (D) is impossible.',
             'Plug in numbers for QC: try a positive integer, a negative, zero, a fraction between 0 and 1, and a large number.',
             'You may do the same operation to both quantities (add, subtract, multiply by a positive) - never multiply by something that could be negative.',
             'Estimate first. Many answer choices are far apart; rough maths saves a minute.'],
      homework='Learn the perfect squares to 20² and powers of 2 to 2¹⁰.'),
    D('Verbal', 'How to learn vocab + text completion with clues', learn=[L('Vocabulary'), L('Text completion-No shifts')],
      read=[G('tcse', 'Read the first text-completion chapter (process: find the clue, predict a word, then look at choices)'),
            R(VSTRAT, 'Manhattan Verbal Strategies: the text-completion chapter'), R(WORKOUT, 'Princeton Verbal Workout: the text-completion chapter')],
      drill={'TC': 6}, quiz=['tc_basic'], course={'ch': ['tc_basic']},
      notes=['Never read the choices first. Cover them, find the clue words in the sentence and write your own word for the blank.',
             'Colons, semicolons and dashes usually mean "here is an explanation / restatement" - the blank agrees with what follows.',
             '"Because", "so", "therefore" are cause-and-effect: the blank must be consistent with the result.',
             'Vocab method: 30 new words a day, flashcards each morning, and say each word in your own sentence.'],
      homework='Make flashcards for today\'s vocab group and review them twice before bed.'),
    D('Quant', 'Number line, signs, decimals and order of operations', learn=[L('Arithmetic and Fractions', 1, 9)],
      read=[R('Number_Line_and_Properties.pdf', 'Notes - number line and properties'), G('fdp', 'Decimals chapter')],
      drill={'MC': 6, 'NE': 2}, books=[R('Number_Lines_Q.pdf', 'Assignment'), R('Number_Lines_Answers_.pdf', 'Answer key - check after'), flash('arithmetic / number')],
      quiz=['arithmetic'], course={'ch': ['arithmetic']},
      notes=['PEMDAS: brackets, exponents, then × and ÷ left to right, then + and − left to right.',
             'Negative × negative = positive. An even power of a negative is positive; an odd power stays negative.',
             'Between 0 and 1, squaring makes a number smaller and square-rooting makes it larger.',
             'Numeric entry: no choices to check against - re-read what the question asks (units, rounding) before typing.'],
      homework='Finish the Number Lines assignment and check it against the answer key.'),
    D('Verbal', 'Text completion: shift words', learn=[L('Text completion-sentence shifts')],
      read=[R('Text_Completions.pdf', 'Notes - text completions')], drill={'TC': 8}, books=[R(GRAIL, 'Verbal Grail: do one text-completion practice set')],
      quiz=['tc_shift'], course={'ch': ['tc_shift']},
      notes=['Shift (contrast) words: although, but, yet, however, despite, rather than, far from, belie, while.',
             'Time shifts ("initially… eventually", "once…") also reverse the meaning.',
             'Double negatives cancel: "not without merit" means it has merit.',
             'After finding the shift, predict the opposite of the clue, then match.'],
      homework='Write 5 sentences of your own using shift words and today\'s vocab.'),
    D('Review', 'Week 1 test and review', drill={'MC': 5, 'QC': 4, 'TC': 5, 'SE': 3}, quiz=['arithmetic', 'qc', 'tc_basic', 'tc_shift'],
      notes=REVIEW_NOTES, homework='Rest well - week 2 starts fractions and number properties.'),
    # ---------------------------------------------------------------- WEEK 2
    D('Quant', 'Fractions', learn=[L('Arithmetic and Fractions', 10, 18)],
      read=[R('Fractions_Decimals.pdf', 'Notes - fractions & decimals'), G('fdp', 'Fractions chapter')],
      drill={'MC': 6, 'QC': 4}, books=[q1014('fractions & arithmetic')], quiz=['fractions'], course={'ch': ['fractions']},
      notes=['To compare fractions, cross-multiply or convert to decimals; benchmarks like 1/2 and 2/3 help.',
             'Dividing by a fraction = multiplying by its reciprocal.',
             'Know the conversions: 1/8 = 0.125, 1/6 ≈ 0.167, 1/7 ≈ 0.143, 1/9 = 0.111…, 1/12 ≈ 0.083.',
             '"Fraction of the remainder" questions: work step by step on what is left, not on the original total.']),
    D('Verbal', 'Two-blank text completions', learn=[L('Text Completion-Double Blanks')], drill={'TC': 8},
      books=[R(WORKOUT, 'Verbal Workout: two-blank text-completion drills')], quiz=['tc_double'], course={'ch': ['tc_double']},
      notes=['Start with the blank that has the clearer clue - it is often the second one.',
             'Test the pair in the full sentence; both words must work together.',
             'Sometimes the other blank IS the clue - decide whether the two blanks agree or contrast.']),
    D('Quant', 'Fraction word problems and estimation', read=[G('fdp', 'Fraction word-problem section'), R('Maths Shortcuts.pdf', 'Estimation and quick-division tricks')],
      drill={'MC': 6, 'NE': 2}, books=[R(P1014, 'Mixed arithmetic set - time yourself at 1.5 minutes per question')], quiz=['fractions', 'arithmetic'],
      notes=['Practice day: no new theory. Today is about speed and setting problems up correctly.',
             '"What fraction of the original remains?" - multiply the remaining fractions step by step.',
             'If a question gives no totals, pick a number that every denominator divides (e.g. 60).',
             'Estimate before you calculate and eliminate choices that are clearly too big or too small.'],
      homework='Redo any question you got wrong today without looking at the solution.'),
    D('Verbal', 'Vocabulary in context: second meanings and word roots', read=[R('GRE verbal notes.pdf', 'Skim the vocabulary section'), G('tcse', 'The chapter on vocabulary strategy')],
      drill={'TC': 6, 'SE': 4}, quiz=['tc_basic', 'tc_shift'],
      notes=['The GRE loves second meanings: temper (moderate), qualify (limit), check (restrain), economy (efficiency), sanction (approve OR penalise).',
             'Roots help you guess: bene (good), mal (bad), loqu (speak), chron (time), path (feeling), ambi (both), vor (eat).',
             'Learn words in context: read the sentence, then say what the word does in it, not just its dictionary meaning.',
             'Today, clear every flashcard due in the Vocab trainer before you start the drill.']),
    D('Quant', 'Divisibility, primes, factors, GCF and LCM', learn=[L('Integer Properties', 1, 7)],
      read=[R('Primes_and_Divisibility.pdf', 'Notes'), G('np', 'Divisibility & primes chapter')],
      drill={'MC': 5, 'QC': 3},
      books=[R('lecture_02_primes_divisibility_factors_multiples_lcm_hcf.docx', 'Assignment'),
             R('lecture_02_primes_divisibility_factors_multiples_lcm_hcf_answers.docx', 'Answer key'), flash('number properties')],
      quiz=['integers'], course={'ch': ['integers']},
      notes=['Prime factorise everything ("factor tree"). Number of divisors = product of (exponent + 1).',
             'GCF: smallest power of each common prime. LCM: largest power of every prime that appears.',
             'GCF × LCM = product of the two numbers.',
             'Primes under 50: 2, 3, 5, 7, 11, 13, 17, 19, 23, 29, 31, 37, 41, 43, 47. 1 is not prime; 2 is the only even prime.']),
    D('Review', 'Week 2 test and review', drill={'MC': 5, 'QC': 4, 'TC': 6}, quiz=['fractions', 'integers', 'tc_double', 'tc_shift'], notes=REVIEW_NOTES),
    # ---------------------------------------------------------------- WEEK 3
    D('Verbal', 'Three-blank text completions', learn=[L('Text Completion-triple Blanks')], drill={'TC': 8},
      books=[R(GRAIL, 'Verbal Grail: one more text-completion set (focus on multi-blank)')], quiz=['tc_triple'], course={'ch': ['tc_triple']},
      notes=['Read the whole sentence first and summarise it in your own words.',
             'Solve the easiest blank first, eliminate, then use it as a clue for the rest.',
             'Three-blank answers are all-or-nothing: re-read the full sentence with your three words before moving on.']),
    D('Quant', 'Odds/evens, remainders and testing cases', learn=[L('Integer Properties', 8, 14)],
      read=[R('Notes_Odds_Evens.pdf', 'Notes')], drill={'MC': 5, 'NE': 2},
      books=[R('Odds_Even_Assignment.pdf', 'Assignment'), R('Odds_Even_Answers.pdf', 'Answer key'), q1014('number properties')],
      quiz=['odd_even'], course={'ch': ['odd_even']},
      notes=['Odd ± odd = even, even ± odd = odd; a product is even if any factor is even.',
             'Remainder r when n is divided by d means n = dq + r with 0 ≤ r < d. List a few values: n = r, r + d, r + 2d…',
             'n(n + 1) is always even; the product of k consecutive integers is divisible by k!.',
             '"Must be true" questions: try to break each choice with one counter-example.']),
    D('Verbal', 'Sentence equivalence', learn=[L('Sentence Equivalence')], read=[G('tcse', 'Sentence-equivalence chapter'), R(VSTRAT, 'Verbal Strategies: the sentence-equivalence chapter')],
      drill={'SE': 8}, books=[R(WORKOUT, 'Verbal Workout: sentence-equivalence drills')], quiz=['se'], course={'ch': ['se']},
      notes=['Predict a word for the blank first, then find TWO choices that match it.',
             'Trap: a pair of synonyms that does not fit the sentence. The pair must fit the meaning, not just match each other.',
             'If only one word fits, you mis-read the sentence - look for a second word with the same sentence meaning.']),
    D('Quant', 'Number properties: mixed practice', read=[G('np', 'End-of-chapter problem sets you have not done')],
      drill={'MC': 6, 'QC': 3, 'NE': 2}, books=[R('320-GRE-Math-Problems.pdf', 'Number-property problems - 10 of them, timed')], quiz=['integers', 'odd_even', 'arithmetic'],
      notes=['Practice day: mix divisibility, remainders, odd/even and signs - the real test never tells you which topic a question is from.',
             'For "which must be true" questions, test the edge cases: 0, 1, negatives, fractions.',
             'Time yourself: aim for 1.5 minutes per question and mark anything over 2 minutes.']),
    D('Verbal', 'Text completion + sentence equivalence: timed set', drill={'TC': 6, 'SE': 6}, quiz=['tc_double', 'tc_triple', 'se'],
      notes=['Time yourself: about 1 minute per one-blank TC or SE, 1.5-2 minutes for two/three blanks.',
             'Words you meet in today\'s questions that you do not know go straight into your flashcards.',
             'After the set, sort each miss: did you misread the logic, or not know a word?']),
    D('Review', 'Week 3 test + first unit tests', drill={'MC': 5, 'NE': 2, 'TC': 4, 'SE': 3}, quiz=['odd_even', 'integers', 'tc_triple', 'se'],
      course={'units': ['u1', 'v1']},
      notes=['Take the two unit tests in the Tutor step: Unit 1 (number properties) and Verbal unit 1 (text completion & sentence equivalence).'] + REVIEW_NOTES),
    # ---------------------------------------------------------------- WEEK 4
    D('Quant', 'Exponents', learn=[L('Powers and Roots', 1, 8)],
      read=[R('Exp_Roots.pdf', 'Notes'), R('Notes_Exponents_and_Roots.pdf', 'Notes'), G('np', 'Exponents chapter'),
            R(MSTRAT, 'Math Strategies: the chapter on exponents / number-property strategies')],
      drill={'MC': 6, 'QC': 3}, quiz=['exponents'], course={'ch': ['exponents']},
      notes=['Same base: multiply → add exponents; divide → subtract; power of a power → multiply.',
             'Rewrite in a common base (4 = 2², 8 = 2³, 27 = 3³) before comparing.',
             'x⁰ = 1, x⁻ⁿ = 1/xⁿ. Units digits repeat in cycles of at most 4.',
             'Adding equal powers is multiplication: 3ⁿ + 3ⁿ + 3ⁿ = 3ⁿ⁺¹.']),
    D('Verbal', 'Reading comprehension: method', learn=[L('Reading Comprehension', 1, 7)],
      read=[G('rc', 'RC chapters on reading strategy and short passages'), R('Verbal RC notes.pdf', 'Notes'), R(GRAIL, 'Verbal Grail: the reading-comprehension method section')],
      drill={'RC': 6}, books=[rc99(1, 5)], quiz=['rc'], course={'ch': ['rc']},
      notes=['Read for structure: what is the main point, and what job does each paragraph do?',
             'Primary purpose answers start with a verb (argue, describe, challenge…) - match the verb to the author\'s tone.',
             'Every right answer is supported by the text; wrong answers are too extreme, too narrow or off-topic.',
             'For detail questions, go back and find the line before answering.']),
    D('Quant', 'Roots', learn=[L('Powers and Roots', 9, 16)], drill={'MC': 5, 'NE': 2},
      books=[R('lecture_04_roots_exponents.docx', 'Assignment'), R('lecture_04_roots_exponents_answers.docx', 'Answer key'), q1014('exponents & roots')],
      quiz=['roots'], course={'ch': ['roots']},
      notes=['√(ab) = √a·√b but √(a + b) ≠ √a + √b.',
             'Simplify: pull out perfect squares (√72 = 6√2). Only like roots add.',
             'Rationalise with the conjugate: 1/(√a − b) × (√a + b)/(√a + b).',
             'After squaring an equation, check each solution in the original - squaring can add a fake one.']),
    D('Verbal', 'Reading comprehension: question types', learn=[L('Reading Comprehension', 8, 14)], drill={'RC': 8}, books=[rc99(6, 10)], quiz=['rc'],
      notes=['Inference: the answer must be true based on the passage - a small step, never a big leap.',
             'Select-all (multiple answer) questions: judge each choice on its own; any number can be right.',
             'Select-in-passage: match the sentence\'s function exactly.',
             'Structure / function questions ask WHY a sentence is there (example, contrast, conclusion…).']),
    D('Quant', 'Algebra: expressions and factoring', learn=[L('Algebra, Equations and Inqualities', 1, 10)],
      read=[R('Algebra.pdf', 'Notes'), G('alg', 'Expressions / factoring chapter')], drill={'MC': 6, 'QC': 3}, books=[flash('algebra')],
      quiz=['algebra_expr'], course={'ch': ['algebra_expr']},
      notes=['Memorise: (a + b)² = a² + 2ab + b², (a − b)² = a² − 2ab + b², a² − b² = (a + b)(a − b).',
             'When a question gives x + y and xy, it usually wants you to use one of these identities - do not solve for x and y.',
             'Factor out the GCF first, then look for a pattern.']),
    D('Review', 'Week 4 test and review', drill={'MC': 5, 'NE': 2, 'RC': 4}, quiz=['exponents', 'roots', 'algebra_expr', 'rc'], notes=REVIEW_NOTES),
    # ---------------------------------------------------------------- WEEK 5
    D('Quant', 'Linear equations and systems', learn=[L('Algebra, Equations and Inqualities', 11, 18)], drill={'MC': 6, 'NE': 2, 'MA': 2},
      books=[q1014('algebra')], quiz=['equations'], course={'ch': ['equations']},
      notes=['Clear fractions first by multiplying by the common denominator.',
             'Two equations, two unknowns: add/subtract to eliminate, or substitute. Look for what the question actually asks (x + y may be quicker than x and y).',
             'Parallel lines (same slope, different intercept) → no solution; identical equations → infinitely many.']),
    D('Verbal', 'Long reading passages', read=[R('Optional_Reading_Comprehensions.pdf', 'Practice passages'), G('rc', 'Long-passage chapter')],
      drill={'RC': 8}, books=[rc99(11, 20)], quiz=['rc'],
      notes=['On long passages, write a 3-word summary of each paragraph as you read.',
             'Note the author\'s attitude words (however, unfortunately, compelling) - tone questions depend on them.',
             'Do not reread the whole passage for every question; use your paragraph map to jump to the right place.']),
    D('Quant', 'Quadratics and harder equations', read=[G('alg', 'Quadratic equations chapter')], drill={'MC': 6, 'QC': 3, 'NE': 1}, quiz=['equations', 'algebra_expr'],
      notes=['Quadratics: set = 0 and factor. Sum of roots = −b/a, product = c/a.',
             'Never divide both sides by a variable - you may lose the solution x = 0. Factor it out instead.',
             'Equations with exponents: rewrite both sides with the same base, then set the exponents equal.',
             'Equations with roots or absolute values: solve, then check every answer in the original equation.']),
    D('Verbal', 'Critical reasoning: arguments, weaken and strengthen', learn=[L('Paragraph Elements', 1, 5)],
      read=[R('n01_basics_of_cr1.pdf', 'Notes'), R('n05_weaken_questions1.pdf', 'Notes'), R('n07_strengthen_and_assumptions4.pdf', 'Notes'),
            R('n02_question_stem_and_answers1.pdf', 'Notes - reading the question stem')],
      drill={'RC': 4}, books=[R('Critical_Reasoning_01_3.pdf', 'Assignment'), R('Critical_Reasoning_01_Answers_3.pdf', 'Answer key')], quiz=['cr'],
      course={'ch': ['cr']},
      notes=['Find the conclusion first ("so", "therefore", "thus"), then the evidence, then the gap between them (the assumption).',
             'Weaken: attack the gap, often with an alternative cause. Strengthen: close the gap or rule out alternatives.',
             'Assumption: negate the choice - if the argument falls apart, it was the assumption.']),
    D('Quant', 'Inequalities and absolute value', learn=[L('Algebra, Equations and Inqualities', 19, 22)],
      read=[R('Inequalities.pdf', 'Notes')], drill={'MC': 5, 'QC': 4}, quiz=['inequalities'], course={'ch': ['inequalities']},
      notes=['Multiplying or dividing an inequality by a negative flips the sign.',
             '|x − a| < b means a − b < x < a + b; |x − a| > b means x < a − b or x > a + b.',
             'For ranges like a − b, combine extremes: min = min(a) − max(b).',
             'Squaring both sides of an inequality is only safe when both sides are positive.']),
    D('Review', 'Week 5 test + unit test', drill={'MC': 6, 'QC': 3, 'NE': 2, 'RC': 3}, quiz=['equations', 'inequalities', 'cr'], course={'units': ['u2']},
      notes=['Take Unit 2 (exponents, roots & expressions) in the Tutor step.'] + REVIEW_NOTES),
    # ---------------------------------------------------------------- WEEK 6
    D('Quant', 'Functions, symbols and formulas', learn=[L('Algebra, Equations and Inqualities', 23, 24)],
      read=[R('Functions_Sequences_and_Formulas_1_.pdf', 'Notes')], drill={'MC': 6, 'NE': 2}, quiz=['functions'], course={'ch': ['functions']},
      notes=['f(x) is a rule: replace every x with what is in the brackets, carefully, with brackets.',
             'Strange symbols (x ◊ y) are just functions - substitute carefully, innermost first.',
             'Composite f(g(x)): do g first, then f.',
             'Formula questions ("if r doubles, what happens to V?"): plug in simple numbers before and after.']),
    D('Verbal', 'Critical reasoning: paradox, boldface and flaws', learn=[L('Paragraph Elements', 6, 10)],
      read=[R('n06_cause_and_effect2.pdf', 'Notes'), R('n08_paradox_questions_and_flaw_in_reasoning3.pdf', 'Notes'), R('n09_parallel_reasoning1.pdf', 'Notes'),
            R('n03_must_be_true_questions1.pdf', 'Notes - must-be-true (inference) questions'), R(VSTRAT, 'Verbal Strategies: the argument-structure / logic-based reading chapter')],
      drill={'RC': 4}, books=[R('Optional_Critical_Reasoning_Extra_Practice.pdf', 'Extra practice')], quiz=['cr', 'cr2'], course={'ch': ['cr2']},
      notes=['Paradox: the answer explains how both surprising facts can be true together.',
             'Boldface: label each bold part (conclusion, evidence, counter-point) before looking at the choices.',
             'Common flaws: reversing a conditional, unrepresentative sample, correlation ≠ causation, numbers vs percents.']),
    D('Quant', 'Quantitative comparison strategies', learn=[L('Adbanced QC strategies')], read=[G('qcdi', 'Quantitative-comparison chapters')], drill={'QC': 10}, quiz=['qc'],
      notes=['Simplify both sides the same way (like a balance scale) until the comparison is obvious.',
             'Plug in at least two very different values; if the answer changes, it is (D).',
             'Geometry QC: figures are not necessarily drawn to scale - imagine stretching the figure.',
             'If the quantities are fixed numbers, the answer cannot be (D).']),
    D('Writing', 'Analytical Writing: the Issue essay', learn=[L('AWA Basics'), L('Issue Task')],
      read=[R('AWA.pdf', 'Magoosh AWA guide'), R('ESSAYANSWERS.pdf', 'ETS scored sample essays - read a 6 and a 4 and compare'),
            {'name': 'ETS - Analytical Writing (official prompts and scoring)', 'note': 'Official page', 'url': ETS_WRITING}],
      essay=True, notes=['Only the Issue task is on the test now (30 minutes). Ignore Argument-task material.',
                         'Plan 5 minutes: take a clear position and pick 2-3 specific examples (history, business, science, your own work).',
                         'Structure: intro with thesis → 2-3 body paragraphs (one example each) → acknowledge the other side → conclusion.',
                         'Graders reward clear reasoning and specific examples over length or fancy words. Save 2 minutes to proofread.'],
      homework='Write one Issue essay in the app (30-minute timer) and press "Save & get AI score".'),
    D('Verbal', 'Critical reasoning + RC mixed set', read=[R('n04_main_point_questions1.pdf', 'Notes - main-point questions')], drill={'RC': 8}, quiz=['cr', 'cr2'],
      notes=['For argument passages inside RC, use the same CR method: conclusion → evidence → gap.',
             'Eliminate choices that are out of scope even if they sound sensible.']),
    D('Review', 'Week 6 test + first timed quant set', drill={'MC': 8, 'QC': 4, 'NE': 2, 'MA': 1}, quiz=['equations', 'inequalities', 'functions', 'qc', 'cr2'],
      course={'units': ['u3']},
      notes=['Do today\'s 15 quant questions in 26 minutes (one real section) - practise pacing.',
             'Then take Unit 3 (equations, inequalities & functions) in the Tutor step.'] + REVIEW_NOTES),
    # ---------------------------------------------------------------- WEEK 7
    D('Quant', 'Percents', learn=[L('Percents and Ratios')], read=[R('Percents1.pdf', 'Notes'), G('fdp', 'Percents chapter')],
      drill={'MC': 6, 'NE': 2}, quiz=['percents'], course={'ch': ['percents']},
      notes=['Percent change = (new − old)/old. Use multipliers: +20% → × 1.2, −15% → × 0.85.',
             'Successive changes multiply: up 20% then down 20% = × 0.96 (a 4% loss).',
             'Reverse percent: if the price after a 20% rise is 360, the original is 360 ÷ 1.2 = 300 (not 360 × 0.8).',
             'Pick 100 for percent problems with no actual numbers.']),
    D('Verbal', 'Hard text completions', drill={'TC': 10}, books=[R(GRAIL, 'Verbal Grail: the hardest text-completion set you have not done')], quiz=['tc_double', 'tc_triple'],
      notes=['Hard TCs hide the clue: paraphrase the sentence in simple words before predicting.',
             'Second meanings are common on hard questions (temper, check, qualify, sanction).']),
    D('Quant', 'Ratios and proportions', read=[R('Ratio.pdf', 'Notes')], drill={'MC': 6, 'QC': 2, 'NE': 2}, books=[q1014('percents & ratios')], quiz=['ratios', 'percents'],
      course={'ch': ['ratios']},
      notes=['Ratios are parts: a : b = 3 : 5 means 8 parts in total, so a = 3/8 of the total.',
             'To join two ratios (a : b and b : c), make the shared term equal first.',
             'If the ratio changes after adding something, write both ratios with an unknown multiplier k and solve.',
             'Pick a multiple of the ratio total when no numbers are given.']),
    D('Verbal', 'Reading: science passages and inference', read=[G('rc', 'Science-passage section')], drill={'RC': 8}, books=[rc99(21, 30)], quiz=['rc'],
      notes=['Science passages are full of detail - read for the claim, the evidence and any "however" or "recent studies" turn.',
             'You do not need to understand every term; track what each paragraph DOES (describe, challenge, explain).',
             'Inference answers stay close to the text. If a choice needs outside knowledge, it is wrong.']),
    D('Quant', 'Word problems: setting up, age and motion', learn=[L('Word Problems', 1, 9)],
      read=[G('wp', 'Translating words / rates chapters'), R('SRT_WRT_2.pdf', 'Notes - speed, rate, time')], drill={'MC': 6, 'NE': 2},
      books=[q1014('word problem')], quiz=['word_motion'], course={'ch': ['word_motion']},
      notes=['Define variables in words ("let m = Maria\'s age now"), then translate sentence by sentence.',
             'Distance = rate × time. Average speed = total distance ÷ total time, never the average of speeds.',
             'Moving toward each other: add speeds. Same direction: subtract speeds.',
             'Age problems: a table with "now" and "in n years" columns avoids mistakes.']),
    D('Review', 'Week 7 test + verbal unit test', drill={'MC': 5, 'NE': 2, 'TC': 4, 'SE': 3, 'RC': 3}, quiz=['percents', 'ratios', 'word_motion', 'cr2'],
      course={'units': ['v2']}, notes=['Take Verbal unit 2 (reading & reasoning) in the Tutor step.'] + REVIEW_NOTES),
    # ---------------------------------------------------------------- WEEK 8
    D('Quant', 'Work, growth, mixtures and overlapping sets', learn=[L('Word Problems', 10, 15)],
      read=[R('Rates_Work.pdf', 'Notes'), R('Venn_Diagram__amp__Matrix_2.pdf', 'Notes - Venn diagrams & double matrix')], drill={'MC': 5, 'NE': 2},
      books=[R('lecture_10_word_problems.docx', 'Assignment'), R('lecture_10_word_problems_answers.docx', 'Answer key'), q1014('rates, work & mixture')],
      quiz=['work_mix_sets'], course={'ch': ['work_mix_sets']},
      notes=['Work: rates add. If A takes a hours and B takes b hours, together 1/a + 1/b jobs per hour.',
             'Mixtures: track the amount of the pure substance, not the percentage.',
             'Two overlapping groups: Total = A + B − Both + Neither. With two yes/no attributes, use a double matrix.']),
    D('Writing', 'Issue essay #2 + RC practice', read=[R('NOVA_GRE_Writing.pdf', 'Skim one model essay')], drill={'RC': 6}, essay=True,
      notes=['Write the essay first (30 minutes), then do the RC set.',
             'Compare with your first essay and its AI feedback: is the thesis clearer? Are the examples more specific?']),
    D('Quant', 'Sequences, consecutive integers, backsolving and VICs', learn=[L('Word Problems', 16, 25)], drill={'MC': 6, 'MA': 2},
      books=[flash('word problems & sequences')], quiz=['sequences'], course={'ch': ['sequences']},
      notes=['Arithmetic sequence: aₙ = a₁ + (n − 1)d. Sum = number of terms × average of first and last.',
             'Inclusive count from a to b = b − a + 1.',
             'Backsolving: when answers are numbers, start with the middle choice and test it.',
             'Variables in the choices (VICs): pick simple numbers for the variables and test every choice.']),
    D('Verbal', 'Mixed text completion + sentence equivalence', drill={'TC': 8, 'SE': 6}, books=[R(GRAIL, 'Verbal Grail: a mixed TC + SE set')], quiz=['tc_shift', 'tc_double', 'se'],
      notes=['Time yourself: about 1 minute per one-blank TC/SE, 1.5-2 minutes for two/three blanks.',
             'Words you meet in today\'s questions that you do not know go straight into your flashcards.']),
    D('Quant', 'Statistics I: mean, median, mode and weighted averages', learn=[L('Statistics')], read=[R('Weighted_Averages__Averages__Medians.pdf', 'Notes')],
      drill={'MC': 6, 'QC': 3}, books=[R('lecture_10_stats.docx', 'Assignment'), R('lecture_10_stats_answers.docx', 'Answer key'), q1014('statistics')],
      quiz=['stats'], course={'ch': ['stats']},
      notes=['Sum = mean × count is the most useful stats fact on the GRE.',
             'Median: sort first; for an even count average the middle two.',
             'Weighted average sits closer to the larger group.',
             'Adding a value above the mean raises the mean; the median moves at most to the next value.']),
    D('Review', 'Week 8 test + unit test', drill={'MC': 6, 'NE': 2, 'TC': 4, 'SE': 3}, quiz=['work_mix_sets', 'sequences', 'stats', 'percents'],
      course={'units': ['u4']}, notes=['Take Unit 4 (word problems) in the Tutor step.'] + REVIEW_NOTES),
    # ---------------------------------------------------------------- WEEK 9
    D('Quant', 'Statistics II: spread, quartiles and the normal distribution', read=[R('Stdev.pdf', 'Notes')], drill={'MC': 5, 'QC': 3, 'DI': 2}, quiz=['stats'],
      notes=['SD measures spread: adding a constant does not change it; multiplying by k multiplies it by |k|.',
             'You never need to calculate an SD on the GRE - compare spreads by eye (which set is more spread out from its mean?).',
             'Normal distribution: about 68% within 1 SD of the mean, 95% within 2 SD, and it is symmetric.',
             'Quartiles and box plots: Q1, median, Q3 split the data into four equal-count groups; range = max − min, IQR = Q3 − Q1.']),
    D('Verbal', 'Sentence equivalence + RC', drill={'SE': 8, 'RC': 4}, books=[rc99(31, 40)], quiz=['se', 'rc'],
      notes=['SE: predict first, then look for two words that both match your prediction. Watch for the trap pair.',
             'RC: before answering, find the line that proves your answer.']),
    D('Quant', 'Counting', learn=[L('Counting')], read=[R('Probability___Combinatorics.pdf', 'Notes')], drill={'MC': 6, 'NE': 2}, books=[q1014('counting')],
      quiz=['counting'], course={'ch': ['counting']},
      notes=['Fundamental counting principle: multiply the number of options at each step.',
             'Order matters → permutations (nPr). Order does not matter → combinations (nCr = n!/(r!(n − r)!)).',
             'Identical items: divide by the factorial of each repeat (LEVEL = 5!/(2!2!)).',
             '"Must sit together": glue them into one unit, then multiply by their internal arrangements.']),
    D('Verbal', 'Critical reasoning: timed set', read=[R('n07_strengthen_and_assumptions4.pdf', 'Re-read the assumption section')], drill={'RC': 6}, quiz=['cr', 'cr2'],
      notes=['About 1.5-2 minutes per argument. Read the question stem FIRST so you know what to look for.',
             'Before reading the choices, say the gap in your own words.',
             'Afterwards, sort each miss in the Error log: did you misread the conclusion, or fall for an out-of-scope choice?']),
    D('Quant', 'Probability basics', learn=[L('Probability', 1, 8)], read=[R('Probability.pdf', 'Notes')], drill={'MC': 6}, books=[q1014('probability')],
      quiz=['probability'], course={'ch': ['probability']},
      notes=['P = favourable / total, when all outcomes are equally likely.',
             'P(A or B) = P(A) + P(B) − P(A and B). Mutually exclusive → just add.',
             'Independent: P(A and B) = P(A) × P(B). Without replacement, change the second fraction.']),
    D('Mock', 'Full practice test 1 (ETS POWERPREP)', mock={'name': 'ETS POWERPREP Online - free practice test 1', 'url': POWERPREP},
      notes=['Choose the TIMED mode - ETS only gives Verbal and Quant scores for timed POWERPREP tests.',
             'This is the midway check: with POWERPREP 2 about a week before the exam, these two are your most accurate score guides.'] + MOCK_NOTES, minutes=150),
    # ---------------------------------------------------------------- WEEK 10
    D('Quant', 'Probability: "at least", combinations and strategy', learn=[L('Probability', 9, 16)], drill={'MC': 5, 'QC': 3, 'MA': 2},
      books=[flash('probability & counting')], quiz=['probability', 'counting'],
      notes=['"At least one" → 1 − P(none).',
             'Probability with counting: P = (ways to get what you want) / (total ways), both using combinations.',
             'If a listing would take under a minute, just list the outcomes.']),
    D('Writing', 'Issue essay #3 + RC', drill={'RC': 6}, essay=True,
      notes=['Write to time (30 minutes). Then reread one of your earlier essays and fix its weakest paragraph.',
             'Use the AI feedback\'s "to improve" list from last time as your checklist.']),
    D('Quant', 'Data interpretation', learn=[L('Data Interpretation')], read=[R('Data_Interpretation.pdf', 'Notes'), G('qcdi', 'Data-interpretation chapters')],
      drill={'DI': 12}, books=[q1014('data interpretation')], quiz=['di'], course={'ch': ['di']},
      notes=['Spend 20-30 seconds reading the graph first: title, units, scale, legend.',
             'Estimate - DI answer choices are usually far enough apart to round.',
             'Percent of total vs percent change: read which one is asked.',
             'Use the on-screen calculator for ugly numbers, but set up the expression first.']),
    D('Verbal', 'Timed verbal section 1', drill={'TC': 5, 'SE': 3, 'RC': 4}, books=[rc99(41, 50)], quiz=['tc_basic', 'tc_shift', 'se', 'rc'],
      course={'sections': ['verbal']},
      notes=['Do the 12 questions in 18 minutes - the length of the first verbal section.',
             'Order: TC and SE first (fast), RC last. Mark and skip anything over 2 minutes.',
             'Then run the verbal section simulation in the Tutor step.']),
    D('Quant', 'Data interpretation II: tricky charts and estimation', read=[G('qcdi', 'Remaining data-interpretation problem sets')], drill={'DI': 10, 'MC': 2}, quiz=['di', 'stats'],
      notes=['Watch for mixed charts: one axis in percent, the other in absolute numbers.',
             'Questions about "approximately" want estimation - round to 1-2 significant figures.',
             'Multiple-answer DI questions: test each choice on its own.',
             'If a DI question takes over 3 minutes, guess and come back - there are usually 3 questions per set.']),
    D('Review', 'Week 10 test + unit test + quant section', drill={'MC': 5, 'DI': 4, 'TC': 4, 'SE': 3}, quiz=['probability', 'counting', 'di', 'cr2'],
      course={'units': ['u5'], 'sections': ['quant']},
      notes=['Take Unit 5 (data analysis) and the first quant section simulation in the Tutor step.'] + REVIEW_NOTES),
    # ---------------------------------------------------------------- WEEK 11 - geometry
    D('Quant', 'Lines, angles and triangles', learn=[L('Geometry', 1, 9)], read=[R('Triangles_Notes.pdf', 'Notes'), R('Lines_notes.pdf', 'Notes'), G('geo', 'Triangles chapter')],
      drill={'MC': 5, 'QC': 3}, books=[R('lecture_07_polygons_triangles.docx', 'Assignment'), R('lecture_07_polygons_triangles_answers.docx', 'Answer key'), flash('geometry')],
      quiz=['triangles'], course={'ch': ['triangles']},
      notes=['Angles in a triangle sum to 180°; the exterior angle equals the sum of the two remote interior angles.',
             'Third side of a triangle: between (difference) and (sum) of the other two.',
             'Right-triangle triples: 3-4-5, 5-12-13, 8-15-17 and their multiples. 45-45-90 = x : x : x√2. 30-60-90 = x : x√3 : 2x.',
             'Similar triangles: corresponding sides in the same ratio; areas in the ratio squared.']),
    D('Verbal', 'Reading: humanities and social-science passages', drill={'RC': 8}, books=[rc99(51, 60)], quiz=['rc', 'cr'],
      notes=['Humanities passages are about viewpoints: separate the author\'s view from the views the author describes.',
             'Social-science passages often contain an argument - use the CR method (conclusion, evidence, gap).',
             'Tone is usually moderate: "qualified support" and "measured criticism" beat extreme choices.']),
    D('Quant', 'Polygons and circles', learn=[L('Geometry', 10, 18)], read=[R('Circles_Notes.pdf', 'Notes'), R('Polygons_Notes.pdf', 'Notes')], drill={'MC': 6, 'QC': 3},
      books=[q1014('geometry')], quiz=['circles_polys'], course={'ch': ['circles_polys']},
      notes=['Sum of interior angles = (n − 2) × 180°.',
             'Circle: C = 2πr, A = πr². Arc and sector = (central angle / 360) × full circle.',
             'An inscribed angle is half the central angle on the same arc; a triangle on a diameter has a right angle.']),
    D('Writing', 'Issue essay #4 + critical reasoning review', drill={'RC': 6}, essay=True, quiz=['cr', 'cr2'],
      notes=['Essay first (30 minutes), then the CR set.', 'Aim for 450-600 words with two developed examples.']),
    D('Quant', 'Coordinate geometry', learn=[L('Coordinate Geometry')], read=[R('Coordinate_Geometry_Notes.pdf', 'Notes')], drill={'MC': 5, 'QC': 3},
      books=[R('lecture_08_circles_coordinate.docx', 'Assignment'), R('lecture_08_circles_coordinate_answers.docx', 'Answer key'), q1014('coordinate geometry')],
      quiz=['coordinate'], course={'ch': ['coordinate']},
      notes=['Slope = rise/run = (y₂ − y₁)/(x₂ − x₁). y = mx + b: m is the slope, b the y-intercept.',
             'Parallel lines: equal slopes. Perpendicular: slopes multiply to −1.',
             'Distance = √((Δx)² + (Δy)²) - it is just Pythagoras.',
             'Reflection over the x-axis: (x, y) → (x, −y); over y = x: (x, y) → (y, x).']),
    D('Mock', 'Full practice test 2 (Manhattan Prep free test)', mock={'name': 'Manhattan Prep - free full-length online GRE practice test', 'url': MANHATTAN_FREE_TEST},
      notes=['POWERPREP test 2 is saved for about a week before your exam, when it is the best guide to your score - so today use Manhattan Prep\'s free test.',
             'Manhattan tests run slightly harder than the real GRE; compare section by section with POWERPREP 1, not just the total.',
             'Pick your 3 weakest topics from the Error log and the Progress tab for the revision weeks ahead.'] + MOCK_NOTES[1:], minutes=150),
    # ================================================================ PHASE 2 - TIMED REVISION (weeks 12-15)
    # ---------------------------------------------------------------- WEEK 12
    D('Quant', '3-D shapes and mixed geometry + geometry unit test', read=[G('geo', 'Solids / 3-D chapter')], drill={'MC': 6, 'QC': 3}, quiz=['circles_polys', 'triangles', 'coordinate'],
      course={'units': ['u6']},
      notes=['Box: V = lwh, surface area = 2(lw + lh + wh), diagonal = √(l² + w² + h²). Cylinder: V = πr²h, SA = 2πr² + 2πrh.',
             'Shaded-area questions: area of the big shape minus the area of what is not shaded.',
             'Draw the figure yourself and label everything you know - most geometry questions are 2-3 small steps.',
             'Then take Unit 6 (geometry) in the Tutor step.']),
    D('Verbal', 'Timed verbal section 2', drill={'TC': 6, 'SE': 4, 'RC': 5}, books=[rc99(61, 75)], quiz=['tc_double', 'tc_triple', 'se', 'rc'],
      course={'sections': ['verbal']},
      notes=['15 questions in 23 minutes - the length of the second verbal section.', 'Then run the verbal section simulation in the Tutor step.']),
    D('Quant', 'Revision: arithmetic and number properties', read=[R(FIVE_LB, 'Do the Arithmetic, Number Properties and Divisibility & Primes chapters (as many as time allows)')],
      drill={'MC': 8, 'QC': 4, 'NE': 2}, books=[tough('arithmetic / number properties')], quiz=['arithmetic', 'integers', 'odd_even', 'exponents'],
      notes=['From now on every set is timed: about 1.5 minutes per quant question.', 'Redo your Error-log entries for these topics first.']),
    D('Verbal', 'Vocabulary sweep + text completion', drill={'TC': 6, 'SE': 4}, quiz=['tc_basic', 'tc_shift', 'se'],
      notes=['Vocab trainer: review every word in boxes 1-2 until it moves up. All 37 groups should be unlocked by now.',
             'Then a timed TC/SE set - note any word that cost you a question.']),
    D('Quant', 'Revision: algebra and inequalities', read=[R(FIVE_LB, 'Algebra, Inequalities & Absolute Values, Functions/Formulas/Sequences chapters')],
      drill={'MC': 8, 'QC': 4, 'MA': 2}, books=[tough('algebra / inequalities')], quiz=['algebra_expr', 'equations', 'inequalities', 'functions']),
    D('Review', 'Week 12 test + unit retests', drill={'MC': 6, 'QC': 3, 'TC': 4, 'SE': 3}, quiz=['exponents', 'roots', 'functions', 'tc_triple'],
      course={'retest': ['u1', 'u2']},
      notes=['Retake Units 1 and 2 in the Tutor step - aim for 80%+. Anything under 70% goes on next week\'s revision list.'] + REVIEW_NOTES),
    # ---------------------------------------------------------------- WEEK 13
    D('Quant', 'Revision: word problems and rates', read=[R(FIVE_LB, 'Word Problems, Rates & Work chapters')], drill={'MC': 8, 'NE': 3, 'DI': 4},
      books=[tough('word problems')], quiz=['word_motion', 'work_mix_sets', 'sequences', 'percents']),
    D('Verbal', 'Two timed verbal sections', drill={'TC': 10, 'SE': 6, 'RC': 11}, books=[R(GRAIL, 'Verbal Grail: redo the sets where you scored lowest')], quiz=['tc_triple', 'se', 'rc', 'cr'],
      course={'sections': ['verbal']},
      notes=['Section A: 12 questions in 18 minutes. Section B: 15 questions in 23 minutes.', 'Short break between, as on test day.']),
    D('Quant', 'Revision: percents, ratios and statistics', read=[R(FIVE_LB, 'Percents, Ratios, Averages/Weighted Averages, Standard Deviation chapters')],
      drill={'MC': 8, 'QC': 4, 'DI': 4}, books=[tough('percents / statistics')], quiz=['percents', 'ratios', 'stats', 'di']),
    D('Writing', 'Issue essay #5 + mixed quant', drill={'MC': 6}, essay=True, quiz=['algebra_expr', 'word_motion'],
      notes=['Write to time. Compare the AI score with your last three essays - is the trend going up?']),
    D('Quant', 'Revision: counting and probability', read=[R(FIVE_LB, 'Probability, Combinatorics & Overlapping Sets chapter')], drill={'MC': 8, 'MA': 3, 'NE': 2},
      books=[tough('counting / probability')], quiz=['counting', 'probability', 'work_mix_sets']),
    D('Mock', 'Full practice test 3', mock={'name': 'Kaplan GRE Prep 2019 - practice test in the PDF (or a free online test from Manhattan Prep / Princeton Review)', 'url': file_url(KAPLAN)},
      books=[R(BARRON6, 'Alternative full test: Barron\'s 6 GRE Practice Tests - test 1')],
      notes=['Third-party tests are often harder than the real GRE - use them for practice, not to predict your score.', 'Review every question and log errors.'], minutes=150),
    # ---------------------------------------------------------------- WEEK 14
    D('Quant', 'Revision: geometry and coordinate geometry', read=[R(FIVE_LB, 'Geometry chapters (polygons, triangles, circles, coordinate)')], drill={'MC': 8, 'QC': 5},
      books=[tough('geometry')], quiz=['triangles', 'circles_polys', 'coordinate'], course={'retest': ['u6']}),
    D('Verbal', 'Reading endurance: long passages under time', drill={'RC': 10}, books=[rc99(76, 85)], quiz=['rc'],
      notes=['Three long passages back to back, timed. Keep your paragraph map for each.',
             'Notice when your concentration drops - that is when to slow down and re-read the question.']),
    D('Quant', 'Two timed quant sections', drill={'MC': 12, 'QC': 7, 'NE': 3, 'DI': 3, 'MA': 2}, quiz=['qc', 'di', 'stats'], course={'sections': ['quant']},
      notes=['Section A: 12 questions in 21 minutes. Section B: 15 questions in 26 minutes. Short break between.',
             'Use the on-screen calculator only when it is faster than mental maths.']),
    D('Verbal', 'Critical reasoning + boldface revision', drill={'RC': 6}, quiz=['cr', 'cr2'],
      notes=['Redo every CR question in your Error log first.', 'Boldface: label each part before you look at the choices.']),
    D('Quant', 'Hard-problem day', drill={'MC': 6, 'QC': 3}, books=[R(TOUGH, 'Hard problems from your 2 weakest topics'), R('320-GRE-Math-Problems.pdf', 'The hardest problems in your weakest topic')],
      quiz=['inequalities', 'probability', 'counting'],
      notes=['To reach 165+ you need the hard questions: spend today on the hardest problems you can find.',
             'Allow up to 3 minutes each today - then study the solution until you could teach it.']),
    D('Mock', 'Full practice test 4', mock={'name': 'Free online practice test from Princeton Review or Magoosh, or the second test in the Kaplan 2019 PDF', 'url': file_url(KAPLAN)},
      books=[R(BARRON6, 'Alternative full test: Barron\'s - test 2')],
      notes=['Track: Quant and Verbal scores, and how many questions you ran out of time on.'] + MOCK_NOTES[1:], minutes=150),
    # ---------------------------------------------------------------- WEEK 15
    D('Quant', 'Weak-area day (quant) + unit retests', drill={'MC': 8}, books=[R('320-GRE-Math-Problems.pdf', 'Pick problems from your 2 weakest topics')],
      quiz=['inequalities', 'probability', 'circles_polys', 'percents'], course={'retest': ['u3', 'u4']},
      notes=['Open the Error log, filter to Quant, and redo every logged question.', 'Then retake Units 3 and 4 in the Tutor step.']),
    D('Verbal', 'Weak-area day (verbal) + vocab sweep', drill={'TC': 6, 'SE': 6}, quiz=['tc_shift', 'tc_double', 'se'], course={'retest': ['v1']},
      notes=['Vocab trainer: review every word in boxes 1-2 until it moves up.', 'Redo every logged verbal error, then retake Verbal unit 1.']),
    D('Writing', 'Issue essay #6 under test conditions', drill={'MC': 4, 'TC': 3}, essay=True,
      notes=['Write at the time of day you will test, with no breaks - exactly 30 minutes.',
             'Afterwards, get the AI score and fix only the one thing it says matters most.']),
    D('Quant', 'Quant section simulation + review', drill={'MC': 6, 'QC': 4, 'NE': 2}, quiz=['qc', 'algebra_expr', 'word_motion'], course={'sections': ['quant']},
      notes=['Run the full quant section simulation in the Tutor step (section 1, then the adaptive section 2).',
             'Review every miss and every slow question - the results page flags them.']),
    D('Verbal', 'Verbal section simulation + review', drill={'TC': 4, 'SE': 3, 'RC': 5}, quiz=['tc_triple', 'se', 'rc'], course={'sections': ['verbal']},
      notes=['Run the full verbal section simulation in the Tutor step.', 'Review every miss; sort them in the Error log.']),
    D('Mock', 'Full practice test 5 (official ETS questions)', mock={'name': 'A practice test from The Official Guide to the GRE, or a POWERPREP Plus test (paid, official)', 'url': ETS_BOOKS},
      books=[off(OG, 'Use one of the full practice tests in the book, timed like the real sections'), R(BARRON6, 'Alternative full test: Barron\'s - test 3')],
      notes=['Official ETS questions are the closest to test day - this is your second-best score guide after POWERPREP.'] + MOCK_NOTES[1:], minutes=150),
    # ================================================================ PHASE 3 - FINAL TESTS AND TAPER (weeks 16-17)
    # ---------------------------------------------------------------- WEEK 16
    D('Review', 'Review test 5 + Error-log sweep + unit retests', drill={'MC': 4, 'TC': 3}, quiz=['stats', 'di', 'rc'], course={'retest': ['u5', 'v2']},
      notes=['Review practice test 5 fully.', 'Read through the whole Error log once - just the rules you wrote.', 'Retake Unit 5 and Verbal unit 2 in the Tutor step.']),
    D('Quant', 'Speed day: data interpretation and quantitative comparison', drill={'QC': 8, 'DI': 6}, quiz=['qc', 'di'], course={'sections': ['quant']},
      notes=['QC and DI are where time is won or lost. Target: QC in under 1 minute, each DI question in under 2.',
             'Then one more quant section simulation in the Tutor step.']),
    D('Verbal', 'Full verbal under time (two sections)', drill={'TC': 8, 'SE': 5, 'RC': 10}, quiz=['tc_double', 'se', 'cr'], course={'sections': ['verbal']},
      notes=['Two verbal sections back to back with a short break.', 'Then one more verbal section simulation in the Tutor step.']),
    D('Writing', 'Final essay + your essay template', drill={'MC': 4}, essay=True,
      notes=['Write your last practice essay to time.',
             'Then write down your personal template: how you open, how many body paragraphs, where the counter-argument goes, how you conclude.',
             'Keep a short list of 5-6 flexible examples (history, business, science, technology, your own experience) you can adapt to any prompt.']),
    D('Quant', 'Light quant review', read=[R('GRE Quant - Formula Sheet - Target Test Prep.pdf', 'Read the full formula sheet once'),
                                          R('GRE Quant Notes.pdf', 'Quick revision notes'), R('Formulas for all topic.pdf', 'All formulas on one sheet'),
                                          R('points to remember1.pdf', 'Points to remember (part 1)'), R('points to remember 2.pdf', 'Points to remember (part 2)')],
      drill={'MC': 6}, quiz=['qc', 'triangles', 'stats'],
      notes=['No new topics from now on. Keep sessions short and confident.']),
    D('Mock', 'Final full practice test (ETS POWERPREP 2)', mock={'name': 'ETS POWERPREP Online - free practice test 2', 'url': POWERPREP},
      notes=['Choose the TIMED mode - ETS only gives Verbal and Quant scores for timed POWERPREP tests.',
             'Taken about a week before the exam, POWERPREP 2 is the most accurate guide to your real score (advice from a 329 scorer).',
             'Take it at the same time of day as your real test.'] + MOCK_NOTES[1:], minutes=150),
    # ---------------------------------------------------------------- WEEK 17 - taper
    D('Review', 'Review the final test + Error log', drill={'MC': 4, 'TC': 3}, read=[R('Maths Shortcuts.pdf', 'Re-read the shortcuts once')],
      notes=['Review the last test.', 'Read through the whole Error log once - just the rules you wrote.']),
    D('Verbal', 'Light verbal review', read=[R('GRE verbal notes.pdf', 'Quick revision notes for verbal')], drill={'TC': 5, 'SE': 5}, quiz=['tc_basic', 'se', 'cr2'],
      notes=['Clear your due flashcards, then a short, relaxed TC/SE set.']),
    D('Orientation', 'Test-day preparation', read=[{'name': 'ETS - register / manage your test', 'note': 'Check your appointment, ID rules and score-report choices', 'url': ETS_REGISTER}],
      drill={'MC': 3, 'TC': 3}, quiz=['arithmetic', 'tc_basic'],
      notes=['Your ID must exactly match the name on your ETS account.',
             'You can send free score reports to 4 institutions on test day - have your programme codes ready.',
             'At home test: check the room, webcam and system requirements a day before.',
             'Sleep 8 hours. Eat beforehand. During the test: mark and move, never stay stuck.']),
    D('Orientation', 'Rest day / test day', notes=['No studying. Light walk, early night - or this is your test day. Good luck!'], minutes=0),
]

# Official ETS material and a proven book order (from a 329 scorer's notes: github.com/DibG1/GRE_Prep):
#   Verbal: Manhattan Verbal Strategies -> 5 lb practice -> Princeton Verbal Workout -> official ETS Verbal book.
#   Quant: Manhattan 5 lb -> official ETS Quant book. Then the Official Guide, POWERPREP 1 midway and POWERPREP 2 a week before.
OFFICIAL = {
    'How the GRE works + baseline': dict(
        read=[W('ETS free mini quiz', 'Take it as your baseline: a short set of real ETS questions with explanations', ETS_MINI_QUIZ),
              W('ETS Math Review (free official PDF)', 'Download it now - you will read one part per topic as the plan reaches it', ETS_MATH_REVIEW)],
        notes=['Book order that worked for a 329 scorer (167Q, 162V): Verbal - Manhattan Verbal Strategies, then the Manhattan 5 lb verbal chapters, '
               'then the Princeton Verbal Workout, finally the official ETS Verbal book. Quant - the Manhattan 5 lb, then the official ETS Quant book. '
               'Then the Official Guide and POWERPREP. This plan follows that order.',
               'Official ETS books (not in the Drive folder): The Official Guide to the GRE (4th ed.) and the Official Quantitative and Verbal Reasoning '
               'Practice Questions books. They are the closest to the real test and are used in the revision weeks - order them early.'],
        homework='Order the three official ETS books (or the Super Power Pack) so they arrive before week 12.'),
    'Number line, signs, decimals and order of operations': dict(read=[mreview('Arithmetic (sections 1.1-1.5)')]),
    'Algebra: expressions and factoring': dict(read=[mreview('Algebra (sections 2.1-2.3)')]),
    'Functions, symbols and formulas': dict(read=[mreview('Algebra (functions, graphs and coordinate sections)')]),
    'Statistics I: mean, median, mode and weighted averages': dict(read=[mreview('Data Analysis (graphical methods and numerical methods for describing data)')]),
    'Statistics II: spread, quartiles and the normal distribution': dict(
        read=[mreview('Data Analysis (percentiles, quartiles, box plots, standard deviation, distributions)')],
        notes=['Also in the official syllabus: percentiles, frequency tables, histograms, scatterplots and time plots - the Math Review covers them; read those pages too.']),
    'Probability basics': dict(read=[mreview('Data Analysis (counting methods and probability, incl. conditional probability)')]),
    'Lines, angles and triangles': dict(read=[mreview('Geometry (lines, angles, triangles)')]),
    'Polygons and circles': dict(read=[mreview('Geometry (quadrilaterals, polygons, circles)')],
                                 notes=['Quadrilaterals: parallelogram area = base × height; trapezoid area = ½(a + b) × h; a rhombus has four equal sides and perpendicular diagonals.']),
    '3-D shapes and mixed geometry + geometry unit test': dict(read=[mreview('Geometry (three-dimensional figures)')]),
    # Manhattan 5 lb verbal chapters (after Verbal Strategies, per the book order above)
    'Text completion + sentence equivalence: timed set': dict(books=[R(FIVE_LB, 'Text Completion and Sentence Equivalence chapters - one timed set of each')]),
    'Hard text completions': dict(books=[R(FIVE_LB, 'The harder Text Completion sets')]),
    'Reading: science passages and inference': dict(books=[R(FIVE_LB, 'Reading Comprehension chapter - 2 passages, timed')]),
    'Mixed text completion + sentence equivalence': dict(books=[R(FIVE_LB, 'A mixed verbal practice set')]),
    'Reading: humanities and social-science passages': dict(books=[R(FIVE_LB, 'Reading Comprehension chapter - 2 more passages, timed')]),
    # revision: the official ETS practice books
    'Timed verbal section 2': dict(books=[off(OV, 'Text Completion chapter - first half')]),
    'Revision: arithmetic and number properties': dict(books=[off(OQ, 'Arithmetic chapter')]),
    'Vocabulary sweep + text completion': dict(books=[off(OV, 'Sentence Equivalence chapter - first half')]),
    'Revision: algebra and inequalities': dict(books=[off(OQ, 'Algebra chapter')]),
    'Revision: word problems and rates': dict(books=[off(OQ, 'Algebra chapter - the word problems you have not done')]),
    'Two timed verbal sections': dict(books=[off(OV, 'Text Completion chapter - second half')]),
    'Revision: percents, ratios and statistics': dict(books=[off(OQ, 'Data Analysis chapter - first half')]),
    'Revision: counting and probability': dict(books=[off(OQ, 'Data Analysis chapter - second half')]),
    'Revision: geometry and coordinate geometry': dict(books=[off(OQ, 'Geometry chapter')]),
    'Reading endurance: long passages under time': dict(books=[off(OV, 'Reading Comprehension chapter - first half')]),
    'Two timed quant sections': dict(books=[off(OQ, 'Mixed practice set 1, timed')]),
    'Critical reasoning + boldface revision': dict(books=[off(OV, 'Reading Comprehension chapter - the argument (critical reasoning) questions')]),
    'Weak-area day (quant) + unit retests': dict(books=[off(OQ, 'Redo the official questions you missed')]),
    'Weak-area day (verbal) + vocab sweep': dict(books=[off(OV, 'Sentence Equivalence chapter - second half')]),
    'Quant section simulation + review': dict(books=[off(OQ, 'Mixed practice set 2, timed')]),
    'Verbal section simulation + review': dict(books=[off(OV, 'Mixed practice set 1, timed')]),
    'Speed day: data interpretation and quantitative comparison': dict(books=[off(OG, 'Quantitative Reasoning practice sets - QC and data interpretation questions')]),
    'Full verbal under time (two sections)': dict(books=[off(OV, 'Mixed practice set 2, timed'), off(OG, 'Verbal Reasoning practice sets')]),
    'Light quant review': dict(books=[off(OG, 'Redo 10 official quant questions you got wrong')]),
    'Light verbal review': dict(books=[off(OG, 'Redo 10 official verbal questions you got wrong')]),
}
_titles = {d['title']: d for d in PLAN}
for _t, _x in OFFICIAL.items():
    _d = _titles[_t]  # KeyError here = a title in OFFICIAL no longer matches the plan
    _d['read'] = _x.get('read', []) + _d['read']
    _d['books'] = _x.get('books', []) + _d['books']
    _d['notes'] = _d['notes'] + _x.get('notes', [])
    if _x.get('homework'):
        _d['homework'] = (_d['homework'] + ' ' if _d['homework'] else '') + _x['homework']
for _d in PLAN:
    if _d['essay']:
        _d['read'].append(W('ETS - official Issue topic pool', 'The real test picks its prompt from this published pool - practise with prompts from it', ETS_ISSUE))

# shown in the Library tab
OFFICIAL_LIBRARY = [
    {'name': OG, 'note': 'Official ETS questions with explanations and full practice tests. Used in weeks 15-17.', 'url': ETS_BOOKS, 'kind': 'Buy'},
    {'name': OQ, 'note': 'Official quant questions by topic (arithmetic, algebra, geometry, data analysis) + mixed sets. Used in weeks 12-15.', 'url': ETS_BOOKS, 'kind': 'Buy'},
    {'name': OV, 'note': 'Official TC, SE and RC questions + mixed sets. Used in weeks 12-15.', 'url': ETS_BOOKS, 'kind': 'Buy'},
    {'name': 'ETS Math Review', 'note': 'The official quant syllabus with exercises - read part by part with the quant classes.', 'url': ETS_MATH_REVIEW, 'kind': 'Free'},
    {'name': 'POWERPREP Online tests 1 and 2', 'note': 'Test 1 on day 54 (midway), test 2 on day 96 (about a week before the exam). Always timed mode.', 'url': POWERPREP, 'kind': 'Free'},
    {'name': 'ETS Issue topic pool', 'note': 'The published pool the real essay prompt comes from.', 'url': ETS_ISSUE, 'kind': 'Free'},
    {'name': 'ETS mini quiz', 'note': 'Short set of real questions - your Day 1 baseline.', 'url': ETS_MINI_QUIZ, 'kind': 'Free'},
    {'name': 'Manhattan Prep free practice test', 'note': 'Full-length test on day 66.', 'url': MANHATTAN_FREE_TEST, 'kind': 'Free'},
]
STUDY_ORDER = {'source': 'https://github.com/DibG1/GRE_Prep', 'who': 'a 329 scorer (167 Q, 162 V)', 'steps': [
    'Verbal: Manhattan Verbal Strategies → Manhattan 5 lb verbal chapters → Princeton Verbal Workout → official ETS Verbal book.',
    'Quant: Manhattan 5 lb → official ETS Quant book.',
    'Then the Official Guide. POWERPREP 1 midway, POWERPREP 2 about a week before the exam - the two most accurate score guides.',
    'Retake a third-party mock a few weeks later to check you have fixed its mistakes.']}

DAYS_PER_WEEK = 6
assert len(PLAN) == 100, len(PLAN)

# daily reading habit (builds RC stamina): rotate through the Best American collections in the RC folder
READING = [
    'Rebecca Solnit - Best American Essays 2019-Mariner Books (2019).epub',
    'Sy Montgomery - The Best American Science and Nature Writing 2019-HMH Books.epub',
    '(Best American Series) Edan Lepucki - The Best American Nonrequired Reading 2019-Mariner Books (2019).epub',
    'Jason Wilson - The Best American Travel Writing 2019-HMH Books.epub',
    '(The Best American Series) Glenn Stout, Howard Bryant - The Best American Sports Writing 2017-Houghton Mifflin Harcourt (2017).epub',
    'Anthony Doerr - The Best American Short Stories 2019-HMH Books.epub',
]


def _add_reading():
    k = 0
    for d in PLAN:
        if not d['mock'] and d['minutes']:
            book = READING[(k // 6) % len(READING)]  # one collection per week, then the next
            k += 1
            d['read'].append(R(book, 'Daily reading habit (15-20 min): read one piece and write its main point in one sentence'))


_add_reading()


def _assign():
    """Give each day its number/week, Magoosh practice ranges (sequential per type) and resolve lesson videos."""
    ptr = {k: 0 for k in PTYPES}
    group = 0
    for i, d in enumerate(PLAN):
        d['day'] = i + 1
        d['week'] = i // DAYS_PER_WEEK + 1
        d['weekday'] = i % DAYS_PER_WEEK  # 0 = Mon ... 5 = Sat
        # vocab: one new group per weekday (not on review/mock Saturdays) until all groups are learnt
        if d['weekday'] != 5 and group < 37:
            group += 1
            d['vocab'] = {'new': group}
        else:
            d['vocab'] = {'review': True}
        sets = []
        for code, n in d['drill'].items():
            folder = PRACTICE.get(PTYPES[code])
            if not folder or not folder['items']:
                continue
            items = folder['items']
            start = ptr[code]
            take = items[start:start + n]
            if len(take) < n:  # ran out: wrap around for revision
                take += items[:n - len(take)]
            ptr[code] = (start + n) % len(items)
            sets.append({'code': code, 'name': PNAMES[code], 'folder': folder['url'],
                         'items': [{'n': it[0], 'q': [f'https://drive.google.com/file/d/{x}/view' for x in it[1]],
                                    's': f'https://drive.google.com/file/d/{it[2]}/view' if it[2] else None} for it in take]})
        d['practice'] = sets
        vids = []
        for _, folder, a, b in d['learn']:
            les = LESSONS.get(folder, {'url': None, 'videos': []})
            chosen = les['videos'][a - 1:b] if b else les['videos'][a - 1:]
            vids.append({'folder': folder, 'folder_url': les['url'], 'videos': [
                {'title': t, 'url': f'https://drive.google.com/file/d/{fid}/view'} for _, t, fid in chosen]})
        d['videos'] = vids
        d['quiz_names'] = d['quiz']
    return ptr


USAGE = _assign()
WEEKS = PLAN[-1]['week']

# ---------------------------------------------------------------- tutor-course schedule (read by gre_course / gre_verbal)
CH_DAY = {}         # chapter -> day it is taught
UNIT_DAY = {}       # unit -> day of its first combined test
RETEST_DAYS = {}    # day -> [units retested]
SECTION_DAYS = {'quant': [], 'verbal': []}
for _d in PLAN:
    _c = _d['course']
    for _ch in _c.get('ch', []):
        assert _ch not in CH_DAY, _ch
        CH_DAY[_ch] = _d['day']
    for _u in _c.get('units', []):
        assert _u not in UNIT_DAY, _u
        UNIT_DAY[_u] = _d['day']
    if _c.get('retest'):
        RETEST_DAYS[_d['day']] = list(_c['retest'])
    for _s in _c.get('sections', []):
        SECTION_DAYS[_s].append(_d['day'])
ESSAY_DAYS = [d['day'] for d in PLAN if d['essay']]
MOCK_DAYS = [d['day'] for d in PLAN if d['mock']]


def retest_days(prefix):
    """Retest days for one course: units starting with 'u' are quant, 'v' verbal."""
    return {day: [u for u in us if u.startswith(prefix)] for day, us in RETEST_DAYS.items() if any(u.startswith(prefix) for u in us)}


def topic_label(folder):
    return re.sub(r'\s+', ' ', folder.replace('Adbanced', 'Advanced').replace('Inqualities', 'Inequalities').replace('Arguement', 'Argument'))
