import os
import time
import random
import requests
import pandas as pd
from bs4 import BeautifulSoup

def run_scraper(output_path: str = 'scripts/data/Articulos.csv') -> pd.DataFrame:
    headers = {
        'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/119.0.0.0 Safari/537.36'
    }

    secciones = ['ocio', 'viajes', 'shopping', 'educacion', 'salud', 'estilo-de-vida']
    ciudades = ['madrid', 'barcelona', 'valencia', 'malaga', 'sevilla', 'zaragoza']
    
    articulos = []
    urls_por_ciudad = {ciudad: set() for ciudad in ciudades}

    def get_request_with_retries(url: str, retries: int = 3, timeout: int = 20) -> requests.Response | None:
        for intento in range(retries):
            try:
                response = requests.get(url, headers=headers, timeout=timeout)
                if response.status_code == 200:
                    return response
                else:
                    print(f"⚠️ Status {response.status_code} en {url}")
            except Exception as e:
                print(f"⚠️ Intento {intento + 1} fallido para {url}: {e}")
            time.sleep(2)
        return None

    for ciudad in ciudades:
        for seccion in secciones:
            print(f"\n🔎 Visitando ciudad: {ciudad.upper()} - sección: {seccion.upper()}")
            for pagina in range(1, 6):
                url = f'https://quehacerconlosninos.es/{ciudad}/{seccion}/' if pagina == 1 else f'https://quehacerconlosninos.es/{ciudad}/{seccion}/page/{pagina}/'

                try:
                    res = requests.get(url, headers=headers, timeout=10)
                    if res.status_code != 200:
                        print(f'❌ No se pudo acceder a {url}')
                        break

                    soup = BeautifulSoup(res.text, 'html.parser')
                    titulos = soup.find_all('h3', class_='elementor-post__title')
                    if not titulos:
                        print(f"⚠️ No hay más artículos en {ciudad}/{seccion} página {pagina}.")
                        break

                    for t in titulos:
                        titulo = t.get_text(strip=True)
                        link = t.find('a')['href']
                        if link in urls_por_ciudad[ciudad]:
                            print(f"⏭️ Ya extraído en {ciudad}: {link}")
                            continue

                        res_art = get_request_with_retries(link)
                        if not res_art:
                            print(f"❌ Fallo en los reintentos para: {link}")
                            continue

                        soup_art = BeautifulSoup(res_art.text, 'html.parser')
                        content = soup_art.find('div', class_='elementor-widget-theme-post-content')
                        if not content:
                            print(f"⚠️ No se encontró contenido en: {link}")
                            continue

                        parrafos = content.find_all('p')
                        texto = " ".join(p.get_text(strip=True) for p in parrafos).strip()
                        if not texto:
                            print(f"⚠️ Contenido vacío: {titulo}")
                            continue

                        articulos.append({
                            'ciudad': ciudad,
                            'seccion': seccion,
                            'titulo': titulo,
                            'url': link,
                            'contenido': texto
                        })
                        urls_por_ciudad[ciudad].add(link)
                        print(f"✅ Extraído: {titulo}")
                        time.sleep(random.uniform(1.0, 2.0))

                except Exception as e:
                    print(f"❌ Error accediendo a {url}: {e}")
                    break

    df = pd.DataFrame(articulos)
    df.to_csv(output_path, index=False)
    print(f"📝 CSV guardado en: {output_path} ({len(df)} registros)")
    return df

import re
import pandas as pd
from datetime import datetime

# Expresiones regulares y diccionario
regex_fechas = r"(?:\b(?:lunes|martes|miércoles|jueves|viernes|sábado|domingo)\s*)?\b\d{1,2}\s+de\s+(?:enero|febrero|marzo|abril|mayo|junio|julio|agosto|septiembre|octubre|noviembre|diciembre)(?:\s+de\s+\d{4})?"
regex_precios = r"\d+(?:[\.,]\d+)? ?€"
meses = {
    "enero": 1, "febrero": 2, "marzo": 3, "abril": 4,
    "mayo": 5, "junio": 6, "julio": 7, "agosto": 8,
    "septiembre": 9, "octubre": 10, "noviembre": 11, "diciembre": 12
}

