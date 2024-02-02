import asyncio
from datetime import datetime, timedelta

import pandas as pd
from sklearn.model_selection import train_test_split
from sklearn.preprocessing import MinMaxScaler
from sqlalchemy import select
from tensorflow.keras.layers import LSTM, Dense
from tensorflow.keras.models import Sequential

from forecast.api.dependencies import InjectedDBSesssion
from forecast.db.models import WeatherJournal


class WeatherPredictor:
    def __init__(self):
        self.model = None
        self.scaler_x = None
        self.scaler_y = None
        self.trained = False

    async def train(self):
        timeframe = datetime.now() - timedelta(days=4)

        df = pd.read_csv('data.csv')
        df['date'] = pd.to_datetime(df['date'])

        df['year'] = df['date'].dt.year
        df['month'] = df['date'].dt.month
        df['day'] = df['date'].dt.day
        df['hour'] = df['date'].dt.hour

        x = df[['year', 'month', 'day', 'hour']].values
        y = df[['temp', 'pres', 'wspd', 'wdir']].values

        self.scaler_x = MinMaxScaler(feature_range=(0, 1))
        self.scaler_y = MinMaxScaler(feature_range=(0, 1))
        x_scaled = self.scaler_x.fit_transform(x)
        y_scaled = self.scaler_y.fit_transform(y)

        x_reshaped = x_scaled.reshape((x_scaled.shape[0], 1, x_scaled.shape[1]))

        x_train, x_test, y_train, y_test = train_test_split(
            x_reshaped, y_scaled, test_size=0.2, random_state=42
        )

        self.model = Sequential([
            LSTM(50, activation='relu', input_shape=(x_train.shape[1], x_train.shape[2])),
            Dense(4)
        ])
        self.model.compile(optimizer='adam', loss='mean_squared_error')
        self.model.fit(x_train, y_train, epochs=10, batch_size=32, verbose=2)

    def predict(self, date: datetime):
        new_date_scaled = self.scaler_x.transform(
            [[date.year, date.month, date.day, date.hour]]
        )
        new_date_reshaped = new_date_scaled.reshape(
            (new_date_scaled.shape[0], 1, new_date_scaled.shape[1])
        )
        predictions_scaled = self.model.predict(new_date_reshaped)
        predictions = self.scaler_y.inverse_transform(predictions_scaled)
        return predictions

    async def __call__(self, date: datetime):
        if self.trained:
            return self.predict(date)
        else:
            await self.train()
            self.trained = True
            return await self.__call__(date)


async def main():
    predictor = WeatherPredictor()
    print(
        await predictor(datetime(2020, 2, 12, 0))
    )


asyncio.run(main())
