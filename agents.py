from capacities import EvaluationCapacity, CommunicativeCapacity
from skills import InvestmentSkill
from events import MarketEvent, FipaPerformative, TransactionType

import random

class Agent:
    """Clase base para todos los agentes."""

    def __init__(self, id: str):
        self.id = id
        self.comms = CommunicativeCapacity()

    def initialize(self):
        print(f"Agente {self.id} inicializado.")

    def run_cycle(self, tick: int):
        """Simula un tick/latido o paso de tiempo."""
        pass

class MarketAgent(Agent, EvaluationCapacity):
    """El agente que simula el mercado de la criptomoneda."""

    def __init__(self, id: str, initial_price: float = 100.0):
        super().__init__(id)
        self.price_history = [initial_price]
        self.current_price = initial_price

    def initialize(self):
        super().initialize()
        print(f"Precio inicial de la criptomoneda: ${self.current_price:.2f}")

    def update_price(self):
        """Simula una fluctuación aleatoria del precio."""
        change = random.uniform(-5.0, 5.0)  # Cambio de precio simulado
        new_price = self.current_price * (1 + change / 100)
        self.current_price = max(1.0, new_price)  # para que el precio no baje de 1.0
        self.price_history.append(self.current_price)
        print(f"--- Atencion! Nuevo Precio: ${self.current_price:.2f} ---")

    def run_cycle(self, tick: int):
        self.update_price()

    def process_cfp(self, event: MarketEvent):
        """Responde a un CFP con una PROPOSE."""
        # La oferta es simplificada: solo se opera a precio de mercado.
        offer = {
            "price": self.current_price,  # algun agente quiere comprar/vender al precio de mercado
            "best_buy": self.current_price * 0.99,  # un poco menos para compra
            "best_sell": self.current_price * 1.01  # un poco más para venta
        }
        response = MarketEvent(self.id, event.sender, FipaPerformative.PROPOSE, offer)
        self.comms.send_event(response)

    def process_accept(self, event: MarketEvent):
        """Ejecuta una transacción y responde con INFORM."""
        transaction_type = event.content.get("type", "UNKNOWN")

        print(f"*** TRANSACCIÓN EJECUTADA: {event.sender} realiza {transaction_type} en ${self.current_price:.2f} ***")

        response = MarketEvent(self.id, event.sender, FipaPerformative.INFORM,
                               {"status": "success", "price": self.current_price, "action": transaction_type})
        self.comms.send_event(response)

class InvestorAgent(Agent, EvaluationCapacity):
    """Agente inversor con personalidad (tolerancia al riesgo).
        Trabajo futuro: conectar con OPENA API para que pueda tomar una decision mas precisa.
    """
    def __init__(self, id: str, risk_tolerance: float, fiat_balance: float = 1000.0, crypto_balance: float = 10.0):
        super().__init__(id)
        self.risk_tolerance = risk_tolerance
        self.skill = InvestmentSkill(risk_tolerance)
        self.fiat_balance = fiat_balance
        self.crypto_balance = crypto_balance
        self.market_id = "Mercado01"
        self.pending_action = None  # Almacena la ultima accion que se hizo (BUY o SELL)

    def initialize(self):
        super().initialize()
        personality = "Impulsivo" if self.risk_tolerance > 0.4 else "Racional"
        print(f"Agente {self.id} inicializado. Personalidad: {personality} (Riesgo: {self.risk_tolerance:.2f})")

    def run_cycle(self, tick: int, market_history: list):
        if len(market_history) < 2:
            print(f"{self.id}: Esperando más datos de mercado.")
            return

        current_price = market_history[-1]
        price_change = self.evaluate_price_change(current_price, market_history)
        
        action, amount = self.skill.decide_transaction(price_change)

        if action:
            # Almacenar la acción para usarla cuando recibamos el PROPOSE
            self.pending_action = action
            print(f"[{self.id} DECISION: {action.value.upper()} | Var: {price_change*100:.2f}%] -> Enviando CFP al Mercado...")
            
            # 1. CFP: Iniciar el FIPA Contract Net Protocol
            cfp_content = {"request": "offer_for_trade", "type": action.value, "amount": amount}
            cfp_event = MarketEvent(self.id, self.market_id, FipaPerformative.CFP, cfp_content)
            self.comms.send_event(cfp_event)
            # Nota: La respuesta PROPOSE se maneja con el handle_propose en el siguiente tick.

    def handle_propose(self, event: MarketEvent):
        """Maneja el PROPOSE del Agente Mercado."""
        # Lógica de Inversor: Acepta la propuesta si está dispuesto a actuar.
        
        price = event.content.get("price")
        
        # Verificar que tenemos una acción pendiente
        if self.pending_action is None:
            print(f"[{self.id} PROPOSE RECIBIDO: ${price:.2f}] -> Sin acción pendiente, rechazando.")
            return
        
        # Determinar el tipo de transacción basado en la acción pendiente
        transaction_type = self.pending_action  # TransactionType.BUY o TransactionType.SELL
        
        print(f"[{self.id} PROPOSE RECIBIDO: ${price:.2f}] -> Aceptando oferta para {transaction_type.value.upper()}.")
        
        # 2. ACCEPT_PROPOSAL
        # Enviamos el tipo de transacción correcto (BUY o SELL)
        accept_content = {"price": price, "type": transaction_type.value}
        accept_event = MarketEvent(self.id, self.market_id, FipaPerformative.ACCEPT_PROPOSAL, accept_content)
        self.comms.send_event(accept_event)
        
        # Limpiar la acción pendiente después de enviar el ACCEPT
        self.pending_action = None

    def handle_inform(self, event: MarketEvent):
        """Maneja el INFORM (confirmación de transacción)."""
        status = event.content.get("status")
        price = event.content.get("price")
        action = event.content.get("action")
        
        if status == "success":
            # Actualización simplificada de cartera
            amount = 1.0 # Cantidad simplificada
            if action == TransactionType.BUY.value:
                self.crypto_balance += amount
                self.fiat_balance -= price * amount
            elif action == TransactionType.SELL.value:
                self.crypto_balance -= amount
                self.fiat_balance += price * amount

            print(f"[{self.id} INFORM: {action.upper()} OK en ${price:.2f}] Saldo Fiat: ${self.fiat_balance:.2f} | Saldo Cripto: {self.crypto_balance:.2f}")
        else:
            print(f"[{self.id} INFORM: Transacción fallida.]")