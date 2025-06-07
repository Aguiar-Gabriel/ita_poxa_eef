import numpy as np
from datetime import datetime, timedelta
import pandas as pd
import re

def parse_wind_info(wind_info):
    wind_direction, wind_speed, wind_status, wind_gust = None, None, None, None

    wind_info = re.sub(r'[^\w\s]', '', wind_info)
    if "at" in wind_info:
        direction_speed = wind_info.split(" at ")

        wind_direction = direction_speed[0]

        if " gusting to " in direction_speed[1]:
            wind_speed = direction_speed[1].split(" gusting to ")
            wind_gust = wind_speed[1]
            wind_speed = wind_speed[0]
            
            wind_gust = np.float64(wind_gust.replace(" knots", ""))
        else:
            wind_speed = direction_speed[1]
    
        wind_speed = np.float64(wind_speed.replace(" knots", ""))
    else:
        wind_status = wind_info

    return wind_direction, wind_speed, wind_status, wind_gust

def get_metar_features(metar, name=""):
    features = {}
    type_of_clouds = ["few", "broken", "overcast", "scattered"]
    
    if name != "":
        name = name + "_"

    # Append time
    features[name+'time'] = metar.time.ctime() or None

    # Append temperature
    if metar.temp is None:
        features[name+'temperature'] = None
    else:
        features[name+'temperature'] = metar.temp.string("C").split()[0] if metar.temp.string("C") else None

    # Append dew point
    if metar.dewpt is None:
        features[name+'dew_point'] = None
    else:
        features[name+'dew_point'] = metar.dewpt.string("C").split()[0] if metar.dewpt.string("C") else None

    # Append wind direction and velocity
    if metar.wind():
        direction, velocity, status, wind_gust = parse_wind_info(metar.wind())
        features[name+'wind_direction'] = direction
        features[name+'wind_velocity'] = velocity
        features[name+'wind_status'] = status
        features["wind_gust"] = wind_gust
    else:
        features[name+'wind_direction'] = None
        features[name+'wind_velocity'] = None
        features[name+'wind_status'] = None
        features["wind_gust"] = None

    # Append peak wind
    features[name+'peak_wind'] = metar.peak_wind() if metar.peak_wind() not in [None, "missing"] else None

    # Append wind shift
    features[name+'wind_shift'] = metar.wind_shift() if metar.wind_shift() not in [None, "missing"] else None

    # Append visibility
    if metar.visibility("M"):
        if 'than' in metar.visibility("M"):
            features[name+'visibility'] = metar.visibility("M").split(' than ')[1].split()[0] if metar.visibility("M") else None
        else:
            features[name+'visibility'] = metar.visibility("M").split()[0] if metar.visibility("M") else None
    else:
        features[name+'visibility'] = None

    # Append runway visual range
    features[name+'runway_visual_range'] = metar.runway_visual_range("M").split()[0] if metar.runway_visual_range("M") else None

    # Append pressure
    if metar.press is None:
        features[name+'pressure'] = None
    else:
        features[name+'pressure'] = metar.press.string("mb").split()[0] if metar.press.string("mb") else None

    # Append present weather
    features[name+'present_weather'] = metar.present_weather() or None

    # Append sky conditions
    if metar.sky_conditions():
        conditions = metar.sky_conditions().split(';')
        for cloud in type_of_clouds:
            cloud_cond = next((cond for cond in conditions if cloud in cond), None)
            if cloud_cond:
                if "at" in cloud_cond:
                    features[name+cloud + '_cloud_height'] = cloud_cond.split(" at ")[1].split()[0] if cloud_cond else None
                else:
                    features[name+cloud + '_cloud_height'] = cloud_cond.split()[0] if cloud_cond else None
            else:
                features[name+cloud + '_cloud_height'] = None
    else:   
        for cloud in type_of_clouds:
            features[name+cloud + '_cloud_height'] = None

    # Append temperature extremes and precipitation
    for attr in ['max_temp_6hr', 'min_temp_6hr', 'max_temp_24hr', 'min_temp_24hr',
                 'precip_1hr', 'precip_3hr', 'precip_6hr', 'precip_24hr',
                 'ice_accretion_1hr', 'ice_accretion_3hr', 'ice_accretion_6hr']:
        features[name+attr] = getattr(metar, attr, None)

    return features


