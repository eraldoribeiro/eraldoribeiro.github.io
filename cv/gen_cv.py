#!/usr/bin/env python3
"""Generate cv.tex for Eraldo Ribeiro from the website's publications.html.

Run from the repo root (parent of cv/). Produces cv/cv.tex.
Re-run after editing publications.html to refresh the publication lists.
"""
import re, html as ihtml, os

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
PUBS = os.path.join(ROOT, "publications.html")

# ---------- extract publications from the website ----------
src = open(PUBS).read()
items = re.findall(r'<li class="pub" data-year="(\d+)">(.*?)</li>', src, re.S)

def grab(cls, block):
    m = re.search(r'class="%s"[^>]*>(.*?)</' % cls, block, re.S)
    return ihtml.unescape(re.sub(r'<[^>]+>', '', m.group(1))).strip() if m else ''

pubs = []
for yr, block in items:
    pubs.append({
        "year": int(yr),
        "title": grab("pub-title", block),
        "authors": grab("pub-authors", block),
        "venue": grab("pub-venue", block),
    })

# fix one malformed author string from the source page
for p in pubs:
    if p["authors"].startswith("M. Kristan") and "incl. E. Ribeiro" in p["authors"]:
        p["authors"] = "M. Kristan, J. Matas, A. Leonardis, M. Felsberg, et al. (incl. E. Ribeiro)"

# ---------- classify journal / conference / book chapter ----------
BOOK_CHAPTER_VENUES = {
    "Handbook of Pattern Recognition and Computer Vision",
    "Emerging Topics in Computer Vision and Its Applications",
}
CONF_KEYWORDS = [
    "Conference", "Workshop", "Symposium", "Proceedings", "ICPR", "CVPR",
    "ICCV", "ECCV", "ICIP", "ISVC", "FLAIRS", "ICASSP", "BMVC", "VISAPP",
    "ICIAR", "CAIP", "WSCG", "SAC", "SIBGRAPI", "ICAPR", "S+SSPR", "SSPR",
    "CSCI", "ICIAP", "Web Intelligence", "NetSci", "CompleNet", "VOT",
    "The Mathematics of Surfaces", "Network Science", "Complex Networks",
]

def classify(p):
    v = p["venue"]
    if v in BOOK_CHAPTER_VENUES:
        return "chapter"
    for kw in CONF_KEYWORDS:
        if kw in v:
            return "conf"
    return "journal"

for p in pubs:
    p["kind"] = classify(p)

# ---------- LaTeX escaping ----------
def esc(s):
    repl = {
        "\\": r"\textbackslash{}", "&": r"\&", "%": r"\%", "$": r"\$",
        "#": r"\#", "_": r"\_", "{": r"\{", "}": r"\}", "~": r"\textasciitilde{}",
        "^": r"\textasciicircum{}",
    }
    out = []
    for ch in s:
        out.append(repl.get(ch, ch))
    return "".join(out)

def fmt_authors(a):
    a = esc(a)
    # bold the CV owner's name wherever it appears
    a = a.replace("E. Ribeiro", r"\textbf{E. Ribeiro}")
    return a

def pub_item(p):
    title = esc(p["title"])
    authors = fmt_authors(p["authors"])
    venue = esc(p["venue"])
    return (
        "  \\item %s\\\\\n  %s. \\textit{%s}, %d.\n"
        % (title, authors, venue, p["year"])
    )

def render_group(kind):
    group = sorted([p for p in pubs if p["kind"] == kind],
                   key=lambda p: -p["year"])
    return "".join(pub_item(p) for p in group), len(group)

journal_tex, n_j = render_group("journal")
conf_tex, n_c = render_group("conf")
chap_tex, n_ch = render_group("chapter")

