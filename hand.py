import cv2
import mediapipe as mp
import serial
import time

# --- Configuration & Hardware ---
SERIAL_PORT = 'COM3'  # Update to your port
BAUD_RATE = 115200
NUM_BOXES = 8
STABLE_TIME = 2.0     # Seconds to hover to turn ON
OFF_DELAY = 5.0       # Seconds of absence to turn OFF
POWER_WATTS = 5.0     # Estimated Power per LED (Watts)

# --- Initialization ---
try:
    ser = serial.Serial(SERIAL_PORT, BAUD_RATE, timeout=1)
    time.sleep(2) 
    print("Hardware Connected")
except:
    ser = None
    print("Debug Mode (No Hardware)")

mp_hands = mp.solutions.hands
hands = mp_hands.Hands(max_num_hands=2, min_detection_confidence=0.7)
cap = cv2.VideoCapture(0)

# State & Data Tracking
led_states = [False] * NUM_BOXES
box_last_seen = [0.0] * NUM_BOXES
led_total_seconds = [0.0] * NUM_BOXES
led_start_time = [0.0] * NUM_BOXES
hand_tracking = {} # {hand_id: [last_box_index, entry_time]}

def send_cmd(cmd):
    if ser: ser.write(f"{cmd}\n".encode())
    print(f"Action: {cmd}")

def get_boxes(w, h):
    bw, bh = w // 3, h // 3
    coords = []
    for i in range(3): coords.append((i*bw, 0, (i+1)*bw, bh))          # Row 1
    for i in range(3): coords.append((i*bw, bh, (i+1)*bw, 2*bh))     # Row 2
    for i in range(2): coords.append((i*(w//2), 2*bh, (i+1)*(w//2), h)) # Row 3
    return coords

while cap.isOpened():
    ret, frame = cap.read()
    if not ret: break

    frame = cv2.flip(frame, 1)
    h, w, _ = frame.shape
    boxes = get_boxes(w, h)
    now = time.time()
    
    rgb = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)
    results = hands.process(rgb)
    active_now = [False] * NUM_BOXES

    # 1. Hand Tracking Logic
    if results.multi_hand_landmarks:
        for idx, hand in enumerate(results.multi_hand_landmarks):
            # Track WRIST position
            cx, cy = int(hand.landmark[0].x * w), int(hand.landmark[0].y * h)
            
            for i, (x1, y1, x2, y2) in enumerate(boxes):
                if x1 <= cx <= x2 and y1 <= cy <= y2:
                    active_now[i] = True
                    box_last_seen[i] = now
                    
                    # Check for stability
                    last_box, start_t = hand_tracking.get(idx, [None, 0])
                    if last_box == i:
                        if not led_states[i] and (now - start_t > STABLE_TIME):
                            led_states[i] = True
                            led_start_time[i] = now
                            send_cmd(f"L{i+1}ON")
                    else:
                        hand_tracking[idx] = [i, now]
            cv2.circle(frame, (cx, cy), 8, (255, 255, 0), -1)

    # 2. Control & Energy Math
    for i in range(NUM_BOXES):
        # Handle Auto-OFF
        if led_states[i] and not active_now[i] and (now - box_last_seen[i] > OFF_DELAY):
            duration = now - led_start_time[i]
            led_total_seconds[i] += duration
            led_states[i] = False
            send_cmd(f"L{i+1}OFF")

        # UI Drawing
        x1, y1, x2, y2 = boxes[i]
        is_on = led_states[i]
        color = (0, 255, 0) if is_on else (0, 0, 255)
        
        # Calculate Live Stats
        current_session = (now - led_start_time[i]) if is_on else 0
        total_hrs = (led_total_seconds[i] + current_session) / 3600
        energy_wh = total_hrs * POWER_WATTS

        # Render UI
        cv2.rectangle(frame, (x1, y1), (x2, y2), color, 2)
        cv2.putText(frame, f"L{i+1} {'ON' if is_on else 'OFF'}", (x1+10, y1+25), 0, 0.6, color, 2)
        cv2.putText(frame, f"{energy_wh:.3f} Wh", (x1+10, y1+50), 0, 0.5, (255, 255, 255), 1)

    cv2.imshow("Vision Energy Monitor", frame)
    if cv2.waitKey(1) == 27: break

cap.release()
cv2.destroyAllWindows()
if ser: ser.close()
