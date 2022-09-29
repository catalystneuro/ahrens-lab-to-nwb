"""Custom interface for handling processed behavior data for Yu Mu 2019 Cell paper."""
from typing import Optional

import h5py
from pynwb import NWBFile, H5DataIO
from pynwb.epoch import TimeIntervals
from neuroconv.basedatainterface import BaseDataInterface
from neuroconv.tools.nwb_helpers import get_module
from neuroconv.utils import FilePathType
from ndx_events import AnnotatedEventsTable


class YuMu2019SwimIntervalsInterface(BaseDataInterface):
    """Custom interface for handling processed behavior data for Yu Mu 2019 Cell paper."""

    def __init__(self, file_path: FilePathType, sampling_frequency: float, verbose: bool = True):
        self.source_data = dict(file_path=file_path, sampling_frequency=sampling_frequency, verbose=verbose)
        self.verbose = verbose

    def run_conversion(self, nwbfile: NWBFile, metadata: Optional[dict] = None):
        behavior_module = get_module(nwbfile=nwbfile, name="behavior", description="TODO")

        with h5py.File(name=self.source_data["file_path"]) as source_file:

            # Swimming intervals
            swim_starts = source_file["data"]["swimStartIndT"][0, :] / self.source_data["sampling_frequency"]
            swim_stops = source_file["data"]["swimEndIndT"][0, :] / self.source_data["sampling_frequency"]

            time_intervals = TimeIntervals(
                name="SwimIntervals", description="Intervals of time when subject is estimated to be swimming."
            )
            for start_time, stop_time in zip(swim_starts, swim_stops):
                time_intervals.add_interval(start_time=start_time, stop_time=stop_time)

            # TODO: units for these two
            time_intervals.add_column(
                name="power",
                description="Estimated power of the swim event.",
                data=H5DataIO(source_file["data"]["swimPower__"][0, :], compression="gzip"),
            )
            time_intervals.add_column(
                name="width",
                description="Estimated width spanned by the swim event.",
                data=H5DataIO(source_file["data"]["swimWidth"][0, :], compression="gzip"),
            )

            behavior_module.add(time_intervals)

            # Burst events
            bursts = source_file["data"]["burstBothIndT"][0, :] / self.source_data["sampling_frequency"]
            annotated_events = AnnotatedEventsTable(
                name="BurstEvents", description="Events of classified bursting activity."
            )
            annotated_events.add_event_type(label="bursts", event_description="Burst events.", event_times=bursts)
            behavior_module.add(annotated_events)
