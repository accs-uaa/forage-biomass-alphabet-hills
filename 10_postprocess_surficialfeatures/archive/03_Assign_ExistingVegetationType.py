# -*- coding: utf-8 -*-
# ---------------------------------------------------------------------------
# Assign existing vegetation type
# Author: Timm Nawrocki
# Last Updated: 2022-10-27
# Usage: Must be executed in an Anaconda Python 3.9+ distribution.
# Description: "Assign existing vegetation type" assigns a vegetation type label from physiography and foliar cover.
# ---------------------------------------------------------------------------

# Import packages
import glob
import pandas as pd
import os

# Define round
round_date = 'round_20220607'

# Set root directory
drive = 'N:/'
root_folder = 'ACCS_Work'

# Define folder structure
data_folder = os.path.join(drive,
                           root_folder,
                           'Projects/WildlifeEcology/Moose_AlphabetHills/Data/Data_Output')
input_folder = os.path.join(data_folder, 'predicted_tables', round_date, 'physiography')
output_folder = os.path.join(data_folder, 'predicted_tables', round_date, 'evt')

# Define input files
os.chdir(input_folder)
input_files = glob.glob('*.csv')

# Define EVT dictionary
evt_dictionary = {'Barren': 1,
                  'Sparsely Vegetated': 2,
                  'Water': 3,
                  'Aspen / White Spruce - Aspen': 4,
                  'Birch': 5,
                  'Black Spruce - Alaska Birch - Sphagnum': 6,
                  'Black Spruce, Mesic (Inactive Floodplain)': 7,
                  'Black Spruce, Hygric (- Hydric)': 8,
                  'White Spruce Floodplain': 9,
                  'White Spruce - Alder': 10,
                  'White Spruce - Birch Shrub': 11,
                  'White Spruce - Willow': 12,
                  'Spruce (- Alaska Birch)': 13,
                  'Alder - Willow Floodplain': 14,
                  'Alder - Willow': 15,
                  'Birch Shrub - Willow, Mesic': 16,
                  'Birch Shrub - Willow, Hygric (- Hydric)': 17,
                  'Ericaceous Dwarf Shrub - Dryas': 18,
                  'Sedge Wetland': 19,
                  'Unclassified Floodplain': 20,
                  'Unclassified Herbaceous': 21,
                  'Unclassified': 22
                  }

