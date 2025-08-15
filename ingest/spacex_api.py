import requests
import pandas as pd
import numpy as np
import datetime

pd.set_option('display.max_columns', None)
pd.set_option('display.max_colwidth', None)

def get_booster_versions(data):
    for rocket_id in data['rocket']:
        res = requests.get(f"https://api.spacexdata.com/v4/rockets/{rocket_id}").json()
        BoosterVersion.append(res['name'])

def get_launch_sites(data):
    for launchpad_id in data['launchpad']:
        res = requests.get(f"https://api.spacexdata.com/v4/launchpads/{launchpad_id}").json()
        Longitude.append(res['longitude'])
        Latitude.append(res['latitude'])
        LaunchSite.append(res['name'])

def get_payload_data(data):
    for payload_id in data['payloads']:
        res = requests.get(f"https://api.spacexdata.com/v4/payloads/{payload_id}").json()
        PayloadMass.append(res['mass_kg'])
        Orbit.append(res['orbit'])

def get_core_data(data):
    for core in data['cores']:
        if core['core'] is not None:
            res = requests.get(f"https://api.spacexdata.com/v4/cores/{core['core']}").json()
            Block.append(res['block'])
            ReusedCount.append(res['reuse_count'])
            Serial.append(res['serial'])
        else:
            Block.append(None)
            ReusedCount.append(None)
            Serial.append(None)

        # mesmo quando não tem core, ainda dá pra salvar dados de pouso
        Outcome.append(f"{core['landing_success']} {core['landing_type']}")
        Flights.append(core['flight'])
        GridFins.append(core['gridfins'])
        Reused.append(core['reused'])
        Legs.append(core['legs'])
        LandingPad.append(core['landpad'])

def main():
    print("buscando dados de lançamentos passados da spacex...")
    url = "https://api.spacexdata.com/v4/launches/past"
    response = requests.get(url)

    if response.status_code != 200:
        print(f"erro ao acessar a api. status: {response.status_code}")
        return

    data = pd.json_normalize(response.json())
    print("dados carregados com sucesso.")

    data = data[['rocket', 'payloads', 'launchpad', 'cores', 'flight_number', 'date_utc']]
    data = data[data['cores'].map(len) == 1]
    data = data[data['payloads'].map(len) == 1]
    data['cores'] = data['cores'].map(lambda x: x[0])
    data['payloads'] = data['payloads'].map(lambda x: x[0])
    data['date'] = pd.to_datetime(data['date_utc']).dt.date

    # corte até o fim de 2020 pra manter consistência com análises anteriores
    data = data[data['date'] <= datetime.date(2020, 11, 13)]

    global BoosterVersion, PayloadMass, Orbit, LaunchSite, Outcome
    global Flights, GridFins, Reused, Legs, LandingPad
    global Block, ReusedCount, Serial, Longitude, Latitude

    BoosterVersion = []
    PayloadMass = []
    Orbit = []
    LaunchSite = []
    Outcome = []
    Flights = []
    GridFins = []
    Reused = []
    Legs = []
    LandingPad = []
    Block = []
    ReusedCount = []
    Serial = []
    Longitude = []
    Latitude = []

    print("coletando dados dos boosters...")
    get_booster_versions(data)

    print("coletando dados dos launchpads...")
    get_launch_sites(data)

    print("coletando dados dos payloads...")
    get_payload_data(data)

    print("coletando dados dos cores...")
    get_core_data(data)

    print("montando o dataframe final...")
    launch_data = {
        'FlightNumber': list(data['flight_number']),
        'Date': list(data['date']),
        'BoosterVersion': BoosterVersion,
        'PayloadMass': PayloadMass,
        'Orbit': Orbit,
        'LaunchSite': LaunchSite,
        'Outcome': Outcome,
        'Flights': Flights,
        'GridFins': GridFins,
        'Reused': Reused,
        'Legs': Legs,
        'LandingPad': LandingPad,
        'Block': Block,
        'ReusedCount': ReusedCount,
        'Serial': Serial,
        'Longitude': Longitude,
        'Latitude': Latitude
    }

    df = pd.DataFrame.from_dict(launch_data)

    # removendo falcon 1 pra focar nos voos do falcon 9
    df = df[df['BoosterVersion'] != 'Falcon 1']

    df['FlightNumber'] = range(1, len(df) + 1)

    # imputando massa média onde estiver ausente
    payload_avg = df['PayloadMass'].mean()
    df['PayloadMass'].fillna(payload_avg, inplace=True)

    output_path = "data/raw/dataset_part_1.csv"
    df.to_csv(output_path, index=False)
    print(f"arquivo salvo em: {output_path}")
    print(df.head())

if __name__ == "__main__":
    main()