# app.py
from flask import Flask, render_template, jsonify, request
from agents import MarketAgent, InvestorAgent
from events import MarketEvent, FipaPerformative, TransactionType
from message_dispatcher import MessageDispatcher
import json

app = Flask(__name__)

class WebBoot:
    """Boot que captura datos para la web."""
    def __init__(self):
        self.agents = {}
        self.market = None
        self.dispatcher = MessageDispatcher()
        self.simulation_data = {
            'price_history': [],
            'cycles': [],
            'transactions': [],
            'agent_states': [],
            'logs': []
        }
    
    def initialize_agents(self, initial_price=100.0):
        """Crea los agentes e inicializa el sistema."""
        self.dispatcher.clear_queue()
        
        # Agente Mercado solo 1 por ahora
        self.market = MarketAgent("Mercado01", initial_price=initial_price)
        self.agents[self.market.id] = self.market
        self.dispatcher.register_agent(self.market.id, self.market)
        self.market.initialize()
        
        # Agentes Inversores con diferentes personalidades
        inv_racional = InvestorAgent("InversorRacional_A1", risk_tolerance=0.1, fiat_balance=500.0, crypto_balance=5.0)
        self.agents[inv_racional.id] = inv_racional
        self.dispatcher.register_agent(inv_racional.id, inv_racional)
        inv_racional.initialize()

        inv_impulsivo = InvestorAgent("InversorImpulsivo_B", risk_tolerance=0.6, fiat_balance=500.0, crypto_balance=5.0)
        self.agents[inv_impulsivo.id] = inv_impulsivo
        self.dispatcher.register_agent(inv_impulsivo.id, inv_impulsivo)
        inv_impulsivo.initialize()
        
        inv_medio = InvestorAgent("InversorMedio_C", risk_tolerance=0.3, fiat_balance=500.0, crypto_balance=5.0)
        self.agents[inv_medio.id] = inv_medio
        self.dispatcher.register_agent(inv_medio.id, inv_medio)
        inv_medio.initialize()
        
        # Configurar los agentes para usar el dispatcher
        for agent in self.agents.values():
            agent.comms.set_dispatcher(self.dispatcher)
        
        # Aqui guardo el estado inicial de los agentes antes de comenzar la simulación.
        self._capture_agent_states(0)
    
    def _capture_agent_states(self, cycle):
        """Captura el estado de todos los agentes."""
        states = {
            'cycle': cycle,
            'market_price': self.market.current_price,
            'investors': {}
        }
        
        for agent_id, agent in self.agents.items():
            if isinstance(agent, InvestorAgent):
                states['investors'][agent_id] = {
                    'fiat_balance': round(agent.fiat_balance, 2),
                    'crypto_balance': round(agent.crypto_balance, 2),
                    'risk_tolerance': agent.risk_tolerance
                }
        
        self.simulation_data['agent_states'].append(states)
        self.simulation_data['price_history'].append(self.market.current_price)
    
    def _dispatch_messages(self, max_iterations=10):
        """Procesa los mensajes de la cola usando el MessageDispatcher."""
        # Despachar mensajes usando el dispatcher
        # La captura de transacciones se hace interceptando los eventos antes del dispatch
        processed = 0
        iterations = 0
        
        while self.dispatcher.message_queue and iterations < max_iterations:
            # Procesar todos los mensajes actuales en la cola
            current_batch = list(self.dispatcher.message_queue)
            self.dispatcher.message_queue.clear()
            
            for event in current_batch:
                # Capturar transacciones antes de procesar
                if event.performative.value == "inform" and event.content.get("status") == "success":
                    cycle = self.current_cycle if hasattr(self, 'current_cycle') else len(self.simulation_data['price_history'])
                    self.simulation_data['transactions'].append({
                        'cycle': cycle,
                        'sender': event.sender,
                        'receiver': event.receiver,
                        'action': event.content.get("action"),
                        'price': event.content.get("price")
                    })
                
                # Procesar el mensaje normalmente
                target_agent = self.dispatcher.agents.get(event.receiver)
                if target_agent:
                    self.dispatcher._deliver_to_agent(target_agent, event)
                    processed += 1
                else:
                    # Si no hay receptor, mantener el mensaje en la cola
                    self.dispatcher.message_queue.append(event)
            
            iterations += 1
    
    def run_simulation(self, cycles: int = 5):
        """Ejecuta la simulación y captura datos."""
        self.simulation_data = {
            'price_history': [],
            'cycles': [],
            'transactions': [],
            'agent_states': [],
            'logs': []
        }
        
        self.current_cycle = 0
        
        for t in range(1, cycles + 1):
            self.current_cycle = t
            
            # 1. El mercado actualiza el precio
            self.market.run_cycle(t)
            
            # 2. Los inversores toman decisiones
            for agent in self.agents.values():
                if isinstance(agent, InvestorAgent):
                    agent.run_cycle(t, self.market.price_history)
            
            # 3. Despacho de Mensajes (itera hasta procesar todos)
            self._dispatch_messages()
            
            # 4. Capturar estado del ciclo
            self._capture_agent_states(t)
        
        return self.simulation_data

@app.route('/')
def index():
    """Página principal."""
    return render_template('index.html')

@app.route('/api/simulate', methods=['POST'])
def simulate():
    """Endpoint para ejecutar una simulación."""
    data = request.json
    cycles = data.get('cycles', 8)
    initial_price = data.get('initial_price', 100.0)
    
    simulator = WebBoot()
    simulator.initialize_agents(initial_price=initial_price)
    result = simulator.run_simulation(cycles=cycles)
    
    # Calcular estadísticas
    prices = result['price_history']
    print(result['transactions'])
    if prices:
        result['statistics'] = {
            'initial_price': prices[0],
            'final_price': prices[-1],
            'max_price': max(prices),
            'min_price': min(prices),
            'price_change': prices[-1] - prices[0],
            'price_change_percent': ((prices[-1] - prices[0]) / prices[0]) * 100,
            'total_transactions': len(result['transactions']),
            'buy_transactions': len([t for t in result['transactions'] if t['action'] == TransactionType.BUY.value]),
            'sell_transactions': len([t for t in result['transactions'] if t['action'] == TransactionType.SELL.value])
        }
    
    return jsonify(result)

if __name__ == '__main__':
    app.run(debug=True, host='0.0.0.0', port=5000)

