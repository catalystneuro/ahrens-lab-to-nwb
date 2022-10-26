"""Primary script to run to convert an entire session of data using the NWBConverter."""
from pathlib import Path
from datetime import datetime
from dateutil import tz

import numpy as np
import h5py

from neuroconv.utils import load_dict_from_file, dict_deep_update

from ahrens_lab_to_nwb.yu_mu_cell_2019.yu_mu_cell_2019_nwbconverter import YuMuCell2019NWBConverter


# Manually specify everything here as it changes
# ----------------------------------------------
stub_test = True  # True for a fast prototype file, False for converting the entire session
stub_frames = 4  # Length of stub file, if stub_test=True

timezone = "US/Eastern"
session_name = "20170228_4_1_gfaprgeco_hucgc_6dpf_shorttrials_20170228_185002"

session_name_split = session_name.split("_")
subject_number = session_name_split[1]
session_start_date = session_name_split[-2]

global_metadata_path = Path(__file__).parent / "yu_mu_cell_2019_metadata.yml"

imaging_folder_path = Path(f"E:/Ahrens/Imaging/{session_start_date}/fish{subject_number}/{session_name}/raw")

# These are the manually re-saved files to correct the half-precision issue
neuron_segmentation_file_path = Path(f"E:/Ahrens/Segmentation/{session_name}/cells1_adjusted.mat")
glia_segmentation_file_path = Path(f"E:/Ahrens/Segmentation/{session_name}/cells0_adjusted.mat")

ephys_folder_path = Path(f"E:/Ahrens/Imaging/{session_start_date}/fish{subject_number}/{session_name}/ephys")
raw_behavior_file_path = ephys_folder_path / "rawdata.mat"
raw_behavior_series_description_file_path = Path(__file__).parent / "yu_mu_cell_2019_behavior_descriptions.yml"
processed_behavior_file_path = ephys_folder_path / "data.mat"
trial_table_file_path = ephys_folder_path / "trial_info.mat"
states_folder_path = ephys_folder_path

nwbfile_path = Path("E:/Ahrens/NWB/testing_imaging+neuron+glia.nwb")
# ----------------------------------------------
# Below here is automated


example_session_id = imaging_folder_path.parent.stem
session_start_time_string = "".join(example_session_id.split("_")[-2:])
session_start_time = datetime.strptime(session_start_time_string, "%Y%m%d%H%M%S")
session_start_time = session_start_time.replace(tzinfo=tz.gettz(timezone))

# The rate is estimated from the mean number of frames between TTL onset (ch3) for frame
# captures divided by average reported volume sampling speed
imaging_rate = 1.56
behavior_rate = 2431.6
source_data = dict(
    NeuronImaging=dict(folder_path=str(imaging_folder_path), sampling_frequency=imaging_rate, region="top"),
    GliaImaging=dict(folder_path=str(imaging_folder_path), sampling_frequency=imaging_rate, region="bottom"),
    NeuronSegmentation=dict(file_path=str(neuron_segmentation_file_path), sampling_frequency=imaging_rate),
    # GliaSegmentation=dict(file_path=str(glia_segmentation_file_path), sampling_frequency=imaging_rate),
    # RawBehavior=dict(
    #     data_file_path=str(raw_behavior_file_path),
    #     metadata_file_path=str(raw_behavior_series_description_file_path),
    #     sampling_frequency=behavior_rate,
    # ),
    # ProcessedBehavior=dict(file_path=str(processed_behavior_file_path), sampling_frequency=behavior_rate),
    # Trials=dict(file_path=str(trial_table_file_path), sampling_frequency=behavior_rate),
    # SwimIntervals=dict(file_path=str(processed_behavior_file_path), sampling_frequency=behavior_rate),
    # ActivityStates=dict(folder_path=str(states_folder_path), sampling_frequency=behavior_rate),
)
conversion_options = dict(
    Imaging=dict(stub_test=stub_test, stub_frames=stub_frames),
    GliaSegmentation=dict(include_roi_centroids=False, mask_type="voxel", stub_test=stub_test, stub_frames=stub_frames),
    NeuronSegmentation=dict(
        include_roi_centroids=False, mask_type="voxel", stub_test=stub_test, stub_frames=stub_frames
    ),
)

converter = YuMuCell2019NWBConverter(source_data=source_data)

# Add synchronized timestamps to all imaging and segmentation objects
with h5py.File(name=processed_behavior_file_path) as file:
    frame_tracker = file["data"]["frame"][:]
timestamps = np.where(np.diff(frame_tracker))[1][:-1] / behavior_rate

# only for corrupted session
imaging_len = converter.data_interface_objects["Imaging"].imaging_extractor.get_num_frames()

# If statements here are mostly for testing purposes, the entire conversion would include all
if "Imaging" in converter.data_interface_objects:
    converter.data_interface_objects["Imaging"].imaging_extractor.set_times(times=timestamps[:imaging_len])
if "NeuronSegmentation" in converter.data_interface_objects:
    converter.data_interface_objects["NeuronSegmentation"].segmentation_extractor.set_times(times=timestamps)
if "GliaSegmentation" in converter.data_interface_objects:
    converter.data_interface_objects["GliaSegmentation"].segmentation_extractor.set_times(times=timestamps)

metadata = converter.get_metadata()
metadata["NWBFile"].update(session_start_time=session_start_time)
metadata_from_yaml = load_dict_from_file(file_path=global_metadata_path)
metadata = dict_deep_update(metadata, metadata_from_yaml)

converter.run_conversion(
    metadata=metadata, nwbfile_path=nwbfile_path, conversion_options=conversion_options, overwrite=True
)
