# Multi-Agent Asset Management Tool for Hackathon
# File structure:
# - main.py (FastAPI backend)
# - agents.py (Agent implementations)
# - models.py (Data models)
# - database.py (Mock database)
# - frontend.html (Simple UI)

# === models.py ===
from pydantic import BaseModel
from typing import List, Dict, Any, Optional
from datetime import datetime
from enum import Enum

class QueryType(str, Enum):
    SEARCH = "search"
    VISUALIZE = "visualize"
    REPORT = "report"
    COMPARE = "compare"

class Fund(BaseModel):
    id: str
    name: str
    country: str
    aum: float  # Assets Under Management in millions
    performance_1y: float  # 1 year performance %
    performance_3y: float  # 3 year performance %
    category: str
    inception_date: datetime
    expense_ratio: float
    
class AgentRequest(BaseModel):
    query: str
    context: Optional[Dict[str, Any]] = None
    query_type: Optional[QueryType] = None

class AgentResponse(BaseModel):
    success: bool
    data: Any
    message: str
    visualization: Optional[Dict[str, Any]] = None
    agent_name: str

class ChatMessage(BaseModel):
    role: str  # "user" or "assistant"
    content: str
    timestamp: datetime
    data: Optional[Any] = None
    visualization: Optional[Dict[str, Any]] = None

# === database.py ===
from datetime import datetime
import random

class MockDatabase:
    """Mock database with sample fund data"""
    
    @staticmethod
    def get_funds():
        countries = ["China", "USA", "Japan", "Germany", "UK", "India", "Brazil", "Canada"]
        categories = ["Equity", "Fixed Income", "Mixed Assets", "Money Market", "Real Estate"]
        
        funds = []
        for i in range(100):
            country = random.choice(countries)
            funds.append(Fund(
                id=f"FUND{i:03d}",
                name=f"{country} {'Growth' if i % 2 == 0 else 'Value'} Fund {i}",
                country=country,
                aum=round(random.uniform(100, 5000), 2),
                performance_1y=round(random.uniform(-10, 30), 2),
                performance_3y=round(random.uniform(-5, 25), 2),
                category=random.choice(categories),
                inception_date=datetime(2010 + i % 10, 1, 1),
                expense_ratio=round(random.uniform(0.5, 2.5), 2)
            ))
        return funds
    
    @staticmethod
    def query_funds(filters: Dict[str, Any]) -> List[Fund]:
        funds = MockDatabase.get_funds()
        
        if "country" in filters:
            funds = [f for f in funds if f.country.lower() == filters["country"].lower()]
        
        if "min_aum" in filters:
            funds = [f for f in funds if f.aum >= filters["min_aum"]]
        
        if "category" in filters:
            funds = [f for f in funds if f.category.lower() == filters["category"].lower()]
        
        return funds

# === agents.py ===
import json
from typing import List, Dict, Any, Optional
from abc import ABC, abstractmethod
import re

class BaseAgent(ABC):
    """Base class for all agents"""
    
    def __init__(self, name: str):
        self.name = name
    
    @abstractmethod
    async def process(self, request: AgentRequest) -> AgentResponse:
        pass
    
    def _call_llm(self, prompt: str, data: Any) -> str:
        """Mock LLM call - in real implementation, this would call your LLM endpoint"""
        # For hackathon, we'll return structured responses
        return f"Analysis of {len(data) if isinstance(data, list) else 'the'} items based on query"

class RouterAgent(BaseAgent):
    """Routes queries to appropriate agents"""
    
    def __init__(self):
        super().__init__("RouterAgent")
    
    async def process(self, request: AgentRequest) -> AgentResponse:
        query_lower = request.query.lower()
        
        # Simple routing logic
        if any(word in query_lower for word in ["visualize", "plot", "chart", "graph", "show me"]):
            query_type = QueryType.VISUALIZE
        elif any(word in query_lower for word in ["report", "summary", "analyze"]):
            query_type = QueryType.REPORT
        elif any(word in query_lower for word in ["compare", "versus", "vs"]):
            query_type = QueryType.COMPARE
        else:
            query_type = QueryType.SEARCH
        
        return AgentResponse(
            success=True,
            data={"query_type": query_type},
            message=f"Routed to {query_type} agent",
            agent_name=self.name
        )

