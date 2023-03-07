# -*- coding: utf-8 -*-
# ---------------------------------------------------------------------------
# Merge existing vegetation type rasters
# Author: Timm Nawrocki, Alaska Center for Conservation Science
# Last Updated: 2023-03-04
# Usage: Code chunks must be executed sequentially in R Studio or R Studio Server installation.
# Description: "Merge existing vegetation type rasters" merges the predicted grid rasters into a single output raster.
# ---------------------------------------------------------------------------

# Define round date
round_date = 'round_20220607'

# Set root directory
drive = 'N:'
root_folder = 'ACCS_Work'

# Set target taxa list
taxa_list = c('alnalnsfru', 'betshr', 'chaang', 'salpul', 'salix')

# Define input folders
project_folder = paste(drive,
                       root_folder,
                       'Projects/WildlifeEcology/Moose_AlphabetHills/Data',
                       sep = '/')

# Import libraries
library(raster)

for (taxon in taxa_list) {
  # Define folder name
  folder_name = paste('for_', taxon, sep = '')
  
  # Define input folder
  raster_folder = paste(project_folder,
                        'Data_Output/predicted_rasters',
                        round_date,
                        folder_name,
                        sep = '/')
  
  # Define output folder
  merge_folder = paste(project_folder,
                       'Data_Output/output_rasters',
                       round_date,
                       'forage_biomass',
                       sep = '/')
  
  # Define output file
  output_raster = paste(merge_folder, '/',
                        'Alphabet_Forage_',
                        taxon,
                        '.tif',
                        sep = '')
  
  # Generate output raster if it does not already exist
  if (!file.exists(output_raster)) {
    
    # Generate list of raster img files from input folder
    raster_files = list.files(path = raster_folder,
                              pattern = paste('..*.tif$', sep = ''),
                              full.names = TRUE)
    count = length(raster_files)
    
    # Convert list of files into list of raster objects
    start = proc.time()
    print(paste('Compiling ', toString(count), ' rasters', '...'))
    raster_objects = lapply(raster_files, raster)
    # Add function and filename attributes to list
    raster_objects$fun = max
    raster_objects$filename = output_raster
    raster_objects$overwrite = TRUE
    raster_objects$datatype = 'INT2S'
    raster_objects$progress = 'text'
    raster_objects$format = 'GTiff'
    raster_objects$options = c('TFW=YES')
    end = proc.time() - start
    print(paste('Completed in ', end[3], ' seconds.', sep = ''))
    
    # Merge rasters
    start = proc.time()
    print(paste('Merging ', toString(count), ' rasters', '...'))
    merged_raster = do.call(mosaic, raster_objects)
    end = proc.time() - start
    print(paste('Completed in ', end[3], ' seconds.', sep = ''))
  } else {
    print('Raster already exists.')
  }
}




