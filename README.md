# RunTracker - Calculadoras de Corrida
# Por: José Eduardo Cardozo Araújo & Filipe Pereira Lima

Uma aplicação web para cálculos relacionados à corrida, incluindo pace, tempo, distância e verificação de condições climáticas utilizando da API Open-Meteo.

## Estrutura
runtracker/
├── app.py
├── requirements.txt
├── .gitignore
├── README.md
├── templates/
│   └── index.html
└── static/
    └── style.css

## Funcionalidades

- Calculadora de Pace
- Calculadora de Tempo
- Calculadora de Distância
- Conversor de Unidades
- Verificação de Condições Climáticas

## Como executar

1. Clone o repositório
2. Instale as dependências: `pip install -r requirements.txt` ou apenas `pip install flask requests`
3. Execute: `python app.py`
4. Acesse: `http://localhost:5000`

## Tecnologias

- Python Flask
- HTML/CSS/JavaScript
- API Open-Meteo para clima
