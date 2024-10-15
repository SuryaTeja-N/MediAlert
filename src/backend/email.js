const express = require('express');
const router = express.Router();
const nodemailer = require('nodemailer');
const db = require('../config/db');

// Configure email service provider
const transporter = nodemailer.createTransport({
    service: 'Gmail',
    auth: {
        user: 'your-email@gmail.com',
        pass: 'your-email-password'
    }
});

// Send email notification for missed dose
router.post('/email/:medicationId', async (req, res) => {
    try {
        const medicationId = req.params.medicationId;
        const { email, missedDose } = req.body;

        const mailOptions = {
            from: 'your-email@gmail.com',
            to: email,
            subject: 'Missed Dose Notification',
            text: `You have missed a dose of your medication: ${missedDose}`
        };

        transporter.sendMail(mailOptions, (error, info) => {
            if (error) {
                console.error('Error sending email:', error);
                res.status(500).json({ error: 'Internal server error' });
            } else {
                console.log('Email sent:', info.response);
                res.json({ message: 'Email sent successfully' });
            }
        });
    } catch (error) {
        console.error('Error sending email notification:', error);
        res.status(500).json({ error: 'Internal server error' });
    }
});

module.exports = router;
