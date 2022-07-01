"""Primary script to run to convert an entire session of data using the NWBConverter."""
from nwb_conversion_tools.utils import load_dict_from_file, dict_deep_update

from ahrens_lab_to_nwb.yu_mu_cell_2019 import YuMuCell2019NWBConverter
from pathlib import Path

example_path = Path("D:/ExampleNWBConversion")
example_session_id = example_path.stem
nwbfile_path = example_path / f"{example_session_id}.nwb"

metadata_path = Path(__file__) / "yu_mu_cell_2019_metadata.yaml"

source_data = dict(
    Recording=dict(),
    LFP=dict(),
    Sorting=dict(),
    Behavior=dict(),
)

converter = YuMuCell2019NWBConverter(source_data=source_data)

metadata = converter.get_metadata()
metadata_from_yaml = load_dict_from_file(metadata_path)
metadata = dict_deep_update(metadata, metadata_from_yaml)

converter.run_conversion(metadata=metadata, nwbfile_path=nwbfile_path)
