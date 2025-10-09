async def handle_mcp_request(request_data: dict, user_profile: dict) -> dict:
    """Handle MCP JSON-RPC requests with user profile data"""
    
    method = request_data.get("method")
    request_id = request_data.get("id")
    
    if method == "initialize":
        return {
            "jsonrpc": "2.0",
            "id": request_id,
            "result": {
                "protocolVersion": "2025-06-18",
                "capabilities": {"tools": {}, "resources": {}},
                "serverInfo": {
                    "name": f"vocalaa-{user_profile['mcp_slug']}",
                    "version": "0.1.0"
                },
                "instructions": "This server provides professional information and background."
            }
        }
    
    elif method == "tools/list":
        tools = [
            {
                "name": "get_basic_info",
                "description": "Get basic personal information and contact details",
                "inputSchema": {"type": "object", "properties": {}, "additionalProperties": False}
            },
            {
                "name": "get_work_experience",
                "description": "Get professional work history and achievements",
                "inputSchema": {"type": "object", "properties": {}, "additionalProperties": False}
            },
            {
                "name": "get_skills",
                "description": "Get technical and soft skills",
                "inputSchema": {"type": "object", "properties": {}, "additionalProperties": False}
            },
            {
                "name": "get_projects",
                "description": "Get portfolio projects and demonstrations",
                "inputSchema": {"type": "object", "properties": {}, "additionalProperties": False}
            },
            {
                "name": "get_education",
                "description": "Get educational background and qualifications",
                "inputSchema": {"type": "object", "properties": {}, "additionalProperties": False}
            }
        ]
        
        return {
            "jsonrpc": "2.0",
            "id": request_id,
            "result": {"tools": tools}
        }
    
    elif method == "tools/call":
        tool_name = request_data.get("params", {}).get("name")
        return await handle_tool_call(tool_name, user_profile, request_id)
    
    else:
        return {
            "jsonrpc": "2.0", 
            "id": request_id,
            "error": {"code": -32601, "message": f"Method not found: {method}"}
        }
async def handle_tool_call(tool_name: str, user_profile: dict, request_id: int) -> dict:
    """Execute MCP tool calls with user profile data"""
    
    try:
        if tool_name == "get_basic_info":
            basic_info = user_profile.get("basic_info", {})
            response_text = f"""**{basic_info.get('name', 'Name not set')}**
{basic_info.get('title', 'Title not set')}
📍 {basic_info.get('location', 'Location not set')}

**Contact:**
📧 {basic_info.get('email', 'Email not set')}

**Summary:**
{basic_info.get('summary', 'Summary not set')}"""

        elif tool_name == "get_work_experience":
            work_exp = user_profile.get("work_experience", [])
            if not work_exp:
                response_text = "No work experience data available."
            else:
                response_text = "**Professional Experience:**\n\n"
                for job in work_exp:
                    response_text += f"**{job.get('role')}** at **{job.get('company')}**\n"
                    response_text += f"📅 {job.get('duration')}\n\n"
                    response_text += f"{job.get('description')}\n\n"
                    
                    if job.get('achievements'):
                        response_text += "**Key Achievements:**\n"
                        for achievement in job['achievements']:
                            response_text += f"• {achievement}\n"
                        response_text += "\n"
                    
                    response_text += "---\n\n"

        elif tool_name == "get_skills":
            skills = user_profile.get("skills", {})
            if not skills:
                response_text = "No skills data available."
            else:
                response_text = "**Technical & Professional Skills:**\n\n"
                for category, skill_list in skills.items():
                    if skill_list:
                        category_name = category.replace('_', ' ').title()
                        response_text += f"**{category_name}:**\n"
                        if isinstance(skill_list, list):
                            response_text += f"{', '.join(skill_list)}\n\n"

        elif tool_name == "get_projects":
            projects = user_profile.get("projects", [])
            if not projects:
                response_text = "No projects data available."
            else:
                response_text = "**Portfolio Projects:**\n\n"
                for project in projects:
                    response_text += f"**{project.get('name', 'Untitled Project')}**\n"
                    response_text += f"{project.get('description', 'No description provided.')}\n\n"

                    if project.get('technologies'):
                        response_text += "**Technologies:**\n"
                        if isinstance(project['technologies'], list):
                            response_text += f"{', '.join(project['technologies'])}\n"
                        response_text += "\n"

                    if project.get('github_url'):
                        response_text += f"🔗 GitHub: {project['github_url']}\n"

                    if project.get('demo_url'):
                        response_text += f"🌐 Demo: {project['demo_url']}\n"

                    response_text += "\n---\n\n"

        elif tool_name == "get_education":
            education = user_profile.get("education", [])
            if not education:
                response_text = "No education data available."
            else:
                response_text = "**Education Background:**\n\n"
                for edu in education:
                    response_text += f"**{edu.get('degree', 'Degree not specified')}** in **{edu.get('field', 'Field not specified')}**\n"
                    response_text += f"🎓 {edu.get('institution', 'Institution not specified')}\n"

                    if edu.get('graduation_year'):
                        response_text += f"📅 Graduated: {edu['graduation_year']}\n"

                    response_text += "\n---\n\n"

        else:
            return {
                "jsonrpc": "2.0",
                "id": request_id,
                "error": {"code": -32601, "message": f"Unknown tool: {tool_name}"}
            }

        return {
            "jsonrpc": "2.0",
            "id": request_id,
            "result": {
                "content": [{
                    "type": "text",
                    "text": response_text
                }]
            }
        }
        
    except Exception as e:
        return {
            "jsonrpc": "2.0",
            "id": request_id,
            "error": {"code": -32603, "message": str(e)}
        }
