import os
import hmac
import json
import bcrypt
import streamlit as st
from qdrant_client import QdrantClient
from qdrant_client.models import (
    Distance,
    VectorParams,
    PointStruct,
    Filter,
    FieldCondition,
    MatchValue,
)
from sentence_transformers import SentenceTransformer
from huggingface_hub import InferenceClient

# -----------------------------
# User Authentication
# -----------------------------
USERS_FILE = "users.json"


def load_users():
    try:
        with open(USERS_FILE, "r", encoding="utf-8") as file:
            return json.load(file)
    except (FileNotFoundError, json.JSONDecodeError):
        return {}


def authenticate(username, password):
    users = load_users()

    user = users.get(username)

    if not user:
        return None

    stored_hash = user["password_hash"].encode("utf-8")

    if bcrypt.checkpw(
        password.encode("utf-8"),
        stored_hash
    ):
        return user["role"]

    return None

# -----------------------------
# Page Configuration
# -----------------------------
st.set_page_config(
    page_title="Role-Based RAG System",
    page_icon="🤖",
    layout="wide"
)


# -----------------------------
# Authentication
# -----------------------------


def authenticate(username, password):
    # Admin authentication
    if username == st.secrets["ADMIN"]["username"]:
        admin_hash = st.secrets["ADMIN"]["password_hash"]

        if bcrypt.checkpw(
            password.encode("utf-8"),
            admin_hash.encode("utf-8")
        ):
            return "ADMIN"

        return None

    # Regular user authentication
    users = load_users()

    user = users.get(username)

    if not user:
        return None

    stored_hash = user["password_hash"].encode("utf-8")

    if bcrypt.checkpw(
        password.encode("utf-8"),
        stored_hash
    ):
        return user["role"]

    return None


# -----------------------------
# Login Screen
# -----------------------------
if "authenticated" not in st.session_state:
    st.session_state.authenticated = False

if "user_role" not in st.session_state:
    st.session_state.user_role = None

if "username" not in st.session_state:
    st.session_state.username = None


if not st.session_state.authenticated:

    st.title("🔐 Role-Based RAG System")
    st.write("Sign in to access documents authorized for your role.")

    with st.form("login_form"):

        username = st.text_input(
            "Username",
            placeholder="Enter your username"
        )

        password = st.text_input(
            "Password",
            type="password",
            placeholder="Enter your password"
        )

        login_button = st.form_submit_button("🔐 Login")

        if login_button:

            authenticated_role = authenticate(
                username.strip(),
                password
            )

            if authenticated_role:

                st.session_state.authenticated = True
                st.session_state.user_role = authenticated_role
                st.session_state.username = username.strip()

                st.rerun()

            else:

                st.error("Invalid username or password.")

    st.stop()

    # -----------------------------
# Admin Panel
# -----------------------------
if st.session_state.user_role == "ADMIN":

    st.title("🛠️ Admin Panel")
    st.write("Create and manage authorized users.")

    with st.form("create_user_form"):

        new_username = st.text_input(
            "Username",
            placeholder="Example: engineer1"
        )

        new_password = st.text_input(
            "Password",
            type="password"
        )

        new_role = st.selectbox(
            "Assign Role",
            [
                "CEO",
                "Director",
                "VP",
                "Manager",
                "TeamLead",
                "SeniorEngineer",
                "Engineer",
                "Analyst",
                "HR",
                "Intern"
            ]
        )

        create_user = st.form_submit_button(
            "➕ Create User"
        )

        if create_user:

            new_username = new_username.strip()

            if not new_username or not new_password:
                st.warning(
                    "Username and password are required."
                )

            else:

                users = load_users()

                if new_username in users:

                    st.error(
                        "Username already exists."
                    )

                else:

                    password_hash = bcrypt.hashpw(
                        new_password.encode("utf-8"),
                        bcrypt.gensalt()
                    ).decode("utf-8")

                    users[new_username] = {
                        "password_hash": password_hash,
                        "role": new_role
                    }

                    with open(
                        USERS_FILE,
                        "w",
                        encoding="utf-8"
                    ) as file:

                        json.dump(
                            users,
                            file,
                            indent=4
                        )

                    st.success(
                        f"User '{new_username}' created successfully "
                        f"with role '{new_role}'."
                    )

# -----------------------------
# Logged-in User
# -----------------------------
st.title("🤖 Role-Based RAG System")

