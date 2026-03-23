import cv2
import mediapipe as mp
import serial
import time

# ================= SERIAL =================
try:
    ser = serial.Serial('COM3', 115200, timeout=1)
    time.sleep(2)
    print("ESP8266 Connected")
except:
    ser = None
    print("Debug Mode")

def send_command(cmd):
    if ser:
        ser.write((cmd + '\n').encode())
    print("CMD:", cmd)

# ================= MEDIAPIPE =================
mp_hands = mp.solutions.hands
hands = mp_hands.Hands(max_num_hands=2)

# ================= CAMERA =================
cap = cv2.VideoCapture(0)

# ================= CONFIG =================
num_boxes = 8
led_states = [False]*num_boxes
box_coords = []

stable_time = 2
off_delay = 5

hand_last_box = {}
hand_start_time = {}
box_last_seen = [0]*num_boxes

# ================= POWER CONFIG =================
POWER_PER_LED = [5]*num_boxes   # Watts per LED

led_on_time = [0]*num_boxes
led_total_energy = [0]*num_boxes  # in Wh
led_start_time = [0]*num_boxes

# ================= LOOP =================
while True:
    ret, frame = cap.read()
    if not ret:
        break

    frame = cv2.flip(frame, 1)
    h, w, _ = frame.shape

    # ===== BOXES =====
    box_coords.clear()
    bw, bh = w//3, h//3

    for i in range(3):
        box_coords.append((i*bw, 0, (i+1)*bw, bh))
    for i in range(3):
        box_coords.append((i*bw, bh, (i+1)*bw, 2*bh))
    for i in range(2):
        box_coords.append((i*(w//2), 2*bh, (i+1)*(w//2), h))

    rgb = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)
    results = hands.process(rgb)

    current_active = [False]*num_boxes

    # ===== HAND DETECTION =====
    if results.multi_hand_landmarks:
        for idx,hand in enumerate(results.multi_hand_landmarks):

            cx = int(hand.landmark[0].x * w)
            cy = int(hand.landmark[0].y * h)

            box = None
            for i,(x1,y1,x2,y2) in enumerate(box_coords):
                if x1 <= cx <= x2 and y1 <= cy <= y2:
                    box = i
                    break

            if box is not None:
                if hand_last_box.get(idx) == box:
                    if time.time() - hand_start_time.get(idx,0) > stable_time:
                        current_active[box] = True
                        box_last_seen[box] = time.time()
                else:
                    hand_last_box[idx] = box
                    hand_start_time[idx] = time.time()

    # ===== CONTROL + POWER TRACK =====
    now = time.time()

    for i in range(num_boxes):

        # TURN ON
        if current_active[i] and not led_states[i]:
            send_command(f"L{i+1}ON")
            led_states[i] = True
            led_start_time[i] = now

        # TURN OFF
        elif not current_active[i] and led_states[i]:
            if now - box_last_seen[i] > off_delay:
                send_command(f"L{i+1}OFF")
                led_states[i] = False

                # Calculate runtime
                run_time = now - led_start_time[i]
                led_on_time[i] += run_time

                # Energy = Power × Time(hours)
                energy = POWER_PER_LED[i] * (run_time / 3600)
                led_total_energy[i] += energy

    # ===== DRAW BOXES WITH DATA =====
    for i,(x1,y1,x2,y2) in enumerate(box_coords):

        color = (0,255,0) if led_states[i] else (0,0,255)
        cv2.rectangle(frame,(x1,y1),(x2,y2),color,2)

        # LIVE runtime
        live_time = 0
        if led_states[i]:
            live_time = now - led_start_time[i]

        total_time = led_on_time[i] + live_time

        # LIVE energy
        live_energy = 0
        if led_states[i]:
            live_energy = POWER_PER_LED[i] * (live_time / 3600)

        total_energy = led_total_energy[i] + live_energy

        # Display text
        cv2.putText(frame, f"L{i+1}", (x1+10,y1+25),
                    cv2.FONT_HERSHEY_SIMPLEX,0.6,color,2)

        cv2.putText(frame, f"Time: {int(total_time)}s",
                    (x1+10,y1+50),
                    cv2.FONT_HERSHEY_SIMPLEX,0.5,(255,255,255),1)

        cv2.putText(frame, f"Energy: {total_energy:.3f}Wh",
                    (x1+10,y1+70),
                    cv2.FONT_HERSHEY_SIMPLEX,0.5,(0,255,255),1)

    cv2.imshow("Smart Energy System", frame)

    if cv2.waitKey(1) == 27:
        break

# ===== CLEANUP =====
cap.release()
cv2.destroyAllWindows()
hands.close()

if ser:
    ser.close()