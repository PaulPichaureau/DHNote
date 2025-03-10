import unittest
from io import BytesIO

from dhnote import DHNote


class DHNoteTests(unittest.TestCase):
    def test_name(self):
        n = DHNote("test")
        self.assertEqual(n.filename, "test.md")

    def test_path(self):
        n = DHNote("test")
        self.assertEqual(n.path, "./test.md")
        n = DHNote("test", destdir="./toto/")
        self.assertEqual(n.path, "./toto/test.md")

    def test_save_output(self):
        outfile = BytesIO()

        n = DHNote("test")
        n.metadata = {"a": 1, "b": 2, "c": [3, 4]}
        n.content = "Rien.\n"

        n.save(outfile=outfile)

        outfile.seek(0)
        content = outfile.read()

        with open("./test_save_output.md") as testfile:
            testcontent = testfile.read().encode("utf-8")

        self.assertEqual(content, testcontent)

    def test_merge_metadata(self):
        n = DHNote("test")
        n.metadata = {"a": 1, "b": 2, "c": [3, 4], "d": [1, 2]}
        n.content = "Rien.\n"

        m = DHNote("test2")
        m.metadata = {"a": 4, "e": 2, "c": 5, "d": [2, 4]}
        m.content = "Rien.\n"

        n.merge_metadata(m)

        merged = {"a": [1, 4], "b": 2, "c": [3, 4, 5], "d": [1, 2, 4], "e": 2}

        self.assertEqual(n.metadata, merged)

    def test_merge(self):
        n = DHNote("test")
        n.metadata = {"a": 1, "b": 2, "c": [3, 4], "d": [1, 2]}
        n.content = "Rien.\n"

        m = DHNote("test2")
        m.metadata = {"a": 4, "e": 2, "c": 5, "d": [2, 4]}
        m.content = "Tout.\n"

        n.merge(m)

        merged = DHNote("test3")
        merged.metadata = {"a": [1, 4], "b": 2, "c": [3, 4, 5], "d": [1, 2, 4], "e": 2}
        merged.content = "Rien.\n\n---\n\nTout.\n"
        self.assertEqual(n, merged)


if __name__ == "__main__":
    unittest.main()
