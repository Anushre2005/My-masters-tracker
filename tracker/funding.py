"""Scholarships, fellowships, assistantships and loan-scholarships per programme, for an Indian applicant.

Researched 2026-11-17 from the official pages linked in each entry (2026-27 / 2027-28 cycles). Rules used:
- Amounts, dates and criteria are only those stated on the official page. Anything not stated there, or only found
  on third-party sites, is written as "check".
- Deadlines are for the CURRENT cycle (for 2027 entry). The task due dates added to the tracker are PROJECTED to the
  same date one or two years later for Fall 2029 entry - always confirm when the next cycle opens.
- `fit` is a first read of eligibility for an Indian applicant with a strong B.Tech CS record and under two years of
  work experience at application time. Re-check against your own profile when you apply.

Each award: name, by, kind (University merit | Need-based | Assistantship | External award | Loan scholarship),
amount, deadline, eligibility, steps (list), prepare (list), link, fit ('likely' | 'check' | 'unlikely'), fit_note.
"""
from . import db

CHECKED = '2026-11-17'

COUNTRY = {
    'US': ['P01', 'P02', 'P05', 'P09', 'P10', 'P17', 'P18', 'P22', 'P23', 'P24', 'P25', 'P26', 'P27', 'P28', 'P29'],
    'UK': ['P03', 'P07', 'P11', 'P15'], 'Canada': ['P06', 'P12'], 'Singapore': ['P04', 'P16'],
    'Germany': ['P08', 'P14'], 'Netherlands': ['P13'], 'Switzerland': ['P19'], 'Australia': ['P20'], 'France': ['P21'],
}
ALL = [p for ps in COUNTRY.values() for p in ps]
TWO_YEAR_US = ['P17', 'P18', 'P22', 'P23', 'P24', 'P26', 'P28', 'P29']  # >= 1 full year left after year 1 (verify per programme)
BIOTECH = ['P23', 'P24', 'P25', 'P26', 'P27', 'P28', 'P29']

