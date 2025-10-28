import sqlite3

def insertar_datos():
    conn = sqlite3.connect('biblioteca.db')
    cursor = conn.cursor()
    
    # Libros para insertar
    libros = [
        ('Don Quijote de la Mancha', 'Miguel de Cervantes', 1605),
        ('Romeo y Julieta', 'William Shakespeare', 1597),
        ('Orgullo y prejuicio', 'Jane Austen', 1813),
        ('Moby Dick', 'Herman Melville', 1851),
        ('Rayuela', 'Julio Cortázar', 1963),
        ('La ciudad y los perros', 'Mario Vargas Llosa', 1963),
        ('Pedro Páramo', 'Juan Rulfo', 1955),
        ('Ficciones', 'Jorge Luis Borges', 1944),
        ('Fahrenheit 451', 'Ray Bradbury', 1953),
        ('Un mundo feliz', 'Aldous Huxley', 1932),
        ('El señor de los anillos', 'J.R.R. Tolkien', 1954),
        ('Juego de tronos', 'George R.R. Martin', 1996),
        ('El código Da Vinci', 'Dan Brown', 2003),
        ('It', 'Stephen King', 1986),
        ('Los pilares de la tierra', 'Ken Follett', 1989),
        ('Cien años de soledad', 'Gabriel García Márquez', 1967),
        ('1984', 'George Orwell', 1949),
        ('El principito', 'Antoine de Saint-Exupéry', 1943),
        ('Harry Potter y la piedra filosofal', 'J.K. Rowling', 1997),
        ('Crónica de una muerte anunciada', 'Gabriel García Márquez', 1981)
    ]
    
    # Usuarios para insertar
    usuarios = [
        ('María González', 'maria@email.com'),
        ('Carlos López', 'carlos@email.com'),
        ('Ana Martínez', 'ana@email.com'),
        ('Pedro Rodríguez', 'pedro@email.com'),
        ('Laura Sánchez', 'laura@email.com'),
        ('José Ramírez', 'jose@email.com'),
        ('Isabel Torres', 'isabel@email.com'),
        ('Miguel Díaz', 'miguel@email.com'),
        ('Elena Castro', 'elena@email.com'),
        ('Roberto Navarro', 'roberto@email.com')
    ]
    
    # Insertar libros
    cursor.executemany(
        "INSERT INTO libros (titulo, autor, año) VALUES (?, ?, ?)",
        libros
    )
    print(f"✅ {len(libros)} libros insertados")
    
    # Insertar usuarios
    cursor.executemany(
        "INSERT INTO usuarios (nombre, correo) VALUES (?, ?)",
        usuarios
    )
    print(f"✅ {len(usuarios)} usuarios insertados")
    
    # Insertar algunos préstamos
    prestamos = [
        (1, 1, '2024-01-10', None),    # Don Quijote prestado a María
        (2, 2, '2024-02-01', '2024-02-15'),  # Romeo y Julieta ya devuelto
        (3, 3, '2024-02-20', None),    # Orgullo y prejuicio prestado
        (16, 4, '2024-01-05', None),   # Cien años de soledad prestado (RETRASADO)
        (17, 5, '2024-02-25', None)    # 1984 prestado recientemente
    ]
    
    cursor.executemany(
        "INSERT INTO prestamos (id_libro, id_usuario, fecha_prestamo, fecha_devolucion) VALUES (?, ?, ?, ?)",
        prestamos
    )
    print(f"✅ {len(prestamos)} préstamos insertados")
    
    # Actualizar disponibilidad de libros prestados
    libros_prestados = [1, 3, 16, 17]  # IDs de libros prestados
    for libro_id in libros_prestados:
        cursor.execute("UPDATE libros SET disponible = 0 WHERE id = ?", (libro_id,))
    print("✅ Disponibilidad actualizada")
    
    conn.commit()
    conn.close()
    print("🎉 TODOS los datos insertados correctamente!")
    print("📚 Ahora ejecuta: python app.py")
    print("🌐 Ve a: http://localhost:5000")

if __name__ == '__main__':
    insertar_datos()