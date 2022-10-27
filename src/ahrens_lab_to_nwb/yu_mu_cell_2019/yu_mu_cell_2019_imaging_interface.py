"""Modification of the roiextractors.Hdf5ImagingExtractor to read the custom miroscope data from the Ahrens lab."""
from pathlib import Path
from typing import Optional

import numpy as np
from natsort import natsorted
from roiextractors import MultiImagingExtractor
from neuroconv.datainterfaces.ophys.baseimagingextractorinterface import BaseImagingExtractorInterface
from neuroconv.utils import FolderPathType


from .yu_mu_cell_2019_imaging_extractor import AhrensHdf5ImagingExtractor


class AhrensHdf5ImagingInterface(BaseImagingExtractorInterface):
    """Data Interface for AhrensHdf5ImagingExtractor."""

    Extractor = AhrensHdf5ImagingExtractor

    def __init__(
        self,
        folder_path: FolderPathType,
        sampling_frequency: float,
        region: Optional[str] = None,  # Literal["top", "bottom"]], but source_schema can't handle it yet
        shape: Optional[list] = None,  # If specified, don't grab from file
        dtype: Optional[str] = None,  # If specified, don't grab from file
        verbose: bool = True,
    ):
        self.source_data = dict(folder_path=folder_path, sampling_frequency=sampling_frequency, verbose=verbose)
        self.verbose = verbose
        dtype = np.dtype(dtype) if dtype is not None else dtype

        frame_files = natsorted([file for file in Path(folder_path).iterdir() if ".h5" in file.suffixes])
        imaging_extractors = [
            AhrensHdf5ImagingExtractor(
                file_path=file_path, sampling_frequency=sampling_frequency, region=region, shape=shape, dtype=dtype
            )
            for file_path in frame_files
        ]
        self.imaging_extractor = MultiImagingExtractor(imaging_extractors=imaging_extractors)
