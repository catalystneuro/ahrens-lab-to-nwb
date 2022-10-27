"""Custom interface for handling processed behavior data for Yu Mu 2019 Cell paper."""
from typing import Optional
from pathlib import Path

import pandas as pd
from scipy.io import loadmat
from pynwb import NWBFile
from pynwb.epoch import TimeIntervals
from neuroconv.basedatainterface import BaseDataInterface
from neuroconv.tools.nwb_helpers import get_module
from neuroconv.utils import FolderPathType


class YuMu2019ActivityStatesInterface(BaseDataInterface):
    """Custom interface for handling processed behavior data for Yu Mu 2019 Cell paper."""

    def __init__(self, folder_path: FolderPathType, sampling_frequency: float, verbose: bool = True):
        self.source_data = dict(folder_path=folder_path, sampling_frequency=sampling_frequency, verbose=verbose)
        self.verbose = verbose

    def run_conversion(self, nwbfile: NWBFile, metadata: Optional[dict] = None):
        behavior_module = get_module(nwbfile=nwbfile, name="behavior", description="TODO")

        table_dict = dict(start_time=list(), stop_time=list(), state_type=list())
        for channel_name in ["ch1", "ch2"]:
            for state_name in ["active", "passive", "transient"]:
                group_name = f"{state_name}State"
                file_path = Path(self.source_data["folder_path"]) / f"{channel_name}{group_name}.mat"

                if file_path.exists():
                    source_file = loadmat(file_name=str(file_path))
                    table_dict["start_time"].extend(
                        source_file[group_name]["start"][0][0][0] / self.source_data["sampling_frequency"]
                    )
                    table_dict["stop_time"].extend(
                        source_file[group_name]["end"][0][0][0] / self.source_data["sampling_frequency"]
                    )
                    table_dict["state_type"].extend([state_name] * len(source_file[group_name]["start"][0][0][0]))

        table_dataframe = pd.DataFrame(data=table_dict)
        table_dataframe.sort_values(by=["start_time"])

        time_intervals = TimeIntervals(
            name="ActivityStates", description="Classified periods of activity (passive, active, or transient)."
        )
        time_intervals.add_column(name="state_type", description="The type of classified state.")
        for start_time, stop_time, state_type in table_dataframe.itertuples(index=False):
            time_intervals.add_interval(start_time=start_time, stop_time=stop_time, state_type=state_type)
        behavior_module.add(time_intervals)
