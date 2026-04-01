from dhnote import DharmalibNote

example = """
A period of time following the death of Buddha when his followers, the arhats in particular,
were able to successfully put his dharma (teachings) into practice and gain deliverance from
suffering in the round of rebirth.  [@Sotoshu2023]

[test](google.com)

**Voir aussi :** [[mappo]]


[@Sotoshu2023]: https://www.sotozen.com/fre/library/glossary/individual.html?key=age_of_the_true_dharma
"""

example2 = """ Un essai \n\n"""


def test_create_and_print():
    n = DharmalibNote("test")
    n.content = example
    print(n)


def test_references():
    n = DharmalibNote("test")
    n.content = example
    n.extract_references()
    print("==" * 50)
    print(n)
    print(n.references)
    n.add_references()
    print("==" * 50)
    print(n)


if __name__ == "__main__":
    test_create_and_print()
    test_references()
