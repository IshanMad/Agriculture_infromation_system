from flasksystem import app, db  # import our Flask app
from flasksystem.models import User, Farm
from flasksystem import socketio
from apscheduler.schedulers.background import BackgroundScheduler
from werkzeug.utils import secure_filename
import os
# Importing Libary Files
import numpy as np
import pandas as pd
# import matplotlib
# matplotlib.use('Agg')
# from matplotlib import pyplot as plt
# import matplotlib.pyplot as plt
import matplotlib

matplotlib.use('Agg')
import matplotlib.pyplot as plt
import tensorflow
from statsmodels.tools.eval_measures import rmse
# importing skleran libary min max scaler
from sklearn.preprocessing import MinMaxScaler
#
from tensorflow.keras.preprocessing.sequence import TimeseriesGenerator
from tensorflow.keras.models import Sequential
from tensorflow.keras.layers import Dense
from tensorflow.keras.layers import LSTM
from tensorflow.keras.layers import Dropout
import warnings

warnings.filterwarnings("ignore")
import os

basepath = os.path.abspath('Plots')


@app.before_first_request
def predict():
    df = pd.read_csv(r"C:\Users\ish\Desktop\New folder\Aginfo\flasksystem\static\predict\r_consumption.csv")
    df.head()

    df.Month = pd.to_datetime(df.Month)
    df = df.set_index("Month")

    train, test = df[:-12], df[-12:]

    scaler = MinMaxScaler()
    scaler.fit(train)
    train = scaler.transform(train)
    test = scaler.transform(test)

    n_input = 12
    n_features = 1
    generator = TimeseriesGenerator(train, train, length=n_input, batch_size=6)
    model = Sequential()
    model.add(LSTM(200, activation='relu', input_shape=(n_input, n_features)))
    model.add(Dropout(0.15))
    model.add(Dense(1))
    model.compile(optimizer='adam', loss='mse')
    model.fit_generator(generator, epochs=90)
    pred_list = []
    batch = train[-n_input:].reshape((1, n_input, n_features))
    for i in range(n_input):
        pred_list.append(model.predict(batch)[0])
        batch = np.append(batch[:, 1:, :], [[pred_list[i]]], axis=1)
    df_predict = pd.DataFrame(scaler.inverse_transform(pred_list),
                              index=df[-n_input:].index, columns=['Prediction'])
    df_test = pd.concat([df, df_predict], axis=1)
    plt.figure(figsize=(30, 10))
    plt.plot(df_test.index, df_test['Rice Consumnption In MT'])
    plt.plot(df_test.index, df_test['Prediction'], color='r')
    plt.legend(loc='best', fontsize='xx-large')
    plt.xticks(fontsize=18)
    plt.yticks(fontsize=16)
    plt.savefig("myfig.png")

    pred_actual_rmse = rmse(df_test.iloc[-n_input:, [0]], df_test.iloc[-n_input:, [1]])
    print("rmse: ", pred_actual_rmse)
    train = df
    scaler.fit(train)
    train = scaler.transform(train)
    n_input = 12
    n_features = 1
    generator = TimeseriesGenerator(train, train, length=n_input, batch_size=6)
    model.fit_generator(generator, epochs=90)
    pred_list = []
    batch = train[-n_input:].reshape((1, n_input, n_features))
    for i in range(n_input):
        pred_list.append(model.predict(batch)[0])
        batch = np.append(batch[:, 1:, :], [[pred_list[i]]], axis=1)
    from pandas.tseries.offsets import DateOffset
    add_dates = [df.index[-1] + DateOffset(months=x) for x in range(0, 13)]
    future_dates = pd.DataFrame(index=add_dates[1:], columns=df.columns)
    df_predict = pd.DataFrame(scaler.inverse_transform(pred_list),
                              index=future_dates[-n_input:].index, columns=['Prediction'])
    df_proj = pd.concat([df, df_predict], axis=1)
    plt.figure(figsize=(15, 10))
    plt.title('Monthly Rice Consumption Prediction in Kaluthara District')
    plt.xlabel('Year')
    plt.ylabel('Rice Consumption in Metric Tones')
    plt.plot(df_proj.index, df_proj['Rice Consumnption In MT'], label='Actual Consumption')
    plt.plot(df_proj.index, df_proj['Prediction'], color='r', label='Prediction')
    plt.legend(loc='best', fontsize='xx-large')
    plt.xticks(fontsize=18)
    plt.yticks(fontsize=16)
    basepath = os.path.abspath(r'C:\Users\ish\Desktop\Filnal new\AgriInfo\flasksystem\static\ai')
    plt.savefig(os.path.join(basepath, 'fmyfigpredict.jpg'))


# 31536000


if __name__ == '__main__':
    scheduler = BackgroundScheduler()
    scheduler.add_job(predict, 'interval', seconds=31536000)
    scheduler.start()
    # app.run(debug=True)
    socketio.run(app, debug=True)
