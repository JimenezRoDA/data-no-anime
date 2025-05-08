import pandas as pd
import ast
import numpy as np
import matplotlib.pyplot as plt
import os
import pandas as pd
import json
import requests
from bs4 import BeautifulSoup
import time

def obtener_animes_top(limit=5550, step=50, delay=1):
    animes = []

    for offset in range(0, limit, step):
        url = f"https://myanimelist.net/topanime.php?limit={offset}"
        response = requests.get(url)
        soup = BeautifulSoup(response.text, 'html.parser')

        lista = soup.find_all('tr', class_='ranking-list')

        for anime in lista:
            title_tag = anime.find('h3', class_='anime_ranking_h3')
            title = title_tag.text.strip() if title_tag else None

            info_div = anime.find('div', class_='information di-ib mt4')
            fecha_emision = None
            if info_div:
                lines = info_div.text.strip().split('\n')
                if len(lines) >= 2:
                    fecha_emision = lines[1].strip()

            animes.append({
                'title': title,
                'fecha_emision': fecha_emision
            })

        time.sleep(delay)  # Pausa para evitar sobrecargar el servidor

    return pd.DataFrame(animes)

def get_popular_animes(limit=5550):
    url = 'https://api.jikan.moe/v4/anime'
    animes = []
    page = 1
    per_page = 25

    while len(animes) < limit:
        response = requests.get(url, params={'page': page, 'limit': per_page})
        print(f"Página {page}, Código: {response.status_code}")

        if response.status_code == 200:
            data = response.json()
            if not data.get('data'):
                print("No hay más datos.")
                break

            animes.extend(data['data'])
            print(f"Total recolectado: {len(animes)}")
            page += 1
            time.sleep(1)  # 🛑 Espera obligatoria para evitar rate limit
        elif response.status_code == 429:
            print("⚠️ Rate limit alcanzado. Esperando 10 segundos...")
            time.sleep(10)  # Espera más larga para recuperarse
        else:
            print(f"❌ Error en página {page}: {response.text}")
            break

    return animes

def extraer_nombres_generos(entrada):
    if pd.isna(entrada) or entrada == '[]':
        return []
    try:
        lista_dicts = ast.literal_eval(entrada) 
        return [d['name'] for d in lista_dicts]
    except:
        return []
    
def contar_generos(df, col1, col2):
    generos = pd.concat([df[col1], df[col2]])
    conteo = generos.value_counts().reset_index()
    conteo.columns = ['Género', 'Frecuencia']
    return conteo

def media_puntuaciones(df, col1, col2, score_col):
    generos = pd.concat([
        df[[col1, score_col]].rename(columns={col1: 'Género'}),
        df[[col2, score_col]].rename(columns={col2: 'Género'})
    ])
    return generos.groupby('Género')[score_col].mean().reset_index()

def media_puntuaciones_origen(df, source_col, score_col):
    origen = df[[source_col, score_col]].dropna()
    origen['Origen'] = origen[source_col]
    return origen.groupby('Origen')[score_col].mean().reset_index()

