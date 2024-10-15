import React, { useState, useEffect } from 'react';

const DosageReminder = ({ medication }) => {
    const [reminders, setReminders] = useState(medication.reminders);

    useEffect(() => {
        displayReminders();
    }, [reminders]);

    const displayReminders = () => {
        reminders.forEach(reminder => {
            alert(`Reminder: Time to take your ${medication.name} dose.`);
        });
    };

    return (
        <div>
            <h2>Dosage Reminders for {medication.name}</h2>
            <ul>
                {reminders.map((reminder, index) => (
                    <li key={index}>{reminder}</li>
                ))}
            </ul>
        </div>
    );
};

export default DosageReminder;
