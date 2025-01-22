# Diasporan Health Insurance Platform

This repository contains the source code for the **Diasporan Health Insurance** project, a web-based platform built using Django. The platform provides comprehensive health insurance solutions tailored for diasporans, enabling subscription management, payment integration, claims tracking, and more.

---

## Features

1. **User Management**
   - User registration, authentication, and profile management.
   - Customizable user profiles with support for identification verification.

2. **Subscription Management**
   - Multiple subscription plans: Bronze, Ruby, Gold, and Platinum.
   - Monthly and yearly subscription options.
   - Integrated with Stripe and Paystack for payment processing.

3. **Payment Integration**
   - Support for multiple payment gateways: Stripe, Paystack, and WorldRemit.
   - Multi-currency support for international payments.

4. **Beneficiary Management**
   - Add, update, or remove beneficiaries.
   - Document verification for beneficiaries.

5. **Claims Management**
   - Submit and track health insurance claims.

6. **Customer Support**
   - Live chat functionality.
   - Multi-language support.
   - FAQ and Help Center for user assistance.

7. **Marketing and Analytics**
   - Health tips and wellness blogs.
   - Analytics dashboard for user insights and system monitoring.

8. **Admin Dashboard**
   - Manage users, subscriptions, claims, and beneficiaries.
   - View analytics and access system logs.

9. **API Integration**
   - Integration with NEM Insurance API for real-time data fetching.

---

## Installation

### Prerequisites

- Python 3.9+
- Django 4.2+
- PostgreSQL (for production)
- Stripe and Paystack API keys

### Steps

1. Clone the repository:
   ```bash
   git clone https://github.com/your-username/diasporan-health-insurance.git
   cd diasporan-health-insurance
   ```

2. Create a virtual environment:
   ```bash
   python -m venv venv
   source venv/bin/activate  # On Windows, use `venv\Scripts\activate`
   ```

3. Install dependencies:
   ```bash
   pip install -r requirements.txt
   ```

4. Configure environment variables:
   - Create a `.env` file in the project root.
   - Add the following variables:
     ```
     SECRET_KEY=your_secret_key
     DEBUG=True
     DATABASE_URL=postgres://user:password@localhost:5432/your_db
     STRIPE_API_KEY=your_stripe_api_key
     PAYSTACK_API_KEY=your_paystack_api_key
     ```

5. Run database migrations:
   ```bash
   python manage.py migrate
   ```

6. Start the development server:
   ```bash
   python manage.py runserver
   ```

7. Access the platform at `http://127.0.0.1:8000`.

---

## Deployment

### For Production

1. Use a production-grade web server (e.g., Nginx or Apache).
2. Configure Gunicorn or uWSGI for WSGI application hosting.
3. Set `DEBUG=False` in your `.env` file.
4. Use PostgreSQL for the database backend.
5. Configure static files:
   ```bash
   python manage.py collectstatic
   ```
6. Secure the application with SSL.

---

## Contribution

Contributions are welcome! Please follow these steps:

1. Fork the repository.
2. Create a new branch:
   ```bash
   git checkout -b feature/your-feature-name
   ```
3. Make your changes and commit them:
   ```bash
   git commit -m "Add your message here"
   ```
4. Push to your fork:
   ```bash
   git push origin feature/your-feature-name
   ```
5. Create a Pull Request.

---

## License

This project is licensed under the MIT License. See the `LICENSE` file for details.

---

## Contact

For inquiries or support, please contact:

- Email: dozimikes@gmail.com
- Phone: +2349061266642
- Website: [Pitchmic](https://pitchmic.com)

