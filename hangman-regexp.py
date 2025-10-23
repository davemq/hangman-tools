#!/usr/bin/env python

import argparse
import re
import string

global chars, outchars

chars = string.ascii_lowercase
removed_chars = set()


# Split s using all the separators in seps, and return the list
def multi_split(s, sepsset):
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
    global chars, removed_chars

    if not removed_chars:
        s = "[[:lower:]]"
    else:
        # split chars by removed_chars
        seqs = multi_split(chars, removed_chars)
        s = "["
        for item in seqs:
            if len(item) < 4:
                s += item
            else:
                s += f"{item[0]}-{item[-1]}"
        s += "]"

    return s


# Remove ch from chars.
def remove(ch):
    global removed_chars
    removed_chars.add(ch)


if __name__ == "__main__":
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
            remove(ch.lower())
    c.phrase = c.phrase.strip().lower()

    # Replace 2 or more spaces or / surrounded by 0 or more spaces with " XXX "
    c.phrase = re.sub(r" */ *", " XXX ", c.phrase)
    c.phrase = re.sub(r" {2,}", " XXX ", c.phrase)

    # Remove phrase alphabetical characters from chars and outchars
    words = c.phrase.split(" XXX ")
    for w in words:
        wordchars = w.split(" ")
        for ch in wordchars:
            if ch != "_" and ch in chars:
                remove(ch)

    # Write regexp
    regex = ""
    separator = ""
    for w in words:
        regex += separator + "\\<"
        wordchars = w.split(" ")
        unders = 0
        for ch in wordchars:
            if ch != "_":
                if unders > 0:
                    regex += chars_to_string()
                if unders > 1:
                    regex += f"\\{{{unders}\\}}"
                unders = 0
                regex += ch
            else:
                unders += 1
        if unders > 0:
            regex += chars_to_string()
        if unders > 1:
            regex += f"\\{{{unders}\\}}"
        regex += "\\>"
        separator = "[[:space:]]\\+"

    print(regex)
