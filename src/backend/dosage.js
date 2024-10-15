const express = require('express');
const router = express.Router();
const db = require('../config/db');

// Fetch dosage data for a specific medication
router.get('/dosage/:medicationId', async (req, res) => {
    try {
        const medicationId = req.params.medicationId;
        const dosageData = await db.query('SELECT dosage FROM medications WHERE id = ?', [medicationId]);
        res.json(dosageData[0]);
    } catch (error) {
        console.error('Error fetching dosage data:', error);
        res.status(500).json({ error: 'Internal server error' });
    }
});

// Update dosage data for a specific medication
router.put('/dosage/:medicationId', async (req, res) => {
    try {
        const medicationId = req.params.medicationId;
        const { dosage } = req.body;
        await db.query('UPDATE medications SET dosage = ? WHERE id = ?', [dosage, medicationId]);
        res.json({ message: 'Dosage updated successfully' });
    } catch (error) {
        console.error('Error updating dosage data:', error);
        res.status(500).json({ error: 'Internal server error' });
    }
});

module.exports = router;
