# -*- coding: utf-8 -*-
# ---------------------------------------------------------------------------
# Extract covariates to points
# Author: Timm Nawrocki
# Last Updated: 2022-01-14
# Usage: Must be executed in R 4.0.0+.
# Description: "Extract covariates to points" extracts data from rasters to points.
# ---------------------------------------------------------------------------

# Set root directory
drive = 'N:'
root_folder = 'ACCS_Work'

# Define data folder
data_folder = paste(drive,
                    root_folder,
                    'Data',
                    sep ='/')

# Define input folders
project_folder = paste(drive,
                       root_folder,
                       'Projects/WildlifeEcology/Moose_AlphabetHills/Data',
                       sep = '/')
zonal_folder = paste(project_folder,
                     'Data_Input/zonal',
                     sep = '/')
grid_folder = paste(project_folder,
                    'Data_Input/validation',
                    sep = '/')

# Define output folders
output_folder = paste(project_folder,
                      'Data_Input/training_data',
                      sep = '/')

# Define work geodatabase
work_geodatabase = paste(project_folder,
                         'AlphabetHillsBrowseBiomass.gdb',
                         sep = '/')

# Define input datasets
point_feature = 'Alphabet_Segments_Point_Classify'

# Define output datasets
output_csv = paste(output_folder,
                   'AllPoints_ExtractedCovariates.csv',
                   sep = '/')

# Import required libraries for geospatial processing: dplyr, raster, rgdal, sp, and stringr.
library(dplyr)
library(raster)
library(rgdal)
library(sp)
library(stringr)

# Create a list of all predictor rasters
predictors_zonal = list.files(zonal_folder, pattern = 'tif$', full.names = TRUE)
predictors_grid = list.files(grid_folder, pattern = 'tif$', full.names = TRUE)
predictors_all = c(predictors_zonal,
                   predictors_grid)
print(paste('Number of predictor rasters: ', length(predictors_all), sep = ''))
print(predictors_all) # Should be 92

# Generate a stack of all covariate rasters
print('Creating raster stack...')
start = proc.time()
predictor_stack = stack(predictors_all)
end = proc.time() - start
print(end[3])

# Read path data and extract covariates
print('Extracting covariates...')
start = proc.time()
point_data = readOGR(dsn = work_geodatabase, layer = point_feature)
point_extracted = data.frame(point_data@data, raster::extract(predictor_stack, point_data))
end = proc.time() - start
print(end[3])

