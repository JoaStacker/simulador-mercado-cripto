from events import MarketEvent
from message_dispatcher import get_dispatcher

class CommunicativeCapacity:
    """Capacidad para enviar y recibir eventos/mensajes."""

    def __init__(self):
        """Inicializa la capacidad comunicativa con referencia al dispatcher."""
        self._dispatcher = None  # Se puede inyectar un dispatcher personalizado

    def _get_dispatcher(self):
        """Obtiene el dispatcher a usar (inyectado o global)."""
        if self._dispatcher is None:
            return get_dispatcher()
        return self._dispatcher

    def set_dispatcher(self, dispatcher):
        """Permite inyectar un dispatcher personalizado."""
        self._dispatcher = dispatcher

    def send_event(self, event: MarketEvent):
        """
        Envía un evento al MessageDispatcher para su procesamiento.

        Args:
            event: El MarketEvent a enviar
        """
        if not isinstance(event, MarketEvent):
            raise ValueError("El evento debe ser una instancia de MarketEvent")

        # Obtener el dispatcher y enviar el evento
        dispatcher = self._get_dispatcher()
        dispatcher.send_event(event)

        # Opcional: mantener el print para debugging (se puede comentar)
        print(f"ENVIADO: {event}")

    def receive_event(self, event):
        """El agente procesa un evento entrante."""
        print(f"RECIBIDO por {self.id}: {event}")
        # Lógica de manejo de performative FIPA
        if event.performative == event.performative.PROPOSE:
            self.handle_propose(event)
        elif event.performative == event.performative.INFORM:
            self.handle_inform(event)

    def handle_propose(self, event):
        """Debe ser implementado por subclases."""
        raise NotImplementedError

    def handle_inform(self, event):
        """Debe ser implementado por subclases."""
        raise NotImplementedError

class EvaluationCapacity:
    """Capacidad para evaluar datos del mercado."""
    def evaluate_price_change(self, current_price, history):
        """Calcula la variación porcentual del precio."""
        if len(history) < 2:
            return 0.0
        prev_price = history[-2]
        return (current_price - prev_price) / prev_price