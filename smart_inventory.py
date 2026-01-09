import cv2
import time
import sqlite3
import os
import threading
import mediapipe as mp
from datetime import datetime

# --- 1. VOICE FUNCTION ---
def speak(text):
    def run_speech():
        # 'say' is the native macOS text-to-speech command
        os.system(f'say "{text}"')
    threading.Thread(target=run_speech, daemon=True).start()

# --- 2. DATABASE INITIALIZATION ---
def init_db():
    conn = sqlite3.connect('inventory.db')
    c = conn.cursor()
    c.execute('CREATE TABLE IF NOT EXISTS stock (sku TEXT PRIMARY KEY, name TEXT, quantity INTEGER)')
    c.execute('CREATE TABLE IF NOT EXISTS logs (sku TEXT, action TEXT, timestamp TEXT)')
    conn.commit()
    conn.close()

def log_to_db(sku, action):
    conn = sqlite3.connect('inventory.db')
    c = conn.cursor()
    c.execute("SELECT name, quantity FROM stock WHERE sku=?", (sku,))
    row = c.fetchone()
    
    delta = 1 if action == "IN" else -1
    
    if row:
        p_name, qty = row[0], row[1]
        new_qty = max(0, qty + delta)
        c.execute("UPDATE stock SET quantity = ? WHERE sku = ?", (new_qty, sku))
    else:
        p_name = f"Item {sku[-4:]}"
        new_qty = 1 if action == "IN" else 0
        c.execute("INSERT INTO stock VALUES (?, ?, ?)", (sku, p_name, new_qty))
    
    c.execute("INSERT INTO logs VALUES (?, ?, ?)", 
              (sku, action, datetime.now().strftime("%H:%M:%S")))
    conn.commit()
    conn.close()
    
    print(f"✅ {action}: {p_name} | Stock: {new_qty}")
    speak(f"{p_name} {action}")

# --- 3. VISION SYSTEM ---
def main():
    init_db()
    
    # Initialize MediaPipe with explicit error handling
    try:
        mp_hands = mp.solutions.hands
        mp_draw = mp.solutions.drawing_utils
        # We define the detector inside main to ensure it's fresh
        detector = mp_hands.Hands(
            static_image_mode=False,
            max_num_hands=1,
            min_detection_confidence=0.7,
            min_tracking_confidence=0.5
        )
    except Exception as e:
        print(f"❌ MediaPipe Initialization Error: {e}")
        print("Try running: pip install mediapipe==0.10.9")
        return

    qr_detector = cv2.QRCodeDetector()
    cap = cv2.VideoCapture(0)
    
    last_scan = 0
    cooldown = 3.0 

    print("🚀 Visilog System Active. Press 'q' to quit.")

    while cap.isOpened():
        success, frame = cap.read()
        if not success: break
        
        frame = cv2.flip(frame, 1)
        h, w, _ = frame.shape
        rgb = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)
        
        # 1. Hand Tracking
        results = detector.process(rgb)
        wrist_x = w // 2 # Default to center
        
        if results.multi_hand_landmarks:
            # Get the wrist landmark (index 0)
            hand_landmarks = results.multi_hand_landmarks[0]
            wrist_x = int(hand_landmarks.landmark[0].x * w)
            mp_draw.draw_landmarks(frame, hand_landmarks, mp_hands.HAND_CONNECTIONS)

        # 2. Scanning Logic
        data, bbox, _ = qr_detector.detectAndDecode(frame)
        
        if data and (time.time() - last_scan > cooldown):
            # If hand is on left side of screen (< mid), it's an IN action
            action = "IN" if wrist_x < (w // 2) else "OUT"
            log_to_db(data, action)
            last_scan = time.time()
            
            # Visual Feedback
            color = (0, 255, 0) if action == "IN" else (0, 0, 255)
            cv2.rectangle(frame, (0,0), (w,h), color, 10)

        # 3. UI Overlay
        cv2.line(frame, (w // 2, 0), (w // 2, h), (255, 255, 255), 1)
        cv2.putText(frame, "<- IN (RESTOCK)", (20, 50), 1, 2, (0, 255, 0), 2)
        cv2.putText(frame, "OUT (PICK) ->", (w - 250, 50), 1, 2, (0, 0, 255), 2)
        
        mode_text = "MODE: RESTOCK" if wrist_x < (w // 2) else "MODE: PICK"
        cv2.putText(frame, mode_text, (w // 2 - 100, h - 30), 1, 1.5, (255, 255, 0), 2)

        cv2.imshow("Visilog Smart Inventory", frame)
        if cv2.waitKey(1) & 0xFF == ord('q'): 
            break

    cap.release()
    cv2.destroyAllWindows()

if __name__ == "__main__":
    main()