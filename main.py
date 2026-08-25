from fastapi import FastAPI, Depends, HTTPException
from fastapi.staticfiles import StaticFiles
from fastapi.middleware.cors import CORSMiddleware
from sqlalchemy.orm import Session
from typing import List
import models, schemas, database
from database import engine, get_db
import re

# Criar tabelas
models.Base.metadata.create_all(bind=engine)

app = FastAPI(title="PMO Portfolio Platform", version="1.0.0")

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Servir arquivos estáticos
app.mount("/static", StaticFiles(directory="static"), name="static")

# ============ CRUD PROJETOS ============

@app.get("/api/projects", response_model=List[schemas.ProjectResponse])
def list_projects(status: str = None, db: Session = Depends(get_db)):
    query = db.query(models.Project)
    if status and status != "todos":
        query = query.filter(models.Project.status == status)
    return query.all()

@app.get("/api/projects/{project_id}", response_model=schemas.ProjectResponse)
def get_project(project_id: int, db: Session = Depends(get_db)):
    project = db.query(models.Project).filter(models.Project.id == project_id).first()
    if not project:
        raise HTTPException(status_code=404, detail="Projeto não encontrado")
    return project

@app.post("/api/projects", response_model=schemas.ProjectResponse)
def create_project(project: schemas.ProjectCreate, db: Session = Depends(get_db)):
    db_project = models.Project(**project.dict())
    db.add(db_project)
    db.commit()
    db.refresh(db_project)
    return db_project

@app.put("/api/projects/{project_id}", response_model=schemas.ProjectResponse)
def update_project(project_id: int, project: schemas.ProjectCreate, db: Session = Depends(get_db)):
    db_project = db.query(models.Project).filter(models.Project.id == project_id).first()
    if not db_project:
        raise HTTPException(status_code=404, detail="Projeto não encontrado")
    for key, value in project.dict().items():
        setattr(db_project, key, value)
    db.commit()
    db.refresh(db_project)
    return db_project

@app.delete("/api/projects/{project_id}")
def delete_project(project_id: int, db: Session = Depends(get_db)):
    db_project = db.query(models.Project).filter(models.Project.id == project_id).first()
    if not db_project:
        raise HTTPException(status_code=404, detail="Projeto não encontrado")
    db.delete(db_project)
    db.commit()
    return {"message": "Projeto removido com sucesso"}

# ============ BUSCA IA ============