def get_voos_para_o_destino_no_mesmo_horario(destino, voos):
    data_hora = datetime.fromisoformat(destino['hora_ref'])
    data_hora_menos_uma_hora = data_hora - timedelta(hours=1)
    data_hora_mais_uma_hora = data_hora + timedelta(hours=1)


    data_hora_menos_uma_hora_str = data_hora_menos_uma_hora.isoformat()
    data_hora_mais_uma_hora_str = data_hora_mais_uma_hora.isoformat()

    #   Criar uma variavel com todos as linhas nos horarios acima
    voos_proximos = voos[(voos['hora_ref'] == data_hora_menos_uma_hora_str) | (voos['hora_ref'] == data_hora_mais_uma_hora_str) | (voos['hora_ref'] == destino['hora_ref'])]

    #   Retornar  a quantidade de voos em inteiro para a mesma origem do destino no voo proximo

    return voos_proximos[voos_proximos['origem'] == destino['origem']].shape[0]


def fill_na(pos, df, type = "metar"):
    destination = df["destino"].iloc[pos]
    current_time = pd.to_datetime(df["hora_ref"].iloc[pos])

    if type == "metar":
        time_window = ["0h", "1h", "2h", "3h"]
    else:
        time_window = ["0h", "1h", "2h", "3h", "4h", "5h", "6h", "7h", "8h", "9h", "10h", "11h", "12h"]
        
    for time in time_window:

        t_ = current_time - pd.Timedelta(time)
        filter_data = df[(df["destino"] == destination) & (df["hora_ref"] == t_)]
        filter_data = filter_data[[not isinstance(metar, float) for metar in filter_data.metar]]

        if len(filter_data) > 0:
            return list(filter_data.head(1).metar)[0]

        if time != "0h":
            t_ = current_time + pd.Timedelta(time)
            filter_data = df[(df["destino"] == destination) & (df["hora_ref"] == t_)]
            filter_data = filter_data[[not isinstance(metar, float) for metar in filter_data.metar]]

            if len(filter_data) > 0:
                return list(filter_data.head(1).metar)[0]

    return df["metar"].iloc[pos]

def estatistical_features(dataframe, entity, transformation, over_variable, time_window, condition):
      
    # Convert entity column to string if not already
    dataframe[entity] = dataframe[entity].astype(str)
    
    # Convert time column to datetime if not already
    dataframe['hora_ref'] = pd.to_datetime(dataframe['hora_ref'])
    
    # Sort DataFrame by time
    dataframe.sort_values(by='hora_ref', inplace=True)
    
    # Initialize DataFrame to store features
    features = pd.DataFrame()
    
    print("Number of Entities: ", len(dataframe[entity].unique()))
    # Iterate over each unique entity
    compute_features = []
    count_iter = 0

    for entity_value in dataframe[entity].unique():
        # Filter data for the current entity
        entity_data = dataframe[dataframe[entity] == entity_value]
        print(f"Iteration {count_iter} of {len(dataframe[entity].unique())}")

        # Iterate over each unique time within the data of the current entity
        for current_time in entity_data['hora_ref'].unique():
            # Filter data within time window
            time_filtered = entity_data[(entity_data['hora_ref'] >= current_time - pd.Timedelta(time_window)) & 
                                        (entity_data['hora_ref'] <= current_time)]
            
            # Apply additional condition if provided
            if condition is not None:
                time_filtered = time_filtered.query(condition)
            
            # Calculate statistical features for filtered data
            if over_variable:
                stats = transformation(time_filtered[over_variable])
            else:
                stats = transformation(time_filtered)
            
            f_name = f"{transformation.__name__}_{entity}_past_{time_window}" if over_variable == None else f"{transformation.__name__}_{entity}_over_{over_variable}_past_{time_window}"
            # Create a dictionary to hold the feature data
            feature_data = {
                "entity": entity_value,
                "hora_ref": current_time,
                f_name: stats
            }
            
            # Append the feature data to the features DataFrame
            compute_features.append(feature_data)
        count_iter += 1

    features = pd.DataFrame(compute_features)
    return features