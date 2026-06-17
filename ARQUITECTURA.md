# Arquitectura del Sistema

El proyecto sigue una arquitectura **Layered / N-Tier Architecture** orientada al Dominio, separando claramente las responsabilidades para facilitar el mantenimiento y las pruebas.

## Componentes

### 1. Modelos (Models) `app/models/`
Definen la estructura de los datos y las reglas de negocio base mediante clases que heredan de `db.Model` (SQLAlchemy). No deben contener lógica compleja ni interactuar con otras capas externas.

### 2. Repositorios (Repositories) `app/repositories/`
Encapsulan las consultas a la base de datos (Querying). Todo el acceso de lectura y persistencia de las entidades pasa por estas clases. Mantienen limpio el código de la capa de Servicios de consultas ORM complejas.

### 3. Servicios (Services) `app/services/`
Contienen toda la **Lógica de Negocio**. Aquí es donde se realizan las operaciones importantes: validaciones complejas, cálculo de totales, interacciones entre múltiples repositorios, manejo de inventarios, pagos, etc. 

### 4. Controladores / Rutas (Routes) `app/admin/`, `app/auth/`
Interactúan con el cliente (Web). Reciben peticiones HTTP, validan la entrada de datos a través de los Formularios (WTForms) y llaman a la capa de Servicios. Manejan respuestas HTTP, templates y redirecciones. No deben contener lógica de negocio.

### 5. Formularios (Forms) `app/*/forms.py`
Usan WTForms para validar y procesar entradas de datos. Se encargan de la higiene de datos (XSS pre-mitigación, validación de tipos, expresiones regulares de seguridad).

## Diagrama del Flujo

```text
[ Cliente (Browser) ] -> [ Rutas (Flask) ]
                              |
                              v
                        [ WTForms ]
                              |
                              v
                     [ Servicios (Business Logic) ]
                              |
                              v
                [ Repositorios (Data Access) ]
                              |
                              v
                     [ SQLAlchemy (ORM) ]
                              |
                              v
                      [ Base de Datos ]
```

## Ventajas de este Enfoque
1. **Testing Aislado**: Permite hacer mock de los repositorios para probar la lógica de servicios.
2. **Reutilización**: Múltiples controladores (ej. API, CLI, Rutas Web) pueden consumir el mismo servicio de negocio.
3. **Escalabilidad**: El código es modular. Cambiar la base de datos o el framework no altera la capa de servicios de manera intrusiva.
