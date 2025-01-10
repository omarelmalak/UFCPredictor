import pandas as pd

from sklearn.ensemble import RandomForestClassifier
from sklearn.metrics import accuracy_score
from sklearn.metrics import precision_score
from sklearn.metrics import recall_score
from sklearn.metrics import f1_score


if __name__ == "__main__":
    fights = pd.read_csv("A_to_M_fighters.csv", index_col=0)

    """
    print(fights.shape)

    print(fights["Fighter"].value_counts())
    print(fights[fights["Fighter"] == "Israel Adesanya"])

    print(fights.dtypes)
    """

    # PARAMETER DEFINITIONS
    # n_estimators: Number of individual decision trees we want to train
    #               HIGHER n_estimators => LONGER runtime => HIGHER accuracy
    # min_samples_split: Number of samples we want in a leaf of decision tree before splitting node
    #               HIGHER min_samples_split => LESS LIKELY training data overfit => LOWER accuracy on training data
    # random_state: Run RandomForestClassifier multiple times, we get the same result
    classifier = RandomForestClassifier(n_estimators=10, min_samples_split=10, random_state=1)


    # SPLIT UP TRAINING AND TEST DATA
    # (BEFORE AND AFTER START OF 2023)
    train = fights[fights["Date"] < '2023-01-01']
    test = fights[fights["Date"] >= '2023-01-01']

    # IDENTIFY ALL THE KEY PREDICTORS
    predictors = ["Round",
                  "Total Fight Time (Sec)",

                  "KD",
                  "Sig. Str. Landed",
                  "Sig. Str. Attempted",
                  "Sig. Str. %",
                  "Total Str. Landed",
                  "Total Str. Attempted",
                  "Total Str. %",
                  "TD Landed",
                  "TD Attempted",
                  "TD %",
                  "Sub. Attempted",
                  "Sub. Successful",
                  "Sub. %",
                  "Ctrl Time (Sec)",

                  "Opp. KD",
                  "Opp. Sig. Str. Landed",
                  "Opp. Sig. Str. Attempted",
                  "Opp. Sig. Str. %",
                  "Opp. Total Str. Landed",
                  "Opp. Total Str. Attempted",
                  "Opp. Total Str. %",
                  "Opp. TD Landed",
                  "Opp. TD Attempted",
                  "Opp. TD %",
                  "Opp. Sub. Attempted",
                  "Opp. Sub. Successful",
                  "Opp. Sub. %",
                  "Opp. Ctrl Time (Sec)",

                  # CATEGORIZED CODE PREDICTORS (BONUS)
                  "Opp. Fighter Code",
                  "Method Code",
                  ]

    # FIT THE MODEL TO PREDICT THE Target COLUMN BASED ON PROVIDED predictors USING train DATA
    classifier.fit(train[predictors], train["Target"])

    # COLLECT A SET OF predictions USING test DATA
    predictions = classifier.predict(test[predictors])

    # PASS IN THE ACTUALS FROM test DATAFRAME AND THE predictions TO OBTAIN SCORE METRICS
    # ACCURACY SCORE = (true positives / all positives) + (true negatives / all negatives)
    acc = float(accuracy_score(test["Target"], predictions))

    # PRECISION SCORE = true positives / (true positives + false positives)
    # USED TO AVOID WRONGLY FLAGGING WINS
    # EX: DON'T WANT TO KEEP FLAGGING REAL EMAILS AS SPAM
    precision = float(precision_score(test["Target"], predictions))

    # RECALL SCORE = true positives / (true positives + false negatives)
    # USED TO AVOID MISSING A WIN PREDICTION
    # EX: DON'T WANT TO MISS A PREDICTION FOR A DISEASE
    recall = float(recall_score(test["Target"], predictions))

    # F1 SCORE = 2 * (precision * recall) / (prediction + recall)
    # HARMONIC MEAN BETWEEN PRECISION AND RECALL (WE DON'T NEED IT TO LEAN TOWARDS ONE OR THE OTHER, THE PREDICTION
    # COULD BE FROM EITHER FIGHTER'S PERSPECTIVE)
    f1 = float(f1_score(test["Target"], predictions))

    # CREATE A DATAFRAME CONTAINING ACTUAL (FROM test DATAFRAME) VS. PREDICTIONS (FROM predictions)
    actual_vs_predictions_df = pd.DataFrame(dict(actual=test["Target"], prediction=predictions))

    # CREATE A CROSSTAB CONTAINING ACTUAL vs. PREDICTIONS
    cross = pd.crosstab(index=actual_vs_predictions_df["actual"], columns=actual_vs_predictions_df["prediction"])
    # print(cross)

    # print(accuracy)

    print("Accuracy: " + str(round(acc * 100, 2)) + "%")
    print("Precision: " + str(round(precision * 100, 2)) + "%")
    print("Recall: " + str(round(recall * 100, 2)) + "%")
    print("F1 Score: " + str(round(f1 * 100, 2)) + "%")


