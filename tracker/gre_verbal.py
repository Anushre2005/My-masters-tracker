"""Verbal course: a tutor-style path through GRE verbal, mirroring the quant course (gre_course).

Chapters follow the 100-day plan (text completion → sentence equivalence → reading → critical reasoning).
Each chapter has a short lesson (concept → worked example revealed step by step → "your turn"), a timed
chapter test, and belongs to a unit with a combined test. There are also GRE-timed verbal section
simulations (12 Q / 18 min, then an adaptive 15 Q / 23 min) and a weak-spot drill.

Verbal questions cannot be generated from templates, so this module holds a hand-written bank of original
GRE-style questions. Choices are written with the right answer(s) FIRST (easier to check); they are shuffled
every time a question is served. Tests prefer questions you have not seen yet (`seen` = {question id: times}).

Question kinds: 'mc' (one answer), 'ma' (select all / select two), 'tc' (multi-blank text completion:
c = one column of choices per blank, a = the right index in each column).
"""
import random
import re

from . import gre_plan

QS = []          # every question in the bank
PASSAGES = {}    # passage id -> {'title', 'text', 'qs': [question ids]}
_count = {}


def _add(ch, concept, diff, kind, q, c, a, x, passage=None):
    n = _count[ch] = _count.get(ch, 0) + 1
    item = dict(id=f'{ch}-{n:03d}', chapter=ch, concept=concept, diff=diff, kind=kind, q=q, c=c, a=a, x=x)
    if passage:
        item['pid'] = passage
        PASSAGES[passage]['qs'].append(item['id'])
    QS.append(item)
    return item


def tc1(ch, concept, diff, q, choices, x):
    """One-blank text completion, five choices, right answer first."""
    _add(ch, concept, diff, 'mc', q, list(choices), 0, x)


def tcn(ch, concept, diff, q, cols, x):
    """Two/three-blank text completion: one column of three choices per blank, right answer first in each."""
    _add(ch, concept, diff, 'tc', q, [list(col) for col in cols], [0] * len(cols), x)


def se(concept, diff, q, choices, x):
    """Sentence equivalence: six choices, the first two are the right pair."""
    _add('se', concept, diff, 'ma', q + '\n(Select the TWO answer choices that give sentences alike in meaning.)', list(choices), [0, 1], x)


def cr(ch, concept, diff, q, choices, x):
    _add(ch, concept, diff, 'mc', q, list(choices), 0, x)


def passage(pid, title, text):
    PASSAGES[pid] = {'title': title, 'text': text, 'qs': []}

    def q(concept, diff, question, choices, x, right=1):
        """right = number of correct choices at the front (> 1 makes it a select-all question)."""
        if right > 1 or question.startswith('Consider each'):
            _add('rc', concept, diff, 'ma', question, list(choices), list(range(right)), x, passage=pid)
        else:
            _add('rc', concept, diff, 'mc', question, list(choices), 0, x, passage=pid)
    return q


SELECT_ALL = 'Consider each of the choices separately and select all that apply.\n'

# ====================================================================== text completion: clues
B = 'tc_basic'
tc1(B, 0, 2, 'The documentary was criticized as ______ because it presented only the evidence that supported the director\'s thesis and ignored everything else.',
    ['tendentious', 'exhaustive', 'ambiguous', 'whimsical', 'laconic'], 'Presenting only one side = biased, promoting a point of view: tendentious.')
tc1(B, 1, 1, 'The architect\'s designs are strikingly ______: she uses only straight lines, plain white walls and no ornament of any kind.',
    ['austere', 'ornate', 'eclectic', 'garish', 'baroque'], 'The colon explains the blank: plain, no ornament = austere.')
tc1(B, 2, 1, 'Investors were ______ about the merger, having been burned twice before by deals that looked promising on paper.',
    ['wary', 'sanguine', 'ebullient', 'apathetic', 'credulous'], 'Past bad experience causes caution: wary. Sanguine and ebullient are the opposite; credulous means too trusting.')
tc1(B, 1, 1, 'The senator is known for her ______: she has changed her position on the issue at least four times in two years.',
    ['vacillation', 'steadfastness', 'eloquence', 'reticence', 'probity'], 'Changing position again and again = vacillation (wavering).')
tc1(B, 1, 1, 'The report\'s conclusions were ______; every claim was supported by data from at least three independent sources.',
    ['well-founded', 'speculative', 'tentative', 'spurious', 'specious'], 'The semicolon gives support: every claim backed by data → well-founded.')
tc1(B, 0, 1, 'Hoping to ______ the angry crowd, the mayor promised an immediate investigation into the incident.',
    ['placate', 'incite', 'ignore', 'provoke', 'deride'], 'Promising an investigation is meant to calm people: placate.')
tc1(B, 1, 1, 'The scholar\'s ______ was legendary: she could quote, from memory, long passages from texts in six languages.',
    ['erudition', 'arrogance', 'diffidence', 'ingenuity', 'frivolity'], 'Deep, wide learning = erudition. Ingenuity is cleverness at inventing, not knowledge.')
tc1(B, 1, 2, 'Long exposure to the region\'s harsh winters had made the villagers ______; they shrugged off storms that would have alarmed visitors.',
    ['inured', 'susceptible', 'vulnerable', 'oblivious', 'sensitive'], 'Shrugging off hardship because you are used to it = inured. Oblivious means unaware, but they are aware - just unbothered.')
tc1(B, 1, 2, 'The company\'s statement was deliberately ______, worded so vaguely that it could be read as either an apology or a denial.',
    ['equivocal', 'forthright', 'emphatic', 'contrite', 'categorical'], 'Open to two readings on purpose = equivocal.')
tc1(B, 2, 2, 'Because the drug\'s side effects were ______ — appearing only after years of use — they went undetected in the short original trials.',
    ['latent', 'acute', 'conspicuous', 'immediate', 'benign'], 'Present but hidden until later = latent. "Because" links the hidden effects to their going undetected.')
tc1(B, 2, 1, 'The critic\'s review was so ______ that the author, stung, refused to give interviews for a year.',
    ['scathing', 'laudatory', 'tepid', 'equivocal', 'perfunctory'], '"So … that the author, stung" - a cause strong enough to hurt: scathing (harshly critical).')
tc1(B, 2, 1, 'Given the region\'s ______ rainfall, farmers there have long relied on elaborate irrigation systems.',
    ['scant', 'copious', 'torrential', 'predictable', 'refreshing'], 'Needing irrigation means there is little rain: scant.')
tc1(B, 0, 2, 'Her apology seemed ______ rather than heartfelt: she recited it quickly, without once looking at the people she had offended.',
    ['perfunctory', 'sincere', 'effusive', 'contrite', 'abject'], 'Done quickly, as a formality, not from the heart = perfunctory.')
tc1(B, 1, 1, 'The young composer\'s work is remarkably ______; it borrows freely from jazz, medieval chant and West African drumming.',
    ['eclectic', 'austere', 'monotonous', 'insular', 'conventional'], 'Drawing on many different sources = eclectic.')
tc1(B, 2, 1, 'Anyone who expected the famously ______ CEO to make a long speech was not disappointed: he spoke for nearly two hours.',
    ['loquacious', 'taciturn', 'laconic', 'reserved', 'terse'], 'The expectation was met - a long speech - so he is known for talking a lot: loquacious.')
tc1(B, 2, 1, 'The evidence against the theory has become so ______ that even its most loyal defenders have begun to abandon it.',
    ['overwhelming', 'flimsy', 'ambiguous', 'anecdotal', 'sparse'], 'Strong enough to make loyal defenders give up = overwhelming.')
tc1(B, 1, 2, 'The museum\'s new director is a ______ of modern art, having spent forty years collecting, studying and writing about it.',
    ['connoisseur', 'detractor', 'novice', 'dilettante', 'skeptic'], 'Forty years of expert study = connoisseur. A dilettante only dabbles.')
tc1(B, 2, 1, 'The mountain road was so ______ that drivers unfamiliar with it were advised to travel only in daylight.',
    ['treacherous', 'scenic', 'straight', 'well-lit', 'congested'], 'The warning to drive only in daylight implies danger: treacherous.')
tc1(B, 1, 1, 'The professor\'s comments on student essays were famously ______; a typical response consisted of a single word, such as "No" or "Why?"',
    ['terse', 'verbose', 'effusive', 'meandering', 'encouraging'], 'One-word comments = terse.')
tc1(B, 0, 1, 'The politician\'s ______ was exposed when reporters discovered that he privately opposed the very policies he publicly championed.',
    ['duplicity', 'candor', 'integrity', 'consistency', 'modesty'], 'Saying one thing in public and another in private = duplicity (deceitfulness).')
tc1(B, 2, 2, 'The ______ of reliable data from the region means that any estimate of its population must be treated as little more than an educated guess.',
    ['paucity', 'abundance', 'accuracy', 'reliability', 'publication'], 'Estimates are guesses because there is little data: paucity (scarcity).')
tc1(B, 1, 2, 'The once-thriving port has become ______: its warehouses stand empty and only a handful of ships call there each year.',
    ['moribund', 'bustling', 'prosperous', 'cosmopolitan', 'renovated'], 'Empty and nearly dead = moribund.')
tc1(B, 1, 2, 'The candidate\'s speech was full of ______, offering grand-sounding phrases but no concrete proposals.',
    ['platitudes', 'specifics', 'statistics', 'insights', 'contradictions'], 'Grand-sounding but empty phrases = platitudes.')
tc1(B, 2, 2, 'Scientists remain ______ about the new findings, noting that the experiment has not yet been replicated by an independent laboratory.',
    ['guarded', 'ecstatic', 'dismissive', 'certain', 'indifferent'], 'Not yet replicated → cautious: guarded. "Dismissive" is too strong - they are waiting, not rejecting.')
tc1(B, 1, 3, 'Her prose is so ______ that readers often need several passes to untangle a single sentence.',
    ['convoluted', 'limpid', 'pellucid', 'terse', 'pedestrian'], 'Needing to "untangle" = convoluted. Limpid and pellucid mean clear - the opposite.')
tc1(B, 0, 2, 'The diplomat\'s remarks were so ______ that observers could not tell whether she supported the proposal or merely refrained from condemning it.',
    ['noncommittal', 'vehement', 'partisan', 'strident', 'unequivocal'], 'Impossible to tell her position = noncommittal.')
tc1(B, 0, 3, 'The critic praised the novel\'s ______, noting that in three hundred pages it never wastes a word.',
    ['economy', 'prolixity', 'opulence', 'digressiveness', 'sentimentality'], 'Secondary meaning: "economy" of style = efficient use of words. Prolixity is the opposite.')
tc1(B, 0, 1, 'Regulators moved quickly to ______ the practice, which they regarded as a serious threat to consumers.',
    ['curb', 'abet', 'foster', 'condone', 'publicize'], 'A threat is something to restrain: curb. Abet, foster and condone all support it.')

# ====================================================================== text completion: shifts
S = 'tc_shift'
tc1(S, 0, 1, 'Although the critic was generally ______ new directors, she reserved unqualified praise for this debut film.',
    ['dismissive of', 'enamored of', 'supportive of', 'lenient toward', 'fascinated by'], '"Although" signals a contrast with "unqualified praise", so the blank is negative: dismissive of.')
tc1(S, 0, 1, 'Despite his reputation for ______, the senator delivered a speech that was remarkably concise.',
    ['verbosity', 'brevity', 'honesty', 'reticence', 'wit'], '"Despite" + "concise" → the reputation is the opposite of concise: verbosity.')
tc1(S, 0, 1, 'Rather than ______ the controversy, the spokesperson\'s statement only intensified it.',
    ['defusing', 'inflaming', 'prolonging', 'publicizing', 'exacerbating'], '"Rather than … only intensified" → the blank is the opposite of intensify: defusing.')
tc1(S, 2, 2, 'Her ______ demeanor in public belied a fierce competitiveness that only her teammates ever saw.',
    ['placid', 'combative', 'aggressive', 'intense', 'belligerent'], '"Belied" = gave a false impression of. The calm public face hid the competitiveness: placid.')
tc1(S, 0, 1, 'Although the novel was a commercial failure when it was published, it is now considered a ______ of the genre.',
    ['landmark', 'travesty', 'footnote', 'parody', 'failure'], '"Although … failure" → now it is seen as the opposite: a landmark.')
tc1(S, 0, 2, 'The athlete\'s public persona is brash and ______, but those who know her describe a thoughtful, even shy, person.',
    ['swaggering', 'diffident', 'reticent', 'introspective', 'timid'], 'The blank goes WITH "brash" (same side of the "but"): swaggering. The other choices describe the private person.')
tc1(S, 0, 1, 'Despite its ______ appearance, the tiny frog secretes a toxin powerful enough to kill a predator many times its size.',
    ['innocuous', 'venomous', 'menacing', 'conspicuous', 'intimidating'], '"Despite" + deadly toxin → it looks harmless: innocuous.')
