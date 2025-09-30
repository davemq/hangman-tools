# hangman-tools

There are two tools here to help with running or playing Hangman style
games online.

  * [hangman-regexp.py](https://github.com/davemq/hangman-tools/blob/main/hangman-regexp.py) creates a regular expression from a hangman
    style expression, which allows searching with tools like `grep`
  * [make-hangman-phrase.py](https://github.com/davemq/hangman-tools/blob/main/make-hangman-phrase.py) creates a hangman style expression from
    plain text. It also has an option to add guesses. It provides the
    hangman style expression, the number of occurrences of guesses
    letters, and a list of wrong guesses.
