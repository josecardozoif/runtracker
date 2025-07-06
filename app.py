from flask import Flask, render_template, request, jsonify
import requests
import math
from typing import Dict, Any

app = Flask(__name__)

class TimeConverter:
    """Classe para conversões de tempo"""
    
    @staticmethod
    def time_to_seconds(time_str: str) -> int:
        """Converte string de tempo (MM:SS ou HH:MM:SS) para segundos"""
        if not time_str:
            return 0
        
        parts = time_str.split(":")
        if len(parts) == 2:
            return int(parts[0]) * 60 + int(parts[1])
        elif len(parts) == 3:
            return int(parts[0]) * 3600 + int(parts[1]) * 60 + int(parts[2])
        return 0

    @staticmethod
    def seconds_to_time(seconds: float) -> str:
        """Converte segundos para string de tempo formatada"""
        hours = math.floor(seconds / 3600)
        minutes = math.floor((seconds % 3600) / 60)
        secs = math.floor(seconds % 60)
        
        if hours > 0:
            return f"{hours:02d}:{minutes:02d}:{secs:02d}"
        else:
            return f"{minutes:02d}:{secs:02d}"

class RunningCalculator:
    """Classe para cálculos de corrida"""
    
    def __init__(self):
        self.time_converter = TimeConverter()
    
    def calculate_pace(self, distance: float, time_str: str) -> Dict[str, Any]:
        """Calcula o pace baseado na distância e tempo"""
        if not distance or not time_str:
            return {'error': 'Por favor, preencha todos os campos.'}
        
        try:
            total_seconds = self.time_converter.time_to_seconds(time_str)
            if total_seconds == 0:
                return {'error': 'Formato de tempo inválido.'}
            
            pace_seconds = total_seconds / distance
            pace_time = self.time_converter.seconds_to_time(pace_seconds)
            speed_kmh = round(distance / (total_seconds / 3600), 2)
            
            return {
                'pace': pace_time,
                'speed': speed_kmh
            }
        except (ValueError, ZeroDivisionError):
            return {'error': 'Erro no cálculo. Verifique os valores inseridos.'}
    
    def calculate_time(self, distance: float, pace_str: str) -> Dict[str, Any]:
        """Calcula o tempo baseado na distância e pace"""
        if not distance or not pace_str:
            return {'error': 'Por favor, preencha todos os campos.'}
        
        try:
            pace_seconds = self.time_converter.time_to_seconds(pace_str)
            if pace_seconds == 0:
                return {'error': 'Formato de pace inválido.'}
            
            total_seconds = pace_seconds * distance
            total_time = self.time_converter.seconds_to_time(total_seconds)
            speed_kmh = round(distance / (total_seconds / 3600), 2)
            
            return {
                'time': total_time,
                'speed': speed_kmh
            }
        except (ValueError, ZeroDivisionError):
            return {'error': 'Erro no cálculo. Verifique os valores inseridos.'}
    
    def calculate_distance(self, time_str: str, pace_str: str) -> Dict[str, Any]:
        """Calcula a distância baseada no tempo e pace"""
        if not time_str or not pace_str:
            return {'error': 'Por favor, preencha todos os campos.'}
        
        try:
            total_seconds = self.time_converter.time_to_seconds(time_str)
            pace_seconds = self.time_converter.time_to_seconds(pace_str)
            
            if total_seconds == 0 or pace_seconds == 0:
                return {'error': 'Formato de tempo inválido.'}
            
            distance = round(total_seconds / pace_seconds, 2)
            speed_kmh = round(distance / (total_seconds / 3600), 2)
            
            return {
                'distance': distance,
                'speed': speed_kmh
            }
        except (ValueError, ZeroDivisionError):
            return {'error': 'Erro no cálculo. Verifique os valores inseridos.'}

class UnitConverter:
    """Classe para conversão de unidades"""
    
    def __init__(self):
        # Conversões para metros
        self.to_meters = {
            'km': 1000,
            'mi': 1609.34,
            'm': 1,
            'ft': 0.3048,
            'yd': 0.9144,
        }
        
        # Nomes das unidades em português
        self.units_pt = {
            'km': 'quilômetros',
            'mi': 'milhas',
            'm': 'metros',
            'ft': 'pés',
            'yd': 'jardas',
        }
    
    def convert(self, value: float, from_unit: str, to_unit: str) -> Dict[str, Any]:
        """Converte entre unidades de distância"""
        if not value:
            return {'error': 'Por favor, insira um valor.'}
        
        try:
            if from_unit not in self.to_meters or to_unit not in self.to_meters:
                return {'error': 'Unidade inválida.'}
            
            value_in_meters = value * self.to_meters[from_unit]
            result = value_in_meters / self.to_meters[to_unit]
            
            return {
                'result': round(result, 3),
                'from_unit_name': self.units_pt[from_unit],
                'to_unit_name': self.units_pt[to_unit],
                'original_value': value
            }
        except (ValueError, KeyError):
            return {'error': 'Erro na conversão. Verifique os valores inseridos.'}

