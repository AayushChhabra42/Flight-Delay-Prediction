import streamlit as st
import pickle as pk
import sklearn
import requests
import joblib
from datetime import datetime
print(sklearn.__version__)
classifier = joblib.load("my_random_forest.joblib")

def round_off_time(time):
    rounded_time = time.replace(minute=round(time.minute / 60) * 60)
    return rounded_time

def get_params(lat,long,ts):
    url=f"https://api.open-meteo.com/v1/forecast?latitude={lat}&longitude={long}&hourly=temperature_2m,relative_humidity_2m,dew_point_2m,precipitation,wind_speed_10m,wind_speed_120m&forecast_days=7"
    payload={}
    response = requests.request("GET", url, data=payload)
    try:
        api_response=response.json()
        dts = datetime.strftime(ts,"%Y-%m-%dT%H:%M")

        hourly_data = api_response.get("hourly", {})
        timestamps_api = hourly_data.get("time", [])
        temperature_2m = hourly_data.get("temperature_2m", [])
        relative_humidity_2m = hourly_data.get("relative_humidity_2m", [])
        dew_point_2m = hourly_data.get("dew_point_2m", [])
        precipitation = hourly_data.get("precipitation", [])
        wind_speed_10m = hourly_data.get("wind_speed_10m", [])
        wind_speed_120m = hourly_data.get("wind_speed_120m", [])

        data_dict = {}

        # Match the single timestamp and extract corresponding data
        if dts in timestamps_api:
            index = timestamps_api.index(dts)
            data_dict[dts] = {
                "temperature_2m": temperature_2m[index],
                "relative_humidity_2m": relative_humidity_2m[index],
                "dew_point_2m": dew_point_2m[index],
                "precipitation": precipitation[index],
                "wind_speed_10m": wind_speed_10m[index],
                "wind_speed_120m": wind_speed_120m[index]
            }
            return data_dict[dts]
        else:
            print(f"No data available for timestamp {ts}")

            
    except:
        pass

def predict_flight_delay(departure_air,arrival_air,departure_date,departure_time,arrival_date,arrival_time):
    lat_and_long={"DEL":(28.556160,77.100281),"BOM":(19.097403,72.874245),"BLR":(13.199379,77.710136),"CCU":(22.654730,88.446722),"HYD":(17.240263,78.429385),"MAA":(12.9814,80.1641)}
    departure_air=lat_and_long[departure_air]
    arrival_air=lat_and_long[arrival_air]
    departure_time = round_off_time(departure_time)
    arrival_time = round_off_time(arrival_time)
    departure_timestamp=datetime.combine(departure_date,departure_time)
    arrival_timestamp=datetime.combine(arrival_date,arrival_time)
    departure_data=get_params(departure_air[0],departure_air[1],departure_timestamp)
    arrival_data=get_params(arrival_air[0],arrival_air[1],arrival_timestamp)
    input_feats=[[arrival_data['temperature_2m'],arrival_data['relative_humidity_2m'],arrival_data['dew_point_2m'],arrival_data['precipitation'],arrival_data['wind_speed_10m'],arrival_data['wind_speed_120m'],departure_data['temperature_2m'],departure_data['relative_humidity_2m'],departure_data['dew_point_2m'],departure_data['precipitation'],departure_data['wind_speed_10m'],departure_data['wind_speed_120m']]]
    pred=classifier.predict(input_feats)
    return pred


def main():
    st.title("Airline Delay Predictor")
    departure_air=st.selectbox("Enter the airport your are Departing from:",("DEL","BOM","MAA","BLR","HYD","CCU"))
    arrival_air=st.selectbox("Enter the airport your are Arriving to:",("DEL","BOM","MAA","BLR","HYD","CCU"))
    departure_date=st.date_input("Enter Date of Departure:")
    departure_time=st.time_input("Enter Time of Departure:")
    arrival_date=st.date_input("Enter Date of Arrival:")
    arrival_time=st.time_input("Enter Time of Arrival:")
    result=""
    if st.button("Predict"):
        result=predict_flight_delay(departure_air,arrival_air,departure_date,departure_time,arrival_date,arrival_time)
    st.success("The output is {}".format(result[0]))
if __name__=="__main__":
    main()
