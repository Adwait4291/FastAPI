from fastapi import FastAPI
from pydantic import BaseModel, Field, computed_field
from fastapi.responses import JSONResponse
from typing import Annotated, Literal
import pickle
import pandas as pd

# Load your trained model
with open("model.pkl", "rb") as f:
    model = pickle.load(f)

# City tier mapping
tier_1_cities = {"Mumbai", "Delhi", "Bangalore", "Hyderabad", "Chennai", "Kolkata"}
tier_2_cities = {"Pune", "Ahmedabad", "Jaipur", "Lucknow", "Nagpur"}

app = FastAPI()

class UserInput(BaseModel):
    age: Annotated[int, Field(..., ge=0, description="Age of the user", example=30)]
    weight: Annotated[float, Field(..., gt=0, description="Weight in kg", example=70.0)]
    height: Annotated[float, Field(..., gt=0, description="Height in cm", example=175.0)]
    income_lpa: Annotated[float, Field(..., gt=0, description="Income in LPA", example=10.0)]
    smoker: bool  # ✅ changed from Literal["True", "False"]
    city: Annotated[str, Field(..., description="User city", example="Mumbai")]
    occupation: Literal[
        'retired', 'freelancer', 'student', 'government_job',
        'business_owner', 'unemployed', 'private_job'
    ]

    @computed_field
    @property
    def bmi(self) -> float:
        height_m = self.height / 100
        return round(self.weight / (height_m ** 2), 2)

    @computed_field
    @property
    def lifestyle_risk(self) -> str:
        if self.smoker and self.bmi > 30:
            return "high"
        elif self.smoker or self.bmi > 27:
            return "medium"
        else:
            return "low"

    @computed_field
    @property
    def age_group(self) -> str:
        if self.age < 25:
            return "young"
        elif self.age < 45:
            return "adult"
        elif self.age < 60:
            return "middle_aged"
        return "senior"

    @computed_field
    @property
    def city_tier(self) -> int:
        if self.city in tier_1_cities:
            return 1
        elif self.city in tier_2_cities:
            return 2
        return 3

@app.post("/predict")
def predict_premium(data: UserInput):
    input_df = pd.DataFrame([{
        "bmi": data.bmi,
        "lifestyle_risk": data.lifestyle_risk,
        "age_group": data.age_group,
        "city_tier": data.city_tier,
        "occupation": data.occupation,
        "income_lpa": data.income_lpa
    }])

    prediction = model.predict(input_df)[0]
    return JSONResponse(status_code=200, content={"predicted_category": prediction})
