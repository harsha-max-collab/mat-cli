"""Load and inspect MATLAB .mat files (classic + v7.3)."""

from pathlib import Path
from typing import Any
import h5py
import numpy as np
from scipy.io import loadmat, whosmat


class MatFile:
    def __init__(self, path: str | Path):
        self.path = Path(path)
        if not self.path.exists():
            raise FileNotFoundError(f"File not found: {self.path}")
        if not self.path.suffix.lower() in (".mat", ".MAT"):
            raise ValueError(f"File does not look like a .mat file: {self.path}")

        self._is_v73 = self._detect_v73()
        self._h5 = None

    def _detect_v73(self) -> bool:
        try:
            with open(self.path, "rb") as f:
                header = f.read(128)
            return b"MATLAB 7.3" in header or header.startswith(b"\x89HDF")
        except Exception:
            return False

    @property
    def is_v73(self) -> bool:
        return self._is_v73

    def list_variables(self) -> list[dict[str, Any]]:
        if self._is_v73:
            return self._list_v73()
        return self._list_classic()

    def _list_classic(self) -> list[dict[str, Any]]:
        try:
            info = whosmat(self.path)
        except Exception as e:
            raise RuntimeError(f"Could not read classic .mat file: {e}")

        result = []
        for name, shape, dtype in info:
            result.append({
                "name": name,
                "shape": shape,
                "dtype": str(dtype),
                "size": int(np.prod(shape)) if shape else 0,
            })
        return result

    def _list_v73(self) -> list[dict[str, Any]]:
        result = []
        try:
            with h5py.File(self.path, "r") as h5:
                def visitor(name, obj):
                    if isinstance(obj, h5py.Dataset):
                        result.append({
                            "name": name,
                            "shape": obj.shape,
                            "dtype": str(obj.dtype),
                            "size": int(np.prod(obj.shape)) if obj.shape else 0,
                        })
                h5.visititems(visitor)
        except Exception as e:
            raise RuntimeError(f"Could not read v7.3 .mat file: {e}")
        return result

    def get(self, name: str) -> Any:
        if self._is_v73:
            try:
                with h5py.File(self.path, "r") as h5:
                    if name not in h5:
                        available = list(h5.keys())
                        raise KeyError(
                            f"Variable '{name}' not found.\n"
                            f"Available variables: {available}"
                        )
                    data = h5[name][()]
                    return np.array(data)
            except KeyError:
                raise
            except Exception as e:
                raise RuntimeError(f"Error reading variable '{name}': {e}")
        else:
            try:
                data = loadmat(self.path, squeeze_me=True, simplify_cells=True)
            except Exception as e:
                raise RuntimeError(f"Could not load .mat file: {e}")

            # Remove MATLAB metadata keys
            clean = {k: v for k, v in data.items() if not k.startswith("__")}
            if name not in clean:
                available = list(clean.keys())
                raise KeyError(
                    f"Variable '{name}' not found.\n"
                    f"Available variables: {available}"
                )
            return clean[name]

    def info(self) -> dict[str, Any]:
        size = self.path.stat().st_size
        variables = self.list_variables()
        return {
            "path": str(self.path),
            "size_bytes": size,
            "format": "MATLAB v7.3 (HDF5)" if self._is_v73 else "MATLAB classic",
            "n_variables": len(variables),
            "variables": variables,
        }