from flask import Flask, render_template, request, redirect, url_for, flash
import os
import uuid
from werkzeug.utils import secure_filename
from flask_sqlalchemy import SQLAlchemy
from datetime import datetime

app = Flask(__name__)
app.secret_key = 'your_secret_key'  # Needed for flash messages

# Configure upload folder
UPLOAD_FOLDER = 'static/uploads'
ALLOWED_EXTENSIONS = {'png', 'jpg', 'jpeg', 'gif'}
app.config['UPLOAD_FOLDER'] = UPLOAD_FOLDER

# Configure database
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///rentals.db'
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
db = SQLAlchemy(app)

# Define database models
class Listing(db.Model):
    id = db.Column(db.String(36), primary_key=True)
    title = db.Column(db.String(100), nullable=False)
    address = db.Column(db.String(200), nullable=False)
    rooms = db.Column(db.Integer, nullable=False)
    price = db.Column(db.Integer, nullable=False)
    price_type = db.Column(db.String(10), default='month')  # 'month' or 'day'
    description = db.Column(db.Text, nullable=False)
    owner_name = db.Column(db.String(100), nullable=False)
    owner_email = db.Column(db.String(100), nullable=False)
    owner_phone = db.Column(db.String(20), nullable=False)
    status = db.Column(db.String(20), nullable=False)
    type = db.Column(db.String(20), nullable=False)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    updated_at = db.Column(db.DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    
    # Relationship with images
    images = db.relationship('Image', backref='listing', lazy=True, cascade="all, delete-orphan")
    
    def to_dict(self):
        return {
            'id': self.id,
            'title': self.title,
            'address': self.address,
            'rooms': self.rooms,
            'price': self.price,
            'price_type': self.price_type,
            'description': self.description,
            'owner_name': self.owner_name,
            'owner_email': self.owner_email,
            'owner_phone': self.owner_phone,
            'status': self.status,
            'type': self.type,
            'images': [image.filename for image in self.images]
        }

class Image(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    filename = db.Column(db.String(255), nullable=False)
    listing_id = db.Column(db.String(36), db.ForeignKey('listing.id'), nullable=False)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)

def allowed_file(filename):
    return '.' in filename and \
           filename.rsplit('.', 1)[1].lower() in ALLOWED_EXTENSIONS

@app.route('/')
def index():
    # Get filter parameters from the query string
    min_price = request.args.get('min_price', '')
    max_price = request.args.get('max_price', '')
    status = request.args.get('status', '')
    type = request.args.get('type', '')
    
    # Start with a base query
    query = Listing.query
    
    # Apply price filters if provided
    if min_price and min_price.isdigit():
        min_price_value = int(min_price)
        query = query.filter(Listing.price >= min_price_value)
    
    if max_price and max_price.isdigit():
        max_price_value = int(max_price)
        query = query.filter(Listing.price <= max_price_value)
    
    # Apply status filter if provided
    if status:
        query = query.filter(Listing.status == status)
    
    # Apply type filter if provided
    if type:
        query = query.filter(Listing.type == type)
    
    # Get the filtered listings
    filtered_listings = query.all()
    
    # Convert to dictionary format for the template
    listings = [listing.to_dict() for listing in filtered_listings]
    
    # Get unique values for dropdowns
    status_options = db.session.query(Listing.status).distinct().all()
    status_options = sorted([status[0] for status in status_options])
    
    type_options = db.session.query(Listing.type).distinct().all()
    type_options = sorted([type[0] for type in type_options])
    
    return render_template('index.html', 
                          listings=listings, 
                          min_price=min_price, 
                          max_price=max_price,
                          status=status,
                          type=type,
                          status_options=status_options,
                          type_options=type_options)

@app.route('/listing/<listing_id>')
def listing_detail(listing_id):
    listing = Listing.query.get_or_404(listing_id)
    return render_template('listing_detail.html', listing=listing.to_dict())

@app.route('/edit/<listing_id>', methods=['GET', 'POST'])
def edit_listing(listing_id):
    # Find the listing to edit
    listing = Listing.query.get_or_404(listing_id)
    
    if request.method == 'POST':
        # Update listing with form data
        listing.title = request.form.get('title')
        listing.address = request.form.get('address')
        listing.rooms = int(request.form.get('rooms'))
        listing.price = int(request.form.get('price'))
        listing.price_type = request.form.get('price_type', 'month')
        listing.description = request.form.get('description')
        listing.owner_name = request.form.get('owner_name')
        listing.owner_email = request.form.get('owner_email')
        listing.owner_phone = request.form.get('owner_phone')
        listing.status = request.form.get('status')
        listing.type = request.form.get('type')
        
        # Handle image uploads
        if 'images' in request.files:
            files = request.files.getlist('images')
            new_images = []
            for file in files:
                if file and allowed_file(file.filename) and file.filename:
                    filename = secure_filename(file.filename)
                    # Add unique identifier to prevent filename collisions
                    unique_filename = f"{uuid.uuid4().hex}_{filename}"
                    file.save(os.path.join(app.config['UPLOAD_FOLDER'], unique_filename))
                    new_images.append(unique_filename)
            
            # If new images were uploaded, replace the old ones
            if new_images:
                # Delete old images from database
                for image in listing.images:
                    db.session.delete(image)
                
                # Add new images to database
                for filename in new_images:
                    new_image = Image(filename=filename, listing=listing)
                    db.session.add(new_image)
        
        # Save changes to database
        db.session.commit()
        flash('Listing updated successfully!')
        return redirect(url_for('listing_detail', listing_id=listing_id))
    
    return render_template('edit_listing.html', listing=listing.to_dict())

@app.route('/delete/<listing_id>', methods=['POST'])
def delete_listing(listing_id):
    # Find the listing to delete
    listing = Listing.query.get_or_404(listing_id)
    
    # Delete the listing
    db.session.delete(listing)
    db.session.commit()
    
    flash('Listing deleted successfully!')
    return redirect(url_for('index'))

@app.route('/add', methods=['GET', 'POST'])
def add_listing(listing_id=None):
    if request.method == 'POST':
        # Get form data
        title = request.form.get('title')
        address = request.form.get('address')
        rooms = request.form.get('rooms')
        price = request.form.get('price')
        price_type = request.form.get('price_type', 'month')
        description = request.form.get('description')
        owner_name = request.form.get('owner_name')
        owner_email = request.form.get('owner_email')
        owner_phone = request.form.get('owner_phone')
        status = request.form.get('status')
        type = request.form.get('type')
        
        # Create new listing
        new_listing = Listing(
            id=str(uuid.uuid4()),
            title=title,
            address=address,
            rooms=int(rooms),
            price=int(price),
            price_type=price_type,
            description=description,
            owner_name=owner_name,
            owner_email=owner_email,
            owner_phone=owner_phone,
            status=status,
            type=type
        )
        
        db.session.add(new_listing)
        
        # Handle image uploads
        if 'images' in request.files:
            files = request.files.getlist('images')
            for file in files:
                if file and allowed_file(file.filename):
                    filename = secure_filename(file.filename)
                    # Add unique identifier to prevent filename collisions
                    unique_filename = f"{uuid.uuid4().hex}_{filename}"
                    file.save(os.path.join(app.config['UPLOAD_FOLDER'], unique_filename))
                    
                    # Create new image record
                    new_image = Image(filename=unique_filename, listing=new_listing)
                    db.session.add(new_image)
        
        # If no images were uploaded, use a default image
        if not new_listing.images:
            default_image = Image(
                filename='1f8ecf990061459ebdf2bdb3887afd92_images.jpeg',
                listing=new_listing
            )
            db.session.add(default_image)
        
        # Save to database
        db.session.commit()
        
        flash('Listing added successfully!')
        return redirect(url_for('index'))
    
    return render_template('add_listing.html')

# Initialize the database and add sample data
def init_db():
    # Create tables
    db.create_all()
    
    # Check if we already have listings
    if Listing.query.count() == 0:
        # Sample data
        sample_listings = [
            {
                'id': '1',
                'title': 'Cozy Studio Apartment',
                'address': '123 Main St, Bangalore, India',
                'rooms': 1,
                'price': 15000,
                'price_type': 'month',
                'description': 'A cozy studio apartment in the heart of downtown.',
                'owner_name': 'John Doe',
                'owner_email': 'john@example.com',
                'owner_phone': '555-123-4567',
                'images': ['1f8ecf990061459ebdf2bdb3887afd92_images.jpeg', '21826cc038984c65b8139e0d1961ff9f_images_1.jpeg'],
                'status': 'Active',
                'type': 'AnyOne'
            },
            {
                'id': '2',
                'title': 'Spacious 2-Bedroom Apartment',
                'address': '456 Oak Ave, Mumbai, India',
                'rooms': 2,
                'price': 25000,
                'price_type': 'month',
                'description': 'A spacious 2-bedroom apartment with a great view.',
                'owner_name': 'Jane Smith',
                'owner_email': 'jane@example.com',
                'owner_phone': '555-987-6543',
                'images': ['301242c407974e09ab12cafd9a900e23_images_2.jpeg', '6d12a5f2f1c44def9f8555dc0ab1c1bf_images_3.jpeg'],
                'status': 'Active',
                'type': 'Family'
            },
            {
                'id': '3',
                'title': 'Boys Hostel Room',
                'address': '789 College Rd, Delhi, India',
                'rooms': 1,
                'price': 8000,
                'price_type': 'month',
                'description': 'Affordable hostel room for male students near university.',
                'owner_name': 'Raj Kumar',
                'owner_email': 'raj@example.com',
                'owner_phone': '555-456-7890',
                'images': ['1f8ecf990061459ebdf2bdb3887afd92_images.jpeg', '38b7ac2f005044aebd814d9505b2bfe5_images_4.jpeg'],
                'status': 'Active',
                'type': 'Boys Only'
            },
            {
                'id': '4',
                'title': 'Girls PG Accommodation',
                'address': '234 Park St, Chennai, India',
                'rooms': 1,
                'price': 9000,
                'price_type': 'month',
                'description': 'Safe and comfortable PG for female students or working professionals.',
                'owner_name': 'Priya Sharma',
                'owner_email': 'priya@example.com',
                'owner_phone': '555-789-0123',
                'images': ['301242c407974e09ab12cafd9a900e23_images_2.jpeg', '1f8ecf990061459ebdf2bdb3887afd92_images.jpeg'],
                'status': 'Active',
                'type': 'Girls Only'
            },
            {
                'id': '5',
                'title': 'Covered Parking Space',
                'address': '567 Market Rd, Hyderabad, India',
                'rooms': 0,
                'price': 300,
                'price_type': 'day',
                'description': 'Secure covered parking space in central location. Rent per day.',
                'owner_name': 'Vikram Singh',
                'owner_email': 'vikram@example.com',
                'owner_phone': '555-234-5678',
                'images': ['9d94ad0e13b94224b5d69dca417f2af2_istockphoto-1280875183-612x612.jpg'],
                'status': 'Active',
                'type': 'Car'
            },
            {
                'id': '6',
                'title': 'Luxury Apartment',
                'address': '890 Elite Blvd, Pune, India',
                'rooms': 3,
                'price': 45000,
                'price_type': 'month',
                'description': 'Luxury apartment with modern amenities and premium finishes.',
                'owner_name': 'Anil Kapoor',
                'owner_email': 'anil@example.com',
                'owner_phone': '555-345-6789',
                'images': ['1f8ecf990061459ebdf2bdb3887afd92_images.jpeg', '301242c407974e09ab12cafd9a900e23_images_2.jpeg'],
                'status': 'Inactive',
                'type': 'Family'
            }
        ]
        
        # Add sample listings to database
        for listing_data in sample_listings:
            image_filenames = listing_data.pop('images')
            listing = Listing(**listing_data)
            
            for filename in image_filenames:
                image = Image(filename=filename, listing=listing)
                db.session.add(image)
            
            db.session.add(listing)
        
        db.session.commit()
        print("Sample data added to database.")

if __name__ == '__main__':
    # Ensure upload directory exists
    os.makedirs(app.config['UPLOAD_FOLDER'], exist_ok=True)
    
    # Initialize database
    with app.app_context():
        init_db()
    
    app.run(debug=True) 