# ---------------------------------------------------------------- external awards (apply to several programmes)
EXTERNAL = {
    'jn_tata': dict(
        name='J N Tata Endowment loan scholarship', by='J N Tata Endowment (Tata Trusts)', kind='Loan scholarship',
        amount='Up to Rs 20 lakh (not everyone gets the maximum). Loan at 2% simple interest, repaid in equal instalments from year 3 to year 7. Selected scholars may also get a travel grant and gift award from allied Tata Trusts.',
        deadline='2026 cycle: applications 5 Jan - 15 Mar 2026 (FAQ); the Selection Process page says Phase 1 ends 29 Mar 2026 - check which applies. Apply in Jan-Mar of the year you start.',
        eligibility='Indian citizen; not older than 45; graduate of a recognised Indian university with at least 60% average; full-time postgraduate study abroad. You may apply before you have an admit (update them by email once admitted). Final-year students can apply.',
        steps=['Create a login on jntataendowment.org when applications open (January) and fill the online form (save drafts).',
               'Phase 1: submit personal/academic details, work experience and an SOP (max 800 words) plus documents.',
               'Phase 2: online aptitude test (critical thinking / problem solving; a mock test is provided).',
               'Phase 3: interview with a subject expert - upload admission letter and supporting documents first.',
               'Phase 4: final selection; sign the loan-scholarship agreement with a guarantor.'],
        prepare=['SOP, max 800 words: why this field and university, how it ties to your degree, work and short/long-term goals (no biography, no plagiarism)',
                 'One recommendation letter (professor or employer) addressed to "The Trustees of the J. N. Tata Endowment", submitted online by the recommender',
                 'Photo 500x500 jpeg, masked Aadhaar, passport (first and last page), marksheets/transcripts as greyscale PDFs',
                 'Working professionals: experience certificate from previous employer, appointment letter, latest ITR or 3 payslips',
                 'For the interview: admission letter, final-year marksheets and degree certificate, GRE/GMAT/TOEFL/IELTS scorecards, prizes/ranks, extracurricular certificates, one research/project report, resume, cost of education, source of funds',
                 'After selection: PAN, cancelled cheque, guarantor photo, PAN, masked Aadhaar and income proof/ITR'],
        link='https://jntataendowment.org/faqs/', fit='likely', fit_note='You meet the 60% / Indian-degree rules. Any country and field.',
        task=('2029-01-05', 'J N Tata Endowment: apply (window projected ~5 Jan - 15 Mar 2029) - SOP 800 words, 1 LoR', 60),
        programs=ALL),
    'kc_mahindra': dict(
        name='K C Mahindra Scholarship for Postgraduate Studies Abroad', by='K. C. Mahindra Education Trust', kind='Loan scholarship',
        amount='Interest-free loan scholarship: up to Rs 10 lakh for the top 3 (K. C. Mahindra Fellows), up to Rs 5 lakh for other awardees; at least 50 awards a year.',
        deadline='2026 cycle closed 30 Apr 2026, 6 pm (for programmes starting Aug 2026 - Feb 2027). Expect a similar window in the spring before you start.',
        eligibility='Indian citizen; First-Class degree (or equivalent diploma) from a recognised university; enrolled in a postgraduate programme starting in the stated window. Final-year students can apply if they show a first-class result by end of June.',
        steps=['Watch kcmet.org from about January of your start year for the new cycle.', 'Apply online before the deadline (about 30 April).',
               'Follow the Trust\'s FAQs for the selection steps - check (not described on the main page).'],
        prepare=['Proof of first-class degree (marksheets / provisional certificate)', 'Admission letter for a programme starting in the window',
                 'Other documents as listed in the KCMET FAQs - check'],
        link='https://www.kcmet.org/what-we-do-Scholarship-Grants.aspx', fit='likely', fit_note='Your CGPA is first class; programme must start Aug-Feb.',
        task=('2029-04-30', 'K C Mahindra PG abroad scholarship: apply (projected deadline ~30 Apr 2029 - check kcmet.org)', 30),
        programs=ALL),
    'nsf_pg': dict(
        name='Narotam Sekhsaria Foundation PG Scholarship', by='Narotam Sekhsaria Foundation', kind='Loan scholarship',
        amount='Repayable, interest-free financial assistance. Amount not stated on the official page - check.',
        deadline='Applications are invited in January each year (2026 cycle: interviews Apr-Jun 2026, in-person orientation in Mumbai in July).',
        eligibility='Indian national living in India; below 30 years of age (as of 31 Jan of the application year); graduate of an accredited Indian university (final-year / awaiting results is fine); postgraduate study in India or abroad starting that fall. You can apply while awaiting admits; the award depends on securing admission.',
        steps=['Register on pg.nsfoundation.co.in in January.', 'Pay the Rs 500 non-refundable fee to open the form.',
               'Fill "Full Application Part 1-2-3" and submit.', 'If shortlisted, upload the documents below.',
               'Attend the interview (Apr-Jun) and, if selected, the mandatory orientation in Mumbai (July).'],
        prepare=['Attested marksheets of all UG years', 'Attested scorecards (GRE/GMAT etc.)', 'University acceptance letter with the fee structure',
                 'Reference letters', 'Proof of any other funding / scholarship / fee waiver', 'Latest income tax return of the co-applicant', 'Attested passport copy'],
        link='https://pg.nsfoundation.co.in/application-process/', fit='likely', fit_note='Age and degree rules fit; interview + July orientation in Mumbai.',
        task=('2029-01-31', 'Narotam Sekhsaria PG scholarship: apply in January 2029 (Rs 500 fee) - check exact dates', 30),
        programs=ALL),
    'inlaks': dict(
        name='Inlaks Shivdasani Scholarship', by='Inlaks Shivdasani Foundation', kind='External award',
        amount='Covers tuition, living expenses, one-way travel, visa and health allowance, up to US$120,000.',
        deadline='2026 round is closed; review of applications in April, interviews in May (Mumbai). Applications open early in the year you start - check the exact window.',
        eligibility='Indian passport holder resident in India; age limit (2026 round: born on or after 1 Jan 1996); Indian degree; sciences/maths need 70% / CGPA 7.2; you must ALREADY HAVE AN ADMIT (conditional OK) at a top university in the UK, Europe or USA. EXCLUDED subjects: Business and Finance, Computer Science, Engineering (except at Imperial), Management/MBA, Medicine and some others.',
        steps=['Get your admit first (a conditional offer is enough; meet any English-test condition before applying).',
               'When the form opens, apply via "Apply Now" on the Inlaks page and follow the downloadable application instructions.',
               'Stage 1: application review (April). Stage 2: online preliminary interview (May). Stage 3: final in-person interview in Mumbai (May).'],
        prepare=['Offer letter (conditional or unconditional)', 'Academic records showing the minimum grade', 'Documents listed in the yearly application-instructions PDF - check'],
        link='https://inlaksfoundation.org/opportunities/scholarship/', fit='check',
        fit_note='Business, computer science and engineering are excluded - so the business-analytics/AI programmes do NOT qualify. Biotech/life-science programmes may; programmes run by engineering schools are doubtful - confirm with the Foundation.',
        task=('2029-02-28', 'Inlaks: check 2029 window and subject eligibility for biotech admits (needs an offer letter)', 30),
        programs=COUNTRY['US'] + COUNTRY['UK'] + COUNTRY['Germany'] + COUNTRY['Netherlands'] + COUNTRY['Switzerland'] + COUNTRY['France']),
    'aga_khan': dict(
        name='Aga Khan Foundation International Scholarship Programme', by='Aga Khan Foundation', kind='Need-based',
        amount='Covers tuition and living expenses; 50% grant and 50% loan (repaid with a service charge, starting 6 months after graduation). Amount depends on need.',
        deadline='The 2026-27 cycle is closed; the next cycle opens in early 2027 - check dates.',
        eligibility='From a listed country (India is listed); excellent academic record; genuine financial need and a multi-source funding plan; admitted to a reputable postgraduate programme and starting its first year; leadership/volunteer record. Preference for under-30s. NOT available for study in the United Kingdom.',
        steps=['Use the eligibility tool on the AKDN page and contact the local AKF team for India.', 'Apply in the annual cycle (opens early in the year).',
               'Treat it as a last-resort source: show the other funding you have applied for.'],
        prepare=['Admission letter', 'Funding plan covering all years with other sources', 'Proof of financial need', 'Evidence of leadership, work and volunteering', 'Guarantor to co-sign the award agreement'],
        link='https://the.akdn/en/what-we-do/developing-human-capacity/education/international-scholarships', fit='check',
        fit_note='Need-based; you must show genuine financial need. Not for UK programmes.',
        task=None, programs=[p for p in ALL if p not in COUNTRY['UK']]),
    'aauw': dict(
        name='AAUW International Fellowship (master\'s)', by='American Association of University Women', kind='External award',
        amount='US$20,000 stipend for a master\'s (paid in two instalments).',
        deadline='2027-28 cycle: applications 17 Aug - 17 Sep 2026 (5 pm ET); results March 2027.',
        eligibility='Women who are not US citizens/permanent residents; FIRST master\'s in a STEM field (data science, information science, bioinformatics, biotechnology etc. are listed); already admitted or enrolled at the time of application; full-time at an accredited US institution; minimum GPA 3.5/4 on the highest degree; programme must start by 15 Sep and end on/after 30 Apr of the award year.',
        steps=['Because you must already be admitted when you apply (Aug-Sep), the realistic route for Fall 2029 entry is to apply in Aug-Sep 2029 for your SECOND year (programme must run until at least 30 Apr 2030).',
               'Apply online in the Aug-Sep window on aauw.org.', 'Award notification in March; report mid-year and at the end.'],
        prepare=['Admission/enrolment letter (or deferral approval)', 'Transcripts showing GPA (check how your CGPA converts to the 3.5/4 minimum)',
                 'Statements: academic/professional plan, commitment to women and girls (examples), long-term STEM career goals and impact at home',
                 'Financial plan: expenses, confirmed and pending funding, remaining gap', 'Recommendations - check current requirements'],
        link='https://www.aauw.org/resources/programs/fellowships-grants/aauw-international-fellowships/', fit='check',
        fit_note='Women + STEM + GPA fit. Business-school MSBA degrees count only if formally STEM-classified - check each programme.',
        task=('2029-08-17', 'AAUW International Fellowship: apply 17 Aug - 17 Sep 2029 for year 2 (2-year US STEM programmes only) - check dates', 7),
        programs=COUNTRY['US']),
    'peo_ips': dict(
        name='P.E.O. International Peace Scholarship', by='P.E.O. International', kind='Need-based',
        amount='Up to US$12,500 (lesser amounts by need).',
        deadline='Applications 15 Sep - 15 Dec each year; awards announced in May.',
        eligibility='Women from outside the US/Canada seeking a graduate degree at an accredited US or Canadian institution; will return home; must have a full year of coursework remaining and be enrolled and in residence for that whole year; need-based. Not for online courses or research-only.',
        steps=['Apply in your first year (15 Sep - 15 Dec) for the following year - so it suits 2-year programmes.', 'Use the IPS form linked on the P.E.O. page.', 'Show other resources (family funds, assistantships, other scholarships) that cover the rest.'],
        prepare=['Enrolment proof', 'Budget showing other funding sources', 'Items listed in "IPS Policies, Prerequisites and Procedures" PDF - check'],
        link='https://www.peointernational.org/educational-support/international-peace-scholarship-fund/eligibility-and-application-process/', fit='check',
        fit_note='Only usable for the second year of a 2-year programme; need-based; you commit to return to India.',
        task=('2029-09-15', 'P.E.O. IPS: apply 15 Sep - 15 Dec 2029 for year 2 (2-year US/Canada programmes)', 7),
        programs=COUNTRY['US'] + COUNTRY['Canada']),
    'fulbright_nehru': dict(
        name='Fulbright-Nehru Master\'s Fellowship', by='USIEF', kind='External award',
        amount='check', deadline='check',
        eligibility='CHECK: on 17 Nov 2026 the official USIEF list of fellowships for Indian citizens did NOT include a Master\'s fellowship (only doctoral, postdoctoral, academic & professional excellence, Humphrey and others). Earlier cycles required 3 years of full-time work experience after the bachelor\'s.',
        steps=['Re-check the USIEF list in early 2028 to see whether a master\'s category returns.'], prepare=[],
        link='https://usief.org.in/fulbright-fellowships/fellowships-for-indian-citizen/', fit='unlikely',
        fit_note='Not currently offered as far as the official list shows; and earlier rules needed 3 years of work (you will have ~21 months).',
        task=None, programs=COUNTRY['US']),
    'chevening': dict(
        name='Chevening Scholarship', by='UK government (FCDO)', kind='External award',
        amount='Fully funded one-year UK master\'s (tuition, living allowance, travel) - see "what a Chevening award covers" on chevening.org.',
        deadline='2027-28 cycle: opened August 2026, closed October 2026 (11:00 UTC; date on the India country page). Interviews Mar-Apr, results mid-June, unconditional offer by 8 Jul 2027.',
        eligibility='Citizen of an eligible country (India); return home for 2 years after; at least 2 years\' work experience after the undergraduate degree (2,800 hours); undergraduate degree FINISHED at least two years before the application deadline; apply to three eligible UK courses and hold one unconditional offer by the July deadline.',
        steps=['Check eligibility timing: with a 2027 graduation, the October 2028 round is less than 2 years after your degree - you would qualify from the October 2029 round (for 2030 entry).',
               'Apply on chevening.org (August-October) with three UK course choices.', 'Shortlisted candidates upload documents 7 working days before the interview (Mar-Apr).'],
        prepare=['Four essays (leadership, networking, why the UK/courses, career plan) - check current questions', 'Two reference letters', 'Photo ID, degree certificate', 'Three UK course applications'],
        link='https://www.chevening.org/resource-hub/guidance/eligibility/', fit='unlikely',
        fit_note='For Fall 2029 entry you would apply in Oct 2028: under 2 years after your degree, so not eligible that round.',
        task=None, programs=COUNTRY['UK']),
    'commonwealth': dict(
        name='Commonwealth Master\'s Scholarship', by='Commonwealth Scholarship Commission (UK)', kind='Need-based',
        amount='Full tuition, return airfare, stipend GBP 1,712/month (GBP 2,000/month in London), study travel grant.',
        deadline='2027-28 cycle closed Tuesday 20 October 2026; nominators set earlier deadlines and nominate by December.',
        eligibility='Citizen and permanent resident of an eligible country (India is listed); available to start in September; first degree of at least 2:1 standard; unable to afford UK study without the scholarship; study linked to one of the six CSC development themes; must apply both to the CSC (CSC Central) AND to a nominator (national nominating agency or listed NGO).',
        steps=['Apply for admission to your UK courses first.', 'Find the Indian nominating agency and its own (earlier) deadline.', 'Complete the CSC Central application (development impact statement in four parts) and get references uploaded by the deadline.', 'Nominator shortlists; CSC selects.'],
        prepare=['Passport', 'Full transcripts of all higher education', 'Three referees (current employer if applicable; at least two references uploaded)', 'Development Impact statement (four parts)', 'Employment history and up to 10 publications/prizes'],
        link='https://cscuk.fcdo.gov.uk/scholarships/commonwealth-masters-scholarships/', fit='check',
        fit_note='Need-based and development-focused; must justify financial need and a development theme.',
        task=('2028-10-20', 'Commonwealth Master\'s Scholarship (UK): CSC deadline projected ~20 Oct 2028; nominator deadline earlier - check', 45),
        programs=COUNTRY['UK']),
    'great': dict(
        name='GREAT Scholarship (India)', by='British Council + UK universities', kind='External award',
        amount='GBP 10,000 towards tuition for a one-year taught postgraduate course.', deadline='Set by each participating university - check.',
        eligibility='Students from India (one of 18 countries) at a PARTICIPATING university. 2026-27 list for India: Anglia Ruskin, Norwich Arts, Queen\'s Belfast, RCA, Bristol, Dundee, Kent, Reading and others - NOT Imperial, Warwick, UCL or Edinburgh.',
        steps=['Re-check the India list for 2029-30 when it is published.'], prepare=[],
        link='https://study-uk.britishcouncil.org/scholarships-funding/great-scholarships/india', fit='unlikely',
        fit_note='None of your UK universities offered it to Indian students in 2026-27.', task=None, programs=COUNTRY['UK']),
    'eiffel': dict(
        name='France Excellence Eiffel Scholarship', by='French Ministry for Europe and Foreign Affairs (via ESSEC)', kind='External award',
        amount='Per ESSEC: monthly allowance of EUR 1,200 plus one international return journey and social-security cover.',
        deadline='Institutions submit to Campus France by 6 Jan 2027 (2027 campaign); results from 12 Apr 2027. ESSEC nominates you - apply to the programme in the FIRST round.',
        eligibility='Non-French; master\'s applicants up to 29 years (Campus France) / no older than 30 when the committee meets (ESSEC page) - check. You cannot apply directly; ESSEC applies on your behalf.',
        steps=['Submit your ESSEC DSBA application in the first round.', 'ESSEC selects and submits Eiffel files; no separate student application.'],
        prepare=['A strong first-round programme application'],
        link='https://www.campusfrance.org/en/france-excellence-eiffel-scholarship-program', fit='likely',
        fit_note='Age fits; depends on ESSEC nominating you.', task=None, programs=['P21']),
    'charpak': dict(
        name='France Excellence Charpak Master Scholarship', by='Embassy of France in India / Campus France India', kind='External award',
        amount='EUR 860/month living allowance; visa and Campus France fee exemption; social security and health top-up; housing help; possible exemption from differentiated fees at public institutions (ESSEC is private - check).',
        deadline='check (Campus France India announces each year)',
        eligibility='Indian citizen or OCI; 30 or younger at application; studying/studied at an Indian institution; full-time master\'s in France (whole course in France); must have applied for admission first.',
        steps=['Apply for admission to the French programme.', 'Apply on scholarship.institutfrancaisindia.in with the documents below.'],
        prepare=['Formal photo', 'Passport first page', 'CV (max 2 pages)', 'Admission/acceptance letter (or email showing it is in process)', 'Class XII, bachelor\'s marksheets and degree', 'DELF/DALF if any', 'Employment/internship record', 'Signed recommendation letter(s) on letterhead'],
        link='https://www.inde.campusfrance.org/charpak-master-s-scholarship', fit='likely',
        fit_note='Fits your profile; note the DSBA has terms at partner campuses abroad, which the grant does not cover.',
        task=None, programs=['P21']),
    'nl_scholarship': dict(
        name='NL Scholarship (formerly Holland Scholarship)', by='Dutch Ministry of Education + universities', kind='External award',
        amount='EUR 5,000 in the first year.', deadline='Set by each participating institution.',
        eligibility='Non-EEA nationality; full-time bachelor\'s/master\'s at a PARTICIPATING institution. Erasmus University Rotterdam (RSM) is NOT on the 2027-28 list.',
        steps=['Re-check the participating list for 2029-30.'], prepare=[],
        link='https://www.studyinnl.org/finances/nl-scholarship', fit='unlikely', fit_note='RSM/Erasmus not participating in 2027-28.',
        task=None, programs=['P13']),
    'deutschland': dict(
        name='Deutschlandstipendium', by='German federal government + private sponsors (via the university)', kind='University merit',
        amount='check (the amount is set nationally - confirm on the university page)', deadline='check (each university runs its own call)',
        eligibility='Students at a German university, chosen for merit and social commitment; international students can apply - check the university\'s call.',
        steps=['After admission, apply through the university\'s scholarship office in its call period.'], prepare=['Transcripts', 'CV', 'Motivation letter - check the call'],
        link='https://www.uni-mannheim.de/en/scholarships/', fit='check', fit_note='Usually applied for after you are admitted/enrolled.',
        task=None, programs=COUNTRY['Germany']),
}