# Funciones auxiliares
def extraer_fechas_separadas(texto):
    fechas = re.findall(regex_fechas, texto, flags=re.IGNORECASE)
    if not fechas:
        return None, None
    elif len(fechas) == 1:
        return fechas[0], fechas[0]
    else:
        return fechas[0], fechas[1]

def extraer_precio(texto):
    if pd.isnull(texto):
        return "No especificado"
    texto = texto.lower()
    if "gratis" in texto:
        return "Gratis"
    precios = re.findall(regex_precios, texto)
    return precios[0].replace(" ", "") if precios else "No especificado"

def corregir_texto(texto):
    texto = re.sub(r'([a-zA-Z])(\d)', r'\1 \2', texto)
    texto = re.sub(r'(\d)([a-zA-Z])', r'\1 \2', texto)
    return texto

def extraer_fecha_contexto_basico(texto):
    if pd.isnull(texto):
        return None
    texto = texto.lower()
    patrones = re.findall(r"(\d{1,2}) de (\w+)(?: de (\d{4}))?", texto)
    if not patrones:
        return None

    for dia, mes_nombre, año in patrones:
        mes = meses.get(mes_nombre)
        if mes is None:
            continue
        año = int(año) if año else datetime.today().year
        try:
            fecha = datetime(año, mes, int(dia))
            hoy = datetime.today()
            return {
                "fecha_normalizada": fecha.strftime("%Y-%m-%d"),
                "dia_semana": fecha.strftime("%A"),
                "mes": fecha.strftime("%B"),
                "año": año,
                "es_este_mes": fecha.month == hoy.month and fecha.year == hoy.year,
                "es_este_fin_de_semana": fecha.weekday() in [5, 6] and 0 <= (fecha - hoy).days <= 7
            }
        except ValueError:
            continue
    return None

def extraer_ciudad(texto):
    ciudades = ['Madrid', 'Barcelona', 'Valencia', 'Málaga', 'Sevilla', 'Zaragoza']
    patron = r'\b(?:' + '|'.join(ciudades) + r')\b'
    coincidencias = re.findall(patron, texto, flags=re.IGNORECASE)
    return coincidencias[0].capitalize() if coincidencias else None

# Función principal
def procesar_articulos(input_path: str = 'scripts/data/Articulos.csv', output_path: str = 'scripts/data/Articulos_limpios.csv') -> pd.DataFrame:
    df = pd.read_csv(input_path)

    # Corrección de texto
    df['contenido'] = df['contenido'].fillna('').apply(corregir_texto)

    # Extracción de fechas
    df[['fecha_inicio', 'fecha_fin']] = df['contenido'].apply(lambda x: pd.Series(extraer_fechas_separadas(x)))

    # Extracción de fecha contextual
    contexto = df['contenido'].apply(extraer_fecha_contexto_basico)
    df['fecha_normalizada'] = contexto.apply(lambda x: x['fecha_normalizada'] if x else None)
    df['dia_semana'] = contexto.apply(lambda x: x['dia_semana'] if x else None)
    df['mes'] = contexto.apply(lambda x: x['mes'] if x else None)
    df['año'] = contexto.apply(lambda x: x['año'] if x else None)
    df['es_este_mes'] = contexto.apply(lambda x: x['es_este_mes'] if x else None)
    df['es_este_fin_de_semana'] = contexto.apply(lambda x: x['es_este_fin_de_semana'] if x else None)

    # Extracción de precio
    df['precio'] = df['contenido'].apply(extraer_precio)

    # Validación o corrección de ciudad
    df['ciudad_detectada'] = df['contenido'].apply(extraer_ciudad)

    # Guardar resultado
    df.to_csv(output_path, index=False)
    print(f"🧹 CSV limpio guardado en: {output_path} ({len(df)} registros)")
    return df

if __name__ == "__main__":
    run_scraper()
    procesar_articulos(
        input_path='scripts/data/Articulos.csv',
        output_path='scripts/data/Articulos_limpios.csv'  # Usa el nombre estándar que espera el resto del flujo
    )


