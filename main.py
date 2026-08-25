import os
from pathlib import Path
from fastapi import FastAPI, Depends, HTTPException
from fastapi.staticfiles import StaticFiles
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import HTMLResponse, RedirectResponse
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

# Caminho absoluto para a pasta static (resolve problemas de diretório no deploy)
BASE_DIR = Path(__file__).resolve().parent
STATIC_DIR = BASE_DIR / "static"

# Garantir que a pasta static existe
STATIC_DIR.mkdir(exist_ok=True)

# Se o index.html não existir na pasta static, criá-lo a partir do inline
INDEX_HTML_PATH = STATIC_DIR / "index.html"
if not INDEX_HTML_PATH.exists():
    # HTML embutido como fallback
    html_fallback = """<!DOCTYPE html>
<html lang="pt-BR">
<head>
<meta charset="UTF-8">
<meta name="viewport" content="width=device-width, initial-scale=1.0">
<title>PMO Portfolio Hub</title>
<style>
*{box-sizing:border-box;margin:0;padding:0}
body{font-family:Inter,system-ui,sans-serif;background:#f8fafc;color:#1e293b;min-height:100vh}
.header{background:linear-gradient(135deg,#6366f1 0%,#4f46e5 100%);color:#fff;padding:24px 32px;display:flex;justify-content:space-between;align-items:center;position:sticky;top:0;z-index:50;box-shadow:0 4px 20px rgba(99,102,241,0.3)}
.header h1{font-size:24px;font-weight:700}
.header p{opacity:.9;font-size:14px;margin-top:4px}
.btn{background:#fff;color:#6366f1;border:none;padding:10px 20px;border-radius:8px;font-weight:600;cursor:pointer;transition:all .2s;font-size:14px}
.btn:hover{transform:translateY(-1px);box-shadow:0 4px 12px rgba(0,0,0,.15)}
.container{padding:24px 32px;max-width:1400px;margin:0 auto}
.stats-grid{display:grid;grid-template-columns:repeat(4,1fr);gap:16px;margin-bottom:24px}
.stat-card{background:#fff;border-radius:12px;padding:20px;box-shadow:0 1px 3px rgba(0,0,0,.05);border:1px solid #e2e8f0}
.stat-card h3{font-size:12px;color:#64748b;text-transform:uppercase;letter-spacing:.5px}
.stat-card .value{font-size:32px;font-weight:700;margin-top:8px}
.stat-card .trend{font-size:13px;margin-top:4px}
.trend.up{color:#22c55e}.trend.down{color:#ef4444}.trend.neutral{color:#64748b}
.ai-search-section{background:linear-gradient(135deg,#1e1b4b 0%,#312e81 100%);border-radius:16px;padding:32px;margin-bottom:24px;color:#fff}
.ai-search-section h2{font-size:20px;margin-bottom:8px}
.ai-search-section p{opacity:.7;margin-bottom:20px;font-size:14px}
.search-box{display:flex;gap:12px;align-items:center}
.search-input{flex:1;background:rgba(255,255,255,.1);border:1px solid rgba(255,255,255,.2);border-radius:12px;padding:14px 20px;color:#fff;font-size:15px;outline:none}
.search-input::placeholder{color:rgba(255,255,255,.5)}
.search-btn{background:#6366f1;color:#fff;border:none;padding:14px 28px;border-radius:12px;font-weight:600;cursor:pointer;display:flex;align-items:center;gap:8px;font-size:14px}
.search-btn:hover{background:#4f46e5}
.search-btn:disabled{opacity:.6;cursor:not-allowed}
.ai-response{margin-top:20px;background:rgba(255,255,255,.05);border-radius:12px;padding:20px;display:none;border-left:3px solid #6366f1;animation:fadeIn .3s ease}
.ai-response.active{display:block}
.ai-response h4{font-size:14px;opacity:.7;margin-bottom:8px}
.ai-response p{opacity:1;line-height:1.7;white-space:pre-line}
.ai-sources{margin-top:12px;display:flex;gap:8px;flex-wrap:wrap}
.ai-source-tag{background:rgba(99,102,241,.3);padding:4px 12px;border-radius:20px;font-size:12px}
.section-header{display:flex;justify-content:space-between;align-items:center;margin-bottom:16px;flex-wrap:wrap;gap:12px}
.section-header h2{font-size:18px}
.filters{display:flex;gap:8px;flex-wrap:wrap}
.filter-btn{background:#fff;border:1px solid #e2e8f0;padding:8px 16px;border-radius:8px;font-size:13px;cursor:pointer;color:#64748b;transition:all .2s}
.filter-btn.active{background:#6366f1;color:#fff;border-color:#6366f1}
.filter-btn:hover:not(.active){background:#f8fafc}
.projects-grid{display:grid;grid-template-columns:repeat(3,1fr);gap:16px}
.project-card{background:#fff;border-radius:12px;padding:20px;border:1px solid #e2e8f0;transition:all .2s;cursor:pointer}
.project-card:hover{box-shadow:0 8px 24px rgba(0,0,0,.08);transform:translateY(-2px)}
.project-header{display:flex;justify-content:space-between;align-items:flex-start;margin-bottom:12px}
.project-code{background:#f8fafc;padding:4px 10px;border-radius:6px;font-size:12px;font-weight:600;color:#6366f1}
.status-badge{padding:4px 12px;border-radius:20px;font-size:12px;font-weight:500}
.status-em-andamento{background:#dbeafe;color:#1d4ed8}
.status-concluido{background:#dcfce7;color:#15803d}
.status-atrasado{background:#fee2e2;color:#b91c1c}
.status-planejado{background:#fef3c7;color:#b45309}
.project-card h3{font-size:16px;margin-bottom:8px}
.project-card p{font-size:13px;color:#64748b;line-height:1.5;margin-bottom:16px}
.project-meta{display:flex;justify-content:space-between;align-items:center;font-size:12px;color:#64748b}
.progress-bar{width:100%;height:6px;background:#f8fafc;border-radius:3px;margin-top:12px;overflow:hidden}
.progress-fill{height:100%;border-radius:3px;transition:width .5s ease}
.progress-fill.high{background:#22c55e}.progress-fill.medium{background:#f59e0b}.progress-fill.low{background:#ef4444}
.modal-overlay{position:fixed;top:0;left:0;right:0;bottom:0;background:rgba(0,0,0,.5);display:none;justify-content:center;align-items:center;z-index:100;padding:20px}
.modal-overlay.active{display:flex}
.modal{background:#fff;border-radius:16px;width:100%;max-width:600px;max-height:85vh;overflow-y:auto;padding:32px;animation:slideUp .3s ease}
.modal h2{margin-bottom:20px}
.form-group{margin-bottom:16px}
.form-group label{display:block;font-size:13px;font-weight:600;margin-bottom:6px;color:#64748b}
.form-group input,.form-group select,.form-group textarea{width:100%;padding:10px 14px;border:1px solid #e2e8f0;border-radius:8px;font-size:14px;outline:none;font-family:inherit}
.form-group input:focus,.form-group select:focus,.form-group textarea:focus{border-color:#6366f1;box-shadow:0 0 0 3px rgba(99,102,241,.1)}
.form-group textarea{min-height:80px;resize:vertical}
.form-row{display:grid;grid-template-columns:1fr 1fr;gap:16px}
.form-actions{display:flex;gap:12px;justify-content:flex-end;margin-top:24px}
.btn-secondary{background:#f8fafc;color:#1e293b}
.btn-primary{background:#6366f1;color:#fff}
.btn-danger{background:#fee2e2;color:#b91c1c}
.quick-questions{display:flex;gap:8px;margin-top:16px;flex-wrap:wrap}
.quick-q{background:rgba(255,255,255,.08);border:1px solid rgba(255,255,255,.15);color:#fff;padding:8px 16px;border-radius:20px;font-size:13px;cursor:pointer;transition:all .2s}
.quick-q:hover{background:rgba(255,255,255,.15)}
.loading-spinner{display:inline-block;width:16px;height:16px;border:2px solid rgba(255,255,255,.3);border-top-color:#fff;border-radius:50%;animation:spin .8s linear infinite}
.empty-state{text-align:center;padding:60px 20px;color:#64748b}
.empty-state h3{font-size:18px;margin-bottom:8px;color:#1e293b}
.toast{position:fixed;bottom:24px;right:24px;background:#1e293b;color:#fff;padding:14px 24px;border-radius:12px;font-size:14px;font-weight:500;z-index:200;transform:translateY(100px);opacity:0;transition:all .3s ease}
.toast.show{transform:translateY(0);opacity:1}
.toast.success{background:#22c55e}
.toast.error{background:#ef4444}
@keyframes fadeIn{from{opacity:0}to{opacity:1}}
@keyframes slideUp{from{transform:translateY(20px);opacity:0}to{transform:translateY(0);opacity:1}}
@keyframes spin{to{transform:rotate(360deg)}}
@media(max-width:1024px){.projects-grid{grid-template-columns:repeat(2,1fr)}.stats-grid{grid-template-columns:repeat(2,1fr)}}
@media(max-width:640px){.projects-grid{grid-template-columns:1fr}.stats-grid{grid-template-columns:1fr 1fr}.form-row{grid-template-columns:1fr}.header{flex-direction:column;gap:12px;text-align:center}.container{padding:16px}}
</style>
</head>
<body>
<div class="header"><div><h1>🏢 PMO Portfolio Hub</h1><p>Gerenciamento Inteligente de Projetos com IA</p></div><button class="btn" onclick="openModal()">+ Novo Projeto</button></div>
<div class="container">
<div class="stats-grid">
<div class="stat-card"><h3>Total de Projetos</h3><div class="value" id="stat-total">-</div><div class="trend neutral">Portfólio ativo</div></div>
<div class="stat-card"><h3>Em Andamento</h3><div class="value" id="stat-active">-</div><div class="trend up">Executando</div></div>
<div class="stat-card"><h3>Orçamento Total</h3><div class="value" id="stat-budget">-</div><div class="trend neutral">Investimento</div></div>
<div class="stat-card"><h3>Concluídos</h3><div class="value" id="stat-done">-</div><div class="trend up">Entregues</div></div>
</div>
<div class="ai-search-section">
<h2>🔍 Assistente IA do Portfólio</h2>
<p>Pergunte qualquer coisa sobre seus projetos: status, riscos, prazos, recursos, orçamento...</p>
<div class="search-box">
<input type="text" class="search-input" id="aiQuery" placeholder="Ex: Quais projetos estão atrasados?" onkeypress="if(event.key==='Enter') searchAI()">
<button class="search-btn" id="searchBtn" onclick="searchAI()"><span>⚡</span> Buscar com IA</button>
</div>
<div class="quick-questions">
<button class="quick-q" onclick="setQuery('Quais projetos estão atrasados?')">Projetos atrasados</button>
<button class="quick-q" onclick="setQuery('Qual o orçamento total do portfólio?')">Orçamento total</button>
<button class="quick-q" onclick="setQuery('Quais são os principais riscos?')">Principais riscos</button>
<button class="quick-q" onclick="setQuery('Resumo geral do portfólio')">Resumo geral</button>
<button class="quick-q" onclick="setQuery('Quem são os gerentes?')">Gerentes</button>
<button class="quick-q" onclick="setQuery('Prazos dos projetos')">Prazos</button>
</div>
<div class="ai-response" id="aiResponse">
<h4>🤖 Resposta da IA</h4>
<p id="aiResponseText"></p>
<div class="ai-sources" id="aiSources"></div>
</div>
</div>
<div class="section-header">
<h2>📁 Projetos do Portfólio</h2>
<div class="filters">
<button class="filter-btn active" onclick="filterProjects('todos')">Todos</button>
<button class="filter-btn" onclick="filterProjects('em-andamento')">Em Andamento</button>
<button class="filter-btn" onclick="filterProjects('concluido')">Concluídos</button>
<button class="filter-btn" onclick="filterProjects('atrasado')">Atrasados</button>
<button class="filter-btn" onclick="filterProjects('planejado')">Planejados</button>
</div>
</div>
<div class="projects-grid" id="projectsGrid"><div class="empty-state" style="grid-column:1/-1"><h3>Carregando projetos...</h3><p>Aguarde enquanto buscamos os dados do portfólio.</p></div></div>
</div>
<div class="modal-overlay" id="modal" onclick="if(event.target===this) closeModal()">
<div class="modal">
<h2 id="modalTitle">📝 Cadastrar Novo Projeto</h2>
<input type="hidden" id="projId">
<div class="form-group"><label>Código do Projeto</label><input type="text" id="projCode" placeholder="PRJ-2026-009"></div>
<div class="form-group"><label>Nome do Projeto *</label><input type="text" id="projName" placeholder="Nome do projeto"></div>
<div class="form-group"><label>Descrição</label><textarea id="projDesc" placeholder="Descreva o objetivo e escopo do projeto"></textarea></div>
<div class="form-row">
<div class="form-group"><label>Status</label><select id="projStatus"><option value="planejado">Planejado</option><option value="em-andamento">Em Andamento</option><option value="atrasado">Atrasado</option><option value="concluido">Concluído</option></select></div>
<div class="form-group"><label>Prioridade</label><select id="projPriority"><option value="baixa">Baixa</option><option value="media">Média</option><option value="alta">Alta</option><option value="critica">Crítica</option></select></div>
</div>
<div class="form-row">
<div class="form-group"><label>Gerente</label><input type="text" id="projManager" placeholder="Nome do gerente"></div>
<div class="form-group"><label>Orçamento (R$)</label><input type="text" id="projBudget" placeholder="500.000"></div>
</div>
<div class="form-row">
<div class="form-group"><label>Progresso (%)</label><input type="number" id="projProgress" min="0" max="100" value="0"></div>
<div class="form-group"><label>Prazo</label><input type="text" id="projDeadline" placeholder="Dez/2026"></div>
</div>
<div class="form-group"><label>Riscos Principais</label><textarea id="projRisks" placeholder="Liste os principais riscos do projeto"></textarea></div>
<div class="form-actions">
<button class="btn btn-danger" id="btnDelete" style="display:none;margin-right:auto;" onclick="deleteProject()">🗑️ Excluir</button>
<button class="btn btn-secondary" onclick="closeModal()">Cancelar</button>
<button class="btn btn-primary" onclick="saveProject()">Salvar Projeto</button>
</div>
</div>
</div>
<div class="toast" id="toast"></div>
<script>
const API_URL=window.location.origin;
let projects=[],currentFilter="todos",editingId=null;
async function loadProjects(){try{const url=currentFilter==="todos"?`${API_URL}/api/projects`:`${API_URL}/api/projects?status=${currentFilter}`;const res=await fetch(url);projects=await res.json();renderProjects();updateStats()}catch(err){console.error(err);document.getElementById("projectsGrid").innerHTML=`<div class="empty-state" style="grid-column:1/-1"><h3>⚠️ Erro ao carregar projetos</h3><p>Verifique se o servidor está rodando em ${API_URL}</p></div>`}}
function renderProjects(){const grid=document.getElementById("projectsGrid");if(projects.length===0){grid.innerHTML=`<div class="empty-state" style="grid-column:1/-1"><h3>Nenhum projeto encontrado</h3><p>Cadastre seu primeiro projeto clicando em "Novo Projeto".</p></div>`;return}grid.innerHTML=projects.map(p=>`<div class="project-card" onclick="editProject(${p.id})"><div class="project-header"><span class="project-code">${p.code||"N/A"}</span><span class="status-badge status-${p.status}">${formatStatus(p.status)}</span></div><h3>${p.name}</h3><p>${p.description||"Sem descrição"}</p><div class="project-meta"><span>👤 ${p.manager||"N/A"}</span><span>💰 ${p.budget||"N/A"}</span></div><div class="progress-bar"><div class="progress-fill ${p.progress>=70?"high":p.progress>=40?"medium":"low"}" style="width:${p.progress||0}%"></div></div><div class="project-meta" style="margin-top:8px"><span>📅 ${p.deadline||"N/A"}</span><span>${p.progress||0}%</span></div></div>`).join("")}
function formatStatus(s){const map={"em-andamento":"Em Andamento",concluido:"Concluído",atrasado:"Atrasado",planejado:"Planejado"};return map[s]||s}
function updateStats(){document.getElementById("stat-total").textContent=projects.length;document.getElementById("stat-active").textContent=projects.filter(p=>p.status==="em-andamento").length;document.getElementById("stat-done").textContent=projects.filter(p=>p.status==="concluido").length;const total=projects.reduce((sum,p)=>{const val=parseFloat((p.budget||"").replace(/[^0-9]/g,""));return sum+(isNaN(val)?0:val)},0);document.getElementById("stat-budget").textContent=total>0?`R$ ${(total/1e6).toFixed(1)}M`:"R$ 0"}
function filterProjects(status){currentFilter=status;document.querySelectorAll(".filter-btn").forEach(btn=>btn.classList.remove("active"));event.target.classList.add("active");loadProjects()}
function openModal(){editingId=null;document.getElementById("modalTitle").textContent="📝 Cadastrar Novo Projeto";document.getElementById("btnDelete").style.display="none";clearForm();document.getElementById("modal").classList.add("active")}
function closeModal(){document.getElementById("modal").classList.remove("active");editingId=null}
function clearForm(){document.getElementById("projId").value="";document.getElementById("projCode").value="";document.getElementById("projName").value="";document.getElementById("projDesc").value="";document.getElementById("projStatus").value="planejado";document.getElementById("projPriority").value="media";document.getElementById("projManager").value="";document.getElementById("projBudget").value="";document.getElementById("projProgress").value=0;document.getElementById("projDeadline").value="";document.getElementById("projRisks").value=""}
function editProject(id){const p=projects.find(proj=>proj.id===id);if(!p)return;editingId=id;document.getElementById("modalTitle").textContent="✏️ Editar Projeto";document.getElementById("btnDelete").style.display="block";document.getElementById("projCode").value=p.code||"";document.getElementById("projName").value=p.name||"";document.getElementById("projDesc").value=p.description||"";document.getElementById("projStatus").value=p.status||"planejado";document.getElementById("projPriority").value=p.priority||"media";document.getElementById("projManager").value=p.manager||"";document.getElementById("projBudget").value=(p.budget||"").replace(/[^0-9]/g,"");document.getElementById("projProgress").value=p.progress||0;document.getElementById("projDeadline").value=p.deadline||"";document.getElementById("projRisks").value=p.risks||"";document.getElementById("modal").classList.add("active")}
async function saveProject(){const name=document.getElementById("projName").value.trim();if(!name){showToast("Por favor, preencha o nome do projeto.","error");return}const budgetRaw=document.getElementById("projBudget").value.trim();const budget=budgetRaw?`R$ ${budgetRaw}`:null;const data={code:document.getElementById("projCode").value.trim()||`PRJ-${new Date().getFullYear()}-${String(projects.length+1).padStart(3,"0")}`,name:name,description:document.getElementById("projDesc").value.trim()||null,status:document.getElementById("projStatus").value,priority:document.getElementById("projPriority").value,manager:document.getElementById("projManager").value.trim()||null,budget:budget,progress:parseInt(document.getElementById("projProgress").value)||0,deadline:document.getElementById("projDeadline").value.trim()||null,risks:document.getElementById("projRisks").value.trim()||null};try{const url=editingId?`${API_URL}/api/projects/${editingId}`:`${API_URL}/api/projects`;const method=editingId?"PUT":"POST";const res=await fetch(url,{method:method,headers:{"Content-Type":"application/json"},body:JSON.stringify(data)});if(res.ok){showToast(editingId?"Projeto atualizado!":"Projeto cadastrado!","success");closeModal();loadProjects()}else{const err=await res.json();showToast(err.detail||"Erro ao salvar projeto.","error")}}catch(err){showToast("Erro de conexão com o servidor.","error")}}
async function deleteProject(){if(!editingId)return;if(!confirm("Tem certeza que deseja excluir este projeto?"))return;try{const res=await fetch(`${API_URL}/api/projects/${editingId}`,{method:"DELETE"});if(res.ok){showToast("Projeto excluído!","success");closeModal();loadProjects()}else{showToast("Erro ao excluir projeto.","error")}}catch(err){showToast("Erro de conexão.","error")}}
function setQuery(q){document.getElementById("aiQuery").value=q;searchAI()}
async function searchAI(){const query=document.getElementById("aiQuery").value.trim();const btn=document.getElementById("searchBtn");const responseDiv=document.getElementById("aiResponse");const responseText=document.getElementById("aiResponseText");const sourcesDiv=document.getElementById("aiSources");if(!query)return;btn.disabled=true;btn.innerHTML='<span class="loading-spinner"></span> Analisando...';responseDiv.classList.add("active");responseText.innerHTML="<em>🧠 A IA está analisando seu portfólio...</em>";sourcesDiv.innerHTML="";try{const res=await fetch(`${API_URL}/api/ai/search`,{method:"POST",headers:{"Content-Type":"application/json"},body:JSON.stringify({query:query})});const data=await res.json();responseText.innerHTML=data.answer.replace(/\n/g,"<br>");sourcesDiv.innerHTML=data.sources.map(s=>`<span class="ai-source-tag">📄 ${s}</span>`).join("")}catch(err){responseText.innerHTML="❌ Erro ao consultar a IA. Verifique se o servidor está online.";sourcesDiv.innerHTML=""}finally{btn.disabled=false;btn.innerHTML="<span>⚡</span> Buscar com IA"}}
function showToast(msg,type="success"){const toast=document.getElementById("toast");toast.textContent=msg;toast.className=`toast ${type} show`;setTimeout(()=>toast.classList.remove("show"),3000)}
loadProjects();
</script>
</body>
</html>"""
    INDEX_HTML_PATH.write_text(html_fallback, encoding="utf-8")

