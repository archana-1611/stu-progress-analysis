from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
from typing import List, Optional
import pickle
import pandas as pd
import uvicorn
import os

app = FastAPI()

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Load Model and Label Encoder
MODEL_PATH = "student_model.pkl"
ENCODER_PATH = "label_encoder.pkl"

model = None
encoder = None

try:
    if os.path.exists(MODEL_PATH):
        with open(MODEL_PATH, "rb") as f:
            model = pickle.load(f)
        print("[OK] Model loaded successfully")
    else:
        print(f"[ERR] Model file not found at {MODEL_PATH}")

    if os.path.exists(ENCODER_PATH):
        with open(ENCODER_PATH, "rb") as f:
            encoder = pickle.load(f)
        print("[OK] Label Encoder loaded successfully")
    else:
        print(f"[ERR] Label Encoder file not found at {ENCODER_PATH}")

except Exception as e:
    print(f"[ERR] Error loading model/encoder: {e}")

class StudentInput(BaseModel):
    Reg_Number: str
    Student_Name: str
    Attendance: float # Map from whatever input (key logic in frontend)
    Internal_Marks: float
    Assignment_Score: float

class PredictionResult(BaseModel):
    Reg_Number: str
    Student_Name: str
    Prediction: str
    Recommendation: str

def get_recommendation(label):
    if label == "Slow":
        return "Needs immediate attention. Schedule extra remedial classes and monitoring."
    elif label == "Average":
        return "Doing okay, but can improve. Encourage consistent practice."
    elif label == "Good" or label == "High":
        return "Excellent performance! Encourage to take advanced topics."
    return "No recommendation available."

@app.post("/predict", response_model=List[PredictionResult])
async def predict_students(students: List[StudentInput]):
    global model, encoder
    
    # Fallback Heuristic if model is missing
    if not model:
        print("[WARN] Using heuristic fallback as model is not loaded")
        results = []
        for s in students:
            # Simple Logic based on training data patterns
            # Slow: Attendance < 60 or Internal < 50
            # Good: Attendance > 90 and Internal > 80
            # Average: Between
            
            att = s.Attendance
            internal = s.Internal_Marks
            
            if att < 50 or internal < 40:
                label = "Slow"
            elif att > 85 and internal > 75:
                label = "Good" # or High
            else:
                label = "Average"
            
            rec = get_recommendation(label)
            results.append(PredictionResult(
                Reg_Number=s.Reg_Number,
                Student_Name=s.Student_Name,
                Prediction=label,
                Recommendation=rec
            ))
        return results

    if not model:
        raise HTTPException(status_code=500, detail="Model is not loaded.")
    
    results = []
    
    # Prepare DataFrame for batch prediction
    # Feature names must match what model expects. 
    # Based on training data: attendance, internal_marks, assignment_score
    
    data_for_df = []
    for s in students:
        data_for_df.append({
            "attendance": s.Attendance,
            "internal_marks": s.Internal_Marks,
            "assignment_score": s.Assignment_Score
        })
        
    if not data_for_df:
        return []

    df = pd.DataFrame(data_for_df)
    
    try:
        predictions = model.predict(df)
        
        # If we have an encoder, decode the labels
        # Assuming predictions are indices if encoder exists, or strings if not?
        # Usually sklearn classifiers return the label directly if trained on strings
        # But if label encoder was used separately, we might need to decode.
        # Let's assume the model returns the label directly (as seen in typical pipelines)
        # OR returns an index. Let's check type.
        
        # If predictions are numeric and we have an encoder, decode
        if encoder and hasattr(encoder, 'inverse_transform') and (predictions.dtype.kind in 'iu'):
             predicted_labels = encoder.inverse_transform(predictions)
        else:
             predicted_labels = predictions

        for i, s in enumerate(students):
            label = predicted_labels[i]
            rec = get_recommendation(label)
            results.append(PredictionResult(
                Reg_Number=s.Reg_Number,
                Student_Name=s.Student_Name,
                Prediction=str(label),
                Recommendation=rec
            ))
            
    except Exception as e:
        print(f"Prediction error: {e}")
        raise HTTPException(status_code=400, detail=f"Prediction failed: {str(e)}")

    return results

@app.get("/")
def health_check():
    return {"status": "online", "model_loaded": model is not None}

if __name__ == "__main__":
    uvicorn.run(app, host="127.0.0.1", port=8001)
