from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session

from app.auth.models.user import User
from app.core.dependencies import get_current_user
from app.database import get_db
from app.models.perfil import PerfilInvestidor
from app.models.suitability_db import PerfilSalvo
from app.services.suitability import classificar_perfil

router = APIRouter(prefix="/suitability", tags=["Suitability"])


@router.post("", status_code=200)
def salvar_perfil(
    perfil: PerfilInvestidor,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    """Classifica o perfil de risco e persiste o resultado vinculado ao usuário (upsert)."""
    perfil_classificado = classificar_perfil(perfil)

    registro = db.query(PerfilSalvo).filter(PerfilSalvo.user_id == current_user.id).first()
    if registro:
        registro.perfil_classificado = perfil_classificado
        registro.idade = perfil.idade
        registro.renda = perfil.renda
        registro.patrimonio = perfil.patrimonio
        registro.horizonte_anos = perfil.horizonte_anos
        registro.objetivo = perfil.objetivo
    else:
        registro = PerfilSalvo(
            user_id=current_user.id,
            perfil_classificado=perfil_classificado,
            idade=perfil.idade,
            renda=perfil.renda,
            patrimonio=perfil.patrimonio,
            horizonte_anos=perfil.horizonte_anos,
            objetivo=perfil.objetivo,
        )
        db.add(registro)

    db.commit()
    db.refresh(registro)
    return {
        "id": registro.id,
        "perfil_classificado": registro.perfil_classificado,
        "updated_at": registro.updated_at,
    }


@router.get("/me")
def meu_perfil(
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    """Retorna o perfil de suitability salvo do usuário autenticado."""
    registro = db.query(PerfilSalvo).filter(PerfilSalvo.user_id == current_user.id).first()
    if not registro:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Perfil não encontrado. Responda o questionário primeiro.",
        )
    return {
        "perfil_classificado": registro.perfil_classificado,
        "idade": registro.idade,
        "renda": registro.renda,
        "patrimonio": registro.patrimonio,
        "horizonte_anos": registro.horizonte_anos,
        "objetivo": registro.objetivo,
        "updated_at": registro.updated_at,
    }
