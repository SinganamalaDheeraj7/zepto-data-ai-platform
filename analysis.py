"""One-load Titanic EDA and train-only-preprocessed modelling workflow."""
from pathlib import Path
import json
import joblib, numpy as np, pandas as pd, seaborn as sns, matplotlib.pyplot as plt
from sklearn.model_selection import train_test_split, GridSearchCV
from sklearn.compose import ColumnTransformer
from sklearn.pipeline import Pipeline
from sklearn.impute import SimpleImputer
from sklearn.preprocessing import OneHotEncoder, StandardScaler
from sklearn.linear_model import LogisticRegression, LinearRegression
from sklearn.tree import DecisionTreeClassifier, plot_tree
from sklearn.ensemble import RandomForestClassifier
from sklearn.metrics import accuracy_score, precision_recall_fscore_support, roc_auc_score, RocCurveDisplay, mean_absolute_error, mean_squared_error, r2_score, ConfusionMatrixDisplay
from imblearn.pipeline import Pipeline as ImbPipeline
from imblearn.over_sampling import SMOTE
ROOT=Path(__file__).parent; ART=ROOT/'artifacts'; ART.mkdir(exist_ok=True)

def savefig(name): plt.tight_layout(); plt.savefig(ART/name, dpi=130); plt.close()
def metrics(name, model, Xtest, ytest):
    p=model.predict(Xtest); prob=model.predict_proba(Xtest)[:,1]
    a,pr,re,f,_=precision_recall_fscore_support(ytest,p,average='binary',zero_division=0)
    ConfusionMatrixDisplay.from_predictions(ytest,p); savefig(f'{name}_confusion.png')
    RocCurveDisplay.from_predictions(ytest,prob); savefig(f'{name}_roc.png')
    return dict(model=name,accuracy=accuracy_score(ytest,p),precision=pr,recall=re,f1=f,auc=roc_auc_score(ytest,prob))
