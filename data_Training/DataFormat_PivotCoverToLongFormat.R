# -*- coding: utf-8 -*-
# ---------------------------------------------------------------------------
# Pivot Line-Point Intercept Data to Long Format
# Author: Timm Nawrocki
# Last Updated: 2022-03-30
# Usage: Should be executed in R 4.0.0+.
# Description: "Pivot Line-Point Intercept Data to Long Format" transforms the cover data table from the grid point intercept data entry form to contain a single taxon observation per row. In the resulting table, each row represents a single site-line-point-layer.
# ---------------------------------------------------------------------------

# Set root directory
drive = 'N:'
root_folder = 'ACCS_Work'

# Define input folders
project_folder = paste(drive,
                       root_folder,
                       'Projects/WildlifeEcology/Moose_AlphabetHills',
                       sep = '/')
field_folder = paste(project_folder,
                     'Field/Data',
                     sep = '/')

# Define input dataset
input_file = paste(field_folder,
                   'unprocessed/2021_AlphabetHills_Data.xlsx',
                   sep = '/')
cover_sheet = 'cover'

# Define output dataset
output_file = paste(field_folder,
                    'processed/2021_AlphabetHills_PlotCover.xlsx')

# Import required libraries.
library(dplyr)
library(readxl)
library(writexl)
library(tidyr)

# Define layer fields
layers = c('Layer1', 'Layer2')

# Read cover data from excel
cover_data = read_xlsx(input_file,
                       sheet = cover_sheet)

# Transform cover data
cover_data_long = cover_data %>%
  select(c(site, line, point, layers)) %>%
  pivot_longer(cols = layers, names_to = 'layer') %>%
  drop_na() %>%
  mutate(Layer=replace(Layer, which(Layer == 'Layer1'), 1)) %>%
  mutate(Layer=replace(Layer, which(Layer == 'Layer2'), 2)) %>%
  rename(Abbreviation = value)

# Convert layer to integer
cover_data_long$layer = as.integer(cover_data_long$layer)

# Summarize data by site and taxon
absolute_cover = cover_data_long %>%
  group_by(Site, Observation) %>%
  summarize(coverTotal = n()) %>%
  rename(siteCode = Site) %>%
  rename(nameOriginal = Observation) %>%
  mutate(coverTotal = round((coverTotal/150)*100, digits = 1))

# Export long format data as a new excel file
write_xlsx(cover_data_long,
           path = output_file)