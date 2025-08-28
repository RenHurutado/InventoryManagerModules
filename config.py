# config.py - Simple configuration file
from pathlib import Path

# Base paths
BASE_DIR = Path(__file__).parent
DATA_DIR = BASE_DIR / 'data'
DATA_DIR.mkdir(exist_ok=True)

# Database settings
DATABASE_CONFIG = {
    'standard': {
        'path': DATA_DIR / 'inventory.db',
        'name': 'Standard Inventory'
    }
}

DEFAULT_DB = 'standard'

# LLM Settings for LM Studio
LLM_CONFIG = {
    'lm_studio': {
        'url': 'http://localhost:1234',
        'endpoint': '/v1/completions'
    },
    'temperature': 0.1,
    'max_tokens': 500
}

# Default employees
DEFAULT_EMPLOYEES = [
    ('Juan Pérez', 'EMP001', 'Mecánica'),
    ('María García', 'EMP002', 'Eléctrica'),
    ('Carlos López', 'EMP003', 'Mantenimiento'),
    ('Ana Martínez', 'EMP004', 'Producción')
]

# Create necessary directories
(DATA_DIR / 'exports').mkdir(exist_ok=True)
(DATA_DIR / 'imports').mkdir(exist_ok=True)