# ---------------------------------------------------------------- programme-specific awards
U = lambda **k: {'kind': 'University merit', 'fit': 'likely', 'fit_note': '', **k}  # noqa: E731
AUTO = ['Submit the programme application (early rounds give the best chance).', 'No separate scholarship form - all admitted applicants are considered.']
APP_PREP = ['Strong programme application: SOP/essays, resume, recommendations, transcripts, test scores']

PROGRAM = {
    'P01': [U(name='MIT Sloan MBAn fellowships', by='MIT Sloan', amount='Limited number; amount check', deadline='With the admission application',
              eligibility='Admitted MBAn candidates of all citizenships, judged on academic record, achievements and professional promise.',
              steps=AUTO, prepare=APP_PREP, link='https://mitsloan.mit.edu/master-of-business-analytics/admissions/tuition-and-financial-aid'),
            dict(name='Research / teaching assistantships', by='MIT Sloan faculty', kind='Assistantship', amount='Hours and pay vary - check',
                 deadline='After enrolment', eligibility='The MBAn office helps place students in RAs with Sloan faculty; TAs you find yourself.',
                 steps=['After admission, ask the MBAn Program Office about RA openings.'], prepare=['Resume highlighting ML/analytics skills'],
                 link='https://mitsloan.mit.edu/master-of-business-analytics/admissions/tuition-and-financial-aid', fit='likely', fit_note='')],
    'P02': [dict(name='Columbia Engineering / IEOR MS financial aid', by='Columbia University', kind='University merit', amount='check',
                 deadline='check', eligibility='The IEOR tuition page answers "What types of financial aid am I eligible for?" in its FAQ and points to Graduate Engineering aid - read it and confirm.',
                 steps=['Read the FAQ on the IEOR tuition page and the Graduate Engineering aid page.'], prepare=APP_PREP,
                 link='https://ieor.columbia.edu/tuition-and-fees', fit='check', fit_note='Not verified - the Columbia pages block automated reading.')],
    'P03': [U(name='Dean\'s Impact Scholarship', by='Imperial Business School', amount='GBP 25,000', deadline='Rolling by round - apply early (scholarships may run out)',
              eligibility='Academic excellence plus demonstrable impact or clear potential in entrepreneurship, technology & innovation, sustainability, social impact or leadership.',
              steps=['Submit the programme application.', 'You are then invited to submit a written assessment for scholarship consideration.'],
              prepare=['Written assessment (scholarship essay) with concrete impact examples', 'Strong programme application'],
              link='https://www.imperial.ac.uk/business-school/masters/business-analytics/fees-and-funding/'),
            U(name='Female Future Leaders Scholarship', by='Imperial Business School', amount='GBP 20,000', deadline='Rolling - apply early',
              eligibility='Female candidates with a strong record of achievement, leadership potential and commitment to contributing to their industry.',
              steps=['Submit the programme application; follow the scholarship instructions on the fees page (written assessment).'], prepare=['Leadership examples', 'Strong programme application'],
              link='https://www.imperial.ac.uk/business-school/masters/business-analytics/fees-and-funding/'),
            U(name='Imperial Excellence Scholarship', by='Imperial Business School', amount='Up to GBP 15,000', deadline='With the offer',
              eligibility='Most outstanding candidates (academic, professional, leadership), judged from application and interview.',
              steps=AUTO, prepare=APP_PREP, link='https://www.imperial.ac.uk/business-school/masters/business-analytics/fees-and-funding/'),
            U(name='Imperial Inspires Scholarship', by='Imperial College London', amount='GBP 15,000', deadline='Essay invitation from September of the application year',
              eligibility='Overseas-fee candidates meeting the minimum entry requirements.',
              steps=['Apply to the programme.', 'If eligible you are invited to complete an extra essay question (from September).'], prepare=['Extra essay'],
              link='https://www.imperial.ac.uk/business-school/masters/business-analytics/fees-and-funding/')],
    'P04': [dict(name='NUS BAC Global Scholarship', by='NUS Business Analytics Centre', kind='University merit', amount='check (third-party sites say S$30,000)',
                 deadline='check (msba.nus.edu.sg lists a scholarship deadline each year)', eligibility='International candidates; considered within the admission application; one scholarship per candidate, not combinable - check on the official page.',
                 steps=['Indicate scholarship interest in the GradApp admission application.'], prepare=APP_PREP,
                 link='https://nusgs.nus.edu.sg/scholarships/nus-bac-global-scholarship', fit='check',
                 fit_note='Official NUS pages sit behind a CAPTCHA, so nothing here could be verified - open the link yourself.')],
    'P05': [dict(name='McCombs MSBAi aid', by='UT Austin McCombs', kind='Need-based', amount='No merit scholarship listed on the official tuition page',
                 deadline='-', eligibility='International students: private loans (better terms with a US co-signer). Federal loans are for US citizens/PRs.',
                 steps=['Ask the McCombs financial aid team (FinancialAid@mccombs.utexas.edu) whether merit awards exist for international students - check.'],
                 prepare=[], link='https://www.mccombs.utexas.edu/graduate/specialized-masters/ms-business-analytics-and-artificial-intelligence/on-campus/admissions/tuition-financial-aid/',
                 fit='check', fit_note='Official tuition page mentions loans only.')],
    'P06': [U(name='Rotman MMA entrance awards', by='Rotman School', amount='CAD 5,000 - 25,000', deadline='With the admission application',
              eligibility='Future MMA students showing exceptional merit.', steps=AUTO, prepare=APP_PREP,
              link='https://rotman.utoronto.ca/programs/specialized-programs/master-of-management-analytics/tuition-scholarships/'),
            U(name='Award for female MMA students', by='Rotman School', amount='Up to CAD 10,000', deadline='With the admission application',
              eligibility='Future female MMA students with exceptional merit.', steps=AUTO, prepare=APP_PREP,
              link='https://rotman.utoronto.ca/programs/specialized-programs/master-of-management-analytics/tuition-scholarships/'),
            U(name='Vector Scholarship in Artificial Intelligence', by='Vector Institute', amount='About CAD 17,500', deadline='Nomination-based - check',
              eligibility='MMA / MMA-AI students (domestic and international) with first-class standing (min A- in the last two years).',
              steps=['Merit and nomination based - ask Rotman how nominations work.'], prepare=['Transcripts showing A- or better'],
              link='https://rotman.utoronto.ca/programs/specialized-programs/master-of-management-analytics/tuition-scholarships/', fit='check',
              fit_note='Check how your CGPA maps to A-.'),
            U(name='Innovation award', by='Rotman School', amount='CAD 4,000 (one award)', deadline='With the admission application',
              eligibility='Applicant showing interest or activities in innovation.', steps=AUTO, prepare=['Innovation examples in the application'],
              link='https://rotman.utoronto.ca/programs/specialized-programs/master-of-management-analytics/tuition-scholarships/')],
    'P07': [U(name='WBS UK and Commonwealth Scholarship', by='Warwick Business School', amount='Part of WBS scholarships covering up to 50% of tuition',
              deadline='Rolling - apply early', eligibility='Outstanding individuals from the UK and Commonwealth (India is Commonwealth).',
              steps=['Apply early - awards are competitive and given on a rolling basis.', 'Follow the scholarship instructions on the WBS scholarships page - check whether a separate form is needed.'],
              prepare=APP_PREP, link='https://www.wbs.ac.uk/courses/masters/scholarships/'),
            U(name='WBS High Potential Scholarship', by='Warwick Business School', amount='Up to 50% of tuition (range)', deadline='Rolling - apply early',
              eligibility='Academic standouts with extracurricular, volunteering or society leadership.', steps=['Apply early; see the scholarships page for how to be considered.'],
              prepare=['Evidence of extracurricular/volunteering impact'], link='https://www.wbs.ac.uk/courses/masters/scholarships/')],
    'P08': [dict(name='TUM scholarships', by='TUM', kind='University merit', amount='check', deadline='check',
                 eligibility='TUM lists its own scholarships plus Deutschlandstipendium and external databases. Non-EU tuition is EUR 4,000 per semester for this programme.',
                 steps=['Read the TUM scholarships page after admission; contact stipendien.zv@tum.de.'], prepare=[],
                 link='https://www.tum.de/en/studies/fees-and-financial-aid/scholarships', fit='check', fit_note='')],
    'P09': [U(name='Tepper MSBA scholarship', by='Tepper School of Business', amount='check', deadline='With the admission application (international applicants: Round 3 is the last round)',
              eligibility='Merit consideration as part of admission; a GMAT/GRE waiver request does not affect scholarship eligibility - check details with admissions.',
              steps=AUTO, prepare=APP_PREP + ['GMAC Common Letter of Recommendation (one, ideally a supervisor)'],
              link='https://www.cmu.edu/tepper/programs/master-business-analytics/admissions/apply', fit='check', fit_note='')],
    'P10': [U(name='USC Marshall MSBA scholarship', by='USC Marshall', amount='Limited; amount check', deadline='Apply in Round 1 or 2 for priority',
              eligibility='Admitted domestic and international students, holistic assessment.',
              steps=['Apply in Round 1 or 2.', 'No separate application; recipients are told within 10 days of admission.'], prepare=APP_PREP,
              link='https://www.marshall.usc.edu/programs/graduate-programs/specialized-masters/ms-business-analytics/admissions')],
    'P11': [U(name='Business Analytics MSc Scholarship', by='UCL School of Management', amount='Up to GBP 10,000 (2027-28)', deadline='With the application',
              eligibility='Outstanding candidates; all applicants are considered; at the Course Director\'s discretion.', steps=AUTO, prepare=APP_PREP,
              link='https://www.ucl.ac.uk/study/prospective-students/graduate/courses/business-analytics-msc'),
            U(name='Director\'s Scholarship for Academic Excellence', by='UCL School of Management', amount='GBP 20,000', deadline='check',
              eligibility='Offer-holders with outstanding academic achievement and future impact.', steps=['Hold an offer; check whether a separate application is needed.'],
              prepare=APP_PREP, link='https://www.ucl.ac.uk/study/prospective-students/graduate/courses/business-analytics-msc', fit='check', fit_note='')],
    'P12': [U(name='UBC Sauder MBAN entrance scholarships', by='UBC Sauder', amount='Dean\'s Entrance CAD 5,000 - full tuition (Early Bird applicants); Regional Top Talent (Asia) CAD 5,000 - full tuition; International Talent CAD 5,000 - 25,000; Global Business Leader of Tomorrow CAD 5,000 - 30,000; Accelerated Career CAD 2,500 - 20,000',
              deadline='By the MBAN deadlines (Dean\'s Entrance needs the Early Bird round); Global Business Leader: 2 Mar 2027 for international applicants',
              eligibility='Automatic consideration on submission; 25-35% of each class gets an entrance award; academics, work experience, drive and essays.',
              steps=['Apply in the Early Bird round for the widest set of awards.', 'Upload official documents by the document deadline.'], prepare=APP_PREP,
              link='https://www.sauder.ubc.ca/master-business-analytics/application-process/mban-scholarships-and-funding'),
            U(name='Women in Analytics Leadership Scholarship', by='UBC Sauder', amount='CAD 2,500 - 30,000', deadline='With the application',
              eligibility='Outstanding academics, career potential and commitment to gender diversity in analytics/data/STEM.', steps=AUTO,
              prepare=['Examples of supporting women in tech/analytics'], link='https://www.sauder.ubc.ca/master-business-analytics/application-process/mban-scholarships-and-funding')],
    'P13': [dict(name='RSM scholarships', by='RSM / Erasmus University', kind='University merit', amount='None for non-EEA students in 2027-28',
                 deadline='-', eligibility='RSM\'s own Erasmus Trustfonds Scholarship is for EU/EEA nationals only; tuition for non-EEA is EUR 28,000 (2027-28).',
                 steps=['Look at external sources (Grantfinder, Scholarship Portal) listed on the RSM page.'], prepare=[],
                 link='https://www.rsm.nl/education/scholarships/msc-scholarships/', fit='unlikely', fit_note='No RSM award open to Indian students.')],
    'P14': [dict(name='Mannheim Scholarship / Opportunity Mannheim', by='University of Mannheim', kind='University merit', amount='check', deadline='check',
                 eligibility='University scholarship system (~200 students a year): Deutschlandstipendium, Mannheim Scholarship, Opportunity Mannheim (financial need).',
                 steps=['Check each scholarship\'s call and deadline early - selection takes months.'], prepare=[],
                 link='https://www.uni-mannheim.de/en/scholarships/', fit='check', fit_note='')],
    'P15': [dict(name='Edinburgh Business School scholarships', by='University of Edinburgh Business School', kind='University merit', amount='check',
                 deadline='check', eligibility='The programme fees page refers to scholarships and other funding - check the programme\'s scholarships page.',
                 steps=['Read the programme scholarships page when the 2029 list is published.'], prepare=[],
                 link='https://www.business-school.ed.ac.uk/msc/business-analytics/fees-living-expenses', fit='check', fit_note='')],
    'P16': [dict(name='SMU MITB scholarships', by='Singapore Management University', kind='University merit', amount='check', deadline='check',
                 eligibility='Official pages sit behind a CAPTCHA and could not be read; third-party sources mention MITB scholarships for some nationalities only.',
                 steps=['Open the MITB page yourself and look for "Scholarships".'], prepare=[],
                 link='https://masters.smu.edu.sg/programme/master-of-it-in-business', fit='check', fit_note='Not verified.')],
    'P17': [U(name='MIMS fellowship packages', by='UC Berkeley School of Information', amount='USD 5,000 - 30,000 (limited number)', deadline='With the admission application',
              eligibility='All MIMS applicants are considered; outstanding achievement and potential to contribute to diversity, equity and inclusion; I School / California Promise packages.',
              steps=AUTO, prepare=APP_PREP + ['Essay content on overcoming challenges / inclusion leadership where genuine'],
              link='https://www.ischool.berkeley.edu/programs/mims/funding'),
            dict(name='GSI / GSR / reader positions', by='UC Berkeley', kind='Assistantship', amount='Wages plus partial fee remission depending on hours',
                 deadline='Department postings each term', eligibility='Enrolled graduate students.', steps=['Apply to postings after enrolment.'],
                 prepare=['Resume', 'Course grades in the subject'], link='https://www.ischool.berkeley.edu/programs/mims/funding', fit='likely', fit_note='')],
    'P18': [U(name='UMSI merit scholarships', by='University of Michigan School of Information', amount='Partial to full tuition', deadline='Priority deadline 15 Jan (first consideration)',
              eligibility='Merit-based, need-informed; automatic with the admission application.', steps=['Apply by the 15 Jan priority deadline.'] + AUTO[1:], prepare=APP_PREP,
              link='https://www.si.umich.edu/admissions-aid/tuition-and-funding/master-science-information-tuition-and-funding'),
            U(name='UMSI external scholarship matching', by='UMSI', amount='Up to USD 10,000 matching funds', deadline='Submit the award letter within 12 months of enrolment',
              eligibility='MSI students who win an EXTERNAL scholarship in their first year (e.g. J N Tata, K C Mahindra, AAUW) - depends on remaining need and available funds.',
              steps=['Win an external scholarship.', 'Send the award statement to the UMSI admissions team.'], prepare=['External award letter'],
              link='https://www.si.umich.edu/admissions-aid/tuition-and-funding/master-science-information-tuition-and-funding'),
            dict(name='Graduate assistantships', by='University of Michigan', kind='Assistantship', amount='Often tuition + stipend + health insurance (competitive)',
                 deadline='Postings', eligibility='Teaching, research or strategic-initiative roles.', steps=['Apply to postings once admitted.'], prepare=['Resume'],
                 link='https://www.si.umich.edu/admissions-aid/tuition-and-funding/master-science-information-tuition-and-funding', fit='check', fit_note='Competitive.')],
    'P19': [U(name='Excellence Scholarship & Opportunity Programme (ESOP)', by='ETH Zurich', amount='CHF 12,000 per semester (CHF 13,500 from autumn 2027) + tuition waiver, for the regular programme length; mentoring',
              deadline='Only in the first application window: 1 - 30 Nov (2026 window for autumn 2027 start)',
              eligibility='Very good bachelor\'s result - top 10% of your programme (grade A, self-assessed); not already in or holding a master\'s at ETH. ~60 awards for 2027-28; decision end of March.',
              steps=['Apply to MTEC through eApply in the 1-30 Nov window and opt in to ESOP.', 'Upload a master\'s thesis pre-proposal (ETH guidelines PDF).',
                     'Name two professor referees if the programme itself asks for none; they upload letters within two weeks.', 'Be reachable for a phone/video interview in February.'],
              prepare=['Master\'s thesis pre-proposal written by you, with proper citations', 'Two professor reference letters', 'Proof of top-10% standing (rank certificate)', 'All MTEC admission documents'],
              link='https://ethz.ch/students/en/studies/financial/scholarships/excellencescholarship.html', fit='check', fit_note='Needs top 10% of your class - get a rank certificate.',
              task_days=0)],
    'P20': [dict(name='MBS scholarships', by='Melbourne Business School', kind='University merit', amount='check', deadline='check',
                 eligibility='The MBS scholarships table (Nov 2026) lists no open award for international Master of Business Analytics students (BHP Indigenous only).',
                 steps=['Re-check the scholarships table when you apply.'], prepare=[], link='https://mbs.edu/scholarships', fit='unlikely', fit_note='')],
    'P21': [U(name='ESSEC Scholarship', by='ESSEC Business School', amount='EUR 10,000', deadline='Decided during the application procedure',
              eligibility='All international applicants; based on overall quality (academics, test scores, motivation).', steps=AUTO, prepare=APP_PREP + ['Management test score (GMAT/GRE/TAGE MAGE)'],
              link='https://www.essec.edu/en/program/master-data-sciences-business-analytics/')],
    'P22': [U(name='Cornell Tech merit scholarship', by='Cornell Tech', amount='Partial tuition (no full-tuition awards for master\'s)', deadline='Apply by the priority deadline for full consideration',
              eligibility='All admitted students who are not fully sponsored; holistic review; tuition only. No need-based aid from Cornell Tech.',
              steps=['Apply by the priority deadline.'] + AUTO[1:], prepare=APP_PREP, link='https://tech.cornell.edu/admissions/tuition-fees/')],
    'P23': [dict(name='Harvard Chan merit and need-based scholarships', by='Harvard T.H. Chan School', kind='Need-based', amount='About 40% of SM students get school grants, most covering a quarter to half of tuition',
                 deadline='With the Harvard Chan Grant/Scholarship Application - check date',
                 eligibility='International students in SM-80 are eligible; awards weigh merit, need and background. The page also says one programme has need-based grants only ("no merit aid") - check whether that applies to SM-80.',
                 steps=['Complete the Harvard Chan Grant/Scholarship Application (separate from admission).'], prepare=['Financial information (income, assets, family contribution)', 'Strong admission application'],
                 link='https://hsph.harvard.edu/tuition-and-financial-aid/types-of-financial-aid/', fit='check', fit_note='', task_days=0),
            dict(name='Presidential Scholars Program', by='Harvard President\'s Office', kind='Need-based', amount='Full tuition (about 7 SM students a year)',
                 deadline='Same scholarship application', eligibility='Talented master\'s students with financial need and interest in public-service careers; especially disadvantaged backgrounds.',
                 steps=['Tick/complete via the Harvard Chan Grant/Scholarship Application.'], prepare=['Public-service career evidence'],
                 link='https://hsph.harvard.edu/tuition-and-financial-aid/types-of-financial-aid/', fit='check', fit_note='')],
    'P24': [dict(name='MSCB funding', by='Carnegie Mellon', kind='University merit', amount='None listed', deadline='-',
                 eligibility='The MSCB page does not list scholarships for master\'s students - ask the department.', steps=['Email the MSCB office about any merit aid or TA roles.'], prepare=[],
                 link='https://www.cmu.edu/cbd/education/mscb.html', fit='check', fit_note='')],
    'P25': [dict(name='Penn Engineering master\'s scholarships', by='Penn Engineering', kind='University merit', amount='check (named funds: Penn Engineering Graduate Scholarship, Haidas/Goldman Sachs Dean\'s Master\'s Fellowship, Rosas, McMullen, Ihsuk Shin, Khan Fellowship)',
                 deadline='check', eligibility='Penn Engineering generally does not fund master\'s students; these named scholarships are the exceptions - open each one for its criteria. The MBiotech generally has no TA/RA positions.',
                 steps=['Open the funding page and each named scholarship.'], prepare=[], link='https://gradadm.engineering.upenn.edu/funding-your-education/', fit='check', fit_note='')],
    'P26': [dict(name='MBP scholarship round', by='Northwestern McCormick (MS Biotechnology)', kind='University merit', amount='check',
                 deadline='Round 1 - Scholarship (domestic and international): 1 March', eligibility='Apply by the scholarship round; McCormick generally does not fund master\'s students otherwise.',
                 steps=['Submit by 1 March (no application fee).'], prepare=['Statement of purpose', 'Resume', 'Two recommendations', 'Unofficial transcript', 'TOEFL/IELTS'],
                 link='https://www.mccormick.northwestern.edu/biotechnology/admissions/', fit='check', fit_note='Amounts not stated.')],
    'P27': [U(name='NYU Tandon merit scholarship', by='NYU Tandon', amount='check', deadline='With the admission application',
              eligibility='A committee reviews all full-time master\'s applicants (grades, test scores); fall and spring only; GPA conditions to keep it.', steps=AUTO, prepare=APP_PREP,
              link='https://engineering.nyu.edu/admissions/graduate/tuition-and-financial-aid')],
    'P28': [dict(name='NSF MILESTONE Scholarship', by='UC Irvine (NSF)', kind='Need-based', amount='Offsets tuition, housing, books',
                 deadline='-', eligibility='DOMESTIC students only (FAFSA required).', steps=[], prepare=[],
                 link='https://mbb.bio.uci.edu/graduates/masters-science-degree-biotechnology-management/scholarships/', fit='unlikely', fit_note='Domestic students only.')],
    'P29': [U(name='KGI merit scholarships', by='Keck Graduate Institute', amount='check (decided at admission for the whole programme)', deadline='Apply in the priority round for first consideration',
              eligibility='Academic potential, work/research experience, leadership and community involvement.', steps=['Apply in the priority round.'] + AUTO[1:], prepare=APP_PREP,
              link='https://www.kgi.edu/future-students/financing-your-studies.html'),
            dict(name='KGI need-based aid (incl. international)', by='Keck Graduate Institute', kind='Need-based', amount='check',
                 deadline='check', eligibility='Incoming MBS students (domestic and international) who show financial need via KGI\'s Need-Based Aid application.',
                 steps=['Complete the Need-Based Aid application: how you paid for undergrad, how you will meet costs, why you need aid.'], prepare=['Funding plan'],
                 link='https://www.kgi.edu/future-students/financing-your-studies.html', fit='check', fit_note='')],
}

