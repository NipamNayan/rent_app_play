# RoomRover Rentals

A Flask web application for managing property and vehicle rentals with a user-friendly interface and persistent database storage.

## Features

- **Property Management**: Add, edit, and delete rental listings
- **Multiple Rental Types**: Support for various rental categories:
  - Apartments and Rooms
  - Boys and Girls Hostels/PG Accommodations
  - Family Accommodations
  - Car/Parking Spaces
- **Flexible Pricing Options**: 
  - Monthly pricing for residential properties
  - Daily pricing for car/parking rentals
  - Automatic price type selection based on listing type
- **Image Management**:
  - Multiple image uploads per listing
  - Image preview in listings
  - Ability to replace images when editing
- **Advanced Filtering**:
  - Filter by price range
  - Filter by property type
  - Filter by listing status
- **Responsive Design**: Works on desktop and mobile devices
- **Data Persistence**: SQLite database with SQLAlchemy ORM

## Technology Stack

- **Backend**: Flask, Python 3
- **Database**: SQLite with SQLAlchemy
- **Frontend**: HTML, CSS, JavaScript
- **File Storage**: Local file system for image uploads
- **Containerization**: Docker support for easy deployment

## Installation

### Standard Installation

1. Clone the repository:
   ```bash
   git clone https://github.com/NipamNayan/rent_app_play.git
   cd rent_app_play
   ```

2. Install dependencies:
   ```bash
   pip install -r requirements.txt
   ```

3. Run the application:
   ```bash
   python app.py
   ```

4. Access the application in your browser:
   ```
   http://127.0.0.1:5000/
   ```

### Docker Installation

1. Clone the repository:
   ```bash
   git clone https://github.com/NipamNayan/rent_app_play.git
   cd rent_app_play
   ```

2. Build and run with Docker Compose:
   ```bash
   docker-compose up --build
   ```

3. Access the application in your browser:
   ```
   http://127.0.0.1:5000/
   ```

## Database Migration

If you need to add the price_type field to an existing database:

```bash
python migrate_db.py
```

## Project Structure

```
webapp_rent/
├── app.py                  # Main application file
├── migrate_db.py           # Database migration script
├── requirements.txt        # Python dependencies
├── Dockerfile              # Docker configuration
├── docker-compose.yml      # Docker Compose configuration
├── instance/               # Database files
├── static/                 # Static assets
│   ├── css/                # CSS stylesheets
│   └── uploads/            # Uploaded images
└── templates/              # HTML templates
    ├── base.html           # Base template
    ├── index.html          # Homepage/listing view
    ├── listing_detail.html # Detailed view of a listing
    ├── add_listing.html    # Form to add a new listing
    └── edit_listing.html   # Form to edit an existing listing
```

## Usage

1. **View Listings**: Browse all available properties on the homepage
2. **Filter Listings**: Use the filter controls to narrow down results
3. **Add Listing**: Click "Add Listing" to create a new rental listing
4. **Edit/Delete**: Manage existing listings from their detail pages
5. **View Details**: Click on any listing to see full information and contact details

## Future Enhancements

- User authentication and role-based access
- Booking and reservation system
- Payment integration
- Advanced search with more filters
- Map integration for property locations
- Email notifications

## License

This project is licensed under the MIT License - see the LICENSE file for details.

## Author

Nipam Nayan Gogoi 