class WeatherChecker:
    """Classe para verificação do clima"""
    
    def __init__(self):
        self.api_url = "https://api.open-meteo.com/v1/forecast"
    
    def check_weather(self, location: str) -> Dict[str, Any]:
        """Verifica as condições climáticas para corrida"""
        if not location:
            return {'error': 'Por favor, insira uma localização.'}
        
        try:
            coords = location.split(',')
            if len(coords) != 2:
                return {'error': 'Formato inválido. Use: latitude, longitude'}
            
            lat = float(coords[0].strip())
            lon = float(coords[1].strip())
            
            # Validação básica das coordenadas
            if not (-90 <= lat <= 90) or not (-180 <= lon <= 180):
                return {'error': 'Coordenadas inválidas.'}
            
            # Fazer requisição para API do clima
            params = {
                'latitude': lat,
                'longitude': lon,
                'current': 'temperature_2m,relative_humidity_2m,precipitation,wind_speed_10m',
                'timezone': 'auto'
            }
            
            response = requests.get(self.api_url, params=params, timeout=10)
            response.raise_for_status()
            weather_data = response.json()
            
            # Extrair dados do clima
            current = weather_data['current']
            temp = current['temperature_2m']
            humidity = current['relative_humidity_2m']
            precipitation = current['precipitation']
            wind_speed = current['wind_speed_10m']
            
            # Avaliação das condições
            status, status_class, recommendations = self._evaluate_conditions(
                temp, humidity, precipitation, wind_speed
            )
            
            return {
                'status': status,
                'status_class': status_class,
                'temperature': temp,
                'humidity': humidity,
                'precipitation': precipitation,
                'wind_speed': wind_speed,
                'recommendations': recommendations
            }
            
        except requests.RequestException as e:
            return {'error': 'Erro ao carregar dados climáticos'}
        except (ValueError, KeyError) as e:
            return {'error': 'Erro ao processar dados. Verifique a localização.'}
    
    def _evaluate_conditions(self, temp: float, humidity: float, 
                           precipitation: float, wind_speed: float) -> tuple:
        """Avalia as condições climáticas para corrida"""
        status = "Agradável"
        status_class = "weather-good"
        recommendations = []
        
        if temp > 30:
            status = "Muito Quente - Desagradável"
            status_class = "weather-bad"
            recommendations.extend([
                "Evite exercícios intensos",
                "Hidrate-se bem",
                "Prefira horários mais frescos"
            ])
        elif temp < 5:
            status = "Muito Frio - Cuidado"
            status_class = "weather-bad"
            recommendations.extend([
                "Use roupas adequadas",
                "Faça aquecimento prolongado"
            ])
        elif precipitation > 2:
            status = "Chuva Forte - Desagradável"
            status_class = "weather-bad"
            recommendations.extend([
                "Prefira exercícios internos",
                "Se correr, use roupas impermeáveis"
            ])
        elif wind_speed > 25:
            status = "Vento Forte - Desagradável"
            status_class = "weather-bad"
            recommendations.extend([
                "Cuidado com a estabilidade",
                "Evite áreas abertas"
            ])
        elif 20 <= temp <= 25 and precipitation <= 0.5:
            status = "Condições Ideais!"
            recommendations.append("Perfeito para corrida")
        elif 0.5 < precipitation <= 2:
            status = "Chuva Leve - Aceitável"
            status_class = "weather-warning"
            recommendations.append("Leve capa de chuva")
        elif humidity > 80:
            recommendations.append("Alta Umidade - hidrate-se bem")
        
        return status, status_class, recommendations

# Instanciar as classes
calculator = RunningCalculator()
converter = UnitConverter()
weather = WeatherChecker()

@app.route('/')
def index():
    return render_template('index.html')

@app.route('/calculate_pace', methods=['POST'])
def calculate_pace():
    """Endpoint para calcular pace"""
    try:
        data = request.get_json()
        distance = float(data.get('distance', 0))
        time_str = data.get('time', '')
        
        return jsonify(calculator.calculate_pace(distance, time_str))
    except (ValueError, TypeError):
        return jsonify({'error': 'Dados inválidos fornecidos.'})

@app.route('/calculate_time', methods=['POST'])
def calculate_time():
    """Endpoint para calcular tempo"""
    try:
        data = request.get_json()
        distance = float(data.get('distance', 0))
        pace_str = data.get('pace', '')
        
        return jsonify(calculator.calculate_time(distance, pace_str))
    except (ValueError, TypeError):
        return jsonify({'error': 'Dados inválidos fornecidos.'})

@app.route('/calculate_distance', methods=['POST'])
def calculate_distance():
    """Endpoint para calcular distância"""
    try:
        data = request.get_json()
        time_str = data.get('time', '')
        pace_str = data.get('pace', '')
        
        return jsonify(calculator.calculate_distance(time_str, pace_str))
    except (ValueError, TypeError):
        return jsonify({'error': 'Dados inválidos fornecidos.'})

@app.route('/convert_units', methods=['POST'])
def convert_units():
    """Endpoint para converter unidades"""
    try:
        data = request.get_json()
        value = float(data.get('value', 0))
        from_unit = data.get('from', '')
        to_unit = data.get('to', '')
        
        return jsonify(converter.convert(value, from_unit, to_unit))
    except (ValueError, TypeError):
        return jsonify({'error': 'Dados inválidos fornecidos.'})

@app.route('/check_weather', methods=['POST'])
def check_weather():
    """Endpoint para verificar condições climáticas"""
    try:
        data = request.get_json()
        location = data.get('location', '')
        
        return jsonify(weather.check_weather(location))
    except Exception as e:
        return jsonify({'error': 'Erro interno do servidor.'})

@app.errorhandler(404)
def not_found(error):
    return jsonify({'error': 'Endpoint não encontrado'}), 404

@app.errorhandler(500)
def internal_error(error):
    return jsonify({'error': 'Erro interno do servidor'}), 500

if __name__ == '__main__':
    app.run(debug=True, host='0.0.0.0', port=5000)