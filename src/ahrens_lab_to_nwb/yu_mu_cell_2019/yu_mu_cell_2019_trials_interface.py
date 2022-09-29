"""Custom interface for processed trials data for Yu Mu 2019 Cell paper."""
from typing import Optional
from collections import defaultdict

from pynwb import NWBFile
from scipy.io import loadmat
from neuroconv.basedatainterface import BaseDataInterface
from neuroconv.utils import FilePathType


class YuMu2019TrialsInterface(BaseDataInterface):
    """Custom interface for processed trials data for Yu Mu 2019 Cell paper."""

    def __init__(self, file_path: FilePathType, sampling_frequency: float, verbose: bool = True):
        self.source_data = dict(file_path=file_path, sampling_frequency=sampling_frequency, verbose=verbose)
        self.verbose = verbose

    def run_conversion(self, nwbfile: NWBFile, metadata: Optional[dict] = None):
        trials_struct = loadmat(file_name=self.source_data["file_path"])["trial_info"]

        # Records time as the frame index for the behavior sync channel
        starts = trials_struct[:, 0] / self.source_data["sampling_frequency"]
        stops = trials_struct[:, 1] / self.source_data["sampling_frequency"]

        # Records type as simple integer; no reference to meaning
        # TODO: need to confirm this assignment
        trial_type_id_to_str = defaultdict(lambda: "other")
        trial_type_id_to_str[1] = "closed-loop"
        trial_type_id_to_str[3] = "open-loop"

        nwbfile.add_trial_column(name="trial_type", description="Closed-loop, open-loop, or other.")
        for start_time, stop_time, trial_type_id in zip(starts, stops, trials_struct[:, -1]):
            nwbfile.add_trial(
                start_time=start_time, stop_time=stop_time, trial_type=trial_type_id_to_str[trial_type_id]
            )
