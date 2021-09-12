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

## Additional Information

- We got the question about tariffs for house B and C. Please be aware that the numbers below have been asked to the home 
  owners some time after the study (Sept 2021). Small deviations with respect to the actual values at the time of the study are to be expected.
  
  |        |                               | Periods |       | Given in \[CHF/kWh\]  |              |                            |
  | ------ | ----------------------------- | ------- | ----- | --------------------- | ------------ | -------------------------- |
  | Haus B |                               | Start   | End   | B\_total\_cons\_power |              | B_to_net_power             |
  |        | high-tariff (not on weekends) | 07:00   | 19:00 | ~0.21                 |              | Q1/Q4: ~0.13, Q2/Q3: ~0.07 |
  |        | low-tariff (complete weekend) | 19:00   | 07:00 | ~0.18                 |              |                            |
  | Haus C |                               |         |       | C\_total\_cons\_power | C\_hp\_power | C\_to\_net\_power          |
  |        | high-tariff                   | 07:00   | 22:00 | ~0.26                 | ~0.17        | 0.08                       |
  |        | low-tariff                    | 22:00   | 07:00 | ~0.16                 | ~0.14        | 0.08                       |


