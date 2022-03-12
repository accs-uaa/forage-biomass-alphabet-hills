# -*- coding: utf-8 -*-
# ---------------------------------------------------------------------------
# Prepare Covariates from Aerial Imagery Metadata
# Author: Amanda Droghini, Alaska Center for Conservation Science
# Usage: Code chunks must be executed sequentially in R Studio or R Studio Server installation.
# Description: "Prepare Covariates from Aerial Imagery Metadata" extracts data in text files and a shapefile, and joins them into a dataframe. We'll use the variables in this dataframe to establish a statistical relationship between the original (text files) and geo-referenced (shapefile) centroid coordinates.
# ---------------------------------------------------------------------------

# Import required libraries
library(tidyverse)
library(sf)

# Set root directory
drive = 'D:'
root_folder = 'ACCS_Work'

# Define input folders
project_folder <- paste(drive,root_folder,"Projects/WildlifeEcology/Moose_AlphabetHills/Data", sep = "/")
image_folder <- paste(project_folder, 'Data_Input/imagery/aerial', sep = "/")
image_subfolders <- list.dirs(image_folder)
metadata_folders <- str_subset(image_subfolders, "METADATA")
unprocessed_folder <- paste(image_folder, 'unprocessed/Images_RGB', sep = "/")

# Define work geodatabase
work_geodatabase <- paste(drive,root_folder,"Projects/WildlifeEcology/Moose_AlphabetHills/Data/AlphabetHillsBrowseBiomass.gdb", sep = "/")

# Define input shapefile
layer_name <- 'AerialImagery_Centroids'

# Define output dataset
output_csv = paste(image_folder,
                   'AerialImagery_Metadata.csv',
                   sep = '/')

# Read in shapefile
centroids <- st_read(dsn=work_geodatabase,layer=layer_name)

# Extract metadata from text files ----

# List variables of interest in the metadata files
variables <- c("imageNumber","latitude","longitude","height","track","speed")

# List image name of all unprocessed images
# Remove extension from image name
unprocessed_images <- list.files(unprocessed_folder, pattern="\\.JPG$", full.names=FALSE)
image_names <- sub("\\.JPG", "", unprocessed_images)

# Create empty dataframe in which to store results
all_metadata <- data.frame(matrix(nrow = 0, ncol = length(variables)))
colnames(all_metadata) <- variables

# Loop through folders
# Within a folder, list all text files
for (m in 1:length(metadata_folders)) {
  current_folder <- metadata_folders[m]
  metadata_files <- list.files(current_folder, full.names = TRUE)
  
  # Loop through each text file within a folder
  # Read in text file
  # Split strings based on '=' sign
  # Characters to the left of the '=' are column names, characters to the right are the values
  # Select only variables of interest
  for (t in 1:length(metadata_files)) {
    cat("Processing", t, "of", length(metadata_files), "from folder", m, "of", length(metadata_folders), "\n")
    text_file <- metadata_files[t]
    data <- read.delim(text_file, header = FALSE, sep = "\t", dec = ".")
    data_split <- as.data.frame(str_split_fixed(data$V1, "=", 2))
    data_wide <- data_split %>% 
      pivot_wider(names_from = V1, values_from = V2) %>% 
      select(all_of(variables))
    all_metadata <- rbind(all_metadata,data_wide)
  }
}

# Add RowID column to match sequential numbering of files rather than ImageNumber, which starts back at 1 with every folder
all_metadata <- rowid_to_column(all_metadata)

# Append image name
all_metadata$fileName <- image_names

# Join metadata and shapefile ----
# Only georeferenced images will have a value for POINT_X and POINT_Y
metadata_join <- left_join(x=all_metadata, y=centroids,by = c("fileName" = "Image_Name")) %>% 
  select(-Shape) %>% 
  rename(georef_latitude = POINT_Y, georef_longitude = POINT_X)

# Export as CSV
write_csv(all_metadata, file = output_csv)

# Clean workspace
rm(list=ls())