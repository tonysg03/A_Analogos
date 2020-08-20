#!/usr/bin/env python
# coding: utf-8
"""
Created on Fri Jun 19 18:27:53 2020

@author: Anthony Segura García

@contact: anthony.seguragarcia@ucr.ac.cr
          asegura@imn.ac.cr

Departamento de Red Meteorológica y Procesamiento de Datos
Instituto Meteorológico Nacional

"""

# Años Análogos

# In[1]:


import requests
import urllib
from bs4 import BeautifulSoup
import pandas as pd
import numpy as np
from scipy.stats import pearsonr
import matplotlib.pyplot as plt


# In[2]:


#Código realizado por ***Daniel Poleo Brito***, profesor de la UCR y pronosticador del IMN para el acceso de datos
#de la oscilación AMO vía web y acomodo de los datos en el archivo de salida.

def acomodaParaCSV(rutaArchivoEntrada, rutaArchivoSalida):
    
    """
    Esta funcion trabaja especificamente con la forma del archivo de la pagina https://psl.noaa.gov/data/correlation/amon.us.long.data
    Podria necesitar modificacion para datos de otras paginas como el resto de las oscilaciones
    """
    
    ptr = open(rutaArchivoEntrada, "r") #abre el archivo descargado en modo lectura
    lineas = ptr.readlines() #Esta funcion regresa una lista cuya cada entrada es una linea del archivo en orden
    ptr.close() #cierro el archivo porque ya no se necesita    
    
    ptr = open(rutaArchivoSalida, "w") #abre el archivo descargado en modoescritura, si el archivo no existe esta funcion lo cree
    
    
    if rutaArchivoEntrada  == "dataSSTA.txt":
        ptr.write("YEAR,MONTH,NINO1+2,ANOM1+2,NINO3,ANOM3,NINO4,ANOM4,NINO3.4,ANOM3.4")
    elif rutaArchivoEntrada == "dataSSTOI.txt":
        ptr.write("YEAR,MONTH,NAtl,ANOM_NAtl,SAtl,ANOM_SAtl,TROP,ANOM_TROP")
    else:
        ptr.write("YEAR,ENE,FEB,MAR,ABR,MAY,JUN,JUL,AGO,SET,OCT,NOV,DIC")
    
        
    for linea in lineas[1:]: #descartando la primera y las últimas 4 líneas del archivo
        
        linea = linea.strip().split(" ") #Los datos estan separados por espacios no uniformes en el archivo original. Es decir, unos estan seaprados por dos espacios
                                  # otros por dos etc... Esto nos va a obligar a hacer un paso extra para acomodar los datos
                                  #"split" regresa una lista con los valores separados por el parametro que se le indique.
                                  # Por ejemplo: x = "1,2,3,4".split(",") regresa: x = [1,2,3,4]
                                  #La funcion strip() elimina el cambio de linea de la linea original
        
        linea2 = [] #lista vacia para acomodar los datos
        for valor in linea:
            if valor!= "": #Si el item no es un esapcio vacio, conservelo
                linea2.append(valor)# Agregandolo a la lista "vacia"
        
        
        #Ahora se puede exribir el archivo de interes muy fácil
        ptr.write("\n") #El cambio de linea se tiene que poner de manera explicita cunado se usa la funcion "open" para escribir archivos
        lineaNueva = "" #string en vlacon apra iterar
        
        for dato in linea2: #ahora "linea2" tiene los datos de interes
            lineaNueva += "%s,"%(dato)
        ptr.write(lineaNueva[:-1]) #-1 para no escribir una coma de mas
    
    ptr.close() #Cerramos el archivo. Esto es importante para evitar posibles problemas al intentar abrir el archivo con otra aplicacion

    #No es necesario que la funcion regrese nada


# In[3]:


def acomodaParaCSV_2(url,archivocreado):
    r = requests.get(url)
    soup = BeautifulSoup(r.text, 'html.parser')
    
    file = open(archivocreado, "w")

    if archivocreado == 'dataONI.txt':
        table = soup.find('table', attrs={"border": "1"})
    elif archivocreado == 'dataAMO_CSU.txt':
        table = soup.find("table", attrs={"id": "amo_table"})
        file.write("YEAR ENE FEB MAR ABR MAY JUN JUL AGO SET OCT NOV DIC")
    else:
        print("Error en: Guardando datos del índice ONI o AMO_CSU")
        
    for row in table.find_all("tr")[0:]:
        valores = [cell.get_text(strip=True) for cell in row.find_all("td")]
        file.write(" ".join(valores) + "\n") 

    file.close() 


