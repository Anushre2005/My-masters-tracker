"""Template for gre_resources.py - the index of YOUR GRE Google Drive folder.

The real gre_resources.py is personal (links to a private Drive folder) and is not in the repository.
Without it the app still runs: the plan, study notes, courses, quizzes and vocab all work; only the
Magoosh video / practice-question links and book links from Drive are missing.

To link your own Drive folder, create tracker/gre_resources.py with the same five names:

ROOT = 'https://drive.google.com/drive/folders/<folder id>'
LESSONS = {'<lesson folder name>': {'url': '<folder url>', 'videos': [[1, '<video title>', '<file id>'], ...]}, ...}
PRACTICE = {'<practice folder name>': {'url': '<folder url>', 'items': [[<question no>, ['<question file id>', ...], '<solution video id or None>'], ...]}, ...}
FILES = [['<sub-folder path>', '<file name>', '<file id>'], ...]
FOLDERS = [['<folder name>', '<folder id>'], ...]

Folder and file names must match the ones used in gre_plan.py (PTYPES, GUIDE, R('...') calls).
"""
ROOT = ''
LESSONS = {}
PRACTICE = {}
FILES = []
FOLDERS = []