class SearchAgent(BaseAgent):
    """Handles fund search queries"""
    
    def __init__(self):
        super().__init__("SearchAgent")
        self.db = MockDatabase()
    
    async def process(self, request: AgentRequest) -> AgentResponse:
        try:
            # Extract search parameters from query
            filters = self._extract_filters(request.query)
            
            # Query database
            funds = self.db.query_funds(filters)
            
            # Call LLM to format response
            llm_response = self._call_llm(request.query, funds)
            
            return AgentResponse(
                success=True,
                data=[f.dict() for f in funds],
                message=f"Found {len(funds)} funds matching your criteria. " + llm_response,
                agent_name=self.name
            )
        except Exception as e:
            return AgentResponse(
                success=False,
                data=None,
                message=f"Error in search: {str(e)}",
                agent_name=self.name
            )
    
    def _extract_filters(self, query: str) -> Dict[str, Any]:
        filters = {}
        
        # Extract country
        countries = ["China", "USA", "Japan", "Germany", "UK", "India", "Brazil", "Canada"]
        for country in countries:
            if country.lower() in query.lower():
                filters["country"] = country
                break
        
        # Extract AUM filter
        aum_match = re.search(r"(?:aum|assets).*?(\d+)", query.lower())
        if aum_match:
            filters["min_aum"] = float(aum_match.group(1))
        
        return filters

class VisualizationAgent(BaseAgent):
    """Creates visualization specifications for the frontend"""
    
    def __init__(self):
        super().__init__("VisualizationAgent")
    
    async def process(self, request: AgentRequest) -> AgentResponse:
        try:
            # Get data from context
            if not request.context or "data" not in request.context:
                return AgentResponse(
                    success=False,
                    data=None,
                    message="No data available for visualization",
                    agent_name=self.name
                )
            
            data = request.context["data"]
            viz_spec = self._create_visualization(request.query, data)
            
            return AgentResponse(
                success=True,
                data=data,
                message="Visualization created",
                visualization=viz_spec,
                agent_name=self.name
            )
        except Exception as e:
            return AgentResponse(
                success=False,
                data=None,
                message=f"Error in visualization: {str(e)}",
                agent_name=self.name
            )
    
    def _create_visualization(self, query: str, data: List[Dict]) -> Dict[str, Any]:
        query_lower = query.lower()
        
        # Determine visualization type
        if "top" in query_lower:
            # Extract number for top N
            num_match = re.search(r"top\s+(\d+)", query_lower)
            top_n = int(num_match.group(1)) if num_match else 5
            
            # Sort by AUM and get top N
            sorted_data = sorted(data, key=lambda x: x["aum"], reverse=True)[:top_n]
            
            return {
                "type": "bar",
                "data": {
                    "labels": [f["name"] for f in sorted_data],
                    "values": [f["aum"] for f in sorted_data]
                },
                "options": {
                    "title": f"Top {top_n} Funds by AUM",
                    "xLabel": "Fund Name",
                    "yLabel": "AUM (Millions)"
                }
            }
        
        elif "performance" in query_lower:
            return {
                "type": "scatter",
                "data": {
                    "points": [{"x": f["performance_1y"], "y": f["performance_3y"], "label": f["name"]} for f in data]
                },
                "options": {
                    "title": "Fund Performance Comparison",
                    "xLabel": "1 Year Performance (%)",
                    "yLabel": "3 Year Performance (%)"
                }
            }
        
        else:
            # Default table view
            return {
                "type": "table",
                "data": {
                    "columns": ["Name", "Country", "AUM", "1Y Perf", "Category"],
                    "rows": [[f["name"], f["country"], f["aum"], f["performance_1y"], f["category"]] for f in data[:10]]
                },
                "options": {
                    "title": "Fund Overview"
                }
            }

class ReportAgent(BaseAgent):
    """Generates reports and summaries"""
    
    def __init__(self):
        super().__init__("ReportAgent")
    
    async def process(self, request: AgentRequest) -> AgentResponse:
        try:
            if not request.context or "data" not in request.context:
                return AgentResponse(
                    success=False,
                    data=None,
                    message="No data available for report generation",
                    agent_name=self.name
                )
            
            data = request.context["data"]
            report = self._generate_report(data)
            
            return AgentResponse(
                success=True,
                data=report,
                message="Report generated successfully",
                agent_name=self.name
            )
        except Exception as e:
            return AgentResponse(
                success=False,
                data=None,
                message=f"Error in report generation: {str(e)}",
                agent_name=self.name
            )
    
    def _generate_report(self, data: List[Dict]) -> Dict[str, Any]:
        if not data:
            return {"summary": "No data available"}
        
        total_aum = sum(f["aum"] for f in data)
        avg_performance_1y = sum(f["performance_1y"] for f in data) / len(data)
        avg_performance_3y = sum(f["performance_3y"] for f in data) / len(data)
        
        country_breakdown = {}
        for f in data:
            country = f["country"]
            if country not in country_breakdown:
                country_breakdown[country] = {"count": 0, "total_aum": 0}
            country_breakdown[country]["count"] += 1
            country_breakdown[country]["total_aum"] += f["aum"]
        
        return {
            "summary": {
                "total_funds": len(data),
                "total_aum": round(total_aum, 2),
                "avg_performance_1y": round(avg_performance_1y, 2),
                "avg_performance_3y": round(avg_performance_3y, 2),
                "country_breakdown": country_breakdown,
                "top_fund": max(data, key=lambda x: x["aum"])["name"] if data else None
            }
        }

