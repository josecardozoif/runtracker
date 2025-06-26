from flask import Flask, render_template, request, jsonify
import requests
import math

app = Flask(__name__)

# Utilitários para conversão de tempo
def time_to_seconds(time_str):
    """Converte string de tempo (MM:SS ou HH:MM:SS) para segundos"""
    parts = time_str.split(":")
    if len(parts) == 2:
        return int(parts[0]) * 60 + int(parts[1])
    elif len(parts) == 3:
        return int(parts[0]) * 3600 + int(parts[1]) * 60 + int(parts[2])
    return 0

def seconds_to_time(seconds):
    """Converte segundos para string de tempo formatada"""
    hours = math.floor(seconds / 3600)
    minutes = math.floor((seconds % 3600) / 60)
    secs = math.floor(seconds % 60)
    
    if hours > 0:
        return f"{hours:02d}:{minutes:02d}:{secs:02d}"
    else:
        return f"{minutes:02d}:{secs:02d}"

@app.route('/')
def index():
    return render_template('index.html')

@app.route('/calculate_pace', methods=['POST'])
def calculate_pace():
    """Calculadora de Pace"""
    try:
        data = request.get_json()
        distance = float(data.get('distance', 0))
        time_str = data.get('time', '')
        
        if not distance or not time_str:
            return jsonify({'error': 'Por favor, preencha todos os campos.'})
        
        total_seconds = time_to_seconds(time_str)
        pace_seconds = total_seconds / distance
        pace_time = seconds_to_time(pace_seconds)
        speed_kmh = round(distance / (total_seconds / 3600), 2)
        
        return jsonify({
            'pace': pace_time,
            'speed': speed_kmh
        })
    except Exception as e:
        return jsonify({'error': 'Erro no cálculo. Verifique os valores inseridos.'})

@app.route('/calculate_time', methods=['POST'])
def calculate_time():
    """Calculadora de Tempo"""
    try:
        data = request.get_json()
        distance = float(data.get('distance', 0))
        pace_str = data.get('pace', '')
        
        if not distance or not pace_str:
            return jsonify({'error': 'Por favor, preencha todos os campos.'})
        
        pace_seconds = time_to_seconds(pace_str)
        total_seconds = pace_seconds * distance
        total_time = seconds_to_time(total_seconds)
        speed_kmh = round(distance / (total_seconds / 3600), 2)
        
        return jsonify({
            'time': total_time,
            'speed': speed_kmh
        })
    except Exception as e:
        return jsonify({'error': 'Erro no cálculo. Verifique os valores inseridos.'})

@app.route('/calculate_distance', methods=['POST'])
def calculate_distance():
    """Calculadora de Distância"""
    try:
        data = request.get_json()
        time_str = data.get('time', '')
        pace_str = data.get('pace', '')
        
        if not time_str or not pace_str:
            return jsonify({'error': 'Por favor, preencha todos os campos.'})
        
        total_seconds = time_to_seconds(time_str)
        pace_seconds = time_to_seconds(pace_str)
        distance = round(total_seconds / pace_seconds, 2)
        speed_kmh = round(distance / (total_seconds / 3600), 2)
        
        return jsonify({
            'distance': distance,
            'speed': speed_kmh
        })
    except Exception as e:
        return jsonify({'error': 'Erro no cálculo. Verifique os valores inseridos.'})

@app.route('/convert_units', methods=['POST'])
def convert_units():
    """Conversor de Unidades"""
    try:
        data = request.get_json()
        value = float(data.get('value', 0))
        from_unit = data.get('from', '')
        to_unit = data.get('to', '')
        
        if not value:
            return jsonify({'error': 'Por favor, insira um valor.'})
        
        # Conversões para metros
        to_meters = {
            'km': 1000,
            'mi': 1609.34,
            'm': 1,
            'ft': 0.3048,
            'yd': 0.9144,
        }
        
        units_pt = {
            'km': 'quilômetros',
            'mi': 'milhas',
            'm': 'metros',
            'ft': 'pés',
            'yd': 'jardas',
        }
        
        value_in_meters = value * to_meters[from_unit]
        result = value_in_meters / to_meters[to_unit]
        
        return jsonify({
            'result': round(result, 3),
            'from_unit_name': units_pt[from_unit],
            'to_unit_name': units_pt[to_unit],
            'original_value': value
        })
    except Exception as e:
        return jsonify({'error': 'Erro na conversão. Verifique os valores inseridos.'})

@app.route('/check_weather', methods=['POST'])
def check_weather():
    """Verificar condições climáticas"""
    try:
        data = request.get_json()
        location = data.get('location', '')
        
        if not location:
            return jsonify({'error': 'Por favor, insira uma localização.'})
        
        coords = location.split(',')
        if len(coords) != 2:
            return jsonify({'error': 'Formato inválido. Use: latitude, longitude'})
        
        lat = float(coords[0].strip())
        lon = float(coords[1].strip())
        
        # Fazer requisição para API do clima
        url = f"https://api.open-meteo.com/v1/forecast?latitude={lat}&longitude={lon}&current=temperature_2m,relative_humidity_2m,precipitation,wind_speed_10m&timezone=auto"
        response = requests.get(url, timeout=10)
        weather_data = response.json()
        
        temp = weather_data['current']['temperature_2m']
        humidity = weather_data['current']['relative_humidity_2m']
        precipitation = weather_data['current']['precipitation']
        wind_speed = weather_data['current']['wind_speed_10m']
        
        # Avaliação das condições
        status = "Agradável"
        status_class = "weather-good"
        recommendations = []
        
        if temp > 30:
            status = "Muito quente - Desagradável"
            status_class = "weather-bad"
            recommendations.extend([
                "Evite exercícios intensos",
                "Hidrate-se bem",
                "Prefira horários mais frescos"
            ])
        elif temp < 5:
            status = "Muito frio - Cuidado"
            status_class = "weather-bad"
            recommendations.extend([
                "Use roupas adequadas",
                "Faça aquecimento prolongado"
            ])
        elif precipitation > 2:
            status = "Chuva forte - Desagradável"
            status_class = "weather-bad"
            recommendations.extend([
                "Prefira exercícios internos",
                "Se correr, use roupas impermeáveis"
            ])
        elif wind_speed > 25:
            status = "Vento forte - Desagradável"
            status_class = "weather-bad"
            recommendations.extend([
                "Cuidado com a estabilidade",
                "Evite áreas abertas"
            ])
        elif 20 <= temp <= 25 and precipitation <= 0.5:
            status = "Condições ideais!"
            recommendations.append("Perfeito para corrida")
        elif 0.5 < precipitation <= 2:
            status = "Chuva leve - Aceitável"
            recommendations.append("Leve capa de chuva")
        
        return jsonify({
            'status': status,
            'status_class': status_class,
            'temperature': temp,
            'humidity': humidity,
            'precipitation': precipitation,
            'wind_speed': wind_speed,
            'recommendations': recommendations
        })
        
    except requests.RequestException:
        return jsonify({'error': 'Erro ao carregar dados climáticos'})
    except Exception as e:
        return jsonify({'error': 'Erro ao processar dados. Verifique a localização.'})

if __name__ == '__main__':
    app.run(debug=True, host='0.0.0.0', port=5000)