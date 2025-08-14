import requests
import pandas as pd
import numpy as np
import datetime

# Configurações do pandas para exibir tudo
pd.set_option('display.max_columns', None)
pd.set_option('display.max_colwidth', None)
# Funções auxiliares de scraping da API
def getBoosterVersion(data):
    for x in data['rocket']:
        response = requests.get("https://api.spacexdata.com/v4/rockets/" + str(x)).json()
        BoosterVersion.append(response['name'])

def getLaunchSite(data):
    for x in data['launchpad']:
        response = requests.get("https://api.spacexdata.com/v4/launchpads/" + str(x)).json()
        Longitude.append(response['longitude'])
        Latitude.append(response['latitude'])
        LaunchSite.append(response['name'])

def getPayloadData(data):
    for load in data['payloads']:
        response = requests.get("https://api.spacexdata.com/v4/payloads/" + load).json()
        PayloadMass.append(response['mass_kg'])
        Orbit.append(response['orbit'])

def getCoreData(data):
    for core in data['cores']:
        if core['core'] is not None:
            response = requests.get("https://api.spacexdata.com/v4/cores/" + core['core']).json()
            Block.append(response['block'])
            ReusedCount.append(response['reuse_count'])
            Serial.append(response['serial'])
        else:
            Block.append(None)
            ReusedCount.append(None)
            Serial.append(None)

        Outcome.append(str(core['landing_success']) + ' ' + str(core['landing_type']))
        Flights.append(core['flight'])
        GridFins.append(core['gridfins'])
        Reused.append(core['reused'])
        Legs.append(core['legs'])
        LandingPad.append(core['landpad'])

def main():
    spacex_url = "https://api.spacexdata.com/v4/launches/past"
    response = requests.get(spacex_url)
    print(f"📡 Status da API: {response.status_code}")

    data = pd.json_normalize(response.json())

    # Subconjunto de colunas
    data = data[['rocket', 'payloads', 'launchpad', 'cores', 'flight_number', 'date_utc']]
    data = data[data['cores'].map(len) == 1]
    data = data[data['payloads'].map(len) == 1]
    data['cores'] = data['cores'].map(lambda x: x[0])
    data['payloads'] = data['payloads'].map(lambda x: x[0])
    data['date'] = pd.to_datetime(data['date_utc']).dt.date
    data = data[data['date'] <= datetime.date(2020, 11, 13)]

    # Variáveis globais
    global BoosterVersion, PayloadMass, Orbit, LaunchSite, Outcome, Flights, GridFins, Reused, Legs, LandingPad, Block, ReusedCount, Serial, Longitude, Latitude
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

    # Coleta de dados estendidos
    print("🚀 Coletando dados dos boosters...")
    getBoosterVersion(data)
    print("📡 Coletando dados dos launchpads...")
    getLaunchSite(data)
    print("📦 Coletando dados dos payloads...")
    getPayloadData(data)
    print("🧱 Coletando dados dos cores...")
    getCoreData(data)

    # Construção do dataset
    launch_dict = {
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

    df = pd.DataFrame.from_dict(launch_dict)

    # Filtra apenas Falcon 9
    df = df[df['BoosterVersion'] != 'Falcon 1']

    # Recalcula os números de voo
    df.loc[:, 'FlightNumber'] = list(range(1, df.shape[0] + 1))

    # Imputa valores ausentes na massa com a média
    payload_mass_mean = df['PayloadMass'].mean()
    df['PayloadMass'].replace(np.nan, payload_mass_mean, inplace=True)

    # Salva o dataset
    df.to_csv("data/raw/dataset_part_1.csv", index=False)
    print("✅ Arquivo salvo em: data/raw/dataset_part_1.csv")
    print(df.head())

if __name__ == "__main__":
    main()