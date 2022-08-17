"""Modification of the roiextractors.Hdf5ImagingExtractor to read the custom miroscope data from the Ahrens lab."""
from pathlib import Path
from typing import Optional, Tuple

import numpy as np
from roiextractors.imagingextractor import ImagingExtractor
from roiextractors.extraction_tools import PathType
from lazy_ops import DatasetView


try:
    import h5py

    HAVE_H5PY = True
except ImportError:
    HAVE_H5PY = False


class AhrensHdf5ImagingExtractor(ImagingExtractor):
    """Custom extractor for reading a single frame file from the Ahrens lab volumentric imaging data."""

    extractor_name = "AhrensHdf5Imaging"
    installed = HAVE_H5PY
    mode = "file"
    installation_mesg = "To use the Hdf5 Extractor run:\n\n pip install h5py\n\n"

    def __init__(self, file_path: PathType, sampling_frequency: float):
        ImagingExtractor.__init__(self)
        self._kwargs = dict(file_path=str(Path(file_path).absolute()), sampling_frequency=sampling_frequency)
        self._sampling_frequency = sampling_frequency
        self.file_path = file_path

        with h5py.File(name=file_path) as file:
            self._num_stacks, self._num_rows, self._num_cols = file["default"].shape
            self._dtype = file["default"].dtype
        self._frame_axis_order = [1, 2, 0]

    def get_video(self, start_frame: Optional[int] = None, end_frame: Optional[int] = None) -> np.ndarray:  # noqa: D102
        with h5py.File(name=self.file_path) as file:
            video = DatasetView(file["default"]).lazy_transpose(self._frame_axis_order)
            return video.lazy_slice[:, :, :].dsetread()[np.newaxis, :]

    def get_image_size(self) -> Tuple[int, int, int]:  # noqa: D102
        return (self._num_rows, self._num_cols, self._num_stacks)

    def get_num_frames(self):  # noqa: D102
        return 1

    def get_sampling_frequency(self):  # noqa: D102
        return self._sampling_frequency

    def get_dtype(self):  # noqa: D102
        return self._dtype

    def get_num_channels(self):  # noqa: D102
        return 1

    def get_channel_names(self):  # noqa: D102
        pass
