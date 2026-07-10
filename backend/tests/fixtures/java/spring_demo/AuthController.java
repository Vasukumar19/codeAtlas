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
