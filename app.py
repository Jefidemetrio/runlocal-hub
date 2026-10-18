import http.server
import socketserver
import sqlite3
import urllib.parse
import os

PORT = 8000
DB_PATH = "portal_corrida.db"

def init_db():
    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()
    cursor.execute("""
        CREATE TABLE IF NOT EXISTS stores (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            name TEXT,
            category TEXT,
            address TEXT
        )
    """)
    cursor.execute("""
        CREATE TABLE IF NOT EXISTS products (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            name TEXT,
            price REAL,
            store_id INTEGER,
            FOREIGN KEY(store_id) REFERENCES stores(id)
        )
    """)
    cursor.execute("""
        CREATE TABLE IF NOT EXISTS events (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            name TEXT,
            date TEXT,
            location TEXT,
            price REAL
        )
    """)
    # Seed data if empty
    cursor.execute("SELECT COUNT(*) FROM stores")
    if cursor.fetchone()[0] == 0:
        cursor.execute("INSERT INTO stores (name, category, address) VALUES ('Corredor Pro Shop', 'Tênis e Acessórios', 'Rua Principal, 100')")
        cursor.execute("INSERT INTO stores (name, category, address) VALUES ('Esporte Total', 'Nutrição e Vestuário', 'Av. Central, 500')")
        cursor.execute("INSERT INTO products (name, price, store_id) VALUES ('Tênis Carbon Performance', 899.90, 1)")
        cursor.execute("INSERT INTO products (name, price, store_id) VALUES ('Gel de Carboidrato (Cx c/ 10)', 79.90, 2)")
        cursor.execute("INSERT INTO events (name, date, location, price) VALUES ('Meia Maratona Regional 2026', '15/11/2026', 'Praça Central', 95.00)")
        conn.commit()
    conn.close()

init_db()

class PortalHandler(http.server.SimpleHTTPRequestHandler):
    def do_GET(self):
        if self.path == "/" or self.path == "/index.html":
            self.send_response(200)
            self.send_header("Content-type", "text/html; charset=utf-8")
            self.end_headers()
            
            conn = sqlite3.connect(DB_PATH)
            cursor = conn.cursor()
            cursor.execute("SELECT p.name, p.price, s.name, s.address FROM products p JOIN stores s ON p.store_id = s.id")
            products = cursor.fetchall()
            
            cursor.execute("SELECT name, date, location, price FROM events")
            events = cursor.fetchall()
            conn.close()
            
            products_html = ""
            for p in products:
                products_html += f"""
                <div class="bg-zinc-900 border border-zinc-800 rounded-xl p-6 space-y-4 hover:border-zinc-700 transition">
                    <div class="flex justify-between items-start">
                        <span class="text-xs bg-emerald-500/10 text-emerald-400 px-2.5 py-1 rounded-full font-medium">{p[2]}</span>
                        <span class="text-emerald-400 font-bold text-lg">R$ {p[1]:.2f}</span>
                    </div>
                    <h3 class="text-xl font-semibold">{p[0]}</h3>
                    <p class="text-xs text-zinc-400">📍 {p[3]}</p>
                    <button onclick="alert('Reserva solicitada com sucesso!')" class="w-full bg-zinc-800 hover:bg-zinc-700 text-white font-medium py-2 rounded-lg text-sm transition">Reservar na Loja</button>
                </div>
                """
                
            events_html = ""
            for e in events:
                events_html += f"""
                <div class="bg-zinc-900 border border-zinc-800 rounded-xl p-6 space-y-4 flex flex-col justify-between">
                    <div class="space-y-2">
                        <div class="flex justify-between items-center">
                            <span class="text-xs bg-blue-500/10 text-blue-400 px-2.5 py-1 rounded-full font-medium">📅 {e[1]}</span>
                            <span class="font-bold text-lg text-emerald-400">R$ {e[3]:.2f}</span>
                        </div>
                        <h3 class="text-2xl font-bold">{e[0]}</h3>
                        <p class="text-sm text-zinc-400">📍 Local: {e[2]}</p>
                    </div>
                    <button onclick="alert('Inscrição simulada com sucesso! Redirecionando para pagamento.')" class="w-full bg-emerald-500 hover:bg-emerald-600 text-zinc-950 font-bold py-2.5 rounded-lg text-sm transition">Garantir Inscrição</button>
                </div>
                """

            html = f"""<!DOCTYPE html>
<html lang="pt-BR" class="dark">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>Portal Regional de Corridas — RunLocal Hub</title>
    <script src="https://cdn.tailwindcss.com"></script>
</head>
<body class="bg-zinc-950 text-zinc-100 font-sans min-h-screen">
    <header class="border-b border-zinc-800 bg-zinc-950/80 backdrop-blur sticky top-0 z-50">
        <div class="max-w-7xl mx-auto px-6 h-16 flex items-center justify-between">
            <div class="flex items-center space-x-3">
                <div class="w-8 h-8 rounded-lg bg-emerald-500 flex items-center justify-center font-bold text-zinc-950">🏃</div>
                <span class="font-bold text-lg tracking-tight">RunLocal Hub</span>
            </div>
            <nav class="hidden md:flex space-x-6 text-sm text-zinc-400">
                <a href="#produtos" class="hover:text-white transition">Equipamentos</a>
                <a href="#eventos" class="hover:text-white transition">Provas & Eventos</a>
            </nav>
            <div>
                <a href="#eventos" class="bg-emerald-500 hover:bg-emerald-600 text-zinc-950 font-semibold px-4 py-2 rounded-lg text-sm transition">Inscrever-se</a>
            </div>
        </div>
    </header>

    <main class="max-w-7xl mx-auto px-6 py-12 space-y-16">
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

        <section id="produtos" class="space-y-6">
            <div class="flex justify-between items-center">
                <h2 class="text-2xl font-bold tracking-tight">Equipamentos em Destaque</h2>
                <span class="text-sm text-zinc-400">Estoque em tempo real nas lojas parceiras</span>
            </div>
            <div class="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-6">
                {products_html}
            </div>
        </section>

        <section id="eventos" class="space-y-6">
            <div class="flex justify-between items-center">
                <h2 class="text-2xl font-bold tracking-tight">Próximas Provas</h2>
                <span class="text-sm text-zinc-400">Inscrições abertas</span>
            </div>
            <div class="grid grid-cols-1 md:grid-cols-2 gap-6">
                {events_html}
            </div>
        </section>
    </main>

    <footer class="border-t border-zinc-800 mt-20 py-8 text-center text-xs text-zinc-500">
        RunLocal Hub &copy; 2026 — Operado pelo Ecossistema Autônomo de Jefi.
    </footer>
</body>
</html>"""
            self.wfile.write(html.encode("utf-8"))
        elif self.path == "/health":
            self.send_response(200)
            self.send_header("Content-type", "application/json")
            self.end_headers()
            self.wfile.write(b'{"status":"ok"}')
        else:
            super().do_GET()

if __name__ == "__main__":
    os.chdir("/opt/data/ecosystem/portal")
    with socketserver.TCPServer(("", PORT), PortalHandler) as httpd:
        print(f"Serving RunLocal Hub MVP at port {PORT}")
        httpd.serve_forever()