@app.post("/api/ai/search", response_model=schemas.AIResponse)
def ai_search(query_data: schemas.AIQuery, db: Session = Depends(get_db)):
    query = query_data.query.lower().strip()
    projects = db.query(models.Project).all()

    answer = ""
    sources = []

    # Normalizar query
    q = query

    # Padrões de busca
    if any(w in q for w in ["atrasado", "atrasados", "delay", "late"]):
        atrasados = [p for p in projects if p.status == "atrasado"]
        if not atrasados:
            answer = "✅ **Boa notícia!** Nenhum projeto está atrasado no momento."
        else:
            answer = f"⚠️ Encontrei **{len(atrasados)} projeto(s) atrasado(s)**:\n\n"
            for p in atrasados:
                answer += f"• **{p.name}** ({p.code}) — Progresso: {p.progress}%, Gerente: {p.manager}\n"
                answer += f"  🚨 Risco: {p.risks or 'Não informado'}\n\n"
            answer += "💡 **Recomendação:** Priorizar ações corretivas e realocar recursos."
        sources = [p.code for p in atrasados]

    elif any(w in q for w in ["orçamento", "budget", "custo", "custo total", "investimento", "dinheiro", "valor"]):
        total = 0
        for p in projects:
            val = re.sub(r"[^0-9]", "", str(p.budget or "0"))
            total += int(val) if val else 0
        answer = f"💰 O **orçamento total do portfólio** é de **R$ {total/1_000_000:.1f} milhões** ({len(projects)} projetos).\n\n"
        answer += "📊 **Maiores investimentos:**\n"
        sorted_p = sorted(projects, key=lambda x: int(re.sub(r"[^0-9]", "", str(x.budget or "0")) or 0), reverse=True)
        for p in sorted_p[:5]:
            answer += f"• {p.name}: {p.budget or 'N/A'}\n"
        sources = ["Portfólio Completo"]

    elif any(w in q for w in ["risco", "riscos", "problema", "problemas", "alerta"]):
        with_risks = [p for p in projects if p.risks and "nenhum" not in p.risks.lower()]
        answer = f"🚨 Identifiquei **{len(with_risks)} projetos com riscos ativos**:\n\n"
        for p in with_risks:
            answer += f"• **{p.name}** ({p.code}) — {p.risks}\n"
        sources = [p.code for p in with_risks]

    elif any(w in q for w in ["prioridade", "prioritário", "critico", "crítico", "urgente"]):
        criticos = [p for p in projects if p.priority in ["critica", "critico", "crítica", "crítico"]]
        answer = f"🔴 Existem **{len(criticos)} projetos de prioridade crítica**:\n\n"
        for p in criticos:
            answer += f"• **{p.name}** ({p.code}) — {p.progress}% concluído, prazo: {p.deadline or 'N/A'}\n"
        if criticos:
            answer += "\n💡 **Recomendação:** Manter foco e alocação de recursos nesses projetos."
        sources = [p.code for p in criticos]

    elif any(w in q for w in ["resumo", "status", "andamento", "visão geral", "overview", "dashboard", "portfólio"]):
        answer = f"📊 **Resumo do Portfólio** ({len(projects)} projetos):\n\n"
        em_andamento = len([p for p in projects if p.status == "em-andamento"])
        concluidos = len([p for p in projects if p.status == "concluido"])
        atrasados = len([p for p in projects if p.status == "atrasado"])
        planejados = len([p for p in projects if p.status == "planejado"])
        avg_progress = sum(p.progress for p in projects) // len(projects) if projects else 0

        answer += f"✅ Concluídos: {concluidos}\n"
        answer += f"🔄 Em Andamento: {em_andamento}\n"
        answer += f"⚠️ Atrasados: {atrasados}\n"
        answer += f"📋 Planejados: {planejados}\n\n"
        answer += f"📈 **Progresso médio:** {avg_progress}%"
        sources = ["Portfólio Completo"]

    elif any(w in q for w in ["gerente", "responsável", "lider", "líder", "quem gerencia"]):
        answer = "👥 **Gerentes de Projetos:**\n\n"
        managers = {}
        for p in projects:
            m = p.manager or "Não atribuído"
            if m not in managers:
                managers[m] = []
            managers[m].append(p)
        for m, projs in managers.items():
            answer += f"• **{m}** ({len(projs)} projeto(s)):\n"
            for p in projs:
                answer += f"  - {p.name} [{p.status}]\n"
            answer += "\n"
        sources = ["Portfólio Completo"]

    elif any(w in q for w in ["prazo", "deadline", "data", "entrega", "quando termina"]):
        answer = "📅 **Prazos dos Projetos:**\n\n"
        sorted_by_progress = sorted(projects, key=lambda x: x.progress)
        for p in sorted_by_progress:
            emoji = "✅" if p.status == "concluido" else "⚠️" if p.status == "atrasado" else "🔄"
            answer += f"{emoji} **{p.name}** — Prazo: {p.deadline or 'N/A'} | Progresso: {p.progress}%\n"
        sources = [p.code for p in sorted_by_progress]

    else:
        # Busca por nome de projeto
        matched = [p for p in projects if any(term in (p.name + " " + (p.description or "")).lower() for term in q.split())]
        if matched:
            answer = f"🔍 Encontrei **{len(matched)} projeto(s)** relacionado(s) à sua busca:\n\n"
            for p in matched:
                answer += f"• **{p.name}** ({p.code})\n"
                answer += f"  Status: {p.status} | Progresso: {p.progress}% | Gerente: {p.manager or 'N/A'}\n"
                if p.description:
                    answer += f"  📝 {p.description[:120]}...\n"
                answer += "\n"
            sources = [p.code for p in matched]
        else:
            answer = f"🤔 Analisei sua pergunta: *\"{query}\"*\n\n"
            answer += "Tente perguntar sobre:\n"
            answer += "• Projetos atrasados\n"
            answer += "• Orçamento total\n"
            answer += "• Riscos\n"
            answer += "• Prioridades críticas\n"
            answer += "• Resumo geral do portfólio\n"
            answer += "• Prazos e deadlines\n"
            answer += "• Gerentes responsáveis"
            sources = ["Portfólio Completo"]

    return schemas.AIResponse(answer=answer, sources=sources if sources else ["Portfólio Completo"])

