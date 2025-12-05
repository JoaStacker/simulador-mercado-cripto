"""
    Define los tipos de mensajes y el estado del mercado.
"""

from enum import Enum

class FipaPerformative(Enum):
    CFP = "call_for_proposals"
    PROPOSE = "propose"
    ACCEPT_PROPOSAL = "accept_proposal"
    REJECT_PROPOSAL = "reject_proposal"
    INFORM = "inform"
    FAILURE = "failure"

class TransactionType(Enum):
    BUY = "buy"
    SELL = "sell"

class MarketEvent:
    """Clase para simular un mensaje/evento entre agentes."""
    def __init__(self, sender: str, receiver: str, performative: FipaPerformative, content: dict):
        self.sender = sender
        self.receiver = receiver
        self.performative = performative
        self.content = content

    def __str__(self):
        return f"[{self.sender} -> {self.receiver}] {self.performative.value}: {self.content}"