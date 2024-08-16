# -*- coding: utf-8 -*-
# ---------------------------------------------------------------------------
# Summarize plot absolute foliar cover
# Author: Timm Nawrocki, Amanda Droghini
# Last Updated: 2024-08-14
# Usage: Should be executed in R 4.1.0+.
# Description: "Summarize plot absolute foliar cover" transforms the line-point intercept hits to absolute foliar cover.
# ---------------------------------------------------------------------------

# Import required libraries.
library(dplyr)
library(fs)
library(lubridate)
library(purrr)
library(readr)
library(readxl)
library(RPostgres)
library(tibble)
library(tidyr)

# Set root directory
drive = 'D:'
root_folder = 'ACCS_Work'

# Set repository directory
akveg_repository = path('C:', root_folder, 'Repositories/akveg-database')
credentials_folder = path('C:', root_folder, 'Credentials/akveg_private_read')

# Define input folders
project_folder = path(drive, root_folder,
                      'Projects/WildlifeEcology/Moose_AlphabetHills')

# Define input files
taxa_file = path(akveg_repository, '05_queries/analysis/00_taxon_query.sql')
cover_input = path(project_folder, 'Field/Data/2021_AlphabetHills_Data.xlsx')
cover_sheet = 'Cover'
additional_sheet = 'AdditionalCover'
site_sheet = 'Site'

# Define output dataset
cover_output = path(project_folder, 'Data/Data_Input/forage/unprocessed/05_vegetationcover_accsalphabethills2021.csv')

#### QUERY AKVEG DATABASE
####------------------------------

# Import database connection function
connection_script = path(akveg_repository, 'package_DataProcessing', 'connect_database_postgresql.R')
source(connection_script)

# Create a connection to the AKVEG PostgreSQL database
authentication = path(credentials_folder, 'authentication_akveg_private.csv')
database_connection = connect_database_postgresql(authentication)

# Read taxonomy standard from AKVEG Database
taxa_query = read_file(taxa_file)
taxa_data = as_tibble(dbGetQuery(database_connection, taxa_query))

#### PROCESS COVER DATA
####------------------------------

# Read cover data from excel
cover_data = read_xlsx(cover_input,
                       sheet = cover_sheet)
site_data = read_xlsx(cover_input,
                      sheet = site_sheet) %>%
  # Format site visit codes
  mutate(site_visit_code = case_when(day(date) < 10 ~
                                       paste('ALPH', site, '_', year(date), '0', month(date), '0', day(date), sep = ''),
                                     TRUE ~ paste('ALPH', site, '_', year(date), '0', month(date), day(date), sep = '')))

# Transform cover data
cover_data_long = cover_data %>%
  pivot_longer(cols = all_of(c('layer1', 'layer2')), names_to = 'layer') %>%
  # Add dead_status variable
  mutate(dead_status = case_when(l1dead == 1 & layer == "layer1" ~ TRUE,
                                 l2dead == 1 & layer == "layer2" ~ TRUE,
                                 TRUE ~ FALSE)) %>% 
  # Rename value and remove none
  rename(code = value) %>%
  filter(code != 'none') %>%
  # Select final fields
  select(site, code, dead_status)

# Prepare visual estimate cover data
visual_cover = read_xlsx(cover_input,
                         sheet = additional_sheet) %>%
  # Fix non-standard codes
  mutate(code = case_when(code == 'salbar' ~ 'salbarc',
                          code == 'alnalnf' ~ 'alnalnsfru',
                          code == 'betnane' ~ 'betnansexi',
                          code == 'betnxg' ~ 'betcfo',
                          code == 'betn×g' ~ 'betcfo',
                          code == 'poptre-sap' ~ 'poptre',
                          TRUE ~ code)) %>%
  # Add missing data
  mutate(cover_type = 'absolute foliar cover',
         dead_status = as.logical("FALSE"))

# Summarize data by site and taxon
absolute_cover = cover_data_long %>%
  # Fix non-standard codes
  mutate(code = case_when(code == 'salbar' ~ 'salbarc',
                          code == 'alnalnf' ~ 'alnalnsfru',
                          code == 'betnane' ~ 'betnansexi',
                          code == 'betnxg' ~ 'betcfo',
                          code == 'betn×g' ~ 'betcfo',
                          code == 'poptre-sap' ~ 'poptre',
                          TRUE ~ code)) %>%
  # Calculate absolute cover
  group_by(site, code, dead_status) %>%
  mutate(cover = round((n()/120)*100, digits = 3)) %>%
  mutate(cover_type = 'absolute foliar cover') %>%
  # Enforce distict observations
  distinct() %>%
  # Remove cover values adjusted by visual estimate
  anti_join(visual_cover, join_by('site', 'code', 'dead_status'))

# Create presence data
presence_data = rbind(absolute_cover, visual_cover) %>%
  # Join accepted names to codes
  left_join(taxa_data, by=c('code'='code_akveg')) %>%
  rename(name_original = taxon_name) %>%
  rename(name_adjudicated = taxon_accepted) %>%
  # Rename to match naming conventions in minimum standards
  rename(cover_percent = cover) %>% 
  ungroup() %>%
  # Join site data
  left_join(site_data, by = 'site') %>%
  # Select output fields
  select(site_visit_code, name_original, name_adjudicated, cover_type, dead_status, cover_percent)

#### ADD EXPLICIT ABSENCES
####------------------------------

# Create site visit list
site_visit_list = presence_data %>%
  distinct(site_visit_code) %>%
  pull(site_visit_code)

# Create taxa target list
target_list = presence_data %>%
  distinct(name_adjudicated) %>%
  pull(name_adjudicated)

# Create absence data frame
target_column = as_tibble(list_c(replicate(length(site_visit_list), list(target_list)))) %>%
  rename(name_adjudicated = value) %>%
  arrange(name_adjudicated)
site_visit_column = as_tibble(list_c(replicate(length(target_list), list(site_visit_list)))) %>%
  rename(site_visit_code = value)
absence_data = cbind(site_visit_column, target_column) %>%
  mutate(name_original = name_adjudicated,
         cover_type = 'absolute foliar cover',
         dead_status = 'FALSE',
         cover_percent = -999) %>%
  anti_join(presence_data, join_by('site_visit_code', 'name_adjudicated')) %>%
  # Select output fields
  select(site_visit_code, name_original, name_adjudicated, cover_type, dead_status, cover_percent)

# Join presence and absence_data
output_data = rbind(presence_data, absence_data) %>%
  left_join(site_data, join_by('site_visit_code')) %>%
  # Correct for Picea survey effort
  filter(name_adjudicated != 'Picea mariana' &
           name_adjudicated != 'Picea glauca' |
           (name_adjudicated == 'Picea mariana' & date > '2021-07-10') |
           (name_adjudicated == 'Picea glauca' & date > '2021-07-10')) %>%
  # Select output fields
  select(site_visit_code, name_original, name_adjudicated, cover_type, dead_status, cover_percent)

# Export absolute cover data as csv file
write.csv(output_data, file = cover_output, fileEncoding = 'UTF-8', row.names = FALSE)