tc1(S, 0, 1, 'While her early paintings were ______, filled with bright colours and playful figures, her later work grew increasingly somber.',
    ['exuberant', 'melancholy', 'austere', 'muted', 'sinister'], 'Bright and playful (and contrasted with somber) = exuberant.')
tc1(S, 0, 1, 'The CEO\'s optimism was not shared by analysts, who called the company\'s growth projections ______.',
    ['unrealistic', 'prudent', 'modest', 'conservative', 'attainable'], 'Analysts did not share the optimism → they doubted the projections: unrealistic.')
tc1(S, 0, 2, 'Though generally ______, the reviewer made an exception for the film\'s cinematography, which she called flawless.',
    ['censorious', 'laudatory', 'effusive', 'enthusiastic', 'admiring'], 'The exception is praise, so in general she was critical: censorious.')
tc1(S, 1, 1, 'The scientist\'s findings, initially greeted with ______, were eventually accepted as the field\'s new orthodoxy.',
    ['skepticism', 'acclaim', 'deference', 'enthusiasm', 'reverence'], '"Initially … eventually accepted" is a time shift: at first they were doubted.')
tc1(S, 1, 1, 'Once considered a ______ pursuit for wealthy amateurs, astronomy is now a highly technical field dominated by professional scientists.',
    ['leisurely', 'rigorous', 'lucrative', 'specialized', 'technical'], '"Once … now highly technical" → in the past it was the opposite: a leisurely hobby.')
tc1(S, 1, 2, 'Surprisingly, the medication proved most ______ in the patients doctors had expected it to help least.',
    ['efficacious', 'harmful', 'dangerous', 'unpredictable', 'ineffective'], '"Surprisingly" + "expected to help least" → it helped them most: efficacious.')
tc1(S, 1, 2, 'The startup\'s founders, at first ______ about their chances, grew steadily more confident as orders poured in.',
    ['diffident', 'sanguine', 'cocksure', 'complacent', 'buoyant'], '"At first … grew more confident" → they began unsure: diffident.')
tc1(S, 1, 1, 'What began as a ______ disagreement over a parking space eventually escalated into a lawsuit that lasted six years.',
    ['trivial', 'momentous', 'bitter', 'violent', 'protracted'], '"Began as … escalated" → it started small: trivial.')
tc1(S, 1, 1, 'Contrary to the predictions of her doubters, the inexperienced coach led the team to its most ______ season in decades.',
    ['triumphant', 'dismal', 'mediocre', 'uneventful', 'forgettable'], 'Doubters predicted failure; "contrary to" → great success: triumphant.')
tc1(S, 2, 1, 'The proposal is not without ______: several of its provisions would genuinely help small businesses.',
    ['merit', 'flaws', 'critics', 'precedent', 'cost'], '"Not without merit" = it has merit. The colon supports it with helpful provisions.')
tc1(S, 2, 2, 'Far from being ______, the senator\'s retirement had been planned for years and announced to her staff long in advance.',
    ['abrupt', 'deliberate', 'anticipated', 'gradual', 'voluntary'], '"Far from" negates the blank: planned for years → NOT abrupt.')
tc1(S, 2, 2, 'Hardly ______, the professor graded so severely that few students earned higher than a C.',
    ['indulgent', 'exacting', 'rigorous', 'demanding', 'harsh'], '"Hardly" negates: severe grading → hardly indulgent (lenient).')
tc1(S, 2, 3, 'Critics who dismissed the theory as mere speculation have been ______ by a decade of confirming experiments.',
    ['confounded', 'vindicated', 'emboldened', 'corroborated', 'flattered'], 'The theory was confirmed, so the critics were proved wrong: confounded. Vindicated would apply to the theory\'s supporters.')
tc1(S, 2, 2, 'The author\'s reputation for ______ is belied by the warmth of her private letters, which are full of affection and humour.',
    ['aloofness', 'geniality', 'warmth', 'wit', 'generosity'], '"Belied by the warmth" → the reputation is the opposite of warm: aloofness.')
tc1(S, 1, 2, 'It is ______ that a scientist so famous for caution should have staked her reputation on such a speculative claim.',
    ['ironic', 'predictable', 'inevitable', 'fitting', 'unsurprising'], 'A cautious person taking a big gamble is the opposite of what you expect: ironic.')
tc1(S, 0, 1, 'Rather than ______ his rivals, the champion praised their skill and credited his win partly to luck.',
    ['disparaging', 'lauding', 'emulating', 'thanking', 'applauding'], '"Rather than" + praised → the opposite of praise: disparaging.')
tc1(S, 2, 3, 'That the treaty survived at all is a testament less to the goodwill of its signatories than to their mutual ______: neither side could afford the cost of abandoning it.',
    ['dependence', 'generosity', 'trust', 'enthusiasm', 'idealism'], '"Less to goodwill than to …" contrasts with goodwill; the colon explains: neither could afford to leave → dependence.')

# ====================================================================== text completion: two blanks
D = 'tc_double'
tcn(D, 0, 1, 'Critics predicted the museum\'s new wing would be a (i)______ intrusion on the historic district, yet most residents now regard it as a (ii)______ addition.',
    [['jarring', 'harmonious', 'subtle'], ['welcome', 'discordant', 'superfluous']], '"Intrusion" is negative, so (i) = jarring. "Yet" flips it: (ii) = welcome.')
tcn(D, 0, 1, 'Though the treaty was hailed as a (i)______ achievement at the time, historians now view its provisions as largely (ii)______, since few were ever enforced.',
    [['landmark', 'minor', 'trivial'], ['toothless', 'binding', 'stringent']], '"Hailed" → (i) positive: landmark. "Few were ever enforced" → (ii) toothless.')
tcn(D, 1, 1, 'The author\'s early essays were (i)______, crammed with digressions and obscure allusions; her later work, by contrast, is a model of (ii)______.',
    [['convoluted', 'lucid', 'concise'], ['clarity', 'obscurity', 'prolixity']], 'Digressions and obscure allusions → convoluted. "By contrast" → the later work is clear.')
tcn(D, 1, 2, 'Far from being (i)______, the reclusive composer kept up a (ii)______ correspondence with dozens of musicians across Europe.',
    [['isolated', 'gregarious', 'prolific'], ['voluminous', 'sparse', 'sporadic']], '"Far from" negates (i): despite his reclusiveness he was not cut off (isolated). Dozens of musicians → a voluminous correspondence.')
tcn(D, 1, 1, 'The scientist\'s (i)______ manner in the lab — she double-checked every measurement — contrasted sharply with her (ii)______ approach to paperwork, which piled up unread for months.',
    [['meticulous', 'slapdash', 'hasty'], ['cavalier', 'scrupulous', 'methodical']], 'Double-checking → meticulous. "Contrasted sharply" + piles of unread paperwork → cavalier (careless).')
tcn(D, 1, 1, 'Although the novel\'s plot is (i)______, its characters are so (ii)______ that readers hardly notice the lack of suspense.',
    [['predictable', 'gripping', 'intricate'], ['compelling', 'flat', 'forgettable']], '"Lack of suspense" → the plot is predictable. "Although" → the characters make up for it: compelling.')
tcn(D, 1, 2, 'The governor\'s critics accused her of (i)______, arguing that her sudden support for the bill was motivated less by conviction than by a desire to (ii)______ voters before the election.',
    [['opportunism', 'idealism', 'consistency'], ['court', 'alienate', 'ignore']], 'Acting from self-interest rather than conviction = opportunism; the aim is to win voters over: court.')
tcn(D, 0, 1, 'Initially (i)______ by the difficulty of the material, the students eventually grew (ii)______, tackling even the hardest problems with confidence.',
    [['daunted', 'bored', 'amused'], ['self-assured', 'timid', 'apathetic']], '"Initially … eventually … with confidence": at first daunted, later self-assured.')
tcn(D, 1, 1, 'The region\'s economy, long (i)______ a single crop, proved (ii)______ when a blight wiped out the harvest.',
    [['reliant on', 'diversified beyond', 'indifferent to'], ['fragile', 'resilient', 'robust']], 'Losing one crop hurt because the economy depended on it: reliant on → fragile.')
tcn(D, 1, 2, 'Though (i)______ in person — he seldom raised his voice or offered an opinion — the essayist was (ii)______ on the page, attacking his opponents with relish.',
    [['mild-mannered', 'combative', 'garrulous'], ['pugnacious', 'diffident', 'reticent']], 'The dashes define (i): quiet, mild-mannered. "Though" + attacking with relish → (ii) pugnacious (eager to fight).')
tcn(D, 1, 2, 'The committee\'s decision to (i)______ the old rules surprised no one; the rules had long been regarded as (ii)______, more a source of confusion than of guidance.',
    [['scrap', 'enshrine', 'strengthen'], ['obsolete', 'indispensable', 'sacrosanct']], 'Rules that confuse are outdated (obsolete), so getting rid of them (scrap) surprised no one.')
tcn(D, 0, 2, 'Her argument, (i)______ on first reading, collapses under scrutiny: its central statistic turns out to be (ii)______.',
    [['persuasive', 'absurd', 'opaque'], ['spurious', 'well documented', 'conservative']], '"Collapses under scrutiny" implies it seemed good at first: persuasive. It collapses because the statistic is false: spurious.')
tcn(D, 1, 2, 'The tribe\'s customs, which outsiders often dismissed as (i)______, in fact reflected a (ii)______ understanding of the local ecosystem.',
    [['primitive', 'sophisticated', 'enlightened'], ['nuanced', 'superficial', 'rudimentary']], '"Dismissed as" → negative: primitive. "In fact" reverses it: a nuanced understanding.')
tcn(D, 1, 2, 'Rather than (i)______ the problem, the new policy merely (ii)______ it, shifting the costs from one agency to another.',
    [['solving', 'worsening', 'publicizing'], ['displaced', 'eliminated', 'resolved']], 'Shifting costs elsewhere = moving the problem (displaced) rather than solving it.')
tcn(D, 0, 2, 'Critics found the film\'s ending (i)______: after two hours of careful buildup, the central mystery is resolved by a (ii)______ coincidence.',
    [['unsatisfying', 'inevitable', 'triumphant'], ['contrived', 'plausible', 'subtle']], 'Resolving a mystery by an artificial coincidence after careful buildup is unsatisfying; the coincidence is contrived.')
tcn(D, 1, 2, 'The economist\'s forecasts have proved so (i)______ that even her rivals now treat her pronouncements as (ii)______.',
    [['prescient', 'erratic', 'timid'], ['authoritative', 'suspect', 'frivolous']], '"Even her rivals" respect her → her forecasts were accurate (prescient) and her words are authoritative.')
tcn(D, 1, 3, 'The historian\'s account is (i)______ rather than comprehensive, but its very selectivity is (ii)______: by focusing on a single village she illuminates forces that broader surveys tend to obscure.',
    [['partial', 'exhaustive', 'encyclopedic'], ['a virtue', 'a liability', 'an accident']], '"Rather than comprehensive" → partial. "But" + "illuminates" → the selectivity is a virtue.')
tcn(D, 1, 3, 'Given how (i)______ the evidence is, the panel\'s confident conclusion seems less a finding than a (ii)______.',
    [['equivocal', 'unambiguous', 'voluminous'], ['leap of faith', 'logical necessity', 'modest inference']], 'A confident conclusion that is "less a finding" → the evidence is unclear (equivocal), so the conclusion is a leap of faith.')
tcn(D, 0, 3, 'Not one to (i)______ her views, the activist was (ii)______ in her criticism, even when tact might have served her cause better.',
    [['temper', 'broadcast', 'exaggerate'], ['unsparing', 'measured', 'hesitant']], 'Secondary meaning: temper = soften. She did not soften her views, so her criticism was unsparing.')
tcn(D, 1, 3, 'What the reviewer praised as the play\'s (i)______ struck many audience members as mere (ii)______: the dialogue was so sparse that the actors spent long stretches in silence.',
    [['restraint', 'exuberance', 'verbosity'], ['emptiness', 'extravagance', 'garrulity']], 'Sparse dialogue: praised as restraint, but others saw it as emptiness.')

# ====================================================================== text completion: three blanks
T = 'tc_triple'
tcn(T, 0, 3, 'The committee\'s report was anything but (i)______: rather than (ii)______ the agency\'s failures, it (iii)______ them in exhaustive detail.',
    [['evasive', 'candid', 'thorough'], ['gloss over', 'catalogue', 'exaggerate'], ['documented', 'concealed', 'ignored']],
    '"Exhaustive detail" anchors (iii): documented. "Rather than" → (ii) the opposite: gloss over. "Anything but" → (i) evasive.')
tcn(T, 1, 2, 'Early reviewers found the symphony\'s dissonances merely (i)______, but later listeners, having grown (ii)______ to its idiom, came to regard those same passages as its most (iii)______ moments.',
    [['grating', 'soothing', 'novel'], ['accustomed', 'hostile', 'indifferent'], ['arresting', 'tedious', 'forgettable']],
    '"Merely" + dissonances → grating. "But later" → listeners got used to it (accustomed) and found those passages striking (arresting).')
