"""Primary script to run to convert an entire session of data using the NWBConverter."""
from pathlib import Path
from datetime import datetime
from dateutil import tz

import numpy as np
import h5py

from neuroconv.utils import load_dict_from_file, dict_deep_update

from ahrens_lab_to_nwb.yu_mu_cell_2019.yu_mu_cell_2019_nwbconverter import YuMuCell2019DualColorNWBConverter


# Manually specify everything here as it changes
# ----------------------------------------------
stub_test = False  # True for a fast prototype file, False for converting the entire session
stub_frames = 4  # Length of stub file, if stub_test=True

timezone = "US/Eastern"
session_name = "20170228_4_1_gfaprgeco_hucgc_6dpf_shorttrials_20170228_185002"
dual_color_session_description = "A dual-color optic channel recording of both neuron and glia populations."

session_name_split = session_name.split("_")
subject_number = session_name_split[1]
session_start_date = session_name_split[-2]

metadata_folder = Path(__file__).parent / "metadata"  # The pre-built one in the repository; can also use a local copy
global_metadata_path = metadata_folder / "yu_mu_cell_2019_global_metadata.yml"
ophys_metadata_path = metadata_folder / "yu_mu_cell_2019_dual_color_neuron_metadata.yml"
raw_behavior_series_description_file_path = metadata_folder / "yu_mu_cell_2019_behavior_descriptions.yml"

imaging_folder_path = Path(f"E:/Ahrens/Imaging/{session_start_date}/fish{subject_number}/{session_name}/raw")

# These are the manually re-saved files to correct the half-precision issue
neuron_segmentation_file_path = Path(f"E:/Ahrens/Segmentation/{session_name}/cells1_adjusted.mat")
glia_segmentation_file_path = Path(f"E:/Ahrens/Segmentation/{session_name}/cells0_adjusted.mat")

ephys_folder_path = Path(f"E:/Ahrens/Imaging/{session_start_date}/fish{subject_number}/{session_name}/ephys")
raw_behavior_file_path = ephys_folder_path / "rawdata.mat"
processed_behavior_file_path = ephys_folder_path / "data.mat"
trial_table_file_path = ephys_folder_path / "trial_info.mat"
states_folder_path = ephys_folder_path

nwbfile_path = Path(f"E:/Ahrens/NWB/{session_name}.nwb")
# ----------------------------------------------
# Below here is automated


example_session_id = imaging_folder_path.parent.stem
session_start_time_string = "".join(example_session_id.split("_")[-2:])
session_start_time = datetime.strptime(session_start_time_string, "%Y%m%d%H%M%S")
session_start_time = session_start_time.replace(tzinfo=tz.gettz(timezone))

subject_id = "_".join([session_start_date, subject_number])
# dpf = days post fertilization
subject_age = "P" + next(string for string in session_name_split if "dpf" in string).replace("dpf", "D")
subject_sex = "U"  # U = unknown

# The rate is estimated from the mean number of frames between TTL onset (ch3) for frame
# captures divided by average reported volume sampling speed
imaging_rate = 1.56
behavior_rate = 5989.6
source_data = dict(
    NeuronImaging=dict(
        folder_path=str(imaging_folder_path),
        sampling_frequency=imaging_rate,
        region="top",
        shape=[29, 2048, 2048],
        dtype="int16",
    ),
    GliaImaging=dict(
        folder_path=str(imaging_folder_path),
        sampling_frequency=imaging_rate,
        region="bottom",
        shape=[29, 2048, 2048],
        dtype="int16",
    ),
    DualColorSegmentation=dict(
        neuron_file_path=str(neuron_segmentation_file_path),
        glia_file_path=str(glia_segmentation_file_path),
        sampling_frequency=imaging_rate,
    ),
    RawBehavior=dict(
        data_file_path=str(raw_behavior_file_path),
        metadata_file_path=str(raw_behavior_series_description_file_path),
        sampling_frequency=behavior_rate,
    ),
    ActivityStates=dict(folder_path=str(states_folder_path), sampling_frequency=behavior_rate),
)
if trial_table_file_path.exists():
    source_data.update(
        Trials=dict(file_path=str(trial_table_file_path), sampling_frequency=behavior_rate),
    )
