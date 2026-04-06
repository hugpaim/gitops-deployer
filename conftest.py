# conftest.py
import sys
from pathlib import Path

# Adiciona a raiz do projeto ao sys.path para que
# "from deployer..." funcione nos testes
sys.path.insert(0, str(Path(__file__).parent))