# In[4]:


def acomodaParaCSV_3(Archivo_Descargado, Archivo_Creado):
    
    archivo = pd.read_csv(Archivo_Descargado)
    
    Años = []
    
    for i in range(0,len(archivo),12):
        Años.append(archivo["YEAR"][i])
        
    data = []
    
    for i in range(0,len(archivo)):
        if Archivo_Creado == 'dataSSTA_12.csv':
            data.append(archivo["ANOM1+2"][i])
        elif Archivo_Creado == 'dataSSTA_3.csv':
            data.append(archivo["ANOM3"][i])
        elif Archivo_Creado == 'dataSSTA_4.csv':
            data.append(archivo["ANOM4"][i])
        elif Archivo_Creado == 'dataSSTA_34.csv':
            data.append(archivo["ANOM3.4"][i])
        elif Archivo_Creado == 'dataAtlTROP.csv':
            data.append(archivo["ANOM_TROP"][i])
        elif Archivo_Creado == 'dataSAtl.csv':
            data.append(archivo["ANOM_SAtl"][i])
        elif Archivo_Creado == 'dataNAtl.csv':
            data.append(archivo["ANOM_NAtl"][i])
        else:
            print("Error en: Asignación de la variable.")
        
    padsize = 12 - (len(data) % 12)
    data = np.array(data)
    data_acomodada = np.pad(data, (0, padsize)).reshape((-1,12))
    
    Años = pd.DataFrame(Años, columns =['YEAR'])
    data = pd.DataFrame(data_acomodada, columns=['ENE', 'FEB', 'MAR', 'ABR', 'MAY', 'JUN', 'JUL', 'AGO', 'SET', 'OCT', 'NOV', 'DIC'])
    
    arhivo_salida = pd.concat([Años, data], axis=1, sort=False)
    
    arhivo_salida.to_csv(Archivo_Creado)


# In[5]:


#### Defincion de Variables de interes, acá simplemente cambiamos el link dependiendo de la oscilación que vayan a usar, como les comenté ayer sólo vamos a usar AMO y ENOS
link = "https://psl.noaa.gov/data/correlation/amon.us.data"
rutaGuardarArchivDescargado = "dataAMO.txt" #Si no se especifica la ruta absoluta, entonces se guarda en la mimsa carpeta en donde esta el script
rutaGuardarArchivoCreado = "dataAMO.csv"


### Llamada a las funciones 
urllib.request.urlretrieve(link, rutaGuardarArchivDescargado) #Descarga de los datos. La llamada a esta funcion puede variar para versiones antiguas de python
acomodaParaCSV(rutaGuardarArchivDescargado, rutaGuardarArchivoCreado) 


# In[6]:


link_AO = 'https://www.cpc.ncep.noaa.gov/products/precip/CWlink/daily_ao_index/monthly.ao.index.b50.current.ascii.table'
Archivo_Descargado_AO = "dataAO.txt"
Archivo_Creado_AO = "dataAO.csv"

urllib.request.urlretrieve(link_AO, Archivo_Descargado_AO)
acomodaParaCSV(Archivo_Descargado_AO, Archivo_Creado_AO) 


# In[7]:


link_MEI = 'https://psl.noaa.gov/enso/mei/data/meiv2.data'
Archivo_Descargado_MEI = "dataMEI_2.txt"
Archivo_Creado_MEI = "dataMEI_2.csv"

urllib.request.urlretrieve(link_MEI, Archivo_Descargado_MEI)
acomodaParaCSV(Archivo_Descargado_MEI, Archivo_Creado_MEI) 


# In[8]:


url = 'https://origin.cpc.ncep.noaa.gov/products/analysis_monitoring/ensostuff/ONI_v5.php'
Archivo_Creado_ONI = "dataONI.txt"

acomodaParaCSV_2(url, Archivo_Creado_ONI)

ONI = pd.read_csv("dataONI.txt", delimiter = " ")
ONI = ONI[ONI.Year != "Year"]
ONI.columns = ONI.columns.str.replace(r"Year", "YEAR")

ONI.to_csv("dataONI.csv")
cols = list(pd.read_csv("dataONI.csv", nrows =1))