STATUSES = ['Not looked at', 'Researching', 'Will apply', 'Applied', 'Awarded', 'Rejected', 'Not eligible']


def _ensure():
    with db._lock:
        db.con().execute('CREATE TABLE IF NOT EXISTS funding_status (program_id TEXT, award_id TEXT, status TEXT, note TEXT, '
                         'PRIMARY KEY (program_id, award_id))')
        db.con().commit()


def for_program(pid):
    """University awards first, then external awards that apply to this programme's country."""
    _ensure()
    st = {r['award_id']: r for r in db.query('SELECT * FROM funding_status WHERE program_id=?', (pid,))}
    out = []
    for i, a in enumerate(PROGRAM.get(pid, [])):
        aid = f'{pid}-u{i + 1}'
        out.append({**{k: v for k, v in a.items() if k != 'task_days'}, 'id': aid, 'scope': 'programme',
                    'status': (st.get(aid) or {}).get('status') or 'Not looked at', 'note': (st.get(aid) or {}).get('note') or ''})
    for key, a in EXTERNAL.items():
        if pid in a['programs']:
            out.append({**{k: v for k, v in a.items() if k not in ('programs', 'task')}, 'id': key, 'scope': 'external',
                        'status': (st.get(key) or {}).get('status') or 'Not looked at', 'note': (st.get(key) or {}).get('note') or ''})
    return out


