# -*- coding: utf-8 -*-
# ---------------------------------------------------------------------------
# Model Train and Test
# Author: Timm Nawrocki
# Last Updated: 2021-08-18
# Usage: Must be executed in an Anaconda Python 3.8+ distribution.
# Description: "Model Train and Test" is a function that contains a model train and test routine for a classification model with threshold optimization and cross validation.
# ---------------------------------------------------------------------------

# Create a function to train and test a classification model
def model_train_test(classifier_params, iteration_data, outer_cv_splits, inner_cv_splits, rstate, threshold_file, output_classifier):
    """
    Description: trains and tests a classification model
    Inputs: 'classifier_params' -- a set of parameters for a random forest classifier specified according to the sklearn API
            'iteration_data' -- a data frame of the data for a specified single iteration
            'outer_cv_splits' -- a splitting method for the outer cross validation specified according to the sklearn API
            'inner_cv_splits' -- a splitting method for the inner cross validation specified according to the sklearn API
            'rstate' -- a random state value
    Returned Value: Returns a trained classifier on disk, a threshold value on disk, a data frame of predictions, an AUC value, and an accuracy percentage
    Preconditions: requires a data frame of covariates and responses
    """

    # Import packages
    from sklearn.utils import shuffle
    from sklearn.metrics import confusion_matrix
    from sklearn.metrics import roc_auc_score
    import time
    import datetime

    # Import functions from repository statistics package
    from package_Statistics import outer_cross_validation
    from package_Statistics import train_export_classifier

    # Shuffle data
    iteration_data = shuffle(iteration_data, random_state=rstate)

    # Conduct outer cross validation
    outer_results = outer_cross_validation(classifier_params,
                                           iteration_data,
                                           outer_cv_splits,
                                           inner_cv_splits)

    # Partition output results to presence-absence observed and predicted
    y_classify_observed = outer_results['response']
    y_classify_predicted = outer_results['prediction']
    y_classify_probability = outer_results['presence']

    # Determine error rates
    confusion_test = confusion_matrix(y_classify_observed.astype('int32'), y_classify_predicted.astype('int32'))
    true_negative = confusion_test[0, 0]
    false_negative = confusion_test[1, 0]
    true_positive = confusion_test[1, 1]
    false_positive = confusion_test[0, 1]

    # Calculate AUC score
    iteration_auc = roc_auc_score(y_classify_observed.astype('int32'), y_classify_probability.astype(float))

    # Calculate overall accuracy
    iteration_accuracy = (true_negative + true_positive) / (true_negative + false_positive + false_negative + true_positive)

    # Train and Export Classification Model
    print('\tPredicting outer cross-validation test data...')
    iteration_start = time.time()
    trained_classifier, importance_table = train_export_classifier(classifier_params,
                                                                   iteration_data,
                                                                   inner_cv_splits,
                                                                   threshold_file,
                                                                   output_classifier)
    iteration_end = time.time()
    iteration_elapsed = int(iteration_end - iteration_start)
    iteration_success_time = datetime.datetime.now()
    print(
        f'\tCompleted at {iteration_success_time.strftime("%Y-%m-%d %H:%M")} (Elapsed time: {datetime.timedelta(seconds=iteration_elapsed)})')
    print('\t----------')

    # Return outer cross validation results
    return outer_results, iteration_auc, iteration_accuracy, trained_classifier, importance_table
