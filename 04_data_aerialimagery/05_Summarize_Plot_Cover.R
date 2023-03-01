# -*- coding: utf-8 -*-
# ---------------------------------------------------------------------------
# Summarize remote line-point intercept data
# Author: Amanda Droghini, Alaska Center for Conservation Science
# Last Updated: 2022-10-31
# Usage: Must be executed in R version 4.1.2.
# Description: "Summarize remote line-point intercept data" reads in delimited text files, compiles them into a single dataframe, summarizes data into a single, per-plot value of percent foliar cover, adds data on plot coordinates, and exports the final dataframe as a CSV.
# ---------------------------------------------------------------------------

rm(list=ls())

# Import required libraries
library(tidyverse)

# Set directories
drive = 'F:'
root_folder = 'ACCS_Work'
project_folder = file.path(drive,root_folder,"Projects","WildlifeEcology","Moose_AlphabetHills")
data_folder = file.path(project_folder,"Data","Data_Output","aerial_imagery_tables")
survey_folder = file.path(data_folder, "survey_data")

# Define inputs
surveys = list.files(survey_folder, full.names = TRUE, pattern = "*.csv")
input_coords = file.path(data_folder,"surveyed_plot_centers.csv")

# Define outputs
cover_output = file.path(data_folder, "ah_remote_lpi_salix_cover.csv")

# Create dataframe to store results
compiled_data = data.frame()

# Read in coordinate data
coords <- read_csv(input_coords)

# Iterate through each file (surveyed plot), add metadata fields, and compile into a single dataframe
# The loop will stop if any NULL values are encountered (would need to be addressed in GIS)
for (f in 1:length(surveys)) {
  text_file <- surveys[f]
  
  # Define metadata
  image_number <- str_split(string = (str_split(text_file,pattern="/")[[1]][10]), pattern = "_")[[1]][2]
  plot <- str_split(string = (str_split(text_file,pattern="/")[[1]][10]), pattern = "_")[[1]][3]
  
  cat("Processing image", image_number, "file", f, "of", length(surveys), "\n")
  
  # Read in data
  data <- read_csv(text_file, show_col_types = FALSE)
  
  data <- data %>%
    mutate(image_name = paste("DSC",image_number,sep="_"),
           image_number = image_number,
           plot_number = plot,
           point = row_number()) %>% 
    select(image_name,image_number,plot_number,point,Salix) 
  
  if (unique(complete.cases(data$Salix))!=TRUE){
    break
    
  } else {
    cat("With a total of", max(data$point), "points. No null values present. \n")
    compiled_data = rbind(data,compiled_data)
    
  }

}

# Summarize values into % foliar cover
cover_data <- compiled_data %>% 
  group_by(image_number,plot_number) %>% 
  summarize(total_points = max(point),
            total_Salix = sum(Salix)) %>% 
  mutate(cover_percent = total_Salix / total_points * 100,
         dead_status = FALSE,
         name_original = "Salix",
         name_adjudicated = "Salix",
         cover_type = "top foliar cover",
         site_visit_id = paste("DSC",image_number,plot_number,sep="_")) %>% 
  ungroup() %>% 
  select(site_visit_id,name_original,name_adjudicated,cover_type,dead_status,cover_percent)

# Append coordinates of plot center
coords <- coords %>% 
  mutate(site_visit_id = paste("DSC",image_number,plot_number,sep="_")) %>% 
  rename(longitude_dd = POINT_X,
         latitude_dd = POINT_Y) %>% 
  select(site_visit_id,longitude_dd,latitude_dd)

cover_data <- cover_data %>% 
  left_join(coords, by = "site_visit_id")

# Round % cover to 3 decimal points
cover_data$cover_percent <- round(cover_data$cover_percent, digits = 3)

# Export data
write_csv(cover_data,cover_output)
