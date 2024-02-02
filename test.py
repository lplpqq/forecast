import pandas as pd
from sklearn.model_selection import train_test_split
from sklearn.preprocessing import MinMaxScaler
from tensorflow.keras.models import Sequential
from tensorflow.keras.layers import LSTM, Dense


file_path = 'data.csv'
data = pd.read_csv(file_path, index_col='date', parse_dates=True)

data['year'] = data.index.year
data['month'] = data.index.month
data['day'] = data.index.day
data['hour'] = data.index.hour

y = data[['temp', 'pres', 'wspd', 'rhum']].values
X = data[['year', 'month', 'day', 'hour']].values

scaler_X = MinMaxScaler(feature_range=(0, 1))
scaler_Y = MinMaxScaler(feature_range=(0, 1))
X_scaled = scaler_X.fit_transform(X)
y_scaled = scaler_Y.fit_transform(y)

X_reshaped = X_scaled.reshape((X_scaled.shape[0], 1, X_scaled.shape[1]))

X_train, X_test, y_train, y_test = train_test_split(X_reshaped, y_scaled, test_size=0.2, random_state=42)

model = Sequential([
    LSTM(50, activation='relu', input_shape=(X_train.shape[1], X_train.shape[2])),
    Dense(4)  # Output layer for four parameters
])
model.compile(optimizer='adam', loss='mean_squared_error')

model.fit(X_train, y_train, epochs=200, batch_size=32, verbose=2)


for i in range(25):
    new_date_data = [[2020, 2, i, 0]]

    new_date_scaled = scaler_X.transform(new_date_data)
    new_date_reshaped = new_date_scaled.reshape((new_date_scaled.shape[0], 1, new_date_scaled.shape[1]))
    predictions_scaled = model.predict(new_date_reshaped)
    predictions = scaler_Y.inverse_transform(predictions_scaled)
    print(f"Predicted Temperature: {predictions}")
