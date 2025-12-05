let priceChart = null;

document.getElementById('runSimulation').addEventListener('click', async () => {
    const cycles = parseInt(document.getElementById('cycles').value);
    const initialPrice = parseFloat(document.getElementById('initial_price').value);
    
    // Mostrar loading
    document.getElementById('loading').classList.remove('hidden');
    document.getElementById('results').classList.add('hidden');
    
    try {
        const response = await fetch('/api/simulate', {
            method: 'POST',
            headers: {
                'Content-Type': 'application/json',
            },
            body: JSON.stringify({
                cycles: cycles,
                initial_price: initialPrice
            })
        });
        
        const data = await response.json();
        
        // Ocultar loading y mostrar resultados
        document.getElementById('loading').classList.add('hidden');
        document.getElementById('results').classList.remove('hidden');
        
        // Actualizar estadísticas
        updateStatistics(data);
        
        // Actualizar gráfico
        updateChart(data.price_history);
        
        // Actualizar información de agentes
        updateAgentsInfo(data.agent_states);
        
        // Actualizar transacciones
        updateTransactions(data.transactions);
        
    } catch (error) {
        console.error('Error:', error);
        document.getElementById('loading').classList.add('hidden');
        alert('Error al ejecutar la simulación. Por favor, intente nuevamente.');
    }
});

function updateStatistics(data) {
    const stats = data.statistics;
    
    document.getElementById('stat-initial').textContent = `$${stats.initial_price.toFixed(2)}`;
    document.getElementById('stat-final').textContent = `$${stats.final_price.toFixed(2)}`;
    
    const changeElement = document.getElementById('stat-change');
    changeElement.textContent = `$${stats.price_change.toFixed(2)}`;
    changeElement.className = 'stat-value ' + (stats.price_change >= 0 ? 'positive' : 'negative');
    
    const changePercentElement = document.getElementById('stat-change-percent');
    changePercentElement.textContent = `${stats.price_change_percent.toFixed(2)}%`;
    changePercentElement.className = 'stat-value ' + (stats.price_change_percent >= 0 ? 'positive' : 'negative');
    
    document.getElementById('stat-max').textContent = `$${stats.max_price.toFixed(2)}`;
    document.getElementById('stat-min').textContent = `$${stats.min_price.toFixed(2)}`;
    document.getElementById('stat-transactions').textContent = stats.total_transactions;
    document.getElementById('stat-buys-sells').textContent = `${stats.buy_transactions} / ${stats.sell_transactions}`;
}

function updateChart(priceHistory) {
    const ctx = document.getElementById('priceChart').getContext('2d');
    
    // Destruir gráfico anterior si existe
    if (priceChart) {
        priceChart.destroy();
    }
    
    // Crear nuevo gráfico
    priceChart = new Chart(ctx, {
        type: 'line',
        data: {
            labels: priceHistory.map((_, index) => `Ciclo ${index}`),
            datasets: [{
                label: 'Precio de la Criptomoneda',
                data: priceHistory,
                borderColor: 'rgb(102, 126, 234)',
                backgroundColor: 'rgba(102, 126, 234, 0.1)',
                borderWidth: 3,
                fill: true,
                tension: 0.4,
                pointRadius: 4,
                pointHoverRadius: 6,
                pointBackgroundColor: 'rgb(102, 126, 234)',
                pointBorderColor: '#fff',
                pointBorderWidth: 2
            }]
        },
        options: {
            responsive: true,
            maintainAspectRatio: true,
            plugins: {
                legend: {
                    display: true,
                    position: 'top',
                },
                tooltip: {
                    mode: 'index',
                    intersect: false,
                    callbacks: {
                        label: function(context) {
                            return `Precio: $${context.parsed.y.toFixed(2)}`;
                        }
                    }
                }
            },
            scales: {
                y: {
                    beginAtZero: false,
                    title: {
                        display: true,
                        text: 'Precio ($)'
                    },
                    ticks: {
                        callback: function(value) {
                            return '$' + value.toFixed(2);
                        }
                    }
                },
                x: {
                    title: {
                        display: true,
                        text: 'Ciclo de Simulación'
                    }
                }
            },
            interaction: {
                mode: 'nearest',
                axis: 'x',
                intersect: false
            }
        }
    });
}

function updateAgentsInfo(agentStates) {
    const agentsContainer = document.getElementById('agents-info');
    agentsContainer.innerHTML = '';
    
    if (agentStates.length === 0) return;
    
    // Obtener el último estado
    const lastState = agentStates[agentStates.length - 1];
    
    // Crear tarjetas para cada inversor
    Object.entries(lastState.investors).forEach(([agentId, info]) => {
        const agentCard = document.createElement('div');
        agentCard.className = 'agent-card';
        
        const personality = info.risk_tolerance > 0.4 ? 'Impulsivo' : 
                           info.risk_tolerance > 0.2 ? 'Medio' : 'Racional';
        
        agentCard.innerHTML = `
            <h4>${agentId}</h4>
            <div class="agent-info">
                <span><strong>Personalidad:</strong></span>
                <span>${personality}</span>
            </div>
            <div class="agent-info">
                <span><strong>Tolerancia al Riesgo:</strong></span>
                <span>${(info.risk_tolerance * 100).toFixed(0)}%</span>
            </div>
            <div class="agent-info">
                <span><strong>Saldo Fiat:</strong></span>
                <span>$${info.fiat_balance.toFixed(2)}</span>
            </div>
            <div class="agent-info">
                <span><strong>Saldo Cripto:</strong></span>
                <span>${info.crypto_balance.toFixed(2)}</span>
            </div>
        `;
        
        agentsContainer.appendChild(agentCard);
    });
}

function updateTransactions(transactions) {
    const transactionsContainer = document.getElementById('transactions-list');
    transactionsContainer.innerHTML = '';
    
    if (transactions.length === 0) {
        transactionsContainer.innerHTML = '<p style="text-align: center; color: #666; padding: 20px;">No se realizaron transacciones en esta simulación.</p>';
        return;
    }
    
    transactions.forEach(transaction => {
        const transactionItem = document.createElement('div');
        transactionItem.className = `transaction-item ${transaction.action}`;
        
        const actionText = transaction.action === 'buy' ? 'COMPRA' : 'VENTA';
        const actionEmoji = transaction.action === 'buy' ? '📈' : '📉';
        
        transactionItem.innerHTML = `
            <div class="transaction-info">
                <strong>${actionEmoji} ${actionText}</strong> por <strong>${transaction.receiver}</strong>
                <br>
                <small>Ciclo ${transaction.cycle}</small>
            </div>
            <div class="transaction-price">
                $${transaction.price.toFixed(2)}
            </div>
        `;
        
        transactionsContainer.appendChild(transactionItem);
    });
}

