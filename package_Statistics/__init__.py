# -*- coding: utf-8 -*-
# ---------------------------------------------------------------------------
# Initialization for statistics module
# Author: Timm Nawrocki
# Last Updated: 2020-01-05
# Usage: Individual functions have varying requirements. All functions that use arcpy must be executed in an Anaconda Python 3.9+ distribution.
# Description: "Initialization for statistics module" imports modules in the package so that the contents are accessible.
# ---------------------------------------------------------------------------

# Import functions from modules
from package_Statistics.multiclassTrainTest import multiclass_train_test
from package_Statistics.multiclassCrossValidation import multiclass_cross_validation
from package_Statistics.multiclassPredict import multiclass_predict
from package_Statistics.trainExportClassifier import train_export_classifier
