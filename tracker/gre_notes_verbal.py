"""Study notes - Verbal, Analytical Writing and test strategy. Original, concise, topic-wise reading (written for this app).
Same markup as gre_notes_quant."""

NOTES = {}


def note(key, title, minutes, body, subject='verbal'):
    NOTES[key] = dict(title=title, minutes=minutes, body=body, subject=subject)


note('gre_overview', 'The GRE in one page + how to use this course', 10, """
# The test (since September 2023)
| Section | Questions | Time |
| Analytical Writing (one Issue essay) | 1 task | 30 min |
| Verbal Reasoning - section 1 | 12 | 18 min |
| Verbal Reasoning - section 2 | 15 | 23 min |
| Quantitative Reasoning - section 1 | 12 | 21 min |
| Quantitative Reasoning - section 2 | 15 | 26 min |
Total: about 1 hour 58 minutes, no scheduled break.
! Verbal and Quant are scored 130-170 each; Writing 0-6 in half points.
! The test is section-adaptive: how well you do in section 1 decides whether section 2 is easier or harder. Hard second sections are needed for high scores.
! No penalty for wrong answers - never leave anything blank.
# Question types
- Verbal: Text Completion (1-3 blanks), Sentence Equivalence (pick two), Reading Comprehension (incl. short arguments).
- Quant: Quantitative Comparison, multiple choice (one or several answers), numeric entry, data interpretation.
# How each class in this course works (like tuition)
- 1. Read today's study notes (this page) - 10-20 minutes, with worked examples and quick checks.
- 2. Do the tutor session: concept → worked example → you try one.
- 3. Solve sums: Magoosh questions with video solutions, then the chapter test. Tap ✗ on anything you got wrong.
- 4. Vocab flashcards, then the GRE-style quiz.
- Books in "Go deeper" are optional - only for extra practice.
# Your targets
Business-analytics programmes value Quant most: aim for 165+ Quant (top programmes' classes average higher) and 155+ Verbal.
""", subject='strategy')

note('tc_clues', 'Text completion 1: find the clue, predict, then match', 15, """
# What Text Completion tests
One to three blanks in a sentence or short paragraph. One-blank questions have 5 choices; two- and three-blank questions have 3 choices per blank. All blanks must be right - no partial credit.
# The method (use it every time)
- 1. Cover the choices.
- 2. Find the CLUE - the words that tell you what the blank must mean.
- 3. Write your own simple word for the blank (plain English is fine: "careful", "not clear").
- 4. Only now look at the choices and pick the one closest to your word.
> Predicting first protects you from choices that "sound good" but do not fit the logic.
# Clue type 1: restatement (colon, semicolon, dashes)
! After a colon or semicolon, or between dashes, the sentence usually explains or restates the blank.
EX: The architect's designs are strikingly ______: straight lines, white walls and no ornament. (austere / ornate / garish / eclectic / baroque) || The colon introduces the explanation. || Plain, no ornament → my word: "plain". || => austere
# Clue type 2: cause and effect
! because, since, so, therefore, thus, as a result, given - the blank must be consistent with the cause or effect.
EX: Given the region's ______ rainfall, farmers rely on irrigation. || Effect: they need irrigation. Cause: little rain. || My word: "low". || => scant
# Clue type 3: support and continuation
! and, also, moreover, indeed, in fact - the blank continues in the same direction.
x Do not pick a word just because it is a hard GRE word. The right answer matches the sentence's LOGIC.
# Learning vocabulary (start today)
- 30 new GregMat words a day: flashcards in the morning, again before bed.
- Say each word in a sentence of your own - context is how the GRE tests words.
- Words you meet in questions and do not know go straight into your notes.
Q: Investors were ______ about the merger, having been burned twice before. Your prediction? => "cautious" → wary
Q: Her prose is so ______ that readers need several passes to untangle one sentence. Prediction? => "complicated" → convoluted
""")

