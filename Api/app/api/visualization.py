from fastapi import APIRouter, Request
from fastapi.responses import HTMLResponse
import os

router = APIRouter()

@router.get("/edr", response_class=HTMLResponse)
async def show_edr(request: Request):
    # Read the EDR HTML content
    try:
        with open("EDR2.html", "r", encoding="utf-8") as file:
            html_content = file.read()
    except FileNotFoundError:
        # Return a simple HTML response if file doesn't exist
        html_content = """
        <!DOCTYPE html>
        <html>
        <head>
            <title>EDR System</title>
            <style>
                body { font-family: Arial, sans-serif; padding: 20px; }
                .container { max-width: 800px; margin: 0 auto; }
            </style>
        </head>
        <body>
            <div class="container">
                <h1>EDR System Visualization</h1>
                <p>EDR2.html file not found. Please ensure it exists in the project root.</p>
                <p>You can access the API documentation at: <a href="/docs">/docs</a></p>
            </div>
        </body>
        </html>
        """
    
    return HTMLResponse(content=html_content)

@router.get("/edr/view")
async def view_edr(request: Request):
    # Simple HTML response without Jinja2 templates
    html_content = """
    <!DOCTYPE html>
    <html lang="en">
    <head>
        <meta charset="UTF-8">
        <meta name="viewport" content="width=device-width, initial-scale=1.0">
        <title>EDR System</title>
        <style>
            body {
                font-family: Arial, sans-serif;
                margin: 0;
                padding: 20px;
                background-color: #f5f5f5;
            }
            .container {
                max-width: 1200px;
                margin: 0 auto;
                background-color: white;
                padding: 30px;
                border-radius: 10px;
                box-shadow: 0 0 10px rgba(0,0,0,0.1);
            }
            h1 {
                color: #333;
                text-align: center;
                margin-bottom: 30px;
            }
            .entities {
                display: grid;
                grid-template-columns: repeat(auto-fit, minmax(300px, 1fr));
                gap: 20px;
                margin-bottom: 40px;
            }
            .entity {
                background-color: #f8f9fa;
                padding: 20px;
                border-radius: 8px;
                border-left: 4px solid #007bff;
            }
            .entity h3 {
                color: #007bff;
                margin-top: 0;
            }
            .api-info {
                background-color: #e7f1ff;
                padding: 20px;
                border-radius: 8px;
                margin-top: 30px;
            }
            .endpoint {
                background-color: white;
                padding: 10px;
                margin: 10px 0;
                border-radius: 4px;
                font-family: monospace;
            }
        </style>
    </head>
    <body>
        <div class="container">
            <h1>EDR System - Entity Relationship Diagram</h1>
            
            <div class="entities">
                <div class="entity">
                    <h3>👤 Users</h3>
                    <div>- id, username, std_id, password</div>
                    <div>- date_join, std_of, active, valid</div>
                </div>
                <div class="entity">
                    <h3>🍽️ Food</h3>
                    <div>- food_name, date, price</div>
                    <div>- reserved, active, contain</div>
                </div>
                <div class="entity">
                    <h3>💬 Message</h3>
                    <div>- from_id, to_id, date</div>
                    <div>- seen, content</div>
                </div>
            </div>
            
            <div class="api-info">
                <h3>🌐 API Endpoints</h3>
                <div class="endpoint">GET / - Welcome message</div>
                <div class="endpoint">POST /api/users/ - Create user</div>
                <div class="endpoint">GET /api/users/ - Get all users</div>
                <div class="endpoint">GET /api/users/{id} - Get user by ID</div>
                <div class="endpoint">POST /api/foods/ - Create food</div>
                <div class="endpoint">POST /api/messages/ - Send message</div>
                <div class="endpoint">GET /edr - View EDR visualization</div>
                <div class="endpoint">GET /docs - API Documentation</div>
            </div>
        </div>
    </body>
    </html>
    """
    return HTMLResponse(content=html_content)