tcn(T, 1, 2, 'Because the founder was usually (i)______ about risk, investors were surprised when she (ii)______ the company\'s entire reserve on an untested product — a gamble that, to the (iii)______ of her critics, paid off handsomely.',
    [['cautious', 'cavalier', 'reckless'], ['staked', 'hoarded', 'withheld'], ['chagrin', 'delight', 'relief']],
    'The surprise means the gamble was out of character → cautious. Gambling the reserve → staked. Critics are annoyed when it works → chagrin.')
tcn(T, 0, 2, 'For most of the twentieth century, the island\'s isolation kept its culture largely (i)______. That changed abruptly when an airport opened in 1985: within a decade, tourism had (ii)______ the local economy, and many residents worried that their traditions were becoming little more than a (iii)______ for visitors.',
    [['intact', 'diluted', 'cosmopolitan'], ['transformed', 'stabilized', 'abandoned'], ['performance', 'mystery', 'burden']],
    'Isolation preserved the culture (intact). "Changed abruptly" → tourism transformed the economy; traditions put on for tourists become a performance.')
tcn(T, 0, 3, 'The biography\'s portrait of the inventor is anything but (i)______. Rather than presenting him as a (ii)______ genius, the author documents his many failures, his (iii)______ to credit collaborators, and his habit of claiming others\' ideas as his own.',
    [['hagiographic', 'unflattering', 'scathing'], ['flawless', 'flawed', 'struggling'], ['reluctance', 'eagerness', 'readiness']],
    'The book exposes faults, so it is not hagiographic (worshipful). It refuses to show a flawless genius, and he was reluctant to credit others.')
tcn(T, 1, 2, 'Researchers had assumed the drug\'s benefits would be (i)______, confined to the few patients with the rare mutation it targets. The trial results were therefore (ii)______: patients without the mutation improved nearly as much, a finding that, if (iii)______ by further studies, could greatly widen the drug\'s use.',
    [['narrow', 'sweeping', 'negligible'], ['startling', 'predictable', 'disappointing'], ['borne out', 'refuted', 'ignored']],
    '"Confined to the few" defines (i): narrow. Benefits for everyone contradict the assumption → startling. Wider use needs the finding confirmed → borne out.')
tcn(T, 1, 2, 'The mayor\'s (i)______ style — she preferred quiet negotiation to public confrontation — was often mistaken for (ii)______. In fact, she was (iii)______ in pursuing her goals, simply unwilling to waste energy on theatrics.',
    [['understated', 'flamboyant', 'combative'], ['weakness', 'aggression', 'arrogance'], ['relentless', 'half-hearted', 'erratic']],
    'The dashes define (i): quiet → understated. Quietness gets mistaken for weakness; "in fact" reverses that → relentless.')
tcn(T, 0, 2, 'Although the theory\'s early proponents were (i)______ by the scientific establishment, their ideas were eventually (ii)______, and today it is the skeptics who seem (iii)______.',
    [['ridiculed', 'celebrated', 'funded'], ['vindicated', 'discredited', 'forgotten'], ['misguided', 'prescient', 'triumphant']],
    '"Although … eventually" → first ridiculed, then vindicated; now the tables have turned and the skeptics look misguided.')
tcn(T, 1, 2, 'Few writers have been as (i)______ as Dickens, who produced fifteen novels along with countless stories and essays; yet his output was not merely (ii)______, for many critics consider his work (iii)______ in its depth as well as its breadth.',
    [['prolific', 'meticulous', 'reclusive'], ['voluminous', 'slight', 'uneven'], ['unrivalled', 'deficient', 'conventional']],
    'Fifteen novels and more → prolific. "Not merely" large (voluminous) → it was also excellent: unrivalled in depth.')
tcn(T, 0, 1, 'Her critics charge that the policy is (i)______, pointing to costs that have (ii)______ while benefits have remained (iii)______.',
    [['wasteful', 'prudent', 'innovative'], ['ballooned', 'shrunk', 'stabilized'], ['elusive', 'substantial', 'obvious']],
    'Critics attack it: wasteful. Evidence for waste: costs ballooned while benefits stayed elusive.')
tcn(T, 1, 3, 'The negotiator\'s reputation for (i)______ was well deserved: she never conceded a point without extracting something in return, and her opponents learned to treat her opening offers as (ii)______ rather than final. Yet she was also (iii)______, and the deals she struck rarely unravelled.',
    [['shrewdness', 'generosity', 'naivety'], ['provisional', 'sincere', 'insulting'], ['trustworthy', 'capricious', 'devious']],
    'Always getting something back = shrewdness; opening offers are just a starting point (provisional). "Yet" + deals that hold → trustworthy.')
tcn(T, 0, 3, 'The study\'s authors are careful to (i)______ their conclusions, acknowledging that the sample was small and the effect (ii)______; journalists covering the study, however, showed no such (iii)______.',
    [['qualify', 'overstate', 'publicize'], ['modest', 'dramatic', 'unprecedented'], ['restraint', 'enthusiasm', 'ignorance']],
    'Acknowledging limits = qualifying conclusions; the effect was modest. "However" → the journalists lacked that restraint.')

# ====================================================================== sentence equivalence
se(0, 1, 'The witness\'s account was so ______ that the detectives could not determine what had actually happened.',
   ['muddled', 'confused', 'lucid', 'consistent', 'detailed', 'brief'], 'The detectives could not work it out → the account was unclear: muddled / confused.')
se(0, 1, 'Known for her ______, the diplomat rarely revealed her own opinions during negotiations.',
   ['reticence', 'reserve', 'garrulousness', 'candor', 'impatience', 'enthusiasm'], 'Rarely revealing opinions = reticence / reserve.')
se(0, 2, 'The once-______ industry has dwindled to a handful of small workshops.',
   ['flourishing', 'thriving', 'moribund', 'declining', 'nascent', 'obscure'], '"Once-" + "dwindled" → it used to be big: flourishing / thriving. Moribund and declining describe it now, not then.')
se(0, 1, 'His ______ remarks offended many at the dinner, though he insisted he had meant no harm.',
   ['gauche', 'tactless', 'tactful', 'diplomatic', 'witty', 'prudent'], 'Offensive without meaning harm → socially clumsy: gauche / tactless.')
se(1, 2, 'The evidence for the theory, though suggestive, remains ______.',
   ['tentative', 'provisional', 'conclusive', 'decisive', 'abundant', 'irrefutable'], '"Though suggestive" → not yet settled: tentative / provisional. Trap: conclusive / decisive match each other but reverse the meaning.')
se(0, 1, 'The senator\'s ______ remarks, delivered without notes, surprised aides who had expected a carefully scripted speech.',
   ['extemporaneous', 'impromptu', 'rehearsed', 'lengthy', 'banal', 'incendiary'], 'Without notes, unscripted = extemporaneous / impromptu.')
se(0, 1, 'Though the company\'s profits were ______, its stock price fell because investors had expected even more.',
   ['robust', 'healthy', 'meager', 'declining', 'unreported', 'surprising'], '"Though … expected even more" → profits were good: robust / healthy.')
se(0, 1, 'The professor was ______ about deadlines, refusing to accept even a paper submitted one minute late.',
   ['inflexible', 'unbending', 'lenient', 'casual', 'vague', 'forgetful'], 'No exceptions at all = inflexible / unbending.')
se(0, 1, 'Many early readers found the poem ______, its allusions so obscure that only specialists could follow them.',
   ['impenetrable', 'abstruse', 'lucid', 'sentimental', 'transparent', 'simplistic'], 'Too obscure to follow = impenetrable / abstruse.')
se(0, 1, 'The rescue team\'s ______ efforts, continuing through three nights without rest, saved all twelve miners.',
   ['tireless', 'indefatigable', 'sporadic', 'halfhearted', 'futile', 'belated'], 'Three nights without rest = tireless / indefatigable.')
se(1, 2, 'The CEO\'s optimism seemed ______ to analysts, who pointed out that sales had fallen for six straight quarters.',
   ['unwarranted', 'unjustified', 'prudent', 'sensible', 'contagious', 'infectious'], 'Falling sales make optimism unjustified: unwarranted / unjustified. Two trap pairs (prudent/sensible, contagious/infectious) are synonyms that do not fit.')
se(1, 2, 'Rather than ______ the crisis, the official\'s comments only made it worse.',
   ['alleviating', 'mitigating', 'exacerbating', 'aggravating', 'explaining', 'describing'], '"Rather than … made it worse" → the opposite of worsening: alleviating / mitigating. Exacerbating / aggravating is the trap pair.')
se(1, 2, 'The author\'s ______ style — long sentences, rare words and endless digressions — tests the patience of even devoted readers.',
   ['ornate', 'baroque', 'spare', 'austere', 'conversational', 'colloquial'], 'Elaborate and over-decorated = ornate / baroque. Spare / austere is the opposite pair.')
se(2, 3, 'The new evidence did little to ______ the scientist\'s confidence; if anything, she became more certain of her hypothesis.',
   ['temper', 'moderate', 'bolster', 'reinforce', 'display', 'publicize'], '"Did little to …; if anything, more certain" → the evidence did not reduce her confidence: temper / moderate (secondary meaning of temper). Bolster / reinforce reverses the logic.')
se(2, 3, 'The diplomat was careful to ______ her criticisms, praising the agreement\'s goals before questioning its methods.',
   ['qualify', 'hedge', 'trumpet', 'broadcast', 'abandon', 'publish'], 'Softening criticism with reservations and praise = qualify / hedge (secondary meanings).')
se(0, 1, 'The townspeople were ______ by the bridge collapse, which killed four people and cut the town off from the highway for months.',
   ['devastated', 'shattered', 'unmoved', 'untroubled', 'enriched', 'inspired'], 'Deaths and months of isolation → devastated / shattered.')
se(1, 2, 'Far from being ______, the treatment requires months of careful follow-up.',
   ['simple', 'uncomplicated', 'arduous', 'demanding', 'costly', 'expensive'], '"Far from being" + months of follow-up → it is not simple / uncomplicated. Arduous / demanding is the trap: it describes the treatment but the "far from" flips it.')
se(0, 1, 'The candidate\'s positions were so ______ that voters could not tell what she actually believed.',
   ['nebulous', 'vague', 'explicit', 'detailed', 'consistent', 'radical'], 'Unclear positions = nebulous / vague.')
se(2, 3, 'The essayist\'s wit is ______: she wounds her targets so deftly that they sometimes do not realise they have been insulted until hours later.',
   ['oblique', 'indirect', 'blunt', 'crude', 'flamboyant', 'exuberant'], 'Insults so subtle they are noticed later = oblique / indirect. Blunt / crude is the opposite pair.')
se(1, 2, 'Despite the team\'s ______ start to the season — it lost its first five games — it went on to win the championship.',
   ['inauspicious', 'unpromising', 'auspicious', 'promising', 'triumphant', 'uneventful'], 'Losing five games = inauspicious / unpromising. Auspicious / promising is the reversed trap pair.')
se(1, 1, 'Critics dismissed the film as ______, a lazy imitation of better movies in the same genre.',
   ['derivative', 'unoriginal', 'innovative', 'groundbreaking', 'controversial', 'provocative'], 'Imitation = derivative / unoriginal.')
se(2, 3, 'The committee\'s approval was merely ______: it rubber-stamped every proposal put before it without discussion.',
   ['perfunctory', 'pro forma', 'deliberative', 'considered', 'enthusiastic', 'unanimous'], 'Done as a formality = perfunctory / pro forma.')
se(0, 1, 'Her ______ for spotting tiny errors made her an excellent proofreader.',
   ['knack', 'flair', 'disdain', 'contempt', 'need', 'demand'], 'A natural talent = knack / flair.')
se(1, 2, 'Though he was ______ in company, the philosopher\'s letters reveal a warm and voluble correspondent.',
   ['taciturn', 'reticent', 'loquacious', 'garrulous', 'cheerful', 'jovial'], '"Though" + voluble (talkative) letters → in company he was quiet: taciturn / reticent.')

# ====================================================================== reading comprehension (passages)
q = passage('heat', 'Urban heat islands',
            'Urban "heat islands" — cities markedly warmer than their surroundings — are usually blamed on building materials: asphalt and concrete absorb sunlight by day and release it slowly at night. Recent studies suggest this explanation is incomplete. In humid regions, the loss of vegetation matters as much as the presence of pavement, because plants cool the air through evapotranspiration, which pavement cannot replicate. In arid regions, by contrast, cities are sometimes cooler during the day than the surrounding desert, since irrigated parks and trees supply shade and moisture the desert lacks. Strategies for cooling cities therefore cannot be uniform: reflective roofs may suffice in some climates, while in others restoring greenery will be essential.')
q(0, 1, 'The primary purpose of the passage is to',
  ['show that a common explanation is incomplete and that cooling strategies should depend on climate', 'argue that reflective roofs are ineffective', 'describe the chemistry of evapotranspiration',
   'compare the populations of humid and arid cities', 'deny that heat islands exist'],
  'The passage calls the usual explanation "incomplete" and concludes strategies "cannot be uniform". The others are too narrow, off-topic or too extreme.')
