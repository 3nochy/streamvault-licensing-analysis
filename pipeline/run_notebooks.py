import argparse
import sys

from ipykernel.kernelspec import install as install_kernel
import nbformat
from nbclient import NotebookClient
from pipeline.config import PROJECT_ROOT


NOTEBOOKS = (
    PROJECT_ROOT / "explore" / "data_profiling.ipynb",
    PROJECT_ROOT / "explore" / "licensing_analysis.ipynb",
)
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
        # Preserve the error output in the notebook so failures are inspectable.
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
    for notebook_path in NOTEBOOKS:
        execute_notebook(notebook_path, args.timeout)


if __name__ == "__main__":
    main()
