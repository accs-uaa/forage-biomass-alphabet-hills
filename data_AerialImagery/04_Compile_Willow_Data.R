# -*- coding: utf-8 -*-
# ---------------------------------------------------------------------------
# Compile remote line-point intercept data
# Author: Amanda Droghini, Alaska Center for Conservation Science
# Last Updated: 2022-10-27
# Usage: Must be executed in R version 4.1.2.
# Description: "Compile remote line-point intercept data" reads in delimited text files and compiles them into a single dataframe, which is exported as a CSV for further analyses.
# ---------------------------------------------------------------------------

rm(list=ls())

# Import required libraries
library(tidyverse)

# Set directories
drive = 'F:'
root_folder = 'ACCS_Work'
project_folder = file.path(drive,root_folder,"Projects","WildlifeEcology","Moose_AlphabetHills")
data_folder = file.path(project_folder,"Data","Data_Output","image_tables")

# Define inputs
files = list.files(data_folder, full.names = TRUE, pattern = "*.csv")
compiled_data = data.frame()

for (f in 1:length(files)) {
  text_file <- files[f]
  
  # Define metadata
  image_number <- str_split(string = (str_split(text_file,pattern="/")[[1]][9]), pattern = "_")[[1]][2]
  line_number <- str_split(string = (str_split(text_file,pattern="/")[[1]][9]), pattern = "_")[[1]][3]
  
  cat("Processing image", image_number, "file", f, "of", length(files), "\n")
  
  # Read in data
  data <- read_csv(text_file, show_col_types = FALSE)
  
  data <- data %>% 
    rename(latitude_dd = POINT_Y,
           longitude_dd = POINT_X) %>% 
    mutate(image_name = paste("DSC",image_number,sep="_"),
           line = line_number,
           point = row_number()) %>% 
    select(image_name,line,point,longitude_dd,latitude_dd,Salix) 
  
  if (unique(complete.cases(data$Salix))!=TRUE){
    break
    
  } else {
    cat("With a total of", max(data$point), "points. No NULL values present. \n")
    compiled_data = rbind(data,compiled_data)
    
  }

}