q(1, 1, 'According to the passage, some cities in arid regions are cooler than the surrounding desert during the day because',
  ['irrigated vegetation provides shade and moisture', 'their pavement reflects sunlight', 'they have fewer buildings', 'evapotranspiration is impossible in deserts', 'reflective roofs are common there'],
  'Detail question: "irrigated parks and trees supply shade and moisture the desert lacks." Find the line before answering.')
q(2, 2, 'The author would most likely agree that',
  ['restoring vegetation may be important for cooling humid cities', 'all cities should adopt the same cooling strategy', 'pavement plays no role in heat islands',
   'desert cities are always cooler than deserts', 'reflective roofs never help'],
  'Supported by "in humid regions, the loss of vegetation matters…". The wrong choices use extreme words (all, no, always, never).')
q(3, 2, SELECT_ALL + 'Which of the following does the passage present as factors that can affect how warm a city is?',
  ['the materials used to build it', 'the amount of vegetation it has', 'the size of its population'],
  'Building materials (first sentence) and vegetation (humid and arid examples) are both discussed. Population is never mentioned.', right=2)

q = passage('letters', 'Merchants\' letters',
            'For decades, historians treated the letters of eighteenth-century merchants as reliable records of trade, assuming that people writing to business partners had little reason to misrepresent their dealings. A closer reading complicates this view. Merchants often wrote with an eye to their reputations, knowing that letters were frequently shared among associates; a merchant facing losses might describe a failed venture as a temporary delay. Such letters remain valuable, but less as ledgers than as evidence of how merchants wished to be seen.')
q(2, 2, 'The author suggests that the earlier view of merchants\' letters',
  ['overlooked how concern for reputation shaped what merchants wrote', 'was correct about the letters\' accuracy', 'relied on too few letters', 'ignored the letters entirely', 'was invented to protect merchants'],
  'The "closer reading" shows merchants wrote "with an eye to their reputations" - the factor the earlier view missed.')
q(2, 1, 'The author\'s attitude toward the letters as historical sources is best described as',
  ['qualified appreciation', 'dismissive', 'uncritical enthusiasm', 'indifference', 'outright hostility'],
  '"Such letters remain valuable, but…" - positive with a reservation = qualified appreciation.')
q(3, 2, 'The example of the "temporary delay" serves mainly to',
  ['illustrate how a merchant might misrepresent an outcome to protect his reputation', 'prove that all merchants lied', 'show that trade was slow in the eighteenth century',
   'explain why letters were shared', 'argue that the letters are worthless'],
  'It is a concrete illustration of the claim just before it. Function questions ask "why is this here?".')

q = passage('coral', 'Coral bleaching',
            'When water temperatures rise even briefly above their normal summer maximum, many reef-building corals expel the symbiotic algae that live in their tissues and supply most of their energy. Without the algae, the corals turn white — the phenomenon known as bleaching — and, if conditions do not improve within weeks, they starve. Researchers long assumed that a coral\'s tolerance of heat was fixed by its species. Recent work suggests otherwise: corals from reefs that regularly experience brief temperature spikes bleach less readily than genetically similar corals from more stable waters, apparently because repeated mild stress primes them to cope with severe stress. This finding has encouraged proposals to "train" corals in nurseries before planting them on damaged reefs. Skeptics caution, however, that such conditioning may not survive the steady warming now under way, which differs in kind from the short spikes to which the conditioned corals had adapted.')
q(0, 2, 'The primary purpose of the passage is to',
  ['describe a finding about coral heat tolerance and note a reservation about a proposal it has inspired', 'argue that bleaching is no longer a threat to reefs',
   'explain why algae leave coral tissue', 'refute the skeptics who doubt coral training', 'compare the heat tolerance of different coral species'],
  'The passage reports the finding (tolerance is not fixed by species), the proposal it inspired, and the skeptics\' caution. It does not take sides against the skeptics.')
q(1, 1, 'According to the passage, bleached corals may starve because they',
  ['have lost the algae that supplied most of their energy', 'can no longer absorb sunlight', 'are attacked by other species', 'stop growing new tissue', 'are moved to nurseries'],
  '"Expel the symbiotic algae that … supply most of their energy … they starve."')
q(2, 2, 'The skeptics mentioned in the passage would most likely agree that',
  ['conditioning corals against brief spikes may not protect them from long-term warming', 'nursery corals should never be planted on reefs', 'corals cannot adapt to heat at all',
   'brief temperature spikes are more harmful than steady warming', 'the original research was flawed'],
  'They worry the conditioning "may not survive the steady warming … which differs in kind from the short spikes".')
q(2, 3, SELECT_ALL + 'Which of the following can be inferred from the passage?',
  ['A coral\'s heat tolerance is not determined solely by its species.', 'Corals that have experienced mild heat stress may withstand severe stress better.', 'Nursery-trained corals have already restored several damaged reefs.'],
  'The first two follow from "recent work suggests otherwise" and "repeated mild stress primes them". The third is never stated - training is only proposed.', right=2)
q(3, 3, 'The phrase "differs in kind" primarily serves to',
  ['emphasize that steady warming is a different challenge from the stresses the corals adapted to', 'suggest that steady warming is milder than temperature spikes',
   'explain how bleaching occurs', 'introduce a new type of coral', 'concede that the proposal will succeed'],
  'It explains why the skeptics doubt the conditioning will transfer: a different KIND of stress, not just more of it.')

q = passage('serial', 'Serialized novels',
            'Victorian novels are often criticized for their length and their reliance on coincidence. Such features are easier to understand once we recall how many of these novels first reached readers: in monthly or weekly installments, published over a year or more. A serial writer had to sustain interest across long gaps, which encouraged cliffhangers, large casts, and subplots that could be advanced or suspended as needed. Coincidence, too, served a practical purpose, allowing an author to reunite characters whom readers might otherwise have forgotten. To judge these books by the standards of the compact modern novel, written to be read in a few sittings, is therefore to misunderstand them. This is not to say the conventions of serial publication excuse every weakness; some installments were plainly padded to fill space. But the features most often condemned are better seen as adaptations than as failures.')
q(0, 1, 'Which of the following best states the main point of the passage?',
  ['Features of Victorian novels that are often criticized largely reflect the demands of serial publication.', 'Victorian novels are superior to modern novels.',
   'Serial publication produced only weak novels.', 'Modern readers should avoid long novels.', 'Victorian authors were paid by the word.'],
  'The passage explains criticized features (length, coincidence) by serial publication and concludes they are "adaptations rather than failures".')
q(3, 2, 'The author mentions installments that were "plainly padded" primarily in order to',
  ['acknowledge that not every weakness of these novels can be explained away by serial publication', 'prove that Victorian novels are poorly written',
   'show that readers preferred long installments', 'explain why coincidence was common', 'criticize modern novelists'],
  '"This is not to say … excuse every weakness" - it is a concession that limits the author\'s own argument.')
q(2, 2, 'The author would most likely regard a critic who faults a serialized novel for its large cast, without considering how it was published, as',
  ['overlooking relevant context', 'making an unanswerable point', 'praising the novel too highly', 'confusing two different authors', 'relying on too much evidence'],
  'The author says judging these books by modern standards "is … to misunderstand them" - the critic ignores the publication context.')
q(2, 2, 'The author\'s attitude toward Victorian serial novels can best be described as',
  ['sympathetic but not uncritical', 'uncritically admiring', 'openly contemptuous', 'completely neutral', 'nostalgic and sentimental'],
  'The author defends the novels (adaptations, not failures) but admits some padding - sympathetic but not uncritical.')

q = passage('anchor', 'Reference prices',
            'Retailers have long known that the first price a shopper sees for an item shapes how attractive later prices seem. A jacket marked "was $300, now $180" appears a better bargain than the same jacket simply priced at $180, even when the shopper has no reason to believe the original price was ever charged. Economists call this anchoring. Some regulators have responded by requiring that any advertised "original" price be one at which the item was actually offered for a meaningful period. Critics of such rules argue that sophisticated consumers discount reference prices anyway. Yet studies consistently find that even shoppers who say they distrust reference prices are influenced by them — suggesting that awareness of a bias is not the same as immunity to it.')
q(0, 2, 'The primary purpose of the passage is to',
  ['describe a pricing tactic and respond to an objection to regulating it', 'argue that all retail discounts are fraudulent', 'explain how jackets are priced',
   'show that consumers always distrust reference prices', 'propose a new law on retail pricing'],
  'It explains anchoring, mentions regulation, then answers the critics with study evidence.')
q(3, 2, 'The final sentence of the passage functions primarily to',
  ['provide evidence that undermines the critics\' claim', 'support the critics\' claim', 'define the term "anchoring"', 'describe a new kind of regulation', 'concede that regulation is unnecessary'],
  'The critics say sophisticated shoppers discount reference prices; the studies show even sceptical shoppers are influenced.')
q(2, 2, 'The author implies that shoppers who say they distrust reference prices',
  ['are nonetheless affected by them', 'are never affected by them', 'buy fewer jackets', 'support stricter regulation', 'are mostly economists'],
  '"Even shoppers who say they distrust reference prices are influenced by them."')
q(2, 3, SELECT_ALL + 'Which of the following is supported by the passage?',
  ['A reference price can affect how valuable an item seems even if it was never actually charged.', 'In at least some places, an advertised original price must have actually been offered for a period of time.',
   'Most consumers are unaware that anchoring exists.'],
  'The jacket example supports the first; "some regulators have responded by requiring…" supports the second. The passage never says how many consumers know about anchoring.', right=2)

q = passage('wegener', 'Continental drift',
            'When Alfred Wegener proposed in 1912 that the continents had once formed a single landmass and had since drifted apart, he assembled an impressive range of evidence: the matching coastlines of South America and Africa, identical fossils on continents now separated by oceans, and rock formations that seemed to continue from one continent to another. Most geologists nevertheless rejected his theory for half a century. Their resistance is sometimes portrayed as mere conservatism, but it had a substantive basis: Wegener could offer no plausible mechanism capable of moving continents through the solid ocean floor, and the forces he proposed were demonstrably far too weak. Only in the 1960s, when studies of the sea floor revealed that new crust forms at mid-ocean ridges and spreads outward, did a mechanism emerge — one quite different from what Wegener had imagined.')
q(0, 2, 'The passage is primarily concerned with',
  ['arguing that geologists\' rejection of Wegener\'s theory had a reasonable basis', 'proving that continents do not move', 'describing fossils found in Africa',
   'criticizing geologists for their conservatism', 'explaining how mid-ocean ridges were discovered'],
  'The key move is "sometimes portrayed as mere conservatism, but it had a substantive basis". The passage defends the geologists\' caution.')
q(1, 1, 'According to the passage, a major weakness of Wegener\'s theory was that',
  ['it lacked a plausible mechanism for moving the continents', 'it ignored fossil evidence', 'its coastline evidence was inaccurate', 'it was proposed too late', 'it relied on sea-floor studies'],
  '"Wegener could offer no plausible mechanism…"')
q(2, 2, 'It can be inferred from the passage that the mechanism eventually accepted',
  ['differed from the one Wegener had proposed', 'was the one Wegener had proposed', 'was discovered by Wegener himself', 'was rejected in the 1960s', 'did not involve the ocean floor'],
  '"A mechanism emerged — one quite different from what Wegener had imagined."')
q(3, 3, 'The list of evidence in the first sentence serves mainly to',
  ['show that Wegener\'s case was not baseless, which makes the geologists\' long resistance worth explaining', 'prove that Wegener was correct about the mechanism',
   'show that geologists had ignored fossils', 'introduce the 1960s sea-floor studies', 'suggest that Wegener exaggerated his evidence'],
  'Strong evidence makes the rejection puzzling; the rest of the passage explains it.')

q = passage('photo', 'Photography and painting',
            'When photography appeared in the 1830s, some painters predicted the end of their art: why commission a portrait when a camera could record a face more accurately? The prediction proved wrong, but not because painting outdid photography at its own task. Instead, freed from the obligation to record appearances, many painters turned toward what the camera could not easily capture — the play of light and colour as the eye perceives it, the emotional character of a scene, or the structure underlying visible forms. In this sense photography did not so much threaten painting as redirect it.')
q(0, 1, 'Which of the following best expresses the main idea of the passage?',
  ['Photography redirected painting rather than replacing it.', 'Painting records faces more accurately than photography.', 'Photography ended the art of portrait painting.',
   'Painters of the 1830s rejected photography.', 'The camera can capture emotion better than painting can.'],
  'The last sentence states it: "did not so much threaten painting as redirect it."')
q(2, 2, 'The author implies that the painters\' prediction was wrong because',
  ['painters turned to aims that photography could not easily achieve', 'painting proved more accurate than photography', 'photography was too expensive', 'few people wanted portraits', 'cameras could not record faces'],
  '"Not because painting outdid photography at its own task. Instead…" painters pursued what the camera could not capture.')
