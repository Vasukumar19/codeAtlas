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
