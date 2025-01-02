import datetime
import sys
import os
from email.mime.text import MIMEText
from PySide6.QtGui import *
from PySide6.QtWidgets import *
from PySide6.QtCore import *
from PIL import Image
from pathlib import *
import smtplib
from email.mime.multipart import MIMEMultipart
from email.mime.base import MIMEBase
from email import encoders
from reportlab.lib.pagesizes import A4
from reportlab.lib.utils import ImageReader
from reportlab.pdfgen import canvas


def absPath(file):
    return str(Path(__file__).parent.absolute() / file)

# IMG
iconroot = os.path.dirname(__file__)
im = Image.open(absPath('Img_hospital/hospital.jpg'))
w, h = im.size


# Queue class
class ListQueueSimple:
    def __init__(self):
        self._L = []

    def enqueue(self, item):
        # Traverse the list to find the position where to insert the item
        i = 0
        while i < len(self._L) and self._L[i][0] <= item[0]:
            i += 1
        # Insert the item at the found position
        self._L.insert(i, item)

    def dequeue(self):
        return self._L.pop(0)

    def peek(self):
        return self._L[0]

    def __len__(self):
        return len(self._L)

    def isempty(self):
        return len(self) == 0


# Patient class
class Patient:
    def __init__(self, name, age, severity, gender):
        self.name = name
        self.age = age
        self.severity = severity
        self.gender = gender


