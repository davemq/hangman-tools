"""Create a regular expression from a hangman-like phrase.

_ represents an unknown letter. Optionally, exclude some letters from
the regular expression; for example, wrong guesses can be excluded.

"""

import argparse
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


def main():
    """Convert the given hangman phrase to a regular expression and print it.

    Optionally remove wrongly guessed characters from the regular expression.
    """
    parser = argparse.ArgumentParser(
        prog="hangman-regexp",
        description="Generate a regular expression from a hangman expression",
    )
    parser.add_argument(
        "-x",
        "--remove",
        help="remove character from generated regular expression",
        action="append",
    )
    parser.add_argument("phrase", help="hangman phrase")

    c = parser.parse_args()

    if c.remove:
        for ch in c.remove:
            removed_chars.add(ch.lower())

    if c.phrase.startswith(" ") or c.phrase.endswith(" "):
        print(
            f"phrase '{c.phrase}' starts or ends with spaces; "
            "possible copy and paste error",
        )
        c.phrase = c.phrase.strip()
    c.phrase = c.phrase.lower()
    c.phrase = c.phrase.replace("\n", " ")

    # Replace 2 or more spaces or / surrounded by 0 or more spaces with " XXX "
    c.phrase = re.sub(r" */ *", " XXX ", c.phrase)
    c.phrase = re.sub(r" {2,}", " XXX ", c.phrase)

    # Remove phrase alphabetical characters from chars and outchars
    word_list = []
    words = c.phrase.split(" XXX ")
    for w in words:
        if len(w) < 1:
            sys.exit("zero length word in phrase")
        wordchars_copy = w.split(" ")
        wordchars = []
        for item in wordchars_copy:
            if len(item) <= 1:
                wordchars.append(item)
            else:
                wordchars.extend(list(item))
        word_list.append(wordchars)
        for ch in wordchars:
            if ch != "_" and ch in chars:
                removed_chars.add(ch)

    # Write regexp
    word_start = "\\<"
    word_end = "\\>"
    regex = ""
    separator = ""
    for w in word_list:
        regex += separator + word_start
        unders = 0
        for ch in w:
            if ch != "_":
                if unders > 0:
                    regex += chars_to_string()
                if unders > 1:
                    regex += f"\\{{{unders}\\}}"
                unders = 0
                regex += ch
                if not ch.isalnum():
                    word_start = ''
                    word_end = ''
            else:
                unders += 1
        if unders > 0:
            regex += chars_to_string()
        if unders > 1:
            regex += f"\\{{{unders}\\}}"
        regex += word_end
        separator = "[[:space:]]\\+"

    print(regex)


if __name__ == "__main__":
    main()
