# -*- coding: utf-8 -*-
# ---------------------------------------------------------------------------
# Summarize plot absolute foliar cover
# Author: Timm Nawrocki, Amanda Droghini
# Last Updated: 2022-10-19
# Usage: Should be executed in R 4.1.0+.
# Description: "Summarize plot absolute foliar cover" transforms the line-point intercept hits to absolute foliar cover.
# ---------------------------------------------------------------------------

rm(list=ls())

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
cover_sheet = 'Cover'
additional_sheet = 'AdditionalCover'

# Define output dataset
output_file = paste(field_folder,
                    'processed/2021_AlphabetHills_PlotCover.csv',
                    sep = '/')

# Set repository directory
repository = 'C:/Users/timmn/Documents/Repositories/akveg-database-public'

# Import required libraries.
library(dplyr)
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
                       'Administrative/Credentials/accs-postgresql/authentication_akveg.csv',
                       sep = '/')
database_connection = connect_database_postgresql(authentication)

# Define queries for AKVEG
query_all = 'SELECT * FROM taxon_all'
query_accepted = 'SELECT * FROM taxon_accepted'
taxa_all = as_tibble(dbGetQuery(database_connection, query_all))
taxa_accepted = as_tibble(dbGetQuery(database_connection, query_accepted))

# Read cover data from excel
cover_data = read_xlsx(input_file,
                       sheet = cover_sheet)

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

# Summarize data by site and taxon
absolute_cover = cover_data_long %>%
  group_by(site, code, dead_status) %>%
  mutate(cover = round((n()/120)*100, digits = 3)) %>%
  mutate(cover_type = 'absolute foliar cover') %>%
  distinct()

# Join additional cover to absolute cover
additional_cover = read_xlsx(input_file,
                             sheet = additional_sheet) %>%
  mutate(cover_type = 'absolute foliar cover',
         dead_status = as.logical("FALSE"))

output_data = rbind(absolute_cover, additional_cover)

# Join species names to data

# Simplify taxonomic tables
taxa_all <- taxa_all %>% 
  select(taxon_code, taxon_name, taxon_accepted_code)

taxa_accepted <- taxa_all %>% 
  filter(taxon_code == taxon_accepted_code) %>% 
  select(-taxon_code) %>% 
  rename(name_adjudicated = taxon_name)

output_data <- output_data %>%
  # Join accepted names to codes
  left_join(taxa_all, by=c('code'='taxon_code')) %>%
  rename(name_original = taxon_name) %>% 
  left_join(taxa_accepted, by='taxon_accepted_code') %>% 
  # Rename to match naming conventions in minimum standards
  rename(cover_percent = cover) %>% 
  ungroup() %>% 
  # Select output fields
  select(site, name_original, name_adjudicated, cover_type, dead_status, cover_percent)

# QA/QC ----

# Do any of the columns have null values that need to be addressed?
cbind(
  lapply(
    lapply(output_data, is.na)
    , sum)
)

# Export absolute cover data as csv file
write.csv(output_data, file = output_file, fileEncoding = 'UTF-8', row.names = FALSE)