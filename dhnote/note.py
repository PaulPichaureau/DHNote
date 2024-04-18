from unidecode import unidecode
import os
import re
import sys
import frontmatter


class ON_YAMLHandler(frontmatter.YAMLHandler):
    FM_BOUNDARY = "---"

    POST_TEMPLATE = """\
{start_delimiter}
{metadata}
{end_delimiter}

{content}
"""


def split(self, text):
    """
    Split text into frontmatter and content
    """
    content, fm, _ = text.rsplit(self.FM_BOUNDARY, 2)
    return fm, content


def metadata_equals(m1, m2):
    """Try to guess if two metadata values are equals"""
    if isinstance(m1, str) and isinstance(m2, str):
        return unidecode(m1.lower()) == unidecode(m2.lower())
    if isinstance(m1, list) and isinstance(m2, list):
        s1 = set((unidecode(_.lower()) for _ in m1))
        s2 = set((unidecode(_.lower()) for _ in m2))
        return s1 == s2

    return False


def format(self, post, **kwargs):
    start_delimiter = kwargs.pop("start_delimiter", self.START_DELIMITER)
    end_delimiter = kwargs.pop("end_delimiter", self.END_DELIMITER)
    metadata = self.export(post.metadata, **kwargs)

    return self.POST_TEMPLATE.format(
        content=post.content.strip(),
        metadata=metadata,
        start_delimiter=start_delimiter,
        end_delimiter=end_delimiter,
    )


def merge_list(l1, l2):
    l = set(l1)
    l.update(l2)
    return list(l)


