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
field_folder = paste(project_folder,
                     'Field/Data',
                     sep = '/')
forage_folder = paste(project_folder,
                      'Data/Data_Input/forage',
                      sep = '/')

# Define input datasets
subplot_file = paste(field_folder,
                   '2021_AlphabetHills_Data.xlsx',
                   sep = '/')
bite_file = paste(forage_folder,
                  'processed',
                  'bite_mass.csv',
                  sep = '/')
cover_file = paste(forage_folder,
                   'unprocessed',
                   '05_vegetationcover_accsalphabethills2021.csv',
                   sep = '/')
site_visit_file = paste(forage_folder,
                        'unprocessed',
                        '03_sitevisit_accsalphabethills2021.csv',
                        sep = '/')
site_file = paste(forage_folder,
                  'unprocessed',
                  '02_site_accsalphabethills2021.csv',
                  sep = '/')

# Define output dataset
output_file = paste(forage_folder,
                    'processed',
                    'plot_mass.csv',
                    sep = '/')

# Set repository directory
repository = 'C:/Users/timmn/Documents/Repositories/akveg-database'

# Import required libraries.
library(dplyr)
library(ggplot2)
library(readxl)
library(RPostgres)
library(tidyr)

# Import database connection function
connection_script = paste(repository,
                          'package_DataProcessing',
                          'connectDatabasePostGreSQL.R',
                          sep = '/')
source(connection_script)

# Create a connection to the AKVEG PostgreSQL database
authentication = paste(drive,
                       root_folder,
                       'Administrative/Credentials/akveg_build/authentication_akveg_build.csv',
                       sep = '/')
database_connection = connect_database_postgresql(authentication)

# Read constraints into data frames from AKVEG
query_taxon = 'SELECT * FROM taxon_all'
taxon_data = as_tibble(dbGetQuery(database_connection, query_taxon))

# Read input data
subplot_original = read_xlsx(subplot_file, sheet = 'Subplots')
bite_original = read.csv(bite_file)
site_data = read.csv(site_file)
site_visit_data = read.csv(site_visit_file)
cover_original = read.csv(cover_file)

# Calculate subplot bite summary
subplot_data = subplot_original %>%
  rename(site_code = site) %>%
  mutate(site_code = paste('ALPH', site_code, sep = '')) %>%
  mutate(large = large_strip + large_clip) %>%
  group_by(site_code, code) %>%
  summarize(cover_sb = mean(cover),
            height = case_when(is.na(sort(height, TRUE)[4]) ~ max(height),
                               TRUE ~ sort(height, TRUE)[2]),
            small = mean(small),
            medium = mean(medium),
            large = mean(large)) %>%
  mutate(area_sb = (cover_sb/100) * 0.25) %>%
  # Join accepted codes to codes
  left_join(taxon_data, by = c('code' = 'taxon_code')) %>%
  dplyr::select(site_code, taxon_accepted_code, cover_sb, area_sb, height,
                small, medium, large)

# Merge Betula shrub subplot data
betula_subplot = subplot_data %>%
  filter(taxon_accepted_code == 'betgla' |
           taxon_accepted_code == 'betnansexi') %>%
  group_by(site_code) %>%
  summarize(cover_sb = sum(cover_sb),
            area_sb = sum(area_sb),
            height = max(height),
            small = sum(small),
            medium = sum(medium),
            large = sum(large)) %>%
  mutate(taxon_accepted_code = 'betshr')

# Replace subplot data with Betula shrub summary
subplot_data = subplot_data %>%
  filter(taxon_accepted_code != 'betgla' &
           taxon_accepted_code != 'betnansexi')
subplot_data = rbind(subplot_data, betula_subplot)

# Prepare cover data
cover_data = cover_original %>%
  filter(dead_status != 'TRUE') %>%
  # Join accepted codes to name_adjudicated
  left_join(taxon_data, by = c('name_adjudicated' = 'taxon_name')) %>%
  # Join site visit data
  left_join(site_visit_data, by = 'site_visit_id') %>%
  dplyr::select(site_code, taxon_accepted_code, cover_percent)

# Merge Betula shrub cover data
betula_cover = cover_data %>%
  filter(taxon_accepted_code == 'betgla' |
         taxon_accepted_code == 'betnansexi') %>%
  group_by(site_code) %>%
  summarize(cover_percent = sum(cover_percent)) %>%
  mutate(taxon_accepted_code = 'betshr')

# Replace cover data with Betula shrub summary
cover_data = cover_data %>%
  filter(taxon_accepted_code != 'betgla' &
           taxon_accepted_code != 'betnansexi')
cover_data = rbind(cover_data, betula_cover)
  
# Join subplot data and cover data
plot_bites = cover_data %>%
  left_join(subplot_data, by = c('site_code', 'taxon_accepted_code')) %>%
  # Calculate plot attributes
  mutate(area_pl = (cover_percent/100) * 490.87) %>%
  mutate(plot_small = ((small/area_sb) * area_pl) / 490.87) %>%
  mutate(plot_medium = ((medium/area_sb) * area_pl) / 490.87) %>%
  mutate(plot_large = ((large/area_sb) * area_pl) / 490.87) %>%
  select(site_code, taxon_accepted_code, cover_percent, height,
         plot_small, plot_medium, plot_large)

# Create wide form bite mass data
bite_data = bite_original %>%
  pivot_wider(names_from = bite_size, values_from = bite_mass) %>%
  dplyr::select(-taxon_name, -large_clip) %>%
  rename(bite_mass_small = small,
         bite_mass_medium = medium,
         bite_mass_large = large_strip)

# Calculate per plot wet mass summary
plot_mass = plot_bites %>%
  # Join bite mass data
  left_join(bite_data, by = 'taxon_accepted_code') %>%
  # Calculate bite mass per square meter
  mutate(mass_small_g_per_m2 = plot_small * bite_mass_small) %>%
  mutate(mass_medium_g_per_m2 = plot_medium * bite_mass_medium) %>%
  mutate(mass_large_g_per_m2 = plot_large * bite_mass_large) %>%
  dplyr::select(site_code, taxon_accepted_code, cover_percent, height,
                mass_small_g_per_m2, mass_medium_g_per_m2, mass_large_g_per_m2)

# Export output as csv file
write.csv(plot_mass, file = output_file, fileEncoding = 'UTF-8', row.names = FALSE)