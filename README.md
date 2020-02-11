# Intro

This repository contains:
- code to pre-process the RAPT Dataset collected by the iHomeLab. The dataset is available here: <https://doi.org/10.5281/zenodo.3581895>. A detailed description of the dataset can be found in the corresponding publication, see next section. 
- some simple Jupyter notebooks to load and visualize the data.

The repo is organized as follows:
- `docs`: contains auto-generated documentatio of the source code
- `notebooks`: 
    - contains a Jupyter notebook for preprocessing of the raw data
    - contains Jupyter notebooks for each house to load and visualize data
- `src`: contains the main functions used for the preprocessing of the raw data

## Citation 
Huber, P.; Ott, M.; Friedli, M.; Rumsch, A.; Paice, A. Residential Power Traces for Five Houses: The iHomeLab RAPT Dataset. Data 2020, 5, 17, <https://doi.org/10.3390/data5010017>

Comments and Questions can be sent to patrick.huber@ihomelab.ch (Answers might take a while).

## Generate Preprocessed Data from Raw Data

In order to use the code, create a conda environment: `conda env create -f environment.yml`

The raw data can be processed by executing the notebook `notebooks/preprocessing_VSxx.ipyn`. Be aware that the raw data
must be available in the following folder structure where the root directory `rawData` is located in the same directory as the notebook.

    .
    +-- rawData
        +--A
        +--B
        +--..

Output:
- folder `datasets` containing a single .hdf-file for each house that combines all sensors. 
- The notebook will create a new folder `missingData` that contains .txt files for each sensor. These files list
  all the intervals of the corresponding sensor that contain no data.
- The notebook will also create a heatmap for each house indicating the percentage of missing data. 


