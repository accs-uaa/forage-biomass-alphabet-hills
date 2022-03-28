# -*- coding: utf-8 -*-
# ---------------------------------------------------------------------------
# Multi-class predict
# Author: Timm Nawrocki
# Last Updated: 2022-03-27
# Usage: Must be executed in an Anaconda Python 3.9+ distribution.
# Description: "Multi-class predict" is a function that predicts values and probabilities for a multi-class classification model to a set of rows.
# ---------------------------------------------------------------------------

# Create a function to predict a multi-class classification model
def multiclass_predict(classifier, X_data, prediction, class_number, output_data):
    """
    Description: predicts values and probabilities from a stored model
    Inputs: 'classifier' -- a classification model loaded in memory
            'X_data' -- a set of data to predict with all necessary covariates for the model
            'prediction' -- name of a field to store the predicted class
            'class_number' -- an integer value less than 100 for the number of possible classes
            'output_data' -- a data frame to store the prediction results
    Returned Value: Returns the output data frame of predictions
    Preconditions: requires a classifier, threshold, and covariates
    """

    import pandas as pd

    # Parse classes into column names
    column_names = []
    i = 1
    while i <= class_number:
        if i < 10:
            column = 'class_0' + str(i)
        elif i < 100:
            column = 'class_' + str(i)
        else:
            print('ERROR: Class numbers greater than 100 not supported.')
            quit()
        column_names.append(column)
        i += 1

    # Predict classes for the X data
    print('\t\tPredicting values...')
    class_prediction = classifier.predict(X_data)

    # Predict probabilities for the X data
    print('\t\tPredicting probabilities...')
    class_probabilities = classifier.predict_proba(X_data)
    probability_data = pd.DataFrame(class_probabilities, columns=column_names)

    # Concatenate predicted values to output data frame
    print('\t\tConcatenating results...')
    output_data = output_data.assign(prediction=class_prediction)
    result = pd.concat([output_data, probability_data], axis=1)
    result = result.rename(columns={'prediction': prediction[0]})

    return result
