# Categorized location data for the scraper UI

LOCATIONS = {
    "Pakistan": [
        "Gujranwala", "Lahore", "Karachi", "Islamabad", "Faisalabad", 
        "Rawalpindi", "Multan", "Sialkot", "Peshawar", "Quetta"
    ],
    "United States": [
        "New York", "Los Angeles", "Chicago", "Houston", "Phoenix", 
        "Philadelphia", "San Antonio", "San Diego", "Dallas", "San Jose"
    ],
    "United Kingdom": [
        "London", "Birmingham", "Glasgow", "Liverpool", "Bristol", 
        "Manchester", "Sheffield", "Leeds", "Edinburgh", "Leicester"
    ],
    "India": [
        "Mumbai", "Delhi", "Bangalore", "Hyderabad", "Ahmedabad", 
        "Chennai", "Kolkata", "Surat", "Pune", "Jaipur"
    ],
    "Germany": [
        "Berlin", "Hamburg", "Munich", "Cologne", "Frankfurt", 
        "Stuttgart", "Düsseldorf", "Dortmund", "Essen", "Leipzig"
    ],
    "Canada": [
        "Toronto", "Montreal", "Vancouver", "Calgary", "Edmonton", 
        "Ottawa", "Winnipeg", "Quebec City", "Hamilton", "Kitchener"
    ],
    "Australia": [
        "Sydney", "Melbourne", "Brisbane", "Perth", "Adelaide", 
        "Gold Coast", "Canberra", "Newcastle", "Wollongong", "Geelong"
    ],
    "United Arab Emirates": [
        "Dubai", "Abu Dhabi", "Sharjah", "Al Ain", "Ajman", "Ras Al Khaimah"
    ],
    "Saudi Arabia": [
        "Riyadh", "Jeddah", "Mecca", "Medina", "Dammam", "Khobar"
    ]
}

# Coordinate mapping for visual circle support
CITY_COORDS = {
    "Gujranwala": [32.1617, 74.1883],
    "Lahore": [31.5204, 74.3587],
    "Karachi": [24.8607, 67.0011],
    "Islamabad": [33.6844, 73.0479],
    "Faisalabad": [31.4504, 73.1350],
    "Dubai": [25.2048, 55.2708],
    "London": [51.5074, -0.1278],
    "New York": [40.7128, -74.0060],
    "Los Angeles": [34.0522, -118.2437],
    "Toronto": [43.6532, -79.3832],
    "Mumbai": [19.0760, 72.8777],
    "Delhi": [28.6139, 77.2090]
}

CATEGORIES = sorted([
    "Manufacturers", "Factories", "Wholesalers", "Showrooms", "Corporate Offices",
    "Software Houses", "Ice Cream Shops", "Restaurants", "Clinics", "Hospitals",
    "Schools", "Gyms", "Car Dealers", "Real Estate Agencies", "Hotels",
    "Supermarkets", "Textile Mills", "Auto Parts Stores", "Furniture Stores", "Printing Presses",
    # Retail & Shopping
    "Clothing Stores", "Electronics Stores", "Jewelry Stores", "Pharmacies", "Pet Shops",
    "Bookstores", "Florists", "Stationery Stores", "Toy Stores", "Hardware Stores",
    "Gift Shops", "Antique Stores", "Optical Shops", "Shoe Stores", "Boutiques",
    # Food & Drink
    "Cafes", "Bakeries", "Bars", "Pizza Places", "Fast Food", "Coffee Shops",
    "Liquor Stores", "Steakhouses", "Sushi Restaurants", "Chinese Restaurants", "Italian Restaurants",
    # Services
    "Barbershops", "Beauty Salons", "Spas", "Dry Cleaners", "Banks", "Law Firms",
    "Accounting Firms", "Travel Agencies", "Courier Services", "Graphic Design Studios",
    "Marketing Agencies", "IT Consultants", "HR Agencies", "Insurance Agencies",
    # Automotive
    "Auto Repair", "Gas Stations", "Car Wash", "Tire Shops", "Rental Car", "Auto Body Shops",
    # Health & Wellness
    "Dental Clinics", "Opticians", "Physical Therapy", "Veterinary Clinics", "Yoga Studios",
    "Diagnostic Centers", "Home Health Care", "Medical Labs",
    # Education
    "Preschools", "Language Schools", "Driving Schools", "Tutoring Centers", "Universities",
    "Vocational Training",
    # Industry & Construction
    "Electricians", "Plumbers", "Architects", "Engineering Consultants", "HVAC Contractors",
    "Solar Energy Companies", "Steel Mills", "Chemical Plants", "Packaging Companies",
    "Construction Companies", "Interior Designers",
    # Entertainment & Leisure
    "Movie Theaters", "Art Galleries", "Museums", "Parks", "Night Clubs", "Stadiums",
    "Amusement Parks", "Zoos", "Libraries",
    # Professional & Others
    "Security Companies", "Cleaning Services", "Event Planners", "Photography Studios",
    "Web Developers", "Mobile App Developers", "Digital Marketing", "E-commerce"
])
