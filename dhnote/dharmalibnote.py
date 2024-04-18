import os.path
import unidecode

import pinyin
import chinese_converter

from .note import ObsidianNote
from .utils import (
    H1regexp,
    map_listorstring,
    hanzi2name,
    first_defined_in_dict,
)


HEADER_ORDER = [
    "pk",
    "nom",
    "terme",
    "titre",
    "français",
    "dates",
    "date",
    "auteur",
    "maître",
    "sanskrit",
    "sanskrit-simplified",
    "hànzì",
    "hànzì-simplified",
    "pinyin",
    "pinyin-simplified",
    "rōmaji",
    "rōmaji-simplified",
    "Wades-Giles",
    "portrait",
    "sources",
    "créé",
    "modifié",
    "aliases",
    "tags",
]


class BasicDharmalibNote(ObsidianNote):
    def __init__(self, note, **kwargs):
        super().__init__(note, **kwargs)


class DharmalibNote(BasicDharmalibNote):
    ORDER_REAL_NAME = ["terme", "nom", "titre"]
    TAG = None

    def __init__(self, note, **kwargs):
        super().__init__(note, **kwargs)

        self.newfirst = None
        self.addtotag(self.TAG)

    def do_sort_header(self):
        self.update_aliases()
        self.sort_header()

    def do_first_part(self):
        self.update_firstpart()

    def do_update(self):
        self.update_header()
        self.sort_header()
        self.update_aliases()

        self.update_firstpart()

    def real_name(self):
        for k in self.ORDER_REAL_NAME:
            if k in self.metadata:
                return self.metadata[k]
        return "Personne/Rien"

    def __repr__(self):
        return self.real_name()

    def get_firstpart(self):
        """Première partie :
        - s'il y a '***' dans la note, tout ce qui est avant
        - sinon simplement le premier h1
        """
        self.new_first = f"# {self.real_name()}\n"

        if "résumé" in self.metadata:
            self.new_first += f", {self.metadata['résumé']}"
            if self.new_first[-1] == ".":
                self.new_first += "\n"
            else:
                self.new_first += ".\n"
            self.new_first += "***\n"

    def update_firstpart(self):
        self.get_firstpart()

        if self.new_first is None:
            return False

        if "***\n" in self.content:
            parts = self.content.split("***")
            parts[0] = self.new_first
            self.content = "".join(parts)
        elif H1regexp.match(self.content):
            self.content = H1regexp.sub(self.new_first, self.content, count=1)

        else:
            self.content = self.new_first + self.content

    def save(self, test=False):
        if test:
            super().save("toto.md")
        else:
            super().save()

    def update_header(self):
        for m in HEADER_ORDER:
            if m in self.metadata and self.metadata[m] is None:
                del self.metadata[m]

        for m in ("rōmaji", "pinyin", "sanskrit", "pāli"):
            if m in self.metadata and self.metadata[m] is not None:
                self.metadata[f"{m}-simplified"] = unidecode.unidecode(self.metadata[m])

        if "hànzì" in self.metadata:
            print(self.metadata["hànzì"])

            self.metadata["hànzì-simplified"] = map_listorstring(
                chinese_converter.to_simplified, self.metadata["hànzì"]
            )
        elif "hànzì-simplified" in self.metadata:
            self.metadata["hànzì"] = map_listorstring(
                chinese_converter.to_traditional, self.metadata["hànzì-simplified"]
            )

        if "hànzì" in self.metadata:
            try:
                if "pinyin" not in self.metadata:
                    self.metadata["pinyin"] = map_listorstring(pinyin.get, self.metadata["hànzì"], delimiter="")
                if "pinyin-simplified" not in self.metadata:
                    self.metadata["pinyin-simplified"] = map_listorstring(
                    pinyin.get, self.metadata["hànzì"], delimiter="", format="strip"
                )
            except TypeError:
                pass

    KEYS_FOR_ALIASES = ("rōmaji-simplified", "pinyin-simplified", "sanskrit-simplified")

    def update_aliases(self):
        self.metadata["aliases"] = set()
        for x in self.KEYS_FOR_ALIASES:
            if x in self.metadata:
                self.metadata["aliases"].add(self.metadata[x])
                if x == "rōmaji-simplified":
                    self.metadata["aliases"].add(self.metadata[x].split()[0])
        self.metadata["aliases"] = ", ".join(self.metadata["aliases"])
        if not self.metadata["aliases"]:
            self.metadata.pop("aliases")

    def addtotag(self, t):
        if t is not None and t:
            if "tags" in self.metadata:
                taglist = [_.strip() for _ in self.metadata["tags"].split(",")]
                if t not in taglist:
                    taglist.append(t)
                    taglist.sort()
                    self.metadata["tags"] = ", ".join(taglist)
            else:
                self.metadata["tags"] = self.TAG

    def sort_header(self):
        newmeta = dict()
        for k in HEADER_ORDER:
            if k in self.metadata:
                newmeta[k] = self.metadata.pop(k)
        otherkeys = list()
        for k, v in self.metadata.items():
            if v is not None:
                otherkeys.append(k)
        # otherkeys = list(self.metadata.keys())
        otherkeys.sort()
        for k in otherkeys:
            newmeta[k] = self.metadata.pop(k)
        self.metadata = newmeta
        self.metadata = self.metadata