# In[9]:


MEI_1 = pd.read_csv("dataMEI_1.txt", delimiter = "\t")
MEI_1.to_csv("dataMEI_1.csv")
cols_MEI_1 = list(pd.read_csv("dataMEI_1.csv", nrows =1))

MEI_1 = pd.read_csv("dataMEI_1.csv", usecols =[i for i in cols_MEI_1 if i != 'Unnamed: 0'])

MEI_2 = pd.read_csv('dataMEI_2.csv', skipfooter=4, engine='python')


# In[10]:


link_NAO = 'https://psl.noaa.gov/data/correlation/nao.data'
Archivo_Descargado_NAO = "dataNAO.txt"
Archivo_Creado_NAO = "dataNAO.csv"

urllib.request.urlretrieve(link_NAO, Archivo_Descargado_NAO)
acomodaParaCSV(Archivo_Descargado_NAO, Archivo_Creado_NAO) 


# In[11]:


link_PDO = 'https://www.ncdc.noaa.gov/teleconnections/pdo/data.txt'
Archivo_Descargado_PDO = "dataPDO.txt"
Archivo_Creado_PDO = "dataPDO.csv"

urllib.request.urlretrieve(link_PDO, Archivo_Descargado_PDO)
acomodaParaCSV(Archivo_Descargado_PDO, Archivo_Creado_PDO) 


# In[12]:


link_TNA = 'https://psl.noaa.gov/data/correlation/tna.data'
Archivo_Descargado_TNA = "dataTNA.txt"
Archivo_Creado_TNA = "dataTNA.csv"

urllib.request.urlretrieve(link_TNA, Archivo_Descargado_TNA)
acomodaParaCSV(Archivo_Descargado_TNA, Archivo_Creado_TNA) 


# In[13]:


link_SSTA = 'https://www.cpc.ncep.noaa.gov/data/indices/sstoi.indices'
Archivo_Descargado_SSTA = "dataSSTA.txt"
Archivo_Creado_SSTA = "dataSSTA.csv"

Archivo_Creado_SSTA_12 = "dataSSTA_12.csv"

urllib.request.urlretrieve(link_SSTA, Archivo_Descargado_SSTA)
acomodaParaCSV(Archivo_Descargado_SSTA, Archivo_Creado_SSTA) 

acomodaParaCSV_3(Archivo_Creado_SSTA, Archivo_Creado_SSTA_12)

SSTA_12 = pd.read_csv("dataSSTA_12.csv")
cols_SSTA = list(pd.read_csv("dataSSTA_12.csv", nrows =1))


# In[14]:


Archivo_Creado_SSTA_3 = "dataSSTA_3.csv"

urllib.request.urlretrieve(link_SSTA, Archivo_Descargado_SSTA)
acomodaParaCSV(Archivo_Descargado_SSTA, Archivo_Creado_SSTA) 

acomodaParaCSV_3(Archivo_Creado_SSTA, Archivo_Creado_SSTA_3)


# In[15]:


Archivo_Creado_SSTA_4 = "dataSSTA_4.csv"

urllib.request.urlretrieve(link_SSTA, Archivo_Descargado_SSTA)
acomodaParaCSV(Archivo_Descargado_SSTA, Archivo_Creado_SSTA) 

acomodaParaCSV_3(Archivo_Creado_SSTA, Archivo_Creado_SSTA_4)


# In[16]:


Archivo_Creado_SSTA_34 = "dataSSTA_34.csv"

urllib.request.urlretrieve(link_SSTA, Archivo_Descargado_SSTA)
acomodaParaCSV(Archivo_Descargado_SSTA, Archivo_Creado_SSTA) 

acomodaParaCSV_3(Archivo_Creado_SSTA, Archivo_Creado_SSTA_34)


# In[17]:


link_SSTOI = 'https://ftp.cpc.ncep.noaa.gov/wd52dg/data/indices/sstoi.atl.indices'
Archivo_Descargado_SSTOI = "dataSSTOI.txt"
Archivo_Creado_SSTOI = "dataSSTOI.csv"

Archivo_Creado_AtlTROP = "dataAtlTROP.csv"

urllib.request.urlretrieve(link_SSTOI, Archivo_Descargado_SSTOI)
acomodaParaCSV(Archivo_Descargado_SSTOI, Archivo_Creado_SSTOI) 