q(1, 2, 'In the passage, the word "obligation" most nearly means',
  ['duty', 'debt', 'gratitude', 'contract', 'favour'],
  'Painters were freed from the duty (expected job) of recording appearances.')

q = passage('sparrow', 'Birdsong dialects',
            'Like human children, young songbirds of many species learn to sing by listening to adults. A young white-crowned sparrow raised in isolation develops only a simplified song, whereas one that hears adults during a sensitive period early in life reproduces their song closely — including the local "dialect" that distinguishes birds of one area from those a few kilometres away. Because these dialects are learned rather than inherited, some researchers once hoped they would serve as a convenient marker of population boundaries. That hope has proved only partly justified. Dialect boundaries are often sharp, but birds do cross them; a young male that moves to a new area during his sensitive period will typically adopt the local dialect, effectively concealing his origin from anyone who relies on song alone.')
q(1, 1, 'According to the passage, a white-crowned sparrow raised in isolation',
  ['develops a simpler song than one that hears adults', 'never sings at all', 'learns the dialect of its birthplace', 'sings exactly like adults', 'cannot hear other birds later in life'],
  '"Develops only a simplified song."')
q(2, 2, 'The author regards the hope that dialects would mark population boundaries as "only partly justified" because',
  ['birds that move early in life adopt the local dialect, hiding where they came from', 'dialect boundaries are never sharp', 'dialects are inherited',
   'researchers cannot record birdsong accurately', 'sparrows do not have dialects'],
  'The last sentence: a young male that moves "will typically adopt the local dialect, effectively concealing his origin".')
q(2, 3, SELECT_ALL + 'Which of the following can be inferred from the passage?',
  ['A bird\'s dialect does not always reveal where it hatched.', 'Exposure to adult song matters most during a particular period of a bird\'s life.', 'Song dialects are passed on genetically.'],
  'The first follows from birds concealing their origin; the second from the "sensitive period". The third contradicts "learned rather than inherited".', right=2)
q(0, 2, 'The primary purpose of the passage is to',
  ['explain how song dialects arise and qualify their usefulness as markers of populations', 'argue that sparrows are as intelligent as children',
   'describe how birds migrate', 'prove that dialects are useless to researchers', 'compare the songs of different species'],
  'It explains learning and dialects, then says the marker hope is "only partly justified" - a qualification, not a rejection.')

q = passage('congestion', 'Congestion pricing',
            'Opponents of congestion pricing — charging drivers a fee to enter crowded city centres at peak hours — often argue that it burdens poorer commuters most. The objection has force where public transit is poor, since drivers there have no affordable alternative. But in many large cities the commuters who drive into the centre at peak hours are, on average, wealthier than those who take buses or trains. In such cities a congestion charge falls mainly on better-off residents, and if the revenue is used to improve transit, the policy may even shift resources toward lower-income commuters. Whether congestion pricing is regressive, in other words, depends less on the charge itself than on who drives and how the money is spent.')
q(0, 2, 'The author\'s main point is that',
  ['whether congestion pricing burdens poorer commuters depends on local circumstances', 'congestion pricing always helps the poor', 'congestion pricing should be abolished',
   'public transit is poor in most cities', 'wealthy commuters never drive'],
  'The last sentence: it "depends less on the charge itself than on who drives and how the money is spent".')
q(3, 2, 'The author treats the opponents\' objection as',
  ['valid in some places but not in others', 'entirely mistaken', 'valid everywhere', 'irrelevant to the debate', 'based on a misunderstanding of transit'],
  'It "has force where public transit is poor", but not in cities where drivers are wealthier.')
q(1, 2, 'As used in the passage, "regressive" most nearly means',
  ['placing a heavier burden on people with lower incomes', 'returning to an earlier state', 'reducing traffic', 'increasing over time', 'favouring public transit'],
  'Context: whether the charge "burdens poorer commuters most" - that is what a regressive charge does.')
q(2, 3, 'The author would most likely agree with which of the following?',
  ['In some cities, a congestion charge whose revenue funds transit could benefit lower-income commuters.', 'Congestion charges should be set higher for poorer drivers.',
   'Transit improvements never help lower-income commuters.', 'Every city should introduce congestion pricing.', 'Wealthy commuters prefer buses.'],
  '"The policy may even shift resources toward lower-income commuters" when revenue improves transit. The others are extreme or unsupported.')

# ====================================================================== critical reasoning: assumption / weaken / strengthen
C = 'cr'
cr(C, 0, 1, 'Restaurant X is adding a delivery service, so its total revenue will rise.\nThe argument ASSUMES that',
   ['delivery orders will not simply replace orders the restaurant would have received anyway', 'delivery will be faster than competitors\'', 'the restaurant\'s food is popular',
    'delivery staff will be well paid', 'competitors will not add delivery'],
   'Negation test: if delivery orders just replaced dine-in orders, revenue would not rise - so the argument needs this.')
cr(C, 0, 2, 'Online sales of a publisher\'s textbooks rose 40% last year, while its sales in campus bookstores fell 10%. The publisher concludes that its total textbook sales rose.\nThe conclusion depends on which assumption?',
   ['Online sales made up a large enough share of the total that their rise outweighed the fall in bookstore sales.', 'Students prefer buying textbooks online.',
    'Campus bookstores will soon close.', 'Textbook prices rose last year.', 'Online sales will keep rising next year.'],
   'Percent changes need a base: a 40% rise on a small base can be smaller than a 10% fall on a large one.')
cr(C, 0, 1, 'To reduce the number of employees who quit, a company plans to raise all salaries by 10%.\nThe plan assumes that',
   ['a significant number of employees who quit do so at least partly because of pay', 'the company\'s salaries are the lowest in the industry', 'all employees deserve the same raise',
    'employees who stay are more productive', 'the raise will be paid monthly'],
   'If pay had nothing to do with quitting, a raise would not reduce quitting. The "lowest in the industry" choice is far stronger than needed.')
cr(C, 0, 2, 'Jogging is better exercise than walking, because joggers burn more calories per minute than walkers do.\nThe argument assumes that',
   ['calories burned per minute is an appropriate measure of how good an exercise is', 'walking burns no calories', 'everyone can jog', 'joggers are healthier than walkers in every way',
    'people exercise for the same number of minutes whichever they choose'],
   'The conclusion is about "better exercise"; the evidence is only about calories per minute. The gap is that this one measure decides "better".')
cr(C, 0, 2, 'The new highway will cut the drive from Riverton to the city from 50 minutes to 30. So once it opens, Riverton residents who work in the city will spend less time commuting.\nThe argument assumes that',
   ['traffic on the new highway will not become so heavy that the time saving disappears', 'most Riverton residents work in the city', 'the highway will be finished on time',
    'driving is cheaper than taking the train', 'the old road will be closed'],
   'If congestion ate up the 20-minute saving, commutes would not get shorter. Negate it and the argument fails.')
cr(C, 0, 3, 'A new reading programme raised average test scores at the three schools that piloted it. The district should therefore adopt it at all of its schools.\nThe argument assumes that',
   ['the pilot schools are similar to the district\'s other schools in ways that matter for the programme\'s success', 'the programme is inexpensive', 'test scores are the only measure of learning',
    'teachers at the pilot schools liked the programme', 'no other programme is available'],
   'A result from three schools only generalises if the schools are representative.')
cr(C, 0, 1, 'Maria earned the highest score on the company\'s sales-skills test, so she will be the best salesperson on the team.\nThe argument assumes that',
   ['performance on the test reflects performance in actual selling', 'Maria has the most experience', 'the test was difficult', 'all team members took the test on the same day', 'Maria wants to be a salesperson'],
   'The evidence is a test score; the conclusion is about real selling. The assumption links the two.')
cr(C, 1, 1, 'After a city installed speed cameras on Main Street, accidents on Main Street fell by 30% within a year. The council concludes that the cameras caused the decline.\nWhich, if true, most WEAKENS the conclusion?',
   ['Accidents fell by a similar percentage across the city, including on streets without cameras.', 'The cameras cost less than expected.', 'Some drivers dislike the cameras.',
    'Main Street is the busiest street in the city.', 'Other cities have also installed cameras.'],
   'If accidents fell everywhere, something else probably caused it. Weakeners often supply an alternative cause.')
cr(C, 1, 1, 'Farms that began using a new fertilizer saw yields rise 15%, so the fertilizer increases yields.\nWhich, if true, most WEAKENS the argument?',
   ['The farms that adopted the fertilizer also installed new irrigation systems the same year.', 'The fertilizer is expensive.', 'The fertilizer is popular with farmers.',
    'Yields at these farms varied slightly from year to year before.', 'Some farms used twice the recommended amount.'],
   'Another change happened at the same time, so the fertilizer may not be the cause.')
cr(C, 1, 1, 'Countries where people drink more coffee have higher rates of heart disease. So drinking coffee increases the risk of heart disease.\nWhich, if true, most WEAKENS the argument?',
   ['In those countries, heavy coffee drinkers are also much more likely to smoke, a known cause of heart disease.', 'Coffee is expensive in some countries.',
    'Some people drink tea instead of coffee.', 'Heart disease is a leading cause of death worldwide.', 'Coffee contains caffeine.'],
   'A third factor (smoking) could explain the correlation.')
cr(C, 1, 2, 'To cut litter in its parks by half, a city plans to double the number of trash cans.\nWhich, if true, most strongly suggests the plan will NOT succeed?',
   ['Surveys show that most park litter is dropped within a few steps of an existing trash can that is less than half full.', 'Trash cans are cheap to install.',
    'The parks are busiest on weekends.', 'Some residents volunteer to pick up litter.', 'Other cities have tried similar plans.'],
   'If people litter right next to empty cans, a lack of cans is not the problem - more cans will not help.')
cr(C, 1, 2, 'Since a popular diet book was published, the number of people who say they follow a low-carbohydrate diet has tripled. Clearly the book convinced many people to change their diets.\nWhich, if true, most WEAKENS the argument?',
   ['The rise began two years before the book was published and continued at the same rate afterward.', 'The book sold over a million copies.', 'Some readers did not finish the book.',
    'Low-carbohydrate diets are hard to follow.', 'The author has written other books.'],
   'If the trend was already under way and did not speed up, the book probably did not cause it.')
cr(C, 1, 1, 'A museum extended its opening hours to 9 p.m., and attendance rose 20%. The director concludes that the later hours attracted more visitors.\nWhich, if true, most WEAKENS the conclusion?',
   ['That same month the museum opened a heavily advertised exhibition, and almost all of the extra visitors came during daytime hours.', 'The museum charges for admission.',
    'Evening staff cost more.', 'Some visitors prefer mornings.', 'Other museums also extended their hours.'],
   'Extra visitors came in the daytime, so the evening hours did not draw them - the exhibition probably did.')
cr(C, 1, 3, 'Hospitals that perform a particular surgery more often have lower death rates for that surgery. So patients needing the surgery should choose high-volume hospitals.\nWhich, if true, most WEAKENS the argument?',
   ['High-volume hospitals send their most difficult cases to specialist centres, so the patients they operate on are, on average, healthier.', 'High-volume hospitals are usually in cities.',
    'Some low-volume hospitals have excellent surgeons.', 'The surgery is expensive.', 'Death rates for the surgery have fallen nationally.'],
   'The lower death rate may reflect healthier patients, not better care - so choosing such a hospital would not lower YOUR risk.')
cr(C, 1, 2, 'A survey found that people who own dogs report less stress than people who do not. So getting a dog reduces stress.\nWhich, if true, most WEAKENS the argument?',
   ['People whose lives are already less stressful are more likely to have the time to care for a dog.', 'Dogs need daily walks.', 'Some cat owners also report low stress.',
    'Dog ownership is rising.', 'Stress can cause health problems.'],
   'Reverse causation: low stress may lead to owning a dog, not the other way round.')
cr(C, 2, 1, 'Students who take an optional review course score higher on the final exam than students who do not. So the course improves exam scores.\nWhich, if true, most STRENGTHENS the argument?',
   ['Before the course, students who enrolled had grades similar to those of students who did not.', 'The course is taught by popular teachers.', 'Most students who take the course enjoy it.',
    'The final exam was harder this year.', 'The course meets twice a week.'],
   'It rules out the alternative that stronger students simply chose the course (selection bias).')
cr(C, 2, 1, 'Bees in areas sprayed with pesticide X produced 30% less honey than bees elsewhere. Scientists conclude that pesticide X reduces honey production.\nWhich, if true, most STRENGTHENS the conclusion?',
   ['The sprayed and unsprayed areas had similar flowers, weather and numbers of hives.', 'Pesticide X is widely used.', 'Honey prices rose last year.', 'Bees are important pollinators.', 'Some farmers stopped using pesticide X.'],
   'It rules out other differences between the areas that could explain the drop.')
cr(C, 2, 1, 'A company that let employees work from home two days a week saw productivity rise. Managers conclude that working from home raised productivity.\nWhich, if true, most STRENGTHENS the conclusion?',
   ['Over the same period, productivity did not rise at the company\'s other offices, where everyone stayed on site.', 'Employees said they liked working from home.',
    'The company saved money on office space.', 'Some employees chose not to work from home.', 'Productivity is hard to measure.'],
   'A comparison group without the change and without the improvement makes the cause more likely.')
