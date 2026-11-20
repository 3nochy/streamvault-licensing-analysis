"""Execute the StreamVault analysis notebooks in configured order."""

import argparse
import sys

from ipykernel.kernelspec import install as install_kernel
import nbformat
from nbclient import NotebookClient

from pipeline.config import NOTEBOOK_PATHS, PROJECT_ROOT


KERNEL_NAME = "streamvault-analysis"


def register_project_kernel():
    """Register a kernel that runs this project's active Python environment."""
    install_kernel(
        user=False,
        kernel_name=KERNEL_NAME,
        display_name="Python (StreamVault Analysis)",
        prefix=sys.prefix,
    )


def execute_notebook(notebook_path, timeout):
    """Execute one notebook and preserve its outputs, including on failure."""
    notebook = nbformat.read(notebook_path, as_version=4)
    client = NotebookClient(
        notebook,
        timeout=timeout,
        kernel_name=KERNEL_NAME,
        resources={"metadata": {"path": str(PROJECT_ROOT)}},
    )

    try:
        client.execute()
    except Exception:
        # Preserve error output for diagnosis.
        nbformat.write(notebook, notebook_path)
        raise

    nbformat.write(notebook, notebook_path)
    print(f"Executed: {notebook_path.relative_to(PROJECT_ROOT)}")


def main():
    parser = argparse.ArgumentParser(
        description="Run StreamVault profiling and licensing notebooks in order"
    )
    parser.add_argument(
        "--timeout",
        type=int,
        default=600,
        help="maximum seconds allowed for an individual notebook cell",
    )
    args = parser.parse_args()

    register_project_kernel()

    for notebook_path in NOTEBOOK_PATHS:
        try:
            execute_notebook(notebook_path, args.timeout)
        except Exception as exc:
            relative_path = notebook_path.relative_to(PROJECT_ROOT)
            print(
                f"ERROR: Notebook execution failed: {relative_path}",
                file=sys.stderr,
            )
            print(f"Details: {exc}", file=sys.stderr)
            print(
                "WARNING: This run is incomplete. Earlier notebooks may "
                "already have saved updated outputs. Fix the error and "
                "rerun the full workflow before using the results.",
                file=sys.stderr,
            )
            raise SystemExit(1) from exc


if __name__ == "__main__":
    main()