# ---------- assemble document ----------
PREAMBLE = r"""\documentclass[11pt]{article}
\usepackage[T1]{fontenc}
\usepackage[utf8]{inputenc}
\usepackage[bitstream-charter]{mathdesign}  % Charter serif
\usepackage[margin=1in,top=0.9in,bottom=1in]{geometry}
\usepackage{microtype}
\usepackage{enumitem}
\usepackage{fancyhdr}
\usepackage[hidelinks]{hyperref}
\usepackage{xcolor}
\usepackage{tabularx}

% --- running footer: name --- Curriculum Vitae --- page ---
\pagestyle{fancy}
\fancyhf{}
\renewcommand{\headrulewidth}{0pt}
\renewcommand{\footrulewidth}{0pt}
\fancyfoot[L]{\small\itshape Eraldo Ribeiro}
\fancyfoot[C]{\small\itshape Curriculum Vitae}
\fancyfoot[R]{\small\thepage}

% --- letter-spaced small-caps section titles with a rule ---
\newcommand{\cvsection}[1]{%
  \vspace{12pt}%
  {\normalfont\large\scshape\textls[120]{#1}}\par
  \vspace{2pt}\hrule height 0.8pt\vspace{7pt}}
\newcommand{\cvsubsection}[1]{%
  \vspace{6pt}{\normalfont\scshape #1}\par\vspace{3pt}}

% --- diamond-bulleted entry list with hanging indent ---
\newlist{cvitems}{itemize}{1}
\setlist[cvitems]{label=$\diamond$, leftmargin=1.4em, labelsep=0.6em,
                  itemsep=4pt, parsep=0pt, topsep=4pt}

% --- a plain dotted list (scholarships etc.) ---
\setlist[itemize]{label=$\cdot$, leftmargin=1.4em, itemsep=2pt, topsep=4pt}

% --- position entry: title (bold) + institution + right-aligned dates ---
\newcommand{\role}[3]{%
  \par\vspace{4pt}\noindent\textbf{#1}\\[1pt]%
  \begin{tabularx}{\linewidth}{@{}Xr@{}}#2 & #3\end{tabularx}\par}

\setlength{\parindent}{0pt}
\linespread{1.04}

\begin{document}
"""

HEADER = r"""
\begin{center}
  {\LARGE\scshape Eraldo Ribeiro}\\[6pt]
  Florida Institute of Technology $\bullet$ Department of Computer Science $\bullet$ Melbourne, FL, USA\\[2pt]
  \href{mailto:eribeiro@fit.edu}{eribeiro@fit.edu} $\bullet$ \href{mailto:eribeiro@cs.fit.edu}{eribeiro@cs.fit.edu}\\[2pt]
  \href{https://scholar.google.com/citations?user=OhniypkAAAAJ}{Google Scholar} $\bullet$
  \href{https://orcid.org/0000-0002-6008-3990}{ORCID: 0000-0002-6008-3990} $\bullet$
  \href{https://github.com/eraldoribeiro}{GitHub}
\end{center}
\thispagestyle{fancy}
"""

EDUCATION = r"""
\cvsection{Education}
\textbf{University of York}, England, UK\\
Ph.D.\ in Computer Science, 2001\\
Dissertation: \textit{Spectral Methods for Shape-from-Texture}. Advisor: Edwin R.\ Hancock.

\vspace{4pt}
\textbf{Federal University of S\~ao Carlos (UFSCar)}, S\~ao Paulo, Brazil\\
M.Sc.\ in Computer Science, 1995\\
Thesis: \textit{A Spectral Approach for the Analysis of Microscopic Images}. Advisor: Paulo Est\^evao Cruvinel.

\vspace{4pt}
\textbf{Catholic University of Salvador (UCSal)}, Salvador, Brazil\\
B.Sc.\ in Mathematics, 1992
"""

INTERESTS = r"""
\cvsection{Research Interests}
Computer Vision, Machine Learning, Artificial Intelligence, Data Science, Shape and
Texture Analysis, 3-D Geometry and Visual Perception, Image Registration, Motion and
Activity Recognition, Object Tracking, Deep Learning and Model Compression,
Bioacoustics and Scientific Imaging, Environmental Image Analysis, Complex Networks.
"""

