from fastapi import FastAPI, HTTPException
from pydantic import BaseModel
import tensorflow as tf
from tensorflow.keras.preprocessing.sequence import pad_sequences
import pickle
import numpy as np
import joblib

app = FastAPI()

# Load the saved model
model = joblib.load('sentiment_model.pkl')

# Load the tokenizer (you need to save and reload your tokenizer used during training)
with open('tokenizer.pkl', 'rb') as handle:
    tokenizer = pickle.load(handle)

# Label mapping dictionary
label_mapping = {0: 'neutral', 1: 'positive', 2: 'negative'}

# Define the input structure for the prediction


class TextInput(BaseModel):
    text: str


# Preprocess input text
def preprocess_input_text(text):
    # Convert text to lowercase
    text = text.lower()

    # Tokenize and pad the text
    text_seq = tokenizer.texts_to_sequences([text])
    text_padded = pad_sequences(text_seq, maxlen=100)

    return text_padded


@app.post("/predict")
async def predict(input_data: TextInput):
    try:
        text = input_data.text

        # Preprocess the text
        processed_text = preprocess_input_text(text)

        # Make predictions
        prediction = model.predict(processed_text)
        predicted_label = np.argmax(prediction, axis=1)[0]
        predicted_sentiment = label_mapping[predicted_label]

        # Return the result as JSON
        return {
            "text": text,
            "sentiment": predicted_sentiment,
            # Include confidence scores for all classes
            "confidence": prediction[0].tolist()
        }

    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)
