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
