// Mock API Client to connect to the backend gateways
export const api = {
  fetchRepositoryStats: async (repoId) => {
    return {
      score: "A+",
      technicalDebt: "Low",
      knowledgeCoverage: "94%",
      graphDensity: "High"
    };
  },
  
  askAI: async (query, repoId) => {
    // Mock the backend HybridRetrieval -> Intelligence Pipeline
    return {
      type: "Execution Flow",
      title: "Authentication Flow",
      summary: "Authentication starts from POST /login and cascades down.",
      sections: [
        { title: "Entry Point", content: "POST /login in auth/routes.py" },
        { title: "Service Layer", content: "AuthService.login" }
      ],
      steps: [
        "/login", "AuthController", "AuthService", "UserRepository", "PostgreSQL"
      ],
      citations: [
        { file_path: "auth/routes.py", confidence: 0.98 },
        { file_path: "auth/service.py", confidence: 0.95 },
        { file_path: "auth/repository.py", confidence: 0.92 }
      ],
      confidence: 0.97
    };
  }
}
