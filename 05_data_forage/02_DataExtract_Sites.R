# -*- coding: utf-8 -*-
# ---------------------------------------------------------------------------
# Extract features to sites
# Author: Timm Nawrocki
# Last Updated: 2022-10-29
# Usage: Must be executed in R 4.0.0+.
# Description: "Extract features to sites" extracts data from rasters to points representing plot locations and collapses multi-point plots into single points with plot-level means.
# ---------------------------------------------------------------------------

# Define round date
round_date = 'round_20220607'

# Set root directory
drive = 'N:'
root_folder = 'ACCS_Work'

# Define project folder
project_folder = paste(drive,
                       root_folder,
                       'Projects/WildlifeEcology/Moose_AlphabetHills/Data',
                       sep = '/')

# Define input folders
site_folder = paste(project_folder,
                    'Data_Input/forage',
                    sep = '/')
foliar_folder = paste(project_folder,
                      'Data_Output/output_rasters',
                      round_date,
                      'foliar_cover',
                      sep = '/')
physiography_folder = paste(project_folder,
                            'Data_Output/output_rasters',
                            round_date,
                            'physioprobability',
                            sep = '/')
validation_folder = paste(project_folder,
                          'Data_Input/validation',
                          sep = '/')

# Define input site data
site_file = paste(site_folder,
                  'unprocessed',
                  '02_site_accsalphabethills2021.csv',
                  sep = '/')
geodatabase = paste(project_folder,
                     'AlphabetHillsBrowseBiomass.gdb',
                     sep = '/')
site_feature = 'Forage_Sites_Formatted_AKALB'

# Define output site data
site_output = paste(site_folder,
                    'processed',
                    'sites_extracted.csv',
                    sep = '/')

# Import required libraries for geospatial processing: dplyr, raster, rgdal, sp, and stringr.
library(dplyr)
library(raster)
library(sf)
library(tibble)
library(tidyr)

# Read site metadata into dataframe
site_metadata = read.csv(site_file, fileEncoding = 'UTF-8')
  
# Create a list of all predictor rasters
predictors_foliar = list.files(foliar_folder, pattern = 'tif$', full.names = TRUE)
predictors_physio = list.files(physiography_folder, pattern = 'tif$', full.names = TRUE)
predictors_validation = list.files(validation_folder, pattern = 'tif$', full.names = TRUE)
predictors_all = c(predictors_foliar,
                   predictors_physio,
                   predictors_validation)
print("Number of predictor rasters:")
print(length(predictors_all))
  
# Generate a stack of all predictor rasters
predictor_stack = raster::stack(predictors_all)
  
# Read site data and extract features
site_data = st_read(dsn = geodatabase, layer = site_feature)
sites_extracted = data.frame(site_data, raster::extract(predictor_stack, site_data))
  
# Convert field names to standard
sites_extracted = sites_extracted %>%
  rename(fol_alnus = Alphabet_fol_alnus,
         fol_betshr = Alphabet_fol_betshr,
         fol_bettre = Alphabet_fol_bettre,
         fol_dectre = Alphabet_fol_dectre,
         fol_dryas = Alphabet_fol_dryas,
         fol_empnig = Alphabet_fol_empnig,
         fol_erivag = Alphabet_fol_erivag,
         fol_picgla = Alphabet_fol_picgla,
         fol_picmar = Alphabet_fol_picmar,
         fol_rhoshr = Alphabet_fol_rhoshr,
         fol_salshr = Alphabet_fol_salshr,
         fol_sphagn = Alphabet_fol_sphagn,
         fol_vaculi = Alphabet_fol_vaculi,
         fol_vacvit = Alphabet_fol_vacvit,
         fol_wetsed = Alphabet_fol_wetsed,
         fol_forb = Alphabet_fol_forb,
         fol_decshr = Alphabet_fol_decshr,
         physio_aspen = Alphabet_PhysioProbability_Aspen,
         physio_barren = Alphabet_PhysioProbability_Barren,
         physio_burned = Alphabet_PhysioProbability_Burned,
         physio_drainage = Alphabet_PhysioProbability_Drainage,
         physio_floodplain = Alphabet_PhysioProbability_Floodplain,
         physio_riparian = Alphabet_PhysioProbability_Riparian,
         physio_upland = Alphabet_PhysioProbability_UplandLowland,
         physio_water = Alphabet_PhysioProbability_Water,
         model_iteration = Alphabet_ModelIteration,
         validation_group = Alphabet_ValidationGroups)

