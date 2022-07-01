# ahrens-lab-to-nwb
NWB conversion scripts for the [Ahrens lab](https://www.janelia.org/lab/ahrens-lab) data to the [Neurodata Without Borders](https://nwb-overview.readthedocs.io/) data format.

## Clone and install
To run the conversion some basic machinery is needed: **python, git and pip**. For most users, we recommend you to install `conda` ([installation instructions](https://docs.conda.io/en/latest/miniconda.html)) as it contains all the required machinery in a single and simple install. If your system is windows you might also need to install `git` ([installation instructions](https://github.com/git-guides/install-git)) to interact with this repository.

From a terminal (note that conda should install one in your system) you can do the following:

```
git clone https://github.com/catalystneuro/ahrens-lab-to-nwb
cd ahrens-lab-to-nwb
conda env create --file make_env.yml
conda activate ahrens-lab-to-nwb-env
```
This create a [conda environment](https://docs.conda.io/projects/conda/en/latest/user-guide/concepts/environments.html) which isolates the conversion from your system. We recommend that you run all your conversion related tasks and analysis from that environment to minimize the intereference of this code with your own system.

Alternatively, if you want to avoid conda altogether (for example if you use another virtual environment tool) you can install the repository with the following commands using only pip:
```
git clone https://github.com/catalystneuro/ahrens-lab-to-nwb
cd ahrens-lab-to-nwb
pip install -e .
```

Note:
both of the methods above install the repository in [editable mode](https://pip.pypa.io/en/stable/cli/pip_install/#editable-installs) 

## Repository structure
Each conversion is organized in a directory of its own in the `src` directory:

    ahrens-lab-to-nwb/
    ├── LICENSE
    ├── make_env.yml
    ├── pyproject.toml
    ├── README.md
    ├── requirements.txt
    ├── setup.py
    └── src
        ├── ahrens_lab_to_nwb
        │   ├── conversion_directory_1
        │   └── yu_mu_cell_2019`
        │       ├── yu_mu_cell_2019behaviorinterface.py
        │       ├── yu_mu_cell_2019_convert_script.py
        │       ├── yu_mu_cell_2019_metadata.yml
        │       ├── yu_mu_cell_2019nwbconverter.py
        │       ├── yu_mu_cell_2019_requirements.txt
        │       ├── yu_mu_cell_2019_notes.md

        │       └── __init__.py
        │   ├── conversion_directory_b

        └── __init__.py

 For example, for the conversion `yu_mu_cell_2019` you can find a directory located in `src/ahrens-lab-to-nwb/yu_mu_cell_2019`. Inside each conversion directory you can find the following files:

* `yu_mu_cell_2019_convert_script.py`: this is the cemtral script that you must run in order to perform the full conversion.
* `yu_mu_cell_2019_requirements.txt`: dependencies specific to this conversion specifically.
* `yu_mu_cell_2019_metadata.yml`: metadata in yaml format for this specific conversion.
* `yu_mu_cell_2019behaviorinterface.py`: the behavior interface. Usually ad-hoc for each conversion.
* `yu_mu_cell_2019nwbconverter.py`: the place where the `NWBConverter` class is defined.
* `yu_mu_cell_2019_notes.md`: notes and comments concerning this specific conversion.

The directory might contain other files that are necessary for the conversion but those are the central ones.

## Running a specific conversion
To run a specific conversion, you might need to install first some conversion specific dependencies that are located in each conversion directory:
```
pip install -r src/ahrens_lab_to_nwb/yu_mu_cell_2019/yu_mu_cell_2019_requirements.txt 
```

You can run a specific conversion with the following command:
```
python src/ahrens_lab_to_nwb/yu_mu_cell_2019/yu_mu_cell_2019_conversion_script.py
```
