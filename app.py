import os
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


# ============================================================
# PAGE CONFIGURATION
# ============================================================

st.set_page_config(
    page_title="Role-Based RAG System",
    page_icon="🤖",
    layout="wide"
)


# ============================================================
# HEADER
# ============================================================

st.title("🤖 Role-Based RAG System")

st.write(
    "Public RAG demo — select a role and ask questions "
    "based on the documents authorized for that role."
)


# ============================================================
# PUBLIC ROLE SELECTION
# ============================================================

st.subheader("👤 Select Your Role")

role = st.selectbox(
    "Choose a role",
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

st.success(f"🔐 Selected Role: {role}")


# ============================================================
# LOAD EMBEDDING MODEL
# ============================================================

@st.cache_resource
def load_model():
    return SentenceTransformer("all-MiniLM-L6-v2")


model = load_model()


# ============================================================
# CREATE QDRANT DATABASE
# ============================================================

@st.cache_resource
def create_qdrant():

    client = QdrantClient(":memory:")

    collection_name = "company_docs"

    # Create collection
    client.create_collection(
        collection_name=collection_name,
        vectors_config=VectorParams(
            size=384,
            distance=Distance.COSINE
        )
    )

    documents_path = "documents"

    # Check documents folder
    if not os.path.exists(documents_path):
        st.error(
            "❌ 'documents' folder not found. "
            "Please create a documents folder and add your .txt files."
        )
        st.stop()

    points = []

    point_id = 0

    # Read documents
    for filename in os.listdir(documents_path):

        if not filename.endswith(".txt"):
            continue

        filepath = os.path.join(
            documents_path,
            filename
        )

        text = ""

        # ----------------------------------------
        # UTF-8
        # ----------------------------------------

        try:

            with open(
                filepath,
                "r",
                encoding="utf-8"
            ) as file:

                text = file.read()

        except UnicodeDecodeError:

            # ------------------------------------
            # UTF-16
            # ------------------------------------

            try:

                with open(
                    filepath,
                    "r",
                    encoding="utf-16"
                ) as file:

                    text = file.read()

            except UnicodeDecodeError:

                # --------------------------------
                # UTF-16 LE
                # --------------------------------

                try:

                    with open(
                        filepath,
                        "r",
                        encoding="utf-16-le"
                    ) as file:

                        text = file.read()

                except UnicodeDecodeError:

                    st.warning(
                        f"⚠️ Could not read file: {filename}"
                    )

                    continue

        # Skip empty documents
        if not text.strip():
            continue

        # ------------------------------------------------
        # ROLE FROM FILE NAME
        #
        # Example:
        # Engineer_responsibilities.txt
        #
        # Role = Engineer
        # ------------------------------------------------

        role_from_document = filename.split("_")[0]

        # Generate embedding
        embedding = model.encode(text).tolist()

        # Create Qdrant point
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

    # Check if documents exist
    if not points:

        st.error(
            "❌ No valid .txt documents found inside the documents folder."
        )

        st.stop()

    # Insert documents into Qdrant
    client.upsert(
        collection_name=collection_name,
        points=points
    )

    return client, collection_name


# Create Qdrant
client, collection_name = create_qdrant()


# ============================================================
# HUGGING FACE AI
# ============================================================

@st.cache_resource
def load_llm():

    return InferenceClient(
        api_key=st.secrets["HF_TOKEN"],
        provider="auto"
    )


llm = load_llm()


# ============================================================
# QUESTION INPUT
# ============================================================

st.subheader("💬 Ask Your Question")

question = st.text_input(
    "Ask your question",
    placeholder=(
        "Example: What are the responsibilities of an engineer?"
    )
)


# ============================================================
# SEARCH BUTTON
# ============================================================

if st.button("🔍 Search"):

    # ----------------------------------------
    # Validate question
    # ----------------------------------------

    if not question.strip():

        st.warning(
            "⚠️ Please enter a question."
        )

        st.stop()

    # ----------------------------------------
    # Search
    # ----------------------------------------

    with st.spinner(
        "🔎 Searching authorized documents..."
    ):

        # Convert question into embedding
        query_embedding = model.encode(
            question
        ).tolist()

        # ------------------------------------------------
        # ROLE-BASED RETRIEVAL
        #
        # Only documents matching the selected role
        # are retrieved.
        # ------------------------------------------------

        results = client.query_points(
            collection_name=collection_name,
            query=query_embedding,
            query_filter=Filter(
                must=[
                    FieldCondition(
                        key="role",
                        match=MatchValue(
                            value=role
                        )
                    )
                ]
            ),
            limit=3
        ).points

    # ====================================================
    # NO RESULTS
    # ====================================================

    if not results:

        st.warning(
            "I could not find enough information "
            "in the authorized documents."
        )

        st.stop()

    # ====================================================
    # BUILD AUTHORIZED CONTEXT
    # ====================================================

    context = "\n\n".join(
        [
            (
                f"Document: {result.payload['filename']}\n"
                f"{result.payload['text']}"
            )
            for result in results
        ]
    )


    # ====================================================
    # AI PROMPT
    # ====================================================

    prompt = f"""
You are a company document assistant.

The selected user's role is: {role}

Answer the user's question ONLY using the authorized
documents provided below.

Do not invent information.

If the documents do not contain enough information, say:

"I could not find enough information in the authorized documents."

User Question:
{question}

Authorized Documents:
{context}
"""


    # ====================================================
    # GENERATE AI ANSWER
    # ====================================================

    with st.spinner(
        "🤖 Generating AI answer..."
    ):

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


            # ====================================================
            # DISPLAY ANSWER
            # ====================================================

            st.subheader("🤖 AI Answer")

            st.write(answer)


            # ====================================================
            # SHOW SOURCES
            # ====================================================

            st.subheader("📚 Sources")

            for result in results:

                st.caption(
                    f"📄 {result.payload['filename']}"
                )


        except Exception as e:

            st.error(
                "❌ An error occurred while generating "
                "the AI answer."
            )

            st.error(str(e))


# ============================================================
# FOOTER
# ============================================================

st.divider()

st.caption(
    "🔒 Role-Based RAG Demo | "
    "Qdrant + Sentence Transformers + Hugging Face"
)