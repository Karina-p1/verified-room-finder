# 🏠 RoomFinder Nepal

> **Nepal's trusted verified room rental marketplace** — connecting honest landlords with serious tenants across all provinces.

[![Python](https://img.shields.io/badge/Python-3.10+-3776AB?style=flat&logo=python&logoColor=white)](https://python.org)
[![Django](https://img.shields.io/badge/Django-4.x-092E20?style=flat&logo=django&logoColor=white)](https://djangoproject.com)
[![Bootstrap](https://img.shields.io/badge/Bootstrap-5.3-7952B3?style=flat&logo=bootstrap&logoColor=white)](https://getbootstrap.com)

---

## 📋 Table of Contents

- [Overview](#-overview)
- [Live Features](#-live-features)
- [Tech Stack](#-tech-stack)
- [Project Structure](#-project-structure)
- [Getting Started](#-getting-started)
- [Environment Variables](#-environment-variables)
- [User Roles](#-user-roles)
- [Key Workflows](#-key-workflows)
- [Admin Dashboard](#-admin-dashboard)
- [Screenshots](#-screenshots)
- [Roadmap](#-roadmap)
- [Contributing](#-contributing)
- [Author](#-author)

---

## 🌐 Overview

RoomFinder Nepal is a full-stack Django web application that solves a real problem in Nepal's rental market: **lack of trust and verification**. Unlike generic listing sites, every landlord must submit identity and property documents before their listings go live. Tenants can browse verified rooms with confidence, while an admin panel gives staff full control over approvals, analytics, and platform health.

The platform supports three distinct user roles — **tenant**, **landlord**, and **staff/admin** — each with a tailored experience and access-controlled views.

---

## ✅ Live Features

### 🔐 Authentication & Accounts
- Custom user model with role-based registration (`tenant` / `landlord`)
- OTP email verification on signup (Gmail SMTP)
- Password reset via email
- Profile management (name, phone, avatar)

### 🏘️ Listings
- Full CRUD for landlords (create, edit, delete listings)
- Multi-image upload per listing with individual image deletion
- Location fields: Province → District → City with Nepal-specific data
- GPS coordinates (latitude/longitude) captured via interactive Leaflet map (6 decimal precision)
- Room categories: Single, Double, 1BHK, 2BHK, Flat, Hostel, etc.
- Amenities selection (WiFi, parking, water, electricity, furnished, etc.)
- Listing status flow: `pending → approved / rejected`
- Admin rejection reason stored and visible to landlord

### 🔍 Search & Discovery
- Full-text search by title, district, city
- Filter by category, price range, furnished status, district
- Pagination across search results
- Recently Viewed listings (session-based)
- Quick category icon row on homepage (Roomsewa-inspired UX)

### 📞 Phone Reveal with Ad Gate
- Tenant must watch an advertisement modal before phone number is revealed
- Every reveal is logged to `PhoneRevealLog` for analytics
- Landlord phone number is hidden behind the modal on the listing detail page

### 📄 Document Verification
- Landlords upload citizenship/identity documents and property ownership proof
- Admin reviews and approves/rejects documents independently
- Landlords cannot create listings until documents are approved
- Document status shown on landlord dashboard

### 📧 Email Notifications
- Listing approved / rejected emails to landlord (with reason on rejection)
- Document approved / rejected emails
- OTP verification email on signup

### 🚩 Listing Reports
- Tenants can report suspicious or fraudulent listings
- Reports appear in a dedicated admin queue (`apps/reports/`)
- Staff can mark reports as resolved

### 📊 Admin Analytics Dashboard
- 30-day Phone Reveals line chart (gap-filled, evenly spaced)
- Listings by Province doughnut chart
- New User Registrations bar chart (gap-filled)
- Listing Status Breakdown doughnut chart
- Top 10 Listings by Phone Reveals table
- Summary stat cards: Total Reveals, Total Users, Active Listings, Active Ads

### 🛠️ Admin Panel
- Pending / Approved / Rejected listings queues
- Pending / Approved / Rejected document queues
- User management (suspend / activate accounts)
- Reports queue (tenant-reported listings)
- Advertisement management (activate / deactivate ads)

---

## 🧰 Tech Stack

| Layer | Technology |
|---|---|
| Backend | Python 3.10+, Django 4.x |
| Database | SQLite (development) / PostgreSQL (production-ready) |
| Frontend | Bootstrap 5.3, custom CSS variables, Bootstrap Icons |
| Typography | Playfair Display (display), Inter (body) |
| Email | Gmail SMTP via Django `send_mail` |
| Auth | Django `AbstractBaseUser` + custom `CustomUser` model |
| Image Storage | Django `MEDIA_ROOT` (local), S3-compatible in production |
| OTP | Django sessions + random 6-digit token |

---

## 📁 Project Structure

```
ROOMFINDER_PROJECT/
├── myenv/                          # Virtual environment (not committed)
└── roomfinder/                     # Django project root
    ├── apps/                       # All Django applications
    │   ├── accounts/               # Auth, registration, OTP, profiles
    │   │   ├── models.py           # CustomUser with role field (tenant/landlord)
    │   │   ├── views.py            # register, login, logout, OTP verify, profile
    │   │   ├── forms.py            # RegistrationForm, LoginForm, ProfileForm
    │   │   └── notifications.py    # Email helper functions (approval/rejection)
    │   ├── admin_panel/            # Staff-only dashboard and review views
    │   │   └── views.py            # Dashboard, analytics, listing/doc review, user mgmt
    │   ├── advertisements/         # Ad modal and phone reveal logging
    │   │   └── models.py           # Advertisement, PhoneRevealLog
    │   ├── documents/              # Landlord document upload & verification
    │   │   └── models.py           # LandlordDocument
    │   ├── listings/               # Core listing app
    │   │   ├── models.py           # Listing, ListingImage
    │   │   ├── views.py            # CRUD, search, detail, recently viewed
    │   │   └── forms.py            # ListingForm with image formset
    │   ├── reports/                # Tenant listing reports
    │   │   └── models.py           # ListingReport
    │   └── __init__.py
    ├── media/                      # Uploaded images and documents (runtime)
    ├── roomfinder/                 # Django config package
    │   ├── settings.py
    │   ├── urls.py
    │   ├── asgi.py
    │   └── wsgi.py
    ├── static/                     # Static assets (CSS, JS, images)
    ├── templates/
    │   └── base.html               # Role-aware navbar, messages block, footer
    ├── .env                        # Environment variables (not committed)
    ├── db.sqlite3                  # SQLite database (development)
    ├── manage.py
    └── requirements.txt
```

---

## 🚀 Getting Started

### Prerequisites

- Python 3.10+
- pip
- Git
- A Gmail account (for SMTP email)

### 1. Clone the repository

```bash
git clone https://github.com/Karina-p1/verified-room-finder.git
cd verified-room-finder/roomfinder
```

### 2. Create and activate a virtual environment

```bash
python -m venv venv

# Windows
venv\Scripts\activate

# macOS / Linux
source venv/bin/activate
```

### 3. Install dependencies

```bash
pip install -r requirements.txt
```

### 4. Set up environment variables

Create a `.env` file in the project root (see [Environment Variables](#-environment-variables) below).

### 5. Apply migrations

```bash
python manage.py migrate
```

### 6. Create a superuser (admin)

```bash
python manage.py createsuperuser
```

### 7. Run the development server

```bash
python manage.py runserver
```

Visit `http://127.0.0.1:8000` in your browser.

---

## 🔑 Environment Variables

Create a `.env` file in the project root:

```env
# Django
SECRET_KEY=your-secret-key-here
DEBUG=True
ALLOWED_HOSTS=127.0.0.1,localhost

# Database (leave blank to use SQLite for development)
DATABASE_URL=

# Email (Gmail SMTP)
EMAIL_BACKEND=django.core.mail.backends.smtp.EmailBackend
EMAIL_HOST=smtp.gmail.com
EMAIL_PORT=587
EMAIL_USE_TLS=True
EMAIL_HOST_USER=your-gmail@gmail.com
EMAIL_HOST_PASSWORD=your-gmail-app-password

# Media
MEDIA_URL=/media/
```

> **Gmail App Password:** Go to Google Account → Security → 2-Step Verification → App Passwords. Generate one for "Mail" and paste it as `EMAIL_HOST_PASSWORD`.

---

## 👤 User Roles

| Role | Can Do |
|---|---|
| **Tenant** | Browse listings, search & filter, reveal phone numbers (ad-gated), message landlords, report listings |
| **Landlord** | Upload documents, create & manage listings (after document approval), view listing analytics |
| **Staff / Admin** | Full admin panel access — review listings & documents, manage users, view platform analytics, manage ads |

---

## 🔄 Key Workflows

### Landlord Onboarding
```
Register (role=landlord)
  → Verify email via OTP
  → Upload identity & property documents
  → Admin reviews and approves documents
  → Landlord can now create listings
  → Listing submitted for admin review
  → Admin approves/rejects (email sent)
  → Approved listing goes live
```

### Tenant Finding a Room
```
Browse / Search listings
  → Filter by district, category, price, furnished
  → View listing detail
  → Click "Reveal Phone Number"
  → Watch ad modal
  → Phone number revealed + logged
  → Message landlord via internal system
```

---

## 📊 Admin Dashboard

The staff analytics dashboard (`/admin-panel/analytics/`) provides:

- **Stat cards** — Total Phone Reveals, Total Users, Active Listings, Active Ads
- **Line chart** — Phone reveals over the last 30 days (all days shown, zeros filled in)
- **Doughnut chart** — Active listing distribution by Province
- **Bar chart** — New user registrations over the last 30 days (all days shown, zeros filled in)
- **Doughnut chart** — Listing status breakdown (Approved / Pending / Rejected)
- **Top listings table** — Top 10 listings by phone reveal count with direct view links

---

## 🤝 Contributing

Contributions are welcome! To get started:

1. Fork the repository
2. Create a new branch: `git checkout -b feature/your-feature-name`
3. Make your changes and commit: `git commit -m "Add: your feature description"`
4. Push to your fork: `git push origin feature/your-feature-name`
5. Open a Pull Request


---

## 👩‍💻 Author

**Karina Paudel**
BIT Student · Nepal

- GitHub: [@Karina-p1](https://github.com/Karina-p1)

---


<p align="center">
  Built with ❤️ in Nepal &nbsp;·&nbsp; RoomFinder Nepal © 2026
</p>
