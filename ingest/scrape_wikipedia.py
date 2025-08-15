import requests
from bs4 import BeautifulSoup
import unicodedata
import pandas as pd

def date_time(table_cells):
    return [data_time.strip() for data_time in list(table_cells.strings)][0:2]

def booster_version(table_cells):
    out = ''.join([booster_version for i, booster_version in enumerate(table_cells.strings) if i % 2 == 0][0:-1])
    return out

def landing_status(table_cells):
    out = [i for i in table_cells.strings][0]
    return out

def get_mass(table_cells):
    mass = unicodedata.normalize("NFKD", table_cells.text).strip()
    if mass:
        new_mass = mass[0:mass.find("kg") + 2]
    else:
        new_mass = 0
    return new_mass

def extract_column_from_header(row):
    if row.br:
        row.br.extract()
    if row.a:
        row.a.extract()
    if row.sup:
        row.sup.extract()
    column_name = ' '.join(row.contents)
    if not column_name.strip().isdigit():
        return column_name.strip()

def main():
    static_url = "https://en.wikipedia.org/w/index.php?title=List_of_Falcon_9_and_Falcon_Heavy_launches&oldid=1027686922"

    html_data = requests.get(static_url)
    if html_data.status_code != 200:
        print(f"erro ao acessar a página: {html_data.status_code}")
        return

    soup = BeautifulSoup(html_data.text, 'html5lib')
    html_tables = soup.find_all('table')
    first_launch_table = html_tables[2]
    print(first_launch_table)

    headers = first_launch_table.find_all('th')
    column_names = [extract_column_from_header(h) for h in headers if extract_column_from_header(h)]
    print(column_names)

    launch_dict = {
        'Flight No.': [],
        'Date': [],
        'Time': [],
        'Version Booster': [],
        'Launch site': [],
        'Payload': [],
        'Payload mass': [],
        'Orbit': [],
        'Customer': [],
        'Launch outcome': [],
        'Booster landing': []
    }

    extracted_row = 0

    for table_number, table in enumerate(soup.find_all('table', "wikitable plainrowheaders collapsible")):
        for rows in table.find_all("tr"):
            if rows.th and rows.th.string and rows.th.string.strip().isdigit():
                flight_number = rows.th.string.strip()
                row = rows.find_all('td')
                extracted_row += 1

                datatimelist = date_time(row[0])
                date = datatimelist[0].strip(',')
                time = datatimelist[1]

                bv = booster_version(row[1])
                if not bv:
                    bv = row[1].a.string if row[1].a else ""

                launch_site = row[2].a.string if row[2].a else ""
                payload = row[3].a.string if row[3].a else ""
                payload_mass = get_mass(row[4])
                orbit = row[5].a.string if row[5].a else ""

                # nem sempre o campo de customer é um link
                try:
                    customer = row[6].a.string
                except:
                    customer = 'Various'

                launch_outcome = list(row[7].strings)[0]
                booster_landing = landing_status(row[8])

                # preenche os dados no dicionário
                launch_dict['Flight No.'].append(flight_number)
                launch_dict['Date'].append(date)
                launch_dict['Time'].append(time)
                launch_dict['Version Booster'].append(bv)
                launch_dict['Launch site'].append(launch_site)
                launch_dict['Payload'].append(payload)
                launch_dict['Payload mass'].append(payload_mass)
                launch_dict['Orbit'].append(orbit)
                launch_dict['Customer'].append(customer)
                launch_dict['Launch outcome'].append(launch_outcome)
                launch_dict['Booster landing'].append(booster_landing)

    df = pd.DataFrame(launch_dict)
    df.to_csv('data/raw/spacex_web_scraped.csv', index=False)
    print(f"\n{extracted_row} linhas extraídas e salvas em data/raw/spacex_web_scraped.csv")

if __name__ == "__main__":
    main()