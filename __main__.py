import argparse
import os
import pathlib
import json

from . import *

arg_parser = argparse.ArgumentParser()
arg_parser.add_argument('--seed')
arg_parser.add_argument('--replay')
arg_parser.add_argument('--quit-after-replay', action='store_true')
arg_parser.add_argument('--quiet', action='store_true')
arg_parser.add_argument('--replay-out')
arg_parser.add_argument('--log')
arg_parser.add_argument('--state')
arg_parser.add_argument('--players', nargs='*')
args = arg_parser.parse_args()

seed = args.seed

if args.replay_out is not None:
    replay_out_path = pathlib.Path(args.replay_out)
    os.makedirs(replay_out_path.parent, exist_ok=True)

if args.log is not None:
    log_path = pathlib.Path(args.log)
    os.makedirs(log_path.parent, exist_ok=True)

if args.state is not None:
    state_path = pathlib.Path(args.state)
    os.makedirs(state_path.parent, exist_ok=True)

replay = None
if args.replay is not None:
    with open(args.replay) as replay_file:
        replay = replay_file.read().rstrip('\n')

player_names = None
if replay is None:
    if args.players is None:
        player_names = ('Sidonia', 'Sundae', 'Nutmeg')
    else:
        player_names = args.players

quit_after_replay = args.quit_after_replay
verbose = not args.quiet

interface = cli.NationsCLI(player_names=player_names, seed=seed, replay=replay, quit_after_replay=quit_after_replay, verbose=verbose)

exception = None
try:
    interface.play()
except Exception as e:
    exception = e

if args.replay_out is not None:
    with open(replay_out_path, 'w') as replay_out_file:
        replay_out_file.write(interface.get_replay())

if args.log is not None:
    with open(log_path, 'w') as log_file:
        log_file.write(interface.get_log())

if args.state is not None:
    with open(state_path, 'w') as state_file:
        json.dump(interface.get_state(), state_file, indent=4)

if exception is not None:
    raise exception
