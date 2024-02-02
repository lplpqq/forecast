import pandas as pd
from sklearn.linear_model import Ridge

df = pd.read_csv('data.csv')


df['date'] = pd.to_datetime(df['date'], format='%Y-%m-%d %H:%M:%S')

ridge = Ridge(alpha=0.1)
predictors = df.columns[~df.columns.isin(['date', 'clouds'])]


def backtest(weather, model: Ridge, predictors, start, step):
    all_predictions = []

    train = weather.iloc[:990, :]
    test = weather.iloc[990:1000, :]

    model.fit(train[predictors], train['temp'])
    predicted = model.predict(test[predictors])

    # all_predictions.append(combined)

    if all_predictions:
        return pd.concat(all_predictions)


predictions = backtest(df, ridge, predictors, 999, 1)
print(predictions)
# predictions.plot()
# plt.show()
