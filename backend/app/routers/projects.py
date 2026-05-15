from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select, func
from typing import List
from app.database import get_db
from app.models.user import User
from app.models.project import Project
from app.models.document import Document
from app.models.chat import Chat
from app.schemas.project import ProjectResponse, ProjectCreate
from app.utils.auth import get_current_user, get_admin_user
from app.rag.vector_store import delete_project_collection

router = APIRouter(prefix="/projects", tags=["Projects"])


@router.get("", response_model=List[ProjectResponse])
async def list_projects(
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
):
    """
    List all projects - accessible by both admin and users
    Admin sees all projects, users see only their own
    """
    if current_user.role.value == "admin":
        # Admin sees all projects
        result = await db.execute(
            select(Project).order_by(Project.created_at.desc())
        )
    else:
        # Regular users see only their projects
        result = await db.execute(
            select(Project).where(Project.created_by == current_user.id).order_by(Project.created_at.desc())
        )
    
    projects = result.scalars().all()

    response = []
    for project in projects:
        doc_count = await db.scalar(
            select(func.count(Document.id)).where(Document.project_id == project.id)
        )
        chat_count = await db.scalar(
            select(func.count(Chat.id)).where(Chat.project_id == project.id)
        )
        response.append(ProjectResponse(
            id=project.id,
            name=project.name,
            description=project.description,
            created_by=project.created_by,
            created_at=project.created_at,
            document_count=doc_count or 0,
            chat_count=chat_count or 0,
        ))
    return response


@router.post("", response_model=ProjectResponse, status_code=status.HTTP_201_CREATED)
async def create_project(
    project_data: ProjectCreate,
    current_user: User = Depends(get_admin_user),  # Only admin can create
    db: AsyncSession = Depends(get_db),
):
    """
    Create a new project - ADMIN ONLY
    """
    project = Project(
        name=project_data.name,
        description=project_data.description,
        created_by=current_user.id,
    )
    db.add(project)
    await db.commit()
    await db.refresh(project)
    return ProjectResponse(
        id=project.id,
        name=project.name,
        description=project.description,
        created_by=project.created_by,
        created_at=project.created_at,
        document_count=0,
        chat_count=0,
    )


@router.get("/{project_id}", response_model=ProjectResponse)
async def get_project(
    project_id: int,
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
):
    """
    Get a specific project - accessible by both admin and users
    """
    if current_user.role.value == "admin":
        # Admin can access any project
        result = await db.execute(
            select(Project).where(Project.id == project_id)
        )
    else:
        # Regular users can only access their own projects
        result = await db.execute(
            select(Project).where(Project.id == project_id, Project.created_by == current_user.id)
        )
    
    project = result.scalar_one_or_none()
    if not project:
        raise HTTPException(status_code=404, detail="Project not found")

    doc_count = await db.scalar(
        select(func.count(Document.id)).where(Document.project_id == project.id)
    )
    chat_count = await db.scalar(
        select(func.count(Chat.id)).where(Chat.project_id == project.id)
    )
    return ProjectResponse(
        id=project.id,
        name=project.name,
        description=project.description,
        created_by=project.created_by,
        created_at=project.created_at,
        document_count=doc_count or 0,
        chat_count=chat_count or 0,
    )


@router.delete("/{project_id}", status_code=status.HTTP_204_NO_CONTENT)
async def delete_project(
    project_id: int,
    current_user: User = Depends(get_admin_user),  # Only admin can delete
    db: AsyncSession = Depends(get_db),
):
    """
    Delete a project - ADMIN ONLY
    """
    result = await db.execute(
        select(Project).where(Project.id == project_id)
    )
    project = result.scalar_one_or_none()
    if not project:
        raise HTTPException(status_code=404, detail="Project not found")

    # Delete ChromaDB collection for this project
    delete_project_collection(project_id)

    await db.delete(project)
    await db.commit()
