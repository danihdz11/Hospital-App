# Hospital Application

This project is a hospital management system built using Python and PySide6 (Qt6), designed to handle patient registration, priority queue management, and invoice generation. The application allows staff (clerks), doctors, and patients to interact with the system in different ways, making it useful for managing patient data and sending invoices.

## Features

- **Patient Registration**: Clerks can enter patient information, such as name, age, severity of condition, and gender.
- **Priority Queue**: Patients are added to a priority queue based on the severity of their condition.
- **Doctor Interaction**: Doctors can view the next patient in the queue and start treatment.
- **Patient Information**: Patients can view the next patient in line.
- **Invoice Generation**: For each patient registered, an invoice is generated and sent via email.
- **Background and Icon**: Custom background and icons are used for an engaging user interface.

## Technologies Used

- **Python**: Programming language used for the application.
- **PySide6 (Qt6)**: Framework for building the graphical user interface (GUI).
- **Pillow**: Library used for image processing.
- **ReportLab**: Used for generating PDF invoices.
- **smtplib**: Used for sending emails with invoices as attachments.

### Prerequisites

Ensure that you have the following Python libraries installed:

- `PySide6`
- `Pillow`
- `reportlab`

## Notes
- Replace the email configuration (`test.email@example.com`) with valid email credentials to send invoices.
- The application requires internet access to send emails via SMTP.
