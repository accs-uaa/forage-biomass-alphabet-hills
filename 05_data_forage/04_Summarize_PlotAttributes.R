# -*- coding: utf-8 -*-
# ---------------------------------------------------------------------------
# Summarize available biomass per plot
# Author: Timm Nawrocki
# Last Updated: 2023-04-18
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
field_file = paste(field_folder,
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
subplot_file = paste(forage_folder,
                     'processed',
                     'subplot_mass.csv',
                     sep = '/')
plot_file = paste(forage_folder,
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
subplot_original = read_xlsx(field_file, sheet = 'Subplots')
bite_original = read.csv(bite_file)
site_data = read.csv(site_file)
site_visit_data = read.csv(site_visit_file)
cover_original = read.csv(cover_file)

# Create wide form bite mass data
bite_data = bite_original %>%
  pivot_wider(names_from = bite_size, values_from = bite_mass) %>%
  dplyr::select(-taxon_name, -large_clip) %>%
  rename(bite_mass_small = small,
         bite_mass_medium = medium,
         bite_mass_large = large_strip) %>%
  select(-whole)
bite_data = bite_data %>%
  # Fill missing data for betken using betneo data
  add_row(taxon_accepted_code = 'betken',
          bite_mass_large = bite_data$bite_mass_large[[which(
            bite_data$taxon_accepted_code == 'betneo')]],
          bite_mass_medium = bite_data$bite_mass_medium[[which(
            bite_data$taxon_accepted_code == 'betneo')]],
          bite_mass_small = bite_data$bite_mass_small[[which(
            bite_data$taxon_accepted_code == 'betneo')]]) %>%
  # Fill missing data for salala using salgla data
  mutate(bite_mass_large = case_when(taxon_accepted_code == 'salala' ~
                                       bite_data$bite_mass_large[[which(
                                         bite_data$taxon_accepted_code == 'salgla')]],
                                     TRUE ~ bite_mass_large))

# Calculate subplot biomass summary
subplot_data = subplot_original %>%
  rename(site_code = site) %>%
  mutate(taxon_accepted_code = case_when(code == 'betgla' ~ 'betshr',
                                         code == 'betnansexi' ~ 'betshr',
                                         code == 'betn×g' ~ 'betcfo',
                                         TRUE ~ code)) %>%
  mutate(site_code = paste('ALPH', site_code, sep = '')) %>%
  mutate(large = large_strip + large_clip) %>%
  # Calculate biomass per bite size
  left_join(bite_data, by = 'taxon_accepted_code') %>%
  mutate(biomass_large = large * bite_mass_large) %>%
  mutate(biomass_medium = medium * bite_mass_medium) %>%
  mutate(biomass_small = small * bite_mass_small) %>%
  mutate(biomass_total = biomass_large + biomass_medium + biomass_small) %>%
  select(site_code, subplot, code, taxon_accepted_code, cover, height, biomass_total)
  
# Summarize subplot biomass
subplot_summary = subplot_data %>%
  group_by(site_code, taxon_accepted_code) %>%
  summarize(cover_mean_sb = mean(cover),
            height_max = case_when(is.na(sort(height, TRUE)[4]) ~ max(height),
                               TRUE ~ sort(height, TRUE)[2]),
            height_mean = mean(height),
            biomass_mean_sb = mean(biomass_total),
            subplot_n = n()) %>%
  select(site_code, taxon_accepted_code, cover_mean_sb, height_max,
         height_mean, biomass_mean_sb, subplot_n)

# Prepare cover data
cover_data = cover_original %>%
  filter(dead_status != 'TRUE') %>%
  filter(name_adjudicated != 'Picea mariana' &
           name_adjudicated != 'Picea glauca' &
           name_adjudicated != 'Salix pseudomyrsinites') %>%
  # Join accepted codes to name_adjudicated
  left_join(taxon_data, by = c('name_adjudicated' = 'taxon_name')) %>%
  # Join site visit data
  left_join(site_visit_data, by = 'site_visit_id') %>%
  rename(cover_pl = cover_percent) %>%
  select(site_code, taxon_accepted_code, cover_pl)
# Merge Betula shrub cover data
betula_cover = cover_data %>%
  filter(taxon_accepted_code == 'betgla' |
         taxon_accepted_code == 'betnansexi') %>%
  group_by(site_code) %>%
  summarize(cover_pl = sum(cover_pl)) %>%
  mutate(taxon_accepted_code = 'betshr')
# Replace cover data with Betula shrub summary
cover_data = cover_data %>%
  filter(taxon_accepted_code != 'betgla' &
           taxon_accepted_code != 'betnansexi')
cover_data = rbind(cover_data, betula_cover)
  
# Calculate plot biomass density
plot_mass = cover_data %>%
  left_join(subplot_summary, by = c('site_code', 'taxon_accepted_code')) %>%
  # Calculate plot biomass density
  mutate(biomass_density_pl = ((biomass_mean_sb/(cover_mean_sb * 0.25))*(cover_pl * 490.87))/490.87) %>%
  select(site_code, taxon_accepted_code, cover_pl, cover_mean_sb, height_max,
         height_mean, biomass_mean_sb, biomass_density_pl, subplot_n) %>%
  filter(!is.na(subplot_n))

# Export outputs as csv files
write.csv(subplot_data, file = subplot_file, fileEncoding = 'UTF-8', row.names = FALSE)
write.csv(plot_mass, file = plot_file, fileEncoding = 'UTF-8', row.names = FALSE)
