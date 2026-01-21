import streamlit as st
import pandas as pd
from datetime import datetime
import os

# ----------------------------
# File Paths for Persistence
# ----------------------------
STUDENTS_FILE = "students.csv"
REQUESTS_FILE = "requests.csv"
LOGS_FILE = "logs.csv"
MESSAGES_FILE = "messages.csv"

# ----------------------------
# Page Configuration
# ----------------------------
st.set_page_config(
    page_title="Detailed Persistent Student Exchange",
    layout="centered"
)

st.title("🔄 Detailed Student Group Exchange")
st.write(
    "Students submit mutual requests. Exchanges happen **only if requests match and gender is same**. "
    "Data and messages are saved automatically."
)

# ----------------------------
# Helper Functions
# ----------------------------
def load_csv(path, columns):
    if os.path.exists(path):
        return pd.read_csv(path)
    else:
        return pd.DataFrame(columns=columns)

def save_csv(df, path):
    df.to_csv(path, index=False)

def log_action(action, student1, student2=None):
    logs = load_csv(LOGS_FILE, ["Date", "Action", "Student1", "Student2"])
    logs = pd.concat([logs, pd.DataFrame([{
        "Date": datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
        "Action": action,
        "Student1": student1,
        "Student2": student2 if student2 else ""
    }])], ignore_index=True)
    save_csv(logs, LOGS_FILE)

def add_message(msg):
    messages = load_csv(MESSAGES_FILE, ["Date", "Message"])
    messages = pd.concat([messages, pd.DataFrame([{
        "Date": datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
        "Message": msg
    }])], ignore_index=True)
    save_csv(messages, MESSAGES_FILE)

# ----------------------------
# Load Persistent Data
# ----------------------------
students = load_csv(STUDENTS_FILE, ["FirstName", "LastName", "Gender", "Group"])
requests_df = load_csv(REQUESTS_FILE, ["FirstName", "LastName", "TargetGroup"])
messages_df = load_csv(MESSAGES_FILE, ["Date", "Message"])

# ----------------------------
# Add Student Section
# ----------------------------
st.subheader("➕ Add Student")
with st.form("add_student_form"):
    col1, col2, col3, col4 = st.columns([2,2,1,1])
    with col1:
        first_name = st.text_input("First Name")
    with col2:
        last_name = st.text_input("Last Name")
    with col3:
        gender = st.selectbox("Gender", ["F","M"])
    with col4:
        group = st.number_input("Group", min_value=1, step=1)

    submitted = st.form_submit_button("Add Student")
    if submitted:
        if not first_name.strip() or not last_name.strip():
            st.error("❌ Both first and last name are required.")
        elif ((students["FirstName"]==first_name.strip()) & (students["LastName"]==last_name.strip())).any():
            st.error("❌ Student already exists.")
        else:
            new_student = pd.DataFrame([{
                "FirstName": first_name.strip(),
                "LastName": last_name.strip(),
                "Gender": gender,
                "Group": group
            }])
            students = pd.concat([students, new_student], ignore_index=True)
            save_csv(students, STUDENTS_FILE)
            log_action("Added Student", f"{first_name} {last_name}")
            st.success(f"✅ {first_name} {last_name} added successfully!")

# ----------------------------
# Display Students
# ----------------------------
st.subheader("📋 Current Students")
if students.empty:
    st.info("No students added yet.")
else:
    students["FullName"] = students["FirstName"] + " " + students["LastName"]
    st.dataframe(students[["FullName", "Gender", "Group"]], use_container_width=True)

# ----------------------------
# Submit Exchange Request
# ----------------------------
st.subheader("📝 Submit Exchange Request")
if not students.empty:
    student_fullname = st.selectbox(
        "Select student",
        students["FirstName"] + " " + students["LastName"]
    )
    student_row = students[(students["FirstName"] + " " + students["LastName"]) == student_fullname].iloc[0]
    current_group = student_row["Group"]

    target_group = st.number_input("Target Group", min_value=1, step=1, value=current_group)

    if st.button("Submit Request"):
        if target_group == current_group:
            st.warning("⚠ Already in this group.")
        elif ((requests_df["FirstName"]==student_row["FirstName"]) & (requests_df["LastName"]==student_row["LastName"])).any():
            st.warning("⚠ You already submitted a request.")
        else:
            new_request = pd.DataFrame([{
                "FirstName": student_row["FirstName"],
                "LastName": student_row["LastName"],
                "TargetGroup": target_group
            }])
            requests_df = pd.concat([requests_df, new_request], ignore_index=True)
            save_csv(requests_df, REQUESTS_FILE)
            log_action("Submitted Request", student_fullname)
            st.success(f"Request submitted: {student_fullname} → Group {target_group}")

