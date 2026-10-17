from fastapi import FastAPI, Request, Form, Depends, HTTPException
from fastapi.responses import HTMLResponse, RedirectResponse
from fastapi.staticfiles import StaticFiles
from fastapi.templating import Jinja2Templates
from sqlalchemy import create_engine, Column, Integer, String, Float, ForeignKey
from sqlalchemy.orm import declarative_base, sessionmaker, relationship, Session
import os

DATABASE_URL = "sqlite:///./portal_corrida.db"

engine = create_engine(DATABASE_URL, connect_args={"check_same_thread": False})
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)
Base = declarative_base()

# Models
class Store(Base):
    __tablename__ = "stores"
    id = Column(Integer, primary_key=True, index=True)
    name = Column(String, index=True)
    category = Column(String)
    address = Column(String)
    products = relationship("Product", back_populates="store")

class Product(Base):
    __tablename__ = "products"
    id = Column(Integer, primary_key=True, index=True)
    name = Column(String, index=True)
    price = Column(Float)
    store_id = Column(Integer, ForeignKey("stores.id"))
    store = relationship("Store", back_populates="products")

class Event(Base):
    __tablename__ = "events"
    id = Column(Integer, primary_key=True, index=True)
    name = Column(String, index=True)
    date = Column(String)
    location = Column(String)
    price = Column(Float)

Base.metadata.create_all(bind=engine)

app = FastAPI(title="Portal Regional de Corridas", version="1.0")

# Seed initial data if empty
def seed_data():
    db = SessionLocal()
    if db.query(Store).count() == 0:
        store1 = Store(name="Corredor Pro Shop", category="Tênis e Acessórios", address="Rua Principal, 100")
        store2 = Store(name="Esporte Total", category="Nutrição e Vestuário", address="Av. Central, 500")
        db.add_all([store1, store2])
        db.commit()
        
        p1 = Product(name="Tênis Carbon Performance", price=899.90, store_id=store1.id)
        p2 = Product(name="Gel de Carboidrato (Cx c/ 10)", price=79.90, store_id=store2.id)
        db.add_all([p1, p2])
        
        e1 = Event(name="Meia Maratona Regional 2026", date="15/11/2026", location="Praça Central", price=95.00)
        db.add(e1)
        db.commit()
    db.close()

seed_data()

def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()

# HTML Template directory
os.makedirs("/opt/data/ecosystem/portal/templates", exist_ok=True)
templates = Jinja2Templates(directory="/opt/data/ecosystem/portal/templates")

