# -*- coding: utf-8 -*-
# ---------------------------------------------------------------------------
# Multiclass cross validation
# Author: Timm Nawrocki
# Last Updated: 2022-01-05
# Usage: Must be executed in an Anaconda Python 3.9+ distribution.
# Description: "Multiclass cross validation" is a function that conducts the outer cross validation routine for all partitions of a pre-defined outer cross validation set for a multiclass classification.
# ---------------------------------------------------------------------------

def multiclass_cross_validation(classifier_params, input_data, class_variable, predictor_all, cv_groups, retain_variables,
                                outer_cv_splits):
    """
    Description: conducts outer cross validation iterations for a multiclass classification model
    Inputs: 'classifier_params' -- a set of parameters for a random forest classifier specified according to the sklearn API
            'input_data' -- a data frame containing the class and covariate data
            'class_variable' -- names of the field that contains the class labels
            'predictor_all' -- names of the fields that contain covariate values
            'cv_groups' -- name of the field that contains the cross validation group values
            'retain_variables' -- names of the fields that should be conserved
            'outer_cv_splits' -- a splitting method for the outer cross validation specified according to the sklearn API
    Returned Value: Returns a data frame of predictions in memory
    Preconditions: requires a classifier specification, a data frame of covariates and responses, field names, and an outer cross validation specification
    """

    # Import packages
    import pandas as pd
    from sklearn.ensemble import RandomForestClassifier
    import time
    import datetime

    # Define variable sets
    outer_cv_split_n = ['outer_cv_split_n']
    prediction = ['prediction']
    output_variables = class_variable + retain_variables + predictor_all + outer_cv_split_n + prediction

    # Create an empty data frame to store the outer cross validation splits
    outer_train = pd.DataFrame(columns=class_variable + predictor_all)
    outer_test = pd.DataFrame(columns=class_variable + predictor_all)

    # Create an empty data frame to store the outer test results
    outer_results = pd.DataFrame(columns=output_variables)

    # Create outer cross validation splits
    count = 1
    for train_index, test_index in outer_cv_splits.split(input_data,
                                                         input_data[class_variable[0]],
                                                         input_data[cv_groups[0]]):
        # Split the data into train and test partitions
        train = input_data.iloc[train_index]
        test = input_data.iloc[test_index]
        # Insert outer_cv_split_n to train
        train = train.assign(outer_cv_split_n=count)
        # Insert iteration to test
        test = test.assign(outer_cv_split_n=count)
        # Append to data frames
        outer_train = outer_train.append(train, ignore_index=True, sort=True)
        outer_test = outer_test.append(test, ignore_index=True, sort=True)
        # Increase counter
        count += 1
    cv_length = count - 1
    print(f'\tCreated {cv_length} outer cross-validation group splits.')

    # Reset indices
    outer_train = outer_train.reset_index()
    outer_test = outer_test.reset_index()

    # Iterate through outer cross validation splits
    outer_cv_i = 1
    while outer_cv_i <= cv_length:

        #### CONDUCT MODEL TRAIN
        ####____________________________________________________

        # Partition the outer train split by iteration number
        print(f'\tConducting outer cross-validation iteration {outer_cv_i} of {cv_length}...')
        train_iteration = outer_train[outer_train['outer_cv_split_n'] == outer_cv_i].copy()

        # Identify X and y train splits for the classifier
        X_train_classify = train_iteration[predictor_all].astype(float).copy()
        y_train_classify = train_iteration[class_variable[0]].astype('int32').copy()

        # Train classifier
        print('\t\tTraining classifier...')
        iteration_start = time.time()
        outer_classifier = RandomForestClassifier(**classifier_params)
        outer_classifier.fit(X_train_classify, y_train_classify)
        iteration_end = time.time()
        iteration_elapsed = int(iteration_end - iteration_start)
        iteration_success_time = datetime.datetime.now()
        print(f'\t\tCompleted at {iteration_success_time.strftime("%Y-%m-%d %H:%M")} (Elapsed time: {datetime.timedelta(seconds=iteration_elapsed)})')
        print('\t\t----------')

        #### CONDUCT MODEL TEST
        ####____________________________________________________

        # Partition the outer test split by iteration number
        print('\t\tPredicting outer cross-validation test data...')
        iteration_start = time.time()
        test_iteration = outer_test[outer_test['outer_cv_split_n'] == outer_cv_i].copy()

        # Identify X test split
        X_test = test_iteration[predictor_all]

        # Use the classifier to predict class
        class_prediction = outer_classifier.predict(X_test)

        # Concatenate predicted values to test data frame
        test_iteration = test_iteration.assign(prediction=class_prediction)

        # Add the test results to output data frame
        outer_results = outer_results.append(test_iteration, ignore_index=True, sort=True)
        iteration_end = time.time()
        iteration_elapsed = int(iteration_end - iteration_start)
        iteration_success_time = datetime.datetime.now()
        print(f'\tCompleted at {iteration_success_time.strftime("%Y-%m-%d %H:%M")} (Elapsed time: {datetime.timedelta(seconds=iteration_elapsed)})')
        print('\t----------')

        # Increase iteration number
        outer_cv_i += 1

    return outer_results