# Seed de dados iniciais
@app.on_event("startup")
def seed_data():
    db = database.SessionLocal()
    try:
        if db.query(models.Project).count() == 0:
            seed_projects = [
                models.Project(code="PRJ-2026-001", name="Migração Cloud AWS", 
                    description="Migração de infraestrutura on-premise para AWS com foco em escalabilidade.",
                    status="em-andamento", priority="critica", manager="Ana Silva",
                    budget="R$ 1.200.000", progress=65, deadline="Nov/2026",
                    risks="Dependência de terceiros para descomissionamento de servidores legados"),
                models.Project(code="PRJ-2026-002", name="App Mobile Clientes",
                    description="Desenvolvimento de aplicativo mobile para autoatendimento com integração ao ERP.",
                    status="em-andamento", priority="alta", manager="Carlos Mendes",
                    budget="R$ 800.000", progress=45, deadline="Jan/2027",
                    risks="Prazo apertado para entrega antes da alta temporada"),
                models.Project(code="PRJ-2026-003", name="ERP Financeiro",
                    description="Implementação de módulo financeiro avançado com BI integrado.",
                    status="atrasado", priority="alta", manager="Mariana Costa",
                    budget="R$ 950.000", progress=30, deadline="Set/2026",
                    risks="Escopo crescente (scope creep) e falta de especialistas em BI"),
                models.Project(code="PRJ-2026-004", name="Cybersecurity Upgrade",
                    description="Modernização da arquitetura de segurança com SOC, SIEM e Zero Trust.",
                    status="em-andamento", priority="critica", manager="Roberto Lima",
                    budget="R$ 600.000", progress=80, deadline="Out/2026",
                    risks="Resistência cultural à adoção de novas políticas de acesso"),
                models.Project(code="PRJ-2026-005", name="Portal RH Digital",
                    description="Portal integrado para gestão de pessoas com onboarding digital.",
                    status="concluido", priority="media", manager="Fernanda Souza",
                    budget="R$ 350.000", progress=100, deadline="Ago/2026",
                    risks="Nenhum - projeto entregue com sucesso"),
                models.Project(code="PRJ-2026-006", name="Data Lake Analytics",
                    description="Construção de data lake para centralização de dados e análises preditivas.",
                    status="planejado", priority="alta", manager="Pedro Henrique",
                    budget="R$ 1.500.000", progress=5, deadline="Mar/2027",
                    risks="Qualidade inconsistente dos dados fonte de sistemas legados"),
                models.Project(code="PRJ-2026-007", name="Chatbot Atendimento",
                    description="Implementação de chatbot com NLP para atendimento ao cliente 24/7.",
                    status="concluido", priority="media", manager="Juliana Torres",
                    budget="R$ 280.000", progress=100, deadline="Jul/2026",
                    risks="Nenhum - projeto entregue com sucesso"),
                models.Project(code="PRJ-2026-008", name="Rede SD-WAN",
                    description="Substituição da rede MPLS por SD-WAN em todas as filiais.",
                    status="em-andamento", priority="alta", manager="Lucas Oliveira",
                    budget="R$ 720.000", progress=55, deadline="Dez/2026",
                    risks="Indisponibilidade temporária durante migração por filial"),
            ]
            db.add_all(seed_projects)
            db.commit()
            print("✅ Dados iniciais inseridos!")
    finally:
        db.close()

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)
