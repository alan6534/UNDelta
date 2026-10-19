import pandas as pd
import psycopg as psy

conn = psy.connect("postgresql://postgres:qF6QIzYfAGAOsNT5@db.cvjmwzvenbriowzilksh.supabase.co:5432/postgres")
cursor = conn.cursor()

usuario = input("Ingrese su usuario: ")

def obtener_costo(producto): 
    query = conn.execute('''
            SELECT costo_puntos
            FROM recompensa
            WHERE nombre = %s
        ''', params=(producto,)) 
    
    costo = query.fetchone() #obteniendo con psycopg 
    return costo[0]

def obtener_stock(producto):
    query = '''
            SELECT stock
            FROM recompensa
            WHERE nombre = %s
        '''
    df = pd.read_sql_query(query,conn,params=(producto,))
    stock = df["stock"].iloc[0]
    return stock

def mostrar_saldo(usuario):
    query = conn.execute('''
        SELECT puntos 
        FROM perfil
        WHERE usuario = %s   
    ''', params=(usuario,))
    puntos = query.fetchone()
    return puntos[0]
    
def verificar_saldo(producto,usuario):
    costo = obtener_costo(producto)
    return costo <= mostrar_saldo(usuario)

def verificar_stock(producto):
    stock = obtener_stock(producto)
    return stock >= 1 
    
def restar_stock(producto):
    query = '''
            UPDATE recompensa
            SET stock = stock-1
            WHERE nombre = %s
        '''
    conn.execute(query,params=(producto,))
    
def restar_saldo(producto, usuario):
    costo = obtener_costo(producto)
    query = '''
            UPDATE perfil
            SET puntos = puntos - %s
            WHERE usuario = %s
        '''
    conn.execute(query,params=(costo,usuario))

def verificar_compra(producto, usuario):
    if verificar_stock(producto) == True:
        if verificar_saldo(producto,usuario) == True:
            return True
        else:  
            return "Saldo insuficiente"
    else: 
        return "stock insuficiente"
    
def obtener_producto_id(producto):
    query= '''
        SELECT id 
        FROM recompensa
        WHERE nombre = %s     
    '''
    df = pd.read_sql_query(query, conn, params=(producto,))
    id = df["id"].iloc[0]
    return id
    
def obtener_usuario_id(usuario):
    query='''
        SELECT id 
        FROM perfil
        WHERE usuario = %s
    '''
    df = pd.read_sql_query(query,conn,params=(usuario,)) #consulta,conexion,parametros
    id = df["id"].iloc[0]
    return id
    
def registrar_canje(producto, usuario):
    recompensa_id = obtener_producto_id(producto)
    usuario_id = obtener_usuario_id(usuario)
    costo_puntos = obtener_costo(producto)
    query = '''
        INSERT INTO canje(perfil_id, recompensa_id, costo_puntos,fecha)
        VALUES(%s,%s,%s,NOW())
    '''
    conn.execute(query, params=(usuario_id, recompensa_id,costo_puntos))
    
def comprar(producto,usuario):
    verificacion = verificar_compra(producto,usuario)
    if verificacion == True:
        try: 
            restar_stock(producto)
            restar_saldo(producto,usuario)
            registrar_canje(producto,usuario)
            conn.commit()
            return "Se ha realizado la compra correctamente"
        except Exception as e:
            conn.rollback()
            print(f"Error: {e}")
            return "No se ha podido realizar la compra"
            
    elif verificacion == "stock insuficiente":
        return "Stock insuficiente"
    else:
        return "saldo insuficiente"
    
def obtener_productos():
    query = conn.execute('''
    SELECT nombre, costo_puntos, stock
    FROM recompensa
    ''')
    productos = query.fetchall()
    return productos
        
def verificar_producto(entrada):
    productos = obtener_productos()
    return any(entrada.lower() == nombre.lower() for nombre, costo, stock in productos)
    
while True:
    print("\n====== TIENDA UNDELTA ======")
    print("OBJETOS DISPONIBLES:")

    productos = obtener_productos()
    for nombre, costo, stock in productos:
        print(f"{nombre} || Costo: {costo} U || Stock: {stock}")

    print("""
    1. Comprar producto
    2. Mostrar saldo
    3. Salir
    """)
    
    entrada = input("Seleccione una opcion: ")
    
    if entrada == "1":
        producto = input("Elija un producto de la tienda: ")
        if verificar_producto(producto) == True:
            print(comprar(producto, usuario))
        else:
            print("----Producto No Encontrado----")
            
    elif entrada == "3":
        break
    
    elif entrada == "2":
        print(f"\nSaldo: {mostrar_saldo(usuario)}U")
        
    else:
        print("----Opción inexistente----")

conn.close()