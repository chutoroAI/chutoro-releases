import hashlib
from pathlib import Path
import tempfile
import unittest

from release_manifest import build_manifest


class ManifestTests(unittest.TestCase):
    def setUp(self):
        self.temp = tempfile.TemporaryDirectory()
        self.addCleanup(self.temp.cleanup)
        self.directory = Path(self.temp.name)
        for system in ("darwin", "linux", "windows"):
            for arch in ("amd64", "arm64"):
                name = f"chutoro-delivery-1.2.3-{system}-{arch}" + (".exe" if system == "windows" else "")
                (self.directory / name).write_bytes(name.encode())

    def test_hashes_actual_six_artifacts(self):
        manifest = build_manifest("1.2.3", self.directory)
        self.assertEqual(manifest["version"], "1.2.3")
        self.assertEqual(len(manifest["sha256"]), 6)
        for name, digest in manifest["sha256"].items():
            self.assertEqual(digest, hashlib.sha256(name.encode()).hexdigest())

    def test_missing_artifact_rejected(self):
        next(self.directory.iterdir()).unlink()
        with self.assertRaises(ValueError):
            build_manifest("1.2.3", self.directory)

    def test_extra_or_wrong_version_artifact_rejected(self):
        (self.directory / "chutoro-delivery-9.9.9-linux-arm64").write_bytes(b"extra")
        with self.assertRaises(ValueError):
            build_manifest("1.2.3", self.directory)

    def test_invalid_version_rejected(self):
        for version in ("latest", "1.2.3\n", "1.2.3;bad"):
            with self.assertRaises(ValueError):
                build_manifest(version, self.directory)

    def test_empty_artifact_rejected(self):
        next(self.directory.iterdir()).write_bytes(b"")
        with self.assertRaises(ValueError):
            build_manifest("1.2.3", self.directory)


if __name__ == "__main__":
    unittest.main()