note('tc_shift', 'Text completion 2: shift words and reversals', 12, """
# Shift words reverse the direction
! although, though, but, yet, however, despite, in spite of, rather than, while, whereas, unlike, instead of, nevertheless
Find the clue on the other side of the shift, then predict the OPPOSITE.
EX: Despite his reputation for ______, the senator gave a remarkably concise speech. || Shift: "despite". Clue on the other side: "concise". || Opposite of concise: wordy. || => verbosity
# Time shifts and expectation
! initially… eventually, once… now, at first, originally, no longer - the past contrasts with the present.
! surprisingly, ironically, unexpectedly, paradoxically - the blank goes against what you would expect.
EX: The findings, initially greeted with ______, were eventually accepted. || "Initially… eventually accepted" is a time shift. || At first they were NOT accepted → "doubt". || => skepticism
# Double negatives and hidden reversals
! not without merit = has merit. far from rare = common. hardly lenient = strict.
! belie = give a false impression of - the two things it links contrast.
x Watch which side of the shift the blank is on. A blank on the same side as the clue agrees with it.
EX: The athlete's public persona is brash and ______, but friends describe a shy person. || The blank sits with "brash", before "but". || It agrees with brash. || => swaggering
> Simplify tricky sentences in your own words before predicting: "Far from being X, it was Y" → "It was Y, not X".
Q: Rather than ______ the controversy, the statement only intensified it. => opposite of intensify: defusing
Q: The proposal is not without ______: several provisions are genuinely useful. => merit
""")

note('tc_double', 'Text completion 3: two-blank questions', 12, """
# How two-blank questions work
Each blank has its own column of three choices. You must get BOTH right.
# Start with the easier blank
You do not have to start with blank (i). Find the blank with the clearest clue - it is often the second one.
EX: The treaty was hailed as a (i)______ achievement, yet historians now see its provisions as largely (ii)______, since few were ever enforced. || Blank (ii) has the clearest clue: "few were ever enforced" → weak → toothless. || "Hailed" → blank (i) is positive → landmark. || Read the whole sentence back. || => landmark … toothless
# Decide the relationship between the blanks
! Do the two blanks point the same way (no shift) or opposite ways (a shift word between them)?
EX: Her early essays were (i)______, crammed with digressions; her later work, by contrast, is a model of (ii)______. || "By contrast" → the blanks are opposites. || Digressions → convoluted. Opposite → clarity. || => convoluted … clarity
x Wrong answers often fit one blank perfectly. Always read the full sentence with both words in place.
> If you cannot decide one blank, eliminate choices in the other blank first - two right choices can only come from one logical story.
Q: Though the novel's plot is (i)______, its characters are so (ii)______ that readers hardly notice the lack of suspense. => predictable … compelling
""")

note('vocab_context', 'Vocabulary in context: second meanings and roots', 12, """
# Words the GRE uses in a second meaning
| Word | Everyday meaning | GRE meaning |
| temper | anger | moderate, soften |
| qualify | be eligible | limit, add reservations |
| check | look at | restrain, stop |
| economy | money system | efficient use (of words, means) |
| sanction | penalty | approve - OR penalise |
| champion | winner | support, defend |
| pedestrian | walker | dull, ordinary |
| arrest | detain | stop; catch attention ("arresting") |
| intimate | close | hint, suggest |
| appreciate | be grateful | increase in value |
> If a familiar word appears among hard choices, ask whether its second meaning fits.
# Roots that help you guess
| Root | Meaning | Examples |
| bene | good | benevolent, beneficial |
| mal | bad | malicious, malign |
| loqu / log | speak | loquacious, eloquent |
| chron | time | chronic, anachronism |
| path | feeling | apathy, empathy |
| ambi | both | ambivalent, ambiguous |
| vor | eat | voracious, omnivore |
| cred | believe | credulous, incredulous |
x Roots are clues, not proof: "pedestrian" is not about feet on the GRE.
# How to learn a word properly
- Learn the GRE sense, not every sense.
- Learn it with a partner word: laconic ↔ verbose, placate ↔ provoke.
- Make your own sentence that would only make sense with that word.
Q: "The editor tempered her criticism." Meaning? => softened / moderated it
Q: A "credulous" reader is…? => too ready to believe things
""")

