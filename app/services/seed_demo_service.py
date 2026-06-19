from decimal import Decimal
from app.extensions import db, bcrypt
from app.models import (
    Usuario, Rol, RolNombre, Producto, ProductoTipo, 
    Ingrediente, Receta, UnidadMedida, Cliente
)

def seed_demo_data() -> str:
    # 1. Crear Roles si no existen
    roles_map = {}
    for role_name in RolNombre:
        role = Rol.query.filter_by(nombre=role_name).first()
        if not role:
            role = Rol(nombre=role_name, descripcion=role_name.value.title())
            db.session.add(role)
        roles_map[role_name.value] = role
    db.session.commit()

    # 2. Crear Usuarios (Contraseña uniforme: P1zz@S3cur3!2026)
    demo_password = bcrypt.generate_password_hash("P1zz@S3cur3!2026").decode("utf-8")
    
    usuarios_demo = [
        {"nombre": "Admin Demo", "usuario": "admin", "rol": roles_map["administrador"]},
        {"nombre": "Vendedor 1", "usuario": "vendedor1", "rol": roles_map["vendedor"]},
        {"nombre": "Vendedor 2", "usuario": "vendedor2", "rol": roles_map["vendedor"]},
        {"工作人员": "Cajero 1", "usuario": "cajero1", "rol": roles_map["cajero"]},
        {"nombre": "Cocina 1", "usuario": "cocina1", "rol": roles_map["cocina"]},
        {"nombre": "Bodeguero 1", "usuario": "bodeguero1", "rol": roles_map["bodeguero"]},
        {"nombre": "Repartidor 1", "usuario": "repartidor1", "rol": roles_map["repartidor"]},
    ]

    for u_data in usuarios_demo:
        nombre = u_data.get("nombre") or u_data.get("工作人员")
        user = Usuario.query.filter_by(usuario=u_data["usuario"]).first()
        if not user:
            user = Usuario(
                nombre=nombre,
                usuario=u_data["usuario"],
                password_hash=demo_password,
                rol_id=u_data["rol"].id,
                activo=True
            )
            db.session.add(user)
    db.session.commit()

    # 3. Crear Clientes
    cliente = Cliente.query.filter_by(telefono="0999999999").first()
    if not cliente:
        cliente = Cliente(nombre="Cliente Frecuente", telefono="0999999999", direccion="Calle Principal 123", referencia="Frente al parque")
        db.session.add(cliente)
    db.session.commit()

    # 4. Crear Ingredientes
    ingredientes_data = [
        {"nombre": "Harina", "unidad": UnidadMedida.kg, "stock": 50.0, "minimo": 10.0},
        {"nombre": "Queso Mozzarella", "unidad": UnidadMedida.kg, "stock": 20.0, "minimo": 5.0},
        {"nombre": "Salsa de Tomate", "unidad": UnidadMedida.l, "stock": 15.0, "minimo": 3.0},
        {"nombre": "Jamón", "unidad": UnidadMedida.kg, "stock": 10.0, "minimo": 2.0},
        {"nombre": "Pepperoni", "unidad": UnidadMedida.kg, "stock": 8.0, "minimo": 2.0},
        {"nombre": "Vegetales Mixtos", "unidad": UnidadMedida.kg, "stock": 12.0, "minimo": 3.0},
    ]

    ingredientes_map = {}
    for i_data in ingredientes_data:
        ing = Ingrediente.query.filter_by(nombre=i_data["nombre"]).first()
        if not ing:
            ing = Ingrediente(
                nombre=i_data["nombre"],
                unidad_medida=i_data["unidad"],
                stock_actual=Decimal(str(i_data["stock"])),
                stock_minimo=Decimal(str(i_data["minimo"]))
            )
            db.session.add(ing)
            db.session.flush()
        ingredientes_map[i_data["nombre"]] = ing
    db.session.commit()

    # 5. Crear Productos y Recetas
    productos_data = [
        {
            "nombre": "Pizza Familiar Pepperoni",
            "tipo": ProductoTipo.pizza,
            "precio": "15.99",
            "receta": [
                ("Harina", "0.5"),
                ("Queso Mozzarella", "0.3"),
                ("Salsa de Tomate", "0.2"),
                ("Pepperoni", "0.2")
            ]
        },
        {
            "nombre": "Pizza Mediana Jamón",
            "tipo": ProductoTipo.pizza,
            "precio": "10.99",
            "receta": [
                ("Harina", "0.3"),
                ("Queso Mozzarella", "0.2"),
                ("Salsa de Tomate", "0.15"),
                ("Jamón", "0.15")
            ]
        },
        {
            "nombre": "Pizza Vegetariana",
            "tipo": ProductoTipo.pizza,
            "precio": "14.99",
            "receta": [
                ("Harina", "0.4"),
                ("Queso Mozzarella", "0.25"),
                ("Salsa de Tomate", "0.2"),
                ("Vegetales Mixtos", "0.3")
            ]
        },
        {
            "nombre": "Lasaña de Carne",
            "tipo": ProductoTipo.lasana,
            "precio": "8.50",
            "receta": [
                ("Queso Mozzarella", "0.1"),
                ("Salsa de Tomate", "0.1")
            ]
        },
        {
            "nombre": "Cola Cola 1L",
            "tipo": ProductoTipo.bebida,
            "precio": "2.50",
            "receta": []
        },
        {
            "nombre": "Combo Familiar (Pizza + Bebida)",
            "tipo": ProductoTipo.combo,
            "precio": "17.00",
            "receta": [] # Los combos usualmente descuentan por separado o tienen lógica especial
        }
    ]

    for p_data in productos_data:
        prod = Producto.query.filter_by(nombre=p_data["nombre"]).first()
        if not prod:
            prod = Producto(
                nombre=p_data["nombre"],
                tipo=p_data["tipo"],
                precio=Decimal(p_data["precio"]),
                disponible=True,
                es_personalizable=p_data["tipo"] == ProductoTipo.pizza
            )
            db.session.add(prod)
            db.session.flush()

            for ing_nombre, cant in p_data["receta"]:
                receta = Receta(
                    producto_id=prod.id,
                    ingrediente_id=ingredientes_map[ing_nombre].id,
                    cantidad=Decimal(cant)
                )
                db.session.add(receta)
    
    db.session.commit()
    return "Datos demo cargados exitosamente."
