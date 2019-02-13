import os

import pycodestyle

import truthdiscovery


class TestCodeStyle:
    """
    Check source code style according to pycodestyle.

    The code should always meet the PEP8 guidelines. More specific code style
    checks are done with pylint, but this is not automated since we allow some
    pylint failures
    """
    REPO_ROOT = os.path.dirname(truthdiscovery.__file__)

    def test_pep8(self):
        style = pycodestyle.StyleGuide()
        report = style.check_files(paths=self.get_source_files(self.REPO_ROOT))
        num_errors = report.get_count()
        assert num_errors == 0, "{} pycodestyle error(s)".format(num_errors)

    def get_source_files(self, root_dir):
        for dirpath, dirnames, filenames in os.walk(root_dir):
            # Skip migration files
            if os.path.split(dirpath)[-1] in ("migrations", "migrations.orig"):
                continue

            for filename in filenames:
                full_path = os.path.join(dirpath, filename)
                if full_path.endswith(".py"):
                    yield full_path
