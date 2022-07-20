from functools import reduce


def get_orcid_url(orcid):
    """Return the URL to the ORCID profile with a given identifier."""
    return f"https://orcid.org/{orcid}"


def check_orcid(orcid):
    """Return a boolean indicating if the ORCID number is valid.

    Implemented based on the instructions given at:
    https://support.orcid.org/hc/en-us/articles/360006897674-Structure-of-the-ORCID-Identifier  # NOQA
    """
    # Remove dashes and convert to a list of integers
    orcid = [
        10 if digit.upper() == "X" else int(digit)  # 'X' corresponds to 10
        for digit in list("".join(orcid.split("-")))
    ]

    # Calculate the checksum
    checksum = reduce(lambda checksum, digit: (checksum + digit) * 2, orcid[:-1], 0)

    # Validate the checksum
    return (12 - checksum % 11) % 11 == orcid[-1]
