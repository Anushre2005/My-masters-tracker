"""Programmes added in the app (not in the original Excel tracker): US programmes that combine biotech / life
sciences with business and computing / AI.

Researched 2026-11-17 from official programme pages (2026-27 cycle). Deadlines for the 2029 intake are projected
from the current cycle; tuition is the current rate times programme length. ensure() inserts anything missing
(INSERT OR IGNORE), so it is safe to run at every start and after an Excel re-import, and never overwrites your
status, dates or notes.
"""
from . import db

CHECKED = '2026-11-17'
PROJECTED = 'Projected from 2026-27 cycle'
OPT = 'US: OPT 12 months + 24-month STEM extension if the programme is STEM-designated (verify)'

# id, short_name, tier, university, programme, duration, tuition (total, USD), fee_basis, deadline (projected), planned_submit,
# deadline_notes, link, living (total, USD), living_note, requirements, curriculum, needs_bio
PROGRAMS = [
    dict(id='P22', short_name='Cornell Tech Health Tech', tier='Ambitious',
         university='Cornell Tech (Jacobs Technion-Cornell Institute), New York City',
         programme='Dual MS - Information Systems (Cornell) + Applied Information Science (Technion), Health Tech concentration',
         duration='2 years full-time; two master\'s degrees', tuition='147892',
         fee_basis='2026-27 official first-year tuition $73,946 x 2 years (official tuition page; second-year rate may rise)',
         deadline='2029-01-05', planned_submit='2028-12-20',
         deadline_notes='Fall 2027 cycle: Priority 5 Jan 2027 (scholarships), Round 2 2 Feb 2027, Rolling 1 Apr 2027 (official admissions page)',
         link='https://health.tech.cornell.edu/masters-program/', living='78908',
         living_note='Cornell Tech estimate $39,454 per year (official FAQ) x 2',
         req=dict(gre='GRE not required and not accepted (official)', english='TOEFL 100 / IELTS 7.0 (waivers for English-medium degrees)',
                  work_exp='Not required', recs='Recommendation letters', essays='Personal statement + resume', interview='Not stated',
                  app_fee='US$95', special='Studio + product/startup courses; deep links to NYC health systems and startups'),
         cur=dict(overview='Two-year dual MS for health-tech careers: technical depth (ML, data science) plus health systems and entrepreneurship.',
                  structure='Technical courses, health courses, business/entrepreneurship courses, Studio (team projects with companies), two-semester specialization project.',
                  core='Applied Machine Learning, Data Science, NLP / Computer Vision options; Digital & Mobile Health, Healthcare System Organization, Health Tech Data and Systems, Predictive Analytics & Clinical Decision-Making.',
                  electives='Entrepreneurship, Product Management, Startup Funding & Pitching, Leadership for Digital Transformation, IP & Law, Behavioral Economics.',
                  capstone='Two-semester Specialization Project (anchor course or faculty-directed).',
                  source='https://health.tech.cornell.edu/masters-program/')),
    dict(id='P23', short_name='Harvard Health Data Sci', tier='Ambitious',
         university='Harvard T.H. Chan School of Public Health, Boston',
         programme='SM in Health Data Science (80-credit)', duration='2 years full-time (4 semesters, 80 credits)', tuition='137280',
         fee_basis='Approx: 2026-27 SM rate $1,716 per credit x 80 credits - verify on the official tuition page',
         deadline='2028-12-01', planned_submit='2028-11-24',
         deadline_notes='Official deadline 1 December (decisions late Feb / early Mar)',
         link='https://hsph.harvard.edu/program/sm-health-data-science/', living='64000',
         living_note='ESTIMATE Boston ~$32,000 per year x 2 - replace with Harvard Chan cost of attendance',
         req=dict(gre='Test scores listed (GRE/MCAT/GMAT...) - required or optional NOT stated: VERIFY',
                  english='TOEFL / IELTS / Duolingo if applicable', work_exp='Not required',
                  recs='Letters of recommendation (via SOPHAS)', essays='Statement of purpose (SOPHAS)', interview='Not stated', app_fee='VERIFY',
                  special='Prereqs: CS/maths/stats degree, R or Python, multivariable calculus, linear algebra'),
         cur=dict(overview='Data science and AI for health and biomedical data - the most technical option on this list.',
                  structure='80 credits: required core, at least 5 credits of computer science, 35 credits of electives.',
                  core='Introduction to Data Science; Computing for Big Data; Statistical Learning; Production Data Science & AI Systems; statistical inference; epidemiology; statistical collaboration.',
                  electives='Machine learning, genomics, causal inference and Harvard-wide electives (incl. business/health policy courses).',
                  capstone='Applied project / collaboration (see handbook).', source='https://hsph.harvard.edu/program/sm-health-data-science/')),
    dict(id='P24', short_name='CMU MS Comp Bio', tier='Ambitious',
         university='Carnegie Mellon University (Computational Biology Dept + Biological Sciences), Pittsburgh',
         programme='MS in Computational Biology (MSCB)', duration='4 semesters (3 possible)', tuition='121800',
         fee_basis='Mellon College of Science master\'s rate 2026-27 $30,450 per semester x 4 (program rate may differ - verify)',
         deadline='2028-12-09', planned_submit='2028-12-01',
         deadline_notes='2026-27 window 9 Sep - 9 Dec 2026 via the SCS online portal',
         link='https://www.cmu.edu/cbd/education/mscb.html', living='40000',
         living_note='ESTIMATE Pittsburgh ~$20,000 per year x 2 - replace with CMU cost of attendance',
         req=dict(gre='GRE not required; reviewed if submitted (official)', english='TOEFL/IELTS/Duolingo for international applicants (verify minimums)',
                  work_exp='Not required', recs='Letters of recommendation', essays='Statement of purpose', interview='Not stated',
                  app_fee='VERIFY (each CMU programme has its own fee)',
                  special='Most CS/ML-heavy biology MS; no business courses - pair with Tepper electives if allowed'),
         cur=dict(overview='Biology + computer science + statistics + machine learning, run by CMU\'s School of Computer Science and Mellon College of Science.',
                  structure='About four semesters; courses chosen from both colleges.',
                  core='Computational genomics, machine learning for biology, statistics, molecular/cell biology foundations.',
                  electives='Wide menu across SCS and MCS.', capstone='Research or project option (see handbook).',
                  source='https://www.cmu.edu/cbd/education/mscb.html')),
    dict(id='P25', short_name='Penn MBiotech', tier='Target',
         university='University of Pennsylvania (Penn Engineering + Arts & Sciences), Philadelphia',
         programme='Master of Biotechnology (MBiotech)', duration='3-4 semesters full-time (10 course units)', tuition='88250',
         fee_basis='2026-27 official Penn Engineering rate $8,825 per course unit x 10 CU (+ about $2,924 fees per term)',
         deadline='2029-02-01', planned_submit='2028-10-31',
         deadline_notes='Fall 2027 cycle: early application 15 Sep - 1 Nov 2026, regular until 1 Feb 2027 (official FAQ). Planned for the early round.',
         link='https://biotech.engineering.upenn.edu/', living='56968',
         living_note='Penn 2026-27 estimate $28,484 per academic year (official SRFS page) x 2',
         req=dict(gre='GRE optional (official FAQ)', english='See Penn Engineering graduate admissions', work_exp='Not required',
                  recs='Letters of recommendation', essays='Statement of purpose', interview='Not stated', app_fee='VERIFY (no fee waivers)',
                  special='Up to 40% of courses outside Engineering incl. 1-2 Wharton classes; computational electives (bioinformatics, data science)'),
         cur=dict(overview='Interdisciplinary biotech master\'s you tailor: biotech core + quantitative/computational electives + room for Wharton courses.',
                  structure='10 CUs: 3 biotech core + 1 lab + 6 electives; tracks: Integrative Molecular Biosciences, Biopharma & Engineering Biotechnology.',
                  core='Choose 3 of 16 biotech core courses (e.g. Modern Biotechnology for Engineers, Genome Engineering, Protein Engineering) + a biotech lab.',
                  electives='Quantitative: Intro to Bioinformatics, Computational Biology, Statistics for Data Science, Biomedical Image Analysis; advanced electives in data science, biomedical informatics, entrepreneurship; Wharton courses as free electives.',
                  capstone='Independent study / research up to 30% of the degree (optional).',
                  source='https://biotech.engineering.upenn.edu/masters-program-curriculum/')),
    dict(id='P26', short_name='Northwestern MS Biotech', tier='Target',
         university='Northwestern University (McCormick School of Engineering), Evanston',
         programme='MS in Biotechnology (Master of Biotechnology Program, MBP)', duration='5 quarters (about 15-18 months)', tuition='94965',
         fee_basis='2026-27 official tuition $18,993 per quarter x 5 quarters (no tuition during internship quarter)',
         deadline='2029-03-01', planned_submit='2028-12-15',
         deadline_notes='Official: Round 1 / scholarship 1 Mar, International final 1 May, Domestic final 31 May; applications open 1 Sep',
         link='https://www.mccormick.northwestern.edu/biotechnology/admissions/', living='31250',
         living_note='ESTIMATE Evanston ~$25,000 per year x 1.25 - replace with Northwestern cost of attendance',
         req=dict(gre='GRE not required (official)', english='Competitive: TOEFL 100+ / IELTS 7.5+ (international, non-English medium)',
                  work_exp='Not required', recs='Letters of recommendation', essays='Statement of purpose', interview='Not stated',
                  app_fee='VERIFY', special='Optional internship / co-op (often paid); bioprocess-engineering heavy, little business'),
         cur=dict(overview='Engineering-focused biotech master\'s (about 70% technical) with professional development and optional industry internship.',
                  structure='Five quarters of coursework; optional internship quarter.',
                  core='Bioprocess engineering, cell and molecular biology, protein/biologics engineering, lab courses.',
                  electives='Technical electives; some business-facing exposure via professional development and biopharma market research projects.',
                  capstone='Internship / research project (optional).',
                  source='https://www.mccormick.northwestern.edu/biotechnology/')),
    dict(id='P27', short_name='NYU Biotech & Entrep', tier='Target',
         university='NYU Tandon School of Engineering, Brooklyn (New York City)',
         programme='MS in Biotechnology and Entrepreneurship', duration='3-4 semesters full-time (30 credits)', tuition='78780',
         fee_basis='2026-27 Tandon graduate rate $2,626 per credit x 30 credits (+ fees) - verify with the NYU Bursar lookup',
         deadline='2028-12-01', planned_submit='2028-11-20',
         deadline_notes='Tandon MS deadlines: priority 1 Dec, final 15 Feb (fall); spring 1 Nov',
         link='https://engineering.nyu.edu/academics/programs/biotechnology-and-entrepreneurship-ms', living='59181',
         living_note='ESTIMATE NYC ~$39,454 per year x 1.5 - replace with NYU cost of attendance',
         req=dict(gre='Tandon: GRE not required for graduate programs (verify for this MS)', english='TOEFL/IELTS (commonly TOEFL 90 / IELTS 7)',
                  work_exp='Not required', recs='Two letters (optional)', essays='Statement of purpose + resume', interview='Not stated',
                  app_fee='US$90', special='PREREQ: undergraduate biochemistry + cell & molecular biology before starting'),
         cur=dict(overview='Turn biotech research into products and companies: biotech core plus innovation, IP, finance and fundraising.',
                  structure='30 credits: 15 core, 3 biotech/management elective, 9 management electives, 3 capstone.',
                  core='4 required biotech courses + Entrepreneurship and Venture Creation.',
                  electives='Innovation, intellectual property, finance, fundraising, product commercialization; Protein Engineering.',
                  capstone='3-credit capstone.', source='https://engineering.nyu.edu/academics/programs/biotechnology-and-entrepreneurship-ms')),
    dict(id='P28', short_name='UC Irvine MS Biotech Mgmt', tier='Target',
         university='UC Irvine (Biological Sciences + Merage School of Business + Samueli Engineering)',
         programme='MS in Biotechnology Management (MSBTM)', duration='2 years full-time', tuition='101055',
         fee_basis='2026-27 official non-California resident rate $50,527.31 per year x 2',
         deadline='2029-01-15', planned_submit='2029-01-05',
         deadline_notes='Official: recommended deadline 15 Jan, then rolling; target deadline 15 Mar',
         link='https://mbb.bio.uci.edu/graduates/masters-science-degree-biotechnology-management/', living='52000',
         living_note='ESTIMATE Irvine ~$26,000 per year x 2 - replace with UCI cost of attendance',
         req=dict(gre='Not stated officially; aggregator says waived for GPA 3.2+ - VERIFY', english='VERIFY (UCI graduate division minimums)',
                  work_exp='Not required', recs='Letters of recommendation', essays='Statement of purpose', interview='Not stated',
                  app_fee='VERIFY', special='Class GPA averages 3.16-3.45; includes MBA courses at Merage + lab research'),
         cur=dict(overview='Biotech science + management: co-taught by biology, engineering and the Merage School of Business.',
                  structure='Two years: business courses, biotech/biomedical engineering courses, 8-unit teaching lab, two quarters of lab research, consulting projects.',
                  core='MBA 200 Management of Innovative Organizations; MB 253/MBA 293 Biotechnology Management (capstone); entrepreneurship / new venture class with a business plan.',
                  electives='Biotech, biomedical engineering and management electives.', capstone='Biotechnology Management capstone + comprehensive exam.',
                  source='https://mbb.bio.uci.edu/graduates/masters-science-degree-biotechnology-management/program-information/')),
    dict(id='P29', short_name='KGI MBS Biotech', tier='Safe',
         university='Keck Graduate Institute (Riggs School of Applied Life Sciences), Claremont CA',
         programme='Master of Business and Science (MBS) in Biotechnology', duration='2 years full-time (year 2 can be hybrid/online)', tuition='75400',
         fee_basis='2026-27 official $18,850 per term ($37,700 per year) x 2 for students admitted Fall 2025 or later',
         deadline='2028-12-08', planned_submit='2028-12-01',
         deadline_notes='Priority deadline in early December (an earlier cycle listed 8 Dec); fall and spring starts - VERIFY dates',
         link='https://www.kgi.edu/degrees-and-programs/biotechnology/master-of-business-and-science/index.html', living='50000',
         living_note='ESTIMATE Claremont ~$25,000 per year x 2 - replace with KGI cost of attendance',
         req=dict(gre='Not mentioned on official pages - VERIFY', english='TOEFL 85 / IELTS 7.0 / Duolingo 120 (or admissions interview)',
                  work_exp='Not required', recs='VERIFY', essays='VERIFY', interview='Possible', app_fee='US$75',
                  special='Year-long team consulting project for a biotech/pharma sponsor; 92% of 2024 entrants got scholarships; AI microcredential'),
         cur=dict(overview='Science + MBA-style business in one degree; built for biotech/pharma management careers.',
                  structure='Year 1 science + business core and a summer industry internship; year 2 concentration + Team Master\'s Project.',
                  core='Pharma discovery & development, diagnostics & devices, bioprocessing; corporate finance, competitive strategy, business design & analytics.',
                  electives='Concentrations: Biotech Management, Data Analytics, Operations & Supply Chain, Regulatory Affairs.',
                  capstone='Team Master\'s Project: year-long consulting assignment for a biotech/pharma company.',
                  source='https://www.kgi.edu/mbs')),
]

