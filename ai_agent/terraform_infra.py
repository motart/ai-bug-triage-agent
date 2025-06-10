import os
import subprocess
from pathlib import Path


class TerraformInfrastructure:
    """Run Terraform to provision infrastructure."""

    def __init__(self, directory: str | Path):
        self.directory = Path(directory)

    def apply(self) -> None:
        """Initialize and apply the Terraform configuration."""
        if not self.directory.is_dir():
            raise ValueError(f"Terraform directory {self.directory} does not exist")

        env = os.environ.copy()
        cmds = [
            ["terraform", "init"],
            ["terraform", "apply", "-auto-approve"],
        ]
        for cmd in cmds:
            subprocess.run(cmd, cwd=self.directory, check=True, env=env)
