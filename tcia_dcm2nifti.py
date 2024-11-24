import os
import subprocess
import SimpleITK as sitk
import json
import nibabel as nib
import numpy as np

"""
Before running this script:
1 - Download dcmqi: https://github.com/QIICR/dcmqi/releases
2 - Find the path to segimage2itkimage

Inputs: 
    - Spine-Mets-CT-SEG Dataset from TCIA in DICOM format
Outputs:
    - Spine-Mets-CT-SEG Dataset from TCIA in Nifti format
    -- CT in nifti
    -- Segmentation in nifti
    -- level to label mapping file (JSON and txt)

"""

def convert_ct_to_nifti(input_folder, output_file):
    """
    Convert a folder of CT DICOM files to a single NIfTI file.
    """
    reader = sitk.ImageSeriesReader()
    dicom_files = reader.GetGDCMSeriesFileNames(input_folder)
    reader.SetFileNames(dicom_files)
    image = reader.Execute()
    sitk.WriteImage(image, output_file)
    print(f"Converted CT: {input_folder} -> {output_file}")
    return image

def convert_segmentation_to_nifti(segmentation_file, output_directory, case_name, path_to_segimage2itkimage):
    """
    Convert a DICOM segmentation file to NIfTI using dcmqi.
    """
    command = [
        path_to_segimage2itkimage,
        "--inputDICOM", segmentation_file,
        "--outputDirectory", os.path.dirname(output_directory),
        "--mergeSegments",
        "-t", "nii",
        "-p", case_name+"_seg",
    ]
    print(f"Running dcmqi: {' '.join(command)}")
    subprocess.run(command, check=True)
    print(f"Converted Segmentation: {segmentation_file} -> {output_directory}")

def find_ct_and_segmentation_folders(case_folder):
    """
    Detect the CT and segmentation folders within the random-named subfolder.
    """
    random_folder = None
    for item in os.listdir(case_folder):
        item_path = os.path.join(case_folder, item)
        if os.path.isdir(item_path):
            random_folder = item_path
            break
    
    if not random_folder:
        raise ValueError(f"No subfolder found under {case_folder}.")
    
    ct_folder = None
    segmentation_folder = None
    segmentation_file = None

    for subfolder in os.listdir(random_folder):
        subfolder_path = os.path.join(random_folder, subfolder)
        if not os.path.isdir(subfolder_path):
            continue
        
        # Check contents of the subfolder
        dicom_files = [
            f for f in os.listdir(subfolder_path) if f.lower().endswith(".dcm")
        ]

        if len(dicom_files) > 1:  # Likely CT folder
            ct_folder = subfolder_path
        elif len(dicom_files) == 1:  # Likely Segmentation folder
            segmentation_folder = subfolder_path
            segmentation_file = os.path.join(subfolder_path, dicom_files[0])

    if not ct_folder or not segmentation_file:
        raise ValueError(f"Could not locate CT or segmentation in {case_folder}.")
    
    return ct_folder, segmentation_file

def batch_convert(input_folder, output_folder, path_to_segimage2itkimage):
    """
    Convert CT and segmentation files in all cases within the main folder.
    """
    if not os.path.exists(output_folder):
        os.makedirs(output_folder)
        
    # Dictionary for fast text-to-label lookup
    text_to_label_mapping = {
        "T1 vertebra": 1,
        "T2 vertebra": 2,
        "T3 vertebra": 3,
        "T4 vertebra": 4,
        "T5 vertebra": 5,
        "T6 vertebra": 6,
        "T7 vertebra": 7,
        "T8 vertebra": 8,
        "T9 vertebra": 9,
        "T10 vertebra": 10,
        "T11 vertebra": 11,
        "T12 vertebra": 12,
        "L1 vertebra": 13,
        "L2 vertebra": 14,
        "L3 vertebra": 15,
        "L4 vertebra": 16,
        "L5 vertebra": 17
    }        
    
    for case in os.listdir(input_folder):
        case_path = os.path.join(input_folder, case)
        if not os.path.isdir(case_path):
            continue

        try:
            ct_folder, segmentation_file = find_ct_and_segmentation_folders(case_path)
        except ValueError as e:
            print(f"Skipping {case}: {e}")
            continue

        # Prepare output paths
        case_output_folder = os.path.join(output_folder, case)
        os.makedirs(case_output_folder, exist_ok=True)

        ct_output_file = os.path.join(case_output_folder, f"{case}_ct.nii.gz")
        segmentation_output_folder = os.path.join(case_output_folder, case)
        
        # Convert CT
        convert_ct_to_nifti(ct_folder, ct_output_file)

        # Convert segmentation
        convert_segmentation_to_nifti(segmentation_file, segmentation_output_folder, case, path_to_segimage2itkimage)

        
        
        
        # Get the segmentation JSON file
        json_file = os.path.join(case_output_folder, f"{case}_seg-meta.json")
        with open(json_file, 'r') as file:
            json_data = json.load(file)
            
        # Get the segmentation NIFTI file
        seg_file = os.path.join(case_output_folder, f"{case}_seg-1.nii.gz")
        seg_img = nib.load(seg_file)  # Load the image
        seg_data = seg_img.get_fdata().astype(np.int32) # Get the segmentation data as a NumPy array

        
        # Extract SegmentLabel and labelID
        segment_labels_and_ids = []

        for segment_group in json_data.get("segmentAttributes", []):
            for segment in segment_group:
                label = segment.get("SegmentLabel")
                label_id = segment.get("labelID")
                if label and label_id is not None:
                    segment_labels_and_ids.append((label, label_id))

        # updated the label ids
        for label_text, label_id in segment_labels_and_ids:
            if label_text in text_to_label_mapping:
                seg_data[seg_data == label_id] = text_to_label_mapping[label_text]
                print(f"{label_text} with label {label_id} modified to label {text_to_label_mapping[label_text]}")
            else:
                print(f"Warning: {label_text} not found in text_to_label_mapping. Skipping.")
   
            
        mod_seg_img = nib.Nifti1Image(seg_data, affine=seg_img.affine, header=seg_img.header)
        nib.save(mod_seg_img, seg_file)        
        os.remove(json_file)
        
    # Save the dictionary as a JSON file    
    with open(os.path.join(output_folder, f"level_to_label_mapping.json"), 'w') as json_file:
        json.dump(text_to_label_mapping, json_file, indent=4)    
    # Save the dictionary to a text file
    with open(os.path.join(output_folder, f"level_to_label_mapping.txt"), 'w') as file:
        for key, value in text_to_label_mapping.items():
            file.write(f"{key}: {value}\n")    
        


# Main execution
if __name__ == "__main__":
    input_folder = "/path/to/folder/Spine-Mets-CT-SEG"  # Replace with the path to the input folder
    output_folder = "/path/to/folder/Spine-Mets-CT-SEG-Nifti"  # Replace with the path for the output
    path_to_segimage2itkimage = "/path/to/folder/dcmqi-1.3.4-mac/bin/segimage2itkimage"
    
    
    batch_convert(input_folder, output_folder, path_to_segimage2itkimage)
