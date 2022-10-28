"""Basically a ScanImageTiffExtractor but done in the more efficient initialization form for the Ahrens lab."""
from pathlib import Path
from typing import Optional, Tuple, Literal

import numpy as np
from roiextractors.imagingextractor import ImagingExtractor
from roiextractors.extraction_tools import PathType, ArrayType
from ScanImageTiffReader import ScanImageTiffReader


class AhrensDownsampledImagingExtractor(ImagingExtractor):
    """Custom extractor for reading a single frame file from the Ahrens lab downsampled ('projections') imaging data."""

    extractor_name = "AhrensDownsampledImaging"
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
            with ScanImageTiffReader(str(self.file_path)) as io:
                shape = io.shape()
                self._num_stacks, self._num_rows, self._num_cols = shape
                self._dtype = self._get_single_frame(idx=0).dtype
        else:
            self._num_stacks, self._num_rows, self._num_cols = shape
            self._dtype = dtype
        self._frame_axis_order = [1, 2, 0]

    def _get_single_frame(self, idx: int) -> np.ndarray:
        """
        Data accessed through an open ScanImageTiffReader io gets scrambled if there are multiple calls.

        Thus, open fresh io in context each time something is needed.
        """
        with ScanImageTiffReader(str(self.file_path)) as io:
            return io.data(beg=idx, end=idx + 1)

    def get_frames(self, frame_idxs: ArrayType, channel: int = 0) -> np.ndarray:
        squeeze_data = False
        if isinstance(frame_idxs, int):
            squeeze_data = True
            frame_idxs = [frame_idxs]

        if not all(np.diff(frame_idxs) == 1):
            return np.concatenate([self._get_single_frame(idx=idx) for idx in frame_idxs])
        else:
            with ScanImageTiffReader(filename=str(self.file_path)) as io:
                frames = io.data(beg=frame_idxs[0], end=frame_idxs[-1] + 1)
                if squeeze_data:
                    frames = frames.squeeze()
            return frames

    def get_video(self, start_frame=None, end_frame=None, channel: Optional[int] = 0) -> np.ndarray:
        print(str(self.file_path))
        with ScanImageTiffReader(filename=str(self.file_path)) as io:
            return io.data(beg=start_frame, end=end_frame)

    def get_image_size(self) -> Tuple[int, int, int]:
        if self.region is None:
            image_size = (self._num_rows, self._num_cols, self._num_stacks)
        elif self.region == "top":
            image_size = (int(self._num_rows / 2), self._num_cols, self._num_stacks)
        elif self.region == "bottom":
            image_size = (int(self._num_rows / 2), self._num_cols, self._num_stacks)
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
