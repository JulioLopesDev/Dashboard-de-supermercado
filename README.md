# Dashboard de Rede de Supermercado

Dashboard interativo para análise de vendas, estoque e performance em uma rede de supermercados. Construído com **Python**, **SQLAlchemy**, **Dash** e **Plotly**.

## Funcionalidades

- **KPIs em Tempo Real**: Receita total, itens vendidos, número de pedidos e margem bruta
- **Gráficos Interativos**:
  - Vendas por dia com tendência
  - Top 10 produtos por receita
  - Participação por categoria
  - Comparativo de receita por loja
  - Vendas por hora do dia
  - Alerta de estoque crítico (< 50 unidades)
- **Filtros Dinâmicos**: Por loja, categoria e período (7-60 dias)
- **Banco de Dados**: SQLite com 60 dias de vendas simuladas

## Estrutura do Projeto

```
supermercado-dashboard/
├── models.py              # Modelos SQLAlchemy
├── seed.py                # Script para gerar dados
├── app_dashboard.py       # Dashboard Dash/Plotly
├── requirements.txt       # Dependências Python
├── supermarket.db         # Banco SQLite (gerado)
└── README.md              # Este arquivo
```

## Instalação

### 1. Criar Ambiente Virtual
```powershell
python -m venv .venv
.venv\Scripts\Activate.ps1
```

### 2. Instalar Dependências
```powershell
pip install -r requirements.txt
```

### 3. Gerar Dados de Teste
```powershell
python seed.py
```

Isso criará `supermarket.db` com:
- 3 lojas (Centro, Norte, Sul)
- 60 produtos (5 categorias)
- ~1500 pedidos (60 dias)

### 4. Executar Dashboard
```powershell
python app_dashboard.py
```

Abra no navegador: **http://127.0.0.1:8050**

## Métricas e Visualizações

### KPIs
- **Receita Total**: Soma de todas as vendas
- **Itens Vendidos**: Quantidade total de itens
- **Pedidos**: Número de transações
- **Margem Bruta**: Lucro (com percentual)

### Gráficos
1. **Vendas por Dia**: Linha com tendência suavizada
2. **Top 10 Produtos**: Gráfico de barras horizontal
3. **Participação por Categoria**: Gráfico de pizza
4. **Receita por Loja**: Comparativo com loja
5. **Vendas por Hora**: Área preenchida com horários de pico
6. **Estoque Crítico**: Alerta visual para produtos com baixo estoque

## Como Usar

1. **Filtrar por Loja**: Selecione uma loja específica ou "Todas"
2. **Filtrar por Categoria**: Escolha uma categoria ou "Todas"
3. **Ajustar Período**: Use o slider para mudar o intervalo (7-60 dias)
4. **Interagir com Gráficos**: 
   - Hover para ver valores exatos
   - Clique na legenda para ocultar/mostrar série
   - Use as ferramentas de zoom no canto superior direito

## Dados do Banco

### Lojas (3)
- Loja Centro, Araraquara
- Loja Norte, Araraquara
- Loja Sul, São Carlos

### Categorias (5)
- Mercearia
- Hortifruti
- Limpeza
- Bebidas
- Padaria

### Produtos (60)
Cada produto tem: SKU, nome, categoria, preço de venda, custo, estoque

### Vendas (60 dias)
~8-40 pedidos por dia, com 1-6 itens por pedido

## Tecnologias

| Componente | Versão |
|-----------|--------|
| Python | 3.8+ |
| SQLAlchemy | 2.0+ |
| Dash | 2.14+ |
| Plotly | 5.17+ |
| Pandas | 2.1+ |
| SQLite | Built-in |
