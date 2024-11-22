# Spine-Mets-CT-SEG
An open annotated dataset and baseline machine learning model for segmentation of vertebrae with metastatic bone lesions from CT
This repository contains some python source code to use the Spine-Mets-CT-SEG dataset.

<br />

![Spine-Mets-CT-SEG dataset](https://www.cancerimagingarchive.net/wp-content/uploads/Spine-Mets-CT-SEG_selected_image.png)

## Dataset
The dataset can be dowloaded here: [TCIA Dataset](https://www.cancerimagingarchive.net/collection/spine-mets-ct-seg/) 

## Usage
CT scans and segmentations are both provided in DICOM. We recommend 3D Slicer's DICOM viewer [3D Slicer](https://www.slicer.org), to view the DICOM images. The CT images can be viewed without additional extensions. 
The segmentations can be viewed using the [QuantitativeReporting extensions](https://qiicr.gitbook.io/quantitativereporting-guide/).

## Convert to Nifti
Use the script _tcia_dcm2nifit.py_ to convert the full dataset to Nifti file format. Make sure to re-assign the correct labels to the the vertebra levels after conversion using the corresponding JSON file. 

## Segmentation Weights
The segmentation weights from the nnUNet training are provided in the folder _/weights_.

## Citation
If you use this code or data for your research please cite this paper:

```
@article{haouchine2024open,
  title={An Open Annotated Dataset and Baseline Machine Learning Model for Segmentation of Vertebrae with Metastatic Bone Lesions from CT},
  author={Haouchine, Nazim and Hackney, David B and Pieper, Steve D and Wells III, William M and Sanhinova, Malika and Balboni, Tracy A and Spektor, Alexander and Huynh, Mai Ann and Kozono, David E and Doyle, Patrick and others},
  journal={medRxiv},
  pages={2024--10},
  year={2024},
  publisher={Cold Spring Harbor Laboratory Press}
}
```

