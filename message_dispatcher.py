# message_dispatcher.py
"""
    MessageDispatcher: Sistema de cola y despacho de mensajes entre agentes.
"""

from collections import deque
from typing import Dict, Optional
from events import MarketEvent, FipaPerformative


class MessageDispatcher:
    """Dispatcher centralizado para manejar la comunicación entre agentes."""
    
    def __init__(self):
        """Inicializa el dispatcher con una cola de mensajes."""
        self.message_queue = deque()  # Cola de mensajes pendientes
        self.agents = {}  # Registro de agentes por ID
        self.message_history = []  # Historial de mensajes (opcional, para debugging)
    
    def register_agent(self, agent_id: str, agent):
        """Registra un agente en el dispatcher."""
        self.agents[agent_id] = agent
    
    def unregister_agent(self, agent_id: str):
        """Elimina un agente del registro."""
        if agent_id in self.agents:
            del self.agents[agent_id]
    
    def send_event(self, event: MarketEvent):
        """Envía un evento a la cola de mensajes."""
        if not isinstance(event, MarketEvent):
            raise ValueError("El evento debe ser una instancia de MarketEvent")
        
        # Agregar a la cola
        self.message_queue.append(event)
        
        # Opcional: guardar en historial
        self.message_history.append(event)
    
    def dispatch(self, max_iterations: int = 10) -> int:
        """
        Despacha mensajes de la cola a los agentes correspondientes.
        
        Args:
            max_iterations: Número máximo de iteraciones para evitar bucles infinitos
            
        Returns:
            Número de mensajes procesados
        """
        processed = 0
        iterations = 0
        
        while self.message_queue and iterations < max_iterations:
            # Procesar todos los mensajes actuales en la cola
            current_batch = list(self.message_queue)
            self.message_queue.clear()
            
            for event in current_batch:
                target_agent = self.agents.get(event.receiver)
                
                if target_agent:
                    # Entregar el mensaje al agente
                    self._deliver_to_agent(target_agent, event)
                    processed += 1
                else:
                    # Si no hay receptor, mantener el mensaje en la cola
                    self.message_queue.append(event)
            
            iterations += 1
        
        return processed
    
    def _deliver_to_agent(self, agent, event: MarketEvent):
        """
        Entrega un evento al agente correspondiente según su performative.
        """
        from agents import MarketAgent, InvestorAgent

        # Si es el MarketAgent, usar sus métodos específicos
        if isinstance(agent, MarketAgent):
            if event.performative == FipaPerformative.CFP:
                agent.process_cfp(event)
            elif event.performative == FipaPerformative.ACCEPT_PROPOSAL:
                agent.process_accept(event)
            else:
                # Para otros performatives, usar receive_event
                agent.comms.receive_event(event)
        
        # Si es un InvestorAgent, usar sus métodos específicos
        elif isinstance(agent, InvestorAgent):
            if event.performative == FipaPerformative.PROPOSE:
                agent.handle_propose(event)
            elif event.performative == FipaPerformative.INFORM:
                agent.handle_inform(event)
            else:
                # Para otros performatives, usar receive_event
                agent.comms.receive_event(event)
        
        # Para otros tipos de agentes, usar receive_event genérico
        else:
            agent.comms.receive_event(event)
    
    def clear_queue(self):
        """Limpia la cola de mensajes."""
        self.message_queue.clear()
    
    def get_queue_size(self) -> int:
        """Retorna el tamaño actual de la cola."""
        return len(self.message_queue)
    
    def has_pending_messages(self) -> bool:
        """Verifica si hay mensajes pendientes en la cola."""
        return len(self.message_queue) > 0


# Instancia global del dispatcher (singleton pattern)
_global_dispatcher: Optional[MessageDispatcher] = None


def get_dispatcher() -> MessageDispatcher:
    """Obtiene la instancia global del MessageDispatcher."""
    global _global_dispatcher
    if _global_dispatcher is None:
        _global_dispatcher = MessageDispatcher()
    return _global_dispatcher


def set_dispatcher(dispatcher: MessageDispatcher):
    """Establece una instancia personalizada del dispatcher."""
    global _global_dispatcher
    _global_dispatcher = dispatcher


def reset_dispatcher():
    """Resetea el dispatcher global (útil para testing)."""
    global _global_dispatcher
    _global_dispatcher = None

