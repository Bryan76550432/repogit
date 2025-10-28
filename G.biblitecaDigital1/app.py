from flask import Flask, render_template, request, redirect, url_for
from datetime import datetime, timedelta
import sqlite3

app = Flask(__name__)

def init_database():
    conn = sqlite3.connect('biblioteca.db')
    
    # Tabla de Libros
    conn.execute('''
        CREATE TABLE IF NOT EXISTS libros (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            titulo TEXT NOT NULL,
            autor TEXT NOT NULL,
            año INTEGER NOT NULL,
            disponible BOOLEAN DEFAULT 1
        )
    ''')
    
    # Tabla de Usuarios
    conn.execute('''
        CREATE TABLE IF NOT EXISTS usuarios (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            nombre TEXT NOT NULL,
            correo TEXT NOT NULL UNIQUE
        )
    ''')
    
    # Tabla de Préstamos
    conn.execute('''
        CREATE TABLE IF NOT EXISTS prestamos (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            id_libro INTEGER NOT NULL,
            id_usuario INTEGER NOT NULL,
            fecha_prestamo DATE NOT NULL,
            fecha_devolucion DATE,
            FOREIGN KEY (id_libro) REFERENCES libros (id),
            FOREIGN KEY (id_usuario) REFERENCES usuarios (id)
        )
    ''')
    
    conn.commit()
    conn.close()

init_database()

# ===== RUTAS PARA LIBROS =====
@app.route('/')
def index_libros():
    conn = sqlite3.connect('biblioteca.db')
    conn.row_factory = sqlite3.Row
    cursor = conn.cursor()
    
    # Filtrar por autor si se proporciona
    autor = request.args.get('autor')
    disponible = request.args.get('disponible')
    
    query = 'SELECT * FROM libros'
    params = []
    
    if autor:
        query += ' WHERE autor LIKE ?'
        params.append(f'%{autor}%')
    elif disponible == 'si':
        query += ' WHERE disponible = 1'
    elif disponible == 'no':
        query += ' WHERE disponible = 0'
    
    cursor.execute(query, params)
    libros = cursor.fetchall()
    conn.close()
    return render_template('index_libros.html', libros=libros)

@app.route('/create_libro')
def create_libro():
    return render_template('create_libro.html')

@app.route('/save_libro', methods=["POST"])
def save_libro():
    titulo = request.form['titulo']
    autor = request.form['autor']
    año = request.form['año']
    
    conn = sqlite3.connect('biblioteca.db')
    cursor = conn.cursor()
    cursor.execute("INSERT INTO libros (titulo, autor, año) VALUES (?, ?, ?)", 
                  (titulo, autor, año))
    conn.commit()
    conn.close()
    return redirect(url_for('index_libros'))

@app.route('/edit_libro/<int:id>')
def edit_libro(id):
    conn = sqlite3.connect('biblioteca.db')
    conn.row_factory = sqlite3.Row
    cursor = conn.cursor()
    cursor.execute('SELECT * FROM libros WHERE id = ?', (id,))
    libro = cursor.fetchone()
    conn.close()
    return render_template('edit_libro.html', libro=libro)

@app.route('/update_libro/<int:id>', methods=["POST"])
def update_libro(id):
    titulo = request.form['titulo']
    autor = request.form['autor']
    año = request.form['año']
    
    conn = sqlite3.connect('biblioteca.db')
    cursor = conn.cursor()
    cursor.execute("UPDATE libros SET titulo = ?, autor = ?, año = ? WHERE id = ?", 
                  (titulo, autor, año, id))
    conn.commit()
    conn.close()
    return redirect(url_for('index_libros'))

@app.route('/delete_libro/<int:id>')
def delete_libro(id):
    conn = sqlite3.connect('biblioteca.db')
    cursor = conn.cursor()
    cursor.execute('DELETE FROM libros WHERE id = ?', (id,))
    conn.commit()
    conn.close()
    return redirect(url_for('index_libros'))

