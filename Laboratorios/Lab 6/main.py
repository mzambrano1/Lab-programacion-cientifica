from typing import Dict, List, Optional
from fastapi import FastAPI,Response
from joblib import load
from tinydb import TinyDB, Query
from datetime import datetime
from tinydb.operations import set
import pandas as pd
import json

app = FastAPI(title="Lab 6")

# aquí carguen el modelo guardado (con load de joblib) y
model = load('./modelo.joblib')
# el cliente de base de datos (con tinydb). Usen './db.json' como bbdd.
db = TinyDB("./db.json")

# Nota: En el caso que al guardar en la bbdd les salga una excepción del estilo JSONSerializable
# conviertan el tipo de dato a uno más sencillo.
# Por ejemplo, si al guardar la predicción les levanta este error, usen int(prediccion[0])
# para convertirla a un entero nativo de python.

# Nota 2: Las funciones ya están implementadas con todos sus parámetros. No deberían
# agregar más que esos.


@app.post("/potabilidad/")
async def predict_and_save(observation: Dict[str, float]):
    data =  pd.DataFrame.from_dict(orient = 'index', data = observation).T
    prediction = model.predict(data) 
    to_db = observation.copy()
    to_db["Prediction"] = int(prediction[0])
    to_db["Day"],to_db["Month"], to_db["Year"] = int(datetime.now().day), int(datetime.now().month), int(datetime.now().year)
    id = db.insert(to_db)
    response = json.dumps({'potabilidad': int(prediction[0]), "id": id})
    return  Response(content=response, media_type="application/json")


@app.get("/potabilidad/")
async def read_all():
    data = json.dumps(db.all())
    return Response(content=data, media_type="application/json")


@app.get("/potabilidad_diaria/")
async def read_by_day(day: int, month: int, year: int):
    Mediciones = Query()
    results = db.search((Mediciones.Day == day) & (Mediciones.Month == month) & (Mediciones.Year == year))
    return Response(content=json.dumps(results), media_type="application/json")


@app.put("/potabilidad/")
async def update_by_day(day: int, month: int, year: int, new_prediction: int):
    Mediciones = Query()
    updated = db.update(set("Prediction", 7),(Mediciones.Day == day) & (Mediciones.Month == month) & (Mediciones.Year == year))
    success = True if len(updated) > 0 else False
    response = {"success": success, "updated_elements": updated}
    return Response(content=json.dumps(response), media_type="application/json")


@app.delete("/potabilidad/")
async def delete_by_day(day: int, month: int, year: int):
    Mediciones = Query()
    removed= db.remove((Mediciones.Day == day) & (Mediciones.Month == month) & (Mediciones.Year == year))
    success = True if len(removed) > 0 else False
    response = {"success": success, "deleted_elements": removed}
    return Response(content=json.dumps(response), media_type="application/json")
