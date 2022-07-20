# Journal rating points scale

JOURNAL_RATING_POINTS = [
    0,
    20,
    40,
    70,
    100,
    140,
    200,
]


# Journal rating points source URL

JOURNAL_RATING_URL = "https://wykazy.net.pl/"


# Elements Digital Object Identifier (DOI) regular expression string
# Source: https://www.crossref.org/blog/dois-and-matching-regular-expressions/

DOI_REGEX = r"10.\d{4,9}/[-._;()/:a-zA-Z0-9]+"


# Prefix for URLs to the articles based on their DOIs

DOI_URL_PREFIX = "https://doi.org"


# Minimum value for the article's publication date

MIN_ARTICLE_YEAR = 1900


# A number of years in the future allowed to report the articles

MAX_ARTICLE_YEAR_OFFSET = 1
