# -*- coding: utf-8 -*-
# ---------------------------------------------------------------------------
# Summarize per species bite masses
# Author: Timm Nawrocki
# Last Updated: 2022-03-03
# Usage: Should be executed in R 4.1.0+.
# Description: "Summarize per species bite masses" transforms bite counts into mean and standard deviation per bite mass.
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
                      'Data/Data_Input/forage/processed',
                      sep = '/')
plots_folder = paste(forage_folder,
                     'plots',
                     sep = '/')

# Define input dataset
input_file = paste(field_folder,
                   '2021_AlphabetHills_Data.xlsx',
                   sep = '/')
mass_file = paste(field_folder,
                  '2021_AlphabetHills_DryMass.xlsx',
                  sep = '/')

# Define output dataset
output_file = paste(forage_folder,
                    'bite_mass.csv',
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

# Calculate per bite sample dry mass
mass_data = read_xlsx(mass_file, sheet = 'dry_mass') %>%
  # Join accepted names to codes
  left_join(taxon_data, by = c('code' = 'taxon_code')) %>%
  dplyr::select(-taxon_name, -taxon_author_id, -taxon_status_id) %>%
  left_join(taxon_data, by = c('taxon_accepted_code' = 'taxon_code')) %>%
  mutate(bite_size = case_when(bite_size == 'clip' ~ 'large_clip',
                               bite_size == 'strip' ~ 'large_strip',
                               bite_size == 'large' ~ 'large_strip',
                               TRUE ~ bite_size)) %>%
  select(sample_id, taxon_accepted_code, taxon_name, bite_size, dry_number, total_mass) %>%
  mutate(taxon_accepted_code = case_when(taxon_accepted_code == 'betgla' ~ 'betshr',
                                         taxon_accepted_code == 'betnansexi' ~ 'betshr',
                                         TRUE ~ taxon_accepted_code)) %>%
  mutate(taxon_name = case_when(taxon_accepted_code == 'betshr' ~ 'Betula shrubs',
                                taxon_accepted_code == 'betshr' ~ 'Betula shrubs',
                                TRUE ~ taxon_name))

# Summarize mean bite mass per species and bite size
output_data = mass_data %>%
  mutate(bite_mass = total_mass / dry_number) %>%
  group_by(taxon_accepted_code, taxon_name, bite_size) %>%
  summarize(bite_mass = mean(bite_mass)) %>%
  dplyr::select(taxon_accepted_code, taxon_name, bite_size, bite_mass)

# Export absolute cover data as csv file
write.csv(output_data, file = output_file, fileEncoding = 'UTF-8', row.names = FALSE)

# Set plot theme
font = theme(strip.text = element_text(size = 12, color = 'black'),
             strip.background = element_rect(color = 'black', fill = 'white'),
             axis.text = element_text(size = 10),
             axis.text.x = element_text(color = 'black'),
             axis.text.y = element_text(color = 'black'),
             axis.title = element_text(size = 12),
             axis.title.x = element_text(margin = margin(t = 10)),
             axis.title.y = element_text(margin = margin(r = 10))
)

# Identify distinct species in mass data
species_list = mass_data %>%
  dplyr::select(taxon_accepted_code, taxon_name) %>%
  distinct()

# Create an output plot for each species
for (i in 1:nrow(species_list)) {
  code_str = species_list$taxon_accepted_code[i]
  name_str = species_list$taxon_name[i]
  print(name_str)
  
  # Define output plot name
  output_plot = paste(plots_folder,
                      '/bitemass_',
                      code_str,
                      '.jpg',
                      sep = '')
  
  # Restrict data to species
  species_data = mass_data %>%
    filter(taxon_accepted_code == code_str)
  
  # Plot dry mass against bite number
  biomass_plot = ggplot(data = species_data, aes(x = dry_number, y = total_mass)) +
    theme_bw() +
    font +
    geom_point(alpha = 0.7,
               size = 2,
               color = '#005280') +
    geom_smooth(method='lm') +
    facet_wrap(~bite_size, ncol = 2) +
    theme(panel.spacing = unit(2, 'lines')) +
    labs(x = paste('Number of bites for ', name_str, sep = ''), y = 'Sample mass (grams)') +
    coord_fixed(ratio = 1) +
    scale_x_continuous(breaks=seq(0, 20, by = 5), limits = c(0, 20), expand = c(0.01, 0)) +
    scale_y_continuous(breaks=seq(0, 20, by = 5), limits = c(0, 20), expand = c(0.02, 0))
  
  ggsave(output_plot,
         plot = biomass_plot,
         device = 'jpeg',
         path = NULL,
         scale = 1,
         width = 6.5,
         height = 6,
         units = 'in',
         dpi = 600)
}
