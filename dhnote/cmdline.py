import logging
import sys
import argparse
from .dharmalibnote import BasicDharmalibNote, Master, Terme, Document, Koan

# Les options

usage = "usage: %prog <command>"
desc = """Description: met à jour l'entête d'une note Dharmalib"""

parser = argparse.ArgumentParser(description=desc)

parser.add_argument("note")

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


TAG2CLASS = {
    "biographie": Master,
    "glossaire": Terme,
    "recueil": Document,
    "texte": Document,
    "koan": Koan,
}


def load_note():
    if args.test:
        return Master(args.note, fromfile=True)

    try:
        note = BasicDharmalibNote(args.note, fromfile=True)
    except:
        print("Impossible de charger la note")
        sys.exit(1)

    for k, v in TAG2CLASS.items():
        if k == note.metadata["tags"] or k in note.metadata["tags"]:
            return v(args.note, fromfile=True)
    return Terme(args.note, fromfile=True)


def sort_header():
    """custom sort metadatas by keys"""
    note = load_note()
    note.do_sort_header()
    note.save(test=args.test)


def update():
    """compute some metadatas"""
    note = load_note()
    note.do_update()
    note.addtotag("metadatas-updated")
    note.save(test=args.test)
