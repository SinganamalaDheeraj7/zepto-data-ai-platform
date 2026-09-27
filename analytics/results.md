Shape: (891, 15)

## info

None

## describe

|        |   survived |     pclass | sex   |      age |      sibsp |      parch |     fare | embarked   | class   | who   |   adult_male | deck   | embark_town   | alive   |   alone |
|:-------|-----------:|-----------:|:------|---------:|-----------:|-----------:|---------:|:-----------|:--------|:------|-------------:|:-------|:--------------|:--------|--------:|
| count  | 891        | 891        | 891   | 714      | 891        | 891        | 891      | 889        | 891     | 891   |          891 | 203    | 889           | 891     |     891 |
| unique | nan        | nan        | 2     | nan      | nan        | nan        | nan      | 3          | 3       | 3     |            2 | 7      | 3             | 2       |       2 |
| top    | nan        | nan        | male  | nan      | nan        | nan        | nan      | S          | Third   | man   |            1 | C      | Southampton   | no      |       1 |
| freq   | nan        | nan        | 577   | nan      | nan        | nan        | nan      | 644        | 491     | 537   |          537 | 59     | 644           | 549     |     537 |
| mean   |   0.383838 |   2.30864  | nan   |  29.6991 |   0.523008 |   0.381594 |  32.2042 | nan        | nan     | nan   |          nan | nan    | nan           | nan     |     nan |
| std    |   0.486592 |   0.836071 | nan   |  14.5265 |   1.10274  |   0.806057 |  49.6934 | nan        | nan     | nan   |          nan | nan    | nan           | nan     |     nan |
| min    |   0        |   1        | nan   |   0.42   |   0        |   0        |   0      | nan        | nan     | nan   |          nan | nan    | nan           | nan     |     nan |
| 25%    |   0        |   2        | nan   |  20.125  |   0        |   0        |   7.9104 | nan        | nan     | nan   |          nan | nan    | nan           | nan     |     nan |
| 50%    |   0        |   3        | nan   |  28      |   0        |   0        |  14.4542 | nan        | nan     | nan   |          nan | nan    | nan           | nan     |     nan |
| 75%    |   1        |   3        | nan   |  38      |   1        |   0        |  31      | nan        | nan     | nan   |          nan | nan    | nan           | nan     |     nan |
| max    |   1        |   3        | nan   |  80      |   8        |   6        | 512.329  | nan        | nan     | nan   |          nan | nan    | nan           | nan     |     nan |

## Missing percentages

|             |     0 |
|:------------|------:|
| age         | 19.87 |
| embarked    |  0.22 |
| deck        | 77.22 |
| embark_town |  0.22 |

age IQR outliers: 65

fare IQR outliers: 114

Fare mean/median/mode: (np.float64(32.09668087739032), 14.4542, np.float64(8.05))

## Survival rates

| sex    |   survived |
|:-------|-----------:|
| female |   0.740385 |
| male   |   0.188908 |

|   pclass |   survived |
|---------:|-----------:|
|        1 |   0.626168 |
|        2 |   0.472826 |
|        3 |   0.242363 |

|               |   survived |
|:--------------|-----------:|
| ('female', 1) |   0.967391 |
| ('female', 2) |   0.921053 |
| ('female', 3) |   0.5      |
| ('male', 1)   |   0.368852 |
| ('male', 2)   |   0.157407 |
| ('male', 3)   |   0.135447 |

## Correlation

|          |   survived |     pclass |        age |      sibsp |      parch |       fare |
|:---------|-----------:|-----------:|-----------:|-----------:|-----------:|-----------:|
| survived |  1         | -0.335549  | -0.0698217 | -0.03404   |  0.0831508 |  0.25529   |
| pclass   | -0.335549  |  1         | -0.336512  |  0.0816556 |  0.0168245 | -0.548193  |
| age      | -0.0698217 | -0.336512  |  1         | -0.232543  | -0.171485  |  0.0937071 |
| sibsp    | -0.03404   |  0.0816556 | -0.232543  |  1         |  0.414542  |  0.160887  |
| parch    |  0.0831508 |  0.0168245 | -0.171485  |  0.414542  |  1         |  0.217532  |
| fare     |  0.25529   | -0.548193  |  0.0937071 |  0.160887  |  0.217532  |  1         |

## Z-score check

|      |   before_mean |   after_mean |   after_std |
|:-----|--------------:|-------------:|------------:|
| age  |       29.3152 |  2.83738e-16 |           1 |
| fare |       32.0967 |  1.31878e-16 |           1 |

## Classification comparison

| model    |   accuracy |   precision |   recall |    f1 |   auc |
|:---------|-----------:|------------:|---------:|------:|------:|
| logistic |      0.809 |       0.783 |    0.691 | 0.734 | 0.861 |
| tree     |      0.77  |       0.69  |    0.721 | 0.705 | 0.754 |
| forest   |      0.809 |       0.766 |    0.721 | 0.742 | 0.82  |

## Imbalance comparison

| model    |   precision |   recall |    f1 |
|:---------|------------:|---------:|------:|
| baseline |       0.783 |    0.691 | 0.734 |
| balanced |       0.718 |    0.75  | 0.734 |
| smote    |       0.735 |    0.735 | 0.735 |

Grid best: {'model__max_depth': None, 'model__max_features': 'sqrt', 'model__n_estimators': 200}; OOB=0.807

Regression: MAE=21.139, RMSE=41.747, R2=0.347, Adjusted R2=0.324