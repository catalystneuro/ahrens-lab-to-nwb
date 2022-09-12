"""Custom interface for handling raw behavior data for Yu Mu 2019 Cell paper."""
from typing import Optional

import h5py
import numpy as np
from pynwb import NWBFile, TimeSeries, H5DataIO
from neuroconv.basedatainterface import BaseDataInterface
from neuroconv.utils import FilePathType, load_dict_from_file


class YuMu2019RawBehaviorInterface(BaseDataInterface):
    """Custom interface for handling raw behavior data for Yu Mu 2019 Cell paper."""

    def __init__(
        self,
        data_file_path: FilePathType,
        metadata_file_path: Optional[FilePathType],
        sampling_frequency: float,
        verbose: bool = True,
    ):
        self.source_data = dict(
            data_file_path=data_file_path,
            metadata_file_path=metadata_file_path,
            sampling_frequency=sampling_frequency,
            verbose=verbose,
        )
        self.verbose = verbose

    def run_conversion(self, nwbfile: NWBFile):
        signals_names_and_descriptions = load_dict_from_file(file_path=self.source_data["metadata_file_path"])
        timing_info = dict(
            starting_time=0.0,  # All time references in NWBFile relative to behavior
            rate=self.source_data["sampling_frequency"],
            unit="a.u.",  # These could technically have some scale of 'voltage' unit but exact is unknown
        )

        with h5py.File(name=self.source_data["file_path"]) as source_file:
            all_series_lengths = source_file["rawdata"]["ch1"].shape[1]

            for series in signals_names_and_descriptions:
                if isinstance(series["matlab_key"], list):
                    series_data = np.empty(shape=(len(series["matlab_key"]), all_series_lengths))
                    for idx, key in enumerate(series["matlab_key"]):
                        series_data[idx, :] = source_file["rawdata"][key][:]
                else:
                    series_data = source_file["rawdata"][series["matlab_key"]][:]
                nwbfile.add_acquisition(
                    TimeSeries(
                        name=series["series_name"],
                        description=series["series_description"],
                        data=H5DataIO(series_data, compression="gzip"),
                        **timing_info,
                    )
                )
