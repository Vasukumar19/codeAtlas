const express = require('express');
const authRoutes = require('./routes/auth');

const app = express();

app.get('/health', (req, res) => {
    // FIXME: fix health status
    res.json({status: 'ok'});
});

app.use('/auth', authRoutes);

app.listen(3000);
