import json
from sys import stderr
from unittest.mock import Base
import requests as reqs
from requests.exceptions import ConnectionError, BaseHTTPError
from urllib3.exceptions import NewConnectionError, MaxRetryError

from pandas import DataFrame, ExcelWriter


def write_estados():
    filename = 'inegi_agem_07.json'

    df_municipios = DataFrame(columns = [
        'Clave Estado', 
        'Clave Municipio', 
        'Nombre Municipio'])

    with open(filename, 'r') as f:
        root = json.load(f)

        municipios = root['features']

        for municipio in municipios:
            df_municipios.loc[int(municipio['properties']['cvegeo'])] = [
                int(municipio['properties']['cve_agee']),
                int(municipio['properties']['cve_agem']),
                municipio['properties']['nom_agem']
            ]
        
    with ExcelWriter('/media/usb/WebRealm/Datos/datos_webrealm.xlsx', mode='a') as writer:
        df_municipios.to_excel(writer, sheet_name="MunicipiosChiapas")
    
    return 0


def get_estados() -> list:
    # La variable donde se guardarán los resultados.
    list_estados = []

    # URL Base para todas las consultas de Área GeoEstadística Estatal (AGEE)
    base_url = 'https://gaia.inegi.org.mx/wscatgeo/mgee/'

    # El resultado de la consulta se guarda en la raviable response.
    # TODO: Implementar try/except para manejar posibles errores.
    try:
        response = reqs.get(base_url)
    except:
        raise
    else:
        # Primero verificar si el código de respuesta de la consulta fue exitoso.
        if response.status_code == 200:
            estados = response.json()['datos']

            for estado in estados:
                list_estados.append({
                    'clave': estado['cve_agee'],
                    'nombre': estado['nom_agee'],
                    'abreviatura_nombre': estado['nom_abrev'],
                    'poblacion_total': estado['pob'],
                    'poblacion_femenina': estado['pob_fem'],
                    'poblacion_masculina': estado['pob_mas'],
                    'viviendas_totales_habitadas': estado['viv']
                })
    
        return list_estados


def get_municipios_by_clave_estado(clave_estado: int) -> list:
    # Se crea una lista vacía para guardar los municipios recuperados.
    list_municipios = []

    # URL Base para todas las consultas de Área GeoEstadística Municipal (AGEM)
    base_url = 'https://gaia.inegi.org.mx/wscatgeo/geo/mgem/'

    # Se agrega la clave del estado (a dos dígitos, rellenando con '0' a la 
    # izquierda sin es necesario), al final de la URL Base.
    query_url = '{}{:02}'.format(base_url, clave_estado)

    # El resultado de la consulta se guarda en la variable response.
    # TODO: implementar try /except para manejar posibles errores.
    try:
        response = reqs.get(query_url)
    except:
        raise
    else:
        if response.status_code == 200:
            # De la respuesta se extrae únicamente la rama que nos interesa.
            municipios = response.json()['features']

            # Por cada municipio úncamente extraemos los datos que nos interesan
            # y los agregamos a un diccionario que ponemos al final de la lista de
            # municipios.
            for municipio in municipios:
                list_municipios.append({
                    'clave': int(municipio['properties']['cvegeo']),
                    'nombre': municipio['properties']['nom_agem'],
                    'poblacion_total': int(municipio['properties']['pob']),
                    'poblacion_femenina': int(municipio['properties']['pob_fem']),
                    'poblacion_masculina': int(municipio['properties']['pob_mas']),
                    'viviendas_totales_habitadas': int(municipio['properties']['viv'])
                })
            
        # Devolvemos la lista de municipios ya poblada con los datos recuperados
        # del catálogo del INEGI.
        return list_municipios


if __name__ == '__main__':
    l_estados = []
    
    l_estados = get_estados()

    for estado in l_estados:
        print('{} {}'.format(estado['clave'], estado['nombre']))

    while True:    
        print('Clave del Estado: ', end='')
        str_clave_estado = input();

        try:
            int_clave_estado = int(str_clave_estado)
            if int_clave_estado == 0:
                break;
            elif int_clave_estado < 1 or int_clave_estado > 32:
                raise ValueError('La clave del Estado debe estar entre 1 y 32, incusive.')
            else:
                list_municipios = get_municipios_by_clave_estado(int_clave_estado)
                for municipio in list_municipios:
                    print('{clave} {nombre} {poblacion_total:,}'.format(**municipio))
        except (ConnectionError, BaseHTTPError, NewConnectionError, MaxRetryError) as e:
            stderr.write('Error de conección al servicio web de INEGI.\n')
            break;
        except:
            stderr.write('Error desconocido.')
            break;