st.write(
    "Ask questions based on your authorized role and company documents."
)

role = st.session_state.user_role

st.success(f"🔐 Authenticated Role: {role}")

if st.button("Logout"):
    st.session_state.authenticated = False
    st.session_state.user_role = None
    st.rerun()


# -----------------------------
# Load Embedding Model
# -----------------------------
@st.cache_resource
def load_model():
    return SentenceTransformer("all-MiniLM-L6-v2")


model = load_model()


# -----------------------------
# Create Qdrant Database
# -----------------------------
@st.cache_resource
def create_qdrant():

    client = QdrantClient(":memory:")

    collection_name = "company_docs"

    client.create_collection(
        collection_name=collection_name,
        vectors_config=VectorParams(
            size=384,
            distance=Distance.COSINE
        )
    )

    documents_path = "documents"

    points = []
    point_id = 0

    for filename in os.listdir(documents_path):

        if not filename.endswith(".txt"):
            continue

        filepath = os.path.join(documents_path, filename)

        # Handle different encodings
        try:

            with open(filepath, "r", encoding="utf-8") as file:
                text = file.read()

        except UnicodeDecodeError:

            try:

                with open(filepath, "r", encoding="utf-16") as file:
                    text = file.read()

            except UnicodeDecodeError:

                with open(
                    filepath,
                    "r",
                    encoding="utf-16-le"
                ) as file:
                    text = file.read()

        role_from_document = filename.split("_")[0]

        embedding = model.encode(text).tolist()

        points.append(
            PointStruct(
                id=point_id,
                vector=embedding,
                payload={
                    "role": role_from_document,
                    "text": text,
                    "filename": filename
                }
            )
        )

        point_id += 1

    client.upsert(
        collection_name=collection_name,
        points=points
    )

    return client, collection_name


client, collection_name = create_qdrant()


# -----------------------------
# Hugging Face AI
# -----------------------------
@st.cache_resource
def load_llm():

    return InferenceClient(
        api_key=st.secrets["HF_TOKEN"],
        provider="auto"
    )


llm = load_llm()


# -----------------------------
# Question
# -----------------------------
question = st.text_input(
    "Ask your question",
    placeholder="Example: What are the responsibilities of an engineer?"
)


# -----------------------------
# Search + AI Answer
# -----------------------------
if st.button("🔍 Search"):

    if not question.strip():

        st.warning("Please enter a question.")

    else:

        with st.spinner("Searching authorized documents..."):

            query_embedding = model.encode(question).tolist()

            # IMPORTANT:
            # Role authorization happens DURING vector retrieval.
            # Unauthorized documents are excluded before they
            # can enter the LLM context.

            results = client.query_points(
                collection_name=collection_name,
                query=query_embedding,
                query_filter=Filter(
                    must=[
                        FieldCondition(
                            key="role",
                            match=MatchValue(value=role)
                        )
                    ]
                ),
                limit=3
            ).points

        if not results:

            st.warning(
                "I could not find enough information "
                "in the authorized documents."
            )

        else:

            # -----------------------------
            # Build Authorized Context
            # -----------------------------
            context = "\n\n".join(
                [
                    f"Document: {result.payload['filename']}\n"
                    f"{result.payload['text']}"
                    for result in results
                ]
            )

            # -----------------------------
            # Generate AI Answer
            # -----------------------------
            with st.spinner("🤖 Generating AI answer..."):

                prompt = f"""
You are a company document assistant.

The authenticated user's role is: {role}

Answer the user's question ONLY using the authorized documents
provided below.

Do not invent information.

If the documents do not contain enough information, say:

"I could not find enough information in the authorized documents."

User Question:
{question}

Authorized Documents:
{context}
"""

                try:

                    response = llm.chat.completions.create(
                        model="deepseek-ai/DeepSeek-V3-0324",
                        messages=[
                            {
                                "role": "system",
                                "content": (
                                    "You answer questions using only "
                                    "the provided authorized company documents."
                                )
                            },
                            {
                                "role": "user",
                                "content": prompt
                            }
                        ],
                        max_tokens=300,
                        temperature=0.2
                    )

                    answer = response.choices[0].message.content

                    st.subheader("🤖 AI Answer")
                    st.write(answer)

                except Exception as e:

                    st.error(
                        "An error occurred while generating the AI answer."
                    )
                    st.error(str(e)) 