# Summarize data by site
sites_mean = sites_extracted %>%
  group_by(site_code) %>%
  mutate(fol_alnus = as.numeric(fol_alnus),
         fol_betshr = as.numeric(fol_betshr),
         fol_bettre = as.numeric(fol_bettre),
         fol_dectre = as.numeric(fol_dectre),
         fol_dryas = as.numeric(fol_dryas),
         fol_empnig = as.numeric(fol_empnig),
         fol_erivag = as.numeric(fol_erivag),
         fol_picgla = as.numeric(fol_picgla),
         fol_picmar = as.numeric(fol_picmar),
         fol_rhoshr = as.numeric(fol_rhoshr),
         fol_salshr = as.numeric(fol_salshr),
         fol_sphagn = as.numeric(fol_sphagn),
         fol_vaculi = as.numeric(fol_vaculi),
         fol_vacvit = as.numeric(fol_vacvit),
         fol_wetsed = as.numeric(fol_wetsed),
         fol_forb = as.numeric(fol_forb),
         fol_decshr = as.numeric(fol_decshr),
         physio_aspen = as.numeric(physio_aspen),
         physio_barren = as.numeric(physio_barren),
         physio_burned = as.numeric(physio_burned),
         physio_drainage = as.numeric(physio_drainage),
         physio_floodplain = as.numeric(physio_floodplain),
         physio_riparian = as.numeric(physio_riparian),
         physio_upland = as.numeric(physio_upland),
         physio_water = as.numeric(physio_water),
         model_iteration = as.numeric(model_iteration),
         validation_group = as.numeric(validation_group)) %>%
  summarize(fol_alnus = mean(fol_alnus),
            fol_betshr = mean(fol_betshr),
            fol_bettre = mean(fol_bettre),
            fol_dectre = mean(fol_dectre),
            fol_dryas = mean(fol_dryas),
            fol_empnig = mean(fol_empnig),
            fol_erivag = mean(fol_erivag),
            fol_picgla = mean(fol_picgla),
            fol_picmar = mean(fol_picmar),
            fol_rhoshr = mean(fol_rhoshr),
            fol_salshr = mean(fol_salshr),
            fol_sphagn = mean(fol_sphagn),
            fol_vaculi = mean(fol_vaculi),
            fol_vacvit = mean(fol_vacvit),
            fol_wetsed = mean(fol_wetsed),
            fol_forb = mean(fol_forb),
            fol_decshr = mean(fol_decshr),
            physio_aspen = mean(physio_aspen),
            physio_barren = mean(physio_barren),
            physio_burned = mean(physio_burned),
            physio_drainage = mean(physio_drainage),
            physio_floodplain = mean(physio_floodplain),
            physio_riparian = mean(physio_riparian),
            physio_upland = mean(physio_upland),
            physio_water = mean(physio_water),
            model_iteration = round(mean(model_iteration), digits = 0),
            validation_group = round(mean(validation_group), digits = 0),
            num_points = n()) %>%
  rowid_to_column('train_class')

# Join site metadata to extracted data and remove na values
sites_joined = site_metadata %>%
  inner_join(sites_mean, by = 'site_code') %>%
  drop_na()

# Export data as a csv
write.csv(sites_joined, file = site_output, fileEncoding = 'UTF-8', row.names = FALSE)
print('Finished extracting data to sites.')
