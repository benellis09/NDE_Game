import os
import json
from groq import Groq

# Initialize the cloud client (it looks for your GROQ_API_KEY secret)
client = Groq(api_key=os.environ.get("GROQ_API_KEY"))

# Ensure your 'collection' variable from chromadb is initialized above this line
# e.g., collection = your_chromadb_setup_here

def get_ndt_question(topic, world):
    # Map the arguments from app.py to match your original variable names
    topic_keyword = topic
    world_name = world

    try:
        # 1. Query your database for matching PDF text snippets
        results = collection.query(query_texts=[topic_keyword], n_results=2)
        if results.get('documents') and results['documents'][0]:
            source_context = "\n---\n".join(results['documents'][0])
        else:
            source_context = "Use standard ASNT Level III NDT principles for this topic."
    except Exception as db_error:
        # Fallback if ChromaDB query fails during deployment initialization
        source_context = "Use standard ASNT Level III NDT principles for this topic."

    # 2. Build the original educational Super Mario prompt
    prompt = f"""
    You are an educational Super Mario game engine. Use the following ASNT Level III NDT technical context to create one highly accurate, challenging multiple-choice question suitable for a Level III certification exam.
    
    Context from study materials:
    {source_context}
    
    Current Game World: {world_name}
    Topic to test: {topic_keyword}
    """

    # 3. Define the blueprint schema for Groq's json_mode
    json_schema = {
        "type": "object",
        "properties": {
            "world": {"type": "string"},
            "question": {"type": "string"},
            "options": {
                "type": "array",
                "items": {"type": "string"},
                "minItems": 4,
                "maxItems": 4
            },
            "correct_option_index": {"type": "integer"},
            "item_reward": {"type": "string"},
            "study_tip": {"type": "string"}
        },
        "required": ["world", "question", "options", "correct_option_index", "item_reward", "study_tip"]
    }

    try:
              # 4. Call Groq Cloud API with structured JSON output enforcement
        response = client.chat.completions.create(
            model="openai/gpt-oss-120b",  # <--- Updated to the active production model
            messages=[

                {
                    "role": "system", 
                    "content": f"You are a helpful assistant that outputs database entries strictly matching this JSON schema: {json.dumps(json_schema)}."
                },
                {"role": "user", "content": prompt}
            ],
            temperature=0.7,
            # This tells Groq to guarantee a parsable JSON object back
            response_format={"type": "json_object"} 
        )

        # 5. Parse the returned text string into a Python dictionary
        raw_response = response.choices[0].message.content
        question_data = json.loads(raw_response.strip())
        question_data["error"] = False
        return question_data

    except Exception as e:
        return {
            "error": True,
            "message": f"An error occurred while compiling game data: {str(e)}"
        }

if __name__ == "__main__":
    print("🔄 Testing structural output engine...")
    # Note: Make sure 'collection' is mocked or available if running this test block locally
    test_quiz = get_ndt_question("Ultrasonic transducer attenuation", "World 3: Water World")
    print(json.dumps(test_quiz, indent=2))
