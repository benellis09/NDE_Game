import os
from groq import Groq

# Initialize the cloud client (it will automatically look for the API key)
client = Groq(api_key=os.environ.get("GROQ_API_KEY"))

def get_ndt_question():
    # Example generation call
    completion = client.chat.completions.create(
        model="llama-3.3-70b-versatile", # A powerful cloud model
        messages=[
            {"role": "user", "content": "Generate a game question..."}
        ]
    )
    return completion.choices[0].message.content

    # Query database for matching PDF text snippets
    results = collection.query(query_texts=[topic_keyword], n_results=2)
    if results['documents'] and results['documents'][0]:
        source_context = "\n---\n".join(results['documents'][0])
    else:
        source_context = "Use standard ASNT Level III NDT principles for this topic."

    prompt = f"""
    You are an educational Super Mario game engine. Use the following ASNT Level III NDT technical context to create one highly accurate, challenging multiple-choice question suitable for a Level III certification exam.
    
    Context from study materials:
    {source_context}
    
    Current Game World: {world_name}
    Topic to test: {topic_keyword}
    """

    # Define a rigid JSON blueprint that Ollama will force the model to follow
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
        # Call ollama passing the explicit format schema blueprint
        response = ollama.generate(
            model="llama3.2", 
            prompt=prompt,
            format=json_schema
        )
        
        # Because we used format=json_schema, this load is guaranteed to succeed
        question_data = json.loads(response['response'].strip())
        question_data["error"] = False
        return question_data
        
    except Exception as e:
        return {
            "error": True,
            "message": f"An error occurred while compiling game data: {str(e)}"
        }

if __name__ == "__main__":
    print("🔄 Testing structural output engine...")
    test_quiz = get_ndt_question("Ultrasonic transducer attenuation", "World 3: Water World")
    print(json.dumps(test_quiz, indent=2))
