import scipy.stats as ss
from sklearn.model_selection import RandomizedSearchCV, train_test_split
from sklearn.ensemble import RandomForestClassifier


def model_rf_benchmark(X_train, y_train):
    """ Fits benchmark random forest model on data
     
    Using a randomized search over the hyperparameter space, selects a random forest model with highest ROC AUC, 
    using 5-fold stratified cross-validation. 

    Args:
        X_train: Training features
        y_train: Training labels

    Returns:
        fitted: fitted RandomizedSearchCV instance  
        
    """

    model = RandomForestClassifier()
    param_distributions = dict(n_estimators=2 ** 8,
                               max_features=ss.beta(a=5, b=2),
                               max_leaf_nodes=ss.nbinom(n=2, p=.001, loc=100))
    model_selector = RandomizedSearchCV(model,
                                        param_distributions=param_distributions,
                                        scoring='roc_auc',
                                        n_iter=5,
                                        refit=True,
                                        verbose=1,
                                        cv=5)

    model_selector.fit(X_train, y_train)

    return model_selector
