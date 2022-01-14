# ---------------------------------------------------------------------------
# Plot covariate importances
# Author: Timm Nawrocki, Alaska Center for Conservation Science
# Last Updated: 2022-01-14
# Usage: Script should be executed in R 4.1.0+.
# Description: "Plot covariate importances" plots the covariate importances from a random forest model as mean decrease in impurity.
# ---------------------------------------------------------------------------

# Define version
round_date = 'round_20220105'

# Set root directory
drive = 'N:'
root_folder = 'ACCS_Work'

# Define input data
data_folder = paste(drive,
                    root_folder,
                    'Projects/WildlifeEcology/Moose_AlphabetHills/Data',
                    sep = '/')
importance_file = paste(data_folder,
                        'Data_Output/model_results',
                        round_date,
                        'importance_classifier_mdi.csv',
                        sep = '/')

# Define output files
output_plot = paste(data_folder,
                    'Data_Output/model_results',
                    round_date,
                    'covariate_importances.jpg',
                    sep = '/')

# Import libraries
library(dplyr)
library(ggplot2)
library(ggtext)
library(cowplot)
library(ggpubr)
library(RColorBrewer)
library(tibble)
library(tidyr)

# Import data to data frame
importance_data = read.csv(importance_file)

# Plot covariate importances
importance_plot = ggplot(importance_data, aes(x=covariate, y=importance)) +
  geom_bar(stat='identity', color = '#808080', fill = '#808080') +
  theme_minimal() +
  labs(y = 'MDI for multiclass random forest') +
  theme(axis.title.x = element_blank(),
        axis.text.x = element_markdown(angle = 45, vjust = 1, hjust = 1))

# Export plot
ggsave(output_plot,
       plot = importance_plot,
       device = 'jpeg',
       path = NULL,
       scale = 1,
       width = 25,
       height = 7,
       units = 'in',
       dpi = 600,
       limitsize = TRUE)