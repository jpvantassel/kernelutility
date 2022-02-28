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
        path_to_envs_txt = path / "environments.txt"
        if not path_to_envs_txt.exists():
            msg = f"No environments found in user space. kernelset has not been initialized."
            warnings.warn(msg, RuntimeWarning)
            self.kernels = {}

        # If environments.txt exists, load it.
        else:
            self.path_to_envs_txt = path_to_envs_txt.resolve()
            with path_to_envs_txt.open("r") as f:
                lines = f.readlines()
            
            # Parse environments.txt to get kernel names and locations.
            self.kernels = {}
            for line in lines:
                path_to_env = pathlib.PurePath(line.rstrip())
                # Skip the base environemnt.
                if path_to_env == pathlib.PurePath("/opt/conda"):
                    continue
                # All others will be stored.
                else:
                    name = path_to_env.name
                self.kernels[name] = str(path_to_env)

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

    def destroy(self, name):
        """Remove kernel and deletes all assocaited files on disk.
        
        Parameters
        ----------
        name : str
            Name of kernel to be destroyed.

        Returns
        -------
        None
            Removes environment from KernelSet and deletes all associated
        environemnt files on disk.

        """
        self.remove(name)
        shutil.rmtree(f"{KERNEL_STORE_DIR}/{name}")

    def restore(self, verbose=False):
        """(Re)activate a KernelSet."""
        os.makedirs(CONDA_DIR, exist_ok=True)
        shutil.copy(self.path_to_envs_txt, f"{CONDA_DIR}/environments.txt")
        self._restore(self.kernels, verbose=verbose)

    @staticmethod
    def _restore(kernels, verbose=False):
        cmd =  "conda init bash && "
        cmd += "source /opt/conda/etc/profile.d/conda.sh && "
        for name in kernels.keys():
            cmd += f"conda activate {KERNEL_STORE_DIR}/{name} && "
            cmd +=  "conda install ipykernel -y && "
        cmd += "echo User-defined kernels have been restored."

        stdout = None if verbose else subprocess.DEVNULL
        subprocess.run(cmd, shell=True, check=True, stdout=stdout, executable="/bin/bash")

    def add(self, path, verbose=False):
        """Add environment from path by making a personal copy.
        
        Parameters
        ----------
        path : str
            Path to directory containing the environment.

        Returns
        -------
        None
            Adds environment to the current available environments.

        """
        path = pathlib.Path(path)
        name = path.name
        new_path = pathlib.Path(f"{KERNEL_STORE_DIR}/{name}/")
        if path.resolve() != new_path:
            shutil.copytree(path, new_path)
        self.kernels[name] = str(new_path)
        
        with open(f"{KERNEL_STORE_DIR}/environments.txt", "a") as f:
            f.write(f"{str(new_path)}\n")

        self._restore(self.kernels, verbose=verbose)

    def remove(self, name):
        """Removes kernel from KernelSet, but does not delete associated files from disk.
        
        Parameters
        ----------
        name : str
            Name of kernel to be removed.

        Returns
        -------
        None
            Removes environment.

        """
        if name not in self.kernels.keys():
            msg = f"name={name} not in KernelSet, try one of the following {list(self.kernels.keys())}"
            raise KeyError(msg)
        self.kernels.pop(name)
        self._write_environments_txt()
        self.restore()

    def _write_environments_txt(self):
        with open(f"{KERNEL_STORE_DIR}/environments.txt", "w") as f:
            f.write("/opt/conda\n")
            for path in self.kernels.values():
                f.write(f"{path}\n")
        
    def __str__(self):
        """Human-readable representation of KernelSet."""
        njust = 10
        ks = f"{'base'.ljust(njust)}/opt/conda\n"
        for name, path in self.kernels.items():
            ks += f"{name.ljust(njust)}{path}\n"
        return ks
