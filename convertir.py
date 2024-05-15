import pandas as pd

datos_json = pd.read_json('C:\\Users\\erick\\OneDrive\\Escritorio\\Erick\\Proyectos_Papeleria\\pape_crm_3\\productos.json')
df = pd.DataFrame(datos_json)
ruta_excel = 'C:\\Users\\erick\\OneDrive\\Escritorio\\Erick\\Proyectos_Papeleria\\pape_crm_3\\datos_excel.xlsx'
df.to_excel(ruta_excel, index=False)
