require('dotenv').config();
const express = require('express');
const cors = require('cors');

const app = express();
app.use(cors());
app.use(express.json());

// 路由
app.use('/api/auth',          require('./src/routes/auth'));
app.use('/api/scenes',        require('./src/routes/scenes'));
app.use('/api/versions',      require('./src/routes/versions'));
app.use('/api/settings',      require('./src/routes/settings'));
app.use('/api/users',         require('./src/routes/users'));
app.use('/api/stats',         require('./src/routes/stats'));
app.use('/api/announcements', require('./src/routes/announcements'));

app.get('/', (req, res) => res.json({ name: 'OnePersonClaw API', version: '1.0.0', author: '常云举19966519194' }));

const PORT = process.env.PORT || 3030;
app.listen(PORT, () => console.log(`OnePersonClaw API running on port ${PORT}`));
