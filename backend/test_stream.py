from app.ai.service import AIService


ai = AIService()

messages = [
    {
        "role": "user",
        "content": "Explain machine learning in three short sentences.",
    }
]


print("\n--- AI SERVICE STREAM START ---\n")


full_response = ""

for chunk in ai.generate_stream(messages):
    print(chunk, end="", flush=True)
    full_response += chunk


print("\n\n--- AI SERVICE STREAM END ---")


print("\nFull response:")

print(full_response)