# Main class
class MainWindow(QMainWindow):
    def __init__(self):
        super(MainWindow, self).__init__()
        self.title = 'Hospital App'
        self.setWindowTitle(self.title)
        self.patient_list = []
        self.priority_queue = ListQueueSimple()
        self.current_widget = None

        # Set icon
        my_icon = QIcon()
        my_icon.addFile(absPath('Img_hospital/favicon.png'))
        self.setWindowIcon(my_icon)

        self.add_image()
        self.build_menu()
        self.setBackground()

        # Set initial window size
        self.resize(800, 600)
    
    def setBackground(self):
        # Create a QPixmap with the background image path
        pixmap = QPixmap(absPath('Img_hospital/hospital.jpg'))

        # Set the background image as the window's background
        self.setAutoFillBackground(True)
        palette = self.palette()
        palette.setBrush(self.backgroundRole(), pixmap)
        self.setPalette(palette)

    # Data Entry for Clerk
    def clerk_widget(self):
        if self.current_widget:
            self.current_widget.deleteLater()
        self.current_widget = QWidget(self)
        self.setCentralWidget(self.current_widget)

        # Create labels for the menu
        self.title_name = QLabel('NAME')
        self.title_name.setFont(QFont('Arial', 20))

        self.title_age = QLabel('AGE')
        self.title_age.setFont(QFont('Arial', 20))

        self.title_severity = QLabel('SEVERITY')
        self.title_severity.setFont(QFont('Arial', 20))

        self.title_gender = QLabel('GENDER')
        self.title_gender.setFont(QFont('Arial', 20))

        # Submit button
        self.submit_button = QPushButton('SUBMIT')
        self.submit_button.setFont(QFont('Arial', 15))
        self.submit_button.setFixedHeight(40)
        self.submit_button.setFixedWidth(200)
        self.submit_button.setStyleSheet('background-color: blue; color: white;')

        # Editor
        self.name = QLineEdit()
        self.name.setFixedSize(100, 50)

        # Combo Box
        self.severity = QComboBox()
        self.severity.addItems(['Select an option',
                                '1. Resuscitation (immediate care)',
                                '2. Emergency (10 - 15 min)',
                                '3. Urgency (60 min)',
                                '4. Minor urgency (2 hours)',
                                '5. No urgency (5 hours)'])
        self.gender = QComboBox()
        self.gender.addItems(['Select an option',
                            'Male',
                            'Female',
                            'Not specified'])

        self.age = QComboBox()
        self.age.addItems([str(i) for i in range(101)])

        # Create layout and add widgets
        layout = QVBoxLayout()
        layout.addWidget(self.title_name)
        layout.addWidget(self.name)
        layout.addWidget(self.title_age)
        layout.addWidget(self.age)
        layout.addWidget(self.title_severity)
        layout.addWidget(self.severity)
        layout.addWidget(self.title_gender)
        layout.addWidget(self.gender)
        layout.addWidget(self.submit_button)
        layout.setAlignment(Qt.AlignCenter)

        self.current_widget.setLayout(layout)

        # Connect button signal to slot
        self.submit_button.clicked.connect(self.submit_data)

    # Background image
    def add_image(self):
        # Image
        buckling_blabel = QLabel(self)
        pixmap = QPixmap(absPath('Img_hospital/logo_tec.png'))
        buckling_blabel.resize(0.25 * pixmap.width(), 0.25 * pixmap.height())
        buckling_blabel.setPixmap(pixmap.scaled(buckling_blabel.size(), Qt.KeepAspectRatio))
        buckling_blabel.setAlignment(Qt.AlignCenter)

    # Queue
    def push_to_queue(self):
        name = self.name.text()
        age = self.age.currentText()
        severity = self.severity.currentText()
        gender = self.gender.currentText()
        patient = Patient(name, age, severity, gender)
        self.priority_queue.enqueue((severity, patient))
        invoice_file = self.generate_invoice(patient)
        self.send_email(patient, invoice_file)
        self.name.clear()
        self.age.setCurrentIndex(0)
        self.severity.setCurrentIndex(0)
        self.gender.setCurrentIndex(0)
        if len(self.priority_queue) > 0:
            self.submit_button.setDisabled(True)
        else:
            self.submit_button.setEnabled(True)

    # Function to add to queue when submit is clicked
    def submit_data(self):
        if self.name.text() == "" or self.age.currentText() == "Select an option" \
                or self.severity.currentText() == "Select an option" or self.gender.currentText() == "Select an option":
            QMessageBox.warning(self, "Empty fields", "Please complete all fields.")
            return

        self.push_to_queue()
        self.submit_button.setEnabled(True)
        self.submit_button.setStyleSheet('background-color: blue; color: white;')

    # MENU
    def build_menu(self):
        self.menu = self.menuBar()

        self.menu_file = self.menu.addMenu('&Mode')

        self.menu_file.addAction(
            QIcon(absPath('Img_hospital/doctor.png')),
            '&Doctor', self.doctor_widget, 'Ctrl+m')
        self.menu_file.addAction(
            QIcon(absPath('Img_hospital/secretario.png')),
            '&Clerk', self.clerk_widget, 'Ctrl+c')
        self.menu_file.addAction(
            QIcon(absPath('Img_hospital/paciente.png')),
            '&Patient', self.patient_widget, 'Ctrl+p')
        self.menu_file.addAction(
            QIcon(absPath('Img_hospital/informacion.png')),
            '&Information', self.image_info, 'Ctrl+i')
        self.menu_file.addAction(
            QIcon(absPath('Img_hospital/cerrar-sesion.png')),
            '&Exit', self.close, 'Ctrl+s')

    # Doctor
    def doctor_widget(self):
        if self.current_widget:
            self.current_widget.deleteLater()
        self.current_widget = QWidget(self)
        self.setCentralWidget(self.current_widget)

        # Next button
        self.button_next = QPushButton('Next')
        self.button_next.setFont(QFont('Arial', 15))
        self.button_next.setFixedHeight(40)
        self.button_next.setFixedWidth(200)
        self.button_next.setStyleSheet('background-color: blue; color: white;')
        self.button_next.clicked.connect(self.show_next_patient)

        layout = QVBoxLayout(self.current_widget)

        if not self.priority_queue.isempty():
            severity, patient = self.priority_queue.dequeue()

            label = QLabel(
                f"Name: {patient.name} \nAge: {patient.age} \nSeverity: {severity} \nGender: {patient.gender}")
            label.setStyleSheet("font-size: 40pt;")

            layout.addWidget(label)
        else:
            QMessageBox.warning(self, "No patients", "There are no patients waiting.")

        layout.addWidget(self.button_next)
        layout.setAlignment(Qt.AlignCenter)

    # Function to show the next patient
    def show_next_patient(self):
        if not self.priority_queue.isempty():
            self.doctor_widget()
            if self.priority_queue.isempty():
                self.button_next.setEnabled(False)
        else:
            QMessageBox.warning(self, "No patients", "There are no patients waiting.")

    # Function to show the next patient
    def patient_widget(self):
        if self.current_widget:
            self.current_widget.deleteLater()
        self.current_widget = QWidget(self)
        self.setCentralWidget(self.current_widget)
        if not self.priority_queue.isempty():
            patient = self.priority_queue.peek()[1]
            patient_label = QLabel(f"Next patient: {patient.name}")
            patient_label.setStyleSheet("font-size: 40pt;")
            layout = QVBoxLayout(self.current_widget)
            layout.addWidget(patient_label)
            layout.setAlignment(Qt.AlignCenter)
        else:
            QMessageBox.warning(self, "No patients", "There are no patients waiting.")
    
    # Information image
    def image_info(self):
        if self.current_widget:
            self.current_widget.deleteLater()
        self.current_widget = QWidget(self)
        self.setCentralWidget(self.current_widget)
        self.image_menu = QLabel(self)
        pixmap = QPixmap(absPath('Img_hospital/Triagemexico.jpg'))
        self.image_menu.resize(0.5 * pixmap.width(), 0.5 * pixmap.height())
        self.image_menu.setPixmap(pixmap.scaled(self.image_menu.size(), Qt.KeepAspectRatio))
        self.image_menu.setAlignment(Qt.AlignCenter)
        layout = QVBoxLayout(self.current_widget)
        layout.addWidget(self.image_menu)
        layout.setAlignment(Qt.AlignCenter)

    # Function to send email
    def send_email(self, patient, invoice_file_name):
        # Get patient data
        name = patient.name
        age = patient.age
        severity = patient.severity
        gender = patient.gender

        # Build the email content including patient data
        content = f"Invoice Confirmation\n\n" \
                f"Name: {name}\n" \
                f"Age: {age}\n" \
                f"Severity: {severity}\n" \
                f"Gender: {gender}\n" \
                f"\nThank you for your consultation! We hope you get better soon."

        # Configure the email
        msg = MIMEMultipart()
        msg['From'] = 'test.email@example.com'  # Put your test email here
        msg['To'] = 'recipient@example.com'  # Put the recipient's email here
        msg['Subject'] = 'Invoice Confirmation'

        # Attach the invoice to the email
        self.attach_invoice(invoice_file_name, msg)

        # Add the content to the email
        msg.attach(MIMEText(content, 'plain'))

        # Send the email
        mail = smtplib.SMTP('smtp.gmail.com', 587)
        mail.ehlo()
        mail.starttls()
        mail.login('test.email@example.com', 'test_password')  # Use a test password here
        mail.sendmail(msg['From'], msg['To'], msg.as_string())
        mail.close()

    # Function to attach the invoice to the email
    def attach_invoice(self, filename, msg):
        # Configure MIME type for the attachment
        part = MIMEBase('application', 'octet-stream')
        part.set_payload(open(filename, 'rb').read())
        encoders.encode_base64(part)
        part.add_header('Content-Disposition', f'attachment; filename={filename}')

        # Attach the file to the message
        msg.attach(part)

    # Function to generate the invoice
    def generate_invoice(self, patient):
        # Get patient data
        name = patient.name
        age = patient.age
        severity = patient.severity
        gender = patient.gender

        # Configure the canvas to generate the PDF invoice
        file_name = f'{name}_Invoice.pdf'
        c = canvas.Canvas(file_name, pagesize=A4)
        c.setFont('Times-Roman', 15)

        # Place the logo in the top left corner
        img = ImageReader(absPath('Img_hospital/logo_tec.png'))
        img2 = ImageReader(absPath('Img_hospital/medical.jpg'))
        img3 = ImageReader(absPath('Img_hospital/gracias.jpg'))

        # Get the width and height of the image
        img_w, img_h = img.getSize()

        today = datetime.date.today()

        # Create text for the invoice
        c.drawString(450, 780, 'Date:')
        c.drawString(450, 750, f'{today}')
        c.drawImage(img, 40, 750, width=200, height=50)

        # Write patient data on the invoice
        c.drawString(50, 680, f'Name: {name}')
        c.drawString(50, 650, f'Age: {age}')
        c.drawString(50, 620, f'Severity: {severity}')
        c.drawString(50, 590, f'Gender: {gender}')
        c.drawString(250, 710, 'Patient Information')
        c.drawString(40, 730, '-' * 100)
        c.drawString(40, 500, '-' * 100)
        c.drawString(250, 480, 'Payment Description')
        c.drawString(100, 430, 'Item')
        c.drawString(100, 400, 'Consultation')
        c.drawString(350, 430, 'Price')
        c.drawString(350, 400, '$1000.00')
        c.drawString(200, 250, 'We hope you recover soon!')

        c.drawImage(img3, 80, 45, width=70, height=100)
        c.drawImage(img2, 370, 0, width=200, height=200)

        c.save()

        return file_name


def get_severity_key(item):
    return item[0]



if __name__ == '__main__':
    app = QApplication(sys.argv)
    GUI = MainWindow()
    GUI.show()
    sys.exit(app.exec())