def set_status(pid, award_id, status=None, note=None):
    _ensure()
    db.execute('INSERT INTO funding_status(program_id, award_id, status, note) VALUES (?,?,?,?) '
               'ON CONFLICT(program_id, award_id) DO UPDATE SET status=COALESCE(excluded.status, status), note=COALESCE(excluded.note, note)',
               (pid, award_id, status, note))


def ensure_tasks():
    """Add funding tasks (INSERT OR IGNORE; never touches your status/notes):
    - one common task per external award with a projected date (tasks scope 'common', id FUND-<key>),
    - per programme: a 'check funding page / scholarship form' task tied to the planned-submit date, and ESOP / Harvard
      scholarship-form tasks where a separate application exists."""
    con = db.con()
    with db._lock:
        tsort = (con.execute('SELECT COALESCE(MAX(sort), 0) FROM tasks').fetchone()[0] or 0)
        for key, a in EXTERNAL.items():
            if not a.get('task'):
                continue
            due, title, _lead = a['task']
            tsort += 1
            con.execute('INSERT OR IGNORE INTO tasks(id,scope,program_id,category,title,details,due_date,days_before,priority,status,'
                        'completed_date,notes,link,created_in_app,sort) VALUES (?,?,?,?,?,?,?,?,?,?,?,?,?,?,?)',
                        (f'FUND-{key}', 'common', None, 'Funding', title, a['eligibility'][:500], due, None, 'High', 'Not started', None,
                         'Projected date from the current cycle - confirm on the official page', a['link'], 0, tsort))
        for pid in ALL:
            if not con.execute('SELECT 1 FROM programs WHERE id=?', (pid,)).fetchone():
                continue
            tsort += 1
            con.execute('INSERT OR IGNORE INTO tasks(id,scope,program_id,category,title,details,due_date,days_before,priority,status,'
                        'completed_date,notes,link,created_in_app,sort) VALUES (?,?,?,?,?,?,?,?,?,?,?,?,?,?,?)',
                        (f'{pid}-F1', 'program', pid, 'Funding', 'Read the Scholarships card for this programme; mark each award and note any separate scholarship form',
                         None, None, 75, 'Medium', 'Not started', None, None, None, 0, tsort))
            for i, a in enumerate(PROGRAM.get(pid, [])):
                if 'task_days' in a:
                    tsort += 1
                    con.execute('INSERT OR IGNORE INTO tasks(id,scope,program_id,category,title,details,due_date,days_before,priority,status,'
                                'completed_date,notes,link,created_in_app,sort) VALUES (?,?,?,?,?,?,?,?,?,?,?,?,?,?,?)',
                                (f'{pid}-F{i + 2}', 'program', pid, 'Funding', f"{a['name']}: complete the separate scholarship application",
                                 a['deadline'][:300], None, a['task_days'], 'High', 'Not started', None, None, a['link'], 0, tsort))
        con.commit()
