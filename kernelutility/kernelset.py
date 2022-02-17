import os
import subprocess
import pathlib
import shutil

from .constants import KERNEL_STORE_DIR, CONDA_DIR

class KernelSet():

    def __init__(self, path=KERNEL_STORE_DIR):
        """Acccess a set of kernels as a specific path."""
        path = pathlib.Path(path)

        # Confirm that environments.txt exists.
        path_to_env = path / "environment.txt"
        if not path_to_env.exists():
            msg = f"Path {path_to_env.resolve()} does not contain environments.txt."
            raise FileNotFoundError(msg)

        # If environments.txt exists,  load it.
        self.path_to_env = path_to_env.resolve()
        with path_to_env.open("r") as f:
            envs = f.readlines()
        
        # Parse environments.txt to get kernel names and locations.
        self.kernels = {}
        for env in envs:
            if env == "/opt/conda":
                name = "base"
            else:
                name = env.split("/")[-1]
            self.kernels[name] = env

    @classmethod
    def create(cls, name, python_version=None):
        """Create new kernel."""
        os.makedirs(KERNEL_STORE_DIR, exist_ok=True)
        python_version = "" if python_version is None else f"python={python_version}"
        cmd =  f"conda create --prefix {KERNEL_STORE_DIR}/{name} {python_version} --yes && "
        cmd +=  "conda init bash && "
        cmd +=  "source /opt/conda/etc/profile.d/conda.sh && "
        cmd += f"conda activate {KERNEL_STORE_DIR}/{name} && "
        cmd +=  "conda install -y ipykernel && "
        cmd +=  "ipython kernel install --name {name} --user && "
        cmd += f"cp -r /home/jupyter/.local/share/jupyter/kernels/{name}/ {KERNEL_STORE_DIR}/{name} && "
        cmd += f"cp /home/jupyter/.conda/environments.txt {KERNEL_STORE_DIR} && "
        cmd += f"rm -r /home/jupyter/.local/share/jupyter/kernels/{name}/"

        subprocess.run(cmd.split(" "), shell=True)

    def restore(self):
        """(Re)activate a KernelSet."""
        os.makedirs(CONDA_DIR, exist_ok=True)
        shutil.copy(self.path_to_env, f"{CONDA_DIR}/environmnets.txt")
        cmd =  "conda init bash && "
        cmd += "source /opt/conda/etc/profile.d/conda.sh && "
        for name, path in self.kernels:
            cmd += f"conda activate {KERNEL_STORE_DIR}/{name} && "
            cmd +=  "conda install ipykernel -y && "
        cmd += "echo User-defined kernels have been restored."

        subprocess.run(cmd.split(" "), shell=True)
        