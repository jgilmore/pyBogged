This is a python implementation of bogged, a word search game.
------------
It WAS implemented in tcl/tk, but I re-implemented it in python 
to allow me to more easily add a few features I was wanting.

After the current functionality is ported over, I plan to implement the
following extra features:

1. a 3-minute timer option.
2. "Qu" as a single tile.
3. Genetic-algorythm optimized virtual dice for maximum average number of found words.
 This turned out to be not the right approach. Ended up with *far* to many E's.
4. network play, via a central bogged server.

The following features have been ported over:

- Efficiently go through the dictionary and use correct rules to winnow out the words that
  can be created on this grid.

These new features have been implemented

- Randomly generate the grid of letters from pre-defined "dice"
- Qu is a single tile
- genetic algorym borrowed, and an evolved set of dice included.
- pyGTK UI implemented
- optional 3 minute timer
- score tracking, saved between sessions in a file (keep each game)
- More evolved set of dice.
- Optional alternate scoring method
- Store and load options from same location as scores.
- Optional hide found words information
- Optional "guest user" setting to allow others to "try it" without screwing up your scores.
- Alternate pipe-free method for windows users (skip grep, minimal imports)

Final version should depend on:

 - 2.5  >= python < 3.0
 - pygtk >= 2.4
 - various python standard library modules

On Posix only:

 - words (POSIX platforms support /usr/share/dict/words, windows does not.)

TODO:

- score tracking, in current set of games
- Show overall percentage
- Score by letter frequency?
- penalty for guessing?
- Penalty for repeating words?
- Switch between several sets of dice?
- Network play client-to-client or via a central server or perhaps through an existing chat protocol?