note('tc_triple', 'Text completion 4: three-blank questions', 12, """
# Treat it as a paragraph puzzle
Three-blank questions are often a short paragraph. Read it all, then summarise its story in one sentence of your own.
# Find the anchor blank
One blank usually has a direct clue. Solve it first, then follow the logic to the others.
EX: The report was anything but (i)______: rather than (ii)______ the agency's failures, it (iii)______ them in exhaustive detail. || Anchor: "in exhaustive detail" → (iii) documented. || "Rather than" → (ii) is the opposite of documenting → gloss over. || "Anything but" → the report did not hide things → (i) evasive. || => evasive … gloss over … documented
# Track the shifts across sentences
A "but", "yet", "however" or "in fact" between sentences flips the direction from one blank to the next.
# Check the whole chain
x A wrong answer often fits two blanks perfectly and breaks the third. Read the whole paragraph with all three words before moving on.
> Budget about 2 minutes. If one blank is impossible, get the other two right and pick the remaining one that keeps the story consistent.
Q: Because the founder was usually (i)______ about risk, investors were surprised when she (ii)______ the entire reserve on an untested product. => cautious … staked
""")

note('se', 'Sentence equivalence: two answers, same meaning', 12, """
# What SE tests
One blank, six choices; pick the TWO that produce sentences alike in meaning. Both must be right - no partial credit.
# The method
- 1. Treat it like a one-blank text completion: find the clue, predict your own word.
- 2. Find TWO choices that both match your prediction.
EX: Known for her ______, the diplomat rarely revealed her opinions. (reticence / reserve / candor / garrulousness / impatience / enthusiasm) || Clue: rarely revealed her opinions → "keeping quiet". || => reticence, reserve
# The trap pair
x Most SE questions contain a pair of synonyms that does NOT fit the sentence. Never pick a pair just because the two words match each other.
EX: The evidence, though suggestive, remains ______. (tentative / provisional / conclusive / decisive / abundant / irrefutable) || "Though suggestive" → not settled yet. || conclusive / decisive match each other but reverse the meaning (trap). || => tentative, provisional
# When only one word fits
If you find only one match, re-read the sentence - you may have the logic slightly wrong - or look for a word used in a second meaning.
> SE answers do not have to be exact synonyms; they must give the sentence the same meaning.
Q: The rescue team's ______ efforts, continuing through three nights without rest, saved all twelve miners. => tireless, indefatigable
Q: Critics dismissed the film as ______, a lazy imitation of better movies. => derivative, unoriginal
""")

note('verbal_pacing', 'Verbal timing: TC + SE under the clock', 8, """
# Time budget
| Question | Target time |
| One-blank TC, SE | about 1 minute |
| Two-blank TC | about 1.5 minutes |
| Three-blank TC | about 2 minutes |
| RC question (after reading the passage) | about 1 minute each |
Verbal section 1: 12 questions in 18 minutes - 1.5 minutes per question on average.
# Order of attack
- Do the TC and SE questions first - they are quicker - but answer every question as you go.
- Read RC passages once, carefully, then answer.
- Mark and move on after 2 minutes; come back at the end.
# After every timed set
Sort each mistake: did you misread the logic, or not know a word? Logic errors → practise the method. Vocab errors → add the word to your flashcards.
""")

note('rc_method', 'Reading comprehension 1: how to read a GRE passage', 15, """
# What the passages are like
Short (1 paragraph) to long (4-5 paragraphs) passages on science, social science, humanities and business. About half of verbal questions are RC.
# Read for structure, not detail
You will look details up later. While reading, track:
- The MAIN POINT - what is the author mostly saying?
- The ROLE of each paragraph or sentence - background, claim, evidence, counter-argument, conclusion.
- The author's ATTITUDE - positive, negative, mixed, neutral?
! Turn words signal the main point: however, but, yet, recent studies suggest, this view is incomplete. The author's own view usually comes after the turn.
# Make a quick map
Write 3-5 words per paragraph: "P1: old view - letters reliable. P2: but reputation bias. P3: still useful, differently."
# Main idea / primary purpose questions
! The right answer covers the whole passage, not just one paragraph, and matches the author's strength of opinion.
! Purpose answers start with a verb: argue, describe, challenge, qualify, explain, compare.
x Too narrow (one detail), too broad (more than the passage covers), or too extreme ("prove", "refute completely") are the usual wrong answers.
EX: A passage says historians treated merchants' letters as reliable; "a closer reading complicates this view"; the letters remain valuable as evidence of how merchants wished to be seen. Primary purpose? || Turn: "a closer reading complicates this view". || The author does not reject the letters - "remain valuable, but…". || => to revise (qualify) a traditional view of a historical source
Q: What is the job of a sentence that begins "Admittedly, …"? => A concession - the author grants a point to the other side before continuing
""")

