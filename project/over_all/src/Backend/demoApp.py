from flask import Flask, request, jsonify
from langchain_community.chat_models import ChatOllama

app = Flask(__name__)

# Initialize the model
model_name = 'llama3'  # Change this if you have a different model
model = ChatOllama(model=model_name)

@app.route('/query', methods=['POST'])
def query_model():
    try:
        data = request.json
        prompt = data.get('prompt', '')
        
        # Print the prompt for debugging
        print(f"Received prompt: {prompt}")
        
        # Generate a response from the model using invoke
        response = model.invoke(prompt)
        
        # Print the response for debugging
        print(f"Model response: {response}")
        
        return jsonify({'response': response})
    
    except Exception as e:
        # Print the exception for debugging
        print(f"Error: {e}")
        return jsonify({'error': str(e)}), 500

if __name__ == '__main__':
    app.run(debug=True)