# Montar arquivos estáticos (usa o arquivo que acabamos de garantir que existe)
app.mount("/static", StaticFiles(directory=str(STATIC_DIR)), name="static")

@app.get("/")
def root():
    return RedirectResponse(url="/static/index.html")

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
    q = query

    if any(w in q for w in ["atrasado", "atrasados", "delay", "late"]):
        atrasados = [p for p in projects if p.status == "atrasado"]
        if not atrasados:
            answer = "✅ **Boa notícia!** Nenhum projeto está atrasado no momento."
        else:
            answer = f"⚠️ Encontrei **{len(atrasados)} projeto(s) atrasado(s)**:

"
            for p in atrasados:
                answer += f"• **{p.name}** ({p.code}) — Progresso: {p.progress}%, Gerente: {p.manager}
"
                answer += f"  🚨 Risco: {p.risks or 'Não informado'}

"
            answer += "💡 **Recomendação:** Priorizar ações corretivas e realocar recursos."
        sources = [p.code for p in atrasados]

    elif any(w in q for w in ["orçamento", "budget", "custo", "custo total", "investimento", "dinheiro", "valor"]):
        total = 0
        for p in projects:
            val = re.sub(r"[^0-9]", "", str(p.budget or "0"))
            total += int(val) if val else 0
        answer = f"💰 O **orçamento total do portfólio** é de **R$ {total/1_000_000:.1f} milhões** ({len(projects)} projetos).

