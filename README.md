# 🖥️ CampusLands Asset Manager — Control Interno de Equipos

Sistema de consola desarrollado en Python + SQLite para gestionar el préstamo de computadores en las instalaciones de Cajasan (CampusLands). Permite controlar asignaciones, estados físicos de equipos y estados de usuarios con trazabilidad completa.

---

## 📁 Estructura del Proyecto

```
gestionEquipos/
│
├── core/
│   ├── __init__.py
│   ├── database.py      # Inicialización del esquema SQLite
│   └── manager.py       # Lógica de negocio (CampusManager)
│
├── main.py              # Interfaz de usuario (menú de consola)
└── campuslands.db       # Base de datos generada automáticamente
```

---

## ⚙️ Requisitos

- Python 3.x
- Librería estándar `sqlite3` (incluida en Python)
- No requiere dependencias externas

---

## 🚀 Cómo ejecutar

```bash
python main.py
```

La base de datos `campuslands.db` se crea automáticamente al iniciar el programa por primera vez.

---

## 🗃️ Esquema de Base de Datos

### `campers`
| Campo  | Tipo    | Descripción                        |
|--------|---------|------------------------------------|
| id     | INTEGER | Clave primaria (ingresada manualmente) |
| nombre | TEXT    | Nombre completo del camper         |
| estado | TEXT    | `Activo` \| `Bloqueado`            |

### `computadores`
| Campo          | Tipo | Descripción                              |
|----------------|------|------------------------------------------|
| serial         | TEXT | Clave primaria                           |
| marca          | TEXT | Marca del equipo                         |
| estado_fisico  | TEXT | `Excelente` \| `Dañado`                  |
| disponibilidad | TEXT | `Disponible` \| `Ocupado` \| `Bloqueado` |

### `asignaciones`
| Campo         | Tipo      | Descripción                              |
|---------------|-----------|------------------------------------------|
| id_asignacion | INTEGER   | Clave primaria autoincremental           |
| id_camper     | INTEGER   | FK → campers.id                          |
| serial_pc     | TEXT      | FK → computadores.serial                 |
| cubiculo      | INTEGER   | Número de cubículo asignado              |
| fecha_inicio  | TIMESTAMP | Fecha/hora de inicio de la asignación    |
| fecha_fin     | TIMESTAMP | Fecha/hora de devolución del equipo      |
| activo        | INTEGER   | `1` = activo, `0` = histórico            |

---

## 📋 Funcionalidades del Menú

| Opción | Acción |
|--------|--------|
| 1 — Registro | Registrar nuevo Camper o PC |
| 2 — Asignar | Vincular un PC disponible a un Camper |
| 3 — Retornar | Liberar un equipo y registrar fecha de devolución |
| 4 — Admin | Bloquear/desbloquear Camper · Reportar PC dañado |
| 5 — Reportes | Ver asignaciones activas · Ver PCs disponibles |
| 6 — Salir | Cerrar el sistema |

---

## 🔒 Reglas de Negocio

- Un Camper **bloqueado** no puede recibir equipos.
- Un PC **dañado** queda bloqueado automáticamente para nuevas asignaciones.
- Un Camper **no puede tener más de un PC** activo simultáneamente.
- Al reportar daño técnico sobre un PC en uso, el sistema **cierra la asignación automáticamente** (registra `fecha_fin` y pone `activo = 0`).
- Todas las operaciones críticas se ejecutan en **transacciones atómicas**: o se completan completamente o se revierten.

---

## 🤖 Trazabilidad de Ingeniería IA

Este proyecto fue desarrollado íntegramente aplicando la metodología de **Ingeniería de Prompts**, usando modelos de lenguaje como colaboradores en los roles de Product Owner, Senior Developer y QA Engineer. A continuación se documenta el flujo completo de prompts y resultados obtenidos.

---

### Iteración 1 — Definición del Producto (Rol: Product Owner)

**Objetivo:** Levantar los requerimientos del sistema desde cero.

**Prompt de elicitación (PO → Stakeholder):**
```
Como Product Owner, necesito que respondas:
1. ¿Cuál es el dolor principal hoy?
2. ¿Qué éxito esperamos ver?
3. ¿Quiénes interactúan con el sistema?
4. ¿Qué datos son críticos capturar?
5. ¿Cuál es el mínimo viable?
```

**Respuestas del stakeholder:**
- Dolor: gestión desordenada, no se registra nada.
- Éxito: saber quién usa qué, poder bloquear usuarios y PCs dañados.
- Usuarios: estudiantes (campers) y administrador(es).
- Datos críticos: ID camper, cubículo, estado físico del equipo.
- MVP: gestión de usuarios.

**Prompt generado (PO → Developer):**
```
Rol: Senior Python Developer con experiencia en arquitectura de software y SQLite.
Stack: Python 3.x + sqlite3 + menú de consola.
Requerimientos:
  - Gestión de campers con bloqueo.
  - Gestión de PCs con estado físico.
  - Control de asignaciones por cubículo.
  - Trazabilidad histórica.
Reglas de negocio críticas:
  - Un camper no puede tener más de un PC activo.
  - Un PC dañado u ocupado no puede asignarse.
  - Validar existencia antes de cualquier transacción.
Entregables: init_db(), clase CampusManager, menú while-True con try-except robusto.
```

**Resultado obtenido:**
- Archivos `database.py`, `manager.py` y `main.py` funcionales.
- Estructura modular con separación de responsabilidades (`core/`).
- Menú operativo con manejo básico de errores.

---

### Iteración 2 — Revisión de Calidad (Rol: QA Engineer)

**Objetivo:** Identificar bugs, vulnerabilidades y mejoras antes de continuar el desarrollo.

**Prompt utilizado:**
```
Rol: Senior QA Automation Engineer especializado en pruebas de integración en Python.
Contexto: Sistema de consola para préstamo de computadores usando Python 3 + SQLite.
Tarea:
  - Casos de borde: asignación a usuario inexistente, PC ya ocupado.
  - Integridad SQLite: transacciones, conexiones, llaves foráneas.
  - Validación de entradas: robustez del try-except.
  - Cumplimiento de reglas de negocio.
Entregables: reporte de bugs, sugerencias de mejora, script de unit tests.
```

**Bugs críticos identificados:**

| # | Severidad | Descripción |
|---|-----------|-------------|
| 1 | Alta | **Atomicidad rota** en `asignar_equipo`: dos conexiones distintas abiertas, riesgo de PC "fantasma" asignado pero marcado como Disponible. |
| 2 | Alta | **PRAGMA foreign_keys** no activado por conexión, solo en `init_db`. Riesgo de registros huérfanos. |
| 3 | Media | **Seriales duplicados** fallan silenciosamente sin mensaje amigable. |
| 4 | Media | **Doble liberación** de PC no lanza error, ejecuta UPDATE innecesario. |
| 5 | Baja | **Entradas vacías** aceptadas en nombre del camper y marca del PC. |
| 6 | Baja | **try-except genérico** en menú mezcla errores de BD con errores de entrada. |

**Mejoras aplicadas en respuesta al QA:**
- Método `_get_connection()` centralizado que activa `PRAGMA foreign_keys = ON` en cada conexión.
- Toda la lógica de `asignar_equipo` unificada en un solo bloque `with` (transacción atómica).
- Validación de campos vacíos en `registrar_camper` y `registrar_pc`.
- Manejo diferenciado de `ValueError` vs `Exception` en el menú.
- Mensajes de éxito/error retornados desde todos los métodos.

---

### Iteración 3 — Nuevas Funcionalidades (Rol: Developer, basado en backlog PO)

**Objetivo:** Agregar visibilidad operativa y acciones administrativas.

**Prompt del Product Owner:**
```
Asunto: Implementación de Módulos de Consulta y Gestión de Estados (Iteración 2 del desarrollo)
Objetivos:
  - Listar PCs disponibles (serial + marca, estado = Disponible y Excelente).
  - Ver asignaciones activas con JOIN (nombre camper, serial PC, cubículo, fecha).
  - Bloquear/desbloquear camper con validación de rowcount.
  - Reportar daño técnico con liberación automática en cascada.
  - Mostrar PCs disponibles antes de asignar (UX preventiva).
  - Tabla visual en consola con columnas alineadas.
Regla crítica adicional: al marcar PC dañado, cerrar asignación activa (fecha_fin + activo=0).
```

**Resultado obtenido:**

| Método nuevo | Descripción |
|---|---|
| `obtener_pcs_disponibles()` | SELECT filtrado por disponibilidad y estado físico |
| `obtener_asignaciones_activas()` | JOIN entre `asignaciones` y `campers`, solo activos |
| `gestionar_estado_camper()` | UPDATE con validación de `rowcount` para detectar IDs inexistentes |
| `reportar_daño_tecnico()` | Transacción atómica: cierra asignación + marca PC dañado |
| `mostrar_tabla()` (UI) | Formato de columnas con f-strings alineadas a 15 caracteres |

**Decisiones de diseño documentadas:**
- La consulta de PCs disponibles se muestra automáticamente al seleccionar "Asignar Equipo", reduciendo errores de digitación de seriales.
- El menú fue reorganizado en categorías semánticas (REGISTRO / ASIGNAR / RETORNAR / ADMIN / REPORTES) para mejorar la orientación del usuario.

---

## 🧪 Script de Pruebas de Reglas de Negocio

Generado por el agente QA para verificar las reglas críticas del sistema:

```python
import unittest
import os
from core.manager import CampusManager
from core.database import init_db

class TestCampusLogic(unittest.TestCase):

    def setUp(self):
        self.db_test = 'test_campus.db'
        self.manager = CampusManager(self.db_test)
        init_db()

    def tearDown(self):
        if os.path.exists(self.db_test):
            os.remove(self.db_test)

    def test_no_doble_asignacion(self):
        """Un Camper no puede tener 2 PCs activos simultáneamente."""
        self.manager.registrar_camper(1, "Test User")
        self.manager.registrar_pc("ABC", "Dell")
        self.manager.registrar_pc("XYZ", "HP")
        self.manager.asignar_equipo(1, "ABC", 101)
        res = self.manager.asignar_equipo(1, "XYZ", 102)
        self.assertEqual(res, "Error: El Camper ya tiene un equipo asignado.")

    def test_pc_danado_no_asignable(self):
        """Un PC dañado no puede entrar en el flujo de asignación."""
        self.manager.registrar_camper(2, "User 2")
        self.manager.registrar_pc("BAD", "Lenovo")
        self.manager.reportar_daño_tecnico("BAD")
        res = self.manager.asignar_equipo(2, "BAD", 105)
        self.assertIn("Error", res)

if __name__ == '__main__':
    unittest.main()
```

---

## 📌 Observaciones Técnicas Pendientes (Backlog)

Identificadas por el QA, priorizadas para futuras iteraciones:

- [ ] Validar que `nuevo_estado` en `gestionar_estado_camper` solo acepte valores del dominio `['Activo', 'Bloqueado']`.
- [ ] Agregar columna `observaciones` en `asignaciones` para notas al liberar equipos.
- [ ] Implementar resumen de inventario: total de PCs, ocupados, disponibles y dañados.
- [ ] Historial por equipo: mostrar todos los campers que han usado un PC específico.
- [ ] Exportación de reportes a CSV/JSON para gestión externa.

---

## 👥 Roles en el Proceso de Desarrollo IA

| Rol | Responsabilidad en este proyecto |
|-----|----------------------------------|
| **Product Owner (IA)** | Elicitación de requerimientos, definición de backlog, prompts hacia el equipo de desarrollo |
| **Senior Developer (IA)** | Implementación del MVP, refactorización por iteraciones, decisiones de arquitectura |
| **QA Engineer (IA)** | Análisis de bugs, pruebas de reglas de negocio, script de unit tests |

---

*Proyecto desarrollado como ejercicio de Ingeniería IA aplicada al ciclo de vida de software — CampusLands / Cajasan.*
