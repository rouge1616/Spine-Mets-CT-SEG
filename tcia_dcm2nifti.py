import os
import subprocess
import SimpleITK as sitk

"""
Before runing this script:
1 - Download dcmqi: https://github.com/QIICR/dcmqi/releases
2 - Find the path to segimage2itkimage
"""

path_to_segimage2itkimage = "/path/to/folder/dcmqi-1.3.4-mac/bin/segimage2itkimage"

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

def convert_segmentation_to_nifti(segmentation_file, output_file):
    """
    Convert a DICOM segmentation file to NIfTI using dcmqi.
    """
    command = [
        path_to_segimage2itkimage,
        "--inputDICOM", segmentation_file,
        "--outputDirectory", os.path.dirname(output_file),
        "--mergeSegments",
        "-t", "nii",
        "-p", "seg",
    ]
    print(f"Running dcmqi: {' '.join(command)}")
    subprocess.run(command, check=True)
    print(f"Converted Segmentation: {segmentation_file} -> {output_file}")

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

def batch_convert(main_folder, output_folder):
    """
    Convert CT and segmentation files in all cases within the main folder.
    """
    if not os.path.exists(output_folder):
        os.makedirs(output_folder)
    
    for case in os.listdir(main_folder):
        case_path = os.path.join(main_folder, case)
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
        segmentation_output_file = os.path.join(case_output_folder, f"{case}_segmentation.nii.gz")

        # Convert CT
        convert_ct_to_nifti(ct_folder, ct_output_file)

        # Convert segmentation
        convert_segmentation_to_nifti(segmentation_file, segmentation_output_file)


# Main execution
if __name__ == "__main__":
    input_folder = "/path/to/folder/Spine-Mets-CT-SEG"  # Replace with the path to the input folder
    output_folder = "/path/to/folder/Spine-Mets-CT-SEG-Nifti"  # Replace with the path for the output

    batch_convert(input_folder, output_folder)
