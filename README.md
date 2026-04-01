# DHNote

Bibliothèque Python pour manipuler les notes du projet Dharmalib au format Obsidian.md.

Gère la lecture, l'écriture, le tri et la fusion de notes avec en-tête YAML (frontmatter),
avec une gestion spécifique des types de notes Dharmalib : termes, personnes, textes, koans.

## Installation

```bash
uv sync
```

## Commandes disponibles

### `dhnote-sort`

Trie les clés de l'en-tête YAML d'une note selon l'ordre Dharmalib.

```bash
dhnote-sort chemin/vers/note.md
```

### `dhnote-update`

Recalcule et met à jour certaines métadonnées automatiques d'une note.

```bash
dhnote-update chemin/vers/note.md
```

### `dhnote-mergedir`

Fusionne les notes de deux répertoires source dans un répertoire destination.

```bash
dhnote-mergedir --src1 dir1/ --src2 dir2/ --dest dest/
```

## Utilisation comme bibliothèque

```python
from dhnote import DharmalibNote

note = DharmalibNote("ma-note", fromfile=True)
note.do_sort_header()
note.save()
```

## Types de notes supportés

- `Term` — termes bouddhistes
- `Person` — personnes historiques
- `Document` — textes et compilations
- `Koan` — koans

## Dépendances

- [python-frontmatter](https://github.com/eyeseast/python-frontmatter) — lecture/écriture YAML frontmatter
- [hanziconv](https://github.com/berniey/hanziconv) — conversion caractères chinois simplifiés/traditionnels
- [pinyin](https://pypi.org/project/pinyin/) — translittération pinyin
- [Unidecode](https://pypi.org/project/Unidecode/) — translittération unicode
- [chinese-converter](https://pypi.org/project/chinese-converter/) — conversion chinois
- [BeautifulSoup4](https://www.crummy.com/software/BeautifulSoup/) — parsing HTML
