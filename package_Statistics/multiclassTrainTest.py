# -*- coding: utf-8 -*-
# ---------------------------------------------------------------------------
# Multi-class model train and test
# Author: Timm Nawrocki
# Last Updated: 2022-03-27
# Usage: Must be executed in an Anaconda Python 3.9+ distribution.
# Description: "Multi-class model train and test" is a function that contains a model train and test routine for a multi-class classification model with cross validation.
# ---------------------------------------------------------------------------

# Create a function to train and test a multi-class classification model
def multiclass_train_test(classifier_params, outer_cv_splits, input_data, class_variable, predictor_all, cv_groups, retain_variables, outer_cv_split_n, prediction, rstate, output_classifier):
    """
    Description: trains and tests a multi-class classification model
    Inputs: 'classifier_params' -- a set of parameters for a random forest classifier specified according to the sklearn API
            'outer_cv_splits' -- a splitting method for the outer cross validation specified according to the sklearn API
            'input_data' -- a data frame containing the class and covariate data
            'class_variable' -- name of the field that contains the class labels
            'predictor_all' -- names of the fields that contain covariate values
            'cv_groups' -- name of the field that contains the cross validation group values
            'retain_variables' -- names of the fields that should be conserved
            'outer_cv_split_n' -- name of the field that stores the outer cross validation split number
            'prediction' -- name of the field that stores the class predictions
            'rstate' -- a random state value
            'output_classifier' -- a file path for storing the trained model on disk
    Returned Value: Returns a trained classifier on disk and a data frame of predictions
    Preconditions: requires a data frame of covariates and responses
    """

    # Import packages
    from sklearn.utils import shuffle

    # Import functions from repository statistics package
    from package_Statistics import multiclass_cross_validation
    from package_Statistics import train_export_classifier

    # Shuffle data
    shuffled_data = shuffle(input_data, random_state=rstate).copy()

    # Conduct outer cross validation
    outer_results = multiclass_cross_validation(classifier_params,
                                                outer_cv_splits,
                                                shuffled_data,
                                                class_variable,
                                                predictor_all,
                                                cv_groups,
                                                retain_variables,
                                                outer_cv_split_n,
                                                prediction)

    # Train and Export Classification Model
    trained_classifier, importance_table = train_export_classifier(classifier_params,
                                                                   input_data,
                                                                   class_variable,
                                                                   predictor_all,
                                                                   output_classifier)

    # Return outer cross validation results
    return outer_results, trained_classifier, importance_table