class ValidatorAgent(BaseAgent):
    """Validates inputs and outputs"""
    
    def __init__(self):
        super().__init__("ValidatorAgent")
    
    async def process(self, request: AgentRequest) -> AgentResponse:
        # Simple validation
        if not request.query or len(request.query.strip()) == 0:
            return AgentResponse(
                success=False,
                data=None,
                message="Query cannot be empty",
                agent_name=self.name
            )
        
        if len(request.query) > 500:
            return AgentResponse(
                success=False,
                data=None,
                message="Query too long (max 500 characters)",
                agent_name=self.name
            )
        
        return AgentResponse(
            success=True,
            data=None,
            message="Query validated",
            agent_name=self.name
        )

# === main.py ===
from fastapi import FastAPI, WebSocket, WebSocketDisconnect
from fastapi.responses import HTMLResponse
from fastapi.middleware.cors import CORSMiddleware
import json
from datetime import datetime
from typing import Dict, List

app = FastAPI()

# Enable CORS
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Initialize agents
agents = {
    "router": RouterAgent(),
    "search": SearchAgent(),
    "visualize": VisualizationAgent(),
    "report": ReportAgent(),
    "validator": ValidatorAgent()
}

# Store conversation context
conversations: Dict[str, List[ChatMessage]] = {}

@app.get("/")
async def get():
    return HTMLResponse(open("frontend.html").read())

@app.websocket("/ws")
async def websocket_endpoint(websocket: WebSocket):
    await websocket.accept()
    session_id = str(datetime.now().timestamp())
    conversations[session_id] = []
    
    try:
        while True:
            # Receive message from client
            data = await websocket.receive_text()
            message_data = json.loads(data)
            
            # Create user message
            user_message = ChatMessage(
                role="user",
                content=message_data["query"],
                timestamp=datetime.now()
            )
            conversations[session_id].append(user_message)
            
            # Process through agents
            request = AgentRequest(query=message_data["query"])
            
            # 1. Validate input
            validation_response = await agents["validator"].process(request)
            if not validation_response.success:
                await websocket.send_text(json.dumps({
                    "role": "assistant",
                    "content": validation_response.message,
                    "error": True
                }))
                continue
            
            # 2. Route query
            router_response = await agents["router"].process(request)
            query_type = router_response.data["query_type"]
            
            # 3. Process based on query type
            if query_type == QueryType.SEARCH:
                response = await agents["search"].process(request)
            
            elif query_type == QueryType.VISUALIZE:
                # Get last search results from conversation
                last_data = None
                for msg in reversed(conversations[session_id]):
                    if msg.data:
                        last_data = msg.data
                        break
                
                request.context = {"data": last_data} if last_data else None
                response = await agents["visualize"].process(request)
            
            elif query_type == QueryType.REPORT:
                # Get last search results from conversation
                last_data = None
                for msg in reversed(conversations[session_id]):
                    if msg.data:
                        last_data = msg.data
                        break
                
                request.context = {"data": last_data} if last_data else None
                response = await agents["report"].process(request)
            
            else:
                response = AgentResponse(
                    success=False,
                    data=None,
                    message="Query type not implemented yet",
                    agent_name="System"
                )
            
            # Create assistant message
            assistant_message = ChatMessage(
                role="assistant",
                content=response.message,
                timestamp=datetime.now(),
                data=response.data,
                visualization=response.visualization
            )
            conversations[session_id].append(assistant_message)
            
            # Send response to client
            await websocket.send_text(json.dumps({
                "role": "assistant",
                "content": response.message,
                "data": response.data,
                "visualization": response.visualization,
                "agent": response.agent_name
            }))
            
    except WebSocketDisconnect:
        del conversations[session_id]

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)