"
        answer += "📊 **Maiores investimentos:**
"
        sorted_p = sorted(projects, key=lambda x: int(re.sub(r"[^0-9]", "", str(x.budget or "0")) or 0), reverse=True)
        for p in sorted_p[:5]:
            answer += f"• {p.name}: {p.budget or 'N/A'}
"
        sources = ["Portfólio Completo"]

    elif any(w in q for w in ["risco", "riscos", "problema", "problemas", "alerta"]):
        with_risks = [p for p in projects if p.risks and "nenhum" not in p.risks.lower()]
        answer = f"🚨 Identifiquei **{len(with_risks)} projetos com riscos ativos**:

"
        for p in with_risks:
            answer += f"• **{p.name}** ({p.code}) — {p.risks}
"
        sources = [p.code for p in with_risks]

    elif any(w in q for w in ["prioridade", "prioritário", "critico", "crítico", "urgente"]):
        criticos = [p for p in projects if p.priority in ["critica", "critico", "crítica", "crítico"]]
        answer = f"🔴 Existem **{len(criticos)} projetos de prioridade crítica**:

"
        for p in criticos:
            answer += f"• **{p.name}** ({p.code}) — {p.progress}% concluído, prazo: {p.deadline or 'N/A'}
"
        if criticos:
            answer += "
