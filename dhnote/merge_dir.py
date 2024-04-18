import logging
import os
import sys
import argparse
from obsidiannote import ObsidianNote

# Les options

usage = "usage: %prog <command>"
desc = """Description: met à jour l'entête d'une note Dharmalib"""

parser = argparse.ArgumentParser(description=desc)

parser.add_argument(
    "-d",
    "--debug",
    help="Print lots of debugging statements",
    action="store_const",
    dest="loglevel",
    const=logging.DEBUG,
    default=logging.WARNING,
)
parser.add_argument(
    "-i",
    "--info",
    help="Print some infos",
    action="store_const",
    dest="loglevel",
    const=logging.INFO,
    default=logging.WARNING,
)

parser.add_argument(
    "--src1",
    help="first source directory for merge",
    action="store",
    dest="sourcedir1",
    default="./",
)

parser.add_argument(
    "--src2",
    help="second source directory for merge",
    action="store",
    dest="sourcedir2",
    default="./",
)

parser.add_argument(
    "--dest",
    help="destination directory for merge",
    action="store",
    dest="destdir",
    default=None,
)

parser.add_argument(
    "-v",
    "--verbose",
    help="Be verbose",
    action="store_const",
    dest="loglevel",
    const=logging.INFO,
)
parser.add_argument(
    "-t", "--test", help="test", action="store_true", dest="test", default=False
)


args = parser.parse_args(sys.argv[1:])

logging.basicConfig(
    level=args.loglevel,
    format="%(asctime)s [ObsidianNote] [%(levelname)-7.7s]  %(message)s",
    handlers=[logging.FileHandler("ObsidianNote.log"), logging.StreamHandler()],
)


def merge_dir():
    if args.test:
        args.destdir = os.path.join(args.srcdir1, "tmp")
    if args.destdir is None:
        print("Merge dir : pas de répertoire cible spécifié")
        sys.exit(1)
    with os.scandir(args.sourcedir1) as src:
        for entry in src:
            if not (
                entry.is_file()
                and not entry.name.startswith(".")
                and entry.name.endswith(".md")
            ):
                continue
            if not os.path.exists(os.path.join(args.sourcedir2, entry.name)):
                continue
            print(entry.name)
            note1 = ObsidianNote(entry.path, fromfile=True)
            note2 = ObsidianNote(
                os.path.join(args.sourcedir2, entry.name), fromfile=True
            )
            note2.merge(note1)

            note2.path = os.path.join(args.destdir, entry.name)
            note2.save()
