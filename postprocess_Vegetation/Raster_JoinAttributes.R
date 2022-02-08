# ---------------------------------------------------------------------------
# Prepare raster attribute table
# Author: Timm Nawrocki, Alaska Center for Conservation Science
# Last Updated: 2022-01-20
# Usage: Script should be executed in R 4.1.0+.
# Description: "Prepare raster attribute table" creates a csv raster attribute table that can replace the segment raster attribute table after conversion to dbf.
# ---------------------------------------------------------------------------

# Set root directory
drive = 'N:'
root_folder = 'ACCS_Work'

# Set round date
round_date = 'round_20220120'

# Define input folders
project_folder = paste(drive,
                       root_folder,
                       'Projects/WildlifeEcology/Moose_AlphabetHills/Data',
                       sep = '/')
table_folder = paste(project_folder,
                     'Data_Output/predicted_tables',
                     round_date,
                     sep = '/')
raster_folder = paste(project_folder,
                      'Data_Output/predicted_rasters',
                      round_date,
                      sep = '/')

# Define input datasets
predicted_table = paste(table_folder,
                        'predicted_points.csv',
                        sep = '/')
raster_table = paste(raster_folder,
                     'Alphabet_Segments_Test.csv',
                     sep = '/')

# Define output datasets
output_file = paste(raster_folder,
                    'Alphabet_Vegetation_Join.csv',
                    sep = '/')

# Import libraries
library(dplyr)
library(tidyr)

# Read data
predict_data = read.csv(predicted_table)
raster_data = read.csv(raster_table)

# Join predictions to raster table
output_data = raster_data %>%
  rename(Value = 1) %>%
  left_join(predict_data, by = c('Value' = 'gridcode')) %>%
  rename(Prediction = prediction) %>%
  mutate(Prediction = replace_na(Prediction, -999)) %>%
  select(Value, Count, Prediction)

# Export table
write.csv(output_data, file = output_file, fileEncoding = 'UTF-8', row.names = FALSE)