acomodaParaCSV_3(Archivo_Creado_SSTOI, Archivo_Creado_AtlTROP)


# In[18]:


Archivo_Creado_SAtl = "dataSAtl.csv"

urllib.request.urlretrieve(link_SSTOI, Archivo_Descargado_SSTOI)
acomodaParaCSV(Archivo_Descargado_SSTOI, Archivo_Creado_SSTOI) 

acomodaParaCSV_3(Archivo_Creado_SSTOI, Archivo_Creado_SAtl)


# In[19]:


Archivo_Creado_NAtl = "dataNAtl.csv"

urllib.request.urlretrieve(link_SSTOI, Archivo_Descargado_SSTOI)
acomodaParaCSV(Archivo_Descargado_SSTOI, Archivo_Creado_SSTOI) 

acomodaParaCSV_3(Archivo_Creado_SSTOI, Archivo_Creado_NAtl)


# In[20]:


link_CAR = 'https://psl.noaa.gov/data/correlation/CAR_ersst.data'
Archivo_Descargado_CAR = "dataCAR.txt"
Archivo_Creado_CAR = "dataCAR.csv"

urllib.request.urlretrieve(link_CAR, Archivo_Descargado_CAR)
acomodaParaCSV(Archivo_Descargado_CAR, Archivo_Creado_CAR) 


# In[21]:


link_WHWP= 'https://psl.noaa.gov/data/correlation/whwp.data'
Archivo_Descargado_WHWP = "dataWHWP.txt"
Archivo_Creado_WHWP = "dataWHWP.csv"

urllib.request.urlretrieve(link_WHWP, Archivo_Descargado_WHWP)
acomodaParaCSV(Archivo_Descargado_WHWP, Archivo_Creado_WHWP) 


# In[22]:


link_PNA= 'https://psl.noaa.gov/data/correlation/pna.data'
Archivo_Descargado_PNA = "dataPNA.txt"
Archivo_Creado_PNA = "dataPNA.csv"

urllib.request.urlretrieve(link_PNA, Archivo_Descargado_PNA)
acomodaParaCSV(Archivo_Descargado_PNA, Archivo_Creado_PNA) 


# In[23]:


link_SOI= 'https://www.cpc.ncep.noaa.gov/data/indices/soi'
Archivo_Descargado_SOI = "dataSOI.txt"
Archivo_Creado_SOI = "dataSOI.csv"

urllib.request.urlretrieve(link_SOI, Archivo_Descargado_SOI)
acomodaParaCSV(Archivo_Descargado_SOI, Archivo_Creado_SOI) 


# In[24]:


link_AMO_CSU = 'https://tropical.colostate.edu/archive.html#amo'
Archivo_Creado_AMO_CSU = "dataAMO_CSU.txt"

acomodaParaCSV_2(link_AMO_CSU, Archivo_Creado_AMO_CSU)


# In[25]:


AMO = pd.read_csv('dataAMO.csv', skipfooter=4, engine='python', skiprows = [i for i in range(1,3)])

AO = pd.read_csv('dataAO.csv')

MEI = pd.concat([MEI_1, MEI_2], sort=False, ignore_index=True)

ONI = pd.read_csv("dataONI.csv", usecols =[i for i in cols if i != 'Unnamed: 0'])

NAO = pd.read_csv('dataNAO.csv', skipfooter=3, engine='python', skiprows = [i for i in range(1,3)])

PDO = pd.read_csv('dataPDO.csv', skiprows= [i for i in range(1,98)])
PDO.iloc[-1] = PDO.iloc[-1].replace('-99.99', '', regex=True)
PDO = PDO.apply(pd.to_numeric)

TNA = pd.read_csv("dataTNA.csv", skipfooter=2, engine='python', skiprows = [i for i in range(1,3)])

SSTA_12 = pd.read_csv("dataSSTA_12.csv",usecols =[i for i in cols_SSTA if i != 'Unnamed: 0'])
SSTA_12.index = pd.RangeIndex(start=32, stop=len(AMO['YEAR']), step=1)

SSTA_3 = pd.read_csv("dataSSTA_3.csv",usecols =[i for i in cols_SSTA if i != 'Unnamed: 0'])
SSTA_3.index = pd.RangeIndex(start=32, stop=len(AMO['YEAR']), step=1)