def main():
    # Sole network/cache load in this module; immediately commit its offline fallback.
    fallback=ROOT/'titanic.csv'
    raw=pd.read_csv(fallback) if fallback.exists() else sns.load_dataset('titanic')
    if not fallback.exists(): raw.to_csv(fallback,index=False)
    report=[f'Shape: {raw.shape}', '## info', str(raw.info()), '## describe', raw.describe(include='all').to_markdown()]
    miss=(raw.isna().mean()*100); report += ['## Missing percentages', miss[miss.gt(0)].round(2).to_markdown()]
    # age (19.87%): median impute; embarked (0.22%): drop rows; deck (77.22%): drop; embark_town follows embarked and is dropped.
    df=raw.drop(columns=['deck','embark_town']).dropna(subset=['embarked']).copy(); df['age']=df.age.fillna(df.age.median())
    for col in ['age','fare']:
        q1,q3=df[col].quantile([.25,.75]); n=((df[col]<q1-1.5*(q3-q1))|(df[col]>q3+1.5*(q3-q1))).sum()
        plt.figure(); sns.histplot(df[col],kde=True); savefig(f'{col}_hist.png'); plt.figure(); sns.boxplot(x=df[col]); savefig(f'{col}_box.png'); report.append(f'{col} IQR outliers: {n}')
    report.append('Fare mean/median/mode: '+str((df.fare.mean(),df.fare.median(),df.fare.mode().iloc[0])))
    # Boolean masking breakdowns
    report += ['## Survival rates', df.groupby('sex').survived.mean().to_markdown(), df.groupby('pclass').survived.mean().to_markdown(), df.groupby(['sex','pclass']).survived.mean().to_markdown()]
    corrcols=['survived','pclass','age','sibsp','parch','fare']; corr=df[corrcols].corr(); report += ['## Correlation',corr.to_markdown()]
    plt.figure(figsize=(7,5)); sns.heatmap(corr,annot=True,cmap='coolwarm'); savefig('correlation.png')
    for name, func in {'sex_survival':lambda: sns.barplot(data=df,x='sex',y='survived'), 'class_survival':lambda: sns.barplot(data=df,x='pclass',y='survived'), 'age_survival':lambda: sns.boxplot(data=df,x='survived',y='age'), 'fare_class':lambda: sns.boxplot(data=df,x='pclass',y='fare')}.items(): plt.figure(); func(); savefig(name+'.png')
    z=(df[['age','fare']]-df[['age','fare']].mean())/df[['age','fare']].std(); report += ['## Z-score check',pd.DataFrame({'before_mean':df[['age','fare']].mean(),'after_mean':z.mean(),'after_std':z.std()}).to_markdown()]
    features=['pclass','sex','age','sibsp','parch','fare','embarked']; X=df[features]; y=df.survived
    Xtr,Xte,ytr,yte=train_test_split(X,y,test_size=.2,stratify=y,random_state=42)
    prep=ColumnTransformer([('num',Pipeline([('impute',SimpleImputer(strategy='median')),('scale',StandardScaler())]),['pclass','age','sibsp','parch','fare']),('cat',Pipeline([('impute',SimpleImputer(strategy='most_frequent')),('onehot',OneHotEncoder(handle_unknown='ignore'))]),['sex','embarked'])])
    models={'logistic':LogisticRegression(max_iter=1000),'tree':DecisionTreeClassifier(random_state=42),'forest':RandomForestClassifier(random_state=42,n_estimators=200)}; rows=[]
    for name,est in models.items():
        pipe=Pipeline([('preprocess',prep),('model',est)]).fit(Xtr,ytr); rows.append(metrics(name,pipe,Xte,yte))
        if name=='tree': plt.figure(figsize=(16,8)); plot_tree(pipe['model'],feature_names=pipe['preprocess'].get_feature_names_out(),class_names=['not survived','survived'],filled=True,max_depth=3); savefig('decision_tree.png')
    # Imbalance comparison: all SMOTE operations occur after splitting, inside the training-only pipeline.
    variants={'baseline':LogisticRegression(max_iter=1000),'balanced':LogisticRegression(max_iter=1000,class_weight='balanced'),'smote':ImbPipeline([('preprocess',prep),('smote',SMOTE(random_state=42)),('model',LogisticRegression(max_iter=1000))])}
    imbalance=[]
    for n,e in variants.items():
        p=e if n=='smote' else Pipeline([('preprocess',prep),('model',e)]); p.fit(Xtr,ytr); imbalance.append(metrics(n,p,Xte,yte))
    grid=GridSearchCV(Pipeline([('preprocess',prep),('model',RandomForestClassifier(random_state=42,oob_score=True))]),{'model__n_estimators':[100,200],'model__max_depth':[None,8],'model__max_features':['sqrt','log2']},cv=3,scoring='f1').fit(Xtr,ytr)
    best=grid.best_estimator_; oob=best['model'].oob_score_; joblib.dump(best,ART/'best_pipeline.joblib'); assert len(joblib.load(ART/'best_pipeline.joblib').predict(Xte.head(2)))==2
    # Regression predicts fare; target is excluded and preprocessing remains train-only.
    rx=df[['pclass','sex','age','sibsp','parch','embarked']]; ry=df.fare; rxtr,rxte,rytr,ryte=train_test_split(rx,ry,test_size=.2,random_state=42)
    rprep=ColumnTransformer([('num',Pipeline([('impute',SimpleImputer(strategy='median')),('scale',StandardScaler())]),['pclass','age','sibsp','parch']),('cat',Pipeline([('impute',SimpleImputer(strategy='most_frequent')),('onehot',OneHotEncoder(handle_unknown='ignore'))]),['sex','embarked'])])
    reg=Pipeline([('preprocess',rprep),('model',LinearRegression())]).fit(rxtr,rytr); pred=reg.predict(rxte); r2=r2_score(ryte,pred); adj=1-(1-r2)*(len(ryte)-1)/(len(ryte)-rxte.shape[1]-1)
    plt.figure(); plt.scatter(pred,ryte-pred,alpha=.5); plt.axhline(0,color='r'); plt.xlabel('Predicted fare'); plt.ylabel('Residual'); savefig('residuals.png')
    report += ['## Classification comparison',pd.DataFrame(rows).round(3).to_markdown(index=False),'## Imbalance comparison',pd.DataFrame(imbalance)[['model','precision','recall','f1']].round(3).to_markdown(index=False),f'Grid best: {grid.best_params_}; OOB={oob:.3f}',f'Regression: MAE={mean_absolute_error(ryte,pred):.3f}, RMSE={mean_squared_error(ryte,pred)**.5:.3f}, R2={r2:.3f}, Adjusted R2={adj:.3f}']
    (ROOT/'results.md').write_text('\n\n'.join(report),encoding='utf8')
if __name__=='__main__': main()
