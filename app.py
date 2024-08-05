from fastapi import FastAPI, HTTPException
from datetime import datetime
import calendar
import firebase_admin
from firebase_admin import credentials, firestore
import uvicorn
import requests
from pydantic import BaseModel
import os


cred = credentials.Certificate("sigaram-test-collection-firebase-adminsdk-c0kj4-b720e081da.json")
firebase_admin.initialize_app(cred)

db = firestore.client()

app = FastAPI()

FAKE_STORE_BASE_URL = "https://fakestoreapi.com"

@app.get("/hello")
def read_root():
    return {"message": "Hello World"}

@app.post("/add")
def add_data():
    try:
        now = datetime.now()
        day_of_week = calendar.day_name[now.weekday()]
        day_of_month = now.day
        month = now.strftime("%B")
        
        data = {
            "Day of Week": day_of_week,
            "Day of Month": day_of_month,
            "Month": month,
            "Timestamp": now
        }
        
        db.collection("sigaram_test_collection").add(data)
        
        return {"message": "Data added succesfully", "data": data}
    except Exception as e:
        return {"error": str(e)}
    
    
class CartItem(BaseModel):
    user_id: int
    product_id: int
    quantity: int
    
@app.get("/products")
def list_all_products():
    response = requests.get(f"{FAKE_STORE_BASE_URL}/products")
    if response.status_code == 200:
        return response.json()
    else:
        raise HTTPException(status_code=response.status_code, detail = "Error fetching products")
    
@app.post("/carts")
def add_item_to_cart(item: CartItem):
    payload = {
        "userId": item.user_id,
        "products": [{"productId": item.product_id, "quantity": item.quantity}]
    }
    response = requests.post(f"{FAKE_STORE_BASE_URL}/carts", json=payload)
    if response.status_code == 200 or response.status_code == 201:
        return response.json()
    else:
        raise HTTPException(status_code=response.status_code, detail="Error adding item to cart")

@app.get("/carts/{user_id}")
def list_items_in_cart(user_id: int):
    response = requests.get(f"{FAKE_STORE_BASE_URL}/carts/user/{user_id}")
    if response.status_code == 200:
        return response.json()
    else:
        raise HTTPException(status_code=response.status_code, detail="Error fetching cart items")
    
if __name__ == "__main__":
    port = int(os.environ.get("PORT", 8080))
    uvicorn.run(app, host="0.0.0.0", port=port)
        