class ObsidianNote:
    INLINE_LINK = r"\[([^\[\]]*)\]\((.*)\)"

    REF = r"\[(\^[^\[\]]*)\][^:(\[\]]"
    REFTEXT = r"\[(\^[^\[\]]*)\]:(.*)"

    OBSIDIAN_REF = r"\[\[([^\[\]]*)\]\]"

    INLINE_LINK_RE = re.compile(INLINE_LINK)
    REF_RE = re.compile(REF)
    REFTEXT_RE = re.compile(REFTEXT)
    OBSIDIAN_REF_RE = re.compile(OBSIDIAN_REF)

    handler = ON_YAMLHandler()

    def __init__(self, src, filename=None, fromfile=False, destdir="./"):
        if fromfile:
            result = frontmatter.load(src)
            self.filename = os.path.basename(src)
            self.path = os.path.dirname(src)

            self.metadata, self.content = result.metadata, result.content
            # WARNING: was self.filename
        else:
            # BUG: il n'y avait pas d'extension ajouté au nom dans une première version
            src = src.strip()
            self.filename = src if src.endswith(".md") else src + ".md"
            self.path = destdir
            self.metadata = dict()
            self.content = ""
        self.pk = self.filename[:-3]
        self.mdlink = f"[[{self.pk}]]"

    def get_references(self):
        """Extract link and references at the end of the content part
        'regular': [foo](some.url)
        'footnotes': [foo][3]

        [3]: some.url
        """

        self.links = list(self.INLINE_LINK_RE.findall(self.content))
        self.obsidian = list(self.OBSIDIAN_REF_RE.findall(self.content))

        self.ref = list(self.REF_RE.findall(self.content))
        self.references = dict(self.REFTEXT_RE.findall(self.content))

    def extract_references(self):
        self.references = dict(self.REFTEXT_RE.findall(self.content))
        self.content = re.sub(self.REFTEXT_RE, "", self.content)

    def add_references(self, references=None):
        ref = references or self.references
        for k, v in ref.items():
            self.content += f"\n[{k}]:{v}"
        self.content += "\n"

    def __getitem__(self, key):
        return self.metadata[key]

    def __setitem__(self, key, value):
        self.metadata[key] = value

    def __contains__(self, key):
        return key in self.metadata

    def __repr__(self):
        return f"Nom : {self.filename}\n" + str(self)

    def __str__(self):
        return self.handler.format(self)
        # s = f"---\n{self.get_header()}---\n\n"

        # s += self.content

        # s = s.replace("\n\n\n", "\n\n")

        # return s

    def __eq__(self, other):
        return (
            isinstance(other, ObsidianNote)
            and self.metadata == other.metadata
            and self.content.strip() == other.content.strip()
        )

    def sort_metadata(self):
        d = dict()
        dd = dict()

        for _ in ["terme", "nom"]:
            if _ in self.metadata:
                d[_] = self.metadata.pop(_)

        for _ in ["pubdate", "résumé"]:
            if _ in self.metadata:
                dd[_] = self.metadata.pop(_)

        d.update(dict(sorted(self.metadata.items())))
        d.update(dd)
        self.metadata = d.copy()

    def add_simplified_metadata(self):
        newmetadata = dict()
        for k, v in self.metadata.items():
            if k in ["rōmaji", "pinyin", "pāli", "sanskrit"]:
                if isinstance(v, list):
                    newmetadata[f"{k}-simplified"] = list()
                    for _ in v:
                        if _ != unidecode(_):
                            newmetadata[f"{k}-simplified"].append(unidecode(_))
                    if not newmetadata[f"{k}-simplified"]:
                        del newmetadata[f"{k}-simplified"]
                elif v != unidecode(v):
                    newmetadata[f"{k}-simplified"] = unidecode(v)
        self.metadata.update(newmetadata)

    def get_header(self):
        self.add_simplified_metadata()
        self.sort_metadata()
        s = ""
        if len(self.metadata):
            for k, v in self.metadata.items():
                if isinstance(v, list):
                    s += f"{k}:\n"
                    for _ in v:
                        s += f"  - {_}\n"
                elif k == "résumé":
                    s += f"résumé: |\n  {v}\n"
                else:
                    s += f"{k}: {v}\n"
        return s

    # clé préservées lors d'un merge

    PRESERVED_METADATA = []

    def merge_metadata(self, other):
        """Fusionne les metadata de cette note et d'une autre"""
        for k, v in other.metadata.items():
            if k in self.PRESERVED_METADATA:
                continue

            if k not in self.metadata:
                self.metadata[k] = v
                continue

            if metadata_equals(self.metadata[k], v):
                continue

            if isinstance(self.metadata[k], list) and isinstance(v, list):
                self.metadata[k].extend(v)
            elif isinstance(v, list):
                self.metadata[k] = [self.metadata[k]] + v
            elif isinstance(self.metadata[k], list):
                self.metadata[k].append(v)
            else:
                self.metadata[k] = [self.metadata[k], v]

            # Remove duplicates
            if isinstance(self.metadata[k], list):
                self.metadata[k] = list(set(self.metadata[k]))
                # collapse one element list
                if len(self.metadata[k]) == 1:
                    self.metadata[k] = self.metadata[k][0]

    def merge_content(self, other, after=False):
        """Fusionne le contenu de cette note et d'une autre. Tente de laisser les appels de notes de bas de pages en fin."""

        other.extract_references()
        self.extract_references()

        if not after:
            self.content = self.content + "\n\n---\n\n" + other.content
        else:
            self.content = other.content + "\n\n---\n\n" + self.content

        self.add_references()
        self.add_references(other.references)

    def merge(self, other):
        self.merge_metadata(other)
        self.merge_content(other)

    def save_with_merge(self, pathname):
        other = ObsidianNote(pathname, fromfile=True)
        other.merge(self)
        other.save(merge=False)

    def save(self, outfile=None, merge=False):
        if merge:
            sys.exit("merge obsolete")
        # if os.path.exists(self.path) and merge:
        #     self.save_with_merge(self.path, outfile=outfile)
        # else:
        if outfile is None:
            outfile = open(os.path.join(self.path,self.filename), "wb")
            # outfile.write(str(self))
        frontmatter.dump(self, outfile, sort_keys=False)
