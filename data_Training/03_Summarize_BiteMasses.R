# -*- coding: utf-8 -*-
# ---------------------------------------------------------------------------
# Summarize per species bite masses
# Author: Timm Nawrocki
# Last Updated: 2022-03-30
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
plots_folder = paste(field_folder,
                     'processed/plots',
                     sep = '/')

# Define input dataset
input_file = paste(field_folder,
                   'unprocessed/2021_AlphabetHills_Data.xlsx',
                   sep = '/')
mass_sheet = 'Mass'

# Define output dataset
output_file = paste(field_folder,
                    'processed/2021_AlphabetHills_BiteMass.csv',
                    sep = '/')

# Set repository directory
repository = 'C:/Users/timmn/Documents/Repositories/akveg-database-public'

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
                       'Administrative/Credentials/accs-postgresql/authentication_akveg.csv',
                       sep = '/')
database_connection = connect_database_postgresql(authentication)

# Define queries for AKVEG
query_all = 'SELECT * FROM taxon_all'
query_accepted = 'SELECT * FROM taxon_accepted'
taxa_all = as_tibble(dbGetQuery(database_connection, query_all))
taxa_accepted = as_tibble(dbGetQuery(database_connection, query_accepted))

# Read cover data from excel
mass_data = read_xlsx(input_file,
                      sheet = mass_sheet)

# Calculate wet sample mass
mass_data = mass_data %>%
  filter(wet_number > 0 &
           total_weight != -999) %>%
  mutate(bite_size = case_when(bite_size == 'clip' ~ 'large-clip',
                               bite_size == 'strip' ~ 'large-strip',
                               bite_size == 'large' ~ 'large-clip',
                               TRUE ~ bite_size)) %>%
  mutate(sample_weight = total_weight - bag_weight) %>%
  mutate(bite_mass = sample_weight / wet_number) %>%
  # Join accepted names to codes
  left_join(taxa_all, by = 'code') %>%
  left_join(taxa_accepted, by = 'code_accepted') %>%
  # Select output fields
  select(site, subplot, code, name_accepted, bite_size,
           wet_number, sample_weight, bite_mass)

# Summarize mean bite mass per species and bite size
output_data = mass_data %>%
  group_by(code, name_accepted, bite_size) %>%
  summarize(bite_mass = round(mean(bite_mass), digits = 2))

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
  select(code, name_accepted) %>%
  distinct()

# Create an output plot for each species
for (i in 1:nrow(species_list)) {
  code_str = species_list$code[i]
  name_str = species_list$name_accepted[i]
  print(name_str)
  
  # Define output plot name
  output_plot = paste(plots_folder,
                      '/bitemass_',
                      code_str,
                      '.jpg',
                      sep = '')
  
  # Restrict data to species
  species_data = mass_data %>%
    filter(code == code_str)
  
  # Plot wet weight against bite number
  biomass_plot = ggplot(data = species_data, aes(x = wet_number, y = sample_weight)) +
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
    scale_x_continuous(breaks=seq(0, 60, by = 10), limits = c(0, 60), expand = c(0.01, 0)) +
    scale_y_continuous(breaks=seq(0, 60, by = 10), limits = c(0, 60), expand = c(0.02, 0))
  
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
