import tarfile

def extract_replays(replays_file):
    replays = []
    with tarfile.open(replays_file) as tar:
        for tarinfo in tar:
            replays.append(tar.extractfile(tarinfo).read().decode())
    return replays