# same 21-step checklist as the other programmes (days before your planned submit date; negative = after)
TASKS = [
    ('Research', 'Confirm 2029 intake date, programme length & curriculum on the official page', 150, 'Medium'),
    ('Research', 'Confirm tuition, fees & living cost for 2029 entry', 140, 'Medium'),
    ('Research', 'Confirm 2028-29 rounds & deadline; update Programs tab dates', 120, 'High'),
    ('Research', 'Check my eligibility vs requirements (BTech Comp Eng, GPA, ~21 months at ZS)', 120, 'High'),
    ('Research', 'Attend info session / email admissions with open questions', 90, 'Low'),
    ('Tests', 'Meet test requirement and send official score reports', 45, 'High'),
    ('Documents', 'Upload transcripts, degree/provisional certificate, ID & photo per portal', 30, 'High'),
    ('Documents', 'ZS employment verification (if asked) + tailored resume/CV', 35, 'Medium'),
    ('Essays', 'Read prompts, word/character limits & any video-essay needs; paste into Essay Tracker', 90, 'High'),
    ('Essays', 'Draft tailored essay/SOP v1 (why this programme, ZS pharma/life-sciences analytics impact, biotech + AI goals)', 60, 'High'),
    ('Essays', 'Feedback round (mentor + one ZS senior) and revise to v2', 35, 'Medium'),
    ('Essays', 'Final proofread and word-count check', 7, 'High'),
    ('Recommenders', 'Enter recommenders in portal and confirm LORs will arrive on time', 40, 'High'),
    ('Portfolio', 'Complete programme-specific assessments / portfolio links', 30, 'Medium'),
    ('Funding', 'Apply for programme-specific scholarship / merit award', 30, 'High'),
    ('Submission', 'Pay application fee', 2, 'Medium'),
    ('Submission', 'Final review against this checklist and SUBMIT application', 0, 'High'),
    ('Submission', 'Confirm receipt; fix anything flagged missing in portal', -7, 'Medium'),
    ('Interview', 'Prepare for interview/assessment (if offered) and attend', -30, 'Medium'),
    ('Decision', 'Record decision & scholarship offer; compare offers in Budget tab', -75, 'Medium'),
    ('Post-admit', 'Accept offer, pay deposit, start student-visa checklist', -100, 'High'),
]
BIO_PREREQ = ('Research', 'Check biology / biochemistry prerequisites; if missing, finish an online course '
              '(cell & molecular biology, biochemistry) and list it on the application', 240, 'High')
