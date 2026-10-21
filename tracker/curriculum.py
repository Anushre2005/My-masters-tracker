"""Curriculum summaries per programme, researched 7 Oct 2026 from the linked pages.

Course names change every year - always confirm on the source page before relying on them.
Seeded into the `curriculum` table once; edits made in the app are kept.
"""
CHECKED = '2026-10-07'

DATA = {
    'P01': dict(
        overview='12-month STEM programme mixing machine learning, optimisation and an industry capstone.',
        structure='Fall: intensive required core + electives. Spring: electives + capstone work on campus (Feb-May). '
                  'Summer: full-time capstone with the host organisation, final report in August. 111-147 units total.',
        core='Machine Learning; Optimization Methods; Advanced Analytics Edge; Analytics Lab; From Analytics to Action; Analytics Tools',
        electives='Unrestricted electives across MIT (see MIT subject catalog).',
        capstone='Analytics Capstone Project: pairs of students with a sponsor organisation (US and abroad); tuition offset of over US$22,000.',
        source='https://mitsloan.mit.edu/master-of-business-analytics/program-components/curriculum'),
    'P02': dict(
        overview='36-credit STEM degree run by Columbia Engineering (IEOR) with Columbia Business School.',
        structure='12 three-credit courses: at least 6 in IEOR and 4-6 at the Business School; rest from Engineering, SIPA, Law, Economics, Maths or Statistics.',
        core='Probability, Statistics & Simulation (IEOR E4101); Data Analytics & Machine Learning (IEOR E4523); Business Analytics (IEOR E4650); Marketing Analytics (MRKT B9651) - all in first fall',
        electives='Wide choice across Engineering and Columbia Business School.',
        capstone='Capstone not confirmed in this search - check the MSBA curriculum page.',
        source='https://bulletin.columbia.edu/columbia-engineering/academic-departments-programs/industrial-engineering-operations-research/graduate-programs/business-analytics-ms'),
    'P03': dict(
        overview='One-year MSc building programming and ML foundations, then business-analytics specialisms and a summer project.',
        structure='Core modules -> Business Analytics electives (+1 elective from other Imperial MSc programmes) -> summer capstone or research report.',
        core='Data Structures & Algorithms; Deep Learning & Generative AI; Data Wrangling & Visualisation',
        electives='Advanced Machine Learning; Causal Modelling for Business Analytics; Data Management & Ethics; Energy Analytics; Financial Analytics; '
                  'Generative AI & LLMs; Healthcare & Medical Analytics; Leadership in Analytics; Logistics & Supply-Chain Analytics; Network Analytics; '
                  'Retail & Marketing Analytics; Text Analysis for Business',
        capstone='Analytics in Business Capstone (work placement or consulting project) OR Individual Research Report.',
        source='https://www.imperial.ac.uk/study/courses/postgraduate-taught/2026/business-analytics/'),
    'P04': dict(
        overview='13-month full-time (or 2-year part-time) MSc run jointly by NUS Business and Computing.',
        structure='8 modules (5 essential + 3 electives) plus the year-long Professional Consulting Capstone.',
        core='Analytics in Managerial Economics; Data Management & Warehousing; Deterministic Operations Research; Foundation in Data Analytics I; Foundation in Data Analytics II',
        electives='3 electives from the MSBA list (see programme page).',
        capstone='Professional Consulting Capstone: capstone classes, industry analytics seminars and a 3-6 month full-time project with a company.',
        source='https://msba.nus.edu.sg/programme/'),
    'P05': dict(
        overview='10-month, 36-credit on-campus programme (renamed MS Business Analytics & AI), AI-forward with business application.',
        structure='Three terms: Summer -> Fall -> Spring.',
        core='Summer: programming, data management, intro to machine learning. Fall: Advanced Machine Learning; Optimization I; Information Management; '
             'Analytics for Unstructured Data; Financial Management.',
        electives='Financial analytics, or supply chain & marketing analytics; AI governance / trustworthy AI content.',
        capstone='Industry-linked project work (check current details on the programme page).',
        source='https://www.mccombs.utexas.edu/graduate/specialized-masters/ms-business-analytics/ms-business-analytics-on-campus/'),
    'P06': dict(
        overview='One academic year (Aug-June) of 13 courses over three terms, with a programme-long industry practicum.',
        structure='Introductory term -> Analytics Toolkit term (Fall) -> Analytics Applications term (Spring).',
        core='Analytics in Management; Applications of Large Language Models; Structuring & Visualizing Data for Analytics; Modeling Tools for Predictive Analytics; '
             'AI & Deep Learning Tools; Analytics Colloquia; Self Development Lab',
        electives='3 electives in the Spring term.',
        capstone='Management Analytics Practicum: teams of 3-4 solve a real problem for an organisation across the whole programme '
                 '(past partners include Google, TD Bank, Unilever). Listed as 15 months incl. a 4-month practicum in the Programs tab - confirm.',
        source='https://rotman.utoronto.ca/programs/specialized-programs/master-of-management-analytics/'),
    'P07': dict(
        overview='Relaunched for 2026 entry as MSc Business Analytics & AI: AI, statistics, optimisation and machine learning applied to business.',
        structure='Core modules + two electives + Analytics Portfolio; choose a route: Predictive & Prescriptive Analytics, AI, Management Analytics, or Marketing Analytics & Technology.',
        core='Earlier cohorts: Data Management; Business Statistics; Analytics in Practice; Optimisation Models; Advanced Analytics; Advanced Data Analysis; '
             'Understanding Business for Analysts. VERIFY: the 2026 redesign may have changed these.',
        electives='Examples: Supply Chain Analytics; Forecasting; Discrete Event Simulation; Strategy Analytics; Pricing Analytics; Text Analytics; Financial Analytics',
        capstone='Dissertation or Business in Practice project (earlier structure - verify).',
        source='https://www.wbs.ac.uk/courses/masters/business-analytics-artificial-intelligence/'),
    'P08': dict(
        overview='4-semester, 120-ECTS Master in Management & Technology: management plus an engineering/tech specialisation.',
        structure='Semesters 1-3: management + technology electives (24 ECTS free choice); semester 3: advanced international experience; semester 4: thesis.',
        core='One of seven management specialisations + one of six technology specialisations (Computer Engineering, Industrial Engineering and '
             'Sustainable Energies fully in English).',
        electives='24 ECTS free electives for a tech, management or international profile.',
        capstone="Master's thesis (semester 4).",
        source='https://www.mgt.tum.de/programs/master-in-management-technology'),
    'P09': dict(
        overview='9-month full-time STEM MSBA covering ML, optimisation, data engineering, communication and business domains.',
        structure='Four mini-semesters.',
        core='Mini 1: Programming in R & Python; Intro to Probability & Statistics; Managing People & Teams; Business Fundamentals. '
             'Mini 2: Business Communications; Statistical Foundations; Machine Learning Fundamentals; Modern Data Management. '
             'Mini 3: Optimization; Data Exploration; electives.',
        electives='Electives from Mini 3 onwards (marketing, operations, finance, people analytics topics).',
        capstone='Capstone project with a real business problem.',
        source='https://www.cmu.edu/tepper/programs/master-business-analytics/curriculum/courses.html'),
    'P10': dict(
        overview='STEM MS Business Analytics, full-time (3-4 courses a semester) or part-time.',
        structure='Required core + electives (unit totals have changed over the years - Programs tab says 33 units; verify).',
        core='Business Analytics (DSO 510); Statistical Computing & Data Visualisation (DSO 545); Algorithmic Thinking with Python (DSO 576); '
             'SQL Databases (DSO 552); Advanced Databases (DSO 555); Applied Modern Statistical Learning (DSO 530); Communication for Management; Data-Driven Decision Making',
        electives='Electives from Marshall analytics list.',
        capstone='Check current programme page.',
        source='https://www.marshall.usc.edu/programs/graduate-programs/specialized-masters/ms-business-analytics'),
    'P11': dict(
        overview='12-month MSc: 6 core modules, 2 options and a 60-credit dissertation.',
        structure='Term 1: 4 modules; Term 2: 4 modules (2 optional); Term 3: dissertation.',
        core='Business Strategy & Analytics; Marketing Analytics; Mathematical Foundations for Business Analytics; Programming for Business Analytics; '
             'Predictive Analytics; Operations Analytics',
        electives='Data Engineering; Data Visualisation; Decision & Risk Analysis; Natural Language Processing; Network Analysis; Machine Learning for Business; '
                  'Machine Learning for Domain Specialists',
        capstone='12,000-word dissertation (independent research project).',
        source='https://www.ucl.ac.uk/prospective-students/graduate/taught-degrees/business-analytics-msc'),
    'P12': dict(
        overview='12-month MBAN: five 6-week periods (Sept-May) then a 4-month experiential component.',
        structure='Courses 1.5 credits each, 4-5 per period. Areas: Data Management, Data Analytics, Decision Analytics, Business Context, Business Skills, Experiential Learning.',
        core='Tools: Python, R, SQL, Tableau, Power BI, AI/ML tools (see programme page for course list).',
        electives='See programme page.',
        capstone='Industry hackathon, then 4 months: analytics internship, group consulting project, or individual research project.',
        source='https://www.sauder.ubc.ca/programs/masters-degrees/mban'),
    'P13': dict(
        overview='12-month MSc specialisation in Business Analytics & Management.',
        structure='Core (20 ECTS, autumn) + 2 electives (18 ECTS) + Business Analytics Workshop (6 ECTS) + thesis (18 ECTS).',
        core='Advanced Statistics & Programming; Data Management & Ethics; Experimentation & Causal Inference; Management Science; Your Future Career',
        electives='Supply Chain Analytics; Marketing Models; Principles of Financial Modelling; Customer Analytics; Digital Economy Analytics; '
                  'Analysing Digital Footprints; FinTech: Business Models & Applications',
        capstone='Business Analytics Workshop (Jan-spring) + master thesis through the year.',
        source='https://www.rsm.nl/education/master/msc-programmes/mscba-business-analytics-management/'),
    'P14': dict(
        overview='2-year, 120-ECTS flexible management master; specialise or go broad across 6 business areas (120+ courses).',
        structure='Methods & Key Qualifications 16 ECTS; Business Economics 12; Business Administration 44-68; Electives 0-24; Thesis 24.',
        core='Areas: Accounting & Taxation; Finance, Banking & Insurance; Information Systems; Management; Marketing & Sales; Operations Management.',
        electives='Free electives incl. neighbouring disciplines (e.g. Information Systems for an analytics profile).',
        capstone="Master's thesis (24 ECTS).",
        source='https://www.uni-mannheim.de/media/Fakultaeten/bwl/Dokumente/Studium/MMM/Module_Catalog_Mannheim_Master_in_Management_en.pdf'),
    'P15': dict(
        overview='One year (mid-Sept to Aug): compulsory courses in semester 1, options in semester 2, then dissertation.',
        structure='Compulsory courses -> exactly 60 credits of options -> dissertation.',
        core='Includes Predictive Analytics & Modelling of Data; Prescriptive Analytics with Mathematical Programming (full list on the degree programme table - VERIFY).',
        electives='60 credits of option courses.',
        capstone='MSc dissertation.',
        source='https://www.business-school.ed.ac.uk/msc/business-analytics/overview/programme-structure'),
    'P16': dict(
        overview='Master of IT in Business (12-24 months), seminar-style 3-hour classes.',
        structure='Choose a track: Analytics (Data Science & Analytics), Artificial Intelligence, Financial Technology & Analytics, or Digital Transformation.',
        core='Track-specific core - VERIFY on the programme page (not listed in search results).',
        electives='Track electives.',
        capstone='Check programme page.',
        source='https://masters.smu.edu.sg/programme/master-of-it-in-business'),
    'P17': dict(
        overview='2-year, 48-unit professional master at the Berkeley School of Information.',
        structure='Year 1 mostly core; year 2 specialisation and electives.',
        core='Info 202 Information Organization & Retrieval; Info 203 Social Issues of Information; Info 205 Information Law & Policy; '
             'Info 206A Intro to Programming & Computation (waivable); Info 206B Intro to Data Structures & Analytics',
        electives='At least one advanced technology course and one advanced social science/policy course, plus electives.',
        capstone='Group final project.',
        source='https://www.ischool.berkeley.edu/programs/mims/degreerequirements'),
    'P18': dict(
        overview='48-credit MSI (usually 2 years); choose one of five pathways.',
        structure='Core in first semester -> pathway selectives -> 9 credits of electives -> mastery course.',
        core='SI 500 Problem-Solving with People, Information & Technology; SI 506 Programming I. Pathway to pick: Information & Data Analytics.',
        electives='Pathway selectives + 9 credits of graduate electives (other schools or internship courses allowed).',
        capstone='SI 699 mastery course (project-based).',
        source='https://si.umich.edu/programs/master-science-information/curriculum'),
    'P19': dict(
        overview='4-semester, 24-month MSc: three lecture semesters, industrial internship and thesis.',
        structure='Core courses min 51 ECTS; electives min 10 ECTS; supplementary min 12 ECTS; internship; thesis.',
        core='General Management; HR Management; Strategy, Markets & Technology; Information & Operations Management; Quantitative & Qualitative Methods; '
             'Micro & Macroeconomics; Financial Management',
        electives='Electives incl. data analytics and technology/innovation management topics.',
        capstone="Industrial internship + master's thesis.",
        source='https://mtec.ethz.ch/studies/prospectives.html'),
    'P20': dict(
        overview='12-month, 150-point MBusA; all subjects compulsory, no electives. January start (does not match the Aug-Sept plan).',
        structure='Five modules + Personal Effectiveness Program throughout.',
        core='Introduction to Business Problems; Business Analytics Foundations; Advanced Business Analytics; Business Analytics Applications',
        electives='None (fully compulsory).',
        capstone='Analytics Lab with a real business; applications in finance, marketing and supply chain.',
        source='https://mbs.edu/degree-programs/full-time-master-of-business-analytics'),
    'P21': dict(
        overview='Joint ESSEC (business) + CentraleSupelec (engineering) programme, 1 or 2 years; ranked #4 in QS Business Analytics 2026.',
        structure='VERIFY - detailed course list not found in search; check the official programme page.',
        core='Data science foundations + business analytics (see official page).',
        electives='See official page.',
        capstone='See official page.',
        source='https://www.essec.edu/en/program/master-data-sciences-business-analytics/'),
}


