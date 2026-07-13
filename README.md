# Nations
Nations the board game rules implementation

## Usage

This repo can be used as a library or on the command line to play Nations matches. It can also read a replay
or group of replays and repeat all the moves with the same state. Optionally, it can collect stats from those replay(s).

### Stats

To gather stats from a group of replays, `cd` to the parent directory of your clone of this repo, and run

`python -m nations --quiet --replays completed_matches_2001.tar.gz --stats -`

The `-` argument to `--stats` means `stdout`. You can specify a file name instead.

Replay bundles can be downloaded from https://games.tabony.net/nations/stats/

### Playing Nations

This repo can be imported as a module by the Tabony Games website repo: https://github.com/Logitude/TabonyGames

This repo can also be run on the command line by going to the parent directory and running `python -m nations --help`

The command-line interface, implemented in `cli.py`, does not show the complete game state. It could use some work to be fully functional.
Its purpose was to be a stepping stone until the website user interface was functional.
