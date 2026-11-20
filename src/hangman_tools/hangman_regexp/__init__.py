"""Create and print a regular expression from a hangman-like phrase.

'_' (underscore) represents an unknown letter. Optionally, exclude some letters
from the regular expression; for example, wrong guesses can be excluded.

Words are separated by a '/' (forward slash) character.

"""

import argparse
from collections import namedtuple
import pyparsing as pp
import re
import string
import sys

chars = string.ascii_lowercase
removed_chars = set()

def multi_split(s, sepsset):
    """Split s using all the separators in seps, and return the list."""
    if len(sepsset) == 0:
        return list(s)

    seps = list(sepsset)
    seps.sort()
    words = []
    for c in seps:
        w = s.split(sep=c, maxsplit=1)
        if len(w[0]) != 0:
            words.append(w[0])
        s = w[1]
    if len(s) != 0:
        words.append(s)
    return words


def chars_to_string():
    """Convert chars to a regular expression."""
    if not removed_chars:
        s = "[[:lower:]]"
    else:
        # split chars by removed_chars
        seqs = multi_split(chars, removed_chars)
        s = "["
        for item in seqs:
            if len(item) < len("a-d"):
                s += item
            else:
                s += f"{item[0]}-{item[-1]}"
        s += "]"

    return s


def single_letter(s):
    """Validate that s is a single letter a-z, and return it lowercased."""
    ch = s.lower()
    if len(ch) != 1 or ch not in chars:
        raise argparse.ArgumentTypeError(f"must be a single letter a-z: {s!r}")
    return ch


def main():
    """Convert the given hangman phrase to a regular expression and print it.

    A hangman phrase has '_' characters as wildcards. Words are separated
    by '/' (forward slash) characters.

    """
    parser = argparse.ArgumentParser(
        prog="hangman-regexp",
        description="""
        Generate a regular expression from a hangman expression.
        Wildcards are represented by '_' (underscore) characters.
        Words are separated by '/' (forward slash) characters.
        Incorrectly guessed letters may be removed from the
        generated phrase using the '-x' option.
        """,
    )
    parser.add_argument(
        "-x",
        "--remove",
        help="remove character from generated regular expression",
        action="append",
        type=single_letter,
    )
    parser.add_argument("phrase", help="hangman phrase")

    c = parser.parse_args()

    if c.remove:
        for ch in c.remove:
            removed_chars.add(ch)

    c.phrase = c.phrase.lower()
    c.phrase = c.phrase.replace("\n", "")
    c.phrase = c.phrase.replace(" ", "")

    word = pp.Word(pp.srange(r"[-._,?'a-z]"))
    words = pp.Opt(pp.Literal("/")).suppress() + \
        pp.DelimitedList(expr=word, delim="/", allow_trailing_delim=True).set_results_name("words", list_all_matches=True)
    word_list = words.parse_string(c.phrase, parse_all=True)

    # Remove phrase alphabetical characters from chars and outchars
    for w in word_list:
        for ch in w:
            if ch != "_" and ch in chars:
                removed_chars.add(ch)

    # constants
    WordParts = namedtuple('WordParts', ['start', 'end'])
    wordparts = WordParts(start="\\<", end="\\>")

    def literal(s):
        """Escape s so it matches itself in a (GNU basic) regular expression.

        Of the punctuation characters hangman-regexp accepts, only '.' is
        special; the others ('-', ',', '?', "'") are ordinary characters.
        """
        return s.replace(".", "\\.")

    # Write regexp
    regex = ""
    separator = ""
    for w in word_list:
        # grep's \< and \> only match next to a *word* character (letter,
        # digit or underscore). Punctuation such as ',' is not a word
        # character, so "\<abc,\>" can never match: \> needs a word character
        # right before it. The same goes for leading punctuation and \<.
        #
        # So split the word into three parts:
        #     lead   punctuation before the first letter/wildcard  -> before \<
        #     core   everything in between                         -> inside \< \>
        #     trail  punctuation after the last letter/wildcard    -> after \>
        # For example, "'___," has lead "'", core "___" and trail ",".
        #
        # Punctuation in the middle of the core, as in "don't" or
        # "well-known", is fine where it is: once the wildcards are filled in,
        # it sits between two letters.
        #
        # '_' is deliberately not in the strip list. It is the wildcard, so it
        # is part of the core.
        core = w.strip("-.,?'")
        if not core:
            # The word is only punctuation (e.g. "-"). There is no word
            # character for \< or \> to attach to, so emit it as a literal.
            regex += separator + literal(w)
            separator = "[[:space:]]\\+"
            continue
        lead = w[:w.index(core)]
        trail = w[len(lead) + len(core):]
        regex += separator + literal(lead) + wordparts.start

        # Walk the core. Consecutive '_' wildcards are counted in `unders`
        # and written out as one character class with a repeat count, e.g.
        # "___" becomes "[b-z]\{3\}". Any other character ends the run, so
        # flush the pending wildcards first and then write that character.
        unders = 0
        for ch in core:
            if ch != "_":
                if unders > 0:
                    regex += chars_to_string()
                if unders > 1:
                    regex += f"\\{{{unders}\\}}"
                unders = 0
                regex += literal(ch)
            else:
                if len(removed_chars) >= len(string.ascii_lowercase):
                    sys.exit("Wildcard in input but there are no wildcard characters")
                unders += 1
        # Flush any wildcards still pending at the end of the core.
        if unders > 0:
            regex += chars_to_string()
        if unders > 1:
            regex += f"\\{{{unders}\\}}"

        # Close the word, then add any trailing punctuation outside the
        # boundary.
        regex += wordparts.end + literal(trail)
        # Words are separated by one or more whitespace characters.
        separator = "[[:space:]]\\+"

    print(regex)


if __name__ == "__main__":
    main()
