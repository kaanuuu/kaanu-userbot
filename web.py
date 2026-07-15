from flask import Flask, request, jsonify, render_template
import os
import subprocess
import json

app = Flask(__name__)

@app.route('/')
def index():
    return render_template('index.html')

@app.route('/deploy', methods=['POST'])
def deploy():
    try:
        data = request.json
        
        # Set environment variables
        os.environ['API_ID'] = str(data['api_id'])
        os.environ['API_HASH'] = data['api_hash']
        os.environ['OWNER_ID'] = str(data['owner_id'])
        os.environ['PHONE'] = data['phone']
        
        # Save to .env file for Render
        with open('.env', 'w') as f:
            f.write(f"API_ID={data['api_id']}\n")
            f.write(f"API_HASH={data['api_hash']}\n")
            f.write(f"OWNER_ID={data['owner_id']}\n")
            f.write(f"PHONE={data['phone']}\n")
        
        # Start bot in background
        subprocess.Popen(['python3', 'bot.py'], stdout=subprocess.PIPE, stderr=subprocess.PIPE)
        
        return jsonify({
            'success': True,
            'message': '✅ UserBot deployed successfully! Bot is now running.'
        })
    except Exception as e:
        return jsonify({
            'success': False,
            'message': f'❌ Deployment failed: {str(e)}'
        })

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=5000)
