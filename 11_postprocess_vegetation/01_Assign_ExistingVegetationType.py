# -*- coding: utf-8 -*-
# ---------------------------------------------------------------------------
# Assign existing vegetation type
# Author: Timm Nawrocki
# Last Updated: 2023-02-28
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
input_folder = os.path.join(data_folder, 'predicted_tables', round_date, 'additional')
output_folder = os.path.join(data_folder, 'predicted_tables', round_date, 'vegetation_type')

# Define input files
os.chdir(input_folder)
input_files = glob.glob('*.csv')

predictor_all = ['aspect', 'elevation', 'exposure', 'heat_load', 'position', 'radiation', 'roughness', 'slope',
                 'surface_area', 'surface_relief', 'wetness',
                 'river_position', 'stream_position',
                 'comp_01_blue', 'comp_02_green', 'comp_03_red', 'comp_04_nearir', 'comp_evi2', 'comp_ndvi',
                 'comp_ndwi',
                 'comp_01_blue_std', 'comp_02_green_std', 'comp_03_red_std', 'comp_04_nearir_std',
                 'comp_evi2_std', 'comp_ndvi_std', 'comp_ndwi_std',
                 'vh', 'vv', 'burn_diff',
                 's2_06_02_blue', 's2_06_03_green', 's2_06_04_red', 's2_06_05_rededge1', 's2_06_06_rededge2',
                 's2_06_07_rededge3', 's2_06_08_nearir', 's2_06_08a_rededge4', 's2_06_11_shortir1', 's2_06_12_shortir2',
                 's2_06_evi2', 's2_06_nbr', 's2_06_ndmi', 's2_06_ndsi', 's2_06_ndvi', 's2_06_ndwi',
                 's2_07_02_blue', 's2_07_03_green', 's2_07_04_red', 's2_07_05_rededge1', 's2_07_06_rededge2',
                 's2_07_07_rededge3', 's2_07_08_nearir', 's2_07_08a_rededge4', 's2_07_11_shortir1', 's2_07_12_shortir2',
                 's2_07_evi2', 's2_07_nbr', 's2_07_ndmi', 's2_07_ndsi', 's2_07_ndvi', 's2_07_ndwi',
                 's2_08_02_blue', 's2_08_03_green', 's2_08_04_red', 's2_08_05_rededge1', 's2_08_06_rededge2',
                 's2_08_07_rededge3', 's2_08_08_nearir', 's2_08_08a_rededge4', 's2_08_11_shortir1', 's2_08_12_shortir2',
                 's2_08_evi2', 's2_08_nbr', 's2_08_ndmi', 's2_08_ndsi', 's2_08_ndvi', 's2_08_ndwi',
                 's2_09_02_blue', 's2_09_03_green', 's2_09_04_red', 's2_09_05_rededge1', 's2_09_06_rededge2',
                 's2_09_07_rededge3', 's2_09_08_nearir', 's2_09_08a_rededge4', 's2_09_11_shortir1', 's2_09_12_shortir2',
                 's2_09_evi2', 's2_09_nbr', 's2_09_ndmi', 's2_09_ndsi', 's2_09_ndvi', 's2_09_ndwi']

# Define EVT dictionary
class_values = {'barren': 1,
                'sparsely vegetated': 2,
                'water': 3,
                'balsalm poplar floodplain (white spruce)': 3,
                'white spruce floodplain': 4,
                'alder - willow floodplain': 5,
                'boreal herbaceous floodplain, mesic': 6,
                'black spruce - Alaska birch - Sphagnum': 7,
                'black spruce, mesic (inactive floodplain)': 8,
                'black spruce, wet': 9,
                'white spruce - alder': 10,
                'white spruce - birch shrub': 11,
                'white spruce - willow': 12,
                'mixed spruce (- Alaska birch)': 13,
                'aspen / white spruce - aspen': 14,
                'birch': 15,
                'alder - willow': 16,
                'birch shrub - willow, mesic': 17,
                'birch shrub - willow, wet': 18,
                'montane Dryas-ericaceous dwarf shrub, acidic': 19,
                'boreal sedge meadow, wet': 20,
                'boreal/boreal-montane herbaceous': 21,
                'unclassified': 22
                }