cr(C, 2, 2, 'An archaeologist argues that an ancient site was a seasonal camp rather than a permanent village.\nWhich, if true, most STRENGTHENS her argument?',
   ['The site has no storage pits, which permanent villages in the region almost always have.', 'The site is near a river.', 'Pottery was found at the site.',
    'Many people lived in the region at that time.', 'The site was discovered recently.'],
   'Missing a feature that permanent villages nearly always have supports "not a permanent village".')
cr(C, 2, 3, 'Students who sleep fewer than six hours a night perform worse on exams. A school therefore proposes starting classes an hour later in order to improve exam performance.\nWhich, if true, most STRENGTHENS the case for the proposal?',
   ['At schools that moved their start times later, students slept longer on average rather than simply going to bed later.', 'Most students prefer later start times.',
    'Teachers support the proposal.', 'Exam performance has been falling.', 'Some students already sleep eight hours.'],
   'The plan only works if a later start actually produces more sleep; this closes that gap.')
cr(C, 2, 2, 'Sales of electric bikes rose sharply after a city built protected bike lanes. Planners conclude that the lanes caused the increase.\nWhich, if true, most STRENGTHENS the conclusion?',
   ['In nearby cities that built no new lanes, e-bike sales stayed flat over the same period.', 'E-bikes are expensive.', 'The lanes were costly to build.',
    'Some residents oppose the lanes.', 'E-bike batteries last longer than they used to.'],
   'A comparison group: no lanes, no rise. That rules out a general trend.')

# ====================================================================== critical reasoning: paradox / flaw / boldface & inference
C2 = 'cr2'
cr(C2, 0, 1, 'Although the town\'s population grew over the past decade, the number of students enrolled in its schools fell.\nWhich, if true, best RESOLVES the apparent paradox?',
   ['Most of the new residents were retirees without school-age children.', 'The town built a new school.', 'Teachers\' salaries rose.', 'The town\'s schools are highly rated.', 'Class sizes decreased.'],
   'A paradox answer explains how both facts can be true: more people, but not families with children.')
cr(C2, 0, 1, 'Umbrella sales in a city rose last year even though there was less rain than usual.\nWhich, if true, best explains this?',
   ['Umbrellas became popular last year as protection against an unusually hot, sunny summer.', 'Umbrella prices rose.', 'Most umbrellas are made abroad.', 'It rained more the year before.', 'Some stores stopped selling umbrellas.'],
   'It gives a reason to buy umbrellas that has nothing to do with rain, so both facts fit.')
cr(C2, 0, 1, 'After a city cut bus fares in half, its total fare revenue increased.\nWhich, if true, best explains this?',
   ['The number of riders more than doubled after the fare cut.', 'Bus drivers received a raise.', 'The city bought new buses.', 'Some riders still drove to work.', 'Fares had not changed for ten years.'],
   'Half the fare × more than twice the riders = more revenue.')
cr(C2, 0, 1, 'Although the hospital hired more nurses, average patient waiting times increased.\nWhich, if true, best explains this?',
   ['At the same time, a nearby hospital closed and many of its patients began coming to this one.', 'The new nurses were well trained.', 'Nurses\' pay increased.',
    'The hospital renovated its lobby.', 'Waiting times are measured in minutes.'],
   'Demand rose faster than staff - both facts are now consistent.')
cr(C2, 0, 2, 'Car models with the highest safety ratings have higher accident rates than models with lower ratings.\nWhich, if true, best explains this?',
   ['Parents disproportionately buy the highest-rated models for teenage drivers, who have far higher accident rates than other drivers.', 'Safety ratings are updated every year.',
    'Highly rated cars cost more.', 'Some accidents are not reported.', 'Most cars have airbags.'],
   'The difference comes from who drives the cars, not the cars themselves.')
cr(C2, 0, 3, 'In a region where a new vaccine is widely used, more of the people hospitalised with the disease are vaccinated than unvaccinated.\nWhich, if true, best explains this without suggesting that the vaccine is ineffective?',
   ['Nearly everyone in the region is vaccinated, so even a low infection rate among the vaccinated produces more cases than the small unvaccinated group.', 'The vaccine was developed quickly.',
    'Some people are afraid of needles.', 'The disease is more common in winter.', 'Hospitals keep careful records.'],
   'Base rates: compare RATES, not raw counts. A huge vaccinated group can produce more cases at a much lower rate.')
cr(C2, 1, 1, 'Every member of the chess club is good at maths. Ana is good at maths, so Ana must be a member of the chess club.\nThe reasoning is flawed because it',
   ['treats a condition that all members meet as if it guaranteed membership', 'relies on an unrepresentative sample', 'attacks Ana rather than her argument',
    'assumes what it is trying to prove about chess', 'uses a term in two different senses'],
   '"Member → good at maths" does not mean "good at maths → member". Reversing the arrow is the classic necessary/sufficient error.')
cr(C2, 1, 1, 'A survey of readers of a cycling magazine found that 80% favour more bike lanes. Therefore most residents of the city favour more bike lanes.\nThe main flaw is that the argument',
   ['relies on an unrepresentative sample', 'confuses cause and effect', 'relies on a circular definition', 'ignores the cost of bike lanes', 'appeals to authority'],
   'Cycling-magazine readers are not typical residents; the sample is biased.')
cr(C2, 1, 2, 'If it rains, the match is cancelled. The match was not cancelled, so it did not rain.\nWhich argument is most similar in its reasoning?',
   ['If the alarm is set, the light is on. The light is off, so the alarm is not set.', 'If the alarm is set, the light is on. The light is on, so the alarm is set.',
    'If the alarm is set, the light is on. The alarm is not set, so the light is off.', 'The light is on, so the alarm must be broken.', 'Alarms and lights are both electrical.'],
   'Original: if A then B; not B; so not A (valid contrapositive). Only the first choice has the same structure.')
cr(C2, 1, 2, 'Every player on the team is excellent, so the team must be excellent.\nThe reasoning is flawed because it',
   ['assumes that what is true of each part must be true of the whole', 'relies on a biased sample', 'confuses cause and effect', 'attacks the coach instead of the argument', 'uses circular reasoning'],
   'Excellent individuals can still form a poor team (no teamwork). This is the part-to-whole flaw.')
cr(C2, 1, 1, 'Professor Lee\'s argument for the new curriculum should be rejected; after all, she was once dismissed from another university.\nThe flaw in this reasoning is that it',
   ['attacks the person making the argument rather than the argument itself', 'relies on statistics', 'assumes the curriculum is expensive', 'confuses cause and effect', 'generalises from one university'],
   'An ad hominem attack: her past says nothing about whether her argument is sound.')
cr(C2, 1, 1, 'Cities with more police officers have more crime. So hiring police officers increases crime.\nThe argument is flawed because it',
   ['overlooks the possibility that high crime leads cities to hire more officers', 'relies on a small sample', 'attacks the police', 'uses a vague term', 'assumes all cities are the same size'],
   'Reverse causation: crime may cause hiring, not the other way round.')
cr(C2, 1, 3, 'Most of the people who won the state lottery last year bought tickets every week. So buying a ticket every week is the best way to win the lottery.\nThe reasoning is flawed because it',
   ['fails to consider how many people who bought tickets every week did not win', 'assumes the lottery is fair', 'relies on last year\'s results only',
    'confuses buying tickets with winning prizes', 'ignores the price of tickets'],
   'If most ticket buyers play weekly, most winners will too - that says nothing about the odds per ticket. You need the comparison group.')
cr(C2, 2, 1, 'All of the paintings in the gallery\'s east wing are by Dutch artists. Some paintings in the east wing were painted before 1700.\nWhich MUST be true?',
   ['Some paintings by Dutch artists were painted before 1700.', 'All Dutch paintings were painted before 1700.', 'The west wing has no Dutch paintings.',
    'Most paintings in the gallery are Dutch.', 'No painting made after 1700 is in the east wing.'],
   'The pre-1700 east-wing paintings are Dutch, so some Dutch paintings are pre-1700. Must-be-true answers stay close to the facts.')
cr(C2, 2, 2, 'Some economists argue that [raising the minimum wage will reduce employment among young workers]. They point out that employers facing higher costs tend to hire fewer people. However, [recent studies in several states found no such decline], perhaps because higher wages also reduce costly staff turnover.\nIn the argument, the two bracketed portions play which roles?',
   ['The first is a position the argument describes; the second is evidence that challenges that position.', 'The first is the argument\'s conclusion; the second supports it.',
    'The first is evidence; the second is the conclusion based on it.', 'Both are evidence for the same conclusion.', 'The first is an assumption; the second is a restatement of it.'],
   'Label each part: the first is the economists\' claim; "However" introduces findings against it.')
cr(C2, 2, 2, 'The city council claims that [the new stadium will pay for itself through increased tax revenue]. But most studies of stadiums find that local spending simply shifts away from other entertainment. Therefore, [the stadium is unlikely to generate significant new revenue].\nThe two bracketed portions play which roles?',
   ['The first is a claim the argument opposes; the second is the argument\'s main conclusion.', 'The first is the conclusion; the second is evidence for it.',
    'Both support the council\'s position.', 'The first is evidence; the second is an objection to that evidence.', 'The first is the main conclusion; the second is an intermediate conclusion.'],
   '"Therefore" marks the second as the conclusion; it contradicts the council\'s claim.')
cr(C2, 2, 1, 'No reptile in the zoo is fed live prey. Every animal in the zoo\'s south wing is a reptile.\nWhich MUST be true?',
   ['No animal in the south wing is fed live prey.', 'All reptiles in the zoo are in the south wing.', 'Some animals outside the south wing are fed live prey.',
    'The south wing has more animals than any other wing.', 'Every animal fed live prey is a mammal.'],
   'South wing → reptile → not fed live prey. Chain the two statements.')
cr(C2, 2, 2, 'At the company, every manager has an MBA, and no one hired before 2010 has an MBA.\nWhich MUST be true?',
   ['No manager at the company was hired before 2010.', 'Everyone hired after 2010 is a manager.', 'Everyone with an MBA is a manager.',
    'Some managers were hired before 2010.', 'Most employees have an MBA.'],
   'Manager → MBA, and hired before 2010 → no MBA. So a manager cannot have been hired before 2010.')
cr(C2, 2, 3, 'Every club member who plays tennis also plays golf. No club member who plays golf also swims.\nWhich MUST be true?',
   ['No club member who plays tennis swims.', 'Every club member who plays golf also plays tennis.', 'Some club members who swim play tennis.',
    'Every club member plays at least one sport.', 'Some club members play golf but not tennis.'],
   'Tennis → golf → no swimming, so tennis players do not swim. The other choices reverse arrows or add facts not given.')

# ====================================================================== lessons
def ex(q, steps, a):
    return dict(q=q, steps=steps, a=a)


