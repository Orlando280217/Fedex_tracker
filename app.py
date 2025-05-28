from flask import Flask, request, jsonify
import requests

app = Flask(__name__)

# Reemplaza con tus datos reales de FedEx
FEDEX_CLIENT_ID = 'TU_CLIENT_ID'
FEDEX_CLIENT_SECRET = 'TU_CLIENT_SECRET'
FEDEX_OAUTH_URL = 'https://apis.fedex.com/oauth/token'
FEDEX_TRACK_URL = 'https://apis.fedex.com/track/v1/trackingnumbers'

def get_fedex_token():
    headers = {'Content-Type': 'application/x-www-form-urlencoded'}
    data = {
        'grant_type': 'client_credentials',
        'client_id': FEDEX_CLIENT_ID,
        'client_secret': FEDEX_CLIENT_SECRET
    }
    response = requests.post(FEDEX_OAUTH_URL, headers=headers, data=data)
    if response.status_code == 200:
        return response.json().get('access_token')
    return None

@app.route('/track-fedex', methods=['POST'])
def track_fedex():
    data = request.get_json()
    tracking_number = data.get('tracking_number')

    token = get_fedex_token()
    if not token:
        return jsonify({'error': 'No se pudo obtener el token'}), 500

    headers = {
        'Authorization': f'Bearer {token}',
        'Content-Type': 'application/json'
    }

    body = {
        "trackingInfo": [
            {
                "trackingNumberInfo": {
                    "trackingNumber": tracking_number
                }
            }
        ],
        "includeDetailedScans": True
    }

    response = requests.post(FEDEX_TRACK_URL, headers=headers, json=body)

    if response.status_code != 200:
        return jsonify({'error': 'No se pudo rastrear la guía'}), 500

    track = response.json()
    try:
        result = track['output']['completeTrackResults'][0]['trackResults'][0]
        status = result['latestStatusDetail']['statusByLocale']
        location = result['scanEvents'][0]['scanLocation']['city']
        estimated = result['dateAndTimes'][0]['dateTime']
        return jsonify({
            'status': status,
            'location': location,
            'estimatedDelivery': estimated
        })
    except:
        return jsonify({'error': 'No se pudo interpretar la respuesta'}), 500

if __name__ == '__main__':
    app.run(debug=True)
