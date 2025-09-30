#!/usr/bin/env python

import argparse
import re
import string

global chars

chars = string.ascii_lowercase

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
            chars = chars.replace(ch.lower(), "")

    c.phrase = c.phrase.lower()

    # Replace 2 or more spaces or / surrounded by 0 or more spaces with " XXX "
    c.phrase = re.sub(r" */ *", " XXX ", c.phrase)
    c.phrase = re.sub(r" {2,}", " XXX ", c.phrase)

    # Remove phrase alphabetical characters from chars and outchars
    words = c.phrase.split(" XXX ")
    for w in words:
        wordchars = w.split(" ")
        for ch in wordchars:
            if ch in chars:
                chars = chars.replace(ch, "")

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
                    regex += f"[{chars}]"
                if unders > 1:
                    regex += f"\\{{{unders}\\}}"
                unders = 0
                regex += ch
            else:
                unders += 1
        if unders > 0:
            regex += f"[{chars}]"
        if unders > 1:
            regex += f"\\{{{unders}\\}}"
        regex += "\\>"
        separator = "[[:space:]]\\+"

    print(regex)