LESSONS = {
    'tc_basic': [
        dict(t='Find the clue, predict your own word', teach=[
            'Cover the answer choices. The sentence always contains a clue - the part that tells you what the blank must mean.',
            'Underline the clue, then write your own simple word for the blank (it can be plain English, e.g. "careful").',
            'Only now look at the choices and pick the one closest to YOUR word. This protects you from attractive wrong answers.'],
            ex=ex('Hoping to ______ the angry crowd, the mayor promised an immediate investigation.  (placate / incite / deride / ignore / provoke)',
                  ['Clue: "hoping to … the angry crowd" + a promise meant to help.', 'My own word: "calm down".', 'Match: placate = calm, soothe. Incite and provoke do the opposite.'], 'placate'),
            hint='Find the words that describe the blank, put your own word in, then match.'),
        dict(t='Punctuation and restatement clues', teach=[
            'A colon, semicolon or a pair of dashes usually introduces an explanation or restatement of the blank.',
            'Phrases like "in other words", "that is", "indeed" also say "the blank agrees with what follows".',
            'So the part after the colon or inside the dashes IS the definition of the blank.'],
            ex=ex('The architect\'s designs are strikingly ______: she uses only straight lines and no ornament of any kind.  (austere / ornate / eclectic / garish / baroque)',
                  ['The colon means the second half explains the blank.', 'Straight lines, no ornament → my word: "plain".', 'austere = severely plain.'], 'austere'),
            hint='Read what comes after the colon, semicolon or dashes - it defines the blank.'),
        dict(t='Cause, effect and support signals', teach=[
            '"Because", "since", "so", "therefore", "thus", "given" link cause and effect - the blank must be consistent with the result.',
            '"And", "also", "moreover" mean the blank continues in the same direction as the rest of the sentence.',
            '"So … that …" sentences: the blank must be strong enough to cause the result.'],
            ex=ex('Given the region\'s ______ rainfall, farmers have long relied on irrigation.  (scant / copious / torrential / predictable / refreshing)',
                  ['"Given" signals cause → effect.', 'Effect: they need irrigation. Cause: little rain.', 'My word: "low" → scant.'], 'scant'),
            hint='Ask: what cause would produce this effect (or what effect follows from this cause)?'),
    ],
    'tc_shift': [
        dict(t='Contrast signals', teach=[
            'Although, though, but, yet, however, despite, rather than, while, whereas, unlike - these REVERSE the direction.',
            'Find the clue on the other side of the shift word, then predict the OPPOSITE for the blank.',
            'Watch which side of the shift the blank is on: a word on the same side as the clue agrees with it.'],
            ex=ex('Despite his reputation for ______, the senator gave a remarkably concise speech.  (verbosity / brevity / honesty / reticence / wit)',
                  ['Shift word: "despite".', 'Clue on the other side: "concise".', 'Opposite of concise: wordy → verbosity.'], 'verbosity'),
            hint='Find the shift word, find the clue on the other side, then go the opposite way.'),
        dict(t='Time shifts and surprise', teach=[
            '"Initially … eventually", "once … now", "at first", "originally", "no longer" contrast the past with the present.',
            '"Surprisingly", "ironically", "unexpectedly", "paradoxically" mean the blank goes against what you would expect.'],
            ex=ex('The findings, initially greeted with ______, were eventually accepted as orthodoxy.  (skepticism / acclaim / deference / enthusiasm / reverence)',
                  ['"Initially … eventually accepted" is a time shift.', 'Later they were accepted, so at first they were NOT accepted.', 'My word: "doubt" → skepticism.'], 'skepticism'),
            hint='Past vs present (or expected vs actual): the blank is the opposite of the other time.'),
        dict(t='Double negatives and hidden reversals', teach=[
            'Two negatives cancel: "not without merit" = has merit; "far from rare" = common; "hardly lenient" = strict.',
            '"Belie" means to give a false impression of - the two things it connects contrast.',
            'Simplify the sentence in your own words before predicting.'],
            ex=ex('Far from being ______, the senator\'s retirement had been planned for years.  (abrupt / deliberate / anticipated / gradual / voluntary)',
                  ['"Far from being X" = it was NOT X.', 'Planned for years → it was NOT sudden.', 'So the blank = sudden → abrupt.'], 'abrupt'),
            hint='Rewrite the negatives as a positive statement first.'),
    ],
    'tc_double': [
        dict(t='Start with the easier blank', teach=[
            'Two-blank questions give three choices per blank, and you must get BOTH right - there is no partial credit.',
            'You do not have to start with blank (i). Start with whichever blank has the clearer clue (often the second one).',
            'Lock in that blank, then use it as an extra clue for the other one.'],
            ex=ex('The treaty was hailed as a (i)______ achievement, yet historians now see its provisions as (ii)______, since few were ever enforced.',
                  ['Blank (ii) has the clearest clue: "few were ever enforced" → weak, ineffective → toothless.', '"Hailed" → blank (i) is positive → landmark.', 'Check the whole sentence: landmark … toothless.'], 'landmark … toothless'),
            hint='Solve the blank with the most obvious clue first.'),
        dict(t='Blanks that agree or contrast', teach=[
            'Decide the RELATIONSHIP between the blanks first: do they point the same way, or opposite ways (look for a shift word)?',
            'Then the blanks constrain each other: once one is fixed, the other must agree or contrast with it.',
            'Always reread the full sentence with both words in before moving on.'],
            ex=ex('The author\'s early essays were (i)______, crammed with digressions; her later work, by contrast, is a model of (ii)______.',
                  ['"By contrast" → the two blanks are opposites.', 'Digressions → early essays are convoluted.', 'Opposite of convoluted → clarity.'], 'convoluted … clarity'),
            hint='Find the relationship between the blanks (same direction or contrast) first.'),
    ],
    'tc_triple': [
        dict(t='Summarise, then find the anchor blank', teach=[
            'Three-blank questions are often a short paragraph. Read it all and summarise its story in one sentence.',
            'One blank usually has a direct clue (the "anchor"). Solve it first, then work outward along the logic.',
            'Track shift words between sentences - they flip the direction from one blank to the next.'],
            ex=ex('The report was anything but (i)______: rather than (ii)______ the failures, it (iii)______ them in exhaustive detail.',
                  ['Anchor: "in exhaustive detail" → (iii) documented.', '"Rather than" → (ii) is the opposite of documenting: gloss over.', '"Anything but" → the report was not hiding anything: (i) evasive.'], 'evasive … gloss over … documented'),
            hint='Find the blank with the most direct clue and build from there.'),
        dict(t='Check the logic chain', teach=[
            'Each blank must fit its own clue AND the whole paragraph. Wrong answers often fit one blank perfectly but break the overall story.',
            'Before you submit, reread the full passage with all three words. If any sentence sounds odd, revisit it.'],
            ex=ex('Because the founder was usually (i)______ about risk, investors were surprised when she (ii)______ the entire reserve on an untested product — a gamble that, to the (iii)______ of her critics, paid off.',
                  ['Surprise = out of character → she is usually cautious.', 'Gambling the reserve → staked.', 'Critics are unhappy when the gamble works → chagrin.', 'Reread: cautious … staked … chagrin - consistent.'], 'cautious … staked … chagrin'),
            hint='Reread the whole paragraph with your three words - the story must make sense.'),
    ],
    'se': [
        dict(t='Predict, then find TWO matches', teach=[
            'Sentence equivalence: one blank, six choices, choose TWO that make sentences with the same meaning.',
            'Use the text-completion method: find the clue and predict your own word.',
            'Then find two choices that both match your prediction. Both must be right - no partial credit.'],
            ex=ex('Known for her ______, the diplomat rarely revealed her opinions.  (reticence / reserve / garrulousness / candor / impatience / enthusiasm)',
                  ['Clue: rarely revealed her opinions.', 'My word: "keeping quiet".', 'Two matches: reticence and reserve.'], 'reticence, reserve'),
            hint='Predict a word first, then find the two choices that both fit it.'),
        dict(t='Synonym-pair traps', teach=[
            'Most SE questions include a TRAP PAIR: two synonyms that match each other but give the sentence the wrong meaning.',
            'So never pick a pair just because the two words mean the same - check each in the sentence.',
            'Often the trap pair is the exact opposite of the right pair.'],
            ex=ex('The evidence, though suggestive, remains ______.  (tentative / provisional / conclusive / decisive / abundant / irrefutable)',
                  ['"Though suggestive" → it is not settled yet.', 'conclusive / decisive is a synonym pair - but it reverses the meaning (trap).', 'tentative / provisional fits "not settled".'], 'tentative, provisional'),
            hint='Be suspicious of a synonym pair: test each word in the sentence.'),
        dict(t='Secondary meanings and tone', teach=[
            'The GRE loves second meanings: temper (soften), qualify (limit), economy (efficiency), check (restrain), sanction (approve OR punish).',
            'If no pair seems to fit, look for a familiar word used in an unusual sense.'],
            ex=ex('The new evidence did little to ______ her confidence; if anything, she grew more certain.  (temper / moderate / bolster / reinforce / display / publicize)',
                  ['"Did little to …; if anything, more certain" → the evidence did not REDUCE her confidence.', 'Reduce/soften: temper (second meaning) and moderate.', 'bolster / reinforce is the reversed trap pair.'], 'temper, moderate'),
            hint='Think of second meanings of common words.'),
    ],
    'rc': [
        dict(t='Main idea and primary purpose', teach=[
            'Read for STRUCTURE, not detail: what is the author\'s main point, and what job does each sentence do?',
            'Watch for turn words ("however", "recent studies suggest", "this view is incomplete") - the main point usually comes after the turn.',
            'Primary-purpose answers start with a verb (argue, describe, challenge, qualify). Match the verb to how strong the author is.'],
            ex=ex('A passage says historians treated merchants\' letters as reliable; a "closer reading complicates this view"; letters remain valuable as evidence of how merchants wished to be seen. Primary purpose?',
                  ['Turn: "a closer reading complicates this view".', 'The author does not reject the letters - "remain valuable, but…".', 'So: to qualify (revise) a traditional view of a historical source.'], 'Revise a traditional view of the letters'),
            hint='Look for the turn word: the main point usually follows it.'),
        dict(t='Detail questions', teach=[
            '"According to the passage" means the answer is stated. Go back and find the line - never answer from memory.',
            'The right answer is usually a paraphrase of the line; wrong answers twist a word or mix up two parts of the passage.'],
            ex=ex('"…corals expel the algae that supply most of their energy … if conditions do not improve, they starve." According to the passage, why do bleached corals starve?',
                  ['Find the line about starving.', 'Starving follows losing the algae, which supply most of their energy.', 'Paraphrase: they lose their main source of energy.'], 'They lose the algae that supplied their energy'),
            hint='Find the exact line, then choose its paraphrase.'),
        dict(t='Inference and the author\'s attitude', teach=[
            'An inference must be TRUE based on the passage - a small, safe step, never a big leap.',
            'Extreme words (always, never, all, only, prove) are usually wrong unless the passage is just as extreme.',
            'Attitude: look for evaluation words ("valuable but…", "compelling", "unfortunately"). GRE authors are usually moderate: qualified approval, measured criticism.'],
            ex=ex('"Such letters remain valuable, but less as ledgers than as evidence of how merchants wished to be seen." The author\'s attitude to the letters?',
                  ['"Remain valuable" = positive.', '"But less as ledgers" = a reservation.', 'Positive with a reservation = qualified appreciation.'], 'Qualified appreciation'),
            hint='Choose the most moderate answer that the text clearly supports.'),
        dict(t='Function questions and select-all', teach=[
            'Function questions ask WHY a sentence or example is there: to illustrate, to concede, to contrast, to support, to introduce.',
            'Read the sentence before and after it - its job is defined by its neighbours.',
            'Select-all: judge each choice on its own - one, two or all three can be right, and there is no partial credit.'],
            ex=ex('"…some installments were plainly padded to fill space. But the features most often condemned are better seen as adaptations." Why mention padded installments?',
                  ['The sentence starts "This is not to say … excuse every weakness".', 'So the author admits a limit to their own defence.', 'Function: a concession.'], 'To concede that not every weakness is explained'),
            hint='Ask "why is this here?" and read the sentences around it.'),
    ],
    'cr': [
        dict(t='Argument structure and assumptions', teach=[
            'Find the CONCLUSION first ("so", "therefore", "thus", "clearly"), then the EVIDENCE, then the GAP between them.',
            'The assumption is the unstated idea that bridges that gap.',
            'Negation test: negate an answer choice. If the argument falls apart, that choice was the assumption.'],
            ex=ex('Restaurant X is adding delivery, so its revenue will rise. What does the argument assume?',
                  ['Conclusion: revenue will rise. Evidence: adding delivery.', 'Gap: delivery orders must be EXTRA, not just replacing dine-in orders.', 'Negate it: "delivery orders just replace dine-in orders" → revenue does not rise. The argument collapses.'],
               'Delivery orders will not just replace existing orders'),
            hint='Conclusion → evidence → what must also be true for it to work? Use the negation test.'),
        dict(t='Weaken', teach=[
            'Attack the gap, not the evidence (the evidence is taken as true).',
            'The most common weakener is an ALTERNATIVE CAUSE: something else explains the result.',
            'Other weakeners: reverse causation, the effect happened anyway (no change in a comparison group), or the sample is unrepresentative.'],
            ex=ex('After speed cameras went up on Main Street, accidents there fell 30%, so the cameras caused the fall. What weakens this?',
                  ['Conclusion: cameras caused the fall.', 'Look for another cause or a comparison.', 'If accidents fell equally on streets WITHOUT cameras, something else caused it.'], 'Accidents fell just as much elsewhere'),
            hint='Look for something else that could have caused the result.'),
        dict(t='Strengthen', teach=[
            'Strengtheners close the gap: they rule out an alternative cause or add support for the link.',
            'A comparison group is powerful: "where the change did not happen, the result did not happen either".',
            'The right answer does not need to prove the conclusion - it just needs to make it more likely.'],
            ex=ex('Students who take a review course score higher, so the course improves scores. What strengthens this?',
                  ['Alternative explanation: stronger students choose the course.', 'Rule it out: enrollees had similar grades before the course.', 'Now the course is the more likely cause.'], 'Enrollees had similar grades beforehand'),
            hint='Rule out the most obvious alternative explanation.'),
    ],
    'cr2': [
        dict(t='Paradox: explain both facts', teach=[
            'A paradox question gives two facts that seem to conflict. The right answer shows how BOTH can be true.',
            'Do not pick an answer that just repeats one fact or makes the conflict worse.',
            'Common keys: a hidden third factor, a different group, or counts vs rates.'],
            ex=ex('Bus fares were cut in half, yet fare revenue went up. What explains this?',
                  ['Revenue = fare × riders.', 'Half the fare can still mean more revenue if riders more than double.', 'An answer saying riders more than doubled resolves it.'], 'Ridership more than doubled'),
            hint='Find a fact that makes both statements true at the same time.'),
        dict(t='Common flaws', teach=[
            'Reversing a conditional: "All A are B" does not mean "all B are A".',
            'Correlation ≠ causation (and watch for reverse causation and third factors).',
            'Unrepresentative sample; part-to-whole; attacking the person (ad hominem); ignoring the comparison group.'],
            ex=ex('Every chess-club member is good at maths. Ana is good at maths, so she is a member. Flaw?',
                  ['Statement: member → good at maths.', 'The argument uses: good at maths → member.', 'That reverses the arrow (necessary vs sufficient).'], 'It reverses a conditional'),
            hint='Name the flaw: reversed conditional, bad sample, correlation-as-cause, part-whole, or personal attack.'),
        dict(t='Boldface roles and must-be-true', teach=[
            'Boldface (here, [bracketed]) questions: label each part BEFORE reading the choices - conclusion, evidence, opposing view, or counter-evidence.',
            '"Therefore" marks a conclusion; "however" often introduces evidence against what came before.',
            'Must-be-true: chain the statements (A → B → C) and pick only what follows with certainty.'],
            ex=ex('No reptile in the zoo is fed live prey. Every animal in the south wing is a reptile. What must be true?',
                  ['Chain: south wing → reptile → not fed live prey.', 'So no south-wing animal is fed live prey.', 'Reject choices that reverse an arrow or add new facts.'], 'No south-wing animal is fed live prey'),
            hint='Chain the statements and take only the guaranteed step.'),
    ],
}

