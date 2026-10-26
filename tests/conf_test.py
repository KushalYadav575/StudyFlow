import importlib
import itertools
import shutil
import subprocess
import sys
from pathlib import Path
from types import SimpleNamespace

import pytest

SRC_PKG = Path(__file__).resolve().parent.parent / "src" / "studyflow"
_counter = itertools.count()

def _build_project(tmp_path, make_data_dir):
    pkg_name = f"sfpkg{next(_counter)}"
    src_root = tmp_path / "src"
    shutil.copytree(
        SRC_PKG, src_root / pkg_name, ignore=shutil.ignore_patterns("__pycache__")
        )
    if make_data_dir:
        (tmp_path / "data").mkdir()
    sys.path.insert(0, str(src_root))
    importlib.invalidate_caches()
    database = importlib.import_module(f"{pkg_name}.database")
    cli = importlib.import_module(f"{pkg_name}.cli")
    return SimpleNamespace(
        name=pkg_name,
        root=tmp_path,
        src_root=src_root,
        db_file=tmp_path / "data" / "studyflow.db",
        database=database,
        cli=cli,
    )

def _cleanup(project):
    sys.path.remove(str(project.src_root))
    for mod in [m for m in sys.modules if m.split(".")[0] == project.name]:
        del sys.modules[mod]

@pytest.fixture
def project(tmp_path):
    p = _build_project(tmp_path, make_data_dir=True)
    yield p
    _cleanup(p)

@pytest.fixture
def project_no_data_dir(tmp_path):
    p = _build_project(tmp_path, make_data_dir=False)
    yield p
    _cleanup(p)

@pytest.fixture
def db(project):
    project.database.make_tables()
    return project.database

@pytest.fixture
def seeded(db):
    subject_id = db.add_subject("Math")
    topic_id = db.add_topic(subject_id, "Algebra")
    return SimpleNamespace(subject_id=subject_id, topic_id=topic_id)

@pytest.fixture
def run_cli(project):
    def _run(*args):
        return subprocess.run(
            [sys.executable, "-m", f"{project.name}.cli", *args],
            cwd=project.root,
            env={"PYTHONPATH": str(project.src_root), "PATH": "/usr/bin:/bin"},
            capture_output=True,
            text=True,
            timeout=30,
        )
    return _run