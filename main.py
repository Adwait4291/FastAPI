from fastapi import FastAPI, Path, HTTPException, Query
from fastapi.responses import JSONResponse
from pydantic import BaseModel, Field, computed_field
from typing_extensions import Literal
from typing import Annotated, Optional
import json

app = FastAPI()

# Patient model
class Patient(BaseModel):
    id: Annotated[str, Field(..., description="Unique identifier for the patient", example="P001")]
    name: Annotated[str, Field(..., description="Full name of the patient", example="John Doe")]
    city: Annotated[str, Field(..., description="City where the patient resides", example="New York")]
    age: Annotated[int, Field(..., ge=0, description="Age of the patient in years", example=30)]
    gender: Annotated[Literal['male', 'female', 'other'], Field(..., description="Gender of the patient")]
    height: Annotated[float, Field(..., gt=0, description="Height in centimeters", example=175.0)]
    weight: Annotated[float, Field(..., gt=0, description="Weight in kilograms", example=70.0)]

    @computed_field
    @property
    def bmi(self) -> float:
        return round(self.weight / ((self.height / 100) ** 2), 2)

    @computed_field
    @property
    def verdict(self) -> str:
        if self.bmi < 18.5:
            return "Underweight"
        elif 18.5 <= self.bmi < 24.9:
            return "Normal weight"
        elif 25 <= self.bmi < 29.9:
            return "Overweight"
        else:
            return "Obesity"

class PatientUpdate(BaseModel):

    name:Annotated[Optional[str], Field(None, description="Full name of the patient", example="John Doe")]
    city: Annotated[Optional[str], Field(None, description="City where the patient resides", example="New York")]
    age: Annotated[Optional[int], Field(None, ge=0, description="Age of the patient in years", example=30)]
    gender: Annotated[Optional[Literal['male','female','other']], Field(default=None)]
    height: Annotated[Optional[float], Field(None, gt=0, description="Height in centimeters", example=175.0)]
    weight: Annotated[Optional[float], Field(None, gt=0, description="Weight in kilograms", example=70.0)]
     

# JSON helpers
def load_data():
    try:
        with open("patients.json", "r") as f:
            return json.load(f)
    except FileNotFoundError:
        return {}

def save_data(data):
    with open("patients.json", "w") as f:
        json.dump(data, f, indent=4)

# Routes
@app.get("/")
def hello():
    return {"message": "Patient Management System"}

@app.get("/about")
def about():
    return {"message": "A fully functional Patient Management System built with FastAPI."}

@app.get('/view')
def view():
    return load_data()

@app.get('/patient/{patient_id}')
def view_patient(
    patient_id: str = Path(..., description="The ID of the patient in DB", examples={"example": {"value": "P001"}})
):
    data = load_data()
    if patient_id in data:
        return data[patient_id]
    raise HTTPException(status_code=404, detail="Patient not found")

@app.get('/sort')
def sort_patients(
    sort_by: str = Query(..., description="Sort by 'height', 'weight', or 'bmi'"),
    order: str = Query("asc", description="Order: 'asc' or 'desc'")
):
    valid_fields = ['height', 'weight', 'bmi']
    if sort_by not in valid_fields:
        raise HTTPException(status_code=400, detail=f"Invalid sort field. Use one of {valid_fields}.")
    if order not in ['asc', 'desc']:
        raise HTTPException(status_code=400, detail="Invalid order. Use 'asc' or 'desc'.")

    data = load_data()
    sort_order = order == 'desc'
    sorted_data = sorted(data.values(), key=lambda x: x[sort_by], reverse=sort_order)
    return sorted_data

@app.post('/create')
def create_patient(patient: Patient):
    data = load_data()
    if patient.id in data:
        raise HTTPException(status_code=400, detail="Patient with this ID already exists.")

    patient_data = patient.model_dump(exclude=["id"])
    patient_data["bmi"] = patient.bmi
    patient_data["verdict"] = patient.verdict

    data[patient.id] = patient_data
    save_data(data)

    return JSONResponse(
        status_code=201,
        content={"message": "Patient created successfully", "patient_id": patient.id}
    )

@app.put('/edit/{patient_id}')
def update_patient(
    patient_id:str,patient_update: PatientUpdate):
    data = load_data()

    if patient_id not in data:
        raise HTTPException(status_code=404, detail="Patient not found")
    
    existing_patient_info = data[patient_id]
    updated_patient_info = patient_update.model_dump(exclude_unset=True)

    for key, value in updated_patient_info.items():
        if value is not None:
            existing_patient_info[key] = value
    
    existing_patient_info['id']= patient_id
    patient_pydantic_obj= Patient(**existing_patient_info)

    existing_patient_info= patient_pydantic_obj.model_dump(exclude=["id"])

    data[patient_id] = existing_patient_info

    save_data(data)

    return JSONResponse(
        status_code=200,
        content={"message": "Patient updated successfully", "patient_id": patient_id}
    )

@app.delete('/delete/{patient_id}')
def delete_patient(
    patient_id: str = Path(..., description="The ID of the patient to delete", examples={"example": {"value": "P001"}})
):
    data = load_data()
    if patient_id in data:
        del data[patient_id]
        save_data(data)
        return JSONResponse(status_code=200, content={"message": "Patient deleted successfully"})
    raise HTTPException(status_code=404, detail="Patient not found")    