note('rc_types', 'Reading comprehension 2: question types', 15, """
# Detail ("according to the passage")
The answer is stated. Go back and find the line - never answer from memory. The right answer is a paraphrase of that line.
# Inference ("suggests", "implies", "most likely agree")
! The right answer must be TRUE based on the passage - a small, safe step, never a big leap.
x Extreme words (always, never, all, only, must) are usually wrong unless the passage is equally extreme.
# Function ("serves to", "in order to", "primarily to")
Why is this sentence or example there? Read the sentences before and after it. Typical roles: illustrate a claim, concede a point, introduce a contrast, give evidence.
# Attitude and tone
GRE authors are usually moderate: "qualified appreciation", "measured scepticism" beat "outrage" or "uncritical praise".
# Special formats
! Select all that apply: three choices, any number can be right (1, 2 or 3). Judge each on its own. No partial credit.
! Select-in-passage: click the sentence that does a described job. Match the function exactly - an example is not a conclusion.
EX: "Such letters remain valuable, but less as ledgers than as evidence of how merchants wished to be seen." The author's attitude? || "Remain valuable" = positive. || "but less as ledgers" = a reservation. || => qualified appreciation
Q: An answer choice says the author "proves" a theory, but the passage says the evidence "suggests" it. Keep or eliminate? => Eliminate - too strong
""")

note('rc_long', 'Reading comprehension 3: long passages', 12, """
# The challenge
Long passages test stamina and organisation. You will get 3-4 questions on one passage.
# Strategy
- Read the first question stem before the passage only if it points to a specific detail; otherwise read first.
- Write a 3-word summary for each paragraph as you go.
- Mark the author's opinion words (unfortunately, compelling, overlooked) - tone questions depend on them.
- Use your map to jump straight to the right paragraph for each question.
> Spend about 3 minutes reading a long passage. That pays off across 3-4 questions.
x Do not reread the whole passage for each question - that is where time disappears.
# Typical long-passage structures
- Old view → new evidence → new view (the most common).
- Problem → several proposed solutions → the author's evaluation.
- A phenomenon → competing explanations → which explanation the author prefers.
Q: In "old view → new evidence → new view" passages, where is the main point? => In the new view, usually after the turn word
""")

note('cr1', 'Critical reasoning 1: arguments, assumptions, weaken and strengthen', 15, """
# Anatomy of an argument
! Conclusion = what the author wants you to believe (signals: so, therefore, thus, clearly, hence).
! Evidence = the facts given to support it (because, since, as shown by).
! Assumption = the unstated idea that connects them - the GAP.
EX: "Restaurant X is adding a delivery service, so its revenue will rise." Find the gap. || Conclusion: revenue will rise. Evidence: adding delivery. || Gap: delivery orders must be NEW business, not just replacing dine-in orders. || => Assumption: delivery won't merely replace existing orders
# The negation test for assumptions
Negate the answer choice. If the argument falls apart, it was the assumption.
# Weaken questions
Accept the evidence as true; attack the gap.
! Most common weakener: an ALTERNATIVE CAUSE for the result.
! Others: the cause happened but the effect did not (or vice versa) elsewhere; reverse causation; an unrepresentative sample.
EX: "Accidents fell 30% after speed cameras went up on Main Street, so the cameras caused it." What weakens it? || Look for another cause or a comparison. || => Accidents fell just as much on streets without cameras
# Strengthen questions
Close the gap: rule out an alternative cause, or add a comparison group.
! "Where the change did not happen, the result did not happen either" is a classic strengthener.
x Out-of-scope answers can sound sensible but do not touch the link between evidence and conclusion.
Q: "Students who take a review course score higher, so the course works." A strengthener? => Before the course, students who enrolled had similar grades to those who did not
""")

