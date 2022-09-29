"""Custom interface for handling processed behavior data for Yu Mu 2019 Cell paper."""
from typing import Optional

import h5py
import numpy as np
from pynwb import NWBFile, TimeSeries, H5DataIO
from neuroconv.basedatainterface import BaseDataInterface
from neuroconv.tools.nwb_helpers import get_module
from neuroconv.utils import FolderPathType


class YuMu2019ProcessedBehaviorInterface(BaseDataInterface):
    """Custom interface for handling processed behavior data for Yu Mu 2019 Cell paper."""

    def __init__(self, file_path: FolderPathType, sampling_frequency: float, verbose: bool = True):
        self.source_data = dict(file_path=file_path, sampling_frequency=sampling_frequency, verbose=verbose)
        self.verbose = verbose

    def run_conversion(self, nwbfile: NWBFile, metadata: Optional[dict] = None):
        behavior_module = get_module(nwbfile=nwbfile, name="behavior", description="TODO")

        with h5py.File(name=self.source_data["file_path"]) as source_file:
            combined_data = np.empty(shape=(source_file["data"]["fltCh1"].shape[1], 2))
            for idx, matlab_key in enumerate(["fltCh1", "fltCh2"]):
                combined_data[:, idx] = source_file["data"][matlab_key]
            behavior_module.add(
                TimeSeries(
                    name="FilteredSwimSignals",
                    description="A filtered version of the raw SwimSignals in acquisition.",
                    data=H5DataIO(combined_data, compression="gzip"),
                    rate=self.source_data["sampling_frequency"],
                    unit="a.u",
                )
            )
