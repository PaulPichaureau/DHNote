import unittest
from io import BytesIO

from obsidiannote import ObsidianNote


class ObsidianNoteTests(unittest.TestCase):
    def test_name(self):
        n = ObsidianNote("test")
        self.assertEqual(n.filename, "test.md")

    def test_path(self):
        n = ObsidianNote("test")
        self.assertEqual(n.path, "./test.md")
        n = ObsidianNote("test", destdir="./toto/")
        self.assertEqual(n.path, "./toto/test.md")

    def test_save_output(self):
        outfile = BytesIO()

        n = ObsidianNote("test")
        n.metadata = {"a": 1, "b": 2, "c": [3, 4]}
        n.content = "Rien.\n"

        n.save(outfile=outfile)

        outfile.seek(0)
        content = outfile.read()

        with open("./test_save_output.md") as testfile:
            testcontent = testfile.read().encode("utf-8")

        self.assertEqual(content, testcontent)

    def test_merge_metadata(self):
        n = ObsidianNote("test")
        n.metadata = {"a": 1, "b": 2, "c": [3, 4], "d": [1, 2]}
        n.content = "Rien.\n"

        m = ObsidianNote("test2")
        m.metadata = {"a": 4, "e": 2, "c": 5, "d": [2, 4]}
        m.content = "Rien.\n"

        n.merge_metadata(m)

        merged = {"a": [1, 4], "b": 2, "c": [3, 4, 5], "d": [1, 2, 4], "e": 2}

        self.assertEqual(n.metadata, merged)

    def test_merge(self):
        n = ObsidianNote("test")
        n.metadata = {"a": 1, "b": 2, "c": [3, 4], "d": [1, 2]}
        n.content = "Rien.\n"

        m = ObsidianNote("test2")
        m.metadata = {"a": 4, "e": 2, "c": 5, "d": [2, 4]}
        m.content = "Tout.\n"

        n.merge(m)

        merged = ObsidianNote("test3")
        merged.metadata = {"a": [1, 4], "b": 2, "c": [3, 4, 5], "d": [1, 2, 4], "e": 2}
        merged.content = "Rien.\n\n---\n\nTout.\n"
        self.assertEqual(n, merged)


if __name__ == "__main__":
    unittest.main()