note('cr2', 'Critical reasoning 2: paradox, flaws, boldface and inference', 15, """
# Paradox / "resolve the discrepancy"
Two facts seem to conflict. The right answer explains how BOTH can be true.
EX: Bus fares were cut in half, yet fare revenue rose. Explain. || Revenue = fare × riders. || If riders more than doubled, revenue rises. || => Ridership more than doubled
# Common flaws
| Flaw | Example |
| Reversing a conditional | All club members are good at maths; Ana is good at maths, so she is a member |
| Correlation ≠ causation | Cities with more police have more crime, so police cause crime |
| Unrepresentative sample | Cycling-magazine readers favour bike lanes, so the city does |
| Part to whole | Every player is excellent, so the team is excellent |
| Attacking the person | Her argument is wrong because she was once fired |
# Boldface (role) questions
Label each bold (or bracketed) part BEFORE reading the choices: main conclusion, intermediate conclusion, evidence, opposing view, or evidence against a view.
! "Therefore" marks a conclusion; "however" often introduces evidence against what came before.
# Inference / must be true
Chain the statements and take only what follows with certainty.
EX: No reptile in the zoo is fed live prey. Every animal in the south wing is a reptile. What must be true? || South wing → reptile → not fed live prey. || => No south-wing animal is fed live prey
x Do not reverse the arrows: "every south-wing animal is a reptile" does not mean every reptile is in the south wing.
Q: "If it rains, the match is cancelled. The match was cancelled, so it rained." Valid? => No - reversing the conditional (it could be cancelled for another reason)
""")

note('cr_in_rc', 'Arguments inside reading passages', 8, """
# Short argument passages
About 1-3 verbal questions per test are short argument passages - the CR question types appear inside RC.
# Read the question stem first
For argument passages, read the question first ("which weakens…", "the argument assumes…") so you read the passage with a purpose.
# Same method as CR
Conclusion → evidence → gap. Then predict what the right answer must do before reading the choices.
x Eliminate choices that are out of scope (about a different time, group or issue), even when they sound reasonable.
""")

note('tc_hard', 'Hard text completions', 10, """
# Why hard TCs are hard
- The clue is hidden or spread across the sentence.
- Double negatives and subtle shifts.
- Second meanings in the choices.
- All choices are hard words.
# Approach
- Paraphrase the sentence in very simple words before predicting.
- Mark every shift and negation; count them - two reversals cancel.
- If you do not know a choice, do not pick it just because it is unfamiliar; eliminate the words you do know first.
EX: Critics who dismissed the theory as mere speculation have been ______ by a decade of confirming experiments. || Paraphrase: critics said "just a guess"; experiments proved the theory. || So the critics were proved WRONG. || => confounded (not "vindicated", which would describe the theory's supporters)
> After each hard TC, write the one word or phrase that was the real clue. That trains you to spot it.
""")

note('rc_science', 'Reading science passages', 10, """
# Do not panic about the content
You do not need to understand every term. Track what each paragraph DOES: describe a phenomenon, report a finding, challenge a theory, propose an explanation.
# Typical structure
Phenomenon → old explanation → new evidence → revised explanation → limitations / open questions.
# Question tips
- Detail questions: find the exact sentence - science passages are full of similar-sounding details.
- "The author would most likely agree": pick the cautious statement supported by the text.
x Choices that use outside science knowledge, or go further than the passage, are wrong even if true in real life.
EX: A passage says corals that experience brief heat spikes bleach less readily, and skeptics doubt this survives steady warming. "Which can be inferred?" || Supported: a coral's heat tolerance is not fixed by species alone. || Not supported: nursery corals have already restored reefs (only proposed). || => Pick the statement the text directly supports
""")

note('rc_humanities', 'Reading humanities and social-science passages', 10, """
# These passages are about viewpoints
Separate the AUTHOR'S view from the views the author describes ("some critics argue…", "it has been claimed…").
! Phrases like "it is often said", "traditionally", "many historians believe" introduce a view the author will usually challenge or qualify.
# Social science = arguments
These passages often contain a claim and evidence - use the CR method (conclusion → evidence → gap).
# Tone
Authors are measured: "qualified support", "measured criticism", "sympathetic but not uncritical".
EX: "Such features are easier to understand once we recall how these novels were published… This is not to say serial publication excuses every weakness." The author's attitude? || Defends the novels' features, but admits a limit. || => sympathetic but not uncritical
""")

