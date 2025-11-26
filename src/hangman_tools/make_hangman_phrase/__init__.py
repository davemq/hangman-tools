"""Create a hangman-style phrase from a plain text phrase.

Optionally specify guessed letters. Show
- the hangman-style phrase
- guessed letters frequency within the phrase
- wrong guesses
"""

import argparse
import string


def main():
    """Create a hangman-style phrase from a plain text phrase.

    Optionally specify guessed letters. Show
    - the hangman-style phrase
    - guessed letters frequency within the phrase
    - wrong guesses
    """
    parser = argparse.ArgumentParser(
        prog="make-hangman-phrase",
        description="Generate a regular expression from a hangman expression",
    )
    parser.add_argument("-g", "--guess", help="guessed character", action="append")
    parser.add_argument("phrase", help="phrase")

    c = parser.parse_args()
    if not c.guess:
        c.guess = []
    guesses = []
    occur = {}
    for ch in c.guess:
        guesses.append(ch.lower())
        occur[ch.lower()] = 0

    c.phrase = c.phrase.lower()

    # Remove phrase alphabetical characters from chars and outchars
    words = c.phrase.split(" ")

    # Write phrase
    phrase = ""
    for w in words:
        for ch in w:
            if ch in guesses:
                phrase += ch.upper() + " "
                occur[ch.lower()] += 1
            elif ch in string.ascii_lowercase:
                phrase += "_ "
            else:
                phrase += ch + " "
        phrase += "/ "
    phrase = phrase.removesuffix(" / ")

    print(f"Phrase:\t\t{phrase}")

    if not occur:
        print("Occurrences:\tNone")
    else:
        print(f"Occurrences:\t{occur}")

    # write wrong guesses
    wrong = ""
    for g in guesses:
        if g.upper() not in phrase:
            wrong += g.upper()
    if not wrong:
        print("Wrong guess:\tNone")
    else:
        print(f"Wrong guesses:\t{wrong}")

if __name__ == "__main__":
    main()