if processed_behavior_file_path.exists():
    source_data.update(
        ProcessedBehavior=dict(file_path=str(processed_behavior_file_path), sampling_frequency=behavior_rate),
    )
if trial_table_file_path.exists():
    source_data.update(
        Trials=dict(file_path=str(trial_table_file_path), sampling_frequency=behavior_rate),
    )
if processed_behavior_file_path.exists():
    source_data.update(
        SwimIntervals=dict(file_path=str(processed_behavior_file_path), sampling_frequency=behavior_rate),
    )

conversion_options = dict(
    NeuronImaging=dict(
        imaging_plane_index=0,
        two_photon_series_index=0,
        stub_test=stub_test,
        stub_frames=stub_frames,
        iterator_options=dict(
            buffer_gb=0.5,
            chunk_shape=(1, 1024, 2048, 1),
            display_progress=True,
            progress_bar_options=dict(desc="Converting neuron imaging data...", position=0),
        ),
    ),
    GliaImaging=dict(
        imaging_plane_index=1,
        two_photon_series_index=1,
        stub_test=stub_test,
        stub_frames=stub_frames,
        iterator_options=dict(
            buffer_gb=0.5,
            chunk_shape=(1, 1024, 2048, 1),
            display_progress=True,
            progress_bar_options=dict(desc="Converting glia imaging data...", position=1),
        ),
    ),
    DualColorSegmentation=dict(
        stub_test=stub_test,
        stub_frames=stub_frames,
        iterator_options=dict(
            buffer_gb=0.5,
            display_progress=True,
            progress_bar_options=dict(desc="Converting segmentation data...", position=2),
        ),
    ),
)

converter = YuMuCell2019DualColorNWBConverter(source_data=source_data)

# Add synchronized timestamps to all imaging and segmentation objects
with h5py.File(name=processed_behavior_file_path) as file:
    frame_tracker = file["data"]["frame"][:]
timestamps = np.where(np.diff(frame_tracker))[1][:-1] / behavior_rate

# only for corrupted session
imaging_len = converter.data_interface_objects["NeuronImaging"].imaging_extractor.get_num_frames()

# If statements here are mostly for testing purposes, the entire conversion would include all
if "NeuronImaging" in converter.data_interface_objects:
    converter.data_interface_objects["NeuronImaging"].imaging_extractor.set_times(times=timestamps[:imaging_len])
if "GliaImaging" in converter.data_interface_objects:
    converter.data_interface_objects["GliaImaging"].imaging_extractor.set_times(times=timestamps[:imaging_len])
if "DualColorSegmentation" in converter.data_interface_objects:
    converter.data_interface_objects["DualColorSegmentation"].neuron_segmentation_extractor.set_times(times=timestamps)
    converter.data_interface_objects["DualColorSegmentation"].glia_segmentation_extractor.set_times(times=timestamps)

metadata = converter.get_metadata()
metadata["NWBFile"].update(session_start_time=session_start_time, session_description=dual_color_session_description)

# Update global metadata
global_metadata_from_yaml = load_dict_from_file(file_path=global_metadata_path)
metadata = dict_deep_update(metadata, global_metadata_from_yaml)

# Add subject info
metadata["Subject"].update(subject_id=subject_id, age=subject_age, sex=subject_sex)

# Add experiment-specific ophys metadata
ophys_metadata_from_yaml = load_dict_from_file(file_path=ophys_metadata_path)
metadata = dict_deep_update(metadata, ophys_metadata_from_yaml, append_list=False)

converter.run_conversion(
    metadata=metadata, nwbfile_path=nwbfile_path, conversion_options=conversion_options, overwrite=True
)
