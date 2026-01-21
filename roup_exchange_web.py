import streamlit as st
import pandas as pd

# ----------------------------
# Page Configuration
# ----------------------------
st.set_page_config(
    page_title="Student Group Exchange",
    page_icon="🔄",
    layout="centered"
)

st.title("🔄 Student Group Exchange System (Mutual Request)")
st.write("Students request exchanges. Swap happens **only if both students request each other** and genders match.")

# ----------------------------
# Session State Initialization
# ----------------------------
if "students" not in st.session_state:
    st.session_state.students = pd.DataFrame(
        columns=["Name", "Gender", "Group"]
    )

if "requests" not in st.session_state:
    st.session_state.requests = pd.DataFrame(
        columns=["Name", "TargetGroup"]
    )

df = st.session_state.students
requests_df = st.session_state.requests

# ----------------------------
# Add Student Section
# ----------------------------
st.subheader("➕ Add a Student")

with st.form("add_student_form"):
    col1, col2, col3 = st.columns(3)
    with col1:
        name = st.text_input("Student Name")
    with col2:
        gender = st.selectbox("Gender", ["F", "M"])
    with col3:
        group = st.number_input("Group", min_value=1, step=1)

    submitted = st.form_submit_button("Add Student")

    if submitted:
        if not name.strip():
            st.error("❌ Name cannot be empty.")
        elif name in df["Name"].values:
            st.error("❌ Student already exists.")
        else:
            new_student = pd.DataFrame([{"Name": name.strip(), "Gender": gender, "Group": group}])
            st.session_state.students = pd.concat([df, new_student], ignore_index=True)
            st.success(f"✅ {name} added successfully!")
            st.rerun()

# ----------------------------
# Show Students
# ----------------------------
st.subheader("📋 Current Students")
if df.empty:
    st.info("No students added yet.")
else:
    st.dataframe(df, use_container_width=True)

# ----------------------------
# Submit Exchange Request
# ----------------------------
st.subheader("📝 Request to Change Group")

if df.empty:
    st.warning("Please add students first.")
else:
    student_name = st.selectbox("Select student", df["Name"].tolist())
    current_group = df[df["Name"] == student_name]["Group"].iloc[0]

    target_group = st.number_input(
        "Target Group",
        min_value=1,
        step=1,
        value=current_group
    )

    if st.button("Submit Request"):
        if target_group == current_group:
            st.warning("⚠ You are already in this group.")
        elif student_name in requests_df["Name"].values:
            st.warning("⚠ You already submitted a request.")
        else:
            st.session_state.requests = pd.concat(
                [requests_df, pd.DataFrame([{"Name": student_name, "TargetGroup": target_group}])],
                ignore_index=True
            )
            st.success(f"Request submitted: {student_name} wants to go to Group {target_group}.")

# ----------------------------
# Show Pending Requests
# ----------------------------
st.subheader("📌 Pending Exchange Requests")
if requests_df.empty:
    st.info("No requests yet.")
else:
    st.dataframe(requests_df, use_container_width=True)

# ----------------------------
# Process Exchanges
# ----------------------------
st.subheader("🔁 Process Eligible Exchanges")

if st.button("Process Exchanges"):
    processed = []
    for _, req in requests_df.iterrows():
        student_name = req["Name"]
        target_group = req["TargetGroup"]
        student = df[df["Name"] == student_name].iloc[0]
        student_gender = student["Gender"]
        current_group = student["Group"]

        # Look for a reciprocal request
        reciprocal = requests_df[
            (requests_df["TargetGroup"] == current_group) &
            (requests_df["Name"] != student_name)
        ]

        # Filter by gender
        reciprocal = reciprocal[
            reciprocal["Name"].apply(lambda n: df[df["Name"] == n]["Gender"].iloc[0] == student_gender)
        ]

        if not reciprocal.empty:
            partner_name = reciprocal.iloc[0]["Name"]
            # Swap groups
            partner_group = df[df["Name"] == partner_name]["Group"].iloc[0]
            df.loc[df["Name"] == student_name, "Group"] = partner_group
            df.loc[df["Name"] == partner_name, "Group"] = current_group
            processed.append(f"{student_name} ↔ {partner_name}")

            # Remove both requests
            requests_df = requests_df[
                ~requests_df["Name"].isin([student_name, partner_name])
            ]

    st.session_state.students = df
    st.session_state.requests = requests_df

    if processed:
        st.success("✅ Exchanges processed:")
        for p in processed:
            st.write(f"🔁 {p}")
    else:
        st.info("No eligible exchanges found.")

# ----------------------------
# Footer
# ----------------------------
st.markdown("---")
st.caption("Web app for classroom group management with mutual request system")