# ----------------------------
# Show Pending Requests
# ----------------------------
st.subheader("📌 Pending Requests")
if requests_df.empty:
    st.info("No requests yet.")
else:
    requests_df["FullName"] = requests_df["FirstName"] + " " + requests_df["LastName"]
    st.dataframe(requests_df[["FullName", "TargetGroup"]], use_container_width=True)

# ----------------------------
# Process Exchanges
# ----------------------------
st.subheader("🔁 Process Eligible Exchanges")
if st.button("Process Exchanges"):
    processed_messages = []
    for _, req in requests_df.iterrows():
        student_name = req["FirstName"] + " " + req["LastName"]
        target_group = req["TargetGroup"]
        student = students[(students["FirstName"]==req["FirstName"]) & (students["LastName"]==req["LastName"])].iloc[0]
        student_gender = student["Gender"]
        current_group = student["Group"]

        # Reciprocal request
        reciprocal = requests_df[
            (requests_df["TargetGroup"]==current_group) &
            ((requests_df["FirstName"] != req["FirstName"]) | (requests_df["LastName"] != req["LastName"]))
        ]
        # Gender check
        reciprocal = reciprocal[
            reciprocal.apply(lambda r: students[(students["FirstName"]==r["FirstName"]) & (students["LastName"]==r["LastName"])]["Gender"].iloc[0] == student_gender, axis=1)
        ]

        if not reciprocal.empty:
            partner_row = reciprocal.iloc[0]
            partner_name = partner_row["FirstName"] + " " + partner_row["LastName"]
            partner_group = students[(students["FirstName"]==partner_row["FirstName"]) & (students["LastName"]==partner_row["LastName"])]["Group"].iloc[0]

            # Swap groups
            students.loc[(students["FirstName"]==student["FirstName"]) & (students["LastName"]==student["LastName"]),"Group"] = partner_group
            students.loc[(students["FirstName"]==partner_row["FirstName"]) & (students["LastName"]==partner_row["LastName"]),"Group"] = current_group

            # Record processed exchange
            processed_messages.append(f"{student_name} ↔ {partner_name}")
            add_message(f"✅ Exchange successful: {student_name} ↔ {partner_name}")

            # Remove processed requests
            requests_df = requests_df[~requests_df.apply(lambda r: (r["FirstName"] in [student["FirstName"], partner_row["FirstName"]]) & (r["LastName"] in [student["LastName"], partner_row["LastName"]]), axis=1)]

            # Log action
            log_action("Processed Exchange", student_name, partner_name)

    # Save updated data
    save_csv(students, STUDENTS_FILE)
    save_csv(requests_df, REQUESTS_FILE)
    save_csv(messages_df, MESSAGES_FILE)

    if processed_messages:
        st.success("✅ Exchanges processed:")
        for msg in processed_messages:
            st.write(msg)
    else:
        st.info("No eligible exchanges found.")

# ----------------------------
# Display Success Messages (Persistent)
# ----------------------------
st.subheader("📬 Success Messages")
messages_df = load_csv(MESSAGES_FILE, ["Date", "Message"])
if messages_df.empty:
    st.info("No exchange messages yet.")
else:
    st.dataframe(messages_df, use_container_width=True)

# ----------------------------
# Logs Section
# ----------------------------
st.subheader("📜 Logs")
logs = load_csv(LOGS_FILE, ["Date", "Action", "Student1", "Student2"])
if logs.empty:
    st.info("No logs yet.")
else:
    st.dataframe(logs, use_container_width=True)

# ----------------------------
# Footer
# ----------------------------
st.markdown("---")
st.caption("Persistent Student Exchange Web App with mutual requests, logs, and messages")