# Define EVT Key
def evt_key(surface, elevation, fol_alnus, fol_betshr, fol_bettre, fol_dectre, fol_dryas,
            fol_empnig, fol_erivag, fol_forb, fol_gramnd, fol_picgla, fol_picmar, fol_rhoshr,
            fol_salshr, fol_sphagn, fol_vaculi, fol_vacvit, fol_wetsed):
    # Calculate summary cover metrics
    total_cover = fol_alnus + fol_betshr + fol_dectre + fol_dryas + fol_empnig + \
                  fol_erivag + fol_forb + fol_picgla + fol_picmar + fol_rhoshr + \
                  fol_salshr + fol_sphagn + fol_vaculi + fol_vacvit + fol_wetsed
    tree_cover = fol_dectre + fol_picgla + fol_picmar
    picea_cover = fol_picgla + fol_picmar
    shrub_cover = fol_alnus + fol_betshr + fol_dryas + fol_empnig + fol_rhoshr + \
                  fol_salshr + fol_vaculi + fol_vacvit
    lowtall_shrub = fol_alnus + fol_betshr + fol_salshr
    alnus_salshr = fol_alnus + fol_salshr
    betshr_salshr = fol_betshr + fol_salshr
    herbaceous_cover = fol_forb + fol_gramnd

    # Calculate ratio metrics
    picea_ratio = fol_picgla / (fol_picgla + fol_picmar + 0.001)
    deciduous_ratio = fol_dectre / (tree_cover + 0.001)

    # Calculate wetland indicator
    wet_indicator = fol_sphagn + fol_wetsed

    # Define default class
    evt_class = 'unclassified'

    #### DEFINE NON-VEGETATED TYPES (OR SPARSELY VEGETATED)
    # Define barren and sparsely vegetated
    if surface == 1:
        if total_cover < 20:
            evt_class = 'barren'
        elif herbaceous_cover >= 30:
            evt_class = 'boreal/boreal-montane herbaceous'
        else:
            evt_class = 'sparsely vegetated'
    # Define water
    elif surface == 6:
        evt_class = 'water'
    #### DEFINE ASPEN TYPE
    elif surface == 8:
        evt_class = 'aspen / white spruce - aspen'
    #### DEFINE FLOODPLAIN TYPES
    elif surface == 5:
        # Define forested floodplains
        if tree_cover >= 15:
            if deciduous_ratio > 0.75:
                evt_class = 'balsalm poplar floodplain (white spruce)'
            elif deciduous_ratio <= 0.75:
                if picea_ratio <= 0.6 and (wet_indicator >= 15 or fol_erivag >= 10):
                    evt_class = 'black spruce, wet'
                elif picea_ratio <= 0.4:
                    evt_class = 'black spruce, mesic (inactive floodplain)'
                else:
                    evt_class = 'white spruce floodplain'
        # Define non-forested floodplain types
        else:
            if lowtall_shrub >= 30:
                if fol_alnus >= 10:
                    evt_class = 'alder - willow floodplain'
                else:
                    if wet_indicator >= 15:
                        evt_class = 'birch shrub - willow, wet'
                    else:
                        evt_class = 'birch shrub - willow, mesic'
            # Define floodplain herbaceous types
            elif fol_wetsed >= 10:
                evt_class = 'boreal sedge meadow, wet'
            elif herbaceous_cover >= 20:
                evt_class = 'boreal herbaceous floodplain, mesic'
            else:
                evt_class = 'unclassified'
    #### DEFINE RIPARIAN TYPES
    elif surface == 4:
        if picea_cover >= 15:
            if picea_ratio <= 0.6 and (wet_indicator >= 15 or fol_erivag >= 10):
                evt_class = 'black spruce, wet'
            elif picea_ratio <= 0.4:
                evt_class = 'black spruce, mesic (inactive floodplain)'
            elif 0.6 > picea_ratio > 0.4:
                evt_class = 'mixed spruce (- Alaska birch)'
            elif picea_ratio >= 0.6:
                if fol_salshr >= 10:
                    evt_class = 'white spruce - willow'
                elif fol_alnus >= 20:
                    evt_class = 'white spruce - alder'
                elif fol_betshr >= 20:
                    evt_class = 'white spruce - birch shrub'
                else:
                    evt_class = 'unclassified'
        else:
            # Define shrub types
            if lowtall_shrub >= 25:
                if fol_alnus >= 10:
                    evt_class = 'alder - willow'
                else:
                    evt_class = 'birch shrub - willow, wet'
            # Define herbaceous types
            else:
                # Define wetland sedge types
                if fol_wetsed >= 10:
                    evt_class = 'boreal sedge meadow, wet'
                elif herbaceous_cover >= 20:
                    evt_class = 'boreal/boreal-montane herbaceous'
                else:
                    evt_class = 'sparsely vegetated'
    #### DEFINE NON-FORESTED DRAINAGE TYPES
    elif surface == 3:
        if lowtall_shrub >= 25:
            if fol_alnus >= 10:
                evt_class = 'alder - willow'
            else:
                evt_class = 'birch shrub - willow, wet'
        # Define herbaceous types
        else:
            # Define wetland sedge types
            if fol_wetsed >= 10:
                evt_class = 'boreal sedge meadow, wet'
            elif herbaceous_cover >= 20:
                evt_class = 'boreal/boreal-montane herbaceous'
            else:
                evt_class = 'unclassified'
    #### DEFINE UPLAND AND LOWLAND TYPES
    elif surface == 7 or surface == 2:
        # Define deciduous and mixed forest types
        if (tree_cover >= 15 or picea_cover >= 10) and elevation <= 1040:
            # Define deciduous forests
            if deciduous_ratio >= 0.75 and fol_dectre >= 20:
                # Account for confusion between deciduous trees, alder - willow, and birch - willow near treeline
                if fol_alnus >= 30:
                    evt_class = 'alder - willow'
                elif fol_bettre >= 25:
                    evt_class = 'birch'
                else:
                    evt_class = 'birch shrub - willow, mesic'
            # Define mixed forests
            elif 0.75 > deciduous_ratio > 0.6 and fol_dectre > 15:
                if picea_ratio <= 0.6 and fol_sphagn >= 15:
                    evt_class = 'black spruce - Alaska birch - Sphagnum'
                else:
                    evt_class = 'mixed spruce (- Alaska birch)'
            # Define coniferous forest types
            else:
                if picea_ratio <= 0.6 and (wet_indicator >= 15 or fol_erivag >= 10):
                    evt_class = 'black spruce, wet'
                elif picea_ratio <= 0.4:
                    evt_class = 'black spruce, mesic (inactive floodplain)'
                elif 0.6 > picea_ratio > 0.4:
                    evt_class = 'mixed spruce (- Alaska birch)'
                elif picea_ratio >= 0.6:
                    if fol_salshr >= 20:
                        evt_class = 'white spruce - willow'
                    elif fol_alnus >= 20:
                        evt_class = 'white spruce - alder'
                    elif fol_betshr >= 20:
                        evt_class = 'white spruce - birch shrub'
                    else:
                        evt_class = 'white spruce - birch shrub'
        # Define non-forest types
        else:
            # Define shrub types
            if shrub_cover >= 30:
                if lowtall_shrub >= 25:
                    if fol_alnus >= 20:
                        evt_class = 'alder - willow'
                    elif elevation <= 1040 and wet_indicator >= 25:
                        evt_class = 'birch shrub - willow, wet'
                    elif elevation <= 1040 and wet_indicator < 25:
                        evt_class = 'birch shrub - willow, mesic'
                    # Define montane types
                    elif elevation > 1040:
                        if herbaceous_cover >= 25:
                            evt_class = 'boreal/boreal-montane herbaceous'
                        elif lowtall_shrub >= 35:
                            evt_class = 'birch shrub - willow, mesic'
                        else:
                            evt_class = 'montane Dryas-ericaceous dwarf shrub, acidic'
                    else:
                        evt_class = 'montane Dryas-ericaceous dwarf shrub, acidic'
                # Define dwarf shrub types
                else:
                    evt_class = 'montane Dryas-ericaceous dwarf shrub, acidic'
            # Define herbaceous types
            else:
                # Define wetland sedge types
                if fol_wetsed >= 10:
                    evt_class = 'boreal sedge meadow, wet'
                elif herbaceous_cover >= 20:
                    evt_class = 'boreal/boreal-montane herbaceous'
                else:
                    if elevation > 1040:
                        evt_class = 'boreal/boreal-montane herbaceous'
                    else:
                        evt_class = 'unclassified'
    else:
        evt_class = 'unclassified'

    return evt_class