# Admission requirements found 7 Oct 2026 (for the 2026-27 cycle - recheck for 2029 entry).
# Only fills fields still marked VERIFY/empty in the Excel tracker; the source is shown on the detail page.
REQUIREMENTS = {
    'P01': dict(gre='Optional (GMAT Focus/10th ed. or GRE) - submit if you have one; no negative inference without',
                english='No TOEFL/IELTS accepted - English assessed in interview',
                recs='3 letters; one must speak to quantitative ability', app_fee='US$150',
                src='https://mitsloan.mit.edu/master-of-business-analytics/admissions/how-to-apply', kind='official',
                force=['gre']),  # Excel said "expected"; official page now says optional (class median Quant 169)
    'P02': dict(gre='GRE expected (no minimum; past classes ~91st+ percentile Quant); waivers offered',
                english='TOEFL/IELTS/PTE required if degree not from an English-speaking country (TOEFL ~99 cited)',
                recs='3 letters', essays='Personal statement', app_fee='US$85',
                src='https://yocket.com/universities/columbia-university/business-analytics-51630', kind='secondary'),
    'P03': dict(gre='Not required but adds weight; if taken, aim ~90th percentile (strongly advised for less quantitative degrees)',
                recs='2 referees (2 academic, or 1 academic + 1 professional); work email addresses only', app_fee='GBP 125',
                special='Online maths test required before applying; 1st/2:1-equivalent in a quantitative degree '
                        '(calculus, probability, statistics, linear algebra)',
                src='https://www.imperial.ac.uk/business-school/masters/business-analytics/admissions/', kind='official'),
    'P04': dict(gre='GRE/GMAT not required',
                english='IELTS/TOEFL needed for non-English-medium degrees (class averages cited: TOEFL 85, IELTS 6)',
                src='https://msba.nus.edu.sg/wp-content/uploads/2024/10/Application-Checklist-for-MSBA-AY2025_26.pdf', kind='official'),
    'P05': dict(gre='Optional (GRE/GMAT) - no disadvantage without',
                english='TOEFL, IELTS or Duolingo for international applicants (exceptions apply)',
                recs='2 letters (at least one academic)', essays='2 essays (500 words max) + 1 optional',
                interview='Kira Talent video assessment (within 7 days of invite)', app_fee='US$90 (international)',
                src='https://www.mccombs.utexas.edu/graduate/specialized-masters/ms-business-analytics/ms-business-analytics-on-campus/admissions/',
                kind='official'),
    'P06': dict(interview='Video assessment (2 questions) + 10-minute timed written response', app_fee='CAD 195',
                special='Quant degree preferred; min B average in quantitative courses; calculus, linear algebra, '
                        'probability & statistics essential',
                src='https://sgs.calendar.utoronto.ca/node/85746', kind='official calendar + secondary'),
    'P07': dict(gre='Not required; a strong score can help', english='IELTS 7.0 (or TOEFL 100 / Duolingo 130 / PTE 70)',
                recs='1 academic or professional reference', essays='Personal statement',
                src='https://www.mastersportal.com/studies/3310/business-analytics-and-artificial-intelligence.html', kind='secondary'),
    'P08': dict(gre='GMAT REQUIRED for Indian bachelor degrees: at least 65th percentile (classic or Focus)',
                english='English-taught degree (or 12+ ECTS in English) accepted; GMAT 53rd+ percentile also accepted as proof',
                essays='None - merit-based aptitude assessment (transcript; written test for borderline files)',
                interview='No interview',
                src='https://mgt.tum.de/programs/master-in-management-technology/how-to-apply', kind='official'),
    'P09': dict(gre='GMAT, GMAT Focus or GRE required (valid 5 yrs at submission)',
                english='TOEFL, IELTS or Duolingo unless degree fully in English',
                recs='1 professional recommendation', essays='1 written essay + 1 video essay', app_fee='US$125',
                src='https://www.cmu.edu/tepper/programs/master-business-analytics/admissions/apply', kind='official'),
    'P10': dict(gre='GMAT/GRE neither required nor accepted', english='TOEFL or IELTS for international applicants',
                recs='Not required or accepted', essays='One-minute video instead of an essay', app_fee='US$155',
                special='Must have a college-level statistics course (inference, t-tests, chi-square, regression); '
                        'work experience preferred',
                src='https://www.marshall.usc.edu/programs/graduate-programs/specialized-masters/ms-business-analytics/admissions',
                kind='official'),
    'P11': dict(english='UCL Level 2: IELTS 7.0 overall, 6.5 in each component',
                special='UK 2:1 or equivalent; strong quantitative aptitude',
                src='https://www.ucl.ac.uk/prospective-students/graduate/taught-degrees/business-analytics-msc', kind='official'),
    'P12': dict(gre='REQUIRED: GRE 155 Verbal & 155 Quant, or GMAT 515 (50th+ percentile in each section); within 5 years',
                english='TOEFL 100 or IELTS 7.0 if degree not in English (within 2 years)', special='B+ average bachelor degree',
                src='https://www.sauder.ubc.ca/programs/masters-degrees/mban', kind='official'),
    'P13': dict(gre='GMAT (565 cited) - GRE optional alternative', english='IELTS 7 / TOEFL 95 (C1 level)', app_fee='EUR 100',
                special='Capped programme: applications close 15 May or when full',
                src='https://www.eur.nl/en/master/business-analytics-management/admission', kind='secondary'),
    'P14': dict(gre='Optional but recommended: GMAT/GRE from 600 earns ranking points',
                english='C1: TOEFL iBT 100 or IELTS 7.0 (or 40%+ of bachelor taught in English)',
                special='Needs 36 ECTS of business administration in the bachelor - CHECK, a BTech may fall short',
                src='https://www.uni-mannheim.de/media/Einrichtungen/zula/Auswahlsatzungen_master/satzung_ma_mmm_en.pdf',
                kind='official'),
    'P15': dict(gre='GMAT currently waived', english='IELTS 7.0', app_fee='GBP 60',
                special='1st or 2:1 in a quantitative discipline',
                src='https://www.business-school.ed.ac.uk/msc/business-analytics/entry-requirements', kind='secondary'),
    'P16': dict(gre='GMAT/GRE or SMU Admissions Test', english='IELTS 6.5 / TOEFL 90', recs='Recommendation letters',
                essays='Personal statement', interview='Admission interview required',
                special='GPA 3.0/4.0 or equivalent; 2-year work-experience rule waived (except Digital Transformation track)',
                src='https://masters.smu.edu.sg/programme/master-of-it-in-business', kind='official (partial)'),
    'P17': dict(english='TOEFL/IELTS for international applicants (class average TOEFL 111)', recs='Letters of recommendation',
                essays='Statement of Purpose + Personal History Statement', app_fee='US$155 (international)',
                special='Programming Proficiency Form; min GPA 3.0',
                src='https://www.ischool.berkeley.edu/programs/mims/admissions', kind='official'),
    'P18': dict(gre='GRE listed as required by one source - CHECK (may now be optional)', english='TOEFL iBT 100',
                recs='3 letters', app_fee='US$90 (international)',
                src='https://www.si.umich.edu/programs/msi/admissions/msi-admissions', kind='secondary'),
    'P19': dict(english='Typically IELTS 7.0 / TOEFL 100 (check MTEC page)',
                special='Very selective (~10-15% for international applicants); bachelor 180 ECTS from a top university',
                src='https://ethz.ch/en/studies/master/application/international-bachelor/prerequisites.html',
                kind='official (general) + secondary'),
    'P21': dict(gre='GMAT, GRE or TAGE-MAGE required', english='TOEFL 95 / IELTS 6.5 (waived after 3+ years fully in English)',
                recs='2 letters (ideally 1 academic + 1 professional)', interview='Interview after file review',
                app_fee='EUR 100-120',
                src='https://www.essec.edu/en/program/master-data-sciences-business-analytics/', kind='secondary'),
}
