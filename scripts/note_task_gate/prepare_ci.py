"""Fetch and verify the durable Note/Task packet for a CI run."""

import argparse
import hashlib
import shutil
import tarfile
import urllib.request
from pathlib import Path, PurePosixPath

from gate import require, verify

URL = (
    "https://github.com/DocumentDrivenDX/batten/releases/download/"
    "note-task-packet-20261111/note-task-20261111.tar.gz"
)
SHA256 = "55860ce18bb43d2567319dd9dcd842debcee76bedcd97e638e19b8d036c72b90"
BYTES = 64_390_716
ROOT = "20261111"


def download(path):
    checksum = hashlib.sha256()
    size = 0
    with urllib.request.urlopen(URL, timeout=45) as source, path.open("xb") as output:
        while block := source.read(1024 * 1024):
            size += len(block)
            require(size <= BYTES, "release asset exceeds pinned length")
            checksum.update(block)
            output.write(block)
    require(
        size == BYTES and checksum.hexdigest() == SHA256, "release archive pin differs"
    )


def extract(archive, destination):
    seen = set()
    with tarfile.open(archive, "r:gz") as packet:
        for entry in packet:
            name = PurePosixPath(entry.name)
            require(
                name.parts and name.parts[0] == ROOT and ".." not in name.parts,
                "release archive path is outside the packet",
            )
            require(name not in seen, "duplicate release archive path")
            seen.add(name)
            output = destination.joinpath(*name.parts)
            if entry.isdir():
                output.mkdir(parents=True, exist_ok=True)
            elif entry.isfile():
                output.parent.mkdir(parents=True, exist_ok=True)
                with packet.extractfile(entry) as source, output.open("xb") as target:
                    shutil.copyfileobj(source, target)
            else:
                raise RuntimeError("release archive contains a link or special file")


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("directory", type=Path)
    args = parser.parse_args()
    args.directory.mkdir()
    archive = args.directory / "packet.tar.gz"
    download(archive)
    extract(archive, args.directory)
    count = verify(args.directory / ROOT)
    archive.unlink()
    print(f"Verified {count} pinned release inputs.")


if __name__ == "__main__":
    main()
