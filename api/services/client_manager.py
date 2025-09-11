from typing import Dict, Any, List
from datetime import datetime
from sqlalchemy import select, update, func
from sqlalchemy.orm import selectinload

from core.config import settings
from core.database import async_session, Client, Project, QASession, WebAnalysis
from models.client import (
    ClientCreate,
    ClientResponse,
    ProjectCreate,
    ProjectResponse,
    QASessionCreate,
    QASessionResponse,
)
import structlog

logger = structlog.get_logger()


class ClientManager:
    """Service for managing clients, projects, and Q&A sessions"""

    def __init__(self):
        pass

    async def create_client(self, client_data: ClientCreate) -> ClientResponse:
        """Create a new client"""
        logger.info("Creating new client", email=client_data.email)

        try:
            async with async_session() as session:
                # Check if client already exists
                existing = await session.execute(
                    select(Client).where(Client.email == client_data.email)
                )
                if existing.scalar_one_or_none():
                    raise ValueError(
                        f"Client with email {client_data.email} already exists"
                    )

                # Create new client
                client = Client(
                    name=client_data.name,
                    email=client_data.email,
                    company=client_data.company,
                    website=client_data.website,
                    phone=client_data.phone,
                    industry=client_data.industry,
                    description=client_data.description,
                    twitter_handle=client_data.twitter_handle,
                    instagram_handle=client_data.instagram_handle,
                    linkedin_profile=client_data.linkedin_profile,
                )

                session.add(client)
                await session.commit()
                await session.refresh(client)

                logger.info("Client created successfully", client_id=client.id)
                return ClientResponse.model_validate(client)

        except Exception as e:
            logger.error("Failed to create client", error=str(e))
            raise

    async def get_client(self, client_id: int) -> ClientResponse:
        """Get client by ID"""
        async with async_session() as session:
            result = await session.execute(select(Client).where(Client.id == client_id))
            client = result.scalar_one_or_none()

            if not client:
                raise ValueError("Client not found")

            return ClientResponse.model_validate(client)

    async def get_all_clients(self) -> List[ClientResponse]:
        """Get all clients"""
        async with async_session() as session:
            result = await session.execute(select(Client))
            clients = result.scalars().all()

            return [ClientResponse.model_validate(client) for client in clients]

    async def update_client(
        self, client_id: int, updates: Dict[str, Any]
    ) -> ClientResponse:
        """Update client information"""
        logger.info("Updating client", client_id=client_id)

        async with async_session() as session:
            stmt = update(Client).where(Client.id == client_id).values(**updates)
            await session.execute(stmt)
            await session.commit()

            # Return updated client
            return await self.get_client(client_id)

    # ===== PROJECT MANAGEMENT =====

    async def create_project(self, project_data: ProjectCreate) -> ProjectResponse:
        """Create a new AI assistant project"""
        logger.info("Creating new project", client_id=project_data.client_id)

        try:
            async with async_session() as session:
                # Verify client exists
                client_result = await session.execute(
                    select(Client).where(Client.id == project_data.client_id)
                )
                if not client_result.scalar_one_or_none():
                    raise ValueError("Client not found")

                # Create project
                project = Project(
                    client_id=project_data.client_id,
                    name=project_data.name,
                    description=project_data.description,
                    assistant_type=project_data.assistant_type,
                    complexity=project_data.complexity,
                    status="pending",
                    progress=0,
                )

                session.add(project)
                await session.commit()
                await session.refresh(project)

                logger.info("Project created successfully", project_id=project.id)
                return ProjectResponse.model_validate(project)

        except Exception as e:
            logger.error("Failed to create project", error=str(e))
            raise

    async def get_client_projects(self, client_id: int) -> List[ProjectResponse]:
        """Get all projects for a client"""
        async with async_session() as session:
            result = await session.execute(
                select(Project).where(Project.client_id == client_id)
            )
            projects = result.scalars().all()

            return [ProjectResponse.model_validate(project) for project in projects]

    async def get_project(self, project_id: int) -> ProjectResponse:
        """Get project by ID"""
        async with async_session() as session:
            result = await session.execute(
                select(Project).where(Project.id == project_id)
            )
            project = result.scalar_one_or_none()

            if not project:
                raise ValueError("Project not found")

            return ProjectResponse.model_validate(project)

    async def update_project_status(
        self, project_id: int, status: str, progress: int = None
    ):
        """Update project status and progress"""
        updates = {"status": status}
        if progress is not None:
            updates["progress"] = progress
        if status == "completed":
            updates["completed_at"] = datetime.utcnow()

        async with async_session() as session:
            stmt = update(Project).where(Project.id == project_id).values(**updates)
            await session.execute(stmt)
            await session.commit()

    # ===== Q&A SESSION MANAGEMENT =====

    async def create_qa_session(
        self, client_id: int, session_name: str = None
    ) -> QASessionResponse:
        """Create a new Q&A session"""
        logger.info("Creating Q&A session", client_id=client_id)

        try:
            async with async_session() as session:
                # Verify client exists
                client_result = await session.execute(
                    select(Client).where(Client.id == client_id)
                )
                if not client_result.scalar_one_or_none():
                    raise ValueError("Client not found")

                # Create Q&A session
                qa_session = QASession(
                    client_id=client_id,
                    session_name=session_name
                    or f"Session {datetime.now().strftime('%Y-%m-%d %H:%M')}",
                    status="active",
                    questions_answers=[],
                )

                session.add(qa_session)
                await session.commit()
                await session.refresh(qa_session)

                logger.info("Q&A session created", session_id=qa_session.id)
                return QASessionResponse.model_validate(qa_session)

        except Exception as e:
            logger.error("Failed to create Q&A session", error=str(e))
            raise

    async def record_qa(
        self, session_id: int, question: str, answer: str
    ) -> Dict[str, Any]:
        """Record a question and answer in the session"""
        logger.info("Recording Q&A", session_id=session_id)

        try:
            async with async_session() as session:
                # Get session
                result = await session.execute(
                    select(QASession).where(QASession.id == session_id)
                )
                qa_session = result.scalar_one_or_none()

                if not qa_session:
                    raise ValueError("Q&A session not found")

                # Add new Q&A pair
                qa_pair = {
                    "question": question,
                    "answer": answer,
                    "timestamp": datetime.utcnow().isoformat(),
                }

                current_qa = qa_session.questions_answers or []
                current_qa.append(qa_pair)

                # Update session
                stmt = (
                    update(QASession)
                    .where(QASession.id == session_id)
                    .values(questions_answers=current_qa)
                )
                await session.execute(stmt)
                await session.commit()

                logger.info("Q&A recorded successfully", session_id=session_id)
                return {"message": "Q&A recorded", "total_pairs": len(current_qa)}

        except Exception as e:
            logger.error("Failed to record Q&A", error=str(e))
            raise

    async def get_qa_session(self, session_id: int) -> QASessionResponse:
        """Get Q&A session by ID"""
        async with async_session() as session:
            result = await session.execute(
                select(QASession).where(QASession.id == session_id)
            )
            qa_session = result.scalar_one_or_none()

            if not qa_session:
                raise ValueError("Q&A session not found")

            return QASessionResponse.model_validate(qa_session)

    async def complete_qa_session(self, session_id: int) -> QASessionResponse:
        """Mark Q&A session as completed and generate insights"""
        logger.info("Completing Q&A session", session_id=session_id)

        try:
            async with async_session() as session:
                # Get session
                result = await session.execute(
                    select(QASession).where(QASession.id == session_id)
                )
                qa_session = result.scalar_one_or_none()

                if not qa_session:
                    raise ValueError("Q&A session not found")

                # Generate insights from Q&A data
                insights = await self._generate_qa_insights(
                    qa_session.questions_answers
                )

                # Update session
                stmt = (
                    update(QASession)
                    .where(QASession.id == session_id)
                    .values(
                        status="completed",
                        completed_at=datetime.utcnow(),
                        insights=insights,
                    )
                )
                await session.execute(stmt)
                await session.commit()

                return await self.get_qa_session(session_id)

        except Exception as e:
            logger.error("Failed to complete Q&A session", error=str(e))
            raise

    async def _generate_qa_insights(
        self, qa_pairs: List[Dict[str, Any]]
    ) -> Dict[str, Any]:
        """Generate insights from Q&A session data"""
        if not qa_pairs:
            return {"message": "No Q&A data to analyze"}

        # Basic analysis
        insights = {
            "total_questions": len(qa_pairs),
            "session_duration": "Calculated from timestamps",
            "common_topics": [],
            "client_concerns": [],
            "business_requirements": [],
            "recommended_features": [],
        }

        # Analyze question patterns
        questions = [qa["question"].lower() for qa in qa_pairs]

        # Simple keyword analysis
        business_keywords = [
            "hours",
            "pricing",
            "cost",
            "payment",
            "service",
            "product",
        ]
        technical_keywords = ["integration", "api", "website", "app", "mobile"]
        support_keywords = ["help", "support", "contact", "problem", "issue"]

        for keyword in business_keywords:
            if any(keyword in q for q in questions):
                insights["business_requirements"].append(
                    f"Client asked about {keyword}"
                )

        for keyword in technical_keywords:
            if any(keyword in q for q in questions):
                insights["recommended_features"].append(
                    f"Consider {keyword} capabilities"
                )

        for keyword in support_keywords:
            if any(keyword in q for q in questions):
                insights["client_concerns"].append(
                    f"Support-related inquiry about {keyword}"
                )

        return insights

    # ===== ANALYTICS AND STATS =====

    async def get_active_projects_count(self) -> int:
        """Get count of active projects"""
        async with async_session() as session:
            result = await session.execute(
                select(func.count(Project.id)).where(
                    Project.status.in_(
                        ["pending", "analyzing", "generating", "coding", "configuring"]
                    )
                )
            )
            return result.scalar() or 0

    async def get_total_clients_count(self) -> int:
        """Get total number of clients"""
        async with async_session() as session:
            result = await session.execute(select(func.count(Client.id)))
            return result.scalar() or 0

    async def get_completed_projects_count(self) -> int:
        """Get count of completed projects"""
        async with async_session() as session:
            result = await session.execute(
                select(func.count(Project.id)).where(Project.status == "completed")
            )
            return result.scalar() or 0

    async def get_client_analytics(self, client_id: int) -> Dict[str, Any]:
        """Get analytics for a specific client"""
        async with async_session() as session:
            # Get client projects
            projects_result = await session.execute(
                select(Project).where(Project.client_id == client_id)
            )
            projects = projects_result.scalars().all()

            # Get Q&A sessions
            qa_result = await session.execute(
                select(QASession).where(QASession.client_id == client_id)
            )
            qa_sessions = qa_result.scalars().all()

            # Get web analyses
            analysis_result = await session.execute(
                select(WebAnalysis).where(WebAnalysis.client_id == client_id)
            )
            analyses = analysis_result.scalars().all()

            return {
                "total_projects": len(projects),
                "completed_projects": len(
                    [p for p in projects if p.status == "completed"]
                ),
                "active_projects": len(
                    [p for p in projects if p.status not in ["completed", "failed"]]
                ),
                "qa_sessions": len(qa_sessions),
                "web_analyses": len(analyses),
                "project_types": list(set(p.assistant_type for p in projects)),
                "last_activity": (
                    max([p.created_at for p in projects]) if projects else None
                ),
            }
