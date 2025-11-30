import pandas as pd
from sqlalchemy import create_engine, text
from dateutil.relativedelta import relativedelta
from datetime import datetime
from dash import Dash, dcc, html, Input, Output, State
import plotly.express as px
import plotly.graph_objects as go

DATABASE_URL = "sqlite:///supermarket.db"
engine = create_engine(DATABASE_URL, echo=False, future=True)


def load_data():
    with engine.connect() as conn:
        orders = pd.read_sql(text("""
            SELECT o.id, o.store_id, o.created_at, s.name as store_name, s.city
            FROM orders o
            JOIN stores s ON s.id = o.store_id
        """), conn)
        items = pd.read_sql(text("""
            SELECT oi.order_id, oi.product_id, oi.quantity, oi.unit_price,
                   p.name as product_name, p.category, p.cost
            FROM order_items oi
            JOIN products p ON p.id = oi.product_id
        """), conn)
        products = pd.read_sql(text("SELECT * FROM products"), conn)
        stores = pd.read_sql(text("SELECT * FROM stores"), conn)
    return orders, items, products, stores


orders, items, products, stores = load_data()
orders["created_at"] = pd.to_datetime(orders["created_at"])
items["revenue"] = items["quantity"] * items["unit_price"]
items["cost_total"] = items["quantity"] * items["cost"].fillna(0)
items["margin"] = items["revenue"] - items["cost_total"]

# Agregações básicas
orders_items = items.merge(orders[["id", "store_id", "store_name", "city", "created_at"]],
                           left_on="order_id", right_on="id", suffixes=("", "_order"))
orders_items["date"] = orders_items["created_at"].dt.date
orders_items["hour"] = orders_items["created_at"].dt.hour

# Inicializar app Dash
app = Dash(__name__)
app.title = "Dashboard - Rede Supermercado"

# Opções de filtro
store_options = [{"label": "Todas", "value": "ALL"}] + [
    {"label": f"{row.store_name} ({row.city})", "value": int(row.store_id)}
    for _, row in orders_items[["store_id", "store_name", "city"]].drop_duplicates().iterrows()
]

category_options = [{"label": "Todas", "value": "ALL"}] + [
    {"label": cat, "value": cat} for cat in sorted(products["category"].dropna().unique())
]

# Layout
app.layout = html.Div([
    html.Div([
        html.H1("📊 Dashboard da Rede de Supermercados", style={"marginBottom": "0", "color": "#2c3e50"}),
        html.P("Análise de vendas, estoque e performance por loja", style={"color": "#7f8c8d", "marginTop": "4px"})
    ], style={"padding": "20px", "backgroundColor": "#f8f9fa", "borderBottom": "2px solid #ecf0f1"}),
    
    # Filtros
    html.Div([
        html.Div([
            html.Label("🏪 Loja", style={"fontWeight": "bold", "marginBottom": "8px"}),
            dcc.Dropdown(
                id="filter-store",
                options=store_options,
                value="ALL",
                clearable=False,
                style={"width": "100%"}
            )
        ], style={"flex": "1", "marginRight": "12px"}),
        
        html.Div([
            html.Label("🏷️ Categoria", style={"fontWeight": "bold", "marginBottom": "8px"}),
            dcc.Dropdown(
                id="filter-category",
                options=category_options,
                value="ALL",
                clearable=False,
                style={"width": "100%"}
            )
        ], style={"flex": "1", "marginRight": "12px"}),
        
        html.Div([
            html.Label("📅 Período (dias)", style={"fontWeight": "bold", "marginBottom": "8px"}),
            dcc.Slider(
                id="filter-days",
                min=7,
                max=60,
                step=1,
                value=30,
                marks={7: "7", 14: "14", 30: "30", 45: "45", 60: "60"},
                tooltip={"placement": "bottom", "always_visible": True}
            )
        ], style={"flex": "1.2"})
    ], style={
        "display": "flex",
        "marginBottom": "20px",
        "padding": "16px",
        "backgroundColor": "#fff",
        "borderRadius": "8px",
        "boxShadow": "0 1px 3px rgba(0,0,0,0.1)"
    }),

    # KPIs
    html.Div(id="kpis", style={
        "display": "flex",
        "gap": "16px",
        "marginBottom": "16px",
        "flexWrap": "wrap"
    }),

    # Gráficos linha 1
    html.Div([
        dcc.Graph(id="graph-sales-time"),
        dcc.Graph(id="graph-top-products")
    ], style={"display": "flex", "gap": "16px", "marginBottom": "16px"}),

    # Gráficos linha 2
    html.Div([
        dcc.Graph(id="graph-category-share"),
        dcc.Graph(id="graph-store-comparison")
    ], style={"display": "flex", "gap": "16px", "marginBottom": "16px"}),

    # Gráficos linha 3
    html.Div([
        dcc.Graph(id="graph-heatmap"),
        dcc.Graph(id="graph-stock")
    ], style={"display": "flex", "gap": "16px"})
], style={"padding": "12px", "backgroundColor": "#ecf0f1", "minHeight": "100vh"})


