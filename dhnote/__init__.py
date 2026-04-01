from .dharmalibnote import DharmalibNote

name = "dhnote"
__all__ = ["DharmalibNote"]


def mergenotes(n1, n2):
    """Fusionne deux notes, le résultat est sauvegardé dans n2."""
    n1.save(n2.filename, merge=True)
