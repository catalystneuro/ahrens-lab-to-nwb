"""Primary NWBConverter class for this dataset."""
from neuroconv import NWBConverter

from . import (
    AhrensHdf5ImagingInterface,
    YuMu2019RawBehaviorInterface,
    YuMu2019ProcessedBehaviorInterface,
    YuMu2019TrialsInterface,
    YuMu2019SwimIntervalsInterface,
    YuMu2019ActivityStatesInterface,
)


class YuMuCell2019NWBConverter(NWBConverter):
    """Primary conversion class for this dataset."""

    data_interface_classes = dict(
        Imaging=AhrensHdf5ImagingInterface,
        RawBehavior=YuMu2019RawBehaviorInterface,
        ProcessedBehavior=YuMu2019ProcessedBehaviorInterface,
        Trials=YuMu2019TrialsInterface,
        SwimIntervals=YuMu2019SwimIntervalsInterface,
        ActivityStates=YuMu2019ActivityStatesInterface,
    )