NEEDS_BIO = {'P25', 'P26', 'P27', 'P28', 'P29'}


def ensure():
    """Insert the programmes, their checklists and curriculum notes if missing. Never overwrites existing rows."""
    con = db.con()
    with db._lock:
        base = (con.execute('SELECT COALESCE(MAX(sort), 0) FROM programs').fetchone()[0] or 0)
        tsort = (con.execute("SELECT COALESCE(MAX(sort), 0) FROM tasks WHERE scope='program'").fetchone()[0] or 0)
        added = 0
        for i, p in enumerate(PROGRAMS):
            r = p['req']
            cur = con.execute('INSERT OR IGNORE INTO programs(id,short_name,tier,country,university,programme,duration,intake,tuition,currency,'
                              'deadline,deadline_notes,planned_submit,confidence,link,status,notes,post_study,scholarship_notes,sort,'
                              'fee_basis,gre,english,work_exp,recs,essays,interview,app_fee,special,living_cost,living_note) '
                              'VALUES (?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?)',
                              (p['id'], p['short_name'], p['tier'], 'US', p['university'], p['programme'], p['duration'], 'Fall 2029',
                               p['tuition'] or None, 'USD', p['deadline'], p['deadline_notes'], p['planned_submit'], PROJECTED, p['link'],
                               'Not started', 'Added 2026-11-17: US biotech + business + AI option', OPT, 'Merit scholarships - VERIFY',
                               base + 1 + i, p['fee_basis'], r['gre'], r['english'], r['work_exp'], r['recs'], r['essays'], r['interview'],
                               r['app_fee'], r['special'], p['living'], p['living_note']))
            if cur.rowcount:
                added += 1
            tasks = ([BIO_PREREQ] if p['id'] in NEEDS_BIO else []) + TASKS
            for k, (cat, title, days, prio) in enumerate(tasks, 1):
                tsort += 1
                con.execute('INSERT OR IGNORE INTO tasks(id,scope,program_id,category,title,details,due_date,days_before,priority,status,'
                            'completed_date,notes,link,created_in_app,sort) VALUES (?,?,?,?,?,?,?,?,?,?,?,?,?,?,?)',
                            (f"{p['id']}-{k:02d}", 'program', p['id'], cat, title, None, None, days, prio, 'Not started', None, None, None, 0, tsort))
            c = p['cur']
            con.execute('INSERT OR IGNORE INTO curriculum(program_id,overview,structure,core,electives,capstone,source,checked) VALUES (?,?,?,?,?,?,?,?)',
                        (p['id'], c['overview'], c['structure'], c['core'], c['electives'], c['capstone'], c['source'], CHECKED))
            con.execute("UPDATE curriculum SET req_source=COALESCE(req_source, ?), req_kind=COALESCE(req_kind, 'official') WHERE program_id=?",
                        (p['link'], p['id']))
        con.commit()
    return added