💡 **Recomendação:** Manter foco e alocação de recursos nesses projetos."
        sources = [p.code for p in criticos]

    elif any(w in q for w in ["resumo", "status", "andamento", "visão geral", "overview", "dashboard", "portfólio"]):
        answer = f"📊 **Resumo do Portfólio** ({len(projects)} projetos):

"
        em_andamento = len([p for p in projects if p.status == "em-andamento"])
        concluidos = len([p for p in projects if p.status == "concluido"])
        atrasados = len([p for p in projects if p.status == "atrasado"])
        planejados = len([p for p in projects if p.status == "planejado"])
        avg_progress = sum(p.progress for p in projects) // len(projects) if projects else 0

        answer += f"✅ Concluídos: {concluidos}
"
        answer += f"🔄 Em Andamento: {em_andamento}
"
        answer += f"⚠️ Atrasados: {atrasados}
"
        answer += f"📋 Planejados: {planejados}

"
        answer += f"📈 **Progresso médio:** {avg_progress}%"
        sources = ["Portfólio Completo"]

    elif any(w in q for w in ["gerente", "responsável", "lider", "líder", "quem gerencia"]):
        answer = "👥 **Gerentes de Projetos:**

"
        managers = {}
        for p in projects:
            m = p.manager or "Não atribuído"
            if m not in managers:
                managers[m] = []
            managers[m].append(p)
        for m, projs in managers.items():
            answer += f"• **{m}** ({len(projs)} projeto(s)):