# Define EVT Key
def evt_key(physiography, elevation, total_cover, tree_cover, spruce_cover, shrub_cover, lowtall_shrub,
            spruce_ratio, deciduous_ratio, alnus_salshr, wet_indicator,
            fol_alnus, fol_betshr, fol_dectre, fol_erivag, fol_salshr, fol_sphagn, fol_wetsed):
    # Define unvegetated types
    if physiography == 1:
        if total_cover < 20:
            return 'Barren'
        elif total_cover >= 20:
            return 'Sparsely Vegetated'
    elif physiography == 6:
        return 'Water'
    elif physiography == 8:
        return 'Aspen / White Spruce - Aspen'
    # Define floodplain types
    elif physiography == 5:
        # Define forested floodplains
        if tree_cover >= 20:
            if spruce_ratio < 0.4:
                return 'Black Spruce, Mesic (Inactive Floodplain)'
            elif spruce_ratio >= 0.4:
                return 'White Spruce Floodplain'
        # Define non-forested floodplain types
        elif tree_cover < 20:
            # Define floodplain shrub types
            if alnus_salshr >= 15:
                return 'Alder - Willow Floodplain'
            # Define floodplain herbaceous types
            elif fol_wetsed >= 10:
                return 'Sedge Wetland'
            else:
                return 'Unclassified Floodplain'
    # Define riparian types
    elif physiography == 4:
        if spruce_cover >= 25:
            if spruce_ratio <= 0.6 and (fol_sphagn >= 15 or fol_erivag >= 15):
                return 'Black Spruce, Hygric (- Hydric)'
            elif spruce_ratio <= 0.4:
                return 'Black Spruce, Mesic (Inactive Floodplain)'
            elif 0.6 > spruce_ratio > 0.4:
                return 'Spruce (- Alaska Birch)'
            elif spruce_ratio >= 0.6:
                if fol_salshr >= 10:
                    return 'White Spruce - Willow'
                elif fol_alnus >= 20:
                    return 'White Spruce - Alder'
                elif fol_betshr >= 20:
                    return 'White Spruce - Birch Shrub'
                else:
                    return 'Spruce (- Alaska Birch)'
        else:
            # Define shrub types
            if lowtall_shrub >= 20:
                if fol_alnus >= 20:
                    return 'Alder - Willow'
                else:
                    return 'Birch Shrub - Willow, Hygric (- Hydric)'
            # Define herbaceous types
            elif lowtall_shrub < 20:
                # Define wetland sedge types
                if fol_wetsed >= 10:
                    return 'Sedge Wetland'
                else:
                    return 'Unclassified Herbaceous'
            else:
                return 'Unclassified'
    # Define non-forested wetland types
    elif physiography == 3:
        if lowtall_shrub >= 20:
            if fol_alnus >= 20:
                return 'Alder - Willow'
            else:
                return 'Birch Shrub - Willow, Hygric (- Hydric)'
        # Define herbaceous types
        elif lowtall_shrub < 20:
            # Define wetland sedge types
            if fol_wetsed >= 10:
                return 'Sedge Wetland'
            else:
                return 'Unclassified Herbaceous'
        else:
            return 'Unclassified'
    # Define upland and lowland types
    elif physiography == 7 or physiography == 2:
        # Define deciduous and mixed forest types
        if (tree_cover >= 20 or spruce_cover >= 10) and elevation <= 1040:
            # Define deciduous forests
            if deciduous_ratio >= 0.75 and fol_dectre >= 15:
                # Account for confusion between deciduous trees and alder - willow near treeline
                if fol_alnus >= 30:
                    return 'Alder - Willow'
                else:
                    return 'Birch'
            # Define mixed forests
            elif 0.75 > deciduous_ratio > 0.6 and fol_dectre > 10:
                if spruce_ratio <= 0.6 and fol_sphagn >= 15:
                    return 'Black Spruce - Alaska Birch - Sphagnum'
                elif spruce_ratio > 0.6 or fol_sphagn < 15:
                    return 'Spruce (- Alaska Birch)'
            # Define coniferous forest types
            elif deciduous_ratio <= 0.6 or fol_dectre <= 10:
                if spruce_ratio <= 0.6 and (fol_sphagn >= 15 or fol_erivag >= 15):
                    return 'Black Spruce, Hygric (- Hydric)'
                elif spruce_ratio <= 0.4:
                    return 'Black Spruce, Mesic (Inactive Floodplain)'
                elif 0.6 > spruce_ratio > 0.4:
                    return 'Spruce (- Alaska Birch)'
                elif spruce_ratio >= 0.6:
                    if fol_salshr >= 15:
                        return 'White Spruce - Willow'
                    elif fol_alnus >= 20:
                        return 'White Spruce - Alder'
                    elif fol_betshr >= 20:
                        return 'White Spruce - Birch Shrub'
                    else:
                        return 'Spruce (- Alaska Birch)'
        # Define non-forest types
        else:
            # Define shrub types
            if shrub_cover >= 25:
                if lowtall_shrub >= 20:
                    if fol_alnus >= 20:
                        return 'Alder - Willow'
                    elif elevation <= 1040 and wet_indicator >= 25:
                        return 'Birch Shrub - Willow, Hygric (- Hydric)'
                    else:
                        return 'Birch Shrub - Willow, Mesic'
                # Define dwarf shrub types
                elif lowtall_shrub < 20:
                    return 'Ericaceous Dwarf Shrub - Dryas'
            # Define herbaceous types
            elif shrub_cover < 25:
                # Define wetland sedge types
                if fol_wetsed >= 10:
                    return 'Sedge Wetland'
                else:
                    return 'Unclassified Herbaceous'
            else:
                return 'Unclassified'
    else:
        'Unclassified'

