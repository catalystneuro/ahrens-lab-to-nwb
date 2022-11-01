"""Modification of the roiextractors.Hdf5ImagingExtractor to read the custom miroscope data from the Ahrens lab."""
from pathlib import Path
from typing import List, Optional

import h5py
import numpy as np
from numpy.typing import ArrayLike
from roiextractors.segmentationextractor import SegmentationExtractor
from neuroconv.utils import FilePathType


class YuMu2019SegmentationExtractor(SegmentationExtractor):
    """Custom extractor for reading segmentation data for the Yu Mu 2019 Cell paper."""

    extractor_name = "YuMu2019SegmentationExtractor"
    mode = "file"

    def __init__(self, file_path: FilePathType, sampling_frequency: float):
        super().__init__()
        self._kwargs = dict(file_path=str(Path(file_path).absolute()), sampling_frequency=sampling_frequency)
        self._sampling_frequency = sampling_frequency
        self.file_path = file_path
        self._file = h5py.File(name=file_path)

        # Automatic detection of differing formats
        if "baseline" in self._file:  # Dual-color sessions
            self._baseline_group_name = "baseline"
            self._timeseries_group_name = "timeseries"
            self._pixel_mask_name_map = dict(x="x", y="y", z="z")

            self._image_shape = (2048, 2048, 29)
        else:  # Single-color sessions
            self._baseline_group_name = "Cell_baseline"
            self._timeseries_group_name = "Cell_timesers"
            self._pixel_mask_name_map = dict(x="Cell_X", y="Cell_Y", z="Cell_Z")

            self._image_shape = (888, 2048, 29)

        baseline_shape = self._file[self._baseline_group_name].shape
        assert baseline_shape != (1, 6,), (  # The MATLAB half-precision coding stores the dataset as a (1,6) object
            "The flourescence series in this file are saved in half precision - file cannot be read in Python! "
            "Please recast the MATLAB datatype and save a new file."
        )

        self._roi_response_raw = self._file[self._baseline_group_name]
        self._roi_response_dff = self._file[self._timeseries_group_name]

    def __del__(self):
        self._file.close()

    def close(self):
        self._file.close()

    def get_image_size(self):
        return self._image_shape

    def get_roi_locations(self, roi_ids: Optional[ArrayLike] = None) -> np.ndarray:
        roi_ids = roi_ids or range(self.get_num_rois())

        roi_locations = np.empty(shape=(3, len(roi_ids)))
        pixel_masks = self.get_roi_pixel_masks(roi_ids=roi_ids)
        for idx, _ in enumerate(roi_ids):
            roi_locations[:, idx] = np.array(
                [
                    np.median(pixel_masks[idx][:, 0]),
                    np.median(pixel_masks[idx][:, 1]),
                    np.median(pixel_masks[idx][:, 2]),
                ]
            )
        return roi_locations

    def get_roi_pixel_masks(self, roi_ids: Optional[ArrayLike] = None) -> List[np.ndarray]:
        pixel_masks = list()
        roi_ids = roi_ids or range(self.get_num_rois())
        dtype = self._file[self._pixel_mask_name_map["x"]].dtype

        # Example data had 122,296 ROI's over 3 dimensions of maximum 164 pixels, stored as uint16...
        # ...approximately 120MB total, so fine to load all into memory.
        # Actual sparse usage will be much smaller than that, too.
        for roi in roi_ids:
            roi_selection = self._file[self._pixel_mask_name_map["x"]][:, roi]
            nonzero_idxs = np.where(np.logical_and(roi_selection != 0, ~np.isnan(roi_selection)))
            num_pixels = len(nonzero_idxs[0]) if np.any(nonzero_idxs) else 0
            pixel_mask = np.empty(shape=(num_pixels, 4), dtype=dtype)
            pixel_mask[:, 0] = self._file[self._pixel_mask_name_map["x"]][:num_pixels, roi]
            pixel_mask[:, 1] = self._file[self._pixel_mask_name_map["y"]][:num_pixels, roi]
            pixel_mask[:, 2] = self._file[self._pixel_mask_name_map["z"]][:num_pixels, roi]
            pixel_mask[:, 3] = 1
            pixel_masks.append(pixel_mask)
        return pixel_masks

    def get_accepted_list(self) -> list:
        return self.get_roi_ids()

    def get_rejected_list(self) -> list:
        return list()