GRANTS = r"""
\cvsection{Research Grants}
\begin{cvitems}
  \item Computer Vision Methods for Enhancing Slosh Videos\\
  PI: \textbf{E. Ribeiro}. Funded by NASA, 2024--2025, \$94,000.
  \item Passenger Identification and Emotion Estimation\\
  PI: \textbf{E. Ribeiro}. Funded by Embraer, Inc., 2019--2021, \$150,000.
  \item Development of App and Web Interface for Automated Anuran Recognition and Mapping\\
  PI: \textbf{E. Ribeiro}. Funded by the U.S. National Science Foundation (NSF), 2012--2017, \$360,000.
  \item Image-Based Characterization of Marine Fouling\\
  PI: \textbf{E. Ribeiro}. Funded by the U.S. Office of Naval Research (ONR), 2006--2009, \$250,000.
  \item Image-Based Detection of Barnacles\\
  PI: \textbf{E. Ribeiro}. Funded by the U.S. Office of Naval Research (ONR), 2005--2006, \$60,000.
  \item Computer Vision Methods for Nanoscale Imaging\\
  PI: \textbf{E. Ribeiro}. Funded by the University of Central Florida (UCF), 2004, \$11,000.
\end{cvitems}
"""

def pub_section():
    s = ["\n\\cvsection{Publications}\n"]
    s.append("\\cvsubsection{Journal Articles}\n\\begin{cvitems}\n")
    s.append(journal_tex)
    s.append("\\end{cvitems}\n")
    s.append("\\cvsubsection{Peer-Reviewed Conferences and Workshops}\n\\begin{cvitems}\n")
    s.append(conf_tex)
    s.append("\\end{cvitems}\n")
    if chap_tex:
        s.append("\\cvsubsection{Book Chapters}\n\\begin{cvitems}\n")
        s.append(chap_tex)
        s.append("\\end{cvitems}\n")
    return "".join(s)

EXPERIENCE = r"""
\cvsection{Work Experience}
\cvsubsection{Academic}
\role{Associate Professor of Computer Science}{Florida Institute of Technology, Melbourne, FL, USA}{2009 -- Present}
\role{Assistant Professor of Computer Science}{Florida Institute of Technology, Melbourne, FL, USA}{2003 -- 2009}
\role{Research Associate}{University of York, England, UK}{2000 -- 2001}

\vspace{6pt}
\cvsubsection{Industry}
\role{Computer Vision Consultant}{SiteScape, Inc., Remote, USA}{2021 -- 2022}
\role{Computer Vision Software Engineer}{Vicon Motion Systems, Oxford, UK}{2001 -- 2002}
"""

TEACHING = r"""
\cvsection{Teaching}
\cvsubsection{Graduate Courses}
\begin{cvitems}
  \item CSE 5683 --- Computer Vision
  \item CSE 5280 --- Computer Graphics Algorithms
\end{cvitems}
\vspace{4pt}
\cvsubsection{Undergraduate Courses}
\begin{cvitems}
  \item CSE 2010 --- Data Structures and Algorithms
  \item CSE 2050 --- Programming in a Second Language (C++)
  \item CSE 4001 --- Operating Systems Concepts
\end{cvitems}
"""

