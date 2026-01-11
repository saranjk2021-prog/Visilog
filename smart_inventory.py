import cv2
import mediapipe as mp
from supabase import create_client
import time

# 1. Supabase Setup
# Since this runs locally, you can use a .env file or hardcode for testing
SUPABASE_URL = "https://lprovzgiotaqxvowufrd.supabase.co"
SUPABASE_KEY = "sb_publishable_gQjRbYoz0KJkL7BpQkMStg_k5D1KQhf"
supabase = create_client(SUPABASE_URL, SUPABASE_KEY)

# 2. MediaPipe Hands Setup
mp_hands = mp.solutions.hands
hands = mp_hands.Hands(min_detection_confidence=0.7, min_tracking_confidence=0.7)
mp_draw = mp.solutions.drawing_utils

def update_supabase_stock(sku, change):
    try:
        # Fetch current quantity from Cloud
        res = supabase.table("stock").select("quantity").eq("sku", sku).single().execute()
        if res.data:
            new_qty = res.data['quantity'] + change
            # Update the row in Supabase
            supabase.table("stock").update({"quantity": new_qty}).eq("sku", sku).execute()
            print(f"✅ Success: {sku} updated to {new_qty}")
    except Exception as e:
        print(f"❌ Error updating Supabase: {e}")

# 3. Camera Loop
cap = cv2.VideoCapture(0)
while cap.isOpened():
    success, image = cap.read()
    if not success: break

    image = cv2.flip(image, 1)
    results = hands.process(cv2.cvtColor(image, cv2.COLOR_BGR2RGB))

    if results.multi_hand_landmarks:
        for hand_landmarks in results.multi_hand_landmarks:
            # Gesture logic (Example: Thumbs up to add stock)
            # You can insert your specific finger-counting logic here
            mp_draw.draw_landmarks(image, hand_landmarks, mp_hands.HAND_CONNECTIONS)
            
            # Trigger update (Example SKU)
            # update_supabase_stock("SKU001", 1) 
            # time.sleep(2) # Prevent rapid multiple updates

    cv2.imshow('Visilog AI Scanner', image)
    if cv2.waitKey(5) & 0xFF == 27: break

cap.release()