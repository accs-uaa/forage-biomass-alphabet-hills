# -*- coding: utf-8 -*-
# ---------------------------------------------------------------------------
# Convert surficial features predictions to rasters
# Author: Timm Nawrocki, Alaska Center for Conservation Science
# Last Updated: 2023-02-22
# Usage: Script must be executed using R 4.2.1+.
# Description: "Convert surficial features predictions to rasters" processes the predicted tables into predicted rasters by grid.
# ---------------------------------------------------------------------------

# Define round date and target
round_date = 'round_20220607'

# Set root directory
drive = 'N:'
root_folder = 'ACCS_Work'

# Define input folders
project_folder = paste(drive,
                       root_folder,
                       'Projects/WildlifeEcology/Moose_AlphabetHills/Data',
                       sep = '/')

# Define folder containing segment rasters
segment_folder = paste(project_folder,
                       'Data_Input/imagery/segments/gridded',
                       sep = '/')

# Define geodatabase storing segment polygons
segment_geodatabase = paste(project_folder,
                            'AlphabetHills_Segments.gdb',
                            sep = '/')

# Define input folder
prediction_folder = paste(project_folder,
                          'Data_Output/predicted_tables',
                          round_date,
                          'surficial_features',
                          sep = '/')
# Define output folder
raster_folder = paste(project_folder,
                      'Data_Output/predicted_rasters',
                      round_date,
                      sep = '/')

# Import libraries
library(dplyr)
library(fasterize)
library(raster)
library(sf)
library(stringr)

# Define grids
grid_list = c('A2', 'A3', 'A4', 'A5', 'A6',
             'B1', 'B2', 'B3', 'B4', 'B5', 'B6', 'B7',
             'C1', 'C2', 'C3', 'C4', 'C5', 'C6', 'C7',
             'D1', 'D2', 'D3', 'D4', 'D5', 'D6', 'D7',
             'E1', 'E2', 'E3', 'E4', 'E5', 'E6')
prediction_length = length(grid_list)

#### CONVERT SURFICIAL FEATURES

# Loop through each grid and convert predictions to raster
count = 1
for (grid in grid_list) {
  # Define output folder
  output_folder = paste(raster_folder, 'surficial_features',  sep = '/')
  
  # Define input and output data
  input_file = paste(prediction_folder, '/', grid, '.csv', sep = '')
  segment_file = paste(segment_folder, '/', grid, '.tif', sep = '')
  segment_feature = paste('polygons_', grid, sep = '')
  output_raster = paste(output_folder, '/', grid, '.tif', sep='')
  
  # Process raster if it does not already exist
  if (!file.exists(output_raster)) {
    start = proc.time()
    # Import data
    input_data = read.csv(input_file)
    segment_raster = raster(segment_file)
    segment_polygon = st_read(dsn = segment_geodatabase, layer = segment_feature)
    
    # Bind predicted points to segment polygons and create value field
    segment_predictions = segment_polygon %>%
      dplyr::left_join(input_data, by = 'segment_id') %>%
      rename(surface = physiography)
    
    # Rasterize the polygon
    predicted_raster = fasterize(segment_predictions,
                                 segment_raster,
                                 field = 'surface',
                                 fun = 'first')
    
    # Export raster
    rf = writeRaster(predicted_raster,
                     filename=output_raster,
                     format="GTiff",
                     overwrite=TRUE)
    end = proc.time() - start
    print(end[3])
    # Print output
    print(paste('Conversion iteration ',
                toString(count),
                ' out of ',
                toString(prediction_length),
                ' completed...',
                sep=''))
    print('----------')
  } else {
    print(paste('Raster ',
                toString(count),
                ' out of ',
                toString(prediction_length),
                ' already exists.',
                sep = ''))
    print('----------')
  }
  count = count + 1
}

#### CONVERT SURFICIAL FEATURE PROBABILITIES

# Define class numbers and labels
class_list = c('class_01', 'class_02', 'class_03', 'class_04',
              'class_05', 'class_06', 'class_07', 'class_08')
label_list = c('burned', 'barren', 'drainage', 'riparian',
               'floodplain', 'water', 'uplandlowland', 'aspen')

# Create probability raster for each class
for (i in seq(1, length(class_list), 1)) {
  # Define class number and label
  class_number = class_list[i]
  class_label = label_list[i]
  
  # Define output folder
  output_folder = paste(raster_folder, '/', 'sf_', class_label, sep = '')
  
  # Create raster directory if it does not exist
  if (!file.exists(output_folder)) {
    dir.create(output_folder)
  }
  
  # Loop through each grid and convert predictions to raster
  count = 1
  for (grid in grid_list) {
    # Define input and output data
    input_file = paste(prediction_folder, '/', grid, '.csv', sep = '')
    segment_file = paste(segment_folder, '/', grid, '.tif', sep = '')
    segment_feature = paste('polygons_', grid, sep = '')
    output_raster = paste(output_folder, '/', grid, '.tif', sep='')
    
    # Process raster if it does not already exist
    if (!file.exists(output_raster)) {
      start = proc.time()
      # Import data
      input_data = read.csv(input_file)
      segment_raster = raster(segment_file)
      segment_polygon = st_read(dsn = segment_geodatabase, layer = segment_feature)
    
      # Bind predicted points to segment polygons and create value field
      segment_predictions = segment_polygon %>%
        dplyr::left_join(input_data, by = 'segment_id') %>%
        mutate(raster_value = as.integer(!!as.name(class_number) * 1000))
    
      # Rasterize the polygon
      predicted_raster = fasterize(segment_predictions,
                                   segment_raster,
                                   field = 'raster_value',
                                   fun = 'first')
    
      # Export raster
      rf = writeRaster(predicted_raster,
                       filename=output_raster,
                       format="GTiff",
                       overwrite=TRUE)
      end = proc.time() - start
      print(end[3])
      # Print output
      print(paste('Conversion iteration ',
                  toString(count),
                  ' out of ',
                  toString(prediction_length),
                  ' completed...',
                  sep=''))
      print('----------')
    } else {
      print(paste('Raster ',
                  toString(count),
                  ' out of ',
                  toString(prediction_length),
                  ' already exists.',
                  sep = ''))
      print('----------')
    }
    count = count + 1
  }
}