
import json
import sys
from urllib.error import HTTPError, URLError
from urllib.request import Request, urlopen
#%%

# paperId	
# string

# Semantic Scholar’s primary unique identifier for a paper.
# corpusId	
# integer

# Semantic Scholar’s secondary unique identifier for a paper.
# externalIds	
# object

# An object that contains the paper’s unique identifiers in external sources. The external sources are limited to: ArXiv, MAG, ACL, PubMed, Medline, PubMedCentral, DBLP, and DOI.
# url	
# string

# URL of the paper on the Semantic Scholar website.
# title	
# string

# Title of the paper.
# abstract	
# string

# The paper's abstract. Note that due to legal reasons, this may be missing even if we display an abstract on the website.
# venue	
# string

# The name of the paper’s publication venue.
# publicationVenue	
# object

# An object that contains the following information about the journal or conference in which this paper was published: id (the venue’s unique ID), name (the venue’s name), type (the type of venue), alternate_names (an array of alternate names for the venue), and url (the venue’s website).
# year	
# integer

# The year the paper was published.
# referenceCount	
# integer

# The total number of papers this paper references.
# citationCount	
# integer

# The total number of papers that references this paper.
# influentialCitationCount	
# integer

# A subset of the citation count, where the cited publication has a significant impact on the citing publication. Determined by Semantic Scholar’s algorithm: https://www.semanticscholar.org/faq#influential-citations.
# isOpenAccess	
# boolean

# Whether the paper is open access. More information here: https://www.openaccess.nl/en/what-is-open-access.
# openAccessPdf	
# object

# An object that contains the following parameters: url (a link to the paper’s PDF), status (the type of open access https://en.wikipedia.org/wiki/Open_access#Colour_naming_system), the paper's license, and a legal disclaimer.
# fieldsOfStudy	
# Array of strings

# A list of the paper’s high-level academic categories from external sources. The possible fields are: Computer Science, Medicine, Chemistry, Biology, Materials Science, Physics, Geology, Psychology, Art, History, Geography, Sociology, Business, Political Science, Economics, Philosophy, Mathematics, Engineering, Environmental Science, Agricultural and Food Sciences, Education, Law, and Linguistics.
# s2FieldsOfStudy	
# Array of objects

# An array of objects. Each object contains the following parameters: category (a field of study. The possible fields are the same as in fieldsOfStudy), and source (specifies whether the category was classified by Semantic Scholar or by an external source. More information on how Semantic Scholar classifies papers https://medium.com/ai2-blog/announcing-s2fos-an-open-source-academic-field-of-study-classifier-9d2f641949e5)
# publicationTypes	
# Array of strings

# The type of this publication.
# publicationDate	
# string

# The date when this paper was published, in YYYY-MM-DD format.
# journal	
# object

# An object that contains the following parameters, if available: name (the journal name), volume (the journal’s volume number), and pages (the page number range)
# citationStyles	
# object

# The BibTex bibliographical citation of the paper.
	
# Array of objects (Author Info)
	
# Array of objects (Paper Info)
	
# Array of objects (Paper Info)
	
# object (Embedding)
	
# object (Tldr)
# textAvailability	
# string

# fulltext, abstract, or none, based on what we have available for this paper

#%%
# wget http://api.semanticscholar.org/graph/v1/paper/649def34f8be52c8b66281af98ae884c09aef38b?fields=title,year,abstract,citationCount
# with pure request, no functions

paper_id = "649def34f8be52c8b66281af98ae884c09aef38b"
url = f"https://api.semanticscholar.org/graph/v1/paper/{paper_id}?fields=title,year,authors,openAccessPdf"
request = Request(url, headers={"User-Agent": "python"})
json_data = None
try:
    with urlopen(request, timeout=20) as response:
        json_data = json.load(response)
except HTTPError as exc:
    print(f"HTTP error: {exc.code} {exc.reason}", file=sys.stderr)
    # sys.exit(1)
#%%

#%%

import time

while True:
    request = Request(url, headers={"User-Agent": "python"})
    json_data = None
    try:
        with urlopen(request, timeout=20) as response:
            json_data = json.load(response)
    except HTTPError as exc:
        print(f"HTTP error: {exc.code} {exc.reason}", file=sys.stderr)
    except URLError as exc:
        print(f"Network error: {exc.reason}", file=sys.stderr)
    except Exception as exc:
        print(f"Error: {exc}", file=sys.stderr)
    else:
        print("Paper data fetched successfully.")
        break
    time.sleep(2)

#%%

json_data
_data = json_data

#%%