# Loop through input files and assign EVT
count = 1
input_length = len(input_files)
for file in input_files:
    print(f'Processing input file {count} of {input_length}...')
    # Define output file
    output_file = os.path.join(output_folder, os.path.split(file)[1])

    # Read input data
    input_data = pd.read_csv(file).dropna().rename(columns={'physiography': 'surface'})

    # Assign EVT
    input_data['evt'] = input_data.apply(
        lambda row: evt_key(row['surface'], row['elevation'], row['fol_alnus'], row['fol_betshr'], row['fol_dectre'],
                            row['fol_bettre'], row['fol_dryas'], row['fol_empnig'], row['fol_erivag'], row['fol_forb'],
                            row['fol_gramnd'], row['fol_picgla'], row['fol_picmar'], row['fol_rhoshr'], row['fol_salshr'],
                            row['fol_sphagn'], row['fol_vaculi'], row['fol_vacvit'], row['fol_wetsed']),
        axis=1)

    # Fill null EVT
    input_data['evt'].fillna('unclassified', inplace=True)

    # Assign EVT value
    input_data['evt_value'] = input_data['evt'].apply(lambda x: class_values.get(x))

    # Save output data
    output_data = input_data.drop(predictor_all, axis=1)
    output_data.to_csv(output_file, header=True, index=False, sep=',', encoding='utf-8')

    # Increase count
    count += 1
