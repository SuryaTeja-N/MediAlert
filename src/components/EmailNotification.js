import React, { useState, useEffect } from 'react';

const EmailNotification = ({ medication }) => {
    const [missedDoses, setMissedDoses] = useState(medication.missedDoses);
    const [email, setEmail] = useState('');

    useEffect(() => {
        fetchEmailData();
    }, []);

    const fetchEmailData = async () => {
        try {
            const response = await fetch(`/api/email/${medication.id}`);
            const data = await response.json();
            setEmail(data.email);
        } catch (error) {
            console.error('Error fetching email data:', error);
        }
    };

    useEffect(() => {
        sendEmailNotifications();
    }, [missedDoses]);

    const sendEmailNotifications = () => {
        missedDoses.forEach(dose => {
            console.log(`Sending email notification for missed dose of ${medication.name} to ${email}`);
            // Add email sending logic here
        });
    };

    return (
        <div>
            <h2>Email Notifications for {medication.name}</h2>
            <ul>
                {missedDoses.map((dose, index) => (
                    <li key={index}>{dose}</li>
                ))}
            </ul>
        </div>
    );
};

export default EmailNotification;