TITLES = {'tc_basic': 'Text completion — clues', 'tc_shift': 'Text completion — shifts', 'tc_double': 'Text completion — two blanks',
          'tc_triple': 'Text completion — three blanks', 'se': 'Sentence equivalence', 'rc': 'Reading comprehension',
          'cr': 'Critical reasoning — assume / weaken / strengthen', 'cr2': 'Critical reasoning — paradox / flaw / boldface'}

# ====================================================================== chapters, units, schedule
UNITS = [
    dict(key='v1', title='Verbal unit 1 · Text completion & sentence equivalence', chapters=['tc_basic', 'tc_shift', 'tc_double', 'tc_triple', 'se']),
    dict(key='v2', title='Verbal unit 2 · Reading & reasoning', chapters=['rc', 'cr', 'cr2']),
]
# schedule from the 100-day plan
CH_DAY = {c: gre_plan.CH_DAY[c] for u in UNITS for c in u['chapters']}
for _u in UNITS:
    _u['day'] = gre_plan.UNIT_DAY[_u['key']]
RETEST_DAYS = gre_plan.retest_days('v')
SECTION_DAYS = gre_plan.SECTION_DAYS['verbal']
UNIT_OF = {c: u['key'] for u in UNITS for c in u['chapters']}
UNIT_BY_KEY = {u['key']: u for u in UNITS}
CHAPTERS = [c for u in UNITS for c in u['chapters']]
TEST_SPEC = {'chapter': (10, 15), 'unit': (20, 30), 'section1': (12, 18), 'section2': (15, 23), 'drill': (10, 15)}
DIFF_W = {'easy': {1: 5, 2: 4, 3: 1}, 'mixed': {1: 3, 2: 5, 3: 2}, 'hard': {1: 1, 2: 4, 3: 5}}
BY_ID = {x['id']: x for x in QS}
TC_CHAPTERS = ['tc_basic', 'tc_shift', 'tc_double', 'tc_triple']
READING = ['rc', 'cr', 'cr2']


def title(ch):
    return TITLES.get(ch, ch)


def concept_name(ch, c):
    try:
        return LESSONS[ch][c]['t']
    except (KeyError, IndexError, TypeError):
        return title(ch)


def lesson(ch):
    return {'chapter': ch, 'title': title(ch), 'unit': UNIT_OF[ch], 'day': CH_DAY[ch], 'subject': 'verbal',
            'concepts': [{'i': i, 'title': c['t'], 'teach': c['teach'], 'example': c['ex'], 'hint': c['hint']} for i, c in enumerate(LESSONS[ch])]}


def serve(item, r):
    """A fresh copy of a bank question for the UI: choices shuffled, passage attached."""
    out = {k: v for k, v in item.items()}
    if item['kind'] == 'tc':
        cols, ans = [], []
        for col, a in zip(item['c'], item['a']):
            order = list(range(len(col)))
            r.shuffle(order)
            cols.append([col[i] for i in order])
            ans.append(order.index(a))
        out['c'], out['a'] = cols, ans
    else:
        order = list(range(len(item['c'])))
        r.shuffle(order)
        out['c'] = [item['c'][i] for i in order]
        out['a'] = sorted(order.index(i) for i in item['a']) if isinstance(item['a'], list) else order.index(item['a'])
    if item.get('pid'):
        p = PASSAGES[item['pid']]
        out['passage'], out['ptitle'] = p['text'], p['title']
    out.update(gen=item['id'], ctitle=title(item['chapter']), cname=concept_name(item['chapter'], item['concept']), subject='verbal')
    return out


def _weight(item, seen, mix):
    """Unseen questions first (they get a big weight), then by the difficulty mix."""
    return mix[item['diff']] * (8 if not seen.get(item['id']) else 1 / (1 + seen[item['id']]))


def _draw(r, pool, n, seen, mix):
    pool = list(pool)
    out = []
    while pool and len(out) < n:
        it = r.choices(pool, weights=[_weight(x, seen, mix) for x in pool])[0]
        pool.remove(it)
        out.append(it)
    return out


def _draw_passages(r, n, seen, mix, concepts=None):
    """Whole passages (their questions stay together) until about n questions."""
    pids = list(PASSAGES)
    out = []
    while pids and len(out) < n:
        w = [sum(_weight(BY_ID[i], seen, mix) for i in PASSAGES[p]['qs']) / len(PASSAGES[p]['qs']) for p in pids]
        p = r.choices(pids, weights=w)[0]
        pids.remove(p)
        qs = [BY_ID[i] for i in PASSAGES[p]['qs'] if concepts is None or BY_ID[i]['concept'] in concepts]
        out += qs[:max(1, n - len(out))]
    return out


EXCLUDED = set()  # question ids reported as bad (filled by gre.load_exclusions)


def _words(s):
    return set(re.findall(r'[a-z]{4,}', (s or '').lower()))


def _example_like():
    """Bank questions that are near-copies of a lesson's worked example: you have already seen them in the lesson."""
    out = set()
    for ch, concepts in LESSONS.items():
        exs = [_words(c['ex']['q']) for c in concepts]
        for q in QS:
            if q['chapter'] == ch:
                w = _words(q['q'])
                if any(w and e and len(w & e) / len(w | e) >= 0.5 for e in exs):
                    out.add(q['id'])
    return out


EXAMPLE_LIKE = _example_like()


def pick(r, ch, n, seen=None, level='mixed', concepts=None, avoid=None):
    """avoid: question ids to leave out (seen in today's practice / the lesson) unless the chapter runs out of others."""
    seen = seen or {}
    avoid = avoid or set()
    mix = DIFF_W.get(level, DIFF_W['mixed'])
    if ch == 'rc':
        return _draw_passages(r, n, seen, mix, concepts)
    pool = [x for x in QS if x['chapter'] == ch and (concepts is None or x['concept'] in concepts) and x['id'] not in EXCLUDED] or \
        [x for x in QS if x['chapter'] == ch and x['id'] not in EXCLUDED] or [x for x in QS if x['chapter'] == ch]
    fresh = [x for x in pool if x['id'] not in avoid]
    out = _draw(r, fresh, n, seen, mix)
    if len(out) < n:  # not enough unseen ones: reuse the ones seen longest ago (seen order is up to the caller)
        out += _draw(r, [x for x in pool if x['id'] in avoid], n - len(out), seen, mix)
    return out


def try_question(ch, concept, seen=None, seed=None):
    r = random.Random(seed)
    seen = seen or {}
    pool = [x for x in QS if x['chapter'] == ch and x['concept'] == concept] or [x for x in QS if x['chapter'] == ch]
    return serve(_draw(r, pool, 1, seen, DIFF_W['easy'])[0], r)


def _order(items):
    """GRE-like order: text completions (1 → 3 blanks), sentence equivalence, then reading blocks."""
    rank = {'tc_basic': 0, 'tc_shift': 0, 'tc_double': 1, 'tc_triple': 2, 'se': 3, 'rc': 4, 'cr': 5, 'cr2': 5}
    pos = {it['id']: i for i, it in enumerate(items)}
    return sorted(items, key=lambda it: (rank[it['chapter']], it.get('pid') or '', pos[it['id']]))


def build_test(kind, key=None, level='mixed', chapters=None, concepts=None, seen=None, seed=None, avoid=None):
    """kind: chapter (key = chapter), unit (key = unit), section1/section2 (chapters = pool), drill (concepts = [(ch, c), ...])."""
    r = random.Random(seed)
    seen = seen or {}
    n, minutes = TEST_SPEC[kind]
    if kind == 'chapter':
        qs = pick(r, key, n, seen, level, avoid=avoid)
        qs.sort(key=lambda q: (q['diff'], q.get('pid') or ''))
        return dict(kind=kind, key=key, subject='verbal', title=f'Chapter test · {title(key)}', minutes=minutes, questions=[serve(q, r) for q in qs])
    if kind == 'unit':
        chs = UNIT_BY_KEY[key]['chapters']
        if key == 'v2':
            per = {'rc': 10, 'cr': 5, 'cr2': 5}
        else:
            per = {c: n // len(chs) for c in chs}
        qs = [q for ch in chs for q in pick(r, ch, per[ch], seen, level, avoid=avoid)]
        return dict(kind=kind, key=key, subject='verbal', title=f'{UNIT_BY_KEY[key]["title"]} - combined test', minutes=minutes, questions=[serve(q, r) for q in _order(qs)])
    if kind in ('section1', 'section2'):
        pool = [c for c in (chapters or CHAPTERS) if c in CH_DAY]
        tcs = [c for c in pool if c in TC_CHAPTERS] or ['tc_basic']
        want = {'section1': (4, 3, 5), 'section2': (5, 3, 7)}[kind]
        n_tc, n_se, n_read = want
        if 'se' not in pool:
            n_tc, n_se = n_tc + n_se, 0
        reading = [c for c in pool if c in READING]
        if not reading:
            n_tc, n_read = n_tc + n_read, 0
        qs = []
        for _ in range(n_tc):
            ch = r.choice(tcs)
            got = pick(r, ch, 1, {**seen, **{q['id']: 99 for q in qs}}, level)
            qs += [g for g in got if g not in qs]
        if n_se:
            qs += pick(r, 'se', n_se, seen, level)
        if n_read:
            if 'rc' in reading:
                rc = pick(r, 'rc', max(2, n_read - 2) if len(reading) > 1 else n_read, seen, level)
                qs += rc
                left = n_read - len(rc)
            else:
                left = n_read
            crs = [c for c in reading if c != 'rc']
            for i in range(max(0, left)):
                if not crs:
                    break
                got = pick(r, crs[i % len(crs)], 1, {**seen, **{q['id']: 99 for q in qs}}, level)
                qs += [g for g in got if g not in qs]
        label = 'Section 1' if kind == 'section1' else f'Section 2 ({"harder" if level == "hard" else "easier" if level == "easy" else "medium"})'
        return dict(kind=kind, key=level, subject='verbal', title=f'Verbal {label} - GRE timing', minutes=minutes, questions=[serve(q, r) for q in _order(qs)])
    if kind == 'drill':
        concepts = concepts or [(CHAPTERS[0], 0)]
        qs = []
        for i in range(n):
            ch, c = concepts[i % len(concepts)]
            got = pick(r, ch, 1 if ch != 'rc' else 3, {**seen, **{q['id']: 99 for q in qs}}, 'mixed', concepts={c})
            qs += [g for g in got if g not in qs]
            if len(qs) >= n:
                break
        return dict(kind=kind, key='drill', subject='verbal', title='Verbal weak-spot drill', minutes=minutes, questions=[serve(q, r) for q in _order(qs[:max(n, len(qs))])])
    raise ValueError(kind)


def quiz_items(topic, k, r, seen=None):
    """k questions on a verbal topic for the daily quiz (fields like gre_quiz.BANK plus kind/passage)."""
    out = []
    for it in pick(r, topic, k, seen or {}, 'mixed'):
        s = serve(it, r)
        out.append(s)
    return out


def _check():
    for x in QS:
        k, c, a = x['kind'], x['c'], x['a']
        if k == 'tc':
            assert all(len(col) == 3 for col in c) and len(a) == len(c) and x['q'].count('______') == len(c), x['id']
        elif k == 'ma':
            assert isinstance(a, list) and all(0 <= i < len(c) for i in a), x['id']
        else:
            assert 0 <= a < len(c), x['id']
        assert len(set(map(str, c))) == len(c), x['id']
        assert x['concept'] < len(LESSONS[x['chapter']]), x['id']
    for ch in CHAPTERS:
        for i in range(len(LESSONS[ch])):
            assert any(x['chapter'] == ch and x['concept'] == i for x in QS), (ch, i)


_check()
