"""Validation tests for the toolkit structure.

Run: pytest  (or: python -m unittest discover -s tests -v)

Verifies that all components have correct schemas, manifests, frontmatter,
links, and contain no committed secrets. Runs validate_toolkit.py as a unit test.
"""

from __future__ import annotations

import subprocess
import sys
import unittest

from conftest import SCRIPTS


class ToolkitValidation(unittest.TestCase):
	"""Toolkit structure and integrity validation."""

	def test_validate_toolkit(self) -> None:
		"""Run validate_toolkit.py and assert no errors or warnings."""
		validator = SCRIPTS / "validate_toolkit.py"

		result = subprocess.run(
			[sys.executable, str(validator)],
			capture_output=True,
			text=True,
			timeout=30,
		)

		# Print output for debugging
		if result.stdout:
			print(result.stdout)
		if result.stderr:
			print(result.stderr, file=sys.stderr)

		self.assertEqual(
			result.returncode,
			0,
			msg="Toolkit validation failed — see output above",
		)


if __name__ == "__main__":
	unittest.main()
