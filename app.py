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


# -----------------------------
# Page Configuration
# -----------------------------
st.set_page_config(
    page_title="Role-Based RAG System",
    page_icon="🤖",
    layout="wide"
)

st.title("🤖 Role-Based RAG System")
st.write("Ask questions based on your authorized role and company documents.")


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

                with open(filepath, "r", encoding="utf-16-le") as file:
                    text = file.read()

        role = filename.split("_")[0]

        embedding = model.encode(text).tolist()

        points.append(
            PointStruct(
                id=point_id,
                vector=embedding,
                payload={
                    "role": role,
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
# Role Selection
# -----------------------------
roles = [
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

role = st.selectbox(
    "Select your role",
    roles
)


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

        with st.spinner("Searching documents..."):

            query_embedding = model.encode(question).tolist()

            # Role-based filtering BEFORE semantic search
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

            st.warning("No documents found for this role.")

        else:

            # -----------------------------
            # Build Context
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

The user's authorized role is: {role}

Answer the user's question ONLY using the provided documents.

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
                                "content": "You answer questions using only the provided company documents."
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

                    # -----------------------------
                    # Retrieved Documents
                    # -----------------------------
                    with st.expander("📚 Retrieved Documents"):

                        for result in results:

                            st.markdown(
                                f"**{result.payload['filename']}**"
                            )

                            st.write(
                                result.payload["text"]
                            )

                            st.divider()

                except Exception as e:

                    st.error(f"AI generation error: {e}")