SSTA_4 = pd.read_csv("dataSSTA_4.csv",usecols =[i for i in cols_SSTA if i != 'Unnamed: 0'])
SSTA_4.index = pd.RangeIndex(start=32, stop=len(AMO['YEAR']), step=1)

SSTA_34 = pd.read_csv("dataSSTA_34.csv",usecols =[i for i in cols_SSTA if i != 'Unnamed: 0'])
SSTA_34.index = pd.RangeIndex(start=32, stop=len(AMO['YEAR']), step=1)

AtlTROP = pd.read_csv("dataAtlTROP.csv",usecols =[i for i in cols_SSTA if i != 'Unnamed: 0'])
AtlTROP.index = pd.RangeIndex(start=32, stop=len(AMO['YEAR']), step=1)

SAtl = pd.read_csv("dataSAtl.csv",usecols =[i for i in cols_SSTA if i != 'Unnamed: 0'])
SAtl.index = pd.RangeIndex(start=32, stop=len(AMO['YEAR']), step=1)

NAtl = pd.read_csv("dataNAtl.csv",usecols =[i for i in cols_SSTA if i != 'Unnamed: 0'])
NAtl.index = pd.RangeIndex(start=32, stop=len(AMO['YEAR']), step=1)

CAR = pd.read_csv('dataCAR.csv', skipfooter=7, engine='python')

WHWP = pd.read_csv('dataWHWP.csv', skipfooter=8, engine='python', skiprows = [i for i in range(1,3)])

PNA = pd.read_csv('dataPNA.csv', skipfooter=3, engine='python', skiprows = [i for i in range(1,3)])

SOI = pd.read_csv('dataSOI.csv', skiprows= [i for i in range(1,88)], skipfooter=10, engine='python')
SOI.iloc[-1] = SOI.iloc[-1].replace('-999.9', '', regex=True)
SOI = SOI.apply(pd.to_numeric)
SOI.index = pd.RangeIndex(start=1, stop=len(AMO['YEAR']), step=1)


AMO_CSU = pd.read_csv("dataAMO_CSU.txt", delimiter = " ")
AMO_CSU.to_csv("dataAMO_CSU.csv")
AMO_CSU = pd.read_csv('dataAMO_CSU.csv', usecols =[i for i in cols_SSTA if i != 'Unnamed: 0'])


# In[26]:


Oscilaciones = {"AMO": AMO, "AO": AO, "MEI": MEI, "ONI": ONI, "NAO": NAO, "PDO": PDO, "TNA": TNA, "SSTA_12": SSTA_12, "SSTA_3": SSTA_3, "SSTA_4": SSTA_4, "SSTA_34": SSTA_34, "AtlTROP": AtlTROP, "SAtl": SAtl, "NAtl": NAtl, "CAR": CAR, "WHWP": WHWP, "PNA": PNA, "SOI": SOI, "AMO_CSU": AMO_CSU}

Coincidencias_Oscilaciones = {}


# In[27]:


def CalculoCoincidencias(mes, oscilacion):
    
    if oscilacion in Oscilaciones.keys():
        if (mes >= 6) & (mes <= 12): 
            mes_final = mes + 1
            mes_inicio = mes - 5
            año = Oscilaciones[oscilacion].iloc[-1,mes_inicio:mes_final]
            año = año.tolist()
        elif mes < 6:
            mes_final = mes + 1
            mes_inicio = mes - len(Oscilaciones[oscilacion].iloc[-1,2:mes_final])
            año = Oscilaciones[oscilacion].iloc[-2,7+mes:13]
            año = año.tolist()
            año_actual = Oscilaciones[oscilacion].iloc[-1,mes_inicio:mes_final]
            año_actual = año_actual.tolist()
            año.extend(año_actual)
        else:
            print("Error en la selección del período.")
    else:
        print("ERROR")
        
    pearsoncorr = []
    MAD = []
    
    if (mes >= 6) & (mes <= 12):
        for i in range(0,len(Oscilaciones[oscilacion])):  
            años_anteriores = Oscilaciones[oscilacion].iloc[i,mes_inicio:mes_final]
            años_anteriores = años_anteriores.tolist()
            pearsoncorr.append(pearsonr(años_anteriores, año)[0])
            resta = [x - y for x,y in zip(año,años_anteriores)]
            absoluto = np.abs(resta)
            promedio = np.average(absoluto)
            MAD.append(promedio)
    elif mes < 6: 
        for i in range(0,len(Oscilaciones[oscilacion])-1):
            años_anteriores = Oscilaciones[oscilacion].iloc[i,7+mes:13]
            meses_anteriores = Oscilaciones[oscilacion].iloc[i+1,mes_inicio:mes_final]
            años_anteriores = años_anteriores.tolist()
            años_anteriores.extend(meses_anteriores)
            pearsoncorr.append(pearsonr(años_anteriores, año)[0])
            resta = [x - y for x,y in zip(año,años_anteriores)]
            absoluto = np.abs(resta)
            promedio = np.average(absoluto)
            MAD.append(promedio)
    else:
        print("Error en: Calculando la correlación de pearson y MAD") 
    
    if (len(MAD) < len(Oscilaciones[oscilacion])) & (len(pearsoncorr) < len(Oscilaciones[oscilacion])):
        MAD.append(-99.99)
        pearsoncorr.append(-99.99)
        Oscilaciones[oscilacion]["MAD"] = MAD
        Oscilaciones[oscilacion]["Pearson Corr"] = pearsoncorr
    elif (len(MAD) == len(Oscilaciones[oscilacion])) & (len(pearsoncorr) == len(Oscilaciones[oscilacion])):
        Oscilaciones[oscilacion]["MAD"] = MAD
        Oscilaciones[oscilacion]["Pearson Corr"] = pearsoncorr
    else:
        print("Error en: Longitud de los archivos.")
    
    if oscilacion == "ONI":
        Coincidencias = Oscilaciones[oscilacion].loc[(Oscilaciones[oscilacion]["Pearson Corr"] > 0.6) & (Oscilaciones[oscilacion]["MAD"] < 0.6), "YEAR"]
    elif (oscilacion == "AMO") or (oscilacion == "SOI") or (oscilacion == "AMO_CSU"):
        Coincidencias = Oscilaciones[oscilacion].loc[(Oscilaciones[oscilacion]["Pearson Corr"] > 0.6) & (Oscilaciones[oscilacion]["MAD"] < 0.3), "YEAR"]
    elif oscilacion == "AO":
        Coincidencias = Oscilaciones[oscilacion].loc[(Oscilaciones[oscilacion]["Pearson Corr"] > 0.4) & (Oscilaciones[oscilacion]["MAD"] < 1.0), "YEAR"]
    elif oscilacion == "MEI":
        Coincidencias = Oscilaciones[oscilacion].loc[(Oscilaciones[oscilacion]["Pearson Corr"] > 0.4) & (Oscilaciones[oscilacion]["MAD"] < 0.5), "YEAR"]
    elif oscilacion == "NAO":
        Coincidencias = Oscilaciones[oscilacion].loc[(Oscilaciones[oscilacion]["Pearson Corr"] > 0.6) & (Oscilaciones[oscilacion]["MAD"] < 0.8), "YEAR"]
    elif oscilacion == "PDO":
        Coincidencias = Oscilaciones[oscilacion].loc[(Oscilaciones[oscilacion]["Pearson Corr"] > 0.4) & (Oscilaciones[oscilacion]["MAD"] < 0.6), "YEAR"]
    elif oscilacion == "TNA":
        Coincidencias = Oscilaciones[oscilacion].loc[(Oscilaciones[oscilacion]["Pearson Corr"] > 0.5) & (Oscilaciones[oscilacion]["MAD"] < 0.3), "YEAR"]
    elif (oscilacion == "SSTA_12") or (oscilacion == "SSTA_34") or (oscilacion == "AtlTROP") or (oscilacion == "SAtl") or (oscilacion == "NAtl") or (oscilacion == "CAR") or (oscilacion == "WHWP") or (oscilacion == "PNA"):
        Coincidencias = Oscilaciones[oscilacion].loc[(Oscilaciones[oscilacion]["Pearson Corr"] > 0.6) & (Oscilaciones[oscilacion]["MAD"] < 0.6), "YEAR"]
    elif oscilacion == "SSTA_3":
        Coincidencias = Oscilaciones[oscilacion].loc[(Oscilaciones[oscilacion]["Pearson Corr"] > 0.5) & (Oscilaciones[oscilacion]["MAD"] < 0.7), "YEAR"]
    elif oscilacion == "SSTA_4":
        Coincidencias = Oscilaciones[oscilacion].loc[(Oscilaciones[oscilacion]["Pearson Corr"] > 0.38) & (Oscilaciones[oscilacion]["MAD"] < 0.7), "YEAR"]
    else:
        print("Error en: Calculando las coincidencias.")
    
    Oscilaciones[oscilacion]["Coincidencias_" + oscilacion] = Coincidencias
    
    Coincidencias_Oscilaciones['Coincidencias ' + oscilacion] = Oscilaciones[oscilacion]["Coincidencias_" + oscilacion]
        
    return Coincidencias