note('awa', 'The Issue essay: structure and scoring', 15, """
# The task
One "Analyze an Issue" essay in 30 minutes. You are given a claim and must take a position and support it. Scored 0-6.
# What earns a high score
- A clear position (you may agree, disagree or take a qualified middle position).
- Specific, well-developed examples - not vague generalities.
- Logical organisation with clear transitions.
- Control of language: varied sentences, precise words. Small errors are fine.
x Length alone does not score - but very short essays (under ~350 words) cannot develop ideas enough for a 4+.
# A 30-minute plan
| Time | Do |
| 0-5 min | Decide your position; jot 2-3 examples and one counter-argument |
| 5-27 min | Write: intro → 2-3 body paragraphs → counter-argument → conclusion |
| 27-30 min | Proofread |
# Structure
- Introduction (3-4 sentences): restate the issue in your words and give your thesis.
- Body paragraphs: one example each - say what happened, then explain HOW it supports your thesis.
- Counter-argument: "Admittedly, … However, …" - acknowledge the other side, then answer it.
- Conclusion (2-3 sentences): restate the thesis with a little nuance.
> Good example sources: history, science and technology, business, literature, and your own engineering or work experience.
""", subject='writing')

note('awa_examples', 'Building strong examples for essays', 10, """
# Specific beats general
x "Many companies have failed and learned from it." - vague.
! "When Nokia dismissed touch-screen phones in 2007, it lost most of its market within five years - a failure that later reshaped its strategy towards networks." - specific and explained.
# Build an example bank before test day
Prepare 6-8 flexible examples you know well, each usable for several kinds of prompts:
- A scientific discovery (e.g. penicillin found by accident; vaccines).
- A business success and failure (e.g. a company that adapted vs one that did not).
- A historical leader or movement.
- A technology with good and bad effects (social media, automation, the internet).
- An education or personal example from your engineering studies or work.
# Explain, don't just mention
Each example needs 3 parts: what happened → why it matters → how it supports your thesis.
""", subject='writing')

note('awa_counter', 'Counter-arguments, qualification and polish', 10, """
# Why the counter-argument matters
High-scoring essays "consider ways the statement might or might not hold true". Showing the other side - and answering it - shows mature reasoning.
! Template: "Admittedly, [the strongest point for the other side]. However, [why your position still holds, or when it applies]."
# Qualified positions often score best
"Leaders should be judged mainly by results" → "Results matter most in the short term, but methods determine whether results last."
# Polish
- Vary sentence length; avoid starting every sentence with "I think".
- Use transitions: however, moreover, consequently, admittedly, ultimately.
- Spend the last 3 minutes fixing errors that change meaning.
""", subject='writing')

note('verbal_section', 'Verbal section strategy and pacing', 8, """
# The clock
Section 1: 12 questions in 18 minutes. Section 2: 15 questions in 23 minutes - about 1.5 minutes per question.
# A plan
- Answer every question as you meet it - mark the ones you are unsure about.
- TC and SE: about 1 minute each; two/three blanks 1.5-2 minutes.
- RC: read the passage once well (2-3 minutes for a long one), then about 1 minute per question.
- Last minute: no blanks - guess on anything left.
x Do not reread a passage for every question; use your paragraph map.
""", subject='strategy')

note('mock_review', 'How to take and review a practice test', 10, """
# Taking it
- Same time of day as your real test, in one sitting, timed, no phone, no pausing.
- Use the official order: essay, then the sections.
# Reviewing it (this is where the score improves)
- Review EVERY question: wrong ones, and right ones you guessed.
- For each miss, decide why: concept, careless, timing, vocab, misread.
- Write the rule you will use next time.
- Add the result to the app (Test results tab) so the predictor and your weak topics update.
> A 3-hour test needs about 2 hours of review. A test you do not review is mostly wasted.
# What to look at
- Did you run out of time? In which section?
- Which question types and topics cost the most points?
- Did section 2 feel harder (good - you earned the harder section) or easier?
""", subject='strategy')

note('test_day', 'Test day checklist', 6, """
# The day before
- Light review only - formula sheet, error-log rules. No new topics.
- Check your appointment, ID (the name must match your ETS account exactly) and the route or, for the home test, the room and system check.
- Sleep 8 hours.
# On the day
- Eat, arrive (or log in) early.
- During the test: mark and move, never stay stuck; no blanks.
- Between sections, breathe - one bad section does not decide your score.
# Scores
- You see unofficial Verbal and Quant scores at the end; official scores (with Writing) arrive in about 8-10 days.
- You can send free score reports to up to 4 institutions on test day - have the codes ready.
""", subject='strategy')
