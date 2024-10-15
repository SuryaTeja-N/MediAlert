import React, { useState, useEffect } from 'react';

const EmailNotification = ({ medication }) => {
    const [missedDoses, setMissedDoses] = useState(medication.missedDoses);

    useEffect(() => {
        sendEmailNotifications();
    }, [missedDoses]);

    const sendEmailNotifications = () => {
        missedDoses.forEach(dose => {
            console.log(`Sending email notification for missed dose of ${medication.name}`);
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