"
            for p in projs:
                answer += f"  - {p.name} [{p.status}]
"
            answer += "
"
        sources = ["Portfólio Completo"]

    elif any(w in q for w in ["prazo", "deadline", "data", "entrega", "quando termina"]):
        answer = "📅 **Prazos dos Projetos:**

"
        sorted_by_progress = sorted(projects, key=lambda x: x.progress)
        for p in sorted_by_progress:
            emoji = "✅" if p.status == "concluido" else "⚠️" if p.status == "atrasado" else "🔄"
            answer += f"{emoji} **{p.name}** — Prazo: {p.deadline or 'N/A'} | Progresso: {p.progress}%
"
        sources = [p.code for p in sorted_by_progress]

    else:
        matched = [p for p in projects if any(term in (p.name + " " + (p.description or "")).lower() for term in q.split())]
        if matched:
            answer = f"🔍 Encontrei **{len(matched)} projeto(s)** relacionado(s) à sua busca:

"
            for p in matched:
                answer += f"• **{p.name}** ({p.code})
"
                answer += f"  Status: {p.status} | Progresso: {p.progress}% | Gerente: {p.manager or 'N/A'}
"
                if p.description:
                    answer += f"  📝 {p.description[:120]}...
"
                answer += "
"
            sources = [p.code for p in matched]
        else:
            answer = f"🤔 Analisei sua pergunta: *\"{query}\"*

"
            answer += "Tente perguntar sobre:
"
            answer += "• Projetos atrasados
"
            answer += "• Orçamento total
"
            answer += "• Riscos
"
            answer += "• Prioridades críticas
"
            answer += "• Resumo geral do portfólio
"
            answer += "• Prazos e deadlines
"
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