class Master(DharmalibNote):
    ORDER_REAL_NAME = [
        "français",
        "sanskrit",
        "rōmaji",
        "pinyin-simplified",
        "nom",
    ]
    PRESERVED_METADATA = [
        "nom",
    ]

    TAG = "biographie"

    def __init__(self, note, **kwargs):
        super().__init__(note, **kwargs)
        self.maître = None
        if "maître" in self:
            try:
                self.maître = Master(os.path.join(self.path, self["maître"][2:-2] + ".md"), fromfile = True)
            except FileNotFoundError:
                 pass
            print(f"{self.maître=}")

    def get_firstpart(self):
        # dates = note.metadata.get("dates", "")
        # if "maître" in note.metadata:
        #     disciple = f"disciple de {note.metadata[maître]})"

        self.new_first = f"# {self.bio_element()}\n\n"

        if "portrait" in self.metadata:
            self.new_first += f"![[{self.metadata['portrait']}]]"

        self.new_first += f"{self.bio_element( chinese=True)}"
        if self.maître is not None:
            self.new_first += (
                f", disciple de {self.maître.bio_element(link=True, chinese=True)}"
            )
        if "résumé" in self.metadata:
            self.new_first += f", {self.metadata['résumé']}"

        if self.new_first[-1] == ".":
            self.new_first += "\n\n"
        else:
            self.new_first += ".\n\n"

        self.new_first += "***\n"

    def update_header(self):
        super().update_header()

        if "hànzì" in self.metadata:
            self.metadata["pinyin"] = hanzi2name(self.metadata["hànzì"])
            self.metadata["pinyin-simplified"] = hanzi2name(
                self.metadata["hànzì"], format="strip"
            )

        if nom := first_defined_in_dict(
            self.metadata, ["nom", "pinyin-simplified", "rōmaji-simplified"]
        ):
            self.metadata["nom"] = nom

    def bio_element(self, link=False, chinese=False):

        # tR = f"--> {self.real_name()}"
        tR = ""
        if link:
            if self.real_name() != self.pk:
                tR += f"[[{self.pk}|{self.real_name()}]]"
            else:
                tR += self.mdlink
        else:
            tR += f"{self.real_name()}"

        for k in ["pinyin-simplified", "pinyin"]:
            if k in self.metadata:
                nomchinois = self.metadata[k]
                break
        else:
            nomchinois = None

        if self.real_name() == nomchinois or (not chinese):
            nomchinois = None

        if "dates" in self.metadata:
            tR += " ("

            if nomchinois is not None:
                tR += "*ch.* " + nomchinois + ", "

            tR += self.metadata["dates"] + ")"
        elif nomchinois is not None:
            tR += " (*ch.* " + nomchinois + ")"

        return tR


class Terme(DharmalibNote):
    ORDER_REAL_NAME = [
        "terme",
        "français",
        "sanskrit",
        "rōmaji",
        "pinyin-simplified",
    ]
    KEYS_FOR_ALIASES = ("rōmaji-simplified", "sanskrit-simplified")
    TAG = "glossaire"
    PRESERVED_METADATA = [
        "titre",
    ]

    def __init__(self, note, **kwargs):
        super().__init__(note, **kwargs)

    def update_header(self):
        super().update_header()

        if terme := first_defined_in_dict(
            self.metadata, ["terme", "rōmaji", "français", "pinyin-simplified"]
        ):
            self.metadata["terme"] = terme


class Document(DharmalibNote):
    ORDER_REAL_NAME = [
        "titre",
    ]
    TAG = "document"
    PRESERVED_METADATA = [
        "titre",
    ]
    KEYS_FOR_ALIASES = ("rōmaji-simplified", "pinyin-simplified", "sanskrit-simplified")

    def __init__(self, note, **kwargs):
        super().__init__(note, **kwargs)


class Koan(DharmalibNote):
    ORDER_REAL_NAME = [
        "titre",
    ]
    TAG = "koan"
    PRESERVED_METADATA = [
        "titre",
    ]
    KEYS_FOR_ALIASES = ()

    def __init__(self, note, **kwargs):
        super().__init__(note, **kwargs)
