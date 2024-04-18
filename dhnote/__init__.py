from .note import ObsidianNote
from .dharmalibnote import Terme

name = "obsidiannote"
__all__ = ["ObsidianNote", "Terme"]


def mergenotes(n1, n2):
    """merge 2 notes in dest
    if no dest specified, merge them in n2
    """
    n1.save(n2.filename, merge=True)


example = """
A period of time following the death of Buddha when his followers, the arhats in particular, were able to successfully put his dharma (teachings) into practice and gain deliverance from suffering in the round of rebirth.  [@Sotoshu2023]

[test](google.com)

**Voir aussi :** [[mappo]]


[@Sotoshu2023]: https://www.sotozen.com/fre/library/glossary/individual.html?key=age_of_the_true_dharma
"""

example2 = """ Un essai \n\n"""

if __name__ == "__main__":
    n = ObsidianNote("test")
    n.content = example

    print(n)

    n.extract_references()
    print("==" * 50)
    print(n)
    print(n.references)

    n.add_references()
    print("==" * 50)
    print(n)

    n.save()

    m = ObsidianNote("test")
    m.content = example2
    m.save(merge=True)
