"""Exercise snapshot cleanup against real Git repositories."""

import json
import os
import shutil
import subprocess
import tempfile
import unittest
from pathlib import Path

SNAPSHOT = (
    Path(__file__).resolve().parents[1]
    / "skills/review/self-review/scripts/self_review_snapshot.sh"
)


class SnapshotCleanupTest(unittest.TestCase):
    """Keep new review work while disposing of unchanged input copies."""

    def setUp(self) -> None:
        """Create an isolated repository with a reviewable commit."""
        self.scratch = tempfile.TemporaryDirectory(prefix="snapshot-cleanup-test-")
        self.repo = Path(self.scratch.name).resolve() / "repo"
        self.repo.mkdir()
        self.snapshot_script = Path(self.scratch.name) / "installed" / SNAPSHOT.name
        self.snapshot_script.parent.mkdir()
        shutil.copy2(SNAPSHOT, self.snapshot_script)
        self.snapshot_roots: set[Path] = set()
        self.git("init", "-q")
        self.git("config", "user.name", "Snapshot Test")
        self.git("config", "user.email", "snapshot@example.invalid")
        (self.repo / "tracked.txt").write_text("original\n")
        (self.repo / ".gitignore").write_text("ignored.txt\n")
        self.git("add", ".")
        self.git("commit", "-qm", "Initial files")
        (self.repo / "tracked.txt").write_text("committed change\n")
        self.git("commit", "-qam", "Change tracked file")

    def tearDown(self) -> None:
        """Remove only fixtures created by this test."""
        for root in self.snapshot_roots:
            self.git(
                "worktree", "remove", "--force", str(root / "worktree"), check=False
            )
            shutil.rmtree(root, ignore_errors=True)
        self.scratch.cleanup()

    def git(
        self, *args: str, repo: Path | None = None, check: bool = True
    ) -> subprocess.CompletedProcess[str]:
        """Run real Git in a fixture worktree."""
        return subprocess.run(
            ["git", "-C", str(repo or self.repo), *args],
            check=check,
            capture_output=True,
            text=True,
        )

    def helper(
        self, *args: str, env: dict[str, str] | None = None
    ) -> subprocess.CompletedProcess[str]:
        """Invoke the distributed snapshot CLI."""
        return subprocess.run(
            ["bash", str(self.snapshot_script), *args],
            cwd=self.repo,
            check=False,
            capture_output=True,
            text=True,
            env=env,
        )

    def create(self, *, branch: bool = True) -> tuple[Path, Path]:
        """Create a snapshot and register its artifacts for fixture cleanup."""
        args = ["--base", "HEAD"] if branch else ["--commit", "HEAD"]
        result = self.helper(
            "create-branch" if branch else "create-commit",
            "--repo",
            str(self.repo),
            *args,
        )
        self.assertEqual(result.returncode, 0, result.stderr)
        metadata = Path(result.stdout.strip())
        self.snapshot_roots.add(metadata.parent)
        return metadata, Path(json.loads(metadata.read_text())["worktree"])

    def test_new_untracked_work_survives_cleanup(self) -> None:
        """Retain investigation files added after snapshot creation."""
        metadata, worktree = self.create(branch=False)
        investigation = worktree / "investigation.txt"
        investigation.write_text("new investigation\n")
        result = self.helper("cleanup", "--metadata", str(metadata))
        self.assertTrue(investigation.exists(), result.stderr)
        self.assertEqual(investigation.read_text(), "new investigation\n")
        self.assertNotEqual(result.returncode, 0)
        self.assertIn(str(worktree), result.stderr)

    def test_unchanged_input_copy_is_removed_and_source_is_preserved(self) -> None:
        """Dispose of an unchanged copy without touching source or other worktrees."""
        (self.repo / "tracked.txt").write_text("staged input\n")
        self.git("add", "tracked.txt")
        (self.repo / "tracked.txt").write_text("unstaged input\n")
        (self.repo / "input.txt").write_text("untracked input\n")
        before_status = self.git("status", "--porcelain=v1").stdout
        before_index = self.git("diff", "--cached", "--binary").stdout
        unrelated = Path(self.scratch.name) / "unrelated"
        self.git("worktree", "add", "--detach", str(unrelated), "HEAD")
        (unrelated / "notes.txt").write_text("other work\n")
        metadata, worktree = self.create()
        self.assertEqual((worktree / "tracked.txt").read_text(), "unstaged input\n")
        self.assertEqual((worktree / "input.txt").read_text(), "untracked input\n")
        verified = self.helper("verify", "--metadata", str(metadata))
        self.assertEqual(verified.returncode, 0, verified.stderr)
        result = self.helper("cleanup", "--metadata", str(metadata))
        self.assertEqual(result.returncode, 0, result.stderr)
        self.assertFalse(worktree.exists())
        self.assertTrue(metadata.exists())
        self.assertTrue((metadata.parent / "diff.patch").exists())
        self.assertEqual(self.git("status", "--porcelain=v1").stdout, before_status)
        self.assertEqual(self.git("diff", "--cached", "--binary").stdout, before_index)
        self.assertEqual((self.repo / "tracked.txt").read_text(), "unstaged input\n")
        self.assertEqual((self.repo / "input.txt").read_text(), "untracked input\n")
        self.assertEqual((unrelated / "notes.txt").read_text(), "other work\n")

    def test_clean_commit_snapshot_is_removed(self) -> None:
        """Remove clean commit snapshots while keeping review artifacts."""
        metadata, worktree = self.create(branch=False)
        result = self.helper("cleanup", "--metadata", str(metadata))
        self.assertEqual(result.returncode, 0, result.stderr)
        self.assertFalse(worktree.exists())
        self.assertTrue(metadata.exists())

    def test_native_removal_refusal_preserves_worktree(self) -> None:
        """Honor Git's refusal to remove a locked worktree."""
        metadata, worktree = self.create(branch=False)
        self.git(
            "worktree", "lock", "--reason", "Investigation in progress", str(worktree)
        )
        result = self.helper("cleanup", "--metadata", str(metadata))
        self.assertNotEqual(result.returncode, 0)
        self.assertTrue(worktree.exists())
        self.assertTrue(metadata.exists())
        self.assertIn(str(worktree), result.stderr)
        self.git("worktree", "unlock", str(worktree))

    def test_changed_snapshot_is_retained(self) -> None:
        """Preserve later file, index, HEAD, and ignored-file changes."""
        for change in ("tracked", "staged", "index-only", "head", "ignored"):
            with self.subTest(change=change):
                (self.repo / "tracked.txt").write_text("input copy\n")
                metadata, worktree = self.create()
                if change == "ignored":
                    (worktree / "ignored.txt").write_text("new ignored work\n")
                else:
                    (worktree / "tracked.txt").write_text("new review work\n")
                    if change in ("staged", "index-only", "head"):
                        self.git("add", "tracked.txt", repo=worktree)
                    if change == "index-only":
                        (worktree / "tracked.txt").write_text("input copy\n")
                    if change == "head":
                        self.git("commit", "-qm", "Investigation", repo=worktree)
                before_status = self.git(
                    "status", "--porcelain=v1", repo=worktree
                ).stdout
                before_head = self.git("rev-parse", "HEAD", repo=worktree).stdout
                before_index = self.git(
                    "diff", "--cached", "--binary", repo=worktree
                ).stdout
                result = self.helper("cleanup", "--metadata", str(metadata))
                self.assertTrue(worktree.exists(), result.stderr)
                self.assertNotEqual(result.returncode, 0)
                self.assertIn(str(worktree), result.stderr)
                self.assertEqual(
                    self.git("status", "--porcelain=v1", repo=worktree).stdout,
                    before_status,
                )
                self.assertEqual(
                    self.git("rev-parse", "HEAD", repo=worktree).stdout, before_head
                )
                self.assertEqual(
                    self.git("diff", "--cached", "--binary", repo=worktree).stdout,
                    before_index,
                )
                if change == "ignored":
                    self.assertEqual(
                        (worktree / "ignored.txt").read_text(), "new ignored work\n"
                    )

    def test_creation_failure_preserves_partial_worktree(self) -> None:
        """Preserve partial work when applying the input patch fails."""
        (self.repo / "tracked.txt").write_text("input copy\n")
        bin_dir = Path(self.scratch.name) / "bin"
        bin_dir.mkdir()
        git_path = shutil.which("git")
        self.assertIsNotNone(git_path)
        wrapper = bin_dir / "git"
        wrapper.write_text(
            "#!/usr/bin/env bash\n"
            "if [[ ${1:-} == -C && ${3:-} == apply ]]; then\n"
            '    printf "partial work\\n" > "$2/investigation.txt"\n'
            "    exit 42\n"
            "fi\n"
            'exec "$REAL_GIT" "$@"\n'
        )
        wrapper.chmod(0o755)
        result = self.helper(
            "create-branch",
            "--repo",
            str(self.repo),
            "--base",
            "HEAD",
            env={
                **os.environ,
                "PATH": f"{bin_dir}:{os.environ['PATH']}",
                "REAL_GIT": str(git_path),
            },
        )
        self.assertNotEqual(result.returncode, 0)
        paths = [
            Path(line.removeprefix("worktree "))
            for line in self.git("worktree", "list", "--porcelain").stdout.splitlines()
            if line.startswith("worktree ")
            and Path(line.removeprefix("worktree ")) != self.repo
        ]
        self.snapshot_roots.update(path.parent for path in paths)
        self.assertEqual(len(paths), 1, result.stderr)
        self.assertEqual((paths[0] / "investigation.txt").read_text(), "partial work\n")
        self.assertIn(str(paths[0]), result.stderr)
        self.assertEqual((self.repo / "tracked.txt").read_text(), "input copy\n")


if __name__ == "__main__":
    unittest.main()
