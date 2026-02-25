"""
agent_router.py - Agentic Tool Calling Endpoint
Natural language queries powered by Groq + Llama
"""

from fastapi import APIRouter, Depends
from pydantic import BaseModel
from groq import Groq
import json
import structlog
from app.config import settings
from app.models import fake_users_db
from app.dependencies import require_user
from app.models import User

logger = structlog.get_logger("app.agent")

router = APIRouter(prefix="/agent", tags=["Agent"])

client = Groq(api_key=settings.groq_api_key)


class AgentQuery(BaseModel):
    question: str


tools = [
    {
        "type": "function",
        "function": {
            "name": "get_user_info",
            "description": "Get information about a specific user by username",
            "parameters": {
                "type": "object",
                "properties": {
                    "username": {
                        "type": "string",
                        "description": "The username to look up"
                    }
                },
                "required": ["username"]
            }
        }
    },
    {
        "type": "function",
        "function": {
            "name": "count_users",
            "description": "Count the total number of registered users",
            "parameters": {
                "type": "object",
                "properties": {},
                "required": []
            }
        }
    },
    {
        "type": "function",
        "function": {
            "name": "check_user_role",
            "description": "Check if a specific user has a specific role",
            "parameters": {
                "type": "object",
                "properties": {
                    "username": {
                        "type": "string",
                        "description": "The username to look up"
                    },
                    "role": {
                        "type": "string",
                        "description": "The role to check for: admin, user, or moderator"
                    }
                },
                "required": ["username", "role"]
            }
        }
    }
]


def execute_tool(tool_name: str, tool_args: dict) -> str:
    if tool_name == "get_user_info":
        username = tool_args.get("username")
        user = fake_users_db.get(username)
        if not user:
            return json.dumps({"error": f"User {username} not found"})
        return json.dumps({
            "username": user.username,
            "email": user.email,
            "role": user.role.value,
            "is_active": user.is_active
        })

    elif tool_name == "count_users":
        return json.dumps({"total_users": len(fake_users_db)})

    elif tool_name == "check_user_role":
        username = tool_args.get("username")
        role = tool_args.get("role")
        user = fake_users_db.get(username)
        if not user:
            return json.dumps({"error": f"User {username} not found"})
        has_role = user.role.value == role
        return json.dumps({
            "username": username,
            "role_checked": role,
            "has_role": has_role
        })

    return json.dumps({"error": f"Unknown tool: {tool_name}"})


@router.post("/query")
async def agent_query(
    query: AgentQuery,
    current_user: User = Depends(require_user)
):
    logger.info("agent_query_received",
                question=query.question,
                user=current_user.username)

    messages = [
        {
            "role": "system",
            "content": "You are a helpful assistant for a user management system. Use the available tools to answer questions accurately."
        },
        {
            "role": "user",
            "content": query.question
        }
    ]

    response = client.chat.completions.create(
        model=settings.groq_model,
        messages=messages,
        tools=tools,
        tool_choice="auto"
    )

    response_message = response.choices[0].message

    if response_message.tool_calls:
        messages.append(response_message)

        for tool_call in response_message.tool_calls:
            tool_name = tool_call.function.name
            tool_args = json.loads(tool_call.function.arguments)

            logger.info("tool_called",
                       tool=tool_name,
                       args=tool_args)

            result = execute_tool(tool_name, tool_args)

            messages.append({
                "role": "tool",
                "tool_call_id": tool_call.id,
                "content": result
            })

        final_response = client.chat.completions.create(
            model=settings.groq_model,
            messages=messages,
            tools=tools,
        )

        answer = final_response.choices[0].message.content

    else:
        answer = response_message.content

    logger.info("agent_query_answered",
                user=current_user.username,
                answer=answer)

    return {"question": query.question, "answer": answer}