# -*- coding: utf-8 -*-
# ---------------------------------------------------------------------------
# Multiclass predict
# Author: Timm Nawrocki
# Last Updated: 2022-01-05
# Usage: Must be executed in an Anaconda Python 3.8+ distribution.
# Description: "Multiclass predict" is a function that predicts a multiclass classification model to a set of rows
# ---------------------------------------------------------------------------

# Create a function to predict and convert a stored path selection model
def multiclass_predict(classifier, X_data, output_data):
    """
    Description: predicts a stored model, applies a conversion threshold, and sets a column name for storage of results
    Inputs: 'classifier' -- a classification model loaded in memory
            'threshold' -- a numerical threshold value loaded in memory
            'X_data' -- a set of data to predict with all necessary covariates for the model
            'iteration' -- a number of the iteration
            'output_data' -- a data frame to store the prediction results
    Returned Value: Returns the output data frame of selection predictions and coordinates
    Preconditions: requires a classifier, threshold, and covariates
    """

    # Predict classes for the X data
    class_prediction = classifier.predict(X_data)

    # Concatenate predicted values to output data frame
    output_data = output_data.assign(prediction=class_prediction)

    return output_data
