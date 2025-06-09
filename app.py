from flask import Flask, request, jsonify
import joblib
import extract_slots

model = joblib.load("nlu_model.joblib")


session_memory = {}

app = Flask(__name__)

@app.route("/nlu", methods=["POST"])
def nlu():
    user_text = request.json.get("text")
    session_id = request.json.get("session_id", "default") 
    print(f"Received text: {user_text}, Session ID: {session_id}")

    if not user_text:
        return jsonify({"error": "No text provided"}), 400


    if session_id in session_memory and session_memory[session_id]["intent"] == "insertAppointment":
        intent = "insertAppointment"
    else:
        intent = model.predict([user_text])[0]

    response = {"intent": intent, "slots": {}, "allRequiredParamsPresent": True}

    if intent == "insertAppointment":
        extracted_slots = extract_slots.extract_slots(user_text)

        # Retrieve or initialize session
        session = session_memory.get(session_id, {"intent": intent, "slots": {}})
        session["intent"] = "insertAppointment"

        # Safely update session with only non-empty extracted slot values
        for key, value in extracted_slots.items():
            if value:
                session["slots"][key] = value

        session_memory[session_id] = session

        # Check for missing required slots
        required_slots = ["name", "date", "time"]
        current_slots = session["slots"]
        missing = [slot for slot in required_slots if not current_slots.get(slot)]

        response["slots"] = current_slots
        if missing:
            next_slot = missing[0]
            prompt_map = {
                "name": "Whose appointment should I book?",
                "date": "What date should I book the appointment for?",
                "time": "What time should I book it?"
            }
            response["missing_slots"] = missing
            response["message"] = prompt_map[next_slot]
            response["allRequiredParamsPresent"] = False
        else:
            response["message"] = "All required details received. Appointment can be booked."
            del session_memory[session_id]  # Clear session after completion

    else:
        # For other intents, no slot filling needed
        response["message"] = "Intent recognized but no slot filling needed."

    return jsonify(response)

@app.route("/", methods=["GET"])
def index():
    return "Welcome to the NLU API! Send a POST request to /nlu with 'text'."

if __name__ == "__main__":
    app.run(debug=True)
