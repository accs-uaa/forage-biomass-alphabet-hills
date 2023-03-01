# -*- coding: utf-8 -*-
# ---------------------------------------------------------------------------
# Extract additional covariates to points
# Author: Timm Nawrocki
# Last Updated: 2022-06-07
# Usage: Must be executed in R 4.0.0+.
# Description: "Extract covariates to points" extracts data from rasters to points.
# ---------------------------------------------------------------------------

# Set round date
round_date = 'round_20220607'

# Set root directory
drive = 'N:'
root_folder = 'ACCS_Work'

# Define input folders
project_folder = paste(drive,
                       root_folder,
                       'Projects/WildlifeEcology/Moose_AlphabetHills/Data',
                       sep = '/')
input_folder = paste(project_folder,
                     'Data_Output/predicted_tables',
                     round_date,
                     'surficial_features',
                     sep = '/')
raster_folder = paste(project_folder,
                      'Data_Output/output_rasters',
                      round_date,
                      'foliar_cover',
                      sep = '/')

# Define output folders
output_folder = paste(project_folder,
                      'Data_Output/predicted_tables',
                      round_date,
                      'additional',
                      sep = '/')

# Define input datasets
forb_raster = paste(raster_folder, 'Alphabet_fol_forb.tif', sep = '/')
graminoid_raster = paste(raster_folder, 'Alphabet_fol_graminoid.tif', sep = '/')
decshr_raster = paste(raster_folder, 'Alphabet_fol_decshr.tif', sep = '/')

# Define grids
grid_list = c('A2', 'A3', 'A4', 'A5', 'A6',
             'B1', 'B2', 'B3', 'B4', 'B5', 'B6', 'B7',
             'C1', 'C2', 'C3', 'C4', 'C5', 'C6', 'C7',
             'D1', 'D2', 'D3', 'D4', 'D5', 'D6', 'D7',
             'E1', 'E2', 'E3', 'E4', 'E5', 'E6')
grid_length = length(grid_list)

# Import required libraries for geospatial processing: dplyr, raster, rgdal, sp, and stringr.
library(dplyr)
library(raster)
library(rgdal)
library(sf)
library(sp)
library(stringr)

# Generate a stack of rasters
print('Creating raster stack...')
start = proc.time()
raster_stack = stack(c(forb_raster, graminoid_raster, decshr_raster))
end = proc.time() - start
print(end[3])

# Set count
count = 1

# Loop through each grid and extract covariates
for (grid in grid_list) {
  # Define input points
  input_points = paste('points_', grid, sep = '')
  
  # Define input file
  input_file = paste(input_folder, '/', grid, '.csv', sep = '')
  
  # Define output file
  output_file = paste(output_folder, '/', grid, '.csv', sep = '')
  
  # Create output table if it does not already exist
  if (!file.exists(output_file)) {
    print(paste('Extracting segments ', toString(count), ' out of ',
                toString(grid_length), '...', sep=''))
    
    # Read path data and extract covariates
    print('Extracting covariates...')
    start = proc.time()
    print(input_points)
    input_data = read.csv(input_file) %>%
      mutate(X_coord = POINT_X,
             Y_coord = POINT_Y)
    point_data = st_as_sf(input_data, coords=c('X_coord', 'Y_coord'), crs=3338)
    point_extract = data.frame(point_data, raster::extract(raster_stack, point_data))
    end = proc.time() - start
    print(end[3])
    
    # Convert field names to standard
    point_extract = point_extract %>%
      dplyr::rename(fol_forb = Alphabet_fol_forb,
                    fol_gramnd = Alphabet_fol_graminoid,
                    fol_decshr = Alphabet_fol_decshr)
    
    # Export data as a csv
    st_write(point_extract, output_file, coords = FALSE)
    print(paste('Extraction iteration ', toString(count), ' out of ', toString(grid_length), ' completed.', sep=''))
    print('----------')
  } else {
    # Report that output already exists
    print(paste('Extraction ', toString(count), ' out of ', toString(grid_length), ' already exists.', sep = ''))
    print('----------')
  }
  # Increase count
  count = count + 1
}
