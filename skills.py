# skills.py
"""
    Define la lógica de decisión específica de los agentes Inversores (habilidades).
"""

from events import TransactionType
from typing import Any

class InvestmentSkill:
    """Habilidad para tomar decisiones de inversión basadas en personalidad y precio."""
    
    def __init__(self, risk_tolerance: float):
        # 0.1 para el racional, 0.5 o mas para el impulsivo
        self.risk_tolerance = risk_tolerance 
        self.MIN_PROFIT_BUY = 0.01 # represneta la "Señal Compra" en el diagrama de Ontologías
        self.MAX_LOSS_SELL = 0.05 # represneta la "Señal Venta" en el diagrama de Ontologías
    
    def decide_transaction(self, price_change: float) -> Any:
        """
        Aca puede decidir entre: COMPRAR, VENDER o NO HACER NADA. 
        Retorna la acción y la cantidad. Es una version simplificada: 1.0 unidad de cripto).
        Al final no tomé los saldos como variable que influye en la decision. Decidí simplificarlo.
        """
        action = None
        amount = 1.0

        # Umbral dinámico basado en la tolerancia al riesgo (más sensible = reacciona más rápido)
        buy_threshold = 0.02 * (1.0 - self.risk_tolerance) # Racional compra si sube lentamente
        panic_threshold = 0.05 * self.risk_tolerance # Impulsivo entra en pánico más rápido

        if price_change > buy_threshold + self.MIN_PROFIT_BUY:
            # Reacción positiva al aumento: Racional compra si la subida es moderada.
            # Impulsivo compra si la subida es explosiva (FOMO).
            if price_change > 0.05 and self.risk_tolerance > 0.3:
                 action = TransactionType.BUY # Impulsivo (FOMO)
            elif price_change > buy_threshold:
                 action = TransactionType.BUY # Racional (Compra con subida controlada)
        
        elif price_change < -panic_threshold:
            # Reacción negativa a la caída: VENTA (Pánico)
            if price_change < -0.05 or self.risk_tolerance > 0.3:
                action = TransactionType.SELL # Ambos pueden vender, Impulsivo más rápido

        # Aqui deberia agregar en un futuro la logica que considere el saldo fiat y saldo cripto del diagrama de ontologia.
        print(action, amount)
        return action, amount