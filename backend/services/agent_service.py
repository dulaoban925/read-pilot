"""
Parlant Agent management service
"""
# NOTE: Parlant 3.0 uses a different API structure (client-server)
# For now, we'll initialize in stub mode to allow backend to start
# TODO: Update to use parlant.client.ParlantClient when ready

from typing import Dict, Optional
from config import settings


class AgentService:
    """Service for managing Parlant agents"""

    def __init__(self):
        self.client: Optional[any] = None
        self.agents: Dict = {}

    async def initialize(self):
        """Initialize Parlant server and all agents"""
        try:
            # TODO: Initialize Parlant 3.0 client
            # from parlant.client import ParlantClient
            # self.client = ParlantClient(
            #     base_url=f"http://{settings.PARLANT_SERVER_HOST}:{settings.PARLANT_SERVER_PORT}"
            # )

            print("⚠️  Parlant agents temporarily disabled (stub mode)")
            print("   TODO: Update agent implementation for Parlant 3.0 API")

            return True

        except Exception as e:
            print(f"❌ Failed to initialize agents: {str(e)}")
            return False

    async def get_or_create_session(self, user_id: str, document_id: Optional[str] = None):
        """Get or create a Parlant session for a user"""
        # TODO: Implement session management
        # This should map user_id to Parlant session_id
        # For now, return a placeholder
        pass

    async def send_message(
        self,
        user_id: str,
        message: str,
        document_id: Optional[str] = None,
        context: Optional[Dict] = None
    ) -> Dict:
        """
        Send a message to the coordinator agent

        Args:
            user_id: User identifier
            message: User message
            document_id: Optional document context
            context: Optional additional context

        Returns:
            Agent response
        """
        if not self.server or not self.agents:
            raise RuntimeError("Agents not initialized. Call initialize() first.")

        try:
            # Get coordinator agent
            coordinator = self.agents["coordinator"]

            # Create or get session
            session = await self.get_or_create_session(user_id, document_id)

            # Build context
            message_context = context or {}
            message_context.update({
                "user_id": user_id,
                "document_id": document_id
            })

            # Send message to coordinator
            # response = await coordinator.send_message(
            #     session_id=session.id,
            #     message=message,
            #     context=message_context
            # )

            # Placeholder response
            response = {
                "agent": "coordinator",
                "message": "This is a placeholder response. Implement actual Parlant integration.",
                "metadata": {}
            }

            return response

        except Exception as e:
            print(f"Failed to send message: {str(e)}")
            raise

    async def shutdown(self):
        """Shutdown Parlant server"""
        if self.server:
            await self.server.shutdown()
            print("✅ Parlant server shutdown complete")


# Global agent service instance
agent_service = AgentService()
