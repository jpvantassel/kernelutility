import os
import subprocess
import pathlib
import shutil
import warnings

from .constants import KERNEL_STORE_DIR, CONDA_DIR

class KernelSet():

    def __init__(self, path=KERNEL_STORE_DIR):
        """Acccess a set of kernels as a specific path."""
        path = pathlib.Path(path)

        # Confirm that environments.txt exists.
        # If it does not exist, warn and create empty kernels dict.
        path_to_env = path / "environments.txt"
        if not path_to_env.exists():
            msg = f"No environments found in user space. kernelset has not been initialized."
            warnings.warn(msg, RuntimeWarning)
            self.kernels = {}

        # If environments.txt exists,  load it.
        else:
            self.path_to_env = path_to_env.resolve()
            with path_to_env.open("r") as f:
                envs = f.readlines()
            
            # Parse environments.txt to get kernel names and locations.
            self.kernels = {}
            for env in envs:
                env = env.rstrip()
                if env == "/opt/conda":
                    continue
                else:
                    name = env.split("/")[-1]
                self.kernels[name] = env

            # Restore discovered environments.
            self.restore()

    def create(self, name, python_version=None, verbose=False):
        """Create new kernel."""
        os.makedirs(KERNEL_STORE_DIR, exist_ok=True)
        python_version = "" if python_version is None else f"python={python_version}"
        cmd =  f"conda create --prefix {KERNEL_STORE_DIR}/{name} {python_version} --yes && "
        cmd +=  "conda init bash && "
        cmd +=  "source /opt/conda/etc/profile.d/conda.sh && "
        cmd += f"conda activate {KERNEL_STORE_DIR}/{name} && "
        cmd +=  "conda install -y ipykernel && "
        cmd += f"ipython kernel install --name {name} --user && "
        cmd += f"cp -r /home/jupyter/.local/share/jupyter/kernels/{name}/ {KERNEL_STORE_DIR}/{name} && "
        cmd += f"cp /home/jupyter/.conda/environments.txt {KERNEL_STORE_DIR} && "
        cmd += f"rm -r /home/jupyter/.local/share/jupyter/kernels/{name}/"
        stdout = None if verbose else subprocess.DEVNULL
        subprocess.run(cmd, shell=True, check=True, stdout=stdout, executable="/bin/bash")
        self.kernels[name] = f"{KERNEL_STORE_DIR}/{name}"

    def restore(self, verbose=False):
        """(Re)activate a KernelSet."""
        os.makedirs(CONDA_DIR, exist_ok=True)
        shutil.copy(self.path_to_env, f"{CONDA_DIR}/environmnets.txt")
        cmd =  "conda init bash && "
        cmd += "source /opt/conda/etc/profile.d/conda.sh && "
        for name, path in self.kernels.items():
            cmd += f"conda activate {KERNEL_STORE_DIR}/{name} && "
            cmd +=  "conda install ipykernel -y && "
        cmd += "echo User-defined kernels have been restored."

        stdout = None if verbose else subprocess.DEVNULL
        subprocess.run(cmd, shell=True, check=True, stdout=stdout, executable="/bin/bash")

    def add(self, path):
        """Add environment from path."""
        path = pathlib.Path(path)
        name = path.resolve.split("/")[-1]
        new_path = f"{KERNEL_STORE_DIR}/{name}"
        shutil.copy(path.resolve(), new_path)
        self.kernels[name] = new_path

    def __str__(self):
        """Human-readable representation of KernelSet."""
        njust = 10
        ks = f"{'base'.ljust(njust)}/opt/bin/\n"
        for name, path in self.kernels.items():
            ks.append(f"{name.ljust(njust)}\t{path}\n")
        return ks