SUPERVISION = r"""
\cvsection{Student Supervision}
\cvsubsection{Current Ph.D. Students}
\begin{cvitems}
  \item \textbf{Mahbuba Perveen} --- \textit{Indoor Layout Estimation}. Expected Fall 2026.
\end{cvitems}
\vspace{4pt}
\cvsubsection{Graduated Ph.D. Students}
\begin{cvitems}
  \item \textbf{Katrina Smart} --- \textit{Automatic Identification of Anuran Species from Acoustic Signals}. Graduated Summer 2018. Scientist at ENSCO, Inc., Melbourne, FL, USA.
  \item \textbf{Yan Li} --- \textit{Underwater Video Mosaicking and Image Classification of Coral-Reef Colonies}. Graduated Spring 2018.
  \item \textbf{Amar Daood} --- \textit{Pollen Classification Using Deep Learning Approaches}. Graduated Fall 2017.
  \item \textbf{Darwinderjeet Kular} --- \textit{Analyzing Motion Patterns and Behaviors of Human Activity}. Graduated Fall 2015. Senior Research Scientist at Raytheon, Melbourne, FL, USA.
  \item \textbf{Ivan Bogun} --- \textit{Tracking and Recognition of Human--Object Interactions Using Information from Sparse Subspaces}. Graduated Spring 2015. Software Engineer at Waymo, USA.
  \item \textbf{Sultan Almotairi} --- \textit{Human Action Recognition Using Manifold Learning}. Graduated Fall 2014. Associate Professor and Dean of the Community College, Majmaah University, Saudi Arabia.
  \item \textbf{Wei Liu} --- \textit{Polynomial Models in Nonrigid Motion Estimation and Analysis}. Graduated Spring 2011. Zillow, WA, USA.
  \item \textbf{Roman Filipovych} --- \textit{Learning the Spatial Structure of Motion Patterns for Tracking and Recognition}. Graduated Fall 2009. Amazon.com, WA, USA.
\end{cvitems}
\vspace{4pt}
\cvsubsection{Graduated M.Sc.\ (Thesis) Students}
\begin{cvitems}
  \item \textbf{Qinxin Fu} --- \textit{Interpolation of 2-D Vector Fields}. Graduated Fall 2015.
  \item \textbf{Weisi Ding} --- \textit{3-D Shape and Image Registration Using Image Moments}. Graduated Spring 2012. Automation Engineer at Wilbur-Ellis, WA, USA.
  \item \textbf{Miles Wallio} --- \textit{Tracking Nonrigid Surface Deformations}. Graduated Spring 2012. Microsoft, WA, USA.
  \item \textbf{Faisal Badughaish} --- \textit{Seismic Data Analysis}. Graduated Spring 2011. Saudi Aramco, Saudi Arabia.
  \item \textbf{Jaron Blackburn} --- \textit{Manifold Learning and Motion-Pattern Matching}. Graduated Fall 2008. Harris Corporation, USA.
  \item \textbf{Arturo Donate} --- \textit{Reconstructing Dynamic Scenes}. Graduated Summer 2006. Booz Allen Hamilton, USA.
\end{cvitems}
"""

SERVICE = r"""
\cvsection{Professional Service}
\cvsubsection{Journal Editorial Boards}
\begin{cvitems}
  \item Associate Editor, \textit{Pattern Recognition} (Elsevier), since 2019.
  \item Associate Editor, \textit{Signal, Image and Video Processing} (Springer), since 2013.
  \item Associate Editor, \textit{Machine Vision and Applications} (Springer), since 2005.
\end{cvitems}
\vspace{4pt}
\cvsubsection{Grant-Proposal Review}
\begin{cvitems}
  \item U.S. National Science Foundation (NSF) review panel, Computer Vision --- 2004, 2005, 2008.
  \item Frequent reviewer of grant proposals for the Czech Science Foundation (GA\v{C}R).
\end{cvitems}
\vspace{4pt}
\cvsubsection{Journal Reviewing}
Frequent reviewer for \textit{IEEE Transactions on Image Processing}; \textit{IEEE Transactions on
Geoscience and Remote Sensing}; \textit{IEEE Transactions on Systems, Man, and Cybernetics};
\textit{IEEE Signal Processing Letters}; \textit{Machine Vision and Applications}; \textit{Computer
Vision and Image Understanding}; and \textit{Pattern Recognition}.\par
\vspace{4pt}
\cvsubsection{Conference Reviewing}
Frequent reviewer for IEEE ICIP, IAPR ICPR, IAPR ICIAP, IAPR DICTA, the International Symposium
on Visual Computing (ISVC), and ICIAR.\par
"""

REFERENCES = r"""
\cvsection{References}
Available upon request.
"""

doc = (PREAMBLE + HEADER + EDUCATION + INTERESTS + GRANTS + pub_section()
       + EXPERIENCE + TEACHING + SUPERVISION + SERVICE + REFERENCES
       + "\n\\end{document}\n")

with open(os.path.join(ROOT, "cv", "cv.tex"), "w") as f:
    f.write(doc)

print("Wrote cv/cv.tex")
print("Publications: %d journal, %d conference, %d book chapter (%d total)"
      % (n_j, n_c, n_ch, n_j + n_c + n_ch))
