# -*- coding: utf-8 -*-
# ---------------------------------------------------------------------------
# Plot observed vs predicted foliar cover
# Author: Timm Nawrocki, Alaska Center for Conservation Science
# Last Updated: 2023-04-07
# Usage: Script should be executed in R 4.0.0+.
# Description: "Plot observed vs predicted foliar cover" creates a plot showing the observed vs predicted foliar cover values with theoretical 1:1 ratio line.
# ---------------------------------------------------------------------------

# Set map classes
map_classes = c('alnalnsfru', 'betshr', 'chaang', 'salix', 'salpul')
upper_limits = c(85,
                 100,
                 80,
                 180,
                 140)

# Set root directory
drive = 'N:'
root_folder = 'ACCS_Work'

# Define input folders
data_folder = paste(drive,
                    root_folder,
                    'Projects/WildlifeEcology/Moose_AlphabetHills',
                    'Data/Data_Output/model_results/round_20220607/forage_biomass',
                    sep = '/')

# Import required libraries
library(dplyr)
library(ggplot2)
library(ggpmisc)
library(readr)
library(readxl)
library(tibble)
library(tidyr)
library(gridExtra)
library(scales)

for (map_class in map_classes) {
  # Define file directory
  class_folder = paste(data_folder,
                       map_class,
                       sep = '/')
  plots_folder = paste(class_folder,
                       'plots',
                       sep = '/')
  
  # Create plots folder if it does not exist
  if (!file.exists(plots_folder)) {
    dir.create(plots_folder)
  }
  
  # Define input and output files
  predictions_file = paste(class_folder,
                           'prediction.csv',
                           sep = '/')
  
  # Read predictions
  predictions_data = read_csv(predictions_file)
  
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
  
  # Retrieve plot upper count limit
  upper_limit = upper_limits[match(map_class, map_classes)]
  
  # Plot native resolution results
  map_plot = ggplot(data = predictions_data, aes(x = mass_g_per_m2, y = pred_mass)) +
    theme_bw() +
    font +
    geom_point(alpha = 0.4,
               size = 2,
               color = '#005280') +
    geom_segment(x = 0,
                 y = 0,
                 xend = upper_limit,
                 yend = upper_limit,
                 size = 0.5,
                 linetype = 1) +
    labs(x = 'Observed available forage biomass (g per sq m)',
         y = 'Predicted available forage biomass (g per sq m)') +
    coord_fixed(ratio = 1) +
    scale_x_continuous(breaks=seq(0, upper_limit, by = round((upper_limit/100), 0)*10),
                       limits = c(0, upper_limit),
                       expand = c(0.01, 0)) +
    scale_y_continuous(breaks=seq(0, upper_limit, by = round((upper_limit/100), 0)*10),
                       limits = c(0, upper_limit),
                       expand = c(0.02, 0))
  
  # Save jpgs at 600 dpi
  plot_file = paste(plots_folder,
                     'Figure_ObservedPredicted.jpg',
                     sep = '/')
  ggsave(plot_file,
         plot = map_plot,
         device = 'jpeg',
         path = NULL,
         scale = 1,
         width = 5,
         height = 5,
         units = 'in',
         dpi = 600,
         limitsize = TRUE)
  print(map_class)
}