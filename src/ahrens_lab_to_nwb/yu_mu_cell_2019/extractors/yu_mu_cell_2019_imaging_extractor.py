"""Modification of the roiextractors.Hdf5ImagingExtractor to read the custom miroscope data from the Ahrens lab."""
from pathlib import Path
from typing import Optional, Tuple, Literal

import h5py
import numpy as np
from roiextractors.imagingextractor import ImagingExtractor
from roiextractors.extraction_tools import PathType
from lazy_ops import DatasetView


class AhrensHdf5ImagingExtractor(ImagingExtractor):
    """Custom extractor for reading a single frame file from the Ahrens lab volumentric imaging data."""

    extractor_name = "AhrensHdf5Imaging"
    mode = "file"

    def __init__(
        self,
        file_path: PathType,
        sampling_frequency: float,
        region: Optional[Literal["top", "bottom"]] = None,
        shape: Optional[Tuple[int]] = None,  # If specified, don't grab from file
        dtype: Optional[np.dtype] = None,  # If specified, don't grab from file
    ):
        ImagingExtractor.__init__(self)
        self._kwargs = dict(file_path=str(Path(file_path).absolute()), sampling_frequency=sampling_frequency)
        self._sampling_frequency = sampling_frequency
        self.file_path = file_path
        self.region = region

        if shape is None or dtype is None:
            with h5py.File(name=file_path) as file:
                self._num_stacks, self._num_rows, self._num_cols = file["default"].shape
                self._dtype = file["default"].dtype
        else:
            self._num_stacks, self._num_rows, self._num_cols = shape
            self._dtype = dtype
        self._frame_axis_order = [2, 1, 0]

    def get_video(self, start_frame: Optional[int] = None, end_frame: Optional[int] = None) -> np.ndarray:
        with h5py.File(name=self.file_path) as file:
            video = DatasetView(file["default"]).lazy_transpose(self._frame_axis_order)

            if self.region is None:
                region_slice = slice(None)
            elif self.region == "top":
                region_slice = slice(int(self._num_rows / 2), None)
            elif self.region == "bottom":
                region_slice = slice(None, int(self._num_rows / 2))

            return video.lazy_slice[:, region_slice, :].dsetread()[np.newaxis, :]

    def get_image_size(self) -> Tuple[int, int, int]:
        if self.region is None:
            image_size = (self._num_rows, self._num_cols, self._num_stacks)
        elif self.region in ["top", "bottom"]:
            image_size = (self._num_rows, int(self._num_cols / 2), self._num_stacks)
        return image_size

    def get_num_frames(self):
        return 1

    def get_sampling_frequency(self):
        return self._sampling_frequency

    def get_dtype(self):
        return self._dtype

    def get_num_channels(self):
        return 1

    def get_channel_names(self):
        pass
