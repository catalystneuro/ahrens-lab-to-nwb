"""Custom interface for handling processed behavior data for Yu Mu 2019 Cell paper."""
import h5py
import numpy as np
from pynwb import NWBFile, TimeSeries, H5DataIO
from neuroconv.basedatainterface import BaseDataInterface
from neuroconv.tools.nwb_helpers import get_module
from neuroconv.utils import FolderPathType


class YuMu2019ActivityStatesInterface(BaseDataInterface):
    """Custom interface for handling processed behavior data for Yu Mu 2019 Cell paper."""

    def __init__(self, folder_path: FolderPathType, verbose: bool = True):
        self.source_data = dict(folder_path=folder_path, verbose=verbose)
        self.verbose = verbose

    def run_conversion(self, nwbfile: NWBFile):
        behavior_module = get_module(nwbfile=nwbfile, name="behavior", description="TODO")

        with h5py.File(name=self.source_data["file_path"]) as source_file:
            pass

            # collect data from all channel analyses and active/passive/transient classifications
            # add as state intervals
