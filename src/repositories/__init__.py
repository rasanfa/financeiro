from src.repositories.beneficiarios import BeneficiariosRepository
from src.repositories.cartoes import CartoesRepository
from src.repositories.categorias import CategoriasRepository, SubcategoriasRepository
from src.repositories.contas import ContasRepository
from src.repositories.instituicoes import InstituicoesRepository
from src.repositories.movimentacoes import MovimentacoesRepository

__all__ = [
    "BeneficiariosRepository",
    "CartoesRepository",
    "CategoriasRepository",
    "ContasRepository",
    "InstituicoesRepository",
    "MovimentacoesRepository",
    "SubcategoriasRepository",
]
