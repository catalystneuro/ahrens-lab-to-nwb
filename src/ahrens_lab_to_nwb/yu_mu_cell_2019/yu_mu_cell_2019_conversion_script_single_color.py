"""Primary script to run to convert an entire session of data using the NWBConverter."""
from pathlib import Path
from datetime import datetime
from dateutil import tz

import numpy as np
import h5py

from neuroconv.utils import load_dict_from_file, dict_deep_update

from ahrens_lab_to_nwb.yu_mu_cell_2019.yu_mu_cell_2019_nwbconverter import YuMuCell2019SingleColorNWBConverter


# Manually specify everything here as it changes
# ----------------------------------------------
stub_test = False  # True for a fast prototype file, False for converting the entire session
stub_frames = 4  # Length of stub file, if stub_test=True
cell_type = "neuron"  # Either "neuron" or "glia"

timezone = "US/Eastern"
session_name = "20160113_4_1_cy14_7dpf_0gain_trial_20170113_171241"
single_color_session_description = "A single-color optic channel recording of either a neuron or a glia population."

cell_type_id = 0 if cell_type == "neuron" else 1
session_name_split = session_name.split("_")
subject_number = session_name_split[1]
session_start_date = session_name_split[-2]

metadata_folder = Path(__file__).parent / "metadata"  # The pre-built one in the repository; can also use a local copy
global_metadata_path = metadata_folder / "yu_mu_cell_2019_global_metadata.yml"
ophys_metadata_path = metadata_folder / "yu_mu_cell_2019_single_color_neuron_metadata.yml"
raw_behavior_series_description_file_path = metadata_folder / "yu_mu_cell_2019_behavior_descriptions.yml"

imaging_folder_path = Path(f"E:/Ahrens/Imaging/{session_start_date}/fish{subject_number}/{session_name}/raw")
segmentation_file_path = Path(f"E:/Ahrens/Segmentation/{session_name}/Cells{cell_type_id}_clean.mat")

# Some of these may not exist and that's OK (existence is checked before adding it to the conversion)
ephys_folder_path = Path(f"E:/Ahrens/Imaging/{session_start_date}/fish{subject_number}/{session_name}/ephys")
raw_behavior_file_path = ephys_folder_path / "rawdata.mat"
processed_behavior_file_path = ephys_folder_path / "data.mat"
trial_table_file_path = ephys_folder_path / "trial_info.mat"
states_folder_path = ephys_folder_path

nwbfile_path = Path("E:/Ahrens/NWB/full_single_color_imaging+neuron.nwb")
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

imaging_rate = 2.73
behavior_rate = 5989.6
source_data = dict(
    Imaging=dict(
        folder_path=str(imaging_folder_path),
        sampling_frequency=imaging_rate,
        shape=[29, 888, 2048],
        dtype="int16",
    ),
    SingleColorSegmentation=dict(file_path=str(segmentation_file_path), sampling_frequency=imaging_rate),
    ActivityStates=dict(folder_path=str(states_folder_path), sampling_frequency=behavior_rate),
)
if raw_behavior_file_path.exists():
    source_data.update(
        RawBehavior=dict(
            data_file_path=str(raw_behavior_file_path),
            metadata_file_path=str(raw_behavior_series_description_file_path),
            sampling_frequency=behavior_rate,
        )
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
    Imaging=dict(
        stub_test=stub_test,
        stub_frames=stub_frames,
        iterator_options=dict(
            buffer_gb=0.5,
            chunk_shape=(1, 2048, 888, 1),
            display_progress=True,
            progress_bar_options=dict(desc="Converting imaging data...", position=0),
        ),
    ),
    SingleColorSegmentation=dict(
        stub_test=stub_test,
        stub_frames=stub_frames,
        iterator_options=dict(
            buffer_gb=0.5,
            display_progress=True,
            progress_bar_options=dict(desc="Converting segmentation data...", position=1),
        ),
    ),
)

converter = YuMuCell2019SingleColorNWBConverter(source_data=source_data)

# Add synchronized timestamps to all imaging and segmentation objects
with h5py.File(name=processed_behavior_file_path) as file:
    frame_tracker = file["data"]["frame"][:]
timestamps = np.where(np.diff(frame_tracker))[1][:-1] / behavior_rate

if session_name == "20160113_4_1_cy14_7dpf_0gain_trial_20170113_171241":
    imaging_timestamps = timestamps[8985:]  # all data prior to this is missing

# For stub mode
if "Imaging" in converter.data_interface_objects:
    converter.data_interface_objects["Imaging"].imaging_extractor.set_times(times=imaging_timestamps)
if "SingleColorSegmentation" in converter.data_interface_objects:
    converter.data_interface_objects["SingleColorSegmentation"].segmentation_extractor.set_times(times=timestamps)

metadata = converter.get_metadata()
metadata["NWBFile"].update(session_start_time=session_start_time, session_description=single_color_session_description)

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
