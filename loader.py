"""Load and inspect MATLAB .mat files (classic + v7.3 HDF5)."""

from pathlib import Path
from typing import Any

import h5py
import numpy as np
from scipy.io import loadmat, whosmat


class MatFile:
    """Unified interface for classic and v7.3 .mat files."""

    def __init__(self, path: str | Path):
        self.path = Path(path)
        if not self.path.exists():
            raise FileNotFoundError(f"File not found: {self.path}")
        self._is_v73 = self._detect_v73()
        self._data = None
        self._h5 = None

    def _detect_v73(self) -> bool:
        """Detect if the file is MATLAB v7.3 (HDF5 based)."""
        try:
            with open(self.path, "rb") as f:
                header = f.read(128)
            return b"MATLAB 7.3" in header
        except Exception:
            return False

    @property
    def is_v73(self) -> bool:
        return self._is_v73

    def list_variables(self) -> list[dict[str, Any]]:
        """Return list of all variables with shape and type."""
        if self._is_v73:
            return self._list_v73()
        return self._list_classic()

    def _list_classic(self) -> list[dict[str, Any]]:
        info = whosmat(self.path)
        result = []
        for name, shape, dtype in info:
            result.append({
                "name": name,
                "shape": shape,
                "dtype": dtype,
                "size": int(np.prod(shape)) if shape else 0,
            })
        return result

    def _list_v73(self) -> list[dict[str, Any]]:
        h5 = h5py.File(self.path, "r")
        result = []

        def visitor(name, obj):
            if isinstance(obj, h5py.Dataset):
                result.append({
                    "name": name,
                    "shape": obj.shape,
                    "dtype": str(obj.dtype),
                    "size": int(np.prod(obj.shape)) if obj.shape else 0,
                })

        h5.visititems(visitor)
        h5.close()
        return result

    def get(self, name: str) -> Any:
        """Get one variable by name."""
        if self._is_v73:
            with h5py.File(self.path, "r") as h5:
                data = h5[name][()]
                return np.array(data)
        else:
            data = loadmat(self.path, squeeze_me=True, simplify_cells=True)
            if name not in data:
                raise KeyError(f"Variable '{name}' not found")
            return data[name]

    def info(self) -> dict[str, Any]:
        """Return basic information about the file."""
        size = self.path.stat().st_size
        variables = self.list_variables()
        return {
            "path": str(self.path),
            "size_bytes": size,
            "format": "MATLAB v7.3 (HDF5)" if self._is_v73 else "MATLAB classic",
            "n_variables": len(variables),
            "variables": variables,
        }