INDEX_HTML = """
<!DOCTYPE html>
<html lang="pt-BR" class="dark">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>Portal Regional de Corridas</title>
    <script src="https://cdn.tailwindcss.com"></script>
    <script>
        tailwind.config = {
            darkMode: 'class',
            theme: {
                extend: {
                    colors: {
                        brand: { 500: '#10b981', 600: '#059669' }
                    }
                }
            }
        }
    </script>
</head>
<body class="bg-zinc-950 text-zinc-100 font-sans min-h-screen">
    <header class="border-b border-zinc-800 bg-zinc-950/80 backdrop-blur sticky top-0 z-50">
        <div class="max-w-7xl mx-auto px-6 h-16 flex items-center justify-between">
            <div class="flex items-center space-x-3">
                <div class="w-8 h-8 rounded-lg bg-emerald-500 flex items-center justify-center font-bold text-zinc-950">🏃</div>
                <span class="font-bold text-lg tracking-tight">RunLocal Hub</span>
            </div>
            <nav class="hidden md:flex space-x-6 text-sm text-zinc-400">
                <a href="#lojas" class="hover:text-white transition">Lojas Parceiras</a>
                <a href="#produtos" class="hover:text-white transition">Equipamentos</a>
                <a href="#eventos" class="hover:text-white transition">Provas & Eventos</a>
            </nav>
            <div>
                <a href="#eventos" class="bg-emerald-500 hover:bg-emerald-600 text-zinc-950 font-semibold px-4 py-2 rounded-lg text-sm transition">Inscrever-se em Prova</a>
            </div>
        </div>
    </header>

    <main class="max-w-7xl mx-auto px-6 py-12 space-y-16">
        <!-- Hero Section -->
        <section class="text-center space-y-6 max-w-3xl mx-auto">
            <div class="inline-flex items-center space-x-2 bg-zinc-900 border border-zinc-800 rounded-full px-4 py-1.5 text-xs text-emerald-400 font-medium">
                <span>⚡ O Ecossistema Regional de Corrida</span>
            </div>
            <h1 class="text-4xl md:text-6xl font-extrabold tracking-tight">
                Conectando Corredores, Lojas e Provas da Região.
            </h1>
            <p class="text-zinc-400 text-lg">
                Encontre o melhor equipamento nas lojas locais, acompanhe métricas e garanta sua vaga nas próximas corridas.
            </p>
        </section>

        <!-- Lojas & Produtos -->
        <section id="produtos" class="space-y-6">
            <div class="flex justify-between items-center">
                <h2 class="text-2xl font-bold tracking-tight">Equipamentos em Destaque</h2>
                <span class="text-sm text-zinc-400">Estoque em tempo real nas lojas parceiras</span>
            </div>
            <div class="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-6">
                {% for p in products %}
                <div class="bg-zinc-900 border border-zinc-800 rounded-xl p-6 space-y-4 hover:border-zinc-700 transition">
                    <div class="flex justify-between items-start">
                        <span class="text-xs bg-emerald-500/10 text-emerald-400 px-2.5 py-1 rounded-full font-medium">{{ p.store.name }}</span>
                        <span class="text-emerald-400 font-bold text-lg">R$ {{ "%.2f"|format(p.price) }}</span>
                    </div>
                    <h3 class="text-xl font-semibold">{{ p.name }}</h3>
                    <p class="text-xs text-zinc-400">📍 {{ p.store.address }}</p>
                    <button class="w-full bg-zinc-800 hover:bg-zinc-700 text-white font-medium py-2 rounded-lg text-sm transition">Reservar na Loja</button>
                </div>
                {% endfor %}
            </div>
        </section>

        <!-- Eventos -->
        <section id="eventos" class="space-y-6">
            <div class="flex justify-between items-center">
                <h2 class="text-2xl font-bold tracking-tight">Próximas Provas</h2>
                <span class="text-sm text-zinc-400">Inscrições abertas</span>
            </div>
            <div class="grid grid-cols-1 md:grid-cols-2 gap-6">
                {% for e in events %}
                <div class="bg-zinc-900 border border-zinc-800 rounded-xl p-6 space-y-4 flex flex-col justify-between">
                    <div class="space-y-2">
                        <div class="flex justify-between items-center">
                            <span class="text-xs bg-blue-500/10 text-blue-400 px-2.5 py-1 rounded-full font-medium">📅 {{ e.date }}</span>
                            <span class="font-bold text-lg text-emerald-400">R$ {{ "%.2f"|format(e.price) }}</span>
                        </div>
                        <h3 class="text-2xl font-bold">{{ e.name }}</h3>
                        <p class="text-sm text-zinc-400">📍 Local: {{ e.location }}</p>
                    </div>
                    <button onclick="alert('Inscrição simulada com sucesso! Redirecionando para pagamento.')" class="w-full bg-emerald-500 hover:bg-emerald-600 text-zinc-950 font-bold py-2.5 rounded-lg text-sm transition">Garantir Inscrição</button>
                </div>
                {% endfor %}
            </div>
        </section>
    </main>

    <footer class="border-t border-zinc-800 mt-20 py-8 text-center text-xs text-zinc-500">
        RunLocal Hub &copy; 2026 — Operado pelo Ecossistema Autônomo de Jefi.
    </footer>
</body>
</html>
"""

with open("/opt/data/ecosystem/portal/templates/index.html", "w", encoding="utf-8") as f:
    f.write(INDEX_HTML)

@app.get("/", response_class=HTMLResponse)
async def home(request: Request, db: Session = Depends(get_db)):
    products = db.query(Product).all()
    events = db.query(Event).all()
    return templates.TemplateResponse("index.html", {"request": request, "products": products, "events": events})

@app.get("/health")
def health():
    return {"status": "ok", "app": "RunLocal Hub MVP"}