# Loop through input files and assign EVT
count = 1
input_length = len(input_files)
for file in input_files:
    print(f'Processing input file {count} of {input_length}...')
    # Define output file
    output_file = os.path.join(output_folder, os.path.split(file)[1])

    # Read input data
    input_data = pd.read_csv(file).dropna()

    # Calculate total cover
    input_data['total_cover'] = input_data['fol_alnus'] + input_data['fol_betshr'] + input_data['fol_dectre'] + \
                                input_data['fol_dryas'] + input_data['fol_empnig'] + input_data['fol_erivag'] + \
                                input_data['fol_picgla'] + input_data['fol_picmar'] + input_data['fol_rhoshr'] + \
                                input_data['fol_salshr'] + input_data['fol_sphagn'] + input_data['fol_vaculi'] + \
                                input_data['fol_vacvit'] + input_data['fol_wetsed']

    # Calculate tree cover
    input_data['tree_cover'] = input_data['fol_dectre'] + input_data['fol_picgla'] + input_data['fol_picmar']
    input_data['spruce_cover'] = input_data['fol_picgla'] + input_data['fol_picmar']

    # Calculate shrub cover
    input_data['shrub_cover'] = input_data['fol_alnus'] + input_data['fol_betshr'] + input_data['fol_dryas'] + \
                                input_data['fol_empnig'] + input_data['fol_rhoshr'] + input_data['fol_salshr'] + \
                                input_data['fol_vaculi'] + input_data['fol_vacvit']

    # Calculate low-tall shrub cover
    input_data['lowtall_shrub'] = input_data['fol_alnus'] + input_data['fol_betshr'] + input_data['fol_salshr']

    # Calculate alder - willow cover
    input_data['alnus_salshr'] = input_data['fol_alnus'] + input_data['fol_salshr']

    # Calculate birch - willow cover
    input_data['betshr_salshr'] = input_data['fol_betshr'] + input_data['fol_salshr']

    # Calculate spruce ratio
    input_data['spruce_ratio'] = input_data['fol_picgla'] / (
            input_data['fol_picgla'] + input_data['fol_picmar'] + 0.001)

    # Calculate deciduous ratio
    input_data['deciduous_ratio'] = input_data['fol_dectre'] / (input_data['tree_cover'] + 0.001)

    # Calculate alder ratio
    input_data['alnus_ratio'] = input_data['fol_alnus'] / (input_data['alnus_salshr'] + 0.001)

    # Calculate birch shrub ratio
    input_data['betshr_ratio'] = input_data['fol_betshr'] / (input_data['betshr_salshr'] + 0.001)

    # Calculate wetland indicator
    input_data['wet_indicator'] = input_data['fol_sphagn'] + input_data['fol_wetsed']

    # Assign EVT
    input_data['evt'] = input_data.apply(
        lambda row: evt_key(row['physiography'], row['elevation'], row['total_cover'], row['tree_cover'],
                            row['spruce_cover'], row['shrub_cover'], row['lowtall_shrub'], row['spruce_ratio'],
                            row['deciduous_ratio'], row['alnus_salshr'], row['wet_indicator'],
                            row['fol_alnus'], row['fol_betshr'], row['fol_dectre'], row['fol_erivag'],
                            row['fol_salshr'], row['fol_sphagn'], row['fol_wetsed']),
        axis=1)

    # Fill null EVT
    input_data['evt'].fillna('Unclassified', inplace=True)

    # Assign EVT value
    input_data['evt_value'] = input_data['evt'].apply(lambda x: evt_dictionary.get(x))

    # Save output data
    input_data.to_csv(output_file, header=True, index=False, sep=',', encoding='utf-8')

    # Increase count
    count += 1
