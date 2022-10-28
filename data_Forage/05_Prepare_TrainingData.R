# -*- coding: utf-8 -*-
# ---------------------------------------------------------------------------
# Summarize available biomass per plot
# Author: Timm Nawrocki
# Last Updated: 2022-10-25
# Usage: Should be executed in R 4.1.0+.
# Description: "Summarize available biomass per plot" summarizes the plot level biomass available to moose per species and bite size using the generalized relationships between bite number and mass.
# ---------------------------------------------------------------------------

# Set root directory
drive = 'N:'
root_folder = 'ACCS_Work'

# Define input folders
project_folder = paste(drive,
                       root_folder,
                       'Projects/WildlifeEcology/Moose_AlphabetHills',
                       sep = '/')
forage_folder = paste(project_folder,
                      'Data/Data_Input/forage',
                      sep = '/')

# Define input datasets
extracted_file = paste(forage_folder,
                       'processed',
                   'sites_extracted.csv',
                   sep = '/')
mass_file = paste(forage_folder,
                  'processed',
                  'plot_mass.csv',
                  sep = '/')

# Define target list
target_list = c('alnalnsfru',
                'betcfo',
                'betneo',
                'betshr',
                'chaang',
                'popbal',
                'poptre',
                'salala',
                'salarb',
                'salbarc',
                'salbeb',
                'salgla',
                'salpul',
                'salric',
                'salsco')

# Import required libraries.
library(dplyr)
library(ggplot2)
library(readxl)
library(RPostgres)
library(tidyr)

# Read input data
extracted_original = read.csv(extracted_file)

#### EXPORT PER TAXON SUMMARIES

# Loop through each target in target list to produce output training data
for (target in target_list) {
  # Define output datasets
  training_file = paste(forage_folder,
                        'processed',
                        paste('train_', target, '.csv', sep = ''),
                        sep = '/')
  metadata_file = paste(forage_folder,
                        'processed',
                        paste('metadata_', target, '.csv', sep = ''),
                        sep = '/')
  
  # Split mass data by taxon
  mass_original = read.csv(mass_file) %>%
    filter(taxon_accepted_code == target) %>%
    # Replace na values
    mutate(cover_percent = replace_na(cover_percent, 0)) %>%
    mutate(height = replace_na(height, 0)) %>%
    mutate(mass_small_g_per_m2 = replace_na(mass_small_g_per_m2, 0)) %>%
    mutate(mass_medium_g_per_m2 = replace_na(mass_medium_g_per_m2, 0)) %>%
    mutate(mass_large_g_per_m2 = replace_na(mass_large_g_per_m2, 0))
  
  # Calculate subplot bite summary
  train_data = extracted_original %>%
    full_join(mass_original, by = 'site_code') %>%
    # Replace na values
    mutate(cover_percent = replace_na(cover_percent, 0)) %>%
    mutate(height = replace_na(height, 0)) %>%
    mutate(mass_small_g_per_m2 = replace_na(mass_small_g_per_m2, 0)) %>%
    mutate(mass_medium_g_per_m2 = replace_na(mass_medium_g_per_m2, 0)) %>%
    mutate(mass_large_g_per_m2 = replace_na(mass_large_g_per_m2, 0)) %>%
    # Calculate total biomass
    mutate(mass_g_per_m2 = mass_small_g_per_m2 + mass_medium_g_per_m2 + mass_large_g_per_m2)
  
  # Create metadata
  metadata = train_data %>%
    filter(mass_g_per_m2 != 0) %>%
    group_by(taxon_accepted_code) %>%
    summarize(cover_median = median(cover_percent),
              cover_mean = mean(cover_percent),
              height_median = median(height),
              height_mean = mean(height),
              mass_median = median(mass_g_per_m2),
              mass_mean = mean(mass_g_per_m2),
              n_sites = n())
  
  # Export output files as csv
  write.csv(train_data, file = training_file, fileEncoding = 'UTF-8', row.names = FALSE)
  write.csv(metadata, file = metadata_file, fileEncoding = 'UTF-8', row.names = FALSE)
}

#### EXPORT WILLOW SUMMARY

# Define output datasets
training_file = paste(forage_folder,
                      'processed',
                      paste('train_', 'salix', '.csv', sep = ''),
                      sep = '/')
metadata_file = paste(forage_folder,
                      'processed',
                      paste('metadata_', 'salix', '.csv', sep = ''),
                      sep = '/')

# Split mass data by taxon
mass_original = read.csv(mass_file) %>%
  filter(taxon_accepted_code != 'alnalnsfru' &
           taxon_accepted_code != 'betcfo' &
           taxon_accepted_code != 'betneo' &
           taxon_accepted_code != 'betshr' &
           taxon_accepted_code != 'chaang' &
           taxon_accepted_code != 'popbal' &
           taxon_accepted_code != 'poptre' &
           taxon_accepted_code != 'picmar' &
           taxon_accepted_code != 'picgla') %>%
  mutate(taxon_accepted_code = 'salix') %>%
  # Replace na values
  mutate(cover_percent = replace_na(cover_percent, 0)) %>%
  mutate(height = replace_na(height, 0)) %>%
  mutate(mass_small_g_per_m2 = replace_na(mass_small_g_per_m2, 0)) %>%
  mutate(mass_medium_g_per_m2 = replace_na(mass_medium_g_per_m2, 0)) %>%
  mutate(mass_large_g_per_m2 = replace_na(mass_large_g_per_m2, 0)) %>%
  # Summarize data for all willows
  group_by(site_code, taxon_accepted_code) %>%
  summarize(cover_percent = sum(cover_percent),
            height = max(height),
            mass_small_g_per_m2 = sum(mass_small_g_per_m2),
            mass_medium_g_per_m2 = sum(mass_medium_g_per_m2),
            mass_large_g_per_m2 = sum(mass_large_g_per_m2),
            n_willow = n())

# Calculate subplot bite summary
train_salix = extracted_original %>%
  full_join(mass_original, by = 'site_code') %>%
  # Replace na values
  mutate(cover_percent = replace_na(cover_percent, 0)) %>%
  mutate(height = replace_na(height, 0)) %>%
  mutate(mass_small_g_per_m2 = replace_na(mass_small_g_per_m2, 0)) %>%
  mutate(mass_medium_g_per_m2 = replace_na(mass_medium_g_per_m2, 0)) %>%
  mutate(mass_large_g_per_m2 = replace_na(mass_large_g_per_m2, 0)) %>%
  mutate(n_willow = replace_na(n_willow, 0)) %>%
  # Calculate total biomass
  mutate(mass_g_per_m2 = mass_small_g_per_m2 + mass_medium_g_per_m2 + mass_large_g_per_m2)

# Create metadata
metadata = train_salix %>%
  filter(mass_g_per_m2 != 0) %>%
  group_by(taxon_accepted_code) %>%
  summarize(cover_median = median(cover_percent),
            cover_mean = mean(cover_percent),
            height_median = median(height),
            height_mean = mean(height),
            mass_median = median(mass_g_per_m2),
            mass_mean = mean(mass_g_per_m2),
            n_sites = n())

# Export output files as csv
write.csv(train_salix, file = training_file, fileEncoding = 'UTF-8', row.names = FALSE)
write.csv(metadata, file = metadata_file, fileEncoding = 'UTF-8', row.names = FALSE)
