import os

files = {
    # PYTHON FASTAPI
    "backend/tests/fixtures/python/fastapi_demo/app.py": """
from fastapi import FastAPI
from users import router as users_router
from auth import router as auth_router

app = FastAPI()

app.include_router(users_router)
app.include_router(auth_router)

@app.get("/health")
def health_check():
    # TODO: Add database check
    return {"status": "ok"}
""",
    "backend/tests/fixtures/python/fastapi_demo/auth.py": """
from fastapi import APIRouter

router = APIRouter(prefix="/auth")

class AuthService:
    def login(self, username, password):
        return {"token": "fake-jwt"}

@router.post("/login")
def login_route(username: str):
    service = AuthService()
    return service.login(username, "pass")
""",
    "backend/tests/fixtures/python/fastapi_demo/users.py": """
from fastapi import APIRouter

router = APIRouter(prefix="/users")

@router.get("/")
def list_users():
    return []
""",
    
    # JAVASCRIPT EXPRESS
    "backend/tests/fixtures/javascript/express_demo/app.js": """
const express = require('express');
const authRoutes = require('./routes/auth');

const app = express();

app.get('/health', (req, res) => {
    // FIXME: fix health status
    res.json({status: 'ok'});
});

app.use('/auth', authRoutes);

app.listen(3000);
""",
    "backend/tests/fixtures/javascript/express_demo/routes/auth.js": """
const express = require('express');
const router = express.Router();

class AuthService {
    login(username, password) {
        return "fake-jwt";
    }
}

router.post('/login', (req, res) => {
    const service = new AuthService();
    res.json({token: service.login(req.body.username, req.body.password)});
});

module.exports = router;
""",

    # JAVA SPRING BOOT
    "backend/tests/fixtures/java/spring_demo/Application.java": """
package com.demo;
import org.springframework.boot.SpringApplication;
import org.springframework.boot.autoconfigure.SpringBootApplication;

@SpringBootApplication
public class Application {
    public static void main(String[] args) {
        SpringApplication.run(Application.class, args);
    }
}
""",
    "backend/tests/fixtures/java/spring_demo/AuthController.java": """
package com.demo;
import org.springframework.web.bind.annotation.*;

@RestController
@RequestMapping("/auth")
public class AuthController {
    
    @PostMapping("/login")
    public String login(@RequestParam String username) {
        // TODO: Validate user
        return "fake-jwt";
    }
}
""",

    # GO GIN
    "backend/tests/fixtures/go/gin_demo/main.go": """
package main

import "github.com/gin-gonic/gin"

func main() {
    r := gin.Default()
    
    r.GET("/health", healthCheck)
    
    auth := r.Group("/auth")
    {
        auth.POST("/login", loginHandler)
    }
    
    r.Run()
}

func healthCheck(c *gin.Context) {
    // TODO: health logic
    c.JSON(200, gin.H{"status": "ok"})
}

func loginHandler(c *gin.Context) {
    c.JSON(200, gin.H{"token": "fake-jwt"})
}
""",

    # CSHARP ASP.NET
    "backend/tests/fixtures/csharp/aspnet_demo/Program.cs": """
using Microsoft.AspNetCore.Builder;
using Microsoft.Extensions.DependencyInjection;

var builder = WebApplication.CreateBuilder(args);
builder.Services.AddControllers();

var app = builder.Build();
app.MapControllers();
app.Run();
""",
    "backend/tests/fixtures/csharp/aspnet_demo/AuthController.cs": """
using Microsoft.AspNetCore.Mvc;

namespace Demo.Controllers
{
    [ApiController]
    [Route("[controller]")]
    public class AuthController : ControllerBase
    {
        [HttpPost("login")]
        public IActionResult Login([FromBody] string username)
        {
            // FIXME: Use real auth
            return Ok(new { token = "fake-jwt" });
        }
    }
}
"""
}

for path, content in files.items():
    full_path = os.path.join("c:/Users/kumar/project/codeAtlas", path)
    os.makedirs(os.path.dirname(full_path), exist_ok=True)
    with open(full_path, "w", encoding="utf-8") as f:
        f.write(content.strip() + "\n")
