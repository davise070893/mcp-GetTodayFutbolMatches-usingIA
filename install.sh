# Configuración de instalación con uv

# Instalar uv si no lo tienes
# Windows (PowerShell):
# powershell -ExecutionPolicy ByPass -c "irm https://astral.sh/uv/install.ps1 | iex"

# Configurar el entorno virtual e instalar dependencias
uv venv
uv pip install -r requirements.txt

# Para desarrollo, instalar con dependencias adicionales
uv pip install -e ".[dev]"

# Ejecutar el servidor MCP
uv run python run_server.py

# Ejecutar pruebas del scraper
uv run python test_scraper.py

# Formatear código
uv run black src/

# Verificar tipos
uv run mypy src/