# Convert field names to standard
point_extracted = point_extracted %>%
  dplyr::rename(aspect = Aspect,
                elevation = Elevation,
                exposure = Exposure,
                heat_load = HeatLoad,
                position = Position,
                radiation = Radiation,
                roughness = Roughness,
                slope = Slope,
                surface_area = SurfaceArea,
                surface_relief = SurfaceRelief,
                wetness = Wetness,
                maxr_01_blue = Chenega_Maxar_01_Blue,
                maxr_01_blue_std = Chenega_Maxar_01_Blue_STD,
                maxr_02_green = Chenega_Maxar_02_Green,
                maxr_02_green_std = Chenega_Maxar_02_Green_STD,
                maxr_03_red = Chenega_Maxar_03_Red,
                maxr_03_red_std = Chenega_Maxar_03_Red_STD,
                maxr_04_nearir = Chenega_Maxar_04_NearIR,
                maxr_04_nearir_std = Chenega_Maxar_04_NearIR_STD,
                maxr_evi2 = Chenega_Maxar_EVI2,
                maxr_evi2_std = Chenega_Maxar_EVI2_STD,
                maxr_ndvi = Chenega_Maxar_NDVI,
                maxr_ndvi_std = Chenega_Maxar_NDVI_STD,
                maxr_ndwi = Chenega_Maxar_NDWI,
                maxr_ndwi_std = Chenega_Maxar_NDWI_STD,
                vh = Sent1_vh,
                vv = Sent1_vv,
                s2_06_02_blue = Sent2_06_2_blue,
                s2_06_03_green = Sent2_06_3_green,
                s2_06_04_red = Sent2_06_4_red,
                s2_06_05_rededge1 = Sent2_06_5_redEdge1,
                s2_06_06_rededge2 = Sent2_06_6_redEdge2,
                s2_06_07_rededge3 = Sent2_06_7_redEdge3,
                s2_06_08_nearir = Sent2_06_8_nearInfrared,
                s2_06_08a_rededge4 = Sent2_06_8a_redEdge4,
                s2_06_11_shortir1 = Sent2_06_11_shortInfrared1,
                s2_06_12_shortir2 = Sent2_06_12_shortInfrared2,
                s2_06_evi2 = Sent2_06_evi2,
                s2_06_nbr = Sent2_06_nbr,
                s2_06_ndmi = Sent2_06_ndmi,
                s2_06_ndsi = Sent2_06_ndsi,
                s2_06_ndvi = Sent2_06_ndvi,
                s2_06_ndwi = Sent2_06_ndwi,
                s2_07_02_blue = Sent2_07_2_blue,
                s2_07_03_green = Sent2_07_3_green,
                s2_07_04_red = Sent2_07_4_red,
                s2_07_05_rededge1 = Sent2_07_5_redEdge1,
                s2_07_06_rededge2 = Sent2_07_6_redEdge2,
                s2_07_07_rededge3 = Sent2_07_7_redEdge3,
                s2_07_08_nearir = Sent2_07_8_nearInfrared,
                s2_07_08a_rededge4 = Sent2_07_8a_redEdge4,
                s2_07_11_shortir1 = Sent2_07_11_shortInfrared1,
                s2_07_12_shortir2 = Sent2_07_12_shortInfrared2,
                s2_07_evi2 = Sent2_07_evi2,
                s2_07_nbr = Sent2_07_nbr,
                s2_07_ndmi = Sent2_07_ndmi,
                s2_07_ndsi = Sent2_07_ndsi,
                s2_07_ndvi = Sent2_07_ndvi,
                s2_07_ndwi = Sent2_07_ndwi,
                s2_08_02_blue = Sent2_08_2_blue,
                s2_08_03_green = Sent2_08_3_green,
                s2_08_04_red = Sent2_08_4_red,
                s2_08_05_rededge1 = Sent2_08_5_redEdge1,
                s2_08_06_rededge2 = Sent2_08_6_redEdge2,
                s2_08_07_rededge3 = Sent2_08_7_redEdge3,
                s2_08_08_nearir = Sent2_08_8_nearInfrared,
                s2_08_08a_rededge4 = Sent2_08_8a_redEdge4,
                s2_08_11_shortir1 = Sent2_08_11_shortInfrared1,
                s2_08_12_shortir2 = Sent2_08_12_shortInfrared2,
                s2_08_evi2 = Sent2_08_evi2,
                s2_08_nbr = Sent2_08_nbr,
                s2_08_ndmi = Sent2_08_ndmi,
                s2_08_ndsi = Sent2_08_ndsi,
                s2_08_ndvi = Sent2_08_ndvi,
                s2_08_ndwi = Sent2_08_ndwi,
                s2_09_02_blue = Sent2_09_2_blue,
                s2_09_03_green = Sent2_09_3_green,
                s2_09_04_red = Sent2_09_4_red,
                s2_09_05_rededge1 = Sent2_09_5_redEdge1,
                s2_09_06_rededge2 = Sent2_09_6_redEdge2,
                s2_09_07_rededge3 = Sent2_09_7_redEdge3,
                s2_09_08_nearir = Sent2_09_8_nearInfrared,
                s2_09_08a_rededge4 = Sent2_09_8a_redEdge4,
                s2_09_11_shortir1 = Sent2_09_11_shortInfrared1,
                s2_09_12_shortir2 = Sent2_09_12_shortInfrared2,
                s2_09_evi2 = Sent2_09_evi2,
                s2_09_nbr = Sent2_09_nbr,
                s2_09_ndmi = Sent2_09_ndmi,
                s2_09_ndsi = Sent2_09_ndsi,
                s2_09_ndvi = Sent2_09_ndvi,
                s2_09_ndwi = Sent2_09_ndwi,
                cv_group = Chenega_ValidationGroups)

# Convert class names to class values
point_final = point_extracted %>%
  mutate(class_value = case_when(manual == 'marine deepwater' ~ 1,
                                 manual == 'marine shallow' ~ 2,
                                 manual == 'freshwater' ~ 3,
                                 manual == 'tidal wetland' ~ 4,
                                 manual == 'coastal herbaceous' ~ 5,
                                 manual == 'coastal barren' ~ 6,
                                 manual == 'anthropogenic' ~ 7,
                                 manual == 'alpine barren' ~ 8,
                                 manual == 'alpine herbaceous' ~ 9,
                                 manual == 'subalpine shrub' ~ 10,
                                 manual == 'coniferous forest' ~ 11,
                                 manual == 'ericaceous low-dwarf shrub' ~ 12,
                                 manual == 'sedge peatland' ~ 13,
                                 manual == 'woody wetland' ~ 14,
                                 TRUE ~ -999))
# Export data as a csv
write.csv(point_final, file = output_csv, fileEncoding = 'UTF-8')
print('Finished extracting to paths.')
print('----------')