def apply_filters(data, store_id, category, days):
    """Aplica filtros ao dataframe"""
    df = data.copy()
    
    # Filtro por período
    end = df["created_at"].max()
    start = end - relativedelta(days=days)
    df = df[(df["created_at"] >= start) & (df["created_at"] <= end)]
    
    # Filtro por loja
    if store_id != "ALL":
        df = df[df["store_id"] == store_id]
    
    # Filtro por categoria
    if category != "ALL":
        df = df[df["category"] == category]
    
    return df


@app.callback(
    [Output("kpis", "children"),
     Output("graph-sales-time", "figure"),
     Output("graph-top-products", "figure"),
     Output("graph-category-share", "figure"),
     Output("graph-store-comparison", "figure"),
     Output("graph-heatmap", "figure"),
     Output("graph-stock", "figure")],
    [Input("filter-store", "value"),
     Input("filter-category", "value"),
     Input("filter-days", "value")]
)
def update_dashboard(store_sel, cat_sel, days):
    df = apply_filters(orders_items, store_sel, cat_sel, days)
    
    if df.empty:
        return ([], go.Figure(), go.Figure(), go.Figure(), go.Figure(), go.Figure(), go.Figure())
    
    # ===== KPIs =====
    revenue = df["revenue"].sum()
    items_sold = df["quantity"].sum()
    orders_count = df["order_id"].nunique()
    margin = df["margin"].sum()
    margin_pct = (margin / revenue * 100) if revenue > 0 else 0
    
    kpi_style = {
        "padding": "16px",
        "border": "1px solid #bdc3c7",
        "borderRadius": "8px",
        "flex": "1",
        "minWidth": "200px",
        "backgroundColor": "#fff",
        "boxShadow": "0 1px 3px rgba(0,0,0,0.1)"
    }
    
    kpis = [
        html.Div([
            html.P("💰 Receita Total", style={"margin": "0", "fontSize": "12px", "color": "#7f8c8d", "fontWeight": "bold"}),
            html.H3(f"R$ {revenue:,.2f}", style={"margin": "8px 0 0 0", "color": "#27ae60"})
        ], style=kpi_style),
        
        html.Div([
            html.P("📦 Itens Vendidos", style={"margin": "0", "fontSize": "12px", "color": "#7f8c8d", "fontWeight": "bold"}),
            html.H3(f"{items_sold:,}", style={"margin": "8px 0 0 0", "color": "#3498db"})
        ], style=kpi_style),
        
        html.Div([
            html.P("🛒 Pedidos", style={"margin": "0", "fontSize": "12px", "color": "#7f8c8d", "fontWeight": "bold"}),
            html.H3(f"{orders_count:,}", style={"margin": "8px 0 0 0", "color": "#e74c3c"})
        ], style=kpi_style),
        
        html.Div([
            html.P("📈 Margem Bruta", style={"margin": "0", "fontSize": "12px", "color": "#7f8c8d", "fontWeight": "bold"}),
            html.H3(f"R$ {margin:,.2f} ({margin_pct:.1f}%)", style={"margin": "8px 0 0 0", "color": "#f39c12"})
        ], style=kpi_style),
    ]
    
    # ===== Vendas por dia =====
    sales_by_day = df.groupby("date", as_index=False)["revenue"].sum().sort_values("date")
    fig_time = px.line(
        sales_by_day,
        x="date",
        y="revenue",
        title="📈 Vendas por Dia",
        markers=True,
        line_shape="spline"
    )
    fig_time.update_layout(
        yaxis_title="Receita (R$)",
        xaxis_title="Data",
        hovermode="x unified",
        plot_bgcolor="#f8f9fa",
        paper_bgcolor="#fff"
    )
    fig_time.update_traces(line=dict(color="#3498db", width=3), marker=dict(size=6))
    
    # ===== Top produtos =====
    top_prod = df.groupby("product_name", as_index=False).agg(
        {"revenue": "sum", "quantity": "sum"}
    ).sort_values("revenue", ascending=False).head(10)
    fig_top = px.bar(
        top_prod,
        x="revenue",
        y="product_name",
        orientation="h",
        title="🏆 Top 10 Produtos por Receita",
        labels={"product_name": "", "revenue": "Receita (R$)"}
    )
    fig_top.update_layout(
        plot_bgcolor="#f8f9fa",
        paper_bgcolor="#fff",
        yaxis_tickfont=dict(size=11)
    )
    fig_top.update_traces(marker=dict(color="#27ae60"))
    
    # ===== Participação por categoria =====
    cat_share = df.groupby("category", as_index=False)["revenue"].sum().sort_values("revenue", ascending=False)
    fig_cat = px.pie(
        cat_share,
        names="category",
        values="revenue",
        title="🏷️ Participação por Categoria",
        hole=0.4
    )
    fig_cat.update_layout(paper_bgcolor="#fff")
    
    # ===== Comparativo por loja =====
    store_rev = df.groupby("store_name", as_index=False).agg(
        {"revenue": "sum", "quantity": "sum", "order_id": "nunique"}
    ).sort_values("revenue", ascending=False)
    fig_store = px.bar(
        store_rev,
        x="store_name",
        y="revenue",
        title="🏪 Receita por Loja",
        labels={"store_name": "Loja", "revenue": "Receita (R$)"},
        text="revenue"
    )
    fig_store.update_layout(
        plot_bgcolor="#f8f9fa",
        paper_bgcolor="#fff",
        showlegend=False
    )
    fig_store.update_traces(marker=dict(color="#e74c3c"), textposition="outside")
    
    # ===== Heatmap: Vendas por Hora =====
    hourly = df.groupby("hour", as_index=False)["revenue"].sum().sort_values("hour")
    fig_heat = go.Figure(data=go.Scatter(
        x=hourly["hour"],
        y=hourly["revenue"],
        fill="tozeroy",
        name="Receita",
        line=dict(color="#9b59b6", width=3)
    ))
    fig_heat.update_layout(
        title="⏰ Vendas por Hora do Dia",
        xaxis_title="Hora",
        yaxis_title="Receita (R$)",
        plot_bgcolor="#f8f9fa",
        paper_bgcolor="#fff",
        hovermode="x"
    )
    
    # ===== Estoque Crítico =====
    stock_crit = products[products["stock"] < 50].sort_values("stock").head(10)
    if len(stock_crit) > 0:
        fig_stock = px.bar(
            stock_crit,
            x="stock",
            y="name",
            orientation="h",
            title="⚠️ Produtos com Estoque Crítico (< 50 unid.)",
            labels={"name": "", "stock": "Estoque (unidades)"},
            color="stock",
            color_continuous_scale="Reds"
        )
    else:
        fig_stock = go.Figure()
        fig_stock.add_annotation(
            text="✓ Sem estoque crítico",
            showarrow=False,
            xref="paper",
            yref="paper",
            x=0.5,
            y=0.5,
            font=dict(size=16, color="#27ae60")
        )
        fig_stock.update_layout(title="⚠️ Produtos com Estoque Crítico (< 50 unid.)")
    
    fig_stock.update_layout(
        plot_bgcolor="#f8f9fa",
        paper_bgcolor="#fff",
        yaxis_tickfont=dict(size=10)
    )
    
    return kpis, fig_time, fig_top, fig_cat, fig_store, fig_heat, fig_stock


if __name__ == "__main__":
    print("🚀 Iniciando dashboard em http://127.0.0.1:8050")
    app.run_server(debug=True)
