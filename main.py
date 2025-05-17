from datetime import datetime, timedelta
import plotly.express as plt
import streamlit as st
import pandas as pd
import requests

def load_option():
    infos = pd.read_csv('items.txt', sep=' : ', names=['Id_item', 'Item_name'])

    infos['Id_item'] = infos['Id_item'].str.replace(r'\s+', '', regex=True)
    infos['Level'] = infos['Id_item'].str.extract(r'(T\d+)')
    infos['Quality'] = infos['Id_item'].apply(lambda x: x[-1:])
    infos['Quality'] = infos['Quality'].str.replace(r'[a-zA-Z]+', '0', regex=True)
    
    return infos

def api_consult(base):
    hj = datetime.now()
    bg = hj - timedelta(days=90)

    url = f'https://west.albion-online-data.com/api/v2/stats/history/{','.join(id_tag for id_tag in base['Id_item'].tolist())}.json?date={bg.strftime('%d-%m-%Y')}&end_date={hj.strftime('%d-%m-%Y')}&locations=Caerleon,Bridgewatch,Lymhurst,Martlock,Thetford,FortSterling&time-scale=24'
    response = requests.get(url)

    if response.status_code == 200:
        data=response.json()

    else:
        print(f"Something failed, here is the erro {response.status_code}")

    df = pd.DataFrame()
    for i in range(len(data)):
        bs = pd.DataFrame(data[i]['data'])
        bs['location'] = data[i]['location']
        bs['item_id'] = data[i]['item_id']
        bs['quality'] = data[i]['quality']

        df = pd.concat([df, bs], ignore_index=True)

    try:
        df['timestamp'] = pd.to_datetime(df['timestamp'])
        df = df.sort_values('timestamp', ascending=False)

        df = pd.merge(df, base, 'inner', left_on='item_id', right_on='Id_item')


        return df[['location', 'item_id', 'Item_name', 'quality', 'item_count', 'avg_price', 'timestamp']]

    except:
        st.subheader(f"Item not found :cry:")
        return 0

st.title('Albion Maket Consult')

items = load_option()

name_select = st.multiselect(
    "SELECT ITEM NAME",
    items['Item_name'].unique(),
    max_selections=5
)

selected = items.loc[items['Item_name'].isin(name_select)]

if len(selected) > 1:
    level_select = st.multiselect(
        "ITEM LEVEL",
        selected['Level'].unique(),
        max_selections=5
    )

    selected = items.loc[(items['Item_name'].isin(name_select)) & (items['Level'].isin(level_select))]

    if len(selected['Quality'].unique()) > 1:
        quality_select = st.multiselect(
            "QUALITY",
            selected['Quality'].unique(),
            max_selections=5
        )

        selected = items.loc[(items['Item_name'].isin(name_select)) & (items['Level'].isin(level_select)) & (items['Quality'].isin(quality_select))]
    
if st.button("Consult"):
    base= api_consult(selected)
    if base != 0:
        items_ = base['Item_name'].unique()

        for item in items_:
            fig = plt.line(base.loc[base['Item_name'] == item], 'timestamp', 'avg_price', color='location', title=item)
            st.write(fig)
    else:
        pass