# In[30]:


Años_Análogos = pd.DataFrame()

def AñosAnálogos(oscilacion):
    
    Años_Análogos = pd.DataFrame(Coincidencias_Oscilaciones)
    
    Años_Análogos = Años_Análogos.set_index(AMO["YEAR"])
    
    Años_Análogos = Años_Análogos.fillna(0)
    Años_Análogos[Años_Análogos>1] = 1
    Años_Análogos["Total"] = Años_Análogos.sum(axis=1)
    
    plt.figure(figsize=(15, 6))

    text = 'Hecho por Anthony Segura García. \n asegura@imn.ac.cr'
    
    plt.text(0, 5.5, text, fontsize=7, va='top')
    
    Años_Análogos["Total"].plot(kind='bar',color='red', legend=True)
    
    plt.yticks(np.arange(0, np.int(Años_Análogos.loc[2019]['Total'])+1, 1))
    
    plt.xticks(rotation=70)
    
    plt.title("Años Análogos")
    plt.ylabel('Cantidad de Indicadores')
    plt.xlabel('Años')
    
    plt.savefig("Años_Análogos.png")

    Años_Análogos = Años_Análogos.sort_values(by='Total', ascending=False)
        
    Años_Análogos.to_csv(r'Años_Análogos.txt', sep=' ', mode='w')
    
    return Años_Análogos

# In[30]

def InputOsc():
    while True:
        oscilacion = input("Por favor ingrese la oscilación que desea usar (AMO, AO, MEI, ONI, NAO, PDO, TNA, SSTA_12, SSTA_3, SSTA_4, SSTA_34, AtlTROP, SAtl, NAtl, CAR, WHWP, PNA, SOI, AMO_CSU): ")
        try:        
            word = [str(x) for x in oscilacion.split()] 
            for i in range(0,len(word)):
                oscilaciones = str(word[i])
                if oscilaciones in Oscilaciones.keys():
                    print("Oscilaciones leídas correctamente")
                    break
                else:
                    print("La oscilación ingresada es incorrecta, inténtelo de nuevo.")
                    oscilacion = InputOsc()
                    continue
        except ValueError:
            print("Dato ingresado incorrecto.")
            continue
        else:
            break
    return oscilacion

# In[31]

def InputMes():
    while True:
        mes = input("Por favor ingrese el número del mes actual: ")
        try:        
            val = int(mes)
            if (val > 0) & (val <= 12):
                mes = int(mes)
                break
            else:
                print("El valor ingresado tiene que ser mayor a 0 y menor que 12, inténtelo de nuevo.")
                continue
        except ValueError:
            print("Dato ingresado incorrecto.")
            continue
        else:
            break
    return mes

# In[32]:


print("Hola, este programa se encarga de calcular los años análogos a partir de las oscilaciones AMO, AO, MEI, ONI, NAO, PDO, TNA, SSTA_12, SSTA_3, SSTA_4, SSTA_34, AtlTROP, SAtl, NAtl, CAR, WHWP, PNA, SOI, AMO_CSU. A continuación se le solicitarán las opciones necesarias para el cálculo: " + "\n")

MAIN_PROMPT = "Ingrese 'C' para Continuar o 'S' para si desea Salir del programa: "
command = input(MAIN_PROMPT)

while not command == "S":
    if command == "C":
        oscilacion = InputOsc()
        
        word = [str(x) for x in oscilacion.split()] 
        
        mes = InputMes()
        for i in range(0,len(word)):
            Calculo_Coincidencias = CalculoCoincidencias(mes,word[i])
            AñosAnálogos(word[i])

    else:
        print("Error al ingresar la opción. Por favor ingrese la opción correcta.")
    command = input(MAIN_PROMPT + "\n")
    
print("Calculando...")