# ===== RUTAS PARA USUARIOS =====
@app.route('/usuarios')
def index_usuarios():
    conn = sqlite3.connect('biblioteca.db')
    conn.row_factory = sqlite3.Row
    cursor = conn.cursor()
    cursor.execute('SELECT * FROM usuarios')
    usuarios = cursor.fetchall()
    conn.close()
    return render_template('index_usuarios.html', usuarios=usuarios)

@app.route('/create_usuario')
def create_usuario():
    return render_template('create_usuario.html')

@app.route('/save_usuario', methods=["POST"])
def save_usuario():
    nombre = request.form['nombre']
    correo = request.form['correo']
    
    conn = sqlite3.connect('biblioteca.db')
    cursor = conn.cursor()
    cursor.execute("INSERT INTO usuarios (nombre, correo) VALUES (?, ?)", 
                  (nombre, correo))
    conn.commit()
    conn.close()
    return redirect(url_for('index_usuarios'))

# ===== RUTAS PARA PRÉSTAMOS =====
@app.route('/prestamos')
def index_prestamos():
    conn = sqlite3.connect('biblioteca.db')
    conn.row_factory = sqlite3.Row
    cursor = conn.cursor()
    
    cursor.execute('''
        SELECT p.*, l.titulo, u.nombre as usuario_nombre,
               CASE 
                   WHEN p.fecha_devolucion IS NULL AND date(p.fecha_prestamo) < date('now', '-15 days') 
                   THEN 'RETRASADO'
                   ELSE 'EN TIEMPO'
               END as estado
        FROM prestamos p
        JOIN libros l ON p.id_libro = l.id
        JOIN usuarios u ON p.id_usuario = u.id
        ORDER BY p.fecha_prestamo DESC
    ''')
    prestamos = cursor.fetchall()
    conn.close()
    return render_template('index_prestamos.html', prestamos=prestamos)

@app.route('/create_prestamo')
def create_prestamo():
    conn = sqlite3.connect('biblioteca.db')
    conn.row_factory = sqlite3.Row
    cursor = conn.cursor()
    
    # Obtener libros disponibles
    cursor.execute('SELECT * FROM libros WHERE disponible = 1')
    libros = cursor.fetchall()
    
    # Obtener usuarios
    cursor.execute('SELECT * FROM usuarios')
    usuarios = cursor.fetchall()
    
    conn.close()
    return render_template('create_prestamo.html', libros=libros, usuarios=usuarios)

@app.route('/save_prestamo', methods=["POST"])
def save_prestamo():
    id_libro = request.form['id_libro']
    id_usuario = request.form['id_usuario']
    fecha_prestamo = datetime.now().strftime('%Y-%m-%d')
    
    conn = sqlite3.connect('biblioteca.db')
    cursor = conn.cursor()
    
    # Insertar préstamo
    cursor.execute("INSERT INTO prestamos (id_libro, id_usuario, fecha_prestamo) VALUES (?, ?, ?)", 
                  (id_libro, id_usuario, fecha_prestamo))
    
    # Marcar libro como no disponible
    cursor.execute("UPDATE libros SET disponible = 0 WHERE id = ?", (id_libro,))
    
    conn.commit()
    conn.close()
    return redirect(url_for('index_prestamos'))

@app.route('/devolver_libro/<int:id>')
def devolver_libro(id):
    conn = sqlite3.connect('biblioteca.db')
    cursor = conn.cursor()
    
    # Obtener id_libro del préstamo
    cursor.execute('SELECT id_libro FROM prestamos WHERE id = ?', (id,))
    prestamo = cursor.fetchone()
    
    if prestamo:# Registrar devolución
        fecha_devolucion = datetime.now().strftime('%Y-%m-%d')
        cursor.execute("UPDATE prestamos SET fecha_devolucion = ? WHERE id = ?", 
                      (fecha_devolucion, id))
        
        # Marcar libro como disponible
        cursor.execute("UPDATE libros SET disponible = 1 WHERE id = ?", (prestamo[0],))
    
    conn.commit()
    conn.close()
    return redirect(url_for('index_prestamos'))

if __name__ == '__main__':
    app.run(debug=True,port=5002)