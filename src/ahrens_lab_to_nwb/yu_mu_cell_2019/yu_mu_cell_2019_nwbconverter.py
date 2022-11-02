"""Primary NWBConverter class for this dataset."""
from neuroconv import NWBConverter

from . import (
    AhrensHdf5ImagingInterface,
    YuMu2019SingleColorSegmentationInterface,
    YuMu2019DualColorSegmentationInterface,
    YuMu2019RawBehaviorInterface,
    YuMu2019ProcessedBehaviorInterface,
    YuMu2019TrialsInterface,
    YuMu2019SwimIntervalsInterface,
    YuMu2019ActivityStatesInterface,
)


class YuMuCell2019SingleColorNWBConverter(NWBConverter):
    """Primary conversion class for this dataset."""

    data_interface_classes = dict(
        Imaging=AhrensHdf5ImagingInterface,
        SingleColorSegmentation=YuMu2019SingleColorSegmentationInterface,
        RawBehavior=YuMu2019RawBehaviorInterface,
        ProcessedBehavior=YuMu2019ProcessedBehaviorInterface,
        Trials=YuMu2019TrialsInterface,
        SwimIntervals=YuMu2019SwimIntervalsInterface,
        ActivityStates=YuMu2019ActivityStatesInterface,
    )


class YuMuCell2019DualColorNWBConverter(NWBConverter):
    """Primary conversion class for this dataset."""

    data_interface_classes = dict(
        NeuronImaging=AhrensHdf5ImagingInterface,
        GliaImaging=AhrensHdf5ImagingInterface,
        DualColorSegmentation=YuMu2019DualColorSegmentationInterface,
        RawBehavior=YuMu2019RawBehaviorInterface,
        ProcessedBehavior=YuMu2019ProcessedBehaviorInterface,
        Trials=YuMu2019TrialsInterface,
        SwimIntervals=YuMu2019SwimIntervalsInterface,
        ActivityStates=YuMu2019